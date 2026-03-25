"""
Data Access Layer for RAG Context
Provides methods to query and analyze the dataset for AI chat context
"""
import pandas as pd
import numpy as np
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

# Get absolute path relative to this file
_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(_DIR, "retail_store_inventory.csv")

# Cache for DataFrame
_df_cache: Optional[pd.DataFrame] = None


def _get_df() -> pd.DataFrame:
    """Load and cache the dataset"""
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_csv(DATA_PATH)
        # Normalize column names
        _df_cache.columns = [c.strip().lower().replace(" ", "_") for c in _df_cache.columns]
        # Convert date
        if "date" in _df_cache.columns:
            _df_cache["date"] = pd.to_datetime(_df_cache["date"], errors="coerce")
    return _df_cache


def reload_data():
    """Force reload the dataset"""
    global _df_cache
    _df_cache = None
    return _get_df()


def get_all_products() -> List[str]:
    """Get list of all product IDs"""
    df = _get_df()
    return sorted(df["product_id"].unique().tolist())


def get_all_categories() -> List[str]:
    """Get list of all categories"""
    df = _get_df()
    if "category" in df.columns:
        return sorted(df["category"].dropna().unique().tolist())
    return []


def get_all_regions() -> List[str]:
    """Get list of all regions"""
    df = _get_df()
    if "region" in df.columns:
        return sorted(df["region"].dropna().unique().tolist())
    return []


