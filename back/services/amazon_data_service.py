"""
Amazon Products Data Service
Handles product search and analysis using real Amazon dataset
"""
import pandas as pd
import re
from typing import Optional, List, Dict, Any
from pathlib import Path
from difflib import SequenceMatcher
import random

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
AMAZON_DIR = DATA_DIR / "amazon"
ECOMMERCE_DIR = DATA_DIR / "ecommerce"

# Cache for loaded data
_amazon_products_cache = None
_ecommerce_cache = None


def load_amazon_products(sample_size: int = None) -> pd.DataFrame:
    """Load Amazon products dataset (full dataset by default)"""
    global _amazon_products_cache

    if _amazon_products_cache is not None:
        return _amazon_products_cache

    products_path = AMAZON_DIR / "Amazon-Products.csv"
    if not products_path.exists():
        return pd.DataFrame()

    try:
        # Load full dataset (or sampled for testing)
        if sample_size:
            df = pd.read_csv(products_path, nrows=sample_size)
        else:
            df = pd.read_csv(products_path)  # Load all 551K products

        # Clean column names
        df.columns = df.columns.str.strip()

        # Clean price columns (remove ₹ and commas)
        if 'discount_price' in df.columns:
            df['discount_price'] = df['discount_price'].astype(str).str.replace('₹', '').str.replace(',', '').str.strip()
            df['discount_price'] = pd.to_numeric(df['discount_price'], errors='coerce')

        if 'actual_price' in df.columns:
            df['actual_price'] = df['actual_price'].astype(str).str.replace('₹', '').str.replace(',', '').str.strip()
            df['actual_price'] = pd.to_numeric(df['actual_price'], errors='coerce')

        # Clean ratings
        if 'no_of_ratings' in df.columns:
            df['no_of_ratings'] = df['no_of_ratings'].astype(str).str.replace(',', '').str.strip()
            df['no_of_ratings'] = pd.to_numeric(df['no_of_ratings'], errors='coerce').fillna(0).astype(int)

        if 'ratings' in df.columns:
            df['ratings'] = pd.to_numeric(df['ratings'], errors='coerce').fillna(0)

        # Add product_id
        df['product_id'] = ['AMZN' + str(i).zfill(6) for i in range(len(df))]

        _amazon_products_cache = df
        return df

    except Exception as e:
        print(f"Error loading Amazon products: {e}")
        return pd.DataFrame()


def load_ecommerce_data() -> pd.DataFrame:
    """Load e-commerce sales data"""
    global _ecommerce_cache

    if _ecommerce_cache is not None:
        return _ecommerce_cache

    data_path = ECOMMERCE_DIR / "data.csv"
    if not data_path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(data_path, encoding='unicode_escape')
        df.columns = df.columns.str.strip()

        # Parse dates
        if 'InvoiceDate' in df.columns:
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
            df['date'] = df['InvoiceDate'].dt.date
            df['month'] = df['InvoiceDate'].dt.month
            df['day_of_week'] = df['InvoiceDate'].dt.dayofweek

        _ecommerce_cache = df
        return df

    except Exception as e:
        print(f"Error loading e-commerce data: {e}")
        return pd.DataFrame()


def similarity_score(a: str, b: str) -> float:
    """Calculate similarity between two strings"""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# Russian to English product name mappings
RU_TO_EN_PRODUCTS = {
    # Phones
    "айфон": "iphone",
    "самсунг": "samsung",
    "сяоми": "xiaomi",
    "хуавей": "huawei",
    "телефон": "phone",
    "смартфон": "smartphone",
    # Computers
    "макбук": "macbook",
    "ноутбук": "laptop",
    "компьютер": "computer",
    # Audio
    "наушники": "headphones earbuds",
    "колонка": "speaker",
    "колонки": "speakers",
    # TV/Video
    "телевизор": "tv television",
    "монитор": "monitor",
    "камера": "camera",
    # Appliances
    "кондиционер": "air conditioner ac",
    "холодильник": "refrigerator fridge",
    "стиральная": "washing machine",
    "микроволновка": "microwave",
    "пылесос": "vacuum",
    # Clothing
    "кроссовки": "sneakers shoes",
    "найк": "nike",
    "адидас": "adidas",
    # Other
    "часы": "watch",
    "принтер": "printer",
    "планшет": "tablet ipad",
    "про": "pro",
    "макс": "max",
    "плюс": "plus",
}


