"""
System prompts for AI Chat
"""

SYSTEM_PROMPT = """You are a demand forecasting analyst assistant for a retail company. Your role is to help users understand product demand patterns, provide forecasts, and give actionable recommendations.

## Your Capabilities:
- Analyze product demand data
- Compare products, categories, and regions
- Identify trends and patterns
- Provide recommendations for inventory management
- Explain seasonality and weather impacts

## Response Guidelines:
1. Be concise and data-driven
2. Always include specific numbers when available
3. Use bullet points for clarity
4. Provide actionable insights
5. If data is limited, acknowledge uncertainty
6. Respond in the same language as the user (Russian or English)

## Data Context:
{context}

## Recent Conversation:
{history}

## Important:
- Base all answers on the provided data context
- Don't make up data that isn't provided
- If information is not available, say so clearly
- Suggest follow-up questions when appropriate
"""

FORECAST_PROMPT = """Based on the data provided, generate a demand forecast analysis.

Product: {product_id}
Horizon: {days} days

Current Statistics:
{stats}

Provide:
1. Expected demand trend (increasing/stable/decreasing)
2. Confidence assessment (high/medium/low)
3. Key factors affecting forecast
4. Actionable recommendation for inventory

Be specific with numbers and percentages.
"""

COMPARISON_PROMPT = """Compare the following items based on demand performance:

Comparison Data:
{comparison_data}

Analyze:
1. Which performs better and why
2. Key differences
3. Trend comparison
4. Recommendation

Use specific numbers to support your analysis.
"""

RECOMMENDATIONS_PROMPT = """Based on the current data, provide strategic recommendations.

Context:
{context}

Focus on:
1. Products that need attention (declining demand)
2. Opportunities (growing demand)
3. Inventory optimization suggestions
4. Regional strategy if applicable

Be actionable and specific.
"""

TRENDS_PROMPT = """Analyze current demand trends.

Data Summary:
{data}

Identify:
1. Overall market trend
2. Top growing products
3. Declining products
4. Seasonal patterns if visible
5. Notable anomalies

Support findings with specific percentages and numbers.
"""

CATEGORY_ANALYSIS_PROMPT = """Analyze the category performance.

Category: {category}
Statistics:
{stats}

Provide:
1. Overall category health
2. Top performers in category
3. Underperformers
4. Cross-category comparison if available
5. Recommendations
"""

REGION_ANALYSIS_PROMPT = """Analyze regional performance.

Region: {region}
Statistics:
{stats}

Provide:
1. Regional demand overview
2. Comparison with other regions
3. Regional trends
4. Recommendations for regional strategy
"""

GENERAL_PROMPT = """Answer the user's question about demand forecasting.

Available Information:
{context}

Guidelines:
- If the question is about specific products, use product data
- If the question is general, provide helpful guidance
- Suggest relevant analyses the user could request
- Be helpful and informative

User Question: {question}
"""

# Intent-specific context builders
def build_forecast_context(product_summary: dict, horizon: int) -> str:
    """Build context for forecast intent"""
    if not product_summary:
        return "No product data available."

    return f"""
Product ID: {product_summary.get('product_id', 'Unknown')}
Category: {product_summary.get('category', 'Unknown')}
Current Price: ${product_summary.get('price', 0):.2f}

Demand Statistics:
- Average: {product_summary.get('avg_demand', 0):.1f} units/day
- Range: {product_summary.get('min_demand', 0):.1f} - {product_summary.get('max_demand', 0):.1f} units
- Std Dev: {product_summary.get('std_demand', 0):.1f}

Trend Analysis:
- Recent Trend: {product_summary.get('trend_pct', 0):+.1f}% ({product_summary.get('trend_direction', 'stable')})
- Forecast Horizon: {horizon} days

Inventory:
- Average Level: {product_summary.get('avg_inventory', 0):.0f} units
- Active Regions: {', '.join(product_summary.get('regions', []))}
"""