def get_product_summary(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Get comprehensive summary for a product
    Returns: category, price, avg demand, trend, min/max demand, etc.
    """
    df = _get_df()
    product_df = df[df["product_id"] == product_id]

    if product_df.empty:
        return None

    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    # Calculate statistics
    avg_demand = product_df[demand_col].mean()
    min_demand = product_df[demand_col].min()
    max_demand = product_df[demand_col].max()
    std_demand = product_df[demand_col].std()
    total_records = len(product_df)

    # Get latest values
    latest = product_df.sort_values("date").iloc[-1] if "date" in product_df.columns else product_df.iloc[-1]

    # Calculate trend (last 7 days vs previous 7 days)
    trend_pct = 0.0
    if "date" in product_df.columns and len(product_df) >= 14:
        sorted_df = product_df.sort_values("date")
        recent = sorted_df.tail(7)[demand_col].mean()
        previous = sorted_df.iloc[-14:-7][demand_col].mean()
        if previous > 0:
            trend_pct = ((recent - previous) / previous) * 100

    return {
        "product_id": product_id,
        "category": str(latest.get("category", "Unknown")),
        "price": float(latest.get("price", 0)),
        "avg_demand": round(avg_demand, 2),
        "min_demand": round(min_demand, 2),
        "max_demand": round(max_demand, 2),
        "std_demand": round(std_demand, 2),
        "trend_pct": round(trend_pct, 2),
        "trend_direction": "up" if trend_pct > 2 else ("down" if trend_pct < -2 else "stable"),
        "total_records": total_records,
        "avg_inventory": round(product_df["inventory_level"].mean(), 2) if "inventory_level" in product_df.columns else 0,
        "regions": product_df["region"].unique().tolist() if "region" in product_df.columns else [],
    }


def get_category_stats(category: str) -> Optional[Dict[str, Any]]:
    """
    Get statistics for a category
    Returns: total products, avg demand, top products, etc.
    """
    df = _get_df()
    if "category" not in df.columns:
        return None

    cat_df = df[df["category"].str.lower() == category.lower()]
    if cat_df.empty:
        return None

    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    # Get product-level stats
    product_stats = cat_df.groupby("product_id").agg({
        demand_col: ["mean", "sum"],
        "price": "mean"
    }).reset_index()
    product_stats.columns = ["product_id", "avg_demand", "total_demand", "avg_price"]

    top_products = product_stats.nlargest(5, "avg_demand")["product_id"].tolist()

    return {
        "category": category,
        "total_products": cat_df["product_id"].nunique(),
        "total_records": len(cat_df),
        "avg_demand": round(cat_df[demand_col].mean(), 2),
        "total_demand": round(cat_df[demand_col].sum(), 2),
        "avg_price": round(cat_df["price"].mean(), 2) if "price" in cat_df.columns else 0,
        "top_products": top_products,
        "regions": cat_df["region"].unique().tolist() if "region" in cat_df.columns else [],
    }


def get_region_stats(region: str) -> Optional[Dict[str, Any]]:
    """
    Get statistics for a region
    Returns: total products, categories, avg demand, etc.
    """
    df = _get_df()
    if "region" not in df.columns:
        return None

    reg_df = df[df["region"].str.lower() == region.lower()]
    if reg_df.empty:
        return None

    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    # Get product-level stats
    product_stats = reg_df.groupby("product_id")[demand_col].mean().reset_index()
    top_products = product_stats.nlargest(5, demand_col)["product_id"].tolist()

    return {
        "region": region,
        "total_products": reg_df["product_id"].nunique(),
        "total_records": len(reg_df),
        "avg_demand": round(reg_df[demand_col].mean(), 2),
        "total_demand": round(reg_df[demand_col].sum(), 2),
        "categories": reg_df["category"].unique().tolist() if "category" in reg_df.columns else [],
        "top_products": top_products,
    }


def get_period_stats(start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
    """
    Get statistics for a specific period
    """
    df = _get_df()
    if "date" not in df.columns:
        return None

    try:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
    except:
        return None

    period_df = df[(df["date"] >= start) & (df["date"] <= end)]
    if period_df.empty:
        return None

    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    return {
        "start_date": str(start.date()),
        "end_date": str(end.date()),
        "total_records": len(period_df),
        "total_products": period_df["product_id"].nunique(),
        "avg_demand": round(period_df[demand_col].mean(), 2),
        "total_demand": round(period_df[demand_col].sum(), 2),
        "top_day": str(period_df.groupby("date")[demand_col].sum().idxmax().date()) if len(period_df) > 0 else None,
    }


def get_seasonality_analysis(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Analyze seasonality patterns for a product
    """
    df = _get_df()
    product_df = df[df["product_id"] == product_id]

    if product_df.empty or "seasonality" not in product_df.columns:
        return None

    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    # Group by seasonality
    season_stats = product_df.groupby("seasonality")[demand_col].agg(["mean", "std", "count"]).reset_index()
    season_stats.columns = ["season", "avg_demand", "std_demand", "count"]

    best_season = season_stats.loc[season_stats["avg_demand"].idxmax()]
    worst_season = season_stats.loc[season_stats["avg_demand"].idxmin()]

    return {
        "product_id": product_id,
        "seasonality_data": season_stats.to_dict("records"),
        "best_season": {
            "name": best_season["season"],
            "avg_demand": round(best_season["avg_demand"], 2)
        },
        "worst_season": {
            "name": worst_season["season"],
            "avg_demand": round(worst_season["avg_demand"], 2)
        },
        "seasonal_variation": round(
            (best_season["avg_demand"] - worst_season["avg_demand"]) / worst_season["avg_demand"] * 100, 2
        ) if worst_season["avg_demand"] > 0 else 0
    }


def get_weather_impact(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Analyze weather impact on product demand
    """
    df = _get_df()
    product_df = df[df["product_id"] == product_id]

    if product_df.empty or "weather_condition" not in product_df.columns:
        return None

    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    # Group by weather
    weather_stats = product_df.groupby("weather_condition")[demand_col].agg(["mean", "count"]).reset_index()
    weather_stats.columns = ["weather", "avg_demand", "count"]

    best_weather = weather_stats.loc[weather_stats["avg_demand"].idxmax()]
    worst_weather = weather_stats.loc[weather_stats["avg_demand"].idxmin()]

    return {
        "product_id": product_id,
        "weather_data": weather_stats.to_dict("records"),
        "best_weather": {
            "condition": best_weather["weather"],
            "avg_demand": round(best_weather["avg_demand"], 2)
        },
        "worst_weather": {
            "condition": worst_weather["weather"],
            "avg_demand": round(worst_weather["avg_demand"], 2)
        },
        "weather_impact_pct": round(
            (best_weather["avg_demand"] - worst_weather["avg_demand"]) / worst_weather["avg_demand"] * 100, 2
        ) if worst_weather["avg_demand"] > 0 else 0
    }


def get_top_performers(n: int = 5, by: str = "demand") -> List[Dict[str, Any]]:
    """
    Get top performing products
    by: 'demand', 'growth', 'stability'
    """
    df = _get_df()
    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    if by == "demand":
        # Top by average demand
        top = df.groupby("product_id")[demand_col].mean().nlargest(n)
        return [
            {"product_id": pid, "avg_demand": round(val, 2), "rank": i+1}
            for i, (pid, val) in enumerate(top.items())
        ]

    elif by == "growth":
        # Calculate growth for each product
        growth_data = []
        for pid in df["product_id"].unique():
            product_df = df[df["product_id"] == pid].sort_values("date")
            if len(product_df) >= 14:
                recent = product_df.tail(7)[demand_col].mean()
                previous = product_df.iloc[-14:-7][demand_col].mean()
                if previous > 0:
                    growth = ((recent - previous) / previous) * 100
                    growth_data.append({"product_id": pid, "growth_pct": round(growth, 2)})

        return sorted(growth_data, key=lambda x: x["growth_pct"], reverse=True)[:n]

    elif by == "stability":
        # Top by lowest coefficient of variation (most stable)
        stability = df.groupby("product_id")[demand_col].agg(["mean", "std"])
        stability["cv"] = stability["std"] / stability["mean"]
        stability = stability.nsmallest(n, "cv")
        return [
            {"product_id": pid, "cv": round(row["cv"], 3), "avg_demand": round(row["mean"], 2)}
            for pid, row in stability.iterrows()
        ]

    return []


def get_low_performers(n: int = 5) -> List[Dict[str, Any]]:
    """
    Get products with declining demand
    """
    df = _get_df()
    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    growth_data = []
    for pid in df["product_id"].unique():
        product_df = df[df["product_id"] == pid].sort_values("date")
        if len(product_df) >= 14:
            recent = product_df.tail(7)[demand_col].mean()
            previous = product_df.iloc[-14:-7][demand_col].mean()
            if previous > 0:
                growth = ((recent - previous) / previous) * 100
                if growth < 0:  # Only declining
                    growth_data.append({
                        "product_id": pid,
                        "decline_pct": round(abs(growth), 2),
                        "recent_demand": round(recent, 2),
                        "category": product_df["category"].iloc[0] if "category" in product_df.columns else None
                    })

    return sorted(growth_data, key=lambda x: x["decline_pct"], reverse=True)[:n]


def search_products(query: str) -> List[Dict[str, Any]]:
    """
    Search products by ID, category, or region
    """
    df = _get_df()
    query_lower = query.lower()

    results = []

    # Search by product ID
    matching_products = df[df["product_id"].str.lower().str.contains(query_lower, na=False)]["product_id"].unique()
    for pid in matching_products[:10]:
        summary = get_product_summary(pid)
        if summary:
            results.append(summary)

    # Search by category
    if "category" in df.columns:
        matching_cats = df[df["category"].str.lower().str.contains(query_lower, na=False)]["category"].unique()
        for cat in matching_cats[:3]:
            stats = get_category_stats(cat)
            if stats:
                results.append({"type": "category", **stats})

    return results


def compare_products(product_ids: List[str]) -> Dict[str, Any]:
    """
    Compare multiple products
    """
    df = _get_df()
    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    comparisons = []
    for pid in product_ids:
        summary = get_product_summary(pid)
        if summary:
            comparisons.append(summary)

    if len(comparisons) < 2:
        return {"error": "Need at least 2 valid products to compare"}

    # Find best/worst
    best_demand = max(comparisons, key=lambda x: x["avg_demand"])
    worst_demand = min(comparisons, key=lambda x: x["avg_demand"])
    best_trend = max(comparisons, key=lambda x: x["trend_pct"])

    return {
        "products": comparisons,
        "best_by_demand": best_demand["product_id"],
        "worst_by_demand": worst_demand["product_id"],
        "best_by_trend": best_trend["product_id"],
        "demand_difference_pct": round(
            (best_demand["avg_demand"] - worst_demand["avg_demand"]) / worst_demand["avg_demand"] * 100, 2
        ) if worst_demand["avg_demand"] > 0 else 0
    }


def compare_regions(regions: List[str]) -> Dict[str, Any]:
    """
    Compare multiple regions
    """
    comparisons = []
    for region in regions:
        stats = get_region_stats(region)
        if stats:
            comparisons.append(stats)

    if len(comparisons) < 2:
        return {"error": "Need at least 2 valid regions to compare"}

    best_demand = max(comparisons, key=lambda x: x["avg_demand"])
    worst_demand = min(comparisons, key=lambda x: x["avg_demand"])

    return {
        "regions": comparisons,
        "best_by_demand": best_demand["region"],
        "worst_by_demand": worst_demand["region"],
        "demand_difference_pct": round(
            (best_demand["avg_demand"] - worst_demand["avg_demand"]) / worst_demand["avg_demand"] * 100, 2
        ) if worst_demand["avg_demand"] > 0 else 0
    }


def get_dataset_overview() -> Dict[str, Any]:
    """
    Get overall dataset statistics including Amazon catalog
    """
    df = _get_df()
    demand_col = "demand_forecast" if "demand_forecast" in df.columns else "units_sold"

    # Try to get Amazon catalog info
    amazon_info = {}
    try:
        from services.amazon_data_service import load_amazon_products, get_category_overview
        amazon_df = load_amazon_products()
        if not amazon_df.empty:
            cat_overview = get_category_overview()
            amazon_info = {
                "amazon_products": len(amazon_df),
                "amazon_categories": cat_overview.get("total_categories", 0),
                "amazon_top_categories": [c["category"] for c in cat_overview.get("categories", [])[:5]]
            }
    except Exception:
        pass

    return {
        "total_records": len(df),
        "total_products": df["product_id"].nunique(),
        "total_categories": df["category"].nunique() if "category" in df.columns else 0,
        "total_regions": df["region"].nunique() if "region" in df.columns else 0,
        "date_range": {
            "start": str(df["date"].min().date()) if "date" in df.columns else None,
            "end": str(df["date"].max().date()) if "date" in df.columns else None,
        },
        "avg_demand": round(df[demand_col].mean(), 2),
        "categories": df["category"].unique().tolist() if "category" in df.columns else [],
        "regions": df["region"].unique().tolist() if "region" in df.columns else [],
        "products": df["product_id"].unique().tolist()[:20],  # First 20 for reference
        **amazon_info  # Include Amazon catalog info
    }
