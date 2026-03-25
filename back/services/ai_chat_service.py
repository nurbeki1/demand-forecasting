"""
AI Chat Service with RAG Pipeline
Handles intent classification, context building, LLM calls, and memory management
"""
from typing import Dict, Any, Optional, List

from services.intent_classifier import (
    classify_intent,
    Intent,
    get_follow_up_suggestions,
    extract_days,
)
from services.data_service import (
    get_product_summary,
    get_category_stats,
    get_region_stats,
    get_seasonality_analysis,
    get_weather_impact,
    get_top_performers,
    get_low_performers,
    get_dataset_overview,
    compare_products,
    compare_regions,
    search_products,
)
from services.product_search_service import (
    search_product,
    get_product_by_id,
    get_comprehensive_analysis,
    get_smart_forecast,
)
from services.amazon_data_service import (
    search_amazon_products,
    get_amazon_product_by_id,
    get_amazon_product_analysis,
    get_category_overview,
    get_amazon_top_products,
    get_amazon_low_performers,
    get_trending_products,
    get_product_alerts,
)
from services.llm_client import ask_llm
from services.forecast_service import get_forecast_chart
from memory.chat_memory import chat_memory
from prompts.chat_prompts import (
    SYSTEM_PROMPT,
    build_forecast_context,
    build_comparison_context,
    build_category_context,
    build_region_context,
    build_seasonality_context,
    build_weather_context,
    build_top_products_context,
    build_low_performers_context,
    build_dataset_context,
    build_product_search_context,
    build_analysis_context,
    build_smart_forecast_context,
    build_amazon_search_context,
    build_amazon_analysis_context,
    build_amazon_top_products_context,
    build_amazon_low_performers_context,
    build_amazon_comparison_context,
    build_trends_context,
)


