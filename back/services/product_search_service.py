"""
Smart Product Search Service
Finds products by name/description and provides comprehensive analysis
"""
import pandas as pd
import re
from typing import Optional, List, Dict, Any
from pathlib import Path
from difflib import SequenceMatcher

# Load data
DATA_DIR = Path(__file__).parent.parent / "data"

def load_catalog() -> pd.DataFrame:
    """Load product catalog"""
    catalog_path = DATA_DIR / "products_catalog.csv"
    if catalog_path.exists():
        return pd.read_csv(catalog_path)
    return pd.DataFrame()

def load_sales() -> pd.DataFrame:
    """Load sales data"""
    # Try multiple possible paths
    possible_paths = [
        DATA_DIR / "demand_forecasting_dataset.csv",
        DATA_DIR.parent / "retail_store_inventory.csv",
    ]
    for path in possible_paths:
        if path.exists():
            df = pd.read_csv(path)
            # Normalize column names (remove spaces, lowercase)
            df.columns = df.columns.str.strip().str.replace(' ', '_')
            return df
    return pd.DataFrame()

def load_events() -> pd.DataFrame:
    """Load events calendar"""
    events_path = DATA_DIR / "events_calendar.csv"
    if events_path.exists():
        return pd.read_csv(events_path)
    return pd.DataFrame()

def load_weather_factors() -> pd.DataFrame:
    """Load weather impact factors"""
    weather_path = DATA_DIR / "weather_factors.csv"
    if weather_path.exists():
        return pd.read_csv(weather_path)
    return pd.DataFrame()