def build_comparison_context(comparison_data: dict) -> str:
    """Build context for comparison intent"""
    if "error" in comparison_data:
        return f"Comparison error: {comparison_data['error']}"

    lines = ["Comparison Results:\n"]

    products = comparison_data.get("products", [])
    regions = comparison_data.get("regions", [])
    items = products or regions

    for item in items:
        if "product_id" in item:
            lines.append(f"""
Product {item['product_id']} ({item.get('category', 'Unknown')}):
  - Avg Demand: {item.get('avg_demand', 0):.1f} units/day
  - Trend: {item.get('trend_pct', 0):+.1f}%
  - Price: ${item.get('price', 0):.2f}
""")
        elif "region" in item:
            lines.append(f"""
Region {item['region']}:
  - Avg Demand: {item.get('avg_demand', 0):.1f} units/day
  - Total Demand: {item.get('total_demand', 0):.0f} units
  - Products: {item.get('total_products', 0)}
""")

    if comparison_data.get("best_by_demand"):
        lines.append(f"\nBest by Demand: {comparison_data['best_by_demand']}")
    if comparison_data.get("best_by_trend"):
        lines.append(f"Best by Trend: {comparison_data['best_by_trend']}")
    if comparison_data.get("demand_difference_pct"):
        lines.append(f"Demand Difference: {comparison_data['demand_difference_pct']:.1f}%")

    return "".join(lines)


def build_category_context(category_stats: dict) -> str:
    """Build context for category stats"""
    if not category_stats:
        return "No category data available."

    return f"""
Category: {category_stats.get('category', 'Unknown')}

Overview:
- Total Products: {category_stats.get('total_products', 0)}
- Total Records: {category_stats.get('total_records', 0)}
- Average Demand: {category_stats.get('avg_demand', 0):.1f} units/day
- Total Demand: {category_stats.get('total_demand', 0):.0f} units
- Average Price: ${category_stats.get('avg_price', 0):.2f}

Top Products: {', '.join(category_stats.get('top_products', []))}
Active Regions: {', '.join(category_stats.get('regions', []))}
"""


def build_region_context(region_stats: dict) -> str:
    """Build context for region stats"""
    if not region_stats:
        return "No region data available."

    return f"""
Region: {region_stats.get('region', 'Unknown')}

Overview:
- Total Products: {region_stats.get('total_products', 0)}
- Total Records: {region_stats.get('total_records', 0)}
- Average Demand: {region_stats.get('avg_demand', 0):.1f} units/day
- Total Demand: {region_stats.get('total_demand', 0):.0f} units

Categories: {', '.join(region_stats.get('categories', []))}
Top Products: {', '.join(region_stats.get('top_products', []))}
"""


def build_seasonality_context(seasonality_data: dict) -> str:
    """Build context for seasonality analysis"""
    if not seasonality_data:
        return "No seasonality data available."

    lines = [f"Seasonality Analysis for {seasonality_data.get('product_id', 'Unknown')}:\n"]

    for season in seasonality_data.get("seasonality_data", []):
        lines.append(f"  - {season['season']}: {season['avg_demand']:.1f} avg demand ({season['count']} records)")

    best = seasonality_data.get("best_season", {})
    worst = seasonality_data.get("worst_season", {})

    lines.append(f"\nBest Season: {best.get('name', 'Unknown')} ({best.get('avg_demand', 0):.1f} units)")
    lines.append(f"Worst Season: {worst.get('name', 'Unknown')} ({worst.get('avg_demand', 0):.1f} units)")
    lines.append(f"Seasonal Variation: {seasonality_data.get('seasonal_variation', 0):.1f}%")

    return "\n".join(lines)