def translate_query(query: str) -> str:
    """Translate Russian product terms to English for search"""
    query_lower = query.lower()
    for ru, en in RU_TO_EN_PRODUCTS.items():
        if ru in query_lower:
            query_lower = query_lower.replace(ru, en)
    return query_lower


def fix_amazon_image_url(url: str) -> str:
    """Fix Amazon image URLs that have invalid path segments"""
    if not url or not isinstance(url, str):
        return ""
    # Remove the IMAGERENDERING segment that causes 400 errors
    # Convert: https://m.media-amazon.com/images/W/IMAGERENDERING_521856-T2/images/I/xxx.jpg
    # To: https://m.media-amazon.com/images/I/xxx.jpg
    import re
    fixed = re.sub(r'/images/W/IMAGERENDERING[^/]*/images/', '/images/', url)
    return fixed


def search_amazon_products(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Search Amazon products by name, category, or description
    Supports both Russian and English queries
    Uses smart filtering to find relevant products efficiently
    """
    df = load_amazon_products()
    if df.empty:
        return []

    # Translate Russian terms to English
    query_translated = translate_query(query)
    query_lower = query_translated.lower().strip()
    query_words = [w for w in query_lower.split() if len(w) >= 2]

    # Identify primary product term (brands and product types)
    primary_terms = [
        # Tech brands
        "iphone", "samsung", "xiaomi", "apple", "macbook", "huawei", "oneplus", "oppo", "vivo",
        "sony", "lg", "panasonic", "philips", "bosch", "dell", "hp", "lenovo", "asus", "acer",
        # Fashion brands
        "nike", "adidas", "puma", "reebok", "fila", "skechers", "new balance", "asics",
        "levis", "zara", "h&m", "gucci", "louis vuitton",
        # Product types
        "laptop", "headphones", "earbuds", "tv", "television", "refrigerator",
        "air conditioner", "washing", "phone", "tablet", "watch", "camera",
        "sneakers", "shoes", "shirt", "dress", "jeans",
    ]
    primary_match = None
    for term in primary_terms:
        if term in query_lower:
            primary_match = term
            break

    # SMART FILTER: Pre-filter dataframe to only include relevant products
    # This avoids iterating through all 50K products
    if primary_match:
        # Filter by primary term in name (vectorized, fast)
        mask = df['name'].str.lower().str.contains(primary_match, na=False)
        filtered_df = df[mask].copy()
        if len(filtered_df) == 0:
            filtered_df = df  # Fallback to full dataset
    else:
        # Filter by any query word
        mask = pd.Series([False] * len(df))
        for word in query_words:
            if len(word) >= 3:
                mask |= df['name'].str.lower().str.contains(word, na=False)
        filtered_df = df[mask].copy() if mask.any() else df
    # Accessory keywords to penalize when searching for main products
    accessory_keywords = ["case", "cover", "charger", "cable", "adapter", "stand",
                          "holder", "protector", "mount", "strap", "band", "sleeve"]

    results = []

    # Iterate through pre-filtered dataframe (much smaller than 50K)
    for idx, row in filtered_df.iterrows():
        name = str(row.get('name', '')).lower()
        category = str(row.get('main_category', '')).lower()
        subcategory = str(row.get('sub_category', '')).lower()

        # Calculate score
        score = 0.0

        # Check if product name STARTS with primary term (e.g., "Apple iPhone 13")
        # This helps find actual products vs accessories
        if primary_match:
            name_start = name[:30]  # First 30 chars
            if primary_match in name_start:
                score += 0.5  # Strong bonus for products starting with the term

            # Penalize accessories when searching for main products
            is_accessory = any(acc in name for acc in accessory_keywords)
            if is_accessory and primary_match in ["iphone", "samsung", "apple", "macbook", "laptop"]:
                score -= 0.3  # Penalty for accessories

        # Exact phrase match in name
        if query_lower in name:
            score += 0.4

        # Word matches
        for word in query_words:
            if len(word) >= 3:  # Skip short words
                if word in name:
                    score += 0.15
                if word in category:
                    score += 0.05
                if word in subcategory:
                    score += 0.05

        # Bonus for higher ratings (better quality products)
        rating = row.get('ratings', 0)
        if rating >= 4.0:
            score += 0.1

        # Bonus for more reviews (popular products)
        num_ratings = row.get('no_of_ratings', 0)
        if num_ratings >= 1000:
            score += 0.1
        elif num_ratings >= 100:
            score += 0.05

        if score > 0.2:  # Minimum threshold
            results.append({
                'product_id': row.get('product_id', ''),
                'name': str(row.get('name', ''))[:100],  # Truncate long names
                'main_category': row.get('main_category', ''),
                'sub_category': row.get('sub_category', ''),
                'price': row.get('discount_price') or row.get('actual_price') or 0,
                'original_price': row.get('actual_price', 0),
                'rating': row.get('ratings', 0),
                'num_ratings': row.get('no_of_ratings', 0),
                'image_url': fix_amazon_image_url(row.get('image', '')),
                'link': row.get('link', ''),
                'score': min(score, 1.0)
            })

        # Early exit for performance
        if len(results) >= 200:
            break

    # Sort by score descending, then by num_ratings
    results.sort(key=lambda x: (x['score'], x['num_ratings']), reverse=True)
    return results[:top_k]


def get_amazon_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Get Amazon product details by ID"""
    df = load_amazon_products()
    if df.empty:
        return None

    product = df[df['product_id'] == product_id]
    if product.empty:
        return None

    row = product.iloc[0]
    return {
        'product_id': row.get('product_id', ''),
        'name': str(row.get('name', '')),
        'main_category': row.get('main_category', ''),
        'sub_category': row.get('sub_category', ''),
        'price': row.get('discount_price') or row.get('actual_price') or 0,
        'original_price': row.get('actual_price', 0),
        'rating': row.get('ratings', 0),
        'num_ratings': row.get('no_of_ratings', 0),
        'image_url': fix_amazon_image_url(row.get('image', '')),
        'link': row.get('link', ''),
    }


def get_amazon_product_analysis(product_id: str) -> Dict[str, Any]:
    """Get comprehensive analysis for an Amazon product"""
    product = get_amazon_product_by_id(product_id)
    if not product:
        return {'error': f'Product {product_id} not found'}

    df = load_amazon_products()

    # Get category statistics
    category = product['main_category']
    subcategory = product['sub_category']

    category_products = df[df['main_category'] == category]
    subcategory_products = df[df['sub_category'] == subcategory]

    # Price analysis
    if len(category_products) > 0:
        cat_avg_price = category_products['discount_price'].mean()
        cat_min_price = category_products['discount_price'].min()
        cat_max_price = category_products['discount_price'].max()
    else:
        cat_avg_price = product['price']
        cat_min_price = product['price']
        cat_max_price = product['price']

    price_position = 'budget'
    if product['price'] > cat_avg_price * 1.3:
        price_position = 'premium'
    elif product['price'] > cat_avg_price * 0.7:
        price_position = 'mid-range'

    # Rating analysis
    if len(category_products) > 0:
        cat_avg_rating = category_products['ratings'].mean()
    else:
        cat_avg_rating = product['rating']

    rating_position = 'average'
    if product['rating'] >= 4.5:
        rating_position = 'excellent'
    elif product['rating'] >= 4.0:
        rating_position = 'good'
    elif product['rating'] < 3.5:
        rating_position = 'below average'

    # Discount analysis
    discount_pct = 0
    if product['original_price'] and product['original_price'] > 0:
        discount_pct = round((1 - product['price'] / product['original_price']) * 100, 1)

    # Ranking in category
    if len(subcategory_products) > 0:
        subcategory_products_sorted = subcategory_products.sort_values('no_of_ratings', ascending=False)
        rank = 1
        for _, row in subcategory_products_sorted.iterrows():
            if row['product_id'] == product_id:
                break
            rank += 1
        total_in_subcategory = len(subcategory_products)
    else:
        rank = 1
        total_in_subcategory = 1

    # Similar products
    similar = search_amazon_products(subcategory, top_k=5)
    similar = [p for p in similar if p['product_id'] != product_id][:3]

    # Generate simulated demand (since Amazon data doesn't have sales)
    # In production, this would come from actual sales data
    base_demand = int(product['num_ratings'] / 30) if product['num_ratings'] > 0 else random.randint(10, 100)
    simulated_demand = {
        'avg_daily': base_demand,
        'trend': random.choice(['up', 'stable', 'down']),
        'trend_pct': round(random.uniform(-10, 15), 1),
    }

    # Recommendations
    recommendations = []
    if discount_pct > 0:
        recommendations.append(f"Currently {discount_pct}% off - good time to stock up")
    if rating_position == 'excellent':
        recommendations.append("High customer satisfaction - strong seller potential")
    if price_position == 'premium':
        recommendations.append("Premium pricing - target affluent customers")
    elif price_position == 'budget':
        recommendations.append("Competitive pricing - good for volume sales")

    return {
        'product': product,
        'category_stats': {
            'main_category': category,
            'sub_category': subcategory,
            'products_in_category': len(category_products),
            'products_in_subcategory': len(subcategory_products),
            'avg_category_price': round(cat_avg_price, 2) if pd.notna(cat_avg_price) else 0,
            'price_range': f"₹{cat_min_price:,.0f} - ₹{cat_max_price:,.0f}" if pd.notna(cat_min_price) else "N/A",
        },
        'price_analysis': {
            'current_price': product['price'],
            'original_price': product['original_price'],
            'discount_percent': discount_pct,
            'position': price_position,
            'vs_category_avg': round((product['price'] / cat_avg_price - 1) * 100, 1) if cat_avg_price > 0 else 0,
        },
        'rating_analysis': {
            'rating': product['rating'],
            'num_ratings': product['num_ratings'],
            'position': rating_position,
            'vs_category_avg': round(product['rating'] - cat_avg_rating, 2) if pd.notna(cat_avg_rating) else 0,
        },
        'ranking': {
            'position': rank,
            'total': total_in_subcategory,
            'percentile': round((1 - rank / total_in_subcategory) * 100) if total_in_subcategory > 0 else 0,
        },
        'demand_estimate': simulated_demand,
        'similar_products': similar,
        'recommendations': recommendations,
    }


def get_ecommerce_sales_analysis(stock_code: str = None) -> Dict[str, Any]:
    """Get sales analysis from e-commerce data"""
    df = load_ecommerce_data()
    if df.empty:
        return {'error': 'No e-commerce data available'}

    if stock_code:
        product_sales = df[df['StockCode'] == stock_code]
    else:
        product_sales = df

    if product_sales.empty:
        return {'error': f'No sales data for {stock_code}'}

    # Aggregate stats
    total_quantity = product_sales['Quantity'].sum()
    total_revenue = (product_sales['Quantity'] * product_sales['UnitPrice']).sum()
    unique_customers = product_sales['CustomerID'].nunique()
    countries = product_sales['Country'].value_counts().head(5).to_dict()

    # Daily sales
    daily_sales = product_sales.groupby('date').agg({
        'Quantity': 'sum',
        'UnitPrice': 'mean',
        'InvoiceNo': 'nunique'
    }).reset_index()

    return {
        'stock_code': stock_code,
        'total_quantity': int(total_quantity),
        'total_revenue': round(total_revenue, 2),
        'unique_customers': int(unique_customers),
        'top_countries': countries,
        'daily_sales': daily_sales.tail(30).to_dict('records') if len(daily_sales) > 0 else [],
    }


def get_category_overview() -> Dict[str, Any]:
    """Get overview of all categories"""
    df = load_amazon_products()
    if df.empty:
        return {'error': 'No data available'}

    categories = df.groupby('main_category').agg({
        'product_id': 'count',
        'discount_price': 'mean',
        'ratings': 'mean',
        'no_of_ratings': 'sum'
    }).reset_index()

    categories.columns = ['category', 'product_count', 'avg_price', 'avg_rating', 'total_ratings']
    categories = categories.sort_values('product_count', ascending=False)

    return {
        'total_products': len(df),
        'total_categories': len(categories),
        'categories': categories.head(20).to_dict('records')
    }


def get_amazon_top_products(n: int = 5, by: str = "popularity") -> List[Dict[str, Any]]:
    """
    Get top products from Amazon dataset
    by: 'popularity' (most ratings), 'rating' (highest rated), 'value' (best price/rating ratio)
    """
    df = load_amazon_products()
    if df.empty:
        return []

    # Filter out products without ratings or prices
    df_clean = df[(df['ratings'] > 0) & (df['no_of_ratings'] > 0)].copy()

    if by == "popularity":
        # Top by number of ratings (most popular)
        top = df_clean.nlargest(n, 'no_of_ratings')
    elif by == "rating":
        # Top by rating (minimum 100 reviews for reliability)
        df_reliable = df_clean[df_clean['no_of_ratings'] >= 100]
        if len(df_reliable) >= n:
            top = df_reliable.nlargest(n, 'ratings')
        else:
            top = df_clean.nlargest(n, 'ratings')
    elif by == "value":
        # Best value: high rating, reasonable price, many reviews
        df_clean['value_score'] = (df_clean['ratings'] * df_clean['no_of_ratings'].apply(lambda x: min(x, 10000) / 10000))
        top = df_clean.nlargest(n, 'value_score')
    else:
        top = df_clean.nlargest(n, 'no_of_ratings')

    results = []
    for i, (_, row) in enumerate(top.iterrows()):
        results.append({
            'rank': i + 1,
            'product_id': row.get('product_id', ''),
            'name': str(row.get('name', ''))[:80],
            'category': row.get('main_category', ''),
            'price': row.get('discount_price') or row.get('actual_price') or 0,
            'rating': row.get('ratings', 0),
            'num_ratings': int(row.get('no_of_ratings', 0)),
            'image_url': fix_amazon_image_url(row.get('image', '')),
        })

    return results


def get_amazon_low_performers(n: int = 5) -> List[Dict[str, Any]]:
    """
    Get lowest rated products (that have significant reviews)
    These are products that may need attention or removal
    """
    df = load_amazon_products()
    if df.empty:
        return []

    # Only consider products with enough reviews to be meaningful
    df_clean = df[(df['ratings'] > 0) & (df['no_of_ratings'] >= 50)].copy()

    # Get lowest rated
    low = df_clean.nsmallest(n, 'ratings')

    results = []
    for i, (_, row) in enumerate(low.iterrows()):
        results.append({
            'rank': i + 1,
            'product_id': row.get('product_id', ''),
            'name': str(row.get('name', ''))[:80],
            'category': row.get('main_category', ''),
            'price': row.get('discount_price') or row.get('actual_price') or 0,
            'rating': row.get('ratings', 0),
            'num_ratings': int(row.get('no_of_ratings', 0)),
            'issue': 'low_rating',
        })

    return results


def estimate_product_trend(row: pd.Series) -> Dict[str, Any]:
    """
    Estimate trend for a product based on available data.
    Since we don't have time-series data, we use proxies:
    - High ratings + high review count = trending up (popular and liked)
    - Low ratings + high review count = trending down (popular but declining quality)
    - High ratings + low review count = stable/new (quality but less known)
    """
    rating = row.get('ratings', 0) or 0
    num_ratings = int(row.get('no_of_ratings', 0) or 0)
    price = row.get('discount_price') or row.get('actual_price') or 0

    # Calculate trend score
    # High rating + many reviews = strong positive trend
    # Low rating + many reviews = negative trend (people buying but not happy)
    # High rating + few reviews = stable/emerging

    if rating >= 4.0 and num_ratings >= 1000:
        trend = "rising"
        trend_pct = random.uniform(8, 25)  # Simulated growth
        alert = "hot" if num_ratings >= 10000 else None
    elif rating >= 4.0 and num_ratings >= 100:
        trend = "stable"
        trend_pct = random.uniform(-3, 5)
        alert = None
    elif rating < 3.0 and num_ratings >= 100:
        trend = "declining"
        trend_pct = random.uniform(-20, -5)
        alert = "warning"
    elif rating < 2.5:
        trend = "critical"
        trend_pct = random.uniform(-30, -15)
        alert = "critical"
    else:
        trend = "stable"
        trend_pct = random.uniform(-5, 5)
        alert = None

    return {
        "direction": trend,
        "percent": round(trend_pct, 1),
        "alert": alert,
        "confidence": "high" if num_ratings >= 500 else "medium" if num_ratings >= 50 else "low"
    }


def get_trending_products(n: int = 5, direction: str = "rising") -> List[Dict[str, Any]]:
    """
    Get trending products based on simulated trend analysis.
    direction: 'rising', 'declining', 'hot' (most popular rising)
    """
    df = load_amazon_products()
    if df.empty:
        return []

    df_clean = df[(df['ratings'] > 0) & (df['no_of_ratings'] >= 50)].copy()

    if direction == "rising":
        # Products with high ratings and good engagement
        df_rising = df_clean[(df_clean['ratings'] >= 4.0) & (df_clean['no_of_ratings'] >= 500)]
        top = df_rising.nlargest(n, 'no_of_ratings')
    elif direction == "declining":
        # Products with low ratings but significant reviews
        df_declining = df_clean[df_clean['ratings'] < 3.5]
        top = df_declining.nsmallest(n, 'ratings')
    elif direction == "hot":
        # Most popular + high rated
        df_hot = df_clean[(df_clean['ratings'] >= 4.0) & (df_clean['no_of_ratings'] >= 10000)]
        top = df_hot.nlargest(n, 'no_of_ratings')
    else:
        top = df_clean.nlargest(n, 'no_of_ratings')

    results = []
    for i, (_, row) in enumerate(top.iterrows()):
        trend = estimate_product_trend(row)
        results.append({
            'rank': i + 1,
            'product_id': row.get('product_id', ''),
            'name': str(row.get('name', ''))[:80],
            'category': row.get('main_category', ''),
            'price': row.get('discount_price') or row.get('actual_price') or 0,
            'rating': row.get('ratings', 0),
            'num_ratings': int(row.get('no_of_ratings', 0)),
            'image_url': fix_amazon_image_url(row.get('image', '')),
            'trend': trend,
        })

    return results


def get_product_alerts() -> List[Dict[str, Any]]:
    """
    Get products that need attention (alerts).
    Returns products with significant issues or opportunities.
    """
    df = load_amazon_products()
    if df.empty:
        return []

    alerts = []

    # Critical: Very low rated products with many reviews
    df_critical = df[(df['ratings'] < 2.5) & (df['no_of_ratings'] >= 100)]
    for _, row in df_critical.head(3).iterrows():
        alerts.append({
            'type': 'critical',
            'icon': '🚨',
            'product_id': row.get('product_id', ''),
            'name': str(row.get('name', ''))[:60],
            'message': f"Критический рейтинг {row.get('ratings', 0)}/5 - требуется срочное внимание",
            'rating': row.get('ratings', 0),
        })

    # Warning: Declining products
    df_warning = df[(df['ratings'] >= 2.5) & (df['ratings'] < 3.5) & (df['no_of_ratings'] >= 50)]
    for _, row in df_warning.head(3).iterrows():
        alerts.append({
            'type': 'warning',
            'icon': '⚠️',
            'product_id': row.get('product_id', ''),
            'name': str(row.get('name', ''))[:60],
            'message': f"Низкий рейтинг {row.get('ratings', 0)}/5 - рекомендуется проверка",
            'rating': row.get('ratings', 0),
        })

    # Hot: Trending up products
    df_hot = df[(df['ratings'] >= 4.5) & (df['no_of_ratings'] >= 10000)]
    for _, row in df_hot.head(3).iterrows():
        alerts.append({
            'type': 'hot',
            'icon': '🔥',
            'product_id': row.get('product_id', ''),
            'name': str(row.get('name', ''))[:60],
            'message': f"Популярный товар! {int(row.get('no_of_ratings', 0)):,} отзывов",
            'rating': row.get('ratings', 0),
        })

    return alerts[:10]  # Max 10 alerts
