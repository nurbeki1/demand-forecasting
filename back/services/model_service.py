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
    return df


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Рассчитывает метрики качества модели"""
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 4),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def train_model(df: pd.DataFrame, test_size: float = 0.2) -> Dict[str, Any]:
    """
    Обучает модель с train/test split и возвращает pipeline + метрики

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
    df = add_date_features(df)

    num_cols_ext = NUM_COLS + ["day", "month", "day_of_week"]

    # Извлекаем y до удаления колонки
    y = df[TARGET_COL]

    # Удаляем ненужные колонки
    for c in DROP_COLS:
        if c in df.columns:
            df = df.drop(columns=[c])

    # Подготовка данных
    X = df[CAT_COLS + num_cols_ext]

    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )

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
        # Обновляем last_row и last_date из текущих данных
        df_with_features = add_date_features(df)
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
    """Создаёт строки для будущих дат"""
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon)

    rows = []
    for d in future_dates:
        r = dict(last_row)
        r[DATE_COL] = d
        r["day"] = d.day
        r["month"] = d.month
        r["day_of_week"] = d.dayofweek
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