def build_weather_context(weather_data: dict) -> str:
    """Build context for weather impact analysis"""
    if not weather_data:
        return "No weather impact data available."

    lines = [f"Weather Impact Analysis for {weather_data.get('product_id', 'Unknown')}:\n"]

    for weather in weather_data.get("weather_data", []):
        lines.append(f"  - {weather['weather']}: {weather['avg_demand']:.1f} avg demand ({weather['count']} records)")

    best = weather_data.get("best_weather", {})
    worst = weather_data.get("worst_weather", {})

    lines.append(f"\nBest Conditions: {best.get('condition', 'Unknown')} ({best.get('avg_demand', 0):.1f} units)")
    lines.append(f"Worst Conditions: {worst.get('condition', 'Unknown')} ({worst.get('avg_demand', 0):.1f} units)")
    lines.append(f"Weather Impact: {weather_data.get('weather_impact_pct', 0):.1f}%")

    return "\n".join(lines)


def build_top_products_context(top_products: list, metric: str = "demand") -> str:
    """Build context for top products"""
    if not top_products:
        return "No top products data available."

    lines = [f"Top Products by {metric.title()}:\n"]

    for i, product in enumerate(top_products, 1):
        if "avg_demand" in product:
            lines.append(f"  {i}. {product['product_id']}: {product['avg_demand']:.1f} avg demand")
        elif "growth_pct" in product:
            lines.append(f"  {i}. {product['product_id']}: {product['growth_pct']:+.1f}% growth")
        elif "cv" in product:
            lines.append(f"  {i}. {product['product_id']}: CV={product['cv']:.3f} ({product.get('avg_demand', 0):.1f} avg)")

    return "\n".join(lines)


def build_low_performers_context(low_performers: list) -> str:
    """Build context for low performing products"""
    if not low_performers:
        return "No declining products found. All products are performing well."

    lines = ["Products with Declining Demand:\n"]

    for i, product in enumerate(low_performers, 1):
        lines.append(
            f"  {i}. {product['product_id']} ({product.get('category', 'Unknown')}): "
            f"-{product['decline_pct']:.1f}% decline, now {product['recent_demand']:.1f} units/day"
        )

    return "\n".join(lines)


def build_dataset_context(overview: dict) -> str:
    """Build context for dataset overview"""
    if not overview:
        return "Dataset information not available."

    date_range = overview.get("date_range", {})

    # Build Amazon catalog info if available
    amazon_section = ""
    if overview.get("amazon_products"):
        amazon_section = f"""
Amazon Product Catalog:
- Total Products: {overview.get('amazon_products', 0):,}
- Categories: {overview.get('amazon_categories', 0)}
- Top Categories: {', '.join(overview.get('amazon_top_categories', []))}
- Use product search to find any product (e.g., "iPhone", "Samsung TV", "Nike shoes")
"""

    return f"""
Dataset Overview:

=== Demand Forecasting Data ===
Records: {overview.get('total_records', 0):,}
Products with History: {overview.get('total_products', 0)} ({', '.join(overview.get('products', []))})
Categories: {overview.get('total_categories', 0)}
Regions: {overview.get('total_regions', 0)}

Date Range: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}
Average Demand: {overview.get('avg_demand', 0):.1f} units/day

Categories: {', '.join(overview.get('categories', []))}
Regions: {', '.join(overview.get('regions', []))}
{amazon_section}
NOTE: For forecasting use P0001, P0002, P0003. For product search, use product names like "iPhone", "laptop", etc.
"""


def build_product_search_context(results: list, query: str) -> str:
    """Build context for product search results"""
    if not results:
        return f"No products found matching '{query}'."

    lines = [f"Search Results for '{query}':\n"]

    for i, product in enumerate(results, 1):
        score_pct = int(product.get('score', 0) * 100)
        lines.append(
            f"  {i}. {product['name']} ({product['product_id']})\n"
            f"     Brand: {product['brand']} | Category: {product['category']}\n"
            f"     Price: ${product['price']} | Match: {score_pct}%"
        )

    return "\n".join(lines)


