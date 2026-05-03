"""
Model Service - кэширование ML моделей и расчёт метрик качества
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import os
import json
import pandas as pd
import numpy as np
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Конфигурация колонок
TARGET_COL = "Demand Forecast"
DATE_COL = "Date"

CAT_COLS = [
    "Category",
    "Region",
    "Weather Condition",
    "Seasonality",
    "Store ID",
]

NUM_COLS = [
    "Inventory Level",
    "Units Ordered",
    "Price",
    "Discount",
    "Competitor Pricing",
    "Holiday/Promotion",
]

DROP_COLS = ["Demand Forecast"]

# Директория для сохранения моделей на диск
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Глобальный кэш моделей
_model_cache: Dict[str, Dict[str, Any]] = {}


def get_cache_key(product_id: str, store_id: Optional[str] = None, model_type: str = "random_forest") -> str:
    """Генерирует ключ кэша для продукта/магазина/типа модели"""
    return f"{product_id}_{store_id or 'all'}_{model_type}"


def build_model(model_type: str = "random_forest"):
    """Создаёт ML модель по типу"""
    if model_type == "lightgbm":
        from lightgbm import LGBMRegressor
        return LGBMRegressor(
            n_estimators=500,
            learning_rate=0.05,
            num_leaves=63,
            n_jobs=-1,
            verbose=-1,
        )
    elif model_type == "xgboost":
        from xgboost import XGBRegressor
        return XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            n_jobs=-1,
            verbosity=0,
        )
    else:  # random_forest (default)
        return RandomForestRegressor(
            n_estimators=300,
            random_state=42,
            n_jobs=-1,
        )


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """Добавляет фичи из даты"""
    df = df.copy()
    df["day"] = df[DATE_COL].dt.day
    df["month"] = df[DATE_COL].dt.month
    df["day_of_week"] = df[DATE_COL].dt.dayofweek

    # Циклические признаки (лучше для ML)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

    return df


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """Добавляет лаговые признаки — критично для временных рядов"""
    df = df.copy()
    df = df.sort_values(DATE_COL)

    # Лаговые признаки
    df["demand_lag_1"] = df[TARGET_COL].shift(1)
    df["demand_lag_7"] = df[TARGET_COL].shift(7)
    df["demand_lag_14"] = df[TARGET_COL].shift(14)
    df["demand_lag_30"] = df[TARGET_COL].shift(30)

    # Скользящие средние
    df["demand_rolling_mean_7"] = df[TARGET_COL].rolling(window=7, min_periods=1).mean()
    df["demand_rolling_std_7"] = df[TARGET_COL].rolling(window=7, min_periods=1).std().fillna(0)
    df["demand_rolling_mean_30"] = df[TARGET_COL].rolling(window=30, min_periods=1).mean()

    # Тренд (изменение)
    df["demand_diff"] = df[TARGET_COL].diff().fillna(0)

    # Заполняем NaN средними
    for col in ["demand_lag_1", "demand_lag_7", "demand_lag_14", "demand_lag_30"]:
        df[col] = df[col].fillna(df[TARGET_COL].mean())

    return df


# Дополнительные числовые колонки с лагами
LAG_COLS = [
    "demand_lag_1",
    "demand_lag_7",
    "demand_lag_14",
    "demand_lag_30",
    "demand_rolling_mean_7",
    "demand_rolling_std_7",
    "demand_rolling_mean_30",
    "demand_diff",
]

CYCLIC_COLS = ["month_sin", "month_cos", "dow_sin", "dow_cos"]


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Рассчитывает метрики качества модели"""
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 4),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def train_model(df: pd.DataFrame, test_size: float = 0.2, model_type: str = "random_forest") -> Dict[str, Any]:
    """
    Обучает модель с временным split и возвращает pipeline + метрики

    Returns:
        {
            "pipeline": trained Pipeline,
            "metrics": {"mae": ..., "rmse": ..., "r2": ...},
            "last_row": dict,
            "last_date": datetime,
            "num_cols_ext": list,
            "model_type": str,
            "trained_at": datetime
        }
    """
    # Сортируем по дате для правильного временного split
    df = df.sort_values(DATE_COL).reset_index(drop=True)

    # Добавляем все признаки
    df = add_lag_features(df)
    df = add_date_features(df)

    # Расширенный список числовых колонок
    num_cols_ext = NUM_COLS + ["day", "month", "day_of_week"] + LAG_COLS + CYCLIC_COLS

    # Извлекаем y до удаления колонки
    y = df[TARGET_COL]

    # Удаляем ненужные колонки
    for c in DROP_COLS:
        if c in df.columns:
            df = df.drop(columns=[c])

    # Подготовка данных
    X = df[CAT_COLS + num_cols_ext]

    # Временной split (хронологический, не случайный!)
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Препроцессор
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
            ("num", "passthrough", num_cols_ext),
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("pre", preprocessor),
            ("model", build_model(model_type)),
        ]
    )

    # Обучение
    pipeline.fit(X_train, y_train)

    # Предсказание на тесте для метрик
    y_pred = pipeline.predict(X_test)
    metrics = calculate_metrics(y_test.values, y_pred)

    # Последняя строка для прогноза
    df_sorted = df.sort_values(DATE_COL)
    last_row = df_sorted.iloc[-1].to_dict()
    last_date = df_sorted.iloc[-1][DATE_COL]

    return {
        "pipeline": pipeline,
        "metrics": metrics,
        "last_row": last_row,
        "last_date": last_date,
        "num_cols_ext": num_cols_ext,
        "model_type": model_type,
        "trained_at": datetime.now(),
    }


