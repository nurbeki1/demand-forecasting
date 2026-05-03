import math
import os

import pandas as pd

from services import model_service

# Get absolute path relative to this file
_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(_DIR, "retail_store_inventory.csv")


def safe_num(x, default=0.0):
    """
    Гарантирует, что число не None / NaN
    """
    try:
        if x is None:
            return default
        if isinstance(x, float) and math.isnan(x):
            return default
        return float(x)
    except Exception:
        return default


def get_forecast_chart(product_id: str, horizon_days: int):
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"])

    sub = df[df["Product ID"] == product_id].copy()

    if sub.empty:
        raise ValueError(f"Product {product_id} not found")

    if len(sub) < 30:
        raise ValueError("Not enough data for this product")

    # Используем реальную ML модель
    trained = model_service.get_or_train_model(sub, product_id)
    future_df, preds = model_service.predict(trained, horizon_days)

    # История: последние 90 дней реального спроса
    history_df = sub.sort_values("Date").tail(90)
    history = [
        {
            "date": str(row["Date"].date()),
            "demand": safe_num(row.get("Demand Forecast")),
        }
        for _, row in history_df.iterrows()
    ]

    forecast = [
        {
            "date": str(d.date()),
            "predicted_demand": round(float(p), 2),
        }
        for d, p in zip(future_df[model_service.DATE_COL], preds)
    ]

    return {
        "product_id": product_id,
        "history": history,
        "forecast": forecast,
        "model_metrics": trained["metrics"],
    }