def build_analysis_context(analysis: dict) -> str:
    """Build comprehensive analysis context"""
    if 'error' in analysis and 'product' not in analysis:
        return f"Analysis error: {analysis['error']}"

    product = analysis.get('product', {})
    stats = analysis.get('sales_stats', {})
    trend = analysis.get('trend', {})
    ranking = analysis.get('ranking', {})
    price_analysis = analysis.get('price_analysis', {})
    regional = analysis.get('regional_performance', [])
    seasonality = analysis.get('seasonality', {})
    forecast = analysis.get('forecast_7day', [])
    events = analysis.get('upcoming_events', [])
    risks = analysis.get('risks', [])
    recommendations = analysis.get('recommendations', [])

    lines = [
        f"=== COMPREHENSIVE ANALYSIS ===\n",
        f"Product: {product.get('name', 'Unknown')} ({product.get('product_id', '')})",
        f"Brand: {product.get('brand', '')} | Category: {product.get('category', '')} > {product.get('subcategory', '')}",
        f"Price: ${product.get('price', 0)} ({price_analysis.get('position', 'mid-range')} in category)",
        f"\n--- SALES STATISTICS ---",
        f"Average Demand: {stats.get('avg_demand', 0):.1f} units/day",
        f"Range: {stats.get('min_demand', 0)} - {stats.get('max_demand', 0)} units",
        f"Volatility (CV): {stats.get('coefficient_of_variation', 0):.1f}%",
        f"Total Records: {stats.get('total_records', 0)}",
        f"\n--- TREND ---",
        f"Direction: {trend.get('direction', 'stable').upper()}",
        f"Change: {trend.get('percent', 0):+.1f}%",
        f"\n--- RANKING ---",
        f"Position: #{ranking.get('position', 0)} of {ranking.get('total_in_category', 0)} products",
        f"Top {ranking.get('percentile', 0):.0f}% in category",
    ]

    if regional:
        lines.append(f"\n--- REGIONAL PERFORMANCE ---")
        for r in regional[:4]:
            diff = r.get('diff_percent', 0)
            diff_str = f"+{diff:.1f}%" if diff > 0 else f"{diff:.1f}%"
            lines.append(f"  {r['region']}: {r['avg_demand']:.1f} units/day ({diff_str})")

    if seasonality:
        lines.append(f"\n--- SEASONALITY ---")
        lines.append(f"Best Month: {seasonality.get('best_month', 'N/A')} ({seasonality.get('best_month_demand', 0):.1f} units)")
        lines.append(f"Worst Month: {seasonality.get('worst_month', 'N/A')} ({seasonality.get('worst_month_demand', 0):.1f} units)")

    if forecast:
        lines.append(f"\n--- 7-DAY FORECAST ---")
        for f in forecast:
            lines.append(f"  {f['day']}: {f['predicted_demand']:.1f} units")

    if events:
        lines.append(f"\n--- UPCOMING EVENTS ---")
        for e in events:
            lines.append(f"  {e['event']} ({e['date']}): {e['impact']}")

    if risks:
        lines.append(f"\n--- RISKS ---")
        for risk in risks:
            lines.append(f"  ⚠️ {risk}")

    if recommendations:
        lines.append(f"\n--- RECOMMENDATIONS ---")
        for rec in recommendations:
            lines.append(f"  💡 {rec}")

    return "\n".join(lines)


def build_amazon_search_context(results: list, query: str) -> str:
    """Build context for Amazon product search results"""
    if not results:
        return f"No Amazon products found matching '{query}'."

    lines = [f"=== Amazon Product Search: '{query}' ===\n"]
    lines.append(f"Found {len(results)} matching products:\n")

    for i, product in enumerate(results, 1):
        price = product.get('price', 0)
        rating = product.get('rating', 0)
        num_ratings = product.get('num_ratings', 0)
        image_url = product.get('image_url', '')

        lines.append(
            f"{i}. **{product.get('name', 'Unknown')[:80]}**\n"
            f"   ID: {product.get('product_id', '')}\n"
            f"   Category: {product.get('main_category', '')} > {product.get('sub_category', '')}\n"
            f"   Price: ₹{price:,.0f} | Rating: {rating}/5 ({num_ratings:,} reviews)\n"
            f"   Match Score: {int(product.get('score', 0) * 100)}%\n"
            f"   Image: {image_url}\n" if image_url else ""
        )

    return "\n".join(lines)