def similarity_score(a: str, b: str) -> float:
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def search_product(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for products by name, brand, category, or description
    Returns top_k matches with similarity scores
    """
    catalog = load_catalog()
    if catalog.empty:
        return []

    query_lower = query.lower().strip()
    results = []

    for _, row in catalog.iterrows():
        # Calculate similarity scores for different fields
        name_score = similarity_score(query_lower, str(row['name']).lower())
        brand_score = similarity_score(query_lower, str(row['brand']).lower())

        # Check if query is in name, brand, or description
        name_contains = query_lower in str(row['name']).lower()
        brand_contains = query_lower in str(row['brand']).lower()
        desc_contains = query_lower in str(row.get('description', '')).lower()
        tags_contains = query_lower in str(row.get('tags', '')).lower()

        # Calculate combined score
        score = max(name_score, brand_score) * 0.6
        if name_contains:
            score += 0.4
        if brand_contains:
            score += 0.2
        if desc_contains:
            score += 0.1
        if tags_contains:
            score += 0.1

        # Check for partial word matches
        query_words = query_lower.split()
        name_words = str(row['name']).lower().split()
        for qw in query_words:
            for nw in name_words:
                if qw in nw or nw in qw:
                    score += 0.15

        if score > 0.2:  # Minimum threshold
            results.append({
                'product_id': row['product_id'],
                'name': row['name'],
                'brand': row['brand'],
                'category': row['category'],
                'subcategory': row.get('subcategory', ''),
                'price': row['price'],
                'description': row.get('description', ''),
                'tags': row.get('tags', ''),
                'score': min(score, 1.0)
            })

    # Sort by score and return top_k
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]


def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Get product details by ID"""
    catalog = load_catalog()
    if catalog.empty:
        return None

    product = catalog[catalog['product_id'] == product_id.upper()]
    if product.empty:
        return None

    row = product.iloc[0]
    return {
        'product_id': row['product_id'],
        'name': row['name'],
        'brand': row['brand'],
        'category': row['category'],
        'subcategory': row.get('subcategory', ''),
        'price': row['price'],
        'description': row.get('description', ''),
        'tags': row.get('tags', '')
    }


def get_comprehensive_analysis(product_id: str) -> Dict[str, Any]:
    """
    Get comprehensive analysis for a product
    Includes: sales stats, trends, regional performance, seasonality, forecasts
    """
    catalog = load_catalog()
    sales = load_sales()
    events = load_events()

    # Get product info
    product_info = get_product_by_id(product_id)
    if not product_info:
        return {'error': f'Product {product_id} not found'}

    # Get sales data for this product
    # Handle different column name formats
    product_col = 'Product_ID' if 'Product_ID' in sales.columns else 'Product_Id' if 'Product_Id' in sales.columns else None
    demand_col = 'Units_Sold' if 'Units_Sold' in sales.columns else 'Demand_Forecast' if 'Demand_Forecast' in sales.columns else None
    region_col = 'Region' if 'Region' in sales.columns else None
    date_col = 'Date' if 'Date' in sales.columns else None

    if not product_col or not demand_col:
        return {
            'product': product_info,
            'error': 'Sales data columns not found'
        }

    product_sales = sales[sales[product_col] == product_id]

    if product_sales.empty:
        return {
            'product': product_info,
            'error': 'No sales data available for this product'
        }

    # Basic stats
    avg_demand = product_sales[demand_col].mean()
    min_demand = product_sales[demand_col].min()
    max_demand = product_sales[demand_col].max()
    std_demand = product_sales[demand_col].std()
    total_records = len(product_sales)

    # Regional analysis
    regional_stats = []
    if region_col and region_col in product_sales.columns:
        for region in product_sales[region_col].unique():
            region_data = product_sales[product_sales[region_col] == region]
            region_avg = region_data[demand_col].mean()
            diff_from_avg = ((region_avg - avg_demand) / avg_demand * 100) if avg_demand > 0 else 0
            regional_stats.append({
                'region': region,
                'avg_demand': round(region_avg, 1),
                'diff_percent': round(diff_from_avg, 1),
                'total_sales': int(region_data[demand_col].sum())
            })
        regional_stats.sort(key=lambda x: x['avg_demand'], reverse=True)

    # Trend calculation (compare first half vs second half)
    half = len(product_sales) // 2
    if half > 0:
        first_half_avg = product_sales.iloc[:half][demand_col].mean()
        second_half_avg = product_sales.iloc[half:][demand_col].mean()
        trend_pct = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
        trend_direction = 'up' if trend_pct > 2 else ('down' if trend_pct < -2 else 'stable')
    else:
        trend_pct = 0
        trend_direction = 'stable'

    # Category ranking
    category = product_info['category']
    category_products = sales.groupby(product_col)[demand_col].mean().reset_index()
    category_products = category_products.sort_values(demand_col, ascending=False)

    # Find rank
    rank = 1
    for idx, row in category_products.iterrows():
        if row[product_col] == product_id:
            break
        rank += 1
    total_in_category = len(category_products)

    # Price analysis
    price = product_info['price']
    category_catalog = catalog[catalog['category'] == category]
    if not category_catalog.empty:
        avg_category_price = category_catalog['price'].mean()
        price_position = 'premium' if price > avg_category_price * 1.2 else ('budget' if price < avg_category_price * 0.8 else 'mid-range')
    else:
        avg_category_price = price
        price_position = 'mid-range'

    # Seasonality (by month if date available)
    seasonality = {}
    if date_col and date_col in product_sales.columns:
        try:
            product_sales_copy = product_sales.copy()
            product_sales_copy['month'] = pd.to_datetime(product_sales_copy[date_col]).dt.month
            monthly = product_sales_copy.groupby('month')[demand_col].mean()
            if len(monthly) > 0:
                best_month = monthly.idxmax()
                worst_month = monthly.idxmin()
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                seasonality = {
                    'best_month': month_names[best_month - 1],
                    'best_month_demand': round(monthly[best_month], 1),
                    'worst_month': month_names[worst_month - 1],
                    'worst_month_demand': round(monthly[worst_month], 1)
                }
        except Exception:
            pass

    # Upcoming events impact
    upcoming_events = []
    if not events.empty:
        category_lower = category.lower()
        for _, event in events.iterrows():
            impact_cat = str(event.get('impact_category', '')).lower()
            if impact_cat == 'all' or impact_cat in category_lower or category_lower in impact_cat:
                upcoming_events.append({
                    'event': event['event_name'],
                    'date': event['date'],
                    'impact': event['impact_percent']
                })

    # Calculate simple forecast (7 days)
    base_forecast = avg_demand
    forecast = []
    for day in range(1, 8):
        # Simple forecast with slight variation
        variation = 1 + (trend_pct / 100) * (day / 7)
        predicted = base_forecast * variation
        forecast.append({
            'day': f'Day {day}',
            'predicted_demand': round(predicted, 1)
        })

    # Risk assessment
    risks = []
    cv = (std_demand / avg_demand * 100) if avg_demand > 0 else 0
    if cv > 30:
        risks.append('High demand volatility (CV > 30%)')
    if trend_direction == 'down':
        risks.append(f'Declining trend ({round(trend_pct, 1)}%)')

    # Find worst region
    if regional_stats:
        worst_region = regional_stats[-1]
        if worst_region['diff_percent'] < -10:
            risks.append(f"Underperforming in {worst_region['region']} region ({worst_region['diff_percent']}%)")

    # Recommendations
    recommendations = []
    if trend_direction == 'up':
        recommendations.append('Consider increasing inventory levels')
    elif trend_direction == 'down':
        recommendations.append('Review pricing strategy or run promotions')

    if regional_stats and len(regional_stats) > 1:
        best_region = regional_stats[0]
        recommendations.append(f"Focus marketing on {best_region['region']} region (best performer)")

    if upcoming_events:
        recommendations.append(f"Prepare for {upcoming_events[0]['event']} ({upcoming_events[0]['impact']})")

    return {
        'product': product_info,
        'sales_stats': {
            'avg_demand': round(avg_demand, 1),
            'min_demand': int(min_demand),
            'max_demand': int(max_demand),
            'std_deviation': round(std_demand, 1),
            'coefficient_of_variation': round(cv, 1),
            'total_records': total_records
        },
        'trend': {
            'direction': trend_direction,
            'percent': round(trend_pct, 1)
        },
        'ranking': {
            'position': rank,
            'total_in_category': total_in_category,
            'percentile': round((1 - rank / total_in_category) * 100, 1) if total_in_category > 0 else 0
        },
        'price_analysis': {
            'price': price,
            'category_avg': round(avg_category_price, 2),
            'position': price_position
        },
        'regional_performance': regional_stats,
        'seasonality': seasonality,
        'forecast_7day': forecast,
        'upcoming_events': upcoming_events[:3],
        'risks': risks,
        'recommendations': recommendations
    }


def get_smart_forecast(product_id: str, days: int = 14) -> Dict[str, Any]:
    """
    Get smart forecast with external factors
    """
    analysis = get_comprehensive_analysis(product_id)
    if 'error' in analysis and 'product' not in analysis:
        return analysis

    base_demand = analysis['sales_stats']['avg_demand']
    trend_pct = analysis['trend']['percent']

    # Load factors
    events = load_events()
    weather_factors = load_weather_factors()

    category = analysis['product']['category']

    forecast_details = []
    factors_applied = []

    for day in range(1, days + 1):
        daily_factors = []
        multiplier = 1.0

        # Apply trend
        trend_impact = 1 + (trend_pct / 100) * (day / days)
        multiplier *= trend_impact

        # Simulate some events (in real scenario, would check actual dates)
        if day >= 10 and day <= 14:
            multiplier *= 1.15
            daily_factors.append({'factor': 'Weekend boost', 'impact': '+15%'})

        if day == 7:
            multiplier *= 1.08
            daily_factors.append({'factor': 'Payday effect', 'impact': '+8%'})

        # Weather simulation (random for demo)
        if day % 5 == 0:
            multiplier *= 1.05
            daily_factors.append({'factor': 'Sunny weather', 'impact': '+5%'})

        predicted = base_demand * multiplier

        forecast_details.append({
            'day': day,
            'date': f'Day +{day}',
            'predicted_demand': round(predicted, 1),
            'base_demand': round(base_demand, 1),
            'factors': daily_factors,
            'confidence': 85 - (day * 2)  # Confidence decreases over time
        })

        factors_applied.extend(daily_factors)

    # Unique factors
    unique_factors = list({f['factor']: f for f in factors_applied}.values())

    # Summary stats
    predictions = [f['predicted_demand'] for f in forecast_details]

    return {
        'product': analysis['product'],
        'forecast_summary': {
            'period_days': days,
            'avg_predicted': round(sum(predictions) / len(predictions), 1),
            'min_predicted': round(min(predictions), 1),
            'max_predicted': round(max(predictions), 1),
            'base_demand': round(base_demand, 1),
            'trend': analysis['trend']
        },
        'daily_forecast': forecast_details,
        'factors_considered': unique_factors,
        'recommendations': [
            f"Stock recommendation: {round(sum(predictions) * 1.1)} units for {days} days",
            f"Peak day: Day {predictions.index(max(predictions)) + 1} ({round(max(predictions))} units)",
            "Monitor competitor pricing mid-period"
        ]
    }
