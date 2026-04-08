"""
Model Service - кэширование ML моделей и расчёт метрик качества
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
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

# Глобальный кэш моделей
_model_cache: Dict[str, Dict[str, Any]] = {}


def get_cache_key(product_id: str, store_id: Optional[str] = None) -> str:
    """Генерирует ключ кэша для продукта/магазина"""
    return f"{product_id}_{store_id or 'all'}"


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


def train_model(df: pd.DataFrame, test_size: float = 0.2) -> Dict[str, Any]:
    """
    Обучает модель с временным split и возвращает pipeline + метрики

    Returns:
        {
            "pipeline": trained Pipeline,
            "metrics": {"mae": ..., "rmse": ..., "r2": ...},
            "last_row": dict,
            "last_date": datetime,
            "num_cols_ext": list,
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

    # Модель
    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
            ("pre", preprocessor),
            ("rf", model),
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
        "trained_at": datetime.now(),
    }


def train_model_preview(
    df: pd.DataFrame,
    product_id: str,
    store_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Обучает новую модель БЕЗ сохранения в кэш.
    Используется для сравнения моделей (preview).
    """
    return train_model(df)


def get_or_train_model(
    df: pd.DataFrame,
    product_id: str,
    store_id: Optional[str] = None,
    force_retrain: bool = False,
) -> Dict[str, Any]:
    """
    Получает модель из кэша или обучает новую

    Args:
        df: DataFrame с данными продукта
        product_id: ID продукта
        store_id: ID магазина (опционально)
        force_retrain: принудительно переобучить

    Returns:
        Словарь с pipeline, метриками и метаданными
    """
    cache_key = get_cache_key(product_id, store_id)

    # Проверяем кэш
    if not force_retrain and cache_key in _model_cache:
        cached = _model_cache[cache_key]
        # Обновляем last_row и last_date из текущих данных (с lag features!)
        df_with_features = add_lag_features(df)
        df_with_features = add_date_features(df_with_features)
        df_sorted = df_with_features.sort_values(DATE_COL)
        cached["last_row"] = df_sorted.iloc[-1].to_dict()
        cached["last_date"] = df_sorted.iloc[-1][DATE_COL]
        return cached

    # Обучаем новую модель
    trained = train_model(df)
    _model_cache[cache_key] = trained

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
            }
            for key, val in _model_cache.items()
        },
    }


def get_feature_importance(product_id: str, store_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Возвращает важность признаков для визуализации модели

    Returns:
        {
            "features": [{"name": "demand_lag_1", "importance": 0.45}, ...],
            "model_type": "RandomForest",
            "n_estimators": 300,
            "total_features": 25
        }
    """
    cache_key = get_cache_key(product_id, store_id)

    if cache_key not in _model_cache:
        return {"error": "Model not trained yet. Call /forecast first."}

    trained = _model_cache[cache_key]
    pipeline = trained["pipeline"]
    num_cols_ext = trained["num_cols_ext"]

    # Получаем модель из pipeline
    rf_model = pipeline.named_steps["rf"]
    preprocessor = pipeline.named_steps["pre"]

    # Получаем имена признаков после OneHotEncoding
    cat_encoder = preprocessor.named_transformers_["cat"]
    cat_feature_names = list(cat_encoder.get_feature_names_out(CAT_COLS))
    all_feature_names = cat_feature_names + num_cols_ext

    # Важность признаков
    importances = rf_model.feature_importances_

    # Сортируем по важности
    feature_importance = [
        {"name": name, "importance": round(float(imp), 4)}
        for name, imp in zip(all_feature_names, importances)
    ]
    feature_importance.sort(key=lambda x: x["importance"], reverse=True)

    return {
        "product_id": product_id,
        "features": feature_importance[:20],  # Top 20
        "model_type": "RandomForestRegressor",
        "n_estimators": rf_model.n_estimators,
        "total_features": len(all_feature_names),
        "metrics": trained["metrics"],
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