def build_amazon_analysis_context(analysis: dict) -> str:
    """Build comprehensive Amazon product analysis context"""
    if 'error' in analysis:
        return f"Analysis error: {analysis['error']}"

    product = analysis.get('product', {})
    cat_stats = analysis.get('category_stats', {})
    price_analysis = analysis.get('price_analysis', {})
    rating_analysis = analysis.get('rating_analysis', {})
    ranking = analysis.get('ranking', {})
    demand = analysis.get('demand_estimate', {})
    similar = analysis.get('similar_products', [])
    recommendations = analysis.get('recommendations', [])

    lines = [
        f"\n=== DETAILED PRODUCT ANALYSIS ===\n",
        f"**{product.get('name', 'Unknown')}**",
        f"Product ID: {product.get('product_id', '')}",
        f"",
        f"--- CATEGORY INFO ---",
        f"Main Category: {cat_stats.get('main_category', '')}",
        f"Sub Category: {cat_stats.get('sub_category', '')}",
        f"Products in Category: {cat_stats.get('products_in_category', 0):,}",
        f"Products in Subcategory: {cat_stats.get('products_in_subcategory', 0):,}",
        f"",
        f"--- PRICE ANALYSIS ---",
        f"Current Price: ₹{price_analysis.get('current_price', 0):,.0f}",
        f"Original Price: ₹{price_analysis.get('original_price', 0):,.0f}",
        f"Discount: {price_analysis.get('discount_percent', 0)}%",
        f"Price Position: {price_analysis.get('position', 'N/A').upper()}",
        f"vs Category Avg: {price_analysis.get('vs_category_avg', 0):+.1f}%",
        f"",
        f"--- RATING ANALYSIS ---",
        f"Rating: {rating_analysis.get('rating', 0)}/5",
        f"Total Reviews: {rating_analysis.get('num_ratings', 0):,}",
        f"Rating Position: {rating_analysis.get('position', 'N/A').upper()}",
        f"vs Category Avg: {rating_analysis.get('vs_category_avg', 0):+.2f}",
        f"",
        f"--- RANKING ---",
        f"Position: #{ranking.get('position', 0)} of {ranking.get('total', 0)}",
        f"Percentile: Top {ranking.get('percentile', 0)}%",
        f"",
        f"--- DEMAND ESTIMATE ---",
        f"Estimated Daily Demand: {demand.get('avg_daily', 0)} units",
        f"Trend: {demand.get('trend', 'stable').upper()} ({demand.get('trend_pct', 0):+.1f}%)",
    ]

    if similar:
        lines.append(f"\n--- SIMILAR PRODUCTS ---")
        for s in similar:
            lines.append(f"  • {s.get('name', '')[:50]} - ₹{s.get('price', 0):,.0f}")

    if recommendations:
        lines.append(f"\n--- RECOMMENDATIONS ---")
        for rec in recommendations:
            lines.append(f"  💡 {rec}")

    # Add image URL if available
    if product.get('image_url'):
        lines.append(f"\nImage: {product.get('image_url')}")

    return "\n".join(lines)