def build_rag_context(intent: Intent, entities: Dict[str, Any]) -> str:
    """
    Build RAG context based on intent and extracted entities

    Args:
        intent: Classified intent
        entities: Extracted entities (product_ids, category, region, etc.)

    Returns:
        Context string for LLM
    """
    context_parts = []
    product_ids = entities.get("product_ids", [])
    category = entities.get("category")
    region = entities.get("region")
    days = entities.get("days", 7)
    top_n = entities.get("top_n", 5)

    if intent == Intent.FORECAST:
        if product_ids:
            for pid in product_ids[:2]:  # Max 2 products
                summary = get_product_summary(pid)
                if summary:
                    context_parts.append(build_forecast_context(summary, days))

    elif intent == Intent.PRODUCT_INFO:
        if product_ids:
            for pid in product_ids[:3]:  # Max 3 products
                summary = get_product_summary(pid)
                if summary:
                    context_parts.append(build_forecast_context(summary, 7))

    elif intent == Intent.COMPARISON:
        comparison_queries = entities.get("comparison_queries", [])
        search_query = entities.get("search_query", "")

        # If we have comparison queries, search Amazon for each
        if comparison_queries:
            comparison_products = []
            for query in comparison_queries[:4]:
                results = search_amazon_products(query, top_k=1)
                if results:
                    product = results[0]
                    analysis = get_amazon_product_analysis(product['product_id'])
                    comparison_products.append({
                        "name": product.get("name", ""),
                        "price": product.get("price", 0),
                        "rating": product.get("rating", 0),
                        "reviews_count": product.get("reviews_count", 0),
                        "category": product.get("category", ""),
                        "analysis": analysis if 'error' not in analysis else {}
                    })

            if comparison_products:
                context_parts.append(build_amazon_comparison_context(comparison_products))
        elif len(product_ids) >= 2:
            comparison = compare_products(product_ids[:4])
            context_parts.append(build_comparison_context(comparison))
        elif region:
            # Compare all regions
            all_regions = ["East", "West", "North", "South"]
            comparison = compare_regions(all_regions)
            context_parts.append(build_comparison_context(comparison))
        elif search_query:
            # Search for similar products to compare
            results = search_amazon_products(search_query, top_k=3)
            if results:
                context_parts.append(build_amazon_search_context(results, search_query))

    elif intent == Intent.CATEGORY_STATS:
        if category:
            stats = get_category_stats(category)
            if stats:
                context_parts.append(build_category_context(stats))

    elif intent == Intent.REGION_STATS:
        if region:
            stats = get_region_stats(region)
            if stats:
                context_parts.append(build_region_context(stats))
        else:
            # Compare all regions
            comparison = compare_regions(["East", "West", "North", "South"])
            context_parts.append(build_comparison_context(comparison))

    elif intent == Intent.SEASONALITY:
        if product_ids:
            for pid in product_ids[:2]:
                seasonality = get_seasonality_analysis(pid)
                if seasonality:
                    context_parts.append(build_seasonality_context(seasonality))

    elif intent == Intent.WEATHER_IMPACT:
        if product_ids:
            for pid in product_ids[:2]:
                weather = get_weather_impact(pid)
                if weather:
                    context_parts.append(build_weather_context(weather))

    elif intent == Intent.TOP_PRODUCTS:
        # Use Amazon data for top products (551K products)
        top_by_popularity = get_amazon_top_products(top_n, by="popularity")
        top_by_rating = get_amazon_top_products(top_n, by="rating")

        if top_by_popularity:
            context_parts.append(build_amazon_top_products_context(top_by_popularity, "popularity"))
        if top_by_rating:
            context_parts.append(build_amazon_top_products_context(top_by_rating, "rating"))

        # Also show category overview
        cat_overview = get_category_overview()
        if cat_overview and 'error' not in cat_overview:
            context_parts.append(f"\nTotal products in catalog: {cat_overview.get('total_products', 0):,}")
            context_parts.append(f"Total categories: {cat_overview.get('total_categories', 0)}")

    elif intent == Intent.LOW_PERFORMERS:
        # Use Amazon data for low performers
        low = get_amazon_low_performers(top_n)
        if low:
            context_parts.append(build_amazon_low_performers_context(low))
        else:
            # Fallback to local data
            local_low = get_low_performers(top_n)
            context_parts.append(build_low_performers_context(local_low))

    elif intent == Intent.DATASET_INFO:
        overview = get_dataset_overview()
        context_parts.append(build_dataset_context(overview))

    elif intent == Intent.TRENDS:
        # Get trending products from Amazon data
        trending_up = get_trending_products(5, direction="rising")
        trending_down = get_trending_products(5, direction="declining")
        hot_products = get_trending_products(3, direction="hot")
        alerts = get_product_alerts()

        context_parts.append(build_trends_context(trending_up, trending_down, hot_products, alerts))

    elif intent == Intent.RECOMMENDATIONS:
        # Comprehensive context for recommendations
        declining = get_low_performers(5)
        growing = get_top_performers(5, by="growth")
        overview = get_dataset_overview()

        context_parts.append("Dataset Overview:\n" + build_dataset_context(overview))
        context_parts.append("\nGrowing Products:\n" + build_top_products_context(growing, "growth"))
        context_parts.append("\nProducts Needing Attention:\n" + build_low_performers_context(declining))

    elif intent == Intent.PRODUCT_SEARCH:
        # Search for product by name
        search_query = entities.get("search_query", "")
        if search_query:
            # Try Amazon products first
            amazon_results = search_amazon_products(search_query, top_k=5)
            if amazon_results:
                context_parts.append(build_amazon_search_context(amazon_results, search_query))
                # Get analysis for top match
                top_match = amazon_results[0]
                analysis = get_amazon_product_analysis(top_match['product_id'])
                if 'error' not in analysis:
                    context_parts.append(build_amazon_analysis_context(analysis))
            else:
                # Fallback to local catalog
                results = search_product(search_query, top_k=5)
                if results:
                    context_parts.append(build_product_search_context(results, search_query))
                    top_match = results[0]
                    analysis = get_comprehensive_analysis(top_match['product_id'])
                    if 'error' not in analysis or 'product' in analysis:
                        context_parts.append(build_analysis_context(analysis))

    elif intent == Intent.PRODUCT_ANALYSIS:
        # Full comprehensive analysis
        if product_ids:
            for pid in product_ids[:2]:
                analysis = get_comprehensive_analysis(pid)
                if 'error' not in analysis or 'product' in analysis:
                    context_parts.append(build_analysis_context(analysis))
        else:
            # Try to find product from search query
            search_query = entities.get("search_query", "")
            if search_query:
                results = search_product(search_query, top_k=1)
                if results:
                    analysis = get_comprehensive_analysis(results[0]['product_id'])
                    context_parts.append(build_analysis_context(analysis))

    elif intent == Intent.SMART_FORECAST:
        # Smart forecast with factors
        if product_ids:
            for pid in product_ids[:2]:
                smart_forecast = get_smart_forecast(pid, days)
                if 'error' not in smart_forecast:
                    context_parts.append(build_smart_forecast_context(smart_forecast))

    elif intent == Intent.GENERAL:
        # Provide basic context
        overview = get_dataset_overview()
        context_parts.append(build_dataset_context(overview))

        # If any entities found, add their context
        if product_ids:
            for pid in product_ids[:2]:
                summary = get_product_summary(pid)
                if summary:
                    context_parts.append(build_forecast_context(summary, 7))

    # Combine all context parts
    if context_parts:
        return "\n\n---\n\n".join(context_parts)

    # Fallback: provide overview
    overview = get_dataset_overview()
    return build_dataset_context(overview)


