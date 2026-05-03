"""
AI Chat Service with RAG Pipeline + Decision Assistant
Handles intent classification, context building, LLM calls, and memory management.

NEW: Routes forecast-related intents to structured Decision Assistant responses
instead of plain LLM text.
"""
from typing import Dict, Any, Optional, List, Union
import asyncio
import json
import pandas as pd

from services.intent_classifier import (
    classify_intent,
    Intent,
    get_follow_up_suggestions,
    extract_days,
)
from services.trust_service import TrustCalculator
from services.insight_service import InsightGenerator
from services.alert_service import AlertService
from services.suggestion_service import SuggestionService
from services.model_service import (
    get_or_train_model,
    predict,
    get_feature_importance,
    predict_from_market_data,
    DATE_COL,
    TARGET_COL,
)
from app.insight_schemas import (
    DecisionAssistantChatResponse,
    ResponseType,
    ConfidenceBlock,
    RiskLevel,
    ConfidenceLevel,
)

# =========================================================
# INTENT ROUTING CONFIGURATION
# =========================================================

# Intents that use structured Decision Assistant response (no LLM)
STRUCTURED_INTENTS = {
    Intent.FORECAST,
    Intent.SMART_FORECAST,
    Intent.PRODUCT_INFO,
    Intent.PRODUCT_ANALYSIS,
    Intent.SEASONALITY,
    Intent.WEATHER_IMPACT,
}

# Intents that use LLM text response
TEXT_INTENTS = {
    Intent.GENERAL,
    Intent.RECOMMENDATIONS,
    Intent.TRENDS,
    Intent.CATEGORY_STATS,
    Intent.REGION_STATS,
    Intent.DATASET_INFO,
    Intent.PRODUCT_SEARCH,
    Intent.COMPARISON,
    Intent.TOP_PRODUCTS,
    Intent.LOW_PERFORMERS,
}

# Kazakhstan market intents - use structured response
KZ_INTENTS = {
    Intent.KZ_ANALYSIS,
    Intent.KZ_ANALYSIS_DETAIL,
    Intent.KZ_CITY_PROFIT,
    Intent.KZ_COMPETITOR,
    Intent.KZ_WHOLESALE,
}

# Store last KZ analysis result for progressive disclosure follow-ups
# Key: user_id, Value: {product_name, result, timestamp}
_kz_analysis_cache: Dict[int, Dict[str, Any]] = {}

# =========================================================
# DB PERSISTENCE HELPERS
# =========================================================