def build_smart_forecast_context(forecast_data: dict) -> str:
    """Build smart forecast context with factors"""
    if 'error' in forecast_data:
        return f"Forecast error: {forecast_data['error']}"

    product = forecast_data.get('product', {})
    summary = forecast_data.get('forecast_summary', {})
    daily = forecast_data.get('daily_forecast', [])
    factors = forecast_data.get('factors_considered', [])
    recommendations = forecast_data.get('recommendations', [])

    lines = [
        f"=== SMART FORECAST ===\n",
        f"Product: {product.get('name', 'Unknown')} ({product.get('product_id', '')})",
        f"\n--- FORECAST SUMMARY ---",
        f"Period: {summary.get('period_days', 0)} days",
        f"Base Demand: {summary.get('base_demand', 0):.1f} units/day",
        f"Predicted Average: {summary.get('avg_predicted', 0):.1f} units/day",
        f"Predicted Range: {summary.get('min_predicted', 0):.1f} - {summary.get('max_predicted', 0):.1f} units",
        f"Trend: {summary.get('trend', {}).get('direction', 'stable')} ({summary.get('trend', {}).get('percent', 0):+.1f}%)",
    ]

    if daily:
        lines.append(f"\n--- DAILY FORECAST ---")
        for d in daily:
            factors_str = ", ".join([f['factor'] for f in d.get('factors', [])]) if d.get('factors') else "baseline"
            lines.append(f"  {d['date']}: {d['predicted_demand']:.1f} units (confidence: {d.get('confidence', 0)}%) [{factors_str}]")

    if factors:
        lines.append(f"\n--- FACTORS APPLIED ---")
        for f in factors:
            lines.append(f"  • {f['factor']}: {f['impact']}")

    if recommendations:
        lines.append(f"\n--- RECOMMENDATIONS ---")
        for rec in recommendations:
            lines.append(f"  💡 {rec}")

    return "\n".join(lines)


def build_amazon_top_products_context(products: list, metric: str = "popularity") -> str:
    """Build context for Amazon top products"""
    if not products:
        return "No top products data available."

    metric_labels = {
        "popularity": "Most Popular (by reviews)",
        "rating": "Highest Rated",
        "value": "Best Value"
    }

    lines = [f"=== Top Products by {metric_labels.get(metric, metric.title())} ===\n"]

    for product in products:
        price = product.get('price', 0)
        rating = product.get('rating', 0)
        num_ratings = product.get('num_ratings', 0)

        lines.append(
            f"{product.get('rank', 0)}. **{product.get('name', 'Unknown')}**\n"
            f"   Category: {product.get('category', '')}\n"
            f"   Price: ₹{price:,.0f} | Rating: {rating}/5 ({num_ratings:,} reviews)\n"
        )

    return "\n".join(lines)


def build_amazon_low_performers_context(products: list) -> str:
    """Build context for Amazon low performing products"""
    if not products:
        return "No low performing products found. Products are generally well-rated."

    lines = ["=== Products Needing Attention (Low Ratings) ===\n"]

    for product in products:
        price = product.get('price', 0)
        rating = product.get('rating', 0)
        num_ratings = product.get('num_ratings', 0)

        lines.append(
            f"{product.get('rank', 0)}. **{product.get('name', 'Unknown')}**\n"
            f"   Category: {product.get('category', '')}\n"
            f"   Price: ₹{price:,.0f} | Rating: {rating}/5 ({num_ratings:,} reviews)\n"
            f"   Issue: Low customer rating - consider product improvements or delisting\n"
        )

    return "\n".join(lines)


def build_trends_context(rising: list, declining: list, hot: list, alerts: list) -> str:
    """Build context for trends analysis with alerts"""
    lines = ["=== ТРЕНДЫ И АНАЛИТИКА ===\n"]

    # Hot products (trending now)
    if hot:
        lines.append("🔥 **ГОРЯЧИЕ ТОВАРЫ (Hot Products)**")
        for p in hot:
            trend = p.get('trend', {})
            trend_str = f"+{trend.get('percent', 0):.1f}%" if trend.get('percent', 0) > 0 else f"{trend.get('percent', 0):.1f}%"
            lines.append(
                f"  • {p.get('name', '')[:50]} - ₹{p.get('price', 0):,.0f}\n"
                f"    Рейтинг: {p.get('rating', 0)}/5 ({p.get('num_ratings', 0):,} отзывов)\n"
                f"    Тренд: {trend_str} ({trend.get('direction', 'stable')})"
            )
        lines.append("")

    # Rising products
    if rising:
        lines.append("📈 **РАСТУЩИЕ ТОВАРЫ (Rising)**")
        for p in rising:
            trend = p.get('trend', {})
            trend_str = f"+{trend.get('percent', 0):.1f}%" if trend.get('percent', 0) > 0 else f"{trend.get('percent', 0):.1f}%"
            lines.append(
                f"  • {p.get('name', '')[:50]}\n"
                f"    Рейтинг: {p.get('rating', 0)}/5 | Тренд: {trend_str}"
            )
        lines.append("")

    # Declining products
    if declining:
        lines.append("📉 **ПАДАЮЩИЕ ТОВАРЫ (Declining)**")
        for p in declining:
            trend = p.get('trend', {})
            trend_str = f"{trend.get('percent', 0):.1f}%"
            lines.append(
                f"  ⚠️ {p.get('name', '')[:50]}\n"
                f"    Рейтинг: {p.get('rating', 0)}/5 | Тренд: {trend_str}"
            )
        lines.append("")

    # Alerts
    if alerts:
        lines.append("🚨 **ОПОВЕЩЕНИЯ (Alerts)**")
        for alert in alerts:
            lines.append(f"  {alert.get('icon', '')} {alert.get('message', '')}")
        lines.append("")

    # Summary
    lines.append("--- РЕЗЮМЕ ---")
    lines.append(f"Горячих товаров: {len(hot)}")
    lines.append(f"Растущих товаров: {len(rising)}")
    lines.append(f"Проблемных товаров: {len(declining)}")
    lines.append(f"Активных оповещений: {len(alerts)}")

    return "\n".join(lines)


