import pandas as pd
import math
import os

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
    df = pd.read_csv(DATA_PATH)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]


    if "product_id" not in df.columns:
        raise ValueError("CSV must contain 'Product ID' column")

    if "demand_forecast" not in df.columns:
        raise ValueError("CSV must contain 'Demand Forecast' column")

    product_df = df[df["product_id"] == product_id].copy()

    if product_df.empty:
        raise ValueError(f"Product {product_id} not found")

    history = []
    for i, row in product_df.iterrows():
        history.append({
            "date": str(row.get("date", f"day-{i}")),
            "demand": safe_num(row.get("demand_forecast"))
        })

    mean_demand = safe_num(product_df["demand_forecast"].mean())

    forecast = []
    for i in range(horizon_days):
        forecast.append({
            "date": f"day+{i+1}",
            "predicted_demand": mean_demand
        })

    return {
        "product_id": product_id,
        "history": history,
        "forecast": forecast
    }