def train_model_preview(
    df: pd.DataFrame,
    product_id: str,
    store_id: Optional[str] = None,
    model_type: str = "random_forest",
) -> Dict[str, Any]:
    """
    Обучает новую модель БЕЗ сохранения в кэш.
    Используется для сравнения моделей (preview).
    """
    return train_model(df, model_type=model_type)


def save_model_to_disk(cache_key: str, trained: Dict[str, Any]) -> None:
    """Сохраняет обученный pipeline и метаданные на диск"""
    try:
        joblib.dump(trained["pipeline"], os.path.join(MODELS_DIR, f"{cache_key}.pkl"))
        meta = {
            "metrics": trained["metrics"],
            "trained_at": str(trained["trained_at"]),
            "model_type": trained.get("model_type", "random_forest"),
            "num_cols_ext": trained["num_cols_ext"],
        }
        with open(os.path.join(MODELS_DIR, f"{cache_key}.meta.json"), "w") as f:
            json.dump(meta, f)
    except Exception:
        pass  # Диск недоступен — не критично, память работает


def load_model_from_disk(cache_key: str) -> Optional[Dict[str, Any]]:
    """Загружает pipeline и метаданные с диска"""
    pkl_path = os.path.join(MODELS_DIR, f"{cache_key}.pkl")
    meta_path = os.path.join(MODELS_DIR, f"{cache_key}.meta.json")
    if not os.path.exists(pkl_path) or not os.path.exists(meta_path):
        return None
    try:
        pipeline = joblib.load(pkl_path)
        with open(meta_path) as f:
            meta = json.load(f)
        return {
            "pipeline": pipeline,
            "metrics": meta["metrics"],
            "trained_at": meta["trained_at"],
            "model_type": meta.get("model_type", "random_forest"),
            "num_cols_ext": meta["num_cols_ext"],
            # last_row и last_date будут обновлены после загрузки
            "last_row": None,
            "last_date": None,
        }
    except Exception:
        return None


