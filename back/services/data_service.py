"""
Data Access Layer for RAG Context
Redirects to Amazon data service for real product data (551K products)
"""
from typing import Optional, List, Dict, Any

# Import all functions from Amazon data service
from services.amazon_data_service import (
    load_amazon_products,
    search_amazon_products,
    get_amazon_product_by_id,
    get_amazon_product_analysis,
    get_amazon_top_products,
    get_amazon_low_performers,
    get_trending_products,
    get_category_overview,
)


def get_all_products() -> List[str]:
    """Get list of all product IDs"""
    df = load_amazon_products()
    if df.empty:
        return []
    return df["product_id"].tolist()[:1000]  # Return first 1000 for performance


def get_all_categories() -> List[str]:
    """Get list of all categories"""
    df = load_amazon_products()
    if df.empty:
        return []
    return sorted(df["main_category"].dropna().unique().tolist())


def get_all_regions() -> List[str]:
    """Get list of all regions (not applicable for Amazon data)"""
    return []


def get_product_name(product_id: str) -> str:
    """Get product name by ID"""
    product = get_amazon_product_by_id(product_id)
    if product:
        return product.get("name", product_id)
    return product_id


def get_product_by_name(name: str) -> Optional[str]:
    """Find product ID by name (partial match)"""
    results = search_amazon_products(name, top_k=1)
    if results:
        return results[0].get("product_id")
    return None


def get_all_products_with_names() -> List[Dict[str, str]]:
    """Get all products with their names"""
    df = load_amazon_products()
    if df.empty:
        return []
    return df[["product_id", "name", "main_category"]].head(100).to_dict("records")


def get_product_summary(product_id: str) -> Optional[Dict[str, Any]]:
    """Get comprehensive summary for a product"""
    product = get_amazon_product_by_id(product_id)
    if not product:
        return None

    return {
        "product_id": product_id,
        "name": product.get("name", ""),
        "category": product.get("main_category", ""),
        "subcategory": product.get("sub_category", ""),
        "price": product.get("price", 0),
        "original_price": product.get("original_price", 0),
        "rating": product.get("rating", 0),
        "num_ratings": product.get("num_ratings", 0),
        "avg_demand": int(product.get("num_ratings", 0) / 30),  # Estimated
        "trend_pct": 0,
        "trend_direction": "stable",
        "image_url": product.get("image_url", ""),
    }


def get_category_stats(category: str) -> Optional[Dict[str, Any]]:
    """Get statistics for a category"""
    df = load_amazon_products()
    if df.empty:
        return None

    cat_df = df[df["main_category"].str.lower() == category.lower()]
    if cat_df.empty:
        # Try partial match
        cat_df = df[df["main_category"].str.lower().str.contains(category.lower(), na=False)]

    if cat_df.empty:
        return None

    top_products = cat_df.nlargest(5, "no_of_ratings")["product_id"].tolist()

    return {
        "category": category,
        "total_products": len(cat_df),
        "avg_price": round(cat_df["discount_price"].mean(), 2) if "discount_price" in cat_df.columns else 0,
        "avg_rating": round(cat_df["ratings"].mean(), 2) if "ratings" in cat_df.columns else 0,
        "top_products": top_products,
        "subcategories": cat_df["sub_category"].unique().tolist()[:10],
    }


def get_region_stats(region: str) -> Optional[Dict[str, Any]]:
    """Get statistics for a region (not applicable for Amazon data)"""
    return None


def get_period_stats(start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
    """Get statistics for a specific period (not applicable for Amazon data)"""
    return None


def get_seasonality_analysis(product_id: str) -> Optional[Dict[str, Any]]:
    """Analyze seasonality patterns (not applicable for Amazon data)"""
    return None


def get_weather_impact(product_id: str) -> Optional[Dict[str, Any]]:
    """Analyze weather impact (not applicable for Amazon data)"""
    return None


def get_top_performers(n: int = 5, by: str = "demand") -> List[Dict[str, Any]]:
    """Get top performing products"""
    if by == "demand" or by == "popularity":
        return get_amazon_top_products(n, by="popularity")
    elif by == "rating":
        return get_amazon_top_products(n, by="rating")
    elif by == "growth":
        return get_trending_products(n, direction="rising")
    else:
        return get_amazon_top_products(n, by="popularity")


def get_low_performers(n: int = 5) -> List[Dict[str, Any]]:
    """Get products with issues"""
    return get_amazon_low_performers(n)


def search_products(query: str) -> List[Dict[str, Any]]:
    """Search products by name, category, or description"""
    return search_amazon_products(query, top_k=10)


def compare_products(product_ids: List[str]) -> Dict[str, Any]:
    """Compare multiple products"""
    comparisons = []
    for pid in product_ids:
        product = get_amazon_product_by_id(pid)
        if product:
            comparisons.append(product)

    if len(comparisons) < 2:
        return {"error": "Need at least 2 valid products to compare"}

    best_price = min(comparisons, key=lambda x: x.get("price", float("inf")))
    best_rating = max(comparisons, key=lambda x: x.get("rating", 0))

    return {
        "products": comparisons,
        "best_by_price": best_price.get("product_id"),
        "best_by_rating": best_rating.get("product_id"),
    }


def compare_regions(regions: List[str]) -> Dict[str, Any]:
    """Compare multiple regions (not applicable for Amazon data)"""
    return {"error": "Region comparison not available for Amazon data"}


def get_dataset_overview() -> Dict[str, Any]:
    """Get overall dataset statistics"""
    overview = get_category_overview()
    if "error" in overview:
        return overview

    df = load_amazon_products()

    return {
        "total_records": len(df),
        "total_products": overview.get("total_products", 0),
        "total_categories": overview.get("total_categories", 0),
        "categories": [c["category"] for c in overview.get("categories", [])[:10]],
        "date_range": {"start": None, "end": None},
        "avg_price": round(df["discount_price"].mean(), 2) if not df.empty else 0,
        "avg_rating": round(df["ratings"].mean(), 2) if not df.empty else 0,
    }


def reload_data():
    """Force reload the dataset"""
    global _amazon_products_cache
    from services import amazon_data_service
    amazon_data_service._amazon_products_cache = None
    return load_amazon_products()