def get_product_images(intent: Intent, entities: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """
    Get product images for display in chat response
    Returns list of {product_id, name, image_url, price}
    """
    import math

    def safe_float(val, default=0):
        """Convert to float, handling NaN/Inf"""
        try:
            f = float(val) if val else default
            return default if (math.isnan(f) or math.isinf(f)) else f
        except (ValueError, TypeError):
            return default

    search_query = entities.get("search_query", "")

    # Return images for TOP_PRODUCTS intent
    if intent == Intent.TOP_PRODUCTS:
        try:
            top_products = get_amazon_top_products(5, by="popularity")
            if top_products:
                return [
                    {
                        "product_id": p.get("product_id", ""),
                        "name": p.get("name", "")[:60],
                        "image_url": p.get("image_url", ""),
                        "price": safe_float(p.get("price", 0)),
                        "rating": safe_float(p.get("rating", 0)),
                    }
                    for p in top_products if p.get("image_url")
                ]
        except Exception:
            pass

    if intent == Intent.PRODUCT_SEARCH and search_query:
        try:
            results = search_amazon_products(search_query, top_k=3)
            if results:
                return [
                    {
                        "product_id": r.get("product_id", ""),
                        "name": r.get("name", "")[:60],
                        "image_url": r.get("image_url", ""),
                        "price": safe_float(r.get("price", 0)),
                        "rating": safe_float(r.get("rating", 0)),
                    }
                    for r in results if r.get("image_url")
                ]
        except Exception:
            pass

    # Return images for COMPARISON intent
    if intent == Intent.COMPARISON:
        try:
            # Extract comparison queries from message
            comparison_queries = entities.get("comparison_queries", [])
            search_query = entities.get("search_query", "")

            images = []

            # If we have explicit comparison queries (e.g., "iPhone vs Samsung")
            if comparison_queries:
                for query in comparison_queries[:4]:  # Max 4 products
                    results = search_amazon_products(query, top_k=1)
                    if results:
                        p = results[0]
                        if p.get("image_url"):
                            images.append({
                                "product_id": p.get("product_id", ""),
                                "name": p.get("name", "")[:60],
                                "image_url": p.get("image_url", ""),
                                "price": safe_float(p.get("price", 0)),
                                "rating": safe_float(p.get("rating", 0)),
                            })
            # If we have a general search query, get multiple products
            elif search_query:
                results = search_amazon_products(search_query, top_k=4)
                if results:
                    for p in results:
                        if p.get("image_url"):
                            images.append({
                                "product_id": p.get("product_id", ""),
                                "name": p.get("name", "")[:60],
                                "image_url": p.get("image_url", ""),
                                "price": safe_float(p.get("price", 0)),
                                "rating": safe_float(p.get("rating", 0)),
                            })

            if images:
                return images
        except Exception:
            pass

    # Return images for TRENDS intent with trend data
    if intent == Intent.TRENDS:
        try:
            trending = get_trending_products(5, direction="hot")
            if trending:
                return [
                    {
                        "product_id": p.get("product_id", ""),
                        "name": p.get("name", "")[:60],
                        "image_url": p.get("image_url", ""),
                        "price": safe_float(p.get("price", 0)),
                        "rating": safe_float(p.get("rating", 0)),
                        "trend": p.get("trend", {}),
                    }
                    for p in trending if p.get("image_url")
                ]
        except Exception:
            pass

    return None


def get_chart_data(intent: Intent, entities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get chart data if applicable for the intent

    Returns chart data for visualization on frontend
    """
    product_ids = entities.get("product_ids", [])
    days = entities.get("days", 7)
    search_query = entities.get("search_query", "")

    # For product search, try to get chart for top match
    if intent == Intent.PRODUCT_SEARCH and search_query:
        try:
            results = search_product(search_query, top_k=1)
            if results:
                return get_forecast_chart(results[0]['product_id'], days)
        except Exception:
            return None

    if intent in [Intent.FORECAST, Intent.PRODUCT_INFO, Intent.PRODUCT_ANALYSIS, Intent.SMART_FORECAST] and product_ids:
        try:
            return get_forecast_chart(product_ids[0], days)
        except Exception:
            return None

    return None


def handle_ai_chat(message: str, user_id: int) -> Dict[str, Any]:
    """
    Main handler for AI chat messages with RAG pipeline

    Args:
        message: User's message
        user_id: User ID for session isolation

    Returns:
        Response dictionary with reply, intent, data, suggestions
    """
    # Step 1: Check for pronoun references ("it", "this product", etc.)
    resolved_reference = chat_memory.resolve_reference(user_id, message)
    if resolved_reference:
        # If no product mentioned but reference found, add it to search
        entities_pre = {}
        entities_pre["search_query"] = resolved_reference

    # Step 2: Classify intent and extract entities
    intent, entities = classify_intent(message)

    # Step 3: If reference was resolved, merge it into entities
    if resolved_reference and not entities.get("product_ids") and not entities.get("search_query"):
        entities["search_query"] = resolved_reference

    # Step 4: Get smart conversation history with entity context
    history = chat_memory.get_smart_context_window(user_id)

    # Step 5: Build RAG context
    context = build_rag_context(intent, entities)

    # Step 6: Build system prompt with context
    system_prompt = SYSTEM_PROMPT.format(
        context=context,
        history=history
    )

    # Step 7: Call LLM
    try:
        response = ask_llm(system_prompt, message)
    except Exception as e:
        response = f"Sorry, I encountered an error: {str(e)}"

    # Step 8: Get chart data if applicable
    chart_data = get_chart_data(intent, entities)

    # Step 9: Generate follow-up suggestions based on context
    suggestions = get_follow_up_suggestions(intent, entities)

    # Step 10: Track entities for context memory
    chat_memory.track_entities(
        user_id=user_id,
        product_ids=entities.get("product_ids"),
        search_query=entities.get("search_query"),
        category=entities.get("category"),
        region=entities.get("region"),
        intent=intent.value
    )

    # Step 11: Store messages in memory
    chat_memory.add_message(
        user_id=user_id,
        role="user",
        content=message,
        intent=intent.value
    )

    chat_memory.add_message(
        user_id=user_id,
        role="assistant",
        content=response,
        data=chart_data,
        intent=intent.value
    )

    # Step 12: Get product images if applicable
    product_images = get_product_images(intent, entities)

    # Step 10: Build response
    result = {
        "reply": response,
        "intent": intent.value,
        "entities": entities,
        "suggestions": suggestions,
    }

    if chart_data:
        result["data"] = chart_data

    if product_images:
        result["images"] = product_images

    return result


def get_chat_history(user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get chat history for user

    Args:
        user_id: User ID
        limit: Optional limit on messages

    Returns:
        List of chat messages
    """
    return chat_memory.get_history(user_id, limit=limit)


def clear_chat_history(user_id: int) -> Dict[str, Any]:
    """
    Clear chat history for user

    Args:
        user_id: User ID

    Returns:
        Result with count of cleared messages
    """
    count = chat_memory.clear_history(user_id)
    return {
        "message": "History cleared",
        "cleared_messages": count
    }


def get_analytics_summary() -> Dict[str, Any]:
    """
    Get analytics summary for dashboard

    Returns comprehensive analytics data
    """
    overview = get_dataset_overview()
    top_demand = get_top_performers(5, by="demand")
    top_growth = get_top_performers(5, by="growth")
    declining = get_low_performers(5)

    return {
        "overview": overview,
        "top_by_demand": top_demand,
        "top_by_growth": top_growth,
        "declining": declining,
    }


def get_analytics_trends() -> Dict[str, Any]:
    """
    Get trend analytics

    Returns trend data for visualization
    """
    growing = get_top_performers(10, by="growth")
    declining = get_low_performers(10)
    stable = get_top_performers(10, by="stability")

    return {
        "growing": growing,
        "declining": declining,
        "stable": stable,
    }