def get_or_train_model(
    df: pd.DataFrame,
    product_id: str,
    store_id: Optional[str] = None,
    force_retrain: bool = False,
    model_type: str = "random_forest",
) -> Dict[str, Any]:
    """
    Получает модель из кэша (память → диск) или обучает новую

    Args:
        df: DataFrame с данными продукта
        product_id: ID продукта
        store_id: ID магазина (опционально)
        force_retrain: принудительно переобучить
        model_type: тип модели ("random_forest", "lightgbm", "xgboost")

    Returns:
        Словарь с pipeline, метриками и метаданными
    """
    cache_key = get_cache_key(product_id, store_id, model_type)

    def _update_last_row(cached: Dict[str, Any]) -> Dict[str, Any]:
        """Обновляет last_row и last_date из текущих данных"""
        df_with_features = add_lag_features(df)
        df_with_features = add_date_features(df_with_features)
        df_sorted = df_with_features.sort_values(DATE_COL)
        cached["last_row"] = df_sorted.iloc[-1].to_dict()
        cached["last_date"] = df_sorted.iloc[-1][DATE_COL]
        return cached

    # 1. Память
    if not force_retrain and cache_key in _model_cache:
        return _update_last_row(_model_cache[cache_key])

    # 2. Диск
    if not force_retrain:
        disk = load_model_from_disk(cache_key)
        if disk:
            disk = _update_last_row(disk)
            _model_cache[cache_key] = disk
            return disk

    # 3. Обучаем новую модель
    trained = train_model(df, model_type=model_type)
    _model_cache[cache_key] = trained
    save_model_to_disk(cache_key, trained)

    return trained


def make_future_rows(
    last_row: Dict[str, Any],
    last_date: pd.Timestamp,
    horizon: int,
) -> pd.DataFrame:
    """Создаёт строки для будущих дат с лаговыми признаками"""
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon)

    rows = []
    for d in future_dates:
        r = dict(last_row)
        r[DATE_COL] = d
        r["day"] = d.day
        r["month"] = d.month
        r["day_of_week"] = d.dayofweek

        # Циклические признаки
        r["month_sin"] = np.sin(2 * np.pi * d.month / 12)
        r["month_cos"] = np.cos(2 * np.pi * d.month / 12)
        r["dow_sin"] = np.sin(2 * np.pi * d.dayofweek / 7)
        r["dow_cos"] = np.cos(2 * np.pi * d.dayofweek / 7)

        # Убедимся что все lag колонки присутствуют (используем последние известные значения)
        for lag_col in LAG_COLS:
            if lag_col not in r:
                r[lag_col] = 0.0

        r.pop(TARGET_COL, None)
        rows.append(r)

    return pd.DataFrame(rows)