def _db_save_message(
    user_id: int,
    role: str,
    content: str,
    intent: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """Save a chat message to the database (fire-and-forget, never raises)."""
    try:
        from app.database import SessionLocal
        from app.models import ChatHistory
        db = SessionLocal()
        try:
            msg = ChatHistory(
                user_id=user_id,
                role=role,
                content=content[:4000],  # cap to avoid huge DB entries
                intent=intent,
                data_json=json.dumps(data, ensure_ascii=False, default=str) if data else None,
            )
            db.add(msg)
            db.commit()
        finally:
            db.close()
    except Exception:
        pass  # DB unavailable — in-memory still works


def _db_load_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Load recent chat history from the database."""
    try:
        from app.database import SessionLocal
        from app.models import ChatHistory
        from sqlalchemy import desc
        db = SessionLocal()
        try:
            rows = (
                db.query(ChatHistory)
                .filter(ChatHistory.user_id == user_id)
                .order_by(desc(ChatHistory.created_at))
                .limit(limit)
                .all()
            )
            rows = list(reversed(rows))  # oldest first
            return [
                {
                    "role": r.role,
                    "content": r.content,
                    "intent": r.intent,
                    "timestamp": r.created_at.isoformat(),
                    "data": json.loads(r.data_json) if r.data_json else None,
                }
                for r in rows
            ]
        finally:
            db.close()
    except Exception:
        return []


def _restore_last_product_from_history(user_id: int, db_history: List[Dict[str, Any]]) -> None:
    """
    Scan DB history in reverse to find the last product the user discussed.
    Sets chat_memory last_product so resolve_reference works after session restore.
    """
    # KZ/product intents that carry a meaningful search_query
    product_intents = {
        "kz_analysis", "kz_analysis_detail", "kz_city_profit",
        "product_search", "product_info", "product_analysis",
        "comparison", "smart_forecast",
    }
    for msg in reversed(db_history):
        if msg.get("role") != "user":
            continue
        intent = msg.get("intent", "")
        if intent not in product_intents:
            continue
        # Re-classify to extract entities
        try:
            from services.intent_classifier import classify_intent
            _, entities = classify_intent(msg["content"])
            sq = entities.get("search_query")
            pids = entities.get("product_ids", [])
            product = sq or (pids[-1] if pids else None)
            if product:
                chat_memory.track_entities(user_id=user_id, search_query=product, intent=intent)
                return
        except Exception:
            continue


def _db_clear_history(user_id: int) -> int:
    """Delete all chat messages for user. Returns count deleted."""
    try:
        from app.database import SessionLocal
        from app.models import ChatHistory
        db = SessionLocal()
        try:
            count = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).delete()
            db.commit()
            return count
        finally:
            db.close()
    except Exception:
        return 0

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

# Kazakhstan Market Services
from services.kz_market_service import kz_market_service
from services.profit_calculator_service import profit_calculator
from services.web_search_service import web_search_service
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


# =========================================================
# DECISION ASSISTANT RESPONSE BUILDER
# =========================================================

def build_decision_response(
    product_id: str,
    intent: Intent,
    entities: Dict[str, Any],
    df: pd.DataFrame,
    horizon_days: int = 7,
    store_id: Optional[str] = None,
    model_type: str = "random_forest",
) -> DecisionAssistantChatResponse:
    """
    Build structured Decision Assistant response with trust, insights, and alerts.
    Replaces plain LLM text for forecast-related intents.

    Args:
        product_id: Product ID to analyze
        intent: Classified intent
        entities: Extracted entities
        df: Full dataset DataFrame
        horizon_days: Forecast horizon
        store_id: Optional store filter

    Returns:
        DecisionAssistantChatResponse with full structured data
    """
    # Filter data for product
    sub = df[df["Product ID"] == product_id]
    if store_id and "Store ID" in sub.columns:
        sub = sub[sub["Store ID"] == store_id]

    if len(sub) < 30:
        return _build_error_response(
            f"Недостаточно данных для {product_id}. Требуется минимум 30 записей, найдено {len(sub)}.",
            intent, entities
        )

    # Get model and predictions
    trained = get_or_train_model(sub, product_id, store_id, model_type=model_type)
    future_df, preds = predict(trained, horizon_days)

    predictions = [
        {"date": str(d.date()), "predicted_units_sold": round(float(p), 2)}
        for d, p in zip(future_df[DATE_COL], preds)
    ]

    # Extract context from latest record
    latest_record = sub.sort_values(DATE_COL).iloc[-1]
    category = latest_record.get("Category") if "Category" in sub.columns else None
    inventory_level = int(latest_record.get("Inventory Level", 0)) if "Inventory Level" in sub.columns else None

    # Get feature importance
    feature_data = get_feature_importance(product_id, store_id)
    feature_importances = feature_data.get("features", [])

    # === 1. TRUST LAYER ===
    trust_calculator = TrustCalculator()
    trust_layer = trust_calculator.calculate_trust_layer(
        model_metrics=trained["metrics"],
        trained_at=trained["trained_at"],
        last_data_date=trained["last_date"],
        historical_demand=sub[TARGET_COL],
        sample_size=len(sub),
    )

    # === 2. INSIGHTS ===
    insight_generator = InsightGenerator()
    insights = insight_generator.generate_insights(
        product_id=product_id,
        predictions=predictions,
        historical_data=sub,
        model_metrics=trained["metrics"],
        feature_importances=feature_importances,
        inventory_level=inventory_level,
        category=category,
    )

    # === 3. ALERTS ===
    alert_service = AlertService()
    alerts = alert_service.generate_alerts(
        product_id=product_id,
        predictions=predictions,
        historical_data=sub,
        model_metrics=trained["metrics"],
        inventory_level=inventory_level,
        category=category,
    )

    # === 4. SUGGESTIONS (Action Chaining) ===
    suggestion_service = SuggestionService()

    # Determine trend direction
    total_predicted = sum(p["predicted_units_sold"] for p in predictions)
    avg_daily = total_predicted / len(predictions) if predictions else 0
    hist_avg = sub[TARGET_COL].tail(7).mean()

    if avg_daily > hist_avg * 1.1:
        trend_direction = "increasing"
    elif avg_daily < hist_avg * 0.9:
        trend_direction = "decreasing"
    else:
        trend_direction = "stable"

    forecast_context = {
        "risk_level": insights.risk.level.value,
        "confidence": trust_layer.confidence.value,
        "trend_direction": trend_direction,
        "category": category,
    }

    suggestions = suggestion_service.generate_suggestions(
        product_id=product_id,
        forecast_context=forecast_context,
        alerts=[a.model_dump() for a in alerts],
        user_role="admin",
    )

    # === BUILD RESPONSE ===
    confidence_block = ConfidenceBlock(
        level=trust_layer.confidence,
        score=trust_layer.confidence_score,
        factors=[f.model_dump() for f in trust_layer.based_on],
        explanation=trust_layer.confidence_explanation,
    )

    # What to do next from top action item
    what_to_do = None
    if insights.what_to_do:
        top_action = insights.what_to_do[0]
        what_to_do = f"{top_action.action}. {top_action.reason}"

    # Check for critical alerts
    has_critical = any(a.severity.value == "critical" for a in alerts)

    # Build human-readable reply for backward compatibility
    reply_parts = [insights.summary.headline]
    if insights.summary.detail:
        reply_parts.append(insights.summary.detail)
    if what_to_do:
        reply_parts.append(f"\nРекомендация: {what_to_do}")
    if has_critical:
        reply_parts.append("\n⚠️ Есть критические алерты, требующие внимания!")
    reply = "\n\n".join(reply_parts)

    return DecisionAssistantChatResponse(
        response_type=ResponseType.STRUCTURED,
        intent=intent.value,
        entities=entities,
        summary=insights.summary.headline,
        why_it_happened=insights.why_it_happened.primary_explanation,
        risk_level=insights.risk.level,
        confidence=confidence_block,
        what_to_do_next=what_to_do,
        action_items=[item.model_dump() for item in insights.what_to_do],
        suggested_questions=[s.model_dump() for s in suggestions],
        data={
            "predictions": predictions,
            "chart": {
                "type": "line",
                "title": f"Прогноз спроса - {product_id}",
                "x_key": "date",
                "y_key": "predicted_units_sold",
            },
            "metrics": {
                "total_predicted": round(total_predicted, 2),
                "avg_daily": round(avg_daily, 2),
                "model_r2": trained["metrics"]["r2"],
                "model_mae": trained["metrics"]["mae"],
            }
        },
        insights=insights,
        trust=trust_layer,
        alerts=[a.model_dump() for a in alerts],
        has_critical_alert=has_critical,
        images=None,
        reply=reply,
    )


def _build_error_response(
    error_msg: str,
    intent: Intent,
    entities: Dict[str, Any],
) -> DecisionAssistantChatResponse:
    """Build error response when data is insufficient"""
    return DecisionAssistantChatResponse(
        response_type=ResponseType.TEXT,
        intent=intent.value,
        entities=entities,
        summary=None,
        why_it_happened=None,
        risk_level=None,
        confidence=None,
        what_to_do_next=None,
        action_items=[],
        suggested_questions=[],
        data=None,
        insights=None,
        trust=None,
        alerts=[],
        has_critical_alert=False,
        images=None,
        reply=error_msg,
    )


# =========================================================
# KAZAKHSTAN MARKET RESPONSE BUILDER
# =========================================================

def _format_number(num: float) -> str:
    """Format large numbers with K/M suffix"""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.0f}K"
    return f"{num:.0f}"


def _format_currency(num: float, currency: str = "₸") -> str:
    """Format currency with thousands separator"""
    return f"{num:,.0f} {currency}"


def _cache_kz_result(user_id: int, product_name: str, result: Any) -> None:
    """Cache KZ analysis result for progressive disclosure follow-ups"""
    import time
    _kz_analysis_cache[user_id] = {
        "product_name": product_name,
        "result": result,
        "timestamp": time.time(),
    }


def _get_cached_kz_result(user_id: int) -> Optional[Dict[str, Any]]:
    """Get cached KZ analysis result if still valid (within 30 minutes)"""
    import time
    cache = _kz_analysis_cache.get(user_id)
    if cache and (time.time() - cache["timestamp"]) < 1800:  # 30 minutes
        return cache
    return None


def _format_short_kz_response(result: Any, markup_percent: float) -> str:
    """Format SHORT KZ analysis response for progressive disclosure"""
    reply_parts = []

    # Header with status
    status_emoji = "✅" if result.is_profitable else "⚠️"
    reply_parts.append(f"# {status_emoji} Анализ рынка: {result.product_name}")
    reply_parts.append("")

    # Price Summary Box (condensed)
    reply_parts.append("## 💰 Ценообразование")
    if result.retail_price_usd and result.wholesale_discount_applied:
        reply_parts.append(f"- Розничная цена: ${result.retail_price_usd:,.2f} (AliExpress/Amazon)")
        reply_parts.append(f"- Оптовая цена: ${result.product_cost_usd:,.2f} (-20% скидка)")
    else:
        reply_parts.append(f"- Оптовая цена: ${result.product_cost_usd:,.2f}")
    reply_parts.append(f"- В тенге: {_format_currency(result.product_cost_kzt)}")
    reply_parts.append(f"- Курс USD/KZT: {result.currency_rate}")
    reply_parts.append(f"- Наценка: {markup_percent}%")
    reply_parts.append("")

    # Competitor Analysis (condensed)
    if result.competitor_analysis:
        ca = result.competitor_analysis
        competition_level = "Высокая" if ca.competitor_count > 10 else "Средняя" if ca.competitor_count > 5 else "Низкая"
        reply_parts.append("## 🏪 Конкуренты на Kaspi.kz")
        reply_parts.append(f"- Средняя цена: {_format_currency(ca.avg_price_kzt)}")
        reply_parts.append(f"- Диапазон: {_format_currency(ca.min_price_kzt)} - {_format_currency(ca.max_price_kzt)}")
        reply_parts.append(f"- Конкуренция: {competition_level}")
        reply_parts.append("")

    # Investment Summary (condensed)
    if result.investment:
        inv = result.investment
        reply_parts.append("## 💵 Инвестиции и ROI")
        reply_parts.append(f"- Начальные инвестиции: ~${inv.total_investment_usd:,.0f}")
        reply_parts.append(f"- Ожидаемая прибыль: {_format_number(inv.expected_profit_kzt)}₸/мес")
        reply_parts.append(f"- ROI: {inv.roi_percent:.0f}%")
        reply_parts.append("")

    # Risk Analysis (condensed)
    if result.risk_analysis:
        ra = result.risk_analysis
        risk_emoji = "🟢" if ra.overall_risk == "low" else "🟡" if ra.overall_risk == "medium" else "🔴"
        risk_label = {"low": "Низкий", "medium": "Средний", "high": "Высокий"}.get(ra.overall_risk, ra.overall_risk)
        reply_parts.append(f"## ⚠️ Риски: {risk_emoji} {risk_label} ({ra.risk_score:.0f}/100)")
        # Show top 2 risk factors
        for factor in ra.factors[:2]:
            f_emoji = "🟢" if factor["level"] == "низкий" else "🟡" if factor["level"] == "средний" else "🔴"
            reply_parts.append(f"- {factor['factor']}: {factor['level']}")
        reply_parts.append("")

    # Divider and options
    reply_parts.append("---")
    reply_parts.append("📊 **Хотите подробнее?** Я могу показать:")
    reply_parts.append("• Анализ по городам (таблица + карта)")
    reply_parts.append("• Советы по продаже")
    reply_parts.append("• Детальный анализ рисков")
    reply_parts.append("• Всё вместе")

    return "\n".join(reply_parts)


def _format_cities_detail(result: Any) -> str:
    """Format cities detail table for KZ analysis"""
    reply_parts = []

    reply_parts.append("## 🏙️ Анализ по городам")
    reply_parts.append("")
    reply_parts.append("| Город | Цена | Прибыль/шт | Спрос | Прибыль/мес | Статус |")
    reply_parts.append("|-------|------|------------|-------|-------------|--------|")

    for city in result.cities:
        profit_formatted = _format_number(city.total_monthly_profit_kzt) + "₸"
        reply_parts.append(
            f"| {city.city_name} | {_format_currency(city.recommended_price_kzt)} | "
            f"{_format_currency(city.profit_per_unit_kzt)} | {city.estimated_monthly_demand} | "
            f"{profit_formatted} | {city.status_icon} |"
        )

    reply_parts.append("")
    reply_parts.append(f"**Всего городов:** {len(result.cities)} | "
                       f"🟢 Выгодных: {result.profitable_cities_count} | "
                       f"🟡 Рискованных: {result.risky_cities_count} | "
                       f"🔴 Невыгодных: {len(result.avoid_cities)}")

    # Best and avoid cities
    if result.best_cities:
        best_3 = ", ".join(result.best_cities[:3])
        reply_parts.append(f"\n🎯 **Лучшие города:** {best_3}")

    if result.avoid_cities:
        avoid_3 = ", ".join(result.avoid_cities[:3])
        reply_parts.append(f"⛔ **Избегай:** {avoid_3}")

    return "\n".join(reply_parts)


def _format_sales_tips(result: Any) -> str:
    """Format sales tips for KZ analysis"""
    reply_parts = []

    if result.market_insights:
        mi = result.market_insights
        reply_parts.append("## 💡 Советы по продаже")
        reply_parts.append("")
        reply_parts.append(f"**Лучшие месяцы:** {', '.join(mi.best_selling_months)}")
        reply_parts.append(f"**Целевая аудитория:** {mi.target_audience}")
        reply_parts.append(f"**Kaspi рассрочка:** {mi.kaspi_installment_impact}")
        reply_parts.append("")
        reply_parts.append("### Рекомендации:")
        for tip in mi.marketing_tips:
            reply_parts.append(f"- {tip}")
    else:
        reply_parts.append("## 💡 Советы по продаже")
        reply_parts.append("")
        reply_parts.append("- Используй Kaspi рассрочку для увеличения конверсии")
        reply_parts.append("- Фокусируйся на городах с высокой покупательской способностью")
        reply_parts.append("- Следи за сезонностью (ноябрь-декабрь пик продаж)")
        reply_parts.append("- Поддерживай рейтинг выше 4.5 для лучшего ранжирования")

    return "\n".join(reply_parts)


def _format_risk_detail(result: Any) -> str:
    """Format detailed risk analysis for KZ analysis"""
    reply_parts = []

    if result.risk_analysis:
        ra = result.risk_analysis
        risk_emoji = "🟢" if ra.overall_risk == "low" else "🟡" if ra.overall_risk == "medium" else "🔴"
        risk_label = {"low": "Низкий", "medium": "Средний", "high": "Высокий"}.get(ra.overall_risk, ra.overall_risk)

        reply_parts.append("## ⚠️ Детальный анализ рисков")
        reply_parts.append(f"\n**Общий риск:** {risk_emoji} {risk_label} ({ra.risk_score:.0f}/100)")
        reply_parts.append("")

        reply_parts.append("### Факторы риска:")
        for factor in ra.factors:
            f_emoji = "🟢" if factor["level"] == "низкий" else "🟡" if factor["level"] == "средний" else "🔴"
            reply_parts.append(f"- {f_emoji} **{factor['factor']}**: {factor['description']}")

        reply_parts.append(f"\n📅 **Сезонность:** {ra.seasonality_note}")

        # Add risk mitigation tips
        reply_parts.append("\n### 🛡️ Как снизить риски:")
        if ra.overall_risk == "high":
            reply_parts.append("- Начни с минимальной партии (10-20 шт)")
            reply_parts.append("- Тестируй спрос перед масштабированием")
            reply_parts.append("- Держи резерв на возвраты (10-15%)")
        elif ra.overall_risk == "medium":
            reply_parts.append("- Диверсифицируй по городам")
            reply_parts.append("- Следи за курсом валют")
            reply_parts.append("- Используй предзаказы для оценки спроса")
        else:
            reply_parts.append("- Масштабируй постепенно")
            reply_parts.append("- Реинвестируй прибыль")
            reply_parts.append("- Строй лояльность клиентов")
    else:
        reply_parts.append("## ⚠️ Анализ рисков")
        reply_parts.append("Данные о рисках недоступны для этого продукта.")

    return "\n".join(reply_parts)


def _format_full_kz_response(result: Any, markup_percent: float) -> str:
    """Format FULL KZ analysis response (all details)"""
    reply_parts = []

    # Header with status
    status_emoji = "✅" if result.is_profitable else "⚠️"
    reply_parts.append(f"# {status_emoji} Полный анализ рынка: {result.product_name}")
    reply_parts.append("")

    # Warnings block (if any)
    if result.warnings:
        reply_parts.append("## ⚠️ Важные предупреждения")
        for warning in result.warnings:
            reply_parts.append(f"- {warning}")
        reply_parts.append("")

    # Price Summary Box
    reply_parts.append("## 💰 Ценообразование")
    reply_parts.append("```")
    if result.retail_price_usd and result.wholesale_discount_applied:
        reply_parts.append(f"Розничная цена:   ${result.retail_price_usd:,.2f} (AliExpress/Amazon)")
        reply_parts.append(f"Оптовая цена:     ${result.product_cost_usd:,.2f} (-20% скидка)")
    else:
        reply_parts.append(f"Оптовая цена:     ${result.product_cost_usd:,.2f}")
    reply_parts.append(f"В тенге:          {_format_currency(result.product_cost_kzt)}")
    reply_parts.append(f"Курс USD/KZT:     {result.currency_rate}")
    reply_parts.append(f"Наценка:          {markup_percent}%")
    reply_parts.append("```")
    reply_parts.append("")

    # Competitor Analysis
    if result.competitor_analysis:
        ca = result.competitor_analysis
        position_emoji = "✅" if ca.price_position == "below" else "⚠️" if ca.price_position == "above" else "➖"
        reply_parts.append("## 🏪 Конкуренты на Kaspi.kz")
        reply_parts.append("```")
        reply_parts.append(f"Средняя цена:     {_format_currency(ca.avg_price_kzt)}")
        reply_parts.append(f"Диапазон:         {_format_currency(ca.min_price_kzt)} - {_format_currency(ca.max_price_kzt)}")
        reply_parts.append(f"Твоя цена vs рынок: {ca.our_price_vs_market:+.1f}% {position_emoji}")
        reply_parts.append(f"Продавцов:        {ca.competitor_count}")
        reply_parts.append("```")
        reply_parts.append("")

    # Investment Summary
    if result.investment:
        inv = result.investment
        reply_parts.append("## 💵 Инвестиции и ROI")
        reply_parts.append("```")
        reply_parts.append(f"Закупка:          {inv.recommended_quantity} шт × ${result.product_cost_usd:,.0f}")
        reply_parts.append(f"Сумма вложений:   ${inv.total_investment_usd:,.0f} ({_format_currency(inv.total_investment_kzt)})")
        reply_parts.append(f"Ожидаемая выручка: {_format_currency(inv.expected_revenue_kzt)}")
        reply_parts.append(f"Чистая прибыль:   {_format_currency(inv.expected_profit_kzt)} ({_format_number(inv.expected_profit_kzt)}₸)")
        reply_parts.append(f"ROI:              {inv.roi_percent:.0f}%")
        reply_parts.append(f"Окупаемость:      {inv.payback_months:.1f} мес")
        reply_parts.append(f"Точка безубыточности: {inv.break_even_units} шт")
        reply_parts.append("```")
        reply_parts.append("")

    # Cities Table
    reply_parts.append(_format_cities_detail(result))
    reply_parts.append("")

    # Risk Analysis
    reply_parts.append(_format_risk_detail(result))
    reply_parts.append("")

    # Market Insights
    reply_parts.append(_format_sales_tips(result))
    reply_parts.append("")

    # Final Recommendation
    reply_parts.append("## ✅ Итоговая рекомендация")
    reply_parts.append("")

    if result.best_cities:
        best_3 = ", ".join(result.best_cities[:3])
        reply_parts.append(f"🎯 **Продавай в:** {best_3}")

    if result.avoid_cities:
        avoid_3 = ", ".join(result.avoid_cities[:3])
        reply_parts.append(f"⛔ **Избегай:** {avoid_3}")

    if result.investment:
        reply_parts.append(f"💸 **Инвестируй:** ${result.investment.total_investment_usd:,.0f} → получи {_format_number(result.investment.expected_profit_kzt)}₸/мес")

    return "\n".join(reply_parts)


async def build_kz_response(
    intent: Intent,
    entities: Dict[str, Any],
    message: str,
    user_id: int = 0,
) -> Dict[str, Any]:
    """
    Build Kazakhstan market analysis response.

    Args:
        intent: KZ-related intent
        entities: Extracted entities (product name, cities, price, markup)
        message: Original user message
        user_id: User ID for caching results

    Returns:
        Structured response with KZ analysis data
    """
    search_query = entities.get("search_query", "")
    kz_cities = entities.get("kz_cities", [])
    price_usd = entities.get("price_usd")
    markup_percent = entities.get("markup_percent", 25.0)
    category = entities.get("category", "electronics")

    # If no product name, try to extract from message
    if not search_query:
        words = message.strip().split()
        kz_words = {
            # Russian
            "казахстан", "кз", "kazakhstan", "продавать", "анализ", "прибыль",
            "город", "алматы", "астана", "в", "для", "по", "рынок", "продай",
            "сделай", "покажи", "дай", "этот", "продукт", "товар",
            # Kazakh
            "қазақстан", "қр", "қалалар", "қалаларына", "қалаларда",
            "арнап", "арналған", "анализ", "жасасы", "жаса", "жасашы",
            "талдау", "сату", "сатуға", "болады", "ма", "осы", "бұл",
            "өнімді", "продуктты", "тауарды", "қай", "қайда",
        }
        filtered = [w for w in words if w.lower() not in kz_words and len(w) > 1]
        if filtered:
            search_query = " ".join(filtered[:5])

    # Handle KZ_ANALYSIS_DETAIL - progressive disclosure follow-up
    if intent == Intent.KZ_ANALYSIS_DETAIL:
        detail_type = entities.get("kz_detail_type", "full")

        # Try to get cached result
        cached = _get_cached_kz_result(user_id)
        if cached:
            result = cached["result"]
            product_name = cached["product_name"]

            if detail_type == "cities":
                reply = _format_cities_detail(result)
                response_type = "kz_cities_detail"
            elif detail_type == "sales_tips":
                reply = _format_sales_tips(result)
                response_type = "kz_sales_tips"
            elif detail_type == "risk_detail":
                reply = _format_risk_detail(result)
                response_type = "kz_risk_detail"
            else:  # full
                reply = _format_full_kz_response(result, markup_percent)
                response_type = "kz_analysis_full"

            return {
                "reply": reply,
                "response_type": response_type,
                "intent": intent.value,
                "entities": entities,
                "data": result.to_dict(),
                "suggested_questions": [
                    {"text": "📦 Другой товар", "prompt": "Samsung Galaxy S24 в Казахстане"},
                    {"text": "🏙️ Анализ по городам", "prompt": "Анализ по городам"},
                    {"text": "💡 Советы по продаже", "prompt": "Советы по продаже"},
                ],
            }
        else:
            # No cached result - ask user to start new analysis
            return {
                "reply": "❌ Нет предыдущего анализа для детализации.\n\nПопробуй сначала запросить анализ товара, например:\n`Samsung Galaxy в Казахстане`",
                "response_type": "error",
                "intent": intent.value,
                "entities": entities,
                "suggested_questions": [
                    {"text": "📱 iPhone 15 в КЗ", "prompt": "iPhone 15 в Казахстане"},
                    {"text": "📦 Samsung Galaxy в КЗ", "prompt": "Samsung Galaxy в Казахстане"},
                ],
            }

    if intent == Intent.KZ_ANALYSIS:
        product_name = search_query or "iPhone 15"

        # === STEP 1: Web search — find ALL market info ===
        market_data = await web_search_service.comprehensive_product_analysis(product_name)

        # === STEP 2: Get competitor prices for city analysis ===
        competitors = await web_search_service.get_competitor_prices(product_name, market="kaspi")
        competitor_prices = [c.price_kzt for c in competitors if c.price_kzt > 0]

        # === STEP 3: Determine wholesale price ===
        if price_usd:
            wholesale_price_usd = price_usd
            retail_price_usd = price_usd
        else:
            retail_price_usd = market_data.get("wholesale_price_usd", 100.0)
            wholesale_price_usd = profit_calculator.apply_wholesale_discount(retail_price_usd)

        # === STEP 4: ML Model — predict demand score from ALL market features ===
        competitor_price_usd = market_data.get("avg_retail_price_kzt", wholesale_price_usd * 1.3 * 450) / 450
        kaspi_data = market_data.get("kaspi", {})
        news_data = market_data.get("news", {})
        mkt_data = market_data.get("market", {})

        ml_result = predict_from_market_data(
            price_usd=wholesale_price_usd,
            competitor_price_usd=max(competitor_price_usd, wholesale_price_usd * 0.8),
            rating=market_data.get("avg_rating", 3.5),
            review_count=market_data.get("review_count", 0),
            trend_direction=market_data.get("trend_direction", "stable"),
            popularity_score=market_data.get("popularity_score", 50),
            # KZ-specific signals
            has_kaspi_installment=kaspi_data.get("has_installment", False),
            kaspi_sellers=kaspi_data.get("kaspi_sellers", 0),
            news_sentiment_score=news_data.get("sentiment_score", 0),
            market_saturation_score=mkt_data.get("saturation_score", 0.5),
            is_new_model=news_data.get("is_new_model", False),
            has_supply_issue=news_data.get("has_supply_issue", False),
            yoy_growth_percent=mkt_data.get("yoy_growth_percent", 0.0),
        )

        # === STEP 5: City-level profitability analysis ===
        kz_result = profit_calculator.analyze_all_cities(
            product_cost_usd=wholesale_price_usd,
            category=category.lower() if category else "electronics",
            markup_percent=markup_percent,
            product_name=product_name,
            competitor_prices=competitor_prices,
        )
        kz_result.retail_price_usd = retail_price_usd
        kz_result.wholesale_discount_applied = not bool(price_usd)

        # === CACHE RESULT FOR PROGRESSIVE DISCLOSURE ===
        _cache_kz_result(user_id, product_name, kz_result)

        # === STEP 6: Claude formats the combined analysis ===
        ml_grade = ml_result["market_grade"]
        ml_score = ml_result["demand_score"]
        ml_percentile = ml_result["demand_percentile"]
        top_factor = ml_result["key_factors"][0] if ml_result["key_factors"] else {}

        kz_sigs = ml_result.get("kz_signals", {})
        key_events = news_data.get("key_events", [])
        llm_context = f"""Өнім: {product_name}

=== БАҒА ДЕРЕКТЕРІ ===
Ұтым баға (оптом): ${wholesale_price_usd:.0f} = {wholesale_price_usd * market_data.get('usd_kzt_rate', 450):,.0f} ₸
Бәсекелестер орт. бағасы: {market_data.get('avg_retail_price_kzt', 0):,.0f} ₸
Маржа: {market_data.get('profit_margin_percent', 0):.1f}%
Бәсекелестер саны: {market_data.get('competitor_count', 0)}

=== РЕЙТИНГ ЖӘНЕ ПІКІРЛЕР ===
Жалпы рейтинг: {market_data.get('avg_rating', 0)}/5
Пікірлер (global + Kaspi): {market_data.get('review_count', 0):,}
Kaspi рейтинг: {kaspi_data.get('kaspi_rating', 0)}/5 ({kaspi_data.get('kaspi_reviews', 0)} пікір)
Kaspi сатушылар: {kaspi_data.get('kaspi_sellers', 0)}
Kaspi рассрочка: {'✅ бар' if kaspi_data.get('has_installment') else '❌ жоқ'}

=== ТРЕНД ЖӘНЕ ЖАҢАЛЫҚТАР ===
Тренд: {market_data.get('trend_direction', 'stable')} | Танымалдық: {market_data.get('popularity_score', 50)}/100
Жаңалықтар сентименті: {news_data.get('sentiment', 'neutral')} ({news_data.get('sentiment_score', 0):+d})
Маңызды оқиғалар: {', '.join(key_events) if key_events else 'жоқ'}
Жаңа модель шықты ма: {'✅ иә' if news_data.get('is_new_model') else 'жоқ'}
Тапшылық: {'⚠️ иә' if news_data.get('has_supply_issue') else 'жоқ'}

=== НАРЫҚ ӨЛШЕМІ ===
Категория: {mkt_data.get('category', '')}
Нарық өлшемі: {mkt_data.get('size_level', 'medium')}
Бәсекелестік деңгейі: {mkt_data.get('saturation_level', 'medium')}
Жылдық өсім: {mkt_data.get('yoy_growth_percent', 0):.1f}%

=== ML МОДЕЛЬ НӘТИЖЕСІ (Amazon 551K датасетінде оқытылған) ===
Сұраныс ұпайы: {ml_score}/100 | Баға: {ml_grade} | Үздік {100 - ml_percentile:.0f}%-да
Модель сенімділігі: {ml_result['ml_confidence'] * 100:.0f}%
KZ коррекциялары:
  - Kaspi рассрочка: {kz_sigs.get('kaspi_installment_boost', 0):+.1f}
  - Жаңалықтар әсері: {kz_sigs.get('news_impact', 0):+.1f}
  - Нарық тапшылығы: {kz_sigs.get('saturation_penalty', 0):+.1f}
  - Санаттың өсімі: {kz_sigs.get('category_growth_boost', 0):+.1f}
Басты фактор: {top_factor.get('label', '')}
ML ұсынысы: {ml_result['recommendation']}

=== ҚАЗАҚСТАН ҚАЛАЛАРЫ ===
Ең жақсы қалалар: {', '.join(kz_result.best_cities[:3]) if kz_result.best_cities else 'анықталмады'}
Болдырмауға тиіс: {', '.join(kz_result.avoid_cities[:2]) if kz_result.avoid_cities else 'жоқ'}
Пайдалы қалалар: {kz_result.profitable_cities_count}/{len(kz_result.cities)}
ROI: {kz_result.investment.roi_percent:.0f}%

=== ТӘУЕКЕЛДЕР ===
{chr(10).join('- ' + r for r in market_data.get('risks', ['жоқ'])[:4])}"""

        llm_prompt = f"""{llm_context}

Жоғарыдағы деректерге сүйене отырып, {product_name} өнімін Қазақстанда сату туралы қысқаша талдау жаса (қазақша жауап бер). Мыналарды қамти: сұраныс деңгейі, ең тиімді қалалар, тәуекелдер, және жалпы ұсыныс."""

        llm_system = (
            "Сен – Қазақстан нарығын зерттейтін сарапшы AI. "
            "Берілген деректер негізінде қысқаша, нақты, қазақша талдау жаса. "
            "Маркдаун форматында жауап бер (тақырыптар, тізімдер). "
            "Жалпы ұсыныс, сұраныс деңгейі, тәуекелдер — міндетті түрде."
        )
        llm_reply = ask_llm(
            system_prompt=llm_system,
            user_prompt=llm_prompt,
        )

        # Append structured details after LLM response
        city_summary = _format_cities_detail(kz_result)
        full_reply = f"{llm_reply}\n\n---\n\n{city_summary}"

        return {
            "reply": full_reply,
            "response_type": "kz_analysis_ml",
            "intent": intent.value,
            "entities": entities,
            "data": {
                **kz_result.to_dict(),
                "ml_analysis": ml_result,
                "market_data": market_data,
            },
            "available_details": ["cities", "sales_tips", "risk_detail", "full"],
            "suggested_questions": [
                {"text": "🏙️ Қалалар бойынша талдау", "prompt": "Қалалар бойынша талдауды көрсет"},
                {"text": "💡 Сату кеңестері", "prompt": "Сату кеңестері"},
                {"text": "⚠️ Тәуекелдер", "prompt": "Тәуекелдерді толық талда"},
                {"text": "📊 Толық талдау", "prompt": "Барлық ақпаратты көрсет"},
            ],
        }

    elif intent == Intent.KZ_CITY_PROFIT:
        # Single city analysis
        city_id = kz_cities[0] if kz_cities else "almaty"

        if not price_usd:
            price_info = await web_search_service.search_product_price(search_query or "iPhone 15")
            price_usd = price_info.price_usd

        analysis = profit_calculator.calculate_city_profit(
            product_cost_usd=price_usd,
            category=category.lower() if category else "electronics",
            city_id=city_id,
            markup_percent=markup_percent,
        )

        if analysis is None:
            return {
                "reply": f"❌ Город `{city_id}` не найден",
                "response_type": "error",
                "intent": intent.value,
                "entities": entities,
            }

        status_text = {"profitable": "Выгодно", "risky": "Рискованно", "unprofitable": "Невыгодно"}

        reply_parts = [
            f"# 🏙️ Анализ: {analysis.city_name}",
            "",
            f"**Продукт:** {search_query or 'Product'}",
            "",
            "## 💰 Финансы",
            "```",
            f"Себестоимость:    {_format_currency(analysis.product_cost_kzt)}",
            f"Логистика:        {_format_currency(analysis.logistics_cost_kzt)}",
            f"Итого затрат:     {_format_currency(analysis.total_cost_kzt)}",
            f"─────────────────────────",
            f"Цена продажи:     {_format_currency(analysis.recommended_price_kzt)}",
            f"Прибыль/шт:       {_format_currency(analysis.profit_per_unit_kzt)}",
            f"Маржа:            {analysis.margin_percent:.1f}%",
            "```",
            "",
            "## 📈 Прогноз продаж",
            "```",
            f"Спрос:            ~{analysis.estimated_monthly_demand} шт/мес",
            f"Месячная прибыль: {_format_currency(analysis.total_monthly_profit_kzt)}",
            "```",
            "",
            f"## Статус: {analysis.status_icon} {status_text.get(analysis.status.value, analysis.status.value)}",
            "",
            "### Факторы:",
            f"- Покупательская способность: {analysis.purchasing_power_index:.2f}",
            f"- Уровень конкуренции: {(1 - analysis.competition_factor) * 100:.0f}%",
            f"- Индекс доступности: {analysis.affordability_index:.2f}",
        ]

        reply = "\n".join(reply_parts)

        return {
            "reply": reply,
            "response_type": "kz_city_profit",
            "intent": intent.value,
            "entities": entities,
            "data": analysis.to_dict(),
            "suggested_questions": [
                {"text": "🗺️ Все города", "prompt": f"{search_query} в Казахстане"},
                {"text": "📍 Сравни с Алматы", "prompt": f"Прибыль {search_query} в Алматы"},
                {"text": "🔄 Изменить наценку", "prompt": f"Прибыль {search_query} в {analysis.city_name} наценка 30%"},
            ],
        }

    elif intent == Intent.KZ_COMPETITOR:
        competitors = await web_search_service.get_competitor_prices(
            search_query or "iPhone 15",
            market="kaspi",
        )

        prices = [c.price_kzt for c in competitors if c.price_kzt > 0]
        avg_price = sum(prices) / len(prices) if prices else 0

        reply_parts = [
            f"# 🏪 Конкуренты: {search_query or 'Product'}",
            "",
            "## 📊 Статистика цен на Kaspi.kz",
            "```",
            f"Средняя цена:  {_format_currency(avg_price)}",
            f"Минимум:       {_format_currency(min(prices)) if prices else 'N/A'}",
            f"Максимум:      {_format_currency(max(prices)) if prices else 'N/A'}",
            f"Разброс:       {((max(prices) - min(prices)) / avg_price * 100):.0f}%" if prices and avg_price else "",
            f"Продавцов:     {len(competitors)}",
            "```",
            "",
            "## 🛒 Предложения:",
        ]

        for i, c in enumerate(competitors[:7], 1):
            price_vs_avg = ((c.price_kzt - avg_price) / avg_price * 100) if avg_price else 0
            indicator = "🟢" if price_vs_avg < -5 else "🔴" if price_vs_avg > 5 else "🟡"
            reply_parts.append(f"{i}. {indicator} **{c.seller}**: {_format_currency(c.price_kzt)} ({price_vs_avg:+.0f}%)")

        reply_parts.append("")
        reply_parts.append("💡 **Совет:** Установи цену на 3-5% ниже средней для быстрых продаж")

        reply = "\n".join(reply_parts)

        return {
            "reply": reply,
            "response_type": "kz_competitor",
            "intent": intent.value,
            "entities": entities,
            "data": {
                "product_name": search_query,
                "competitors": [{"seller": c.seller, "price_kzt": c.price_kzt, "platform": c.platform, "url": c.url} for c in competitors],
                "avg_price_kzt": avg_price,
                "min_price_kzt": min(prices) if prices else 0,
                "max_price_kzt": max(prices) if prices else 0,
            },
            "suggested_questions": [
                {"text": "📊 Полный анализ", "prompt": f"{search_query} в Казахстане"},
                {"text": "💰 Оптовая цена", "prompt": f"Оптовая цена {search_query}"},
            ],
        }

    elif intent == Intent.KZ_WHOLESALE:
        price_info = await web_search_service.search_product_price(search_query or "iPhone 15")
        currency_rate = kz_market_service.get_currency_rate("USD")

        reply_parts = [
            f"# 📦 Оптовая цена: {search_query or 'Product'}",
            "",
            "## 💵 Найденная цена",
            "```",
            f"Цена USD:      ${price_info.price_usd:,.2f}",
            f"Цена KZT:      {_format_currency(price_info.price_usd * currency_rate)}",
            f"Источник:      {price_info.source}",
            f"Курс:          1 USD = {currency_rate} KZT",
        ]

        if price_info.price_range:
            reply_parts.append(f"Диапазон:      ${price_info.price_range['min']:,.0f} - ${price_info.price_range['max']:,.0f}")

        reply_parts.append("```")

        if price_info.url:
            reply_parts.append(f"\n🔗 [Открыть источник]({price_info.url})")

        reply_parts.extend([
            "",
            "## 💡 Что дальше?",
            "- Проверь цены на AliExpress и Amazon",
            "- Учти стоимость доставки ($5-30 за единицу)",
            "- Запроси оптовую скидку от 50+ штук",
        ])

        reply = "\n".join(reply_parts)

        return {
            "reply": reply,
            "response_type": "kz_wholesale",
            "intent": intent.value,
            "entities": entities,
            "data": {
                "product_name": price_info.product_name,
                "price_usd": price_info.price_usd,
                "price_kzt": price_info.price_usd * currency_rate,
                "source": price_info.source,
                "url": price_info.url,
                "currency_rate": currency_rate,
            },
            "suggested_questions": [
                {"text": "📊 Анализ по городам", "prompt": f"{search_query} в Казахстане"},
                {"text": "🏪 Цены конкурентов", "prompt": f"Конкуренты {search_query} на Kaspi"},
            ],
        }

    # Fallback
    return {
        "reply": "❌ Не удалось обработать запрос. Попробуй: `iPhone 15 в Казахстане`",
        "response_type": "error",
        "intent": intent.value,
        "entities": entities,
    }


def _track_and_store(
    user_id: int,
    message: str,
    response: str,
    intent: Intent,
    entities: Dict[str, Any],
    data: Optional[Dict] = None,
):
    """Helper to track entities and store messages in chat memory + DB"""
    chat_memory.track_entities(
        user_id=user_id,
        product_ids=entities.get("product_ids"),
        search_query=entities.get("search_query"),
        category=entities.get("category"),
        region=entities.get("region"),
        intent=intent.value
    )

    chat_memory.add_message(user_id=user_id, role="user", content=message, intent=intent.value)
    chat_memory.add_message(user_id=user_id, role="assistant", content=response, data=data, intent=intent.value)

    # Persist to DB
    _db_save_message(user_id, "user", message, intent=intent.value)
    _db_save_message(user_id, "assistant", response, intent=intent.value, data=data)


# =========================================================
# MAIN CHAT HANDLER
# =========================================================

def handle_ai_chat(message: str, user_id: int, language: str = "kk", model_type: str = "random_forest") -> Dict[str, Any]:
    """
    Main handler for AI chat messages with Decision Assistant pipeline.

    Routes forecast-related intents to structured responses,
    others to LLM text responses.

    Args:
        message: User's message
        user_id: User ID for session isolation
        language: Language code for responses (kk, ru, en). Defaults to Kazakh.

    Returns:
        Response dictionary with reply, intent, data, suggestions
    """
    # Step 0: Restore session from DB if in-memory is empty (after restart / new login)
    session_info = chat_memory.get_session_info(user_id)
    if not session_info.get("exists") or session_info.get("message_count", 0) == 0:
        db_history = _db_load_history(user_id, limit=30)
        for msg in db_history:
            chat_memory.add_message(
                user_id=user_id,
                role=msg["role"],
                content=msg["content"],
                intent=msg.get("intent"),
                data=msg.get("data"),
            )

        # Restore last_product from DB history so resolve_reference works after restart
        if db_history:
            _restore_last_product_from_history(user_id, db_history)

    # Step 1: Check for pronoun references ("it", "this product", etc.)
    resolved_reference = chat_memory.resolve_reference(user_id, message)
    if resolved_reference:
        entities_pre = {}
        entities_pre["search_query"] = resolved_reference

    # Step 2: Classify intent and extract entities
    intent, entities = classify_intent(message)

    # Step 3: If reference was resolved, merge it into entities
    if resolved_reference and not entities.get("product_ids") and not entities.get("search_query"):
        entities["search_query"] = resolved_reference

    # Extract key parameters
    product_ids = entities.get("product_ids", [])
    days = entities.get("days", 7)

    # =========================================================
    # KAZAKHSTAN MARKET ANALYSIS ROUTING
    # =========================================================
    if intent in KZ_INTENTS:
        try:
            import asyncio
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    build_kz_response(intent, entities, message, user_id)
                )
            finally:
                loop.close()

            # Track and store for memory
            _track_and_store(
                user_id=user_id,
                message=message,
                response=response.get("reply", ""),
                intent=intent,
                entities=entities,
                data=response.get("data"),
            )

            return response

        except Exception as e:
            import logging
            logging.warning(f"KZ Analysis failed: {e}")
            # Fall through to LLM

    # =========================================================
    # DECISION ASSISTANT ROUTING
    # Route forecast-related intents to structured responses
    # =========================================================
    if intent in STRUCTURED_INTENTS and product_ids:
        try:
            from backend import get_df
            df = get_df()

            response = build_decision_response(
                product_id=product_ids[0],
                intent=intent,
                entities=entities,
                df=df,
                horizon_days=days,
                model_type=model_type,
            )

            # Track and store for memory
            _track_and_store(
                user_id=user_id,
                message=message,
                response=response.reply,
                intent=intent,
                entities=entities,
                data=response.data,
            )

            return response.model_dump()

        except Exception as e:
            # Log error and fall back to LLM
            import logging
            logging.warning(f"Decision Assistant failed, falling back to LLM: {e}")
            # Continue to LLM flow below

    # =========================================================
    # LLM TEXT RESPONSE FLOW (for TEXT_INTENTS or fallback)
    # =========================================================

    # Step 4: Get conversation history (OpenAI messages format for proper multi-turn)
    raw_history = chat_memory.get_history(user_id, limit=12)
    llm_history = [
        {"role": m["role"], "content": m["content"]}
        for m in raw_history
        if m.get("role") in ("user", "assistant")
    ]

    # Step 5: Build RAG context
    context = build_rag_context(intent, entities)

    # Step 6: Build system prompt
    lang_instructions = {
        "kk": "МАҢЫЗДЫ: Қазақ тілінде жауап беріңіз. Барлық жауаптар қазақша болуы керек.",
        "ru": "ВАЖНО: Отвечайте на русском языке. Все ответы должны быть на русском.",
        "en": "IMPORTANT: Respond in English. All responses must be in English.",
    }
    lang_instruction = lang_instructions.get(language, lang_instructions["kk"])

    # Pass entity context in system prompt (not as fake conversation turns)
    entity_ctx = chat_memory.get_entity_context(user_id)
    entity_hint = ""
    if entity_ctx.get("last_product"):
        entity_hint = f"\n[Соңғы талқыланған өнім: {entity_ctx['last_product']}]"

    system_prompt = f"{lang_instruction}{entity_hint}\n\n" + SYSTEM_PROMPT.format(
        context=context,
        history="",  # history now passed as messages, not string
    )

    # Step 7: Call LLM with proper message history
    try:
        response = ask_llm(system_prompt, message, history=llm_history)
    except Exception as e:
        error_messages = {
            "kk": "Кешіріңіз, қате орын алды",
            "ru": "Извините, произошла ошибка",
            "en": "Sorry, I encountered an error"
        }
        response = f"{error_messages.get(language, error_messages['kk'])}: {str(e)}"

    # Step 8: Get chart data if applicable
    chart_data = get_chart_data(intent, entities)

    # Step 9: Generate follow-up suggestions based on context
    # Use SuggestionService for better contextual suggestions when product available
    if product_ids:
        suggestion_svc = SuggestionService()
        suggestion_list = suggestion_svc.generate_suggestions(
            product_id=product_ids[0],
            forecast_context={"risk_level": "low", "confidence": "medium"},
            alerts=[],
        )
        suggestions = [s.model_dump() for s in suggestion_list]
    else:
        # Fall back to simple suggestions
        simple_suggestions = get_follow_up_suggestions(intent, entities)
        suggestions = [{"text": s, "prompt": s} for s in simple_suggestions]

    # Step 10: Track entities for context memory
    chat_memory.track_entities(
        user_id=user_id,
        product_ids=entities.get("product_ids"),
        search_query=entities.get("search_query"),
        category=entities.get("category"),
        region=entities.get("region"),
        intent=intent.value
    )

    # Step 11: Store messages in memory + DB
    chat_memory.add_message(user_id=user_id, role="user", content=message, intent=intent.value)
    chat_memory.add_message(user_id=user_id, role="assistant", content=response, data=chart_data, intent=intent.value)
    _db_save_message(user_id, "user", message, intent=intent.value)
    _db_save_message(user_id, "assistant", response, intent=intent.value, data=chart_data)

    # Step 12: Get product images if applicable
    product_images = get_product_images(intent, entities)

    # Step 13: Build response
    result = {
        "reply": response,
        "response_type": "text",  # LLM text response (vs "structured" for Decision Assistant)
        "intent": intent.value,
        "entities": entities,
        "suggested_questions": suggestions,  # Match structured response field name
    }

    if chart_data:
        result["data"] = chart_data

    if product_images:
        result["images"] = product_images

    return result


def get_chat_history(user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get chat history for user — reads from DB (persistent across restarts).
    Falls back to in-memory if DB unavailable.
    """
    db_history = _db_load_history(user_id, limit=limit or 100)
    if db_history:
        return db_history
    return chat_memory.get_history(user_id, limit=limit)


def clear_chat_history(user_id: int) -> Dict[str, Any]:
    """
    Clear chat history for user — clears both DB and in-memory.
    """
    db_count = _db_clear_history(user_id)
    mem_count = chat_memory.clear_history(user_id)
    return {
        "message": "History cleared",
        "cleared_messages": max(db_count, mem_count),
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


class AIChatService:
    """Async wrapper for Telegram bot (python-telegram-bot) and similar callers."""

    async def process_message(
        self,
        message: str,
        user_id: Union[str, int],
        language: str = "kk",
        model_type: str = "random_forest",
    ) -> Dict[str, Any]:
        uid = int(user_id) if not isinstance(user_id, int) else user_id
        return await asyncio.to_thread(
            handle_ai_chat, message, uid, language, model_type
        )