def build_amazon_comparison_context(products: list) -> str:
    """Build context for comparing Amazon products side-by-side"""
    if not products:
        return "No products to compare."

    if len(products) < 2:
        return "Need at least 2 products to compare."

    lines = ["=== PRODUCT COMPARISON ===\n"]

    # Header with product names
    names = [p.get('name', 'Unknown')[:40] for p in products]
    lines.append("Comparing: " + " vs ".join(names) + "\n")

    # Side-by-side comparison table
    lines.append("\n--- PRICE ---")
    prices = [p.get('price', 0) for p in products]
    min_price = min(prices) if prices else 0
    for i, p in enumerate(products):
        price = p.get('price', 0)
        is_cheapest = price == min_price and prices.count(min_price) == 1
        badge = " 🏆 BEST PRICE" if is_cheapest else ""
        lines.append(f"  {names[i]}: ₹{price:,.0f}{badge}")

    lines.append("\n--- RATING ---")
    ratings = [p.get('rating', 0) for p in products]
    max_rating = max(ratings) if ratings else 0
    for i, p in enumerate(products):
        rating = p.get('rating', 0)
        reviews = p.get('reviews_count', 0)
        is_best = rating == max_rating and ratings.count(max_rating) == 1
        badge = " 🏆 BEST RATED" if is_best else ""
        lines.append(f"  {names[i]}: {rating}/5 ({reviews:,} reviews){badge}")

    lines.append("\n--- CATEGORY ---")
    for i, p in enumerate(products):
        lines.append(f"  {names[i]}: {p.get('category', 'Unknown')}")

    # Value analysis
    lines.append("\n--- VALUE ANALYSIS ---")
    for i, p in enumerate(products):
        price = p.get('price', 0) or 1
        rating = p.get('rating', 0) or 1
        value_score = (rating / 5) * 100 / (price / 1000)  # Higher is better
        lines.append(f"  {names[i]}: Value Score {value_score:.1f}")

    # Winner summary
    lines.append("\n--- SUMMARY ---")

    # Best price
    if min_price > 0:
        best_price_idx = prices.index(min_price)
        lines.append(f"💰 Best Price: {names[best_price_idx]} (₹{min_price:,.0f})")

    # Best rating
    if max_rating > 0:
        best_rating_idx = ratings.index(max_rating)
        lines.append(f"⭐ Best Rating: {names[best_rating_idx]} ({max_rating}/5)")

    # Best value (highest rating per rupee)
    value_scores = [(p.get('rating', 0) / max(p.get('price', 1), 1)) * 10000 for p in products]
    best_value_idx = value_scores.index(max(value_scores))
    lines.append(f"🎯 Best Value: {names[best_value_idx]}")

    return "\n".join(lines)