def predict(
    trained: Dict[str, Any],
    horizon_days: int,
) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Генерирует предсказания на будущие даты

    Returns:
        (future_df, predictions)
    """
    pipeline = trained["pipeline"]
    last_row = trained["last_row"]
    last_date = trained["last_date"]
    num_cols_ext = trained["num_cols_ext"]

    future_df = make_future_rows(last_row, last_date, horizon_days)
    X_future = future_df[CAT_COLS + num_cols_ext]
    predictions = pipeline.predict(X_future)

    return future_df, predictions


def clear_cache() -> int:
    """Очищает кэш моделей. Возвращает количество удалённых записей."""
    global _model_cache
    count = len(_model_cache)
    _model_cache = {}
    return count


def get_cache_info() -> Dict[str, Any]:
    """Возвращает информацию о кэше"""
    return {
        "cached_models": len(_model_cache),
        "keys": list(_model_cache.keys()),
        "details": {
            key: {
                "trained_at": str(val["trained_at"]),
                "metrics": val["metrics"],
                "model_type": val.get("model_type", "random_forest"),
            }
            for key, val in _model_cache.items()
        },
    }


def get_feature_importance(product_id: str, store_id: Optional[str] = None, model_type: str = "random_forest") -> Dict[str, Any]:
    """
    Возвращает важность признаков для визуализации модели

    Returns:
        {
            "features": [{"name": "demand_lag_1", "importance": 0.45}, ...],
            "model_type": "random_forest",
            "total_features": 25
        }
    """
    cache_key = get_cache_key(product_id, store_id, model_type)

    if cache_key not in _model_cache:
        return {"error": "Model not trained yet. Call /forecast first."}

    trained = _model_cache[cache_key]
    pipeline = trained["pipeline"]
    num_cols_ext = trained["num_cols_ext"]

    # Получаем модель из pipeline
    estimator = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["pre"]

    # Получаем имена признаков после OneHotEncoding
    cat_encoder = preprocessor.named_transformers_["cat"]
    cat_feature_names = list(cat_encoder.get_feature_names_out(CAT_COLS))
    all_feature_names = cat_feature_names + num_cols_ext

    # Важность признаков
    importances = estimator.feature_importances_

    # Сортируем по важности
    feature_importance = [
        {"name": name, "importance": round(float(imp), 4)}
        for name, imp in zip(all_feature_names, importances)
    ]
    feature_importance.sort(key=lambda x: x["importance"], reverse=True)

    return {
        "product_id": product_id,
        "features": feature_importance[:20],  # Top 20
        "model_type": trained.get("model_type", "random_forest"),
        "total_features": len(all_feature_names),
        "metrics": trained["metrics"],
    }


# =========================================================
# MARKET DATA PREDICTOR (web-search → ML → demand score)
# =========================================================

# Path to Amazon dataset
_AMAZON_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "amazon", "Amazon-Products.csv",
)

# Cache key for market model
_MARKET_MODEL_KEY = "__market_predictor__"

INR_TO_USD = 0.012  # ~1 INR = 0.012 USD


def _load_amazon_for_market() -> Optional[pd.DataFrame]:
    """Load and clean Amazon CSV for market model training"""
    if not os.path.exists(_AMAZON_CSV):
        return None
    try:
        df = pd.read_csv(_AMAZON_CSV, usecols=["ratings", "no_of_ratings", "discount_price", "actual_price"])

        def _clean_price(s):
            if pd.isna(s):
                return np.nan
            return float(str(s).replace("₹", "").replace(",", "").strip())

        def _clean_num(s):
            if pd.isna(s):
                return 0.0
            try:
                return float(str(s).replace(",", "").strip())
            except ValueError:
                return 0.0

        df["actual_price"] = df["actual_price"].apply(_clean_price)
        df["discount_price"] = df["discount_price"].apply(_clean_price)
        df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")
        df["no_of_ratings"] = df["no_of_ratings"].apply(_clean_num)

        df = df.dropna(subset=["actual_price", "ratings"])
        df = df[df["actual_price"] > 0]
        df = df[df["ratings"].between(1, 5)]

        # Price in USD
        df["price_usd"] = df["actual_price"] * INR_TO_USD

        # Discount percent
        df["discount_pct"] = np.where(
            df["actual_price"] > 0,
            (df["actual_price"] - df["discount_price"].fillna(df["actual_price"])) / df["actual_price"],
            0.0,
        ).clip(0, 1)

        # Log reviews
        df["log_reviews"] = np.log1p(df["no_of_ratings"])

        # Demand score: rating × log(reviews+1) — normalized 0–100
        raw_score = df["ratings"] * df["log_reviews"]
        df["demand_score"] = (raw_score / raw_score.max() * 100).clip(0, 100)

        return df[["price_usd", "discount_pct", "ratings", "log_reviews", "demand_score"]].dropna()
    except Exception as e:
        print(f"[market model] load error: {e}")
        return None


def _get_or_train_market_model() -> Optional[Dict[str, Any]]:
    """Get cached market model or train from Amazon data"""
    if _MARKET_MODEL_KEY in _model_cache:
        return _model_cache[_MARKET_MODEL_KEY]

    df = _load_amazon_for_market()
    if df is None or len(df) < 100:
        return None

    # Sample up to 50K rows for speed
    df = df.sample(min(50_000, len(df)), random_state=42)

    X = df[["price_usd", "discount_pct", "ratings", "log_reviews"]]
    y = df["demand_score"]

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)

    # Compute percentile lookup from training data
    demand_scores_sorted = np.sort(y.values)

    result = {
        "model": model,
        "demand_scores_sorted": demand_scores_sorted,
        "feature_names": ["price_usd", "discount_pct", "ratings", "log_reviews"],
        "trained_at": datetime.now(),
        "training_size": len(df),
    }
    _model_cache[_MARKET_MODEL_KEY] = result
    return result


def predict_from_market_data(
    price_usd: float,
    competitor_price_usd: float,
    rating: float,
    review_count: int,
    trend_direction: str = "stable",
    popularity_score: float = 50.0,
    # New Kazakhstan-specific signals
    has_kaspi_installment: bool = False,
    kaspi_sellers: int = 0,
    news_sentiment_score: int = 0,
    market_saturation_score: float = 0.5,
    is_new_model: bool = False,
    has_supply_issue: bool = False,
    yoy_growth_percent: float = 0.0,
) -> Dict[str, Any]:
    """
    Predict market demand score using Amazon-trained ML model + KZ signals.

    Args:
        price_usd: Product wholesale price in USD
        competitor_price_usd: Average competitor price in USD
        rating: Average combined rating (global + Kaspi)
        review_count: Total number of reviews (global + Kaspi)
        trend_direction: "up", "down", or "stable"
        popularity_score: Web search popularity adjusted for news (0–100)
        has_kaspi_installment: Product available on Kaspi рассрочка
        kaspi_sellers: Number of sellers on Kaspi.kz
        news_sentiment_score: News sentiment (-5 to +5)
        market_saturation_score: Market saturation (0=low, 1=high)
        is_new_model: Whether a new version was recently announced
        has_supply_issue: Known supply deficit
        yoy_growth_percent: Category year-over-year growth %

    Returns:
        {
            "demand_score": 0–100,
            "demand_percentile": 0–100 (vs Amazon catalog),
            "market_grade": "A"/"B"/"C"/"D",
            "ml_confidence": float,
            "key_factors": [...],
            "recommendation": str,
            "kz_signals": {...},
        }
    """
    # Clamp base inputs
    rating = max(0.0, min(5.0, float(rating or 3.5)))
    review_count = max(0, int(review_count or 0))
    price_usd = max(0.1, float(price_usd or 10.0))
    competitor_price_usd = max(0.1, float(competitor_price_usd or price_usd * 1.2))

    # Derived features
    discount_pct = max(0.0, min(0.9, (competitor_price_usd - price_usd) / competitor_price_usd))
    log_reviews = np.log1p(review_count)

    market_model = _get_or_train_market_model()

    if market_model is not None:
        X = pd.DataFrame([[price_usd, discount_pct, rating, log_reviews]], columns=market_model["feature_names"])
        demand_score = float(market_model["model"].predict(X)[0])
        demand_score = max(0.0, min(100.0, demand_score))

        # Compute percentile
        sorted_scores = market_model["demand_scores_sorted"]
        percentile = float(np.searchsorted(sorted_scores, demand_score) / len(sorted_scores) * 100)
        ml_confidence = min(0.95, 0.6 + (review_count / 5000) * 0.35) if review_count > 0 else 0.5

        importances = market_model["model"].feature_importances_
        feature_names = market_model["feature_names"]
        top_factors = sorted(zip(feature_names, importances), key=lambda x: -x[1])[:3]
    else:
        # Heuristic fallback
        demand_score = rating * 15 + min(log_reviews * 5, 40) + discount_pct * 20
        demand_score = max(0.0, min(100.0, demand_score + (popularity_score - 50) * 0.2))
        percentile = demand_score
        ml_confidence = 0.45
        top_factors = [("rating", 0.5), ("discount_pct", 0.3), ("log_reviews", 0.2)]

    # ── Kazakhstan market adjustments ──────────────────────────
    kz_delta = 0.0

    # Kaspi installment increases demand significantly in KZ (30-60% of purchases)
    if has_kaspi_installment:
        kz_delta += 7.0

    # News sentiment
    kz_delta += float(news_sentiment_score) * 1.5  # each point = ±1.5 score

    # Market saturation penalizes demand (hard to compete)
    kz_delta -= (market_saturation_score - 0.5) * 10.0

    # New model announcement: if upcoming model exists, current model demand drops
    if is_new_model:
        kz_delta -= 5.0

    # Supply issue creates artificial demand boost (scarcity effect)
    if has_supply_issue:
        kz_delta += 4.0

    # Category growth
    kz_delta += min(yoy_growth_percent * 0.15, 6.0)

    # Trend adjustment
    trend_boost = {"up": 8.0, "down": -8.0, "stable": 0.0}.get(trend_direction, 0.0)

    demand_score = max(0.0, min(100.0, demand_score + trend_boost + kz_delta))

    # Grade
    if demand_score >= 70:
        grade = "A"
    elif demand_score >= 50:
        grade = "B"
    elif demand_score >= 30:
        grade = "C"
    else:
        grade = "D"

    # Key factors explanation
    factor_labels = {
        "ratings": "Рейтинг өнімнің сапасын көрсетеді",
        "rating": "Рейтинг өнімнің сапасын көрсетеді",
        "log_reviews": "Шолулар саны сұранысты растайды",
        "discount_pct": "Бәсекелестерге қарағандағы баға артықшылығы",
        "price_usd": "Баға деңгейі нарықта маңызды рөл атқарады",
    }
    key_factors = [
        {"factor": name, "importance": round(float(imp), 3), "label": factor_labels.get(name, name)}
        for name, imp in top_factors
    ]

    # Recommendation
    if grade == "A":
        recommendation = "Өте жоғары сұраныс. Нарыққа кіруге кеңес беріледі."
    elif grade == "B":
        recommendation = "Жақсы сұраныс. Сатуға болады, бірақ бәсекені бақылаңыз."
    elif grade == "C":
        recommendation = "Орташа сұраныс. Маркетингке инвестиция керек."
    else:
        recommendation = "Төмен сұраныс. Альтернативті өнімдерді қарастырыңыз."

    return {
        "demand_score": round(demand_score, 1),
        "demand_percentile": round(percentile, 1),
        "market_grade": grade,
        "ml_confidence": round(ml_confidence, 2),
        "key_factors": key_factors,
        "recommendation": recommendation,
        "inputs": {
            "price_usd": price_usd,
            "competitor_price_usd": competitor_price_usd,
            "discount_pct": round(discount_pct * 100, 1),
            "rating": rating,
            "review_count": review_count,
            "trend_direction": trend_direction,
        },
        "kz_signals": {
            "kz_adjustment": round(kz_delta, 1),
            "kaspi_installment_boost": 7.0 if has_kaspi_installment else 0.0,
            "news_impact": round(float(news_sentiment_score) * 1.5, 1),
            "saturation_penalty": round(-(market_saturation_score - 0.5) * 10.0, 1),
            "new_model_penalty": -5.0 if is_new_model else 0.0,
            "supply_scarcity_boost": 4.0 if has_supply_issue else 0.0,
            "category_growth_boost": round(min(yoy_growth_percent * 0.15, 6.0), 1),
        },
    }


def get_model_structure() -> Dict[str, Any]:
    """
    Возвращает структуру модели для визуализации

    Returns:
        Описание слоёв и связей модели
    """
    return {
        "model_type": "RandomForestRegressor",
        "layers": [
            {
                "id": "input",
                "name": "Input Layer",
                "type": "input",
                "features": {
                    "categorical": CAT_COLS,
                    "numerical": NUM_COLS,
                    "temporal": ["day", "month", "day_of_week"],
                    "lag_features": LAG_COLS,
                    "cyclic": CYCLIC_COLS,
                }
            },
            {
                "id": "preprocessor",
                "name": "Preprocessor",
                "type": "transform",
                "operations": [
                    "OneHotEncoder for categorical",
                    "Passthrough for numerical"
                ]
            },
            {
                "id": "forest",
                "name": "Random Forest",
                "type": "ensemble",
                "config": {
                    "n_estimators": 300,
                    "algorithm": "RandomForestRegressor",
                    "description": "300 decision trees voting together"
                }
            },
            {
                "id": "output",
                "name": "Output",
                "type": "output",
                "target": "Demand Forecast (units)"
            }
        ],
        "connections": [
            {"from": "input", "to": "preprocessor"},
            {"from": "preprocessor", "to": "forest"},
            {"from": "forest", "to": "output"}
        ],
        "editable_params": [
            {"name": "n_estimators", "type": "int", "min": 50, "max": 500, "default": 300},
            {"name": "max_depth", "type": "int", "min": 5, "max": 50, "default": None},
            {"name": "min_samples_split", "type": "int", "min": 2, "max": 20, "default": 2},
            {"name": "test_size", "type": "float", "min": 0.1, "max": 0.4, "default": 0.2},
        ]
    }
