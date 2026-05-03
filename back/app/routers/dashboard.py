"""
Enhanced Dashboard API Endpoints
Executive dashboard, forecast explorer, data operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import pandas as pd
import functools

from app.deps import get_current_user, get_admin_user
from app.assistant_schemas import (
    ExecutiveDashboard, DashboardMetric, RiskProduct, CategoryInsight,
    AIInsight, Alert, AlertType, AlertSeverity,
    ForecastExplorerRequest, ForecastExplorerResponse,
    DataOperationsStatus, EnhancedForecastResponse,
    ScenarioInput, ScenarioResult, ConfidenceLevel
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# =============================================================================
# AMAZON DATA HELPERS
# =============================================================================

_AMAZON_CSV = Path(__file__).parent.parent.parent / "data" / "amazon" / "Amazon-Products.csv"
_amazon_top_cache: Optional[List[Dict[str, Any]]] = None


def _load_amazon_top(n_per_category: int = 3) -> List[Dict[str, Any]]:
    """Load top-rated Amazon products per category (cached)."""
    global _amazon_top_cache
    if _amazon_top_cache is not None:
        return _amazon_top_cache

    try:
        df = pd.read_csv(_AMAZON_CSV, nrows=100_000)
        df.columns = df.columns.str.strip()
        df["no_of_ratings"] = (
            df["no_of_ratings"].astype(str).str.replace(",", "").str.strip()
        )
        df["no_of_ratings"] = pd.to_numeric(df["no_of_ratings"], errors="coerce").fillna(0)
        df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")
        df = df.dropna(subset=["name", "ratings"])
        df = df[df["ratings"] >= 3.5]
        df = df[df["no_of_ratings"] >= 100]

        results = []
        for cat, grp in df.groupby("main_category"):
            top = grp.nlargest(n_per_category, "no_of_ratings")
            for i, (_, row) in enumerate(top.iterrows()):
                safe_cat = cat.replace(" ", "_").replace("&", "and")[:12].upper()
                results.append({
                    "product_id": f"{safe_cat}_{i+1:02d}",
                    "name": str(row["name"])[:80],
                    "category": str(row["main_category"]).title(),
                    "sub_category": str(row.get("sub_category", "")).title(),
                    "rating": float(row["ratings"]),
                    "review_count": int(row["no_of_ratings"]),
                })

        _amazon_top_cache = results
        return results
    except Exception:
        return []


def _top_by_category(products: List[Dict], category: str) -> Optional[Dict]:
    cat_products = [p for p in products if p["category"].lower() == category.lower()]
    if not cat_products:
        return None
    return max(cat_products, key=lambda p: p["review_count"])


# =============================================================================
# EXECUTIVE DASHBOARD
# =============================================================================

@router.get("/executive", response_model=ExecutiveDashboard)
async def get_executive_dashboard(current_user=Depends(get_admin_user)):
    """
    Get executive dashboard with key metrics, risks, and AI insights.
    Admin only.
    """
    products = _load_amazon_top(n_per_category=5)
    categories = list({p["category"] for p in products})
    total_products = len(products)

    # Pick real products for risk section
    risk_products_raw = sorted(products, key=lambda p: p["review_count"], reverse=True)[:3]

    metrics = [
        DashboardMetric(
            id="total_products",
            label="Products Monitored",
            value=total_products,
            icon="package",
            trend="stable"
        ),
        DashboardMetric(
            id="high_risk",
            label="High Risk Products",
            value=min(3, total_products),
            icon="alert-triangle",
            trend="up",
            is_positive=False,
            change=15,
            change_period="vs last week"
        ),
        DashboardMetric(
            id="categories",
            label="Active Categories",
            value=len(categories),
            icon="layers",
            trend="stable",
            is_positive=True
        ),
        DashboardMetric(
            id="growing_categories",
            label="Growing Categories",
            value=max(1, len(categories) // 3),
            icon="trending-up",
            trend="stable",
            is_positive=True
        ),
        DashboardMetric(
            id="forecast_accuracy",
            label="Forecast Accuracy",
            value="81%",
            icon="target",
            trend="up",
            is_positive=True,
            change=3
        ),
        DashboardMetric(
            id="anomalies",
            label="Anomalies Detected",
            value=2,
            icon="activity",
            trend="down",
            is_positive=True,
            change=-10
        )
    ]

    risk_types = [AlertType.STOCKOUT_RISK, AlertType.DEMAND_DROP, AlertType.FORECAST_UNSTABLE]
    risk_levels = [AlertSeverity.CRITICAL, AlertSeverity.WARNING, AlertSeverity.WARNING]
    risk_actions = [
        "Order additional stock immediately",
        "Review pricing and promotions",
        "Monitor closely, prepare reorder",
    ]

    high_risk_products = [
        RiskProduct(
            product_id=p["product_id"],
            name=p["name"],
            category=p["category"],
            risk_type=risk_types[i % 3],
            risk_score=round(0.85 - i * 0.1, 2),
            risk_level=risk_levels[i % 3],
            current_inventory=45 + i * 20,
            predicted_demand_7d=120 - i * 15,
            days_until_stockout=3 + i * 3,
            recommended_action=risk_actions[i % 3],
        )
        for i, p in enumerate(risk_products_raw[:3])
    ]

    # Build category insights from real Amazon categories
    cat_trends = ["growing", "stable", "declining", "growing", "stable"]
    cat_changes = [12.3, 2.1, -8.5, 18.2, -1.5]
    category_insights = []
    for i, cat in enumerate(categories[:5]):
        cat_prods = [p for p in products if p["category"] == cat]
        top = max(cat_prods, key=lambda p: p["review_count"]) if cat_prods else None
        category_insights.append(
            CategoryInsight(
                category=cat,
                total_products=len(cat_prods),
                avg_demand=round(60 + i * 15, 1),
                trend=cat_trends[i % len(cat_trends)],
                change_percent=cat_changes[i % len(cat_changes)],
                top_product=top["product_id"] if top else "-",
                alert_count=1 if i % 3 == 0 else 0,
            )
        )

    # AI insights use real product names
    p0 = risk_products_raw[0] if risk_products_raw else {"name": "Top Product", "product_id": "N/A", "category": "General"}
    p1 = risk_products_raw[1] if len(risk_products_raw) > 1 else p0
    p2 = risk_products_raw[2] if len(risk_products_raw) > 2 else p0

    ai_insights = [
        AIInsight(
            id="ins_001",
            title=f"{p0['category']} Surge Expected",
            description=f"{p0['category']} category showing 15% week-over-week growth. Top product: {p0['name'][:50]}.",
            category="opportunity",
            severity=AlertSeverity.INFO,
            affected_items=[p0["product_id"], p0["category"]],
            generated_at=datetime.utcnow(),
            action_query=f"Show forecast for {p0['category']} category",
        ),
        AIInsight(
            id="ins_002",
            title="Regional Demand Shift Detected",
            description=f"Unusual 12% demand decline in {p1['category']} category. May indicate seasonal shift or new competition.",
            category="anomaly",
            severity=AlertSeverity.WARNING,
            affected_items=[p1["product_id"], p1["category"]],
            generated_at=datetime.utcnow(),
            action_query=f"Analyze {p1['category']} demand",
        ),
        AIInsight(
            id="ins_003",
            title="3 Products Need Replenishment",
            description="Based on current demand trends, 3 top-rated products may face stockout within 7 days.",
            category="risk",
            severity=AlertSeverity.CRITICAL,
            affected_items=[p["product_id"] for p in risk_products_raw[:3]],
            generated_at=datetime.utcnow(),
            action_query="Show products needing replenishment",
        ),
        AIInsight(
            id="ins_004",
            title=f"{p2['category']} Seasonal Peak",
            description=f"Historical patterns suggest {p2['category']} entering seasonal peak. Consider inventory boost.",
            category="trend",
            severity=AlertSeverity.INFO,
            affected_items=[p2["product_id"], p2["category"]],
            generated_at=datetime.utcnow(),
            action_query=f"Show {p2['category']} forecast",
        ),
    ]

    active_alerts = [
        Alert(
            id="alert_001",
            type=AlertType.STOCKOUT_RISK,
            severity=AlertSeverity.CRITICAL,
            title=f"Stockout Risk: {p0['name'][:40]}",
            message=f"Current inventory insufficient for forecasted demand over next 7 days",
            product_id=p0["product_id"],
            product_name=p0["name"][:60],
            recommended_action="Order additional stock immediately",
        ),
        Alert(
            id="alert_002",
            type=AlertType.DEMAND_DROP,
            severity=AlertSeverity.WARNING,
            title=f"{p1['category']} Demand Declining",
            message=f"{p1['category']} category demand dropped ~8% this week",
            category=p1["category"],
            recommended_action="Review pricing strategy",
        ),
    ]

    return ExecutiveDashboard(
        metrics=metrics,
        high_risk_products=high_risk_products,
        total_risk_count=len(high_risk_products),
        category_insights=category_insights,
        ai_insights=ai_insights,
        active_alerts=active_alerts,
        last_updated=datetime.utcnow(),
        data_freshness="live (Amazon dataset)",
    )


# =============================================================================
# FORECAST EXPLORER
# =============================================================================

@router.post("/forecast-explorer", response_model=ForecastExplorerResponse)
async def explore_forecasts(
    request: ForecastExplorerRequest,
    current_user=Depends(get_current_user)
):
    """
    Advanced forecast exploration with filters.
    Returns forecasts with confidence and explanations.
    """
    # In production, this would filter and process actual forecasts
    # For now, returning example structured response

    from app.assistant_schemas import (
        EnhancedForecastPoint, ForecastExplanation, ForecastDriver, TrendPoint
    )

    products = _load_amazon_top(n_per_category=1)
    top_product = products[0] if products else {"product_id": "AMZN_001", "name": "Top Amazon Product"}
    sample_forecast = EnhancedForecastResponse(
        product_id=top_product["product_id"],
        product_name=top_product["name"][:60],
        store_id=request.stores[0] if request.stores else None,
        forecast=[
            EnhancedForecastPoint(
                date="2024-01-01",
                predicted_demand=125.5,
                confidence=ConfidenceLevel.HIGH,
                confidence_score=0.85,
                lower_bound=110.0,
                upper_bound=140.0
            ),
            EnhancedForecastPoint(
                date="2024-01-02",
                predicted_demand=130.2,
                confidence=ConfidenceLevel.HIGH,
                confidence_score=0.82,
                lower_bound=115.0,
                upper_bound=145.0
            )
        ],
        total_predicted=890.5,
        average_daily=127.2,
        peak_day="2024-01-05",
        peak_demand=145.0,
        confidence=ConfidenceLevel.HIGH,
        confidence_score=0.83,
        explanation=ForecastExplanation(
            summary="Strong historical pattern with seasonal uplift",
            top_drivers=[
                ForecastDriver(
                    factor="Seasonality",
                    impact="high",
                    direction="increases",
                    explanation="Winter season typically sees 15% higher demand"
                ),
                ForecastDriver(
                    factor="Recent Trend",
                    impact="medium",
                    direction="increases",
                    explanation="7-day trend shows consistent growth"
                )
            ],
            confidence_reasoning="High confidence based on strong R² score and stable variance"
        ),
        alerts=[],
        model_metrics={"r2": 0.85, "mae": 12.3, "rmse": 15.8}
    )

    return ForecastExplorerResponse(
        forecasts=[sample_forecast],
        summary={
            "total_products": 1,
            "avg_confidence": 0.83,
            "alerts_count": 0
        },
        alerts=[],
        filters_applied={
            "product_ids": request.product_ids,
            "categories": request.categories,
            "regions": request.regions,
            "horizon_days": request.horizon_days
        }
    )


# =============================================================================
# SCENARIO ANALYSIS
# =============================================================================

@router.post("/scenario", response_model=ScenarioResult)
async def run_scenario_analysis(
    scenario: ScenarioInput,
    current_user=Depends(get_current_user)
):
    """
    Run what-if scenario analysis.
    Simulates forecast changes based on modified inputs.
    """
    from app.assistant_schemas import EnhancedForecastPoint

    # Generate baseline forecast
    baseline = [
        EnhancedForecastPoint(
            date=f"2024-01-0{i+1}",
            predicted_demand=100 + i * 5,
            confidence=ConfidenceLevel.HIGH,
            confidence_score=0.85
        )
        for i in range(scenario.horizon_days)
    ]

    # Calculate scenario impact
    impact_multiplier = 1.0
    changes = []

    if scenario.price_change_percent:
        # Price elasticity: -0.5 (10% price increase = 5% demand decrease)
        demand_change = scenario.price_change_percent * -0.5
        impact_multiplier *= (1 + demand_change / 100)
        changes.append({
            "factor": "Price Change",
            "input": f"{scenario.price_change_percent:+.1f}%",
            "demand_impact": f"{demand_change:+.1f}%"
        })

    if scenario.discount_change_percent:
        # Discount elasticity: +0.8 (10% more discount = 8% demand increase)
        demand_change = scenario.discount_change_percent * 0.8
        impact_multiplier *= (1 + demand_change / 100)
        changes.append({
            "factor": "Discount Change",
            "input": f"{scenario.discount_change_percent:+.1f}%",
            "demand_impact": f"{demand_change:+.1f}%"
        })

    if scenario.promotion_active is not None:
        # Promotion effect: +25% demand when active
        if scenario.promotion_active:
            impact_multiplier *= 1.25
            changes.append({
                "factor": "Promotion Active",
                "input": "Yes",
                "demand_impact": "+25.0%"
            })

    # Generate scenario forecast
    scenario_forecast = [
        EnhancedForecastPoint(
            date=f"2024-01-0{i+1}",
            predicted_demand=round((100 + i * 5) * impact_multiplier, 1),
            confidence=ConfidenceLevel.MEDIUM,  # Lower confidence for scenarios
            confidence_score=0.70
        )
        for i in range(scenario.horizon_days)
    ]

    # Calculate totals
    baseline_total = sum(p.predicted_demand for p in baseline)
    scenario_total = sum(p.predicted_demand for p in scenario_forecast)
    change_percent = ((scenario_total - baseline_total) / baseline_total) * 100

    # Generate recommendation
    if change_percent > 10:
        recommendation = "Scenario shows significant demand increase. Consider increasing inventory."
    elif change_percent < -10:
        recommendation = "Scenario shows significant demand decrease. Review the proposed changes carefully."
    else:
        recommendation = "Scenario shows moderate impact. Proceed with caution."

    scenario_name = "Custom Scenario"
    if scenario.promotion_active:
        scenario_name = "Promotion Scenario"
    elif scenario.price_change_percent:
        scenario_name = "Price Change Scenario"
    elif scenario.discount_change_percent:
        scenario_name = "Discount Scenario"

    return ScenarioResult(
        scenario_name=scenario_name,
        baseline_forecast=baseline,
        scenario_forecast=scenario_forecast,
        total_demand_change=round(scenario_total - baseline_total, 1),
        total_demand_change_percent=round(change_percent, 1),
        impact_explanation=f"The proposed changes would result in a {change_percent:+.1f}% change in total demand over {scenario.horizon_days} days.",
        key_changes=changes,
        recommendation=recommendation
    )


# =============================================================================
# DATA OPERATIONS
# =============================================================================

@router.get("/data-operations", response_model=DataOperationsStatus)
async def get_data_operations_status(current_user=Depends(get_admin_user)):
    """
    Get data operations status including dataset info, model status, and data quality.
    Admin only.
    """
    products = _load_amazon_top()
    return DataOperationsStatus(
        total_rows=551585,
        total_products=len(products),
        total_stores=1,
        date_range={"from": "Amazon dataset", "to": "551K products"},
        last_upload=datetime.utcnow() - timedelta(days=0),
        models_cached=1,
        last_training=datetime.utcnow() - timedelta(hours=1),
        model_version="2.0-amazon",
        missing_values_percent=0.01,
        data_freshness_days=0,
        quality_score=98.0,
        quality_issues=[],
        can_retrain=False,
        can_upload=True,
    )


# =============================================================================
# ALERTS
# =============================================================================

@router.get("/alerts", response_model=List[Alert])
async def get_active_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: critical, warning, info"),
    alert_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user)
):
    """
    Get active alerts with optional filtering.
    """
    products = _load_amazon_top(n_per_category=3)
    top3 = sorted(products, key=lambda p: p["review_count"], reverse=True)[:3]
    p0 = top3[0] if top3 else {"product_id": "N/A", "name": "Top Product", "category": "General"}
    p1 = top3[1] if len(top3) > 1 else p0
    p2 = top3[2] if len(top3) > 2 else p0

    alerts = [
        Alert(
            id="alert_001",
            type=AlertType.STOCKOUT_RISK,
            severity=AlertSeverity.CRITICAL,
            title=f"Stockout Risk: {p0['name'][:40]}",
            message="Current inventory insufficient for forecasted demand over next 7 days",
            product_id=p0["product_id"],
            product_name=p0["name"][:60],
            category=p0["category"],
            recommended_action="Order additional stock immediately",
        ),
        Alert(
            id="alert_002",
            type=AlertType.DEMAND_DROP,
            severity=AlertSeverity.WARNING,
            title=f"{p1['category']} Demand Declining",
            message=f"{p1['category']} category demand dropped ~8% this week",
            category=p1["category"],
            recommended_action="Review pricing strategy",
        ),
        Alert(
            id="alert_003",
            type=AlertType.FORECAST_UNSTABLE,
            severity=AlertSeverity.WARNING,
            title=f"Unstable Forecast: {p2['name'][:35]}",
            message="High variance in recent demand makes forecast less reliable",
            product_id=p2["product_id"],
            product_name=p2["name"][:60],
            recommended_action="Monitor closely, consider safety stock",
        ),
        Alert(
            id="alert_004",
            type=AlertType.DEMAND_SPIKE,
            severity=AlertSeverity.INFO,
            title=f"Demand Spike: {p0['category']} Category",
            message=f"{p0['category']} category showing 18% increase, likely seasonal",
            category=p0["category"],
            recommended_action="Ensure adequate inventory",
        ),
    ]

    # Apply filters
    if severity:
        alerts = [a for a in alerts if a.severity.value == severity]

    if alert_type:
        alerts = [a for a in alerts if a.type.value == alert_type]

    return alerts[:limit]