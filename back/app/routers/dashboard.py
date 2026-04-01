"""
Enhanced Dashboard API Endpoints
Executive dashboard, forecast explorer, data operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

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
# EXECUTIVE DASHBOARD
# =============================================================================

@router.get("/executive", response_model=ExecutiveDashboard)
async def get_executive_dashboard(current_user=Depends(get_admin_user)):
    """
    Get executive dashboard with key metrics, risks, and AI insights.
    Admin only.
    """
    # In production, these would come from actual data analysis
    # For now, returning structured mock data that demonstrates the schema

    metrics = [
        DashboardMetric(
            id="total_products",
            label="Products Monitored",
            value=20,
            icon="package",
            trend="stable"
        ),
        DashboardMetric(
            id="high_risk",
            label="High Risk Products",
            value=3,
            icon="alert-triangle",
            trend="up",
            is_positive=False,
            change=15,
            change_period="vs last week"
        ),
        DashboardMetric(
            id="stockout_risk",
            label="Stockout Risk",
            value=5,
            icon="package-x",
            trend="up",
            is_positive=False,
            change=25
        ),
        DashboardMetric(
            id="growing_categories",
            label="Growing Categories",
            value=2,
            icon="trending-up",
            trend="stable",
            is_positive=True
        ),
        DashboardMetric(
            id="forecast_accuracy",
            label="Forecast Accuracy",
            value="78%",
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

    high_risk_products = [
        RiskProduct(
            product_id="P0003",
            name="Electronics Item A",
            category="Electronics",
            risk_type=AlertType.STOCKOUT_RISK,
            risk_score=0.85,
            risk_level=AlertSeverity.CRITICAL,
            current_inventory=45,
            predicted_demand_7d=120,
            days_until_stockout=3,
            recommended_action="Order 200 units immediately"
        ),
        RiskProduct(
            product_id="P0007",
            name="Furniture Item B",
            category="Furniture",
            risk_type=AlertType.DEMAND_DROP,
            risk_score=0.72,
            risk_level=AlertSeverity.WARNING,
            current_inventory=200,
            predicted_demand_7d=50,
            days_until_stockout=28,
            recommended_action="Review pricing strategy"
        ),
        RiskProduct(
            product_id="P0015",
            name="Clothing Item C",
            category="Clothing",
            risk_type=AlertType.FORECAST_UNSTABLE,
            risk_score=0.65,
            risk_level=AlertSeverity.WARNING,
            current_inventory=80,
            predicted_demand_7d=95,
            days_until_stockout=6,
            recommended_action="Monitor closely, prepare reorder"
        )
    ]

    category_insights = [
        CategoryInsight(
            category="Electronics",
            total_products=5,
            avg_demand=85.5,
            trend="growing",
            change_percent=12.3,
            top_product="P0003",
            alert_count=1
        ),
        CategoryInsight(
            category="Groceries",
            total_products=4,
            avg_demand=120.2,
            trend="stable",
            change_percent=2.1,
            top_product="P0001",
            alert_count=0
        ),
        CategoryInsight(
            category="Furniture",
            total_products=3,
            avg_demand=45.0,
            trend="declining",
            change_percent=-8.5,
            top_product="P0012",
            alert_count=2
        ),
        CategoryInsight(
            category="Toys",
            total_products=4,
            avg_demand=65.8,
            trend="growing",
            change_percent=18.2,
            top_product="P0008",
            alert_count=0
        ),
        CategoryInsight(
            category="Clothing",
            total_products=4,
            avg_demand=55.3,
            trend="stable",
            change_percent=-1.5,
            top_product="P0015",
            alert_count=1
        )
    ]

    ai_insights = [
        AIInsight(
            id="ins_001",
            title="Electronics Surge Expected",
            description="Electronics category showing 15% week-over-week growth. Recommend increasing stock levels for P0003 and P0005.",
            category="opportunity",
            severity=AlertSeverity.INFO,
            affected_items=["P0003", "P0005", "Electronics"],
            generated_at=datetime.utcnow(),
            action_query="Show forecast for Electronics category"
        ),
        AIInsight(
            id="ins_002",
            title="North Region Demand Drop",
            description="North region showing unusual 12% demand decline across Furniture category. May indicate seasonal shift or competition.",
            category="anomaly",
            severity=AlertSeverity.WARNING,
            affected_items=["Furniture", "North"],
            generated_at=datetime.utcnow(),
            action_query="Analyze North region Furniture demand"
        ),
        AIInsight(
            id="ins_003",
            title="3 Products Need Replenishment",
            description="Based on current inventory and forecasted demand, 3 products may face stockout within 7 days.",
            category="risk",
            severity=AlertSeverity.CRITICAL,
            affected_items=["P0003", "P0008", "P0015"],
            generated_at=datetime.utcnow(),
            action_query="Show products needing replenishment"
        ),
        AIInsight(
            id="ins_004",
            title="Toys Category Seasonal Peak",
            description="Historical data suggests Toys category entering seasonal peak. Consider promotional inventory boost.",
            category="trend",
            severity=AlertSeverity.INFO,
            affected_items=["Toys", "P0008", "P0009"],
            generated_at=datetime.utcnow(),
            action_query="Show Toys category forecast"
        )
    ]

    active_alerts = [
        Alert(
            id="alert_001",
            type=AlertType.STOCKOUT_RISK,
            severity=AlertSeverity.CRITICAL,
            title="Critical: P0003 Stockout Risk",
            message="Current inventory (45) insufficient for forecasted demand (120) over next 7 days",
            product_id="P0003",
            product_name="Electronics Item A",
            recommended_action="Order immediately"
        ),
        Alert(
            id="alert_002",
            type=AlertType.DEMAND_DROP,
            severity=AlertSeverity.WARNING,
            title="Furniture Demand Declining",
            message="Furniture category demand dropped 8.5% this week",
            category="Furniture",
            recommended_action="Review pricing strategy"
        )
    ]

    return ExecutiveDashboard(
        metrics=metrics,
        high_risk_products=high_risk_products,
        total_risk_count=len(high_risk_products),
        category_insights=category_insights,
        ai_insights=ai_insights,
        active_alerts=active_alerts,
        last_updated=datetime.utcnow(),
        data_freshness="2 hours ago"
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

    sample_forecast = EnhancedForecastResponse(
        product_id="P0001",
        product_name="Sample Product",
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
    return DataOperationsStatus(
        total_rows=6200000,
        total_products=20,
        total_stores=5,
        date_range={"from": "2022-01-01", "to": "2024-12-31"},
        last_upload=datetime.utcnow() - timedelta(days=3),
        models_cached=5,
        last_training=datetime.utcnow() - timedelta(hours=6),
        model_version="1.0",
        missing_values_percent=0.02,
        data_freshness_days=3,
        quality_score=95.5,
        quality_issues=["Some missing competitor pricing data for Q3 2024"],
        can_retrain=True,
        can_upload=True
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
    alerts = [
        Alert(
            id="alert_001",
            type=AlertType.STOCKOUT_RISK,
            severity=AlertSeverity.CRITICAL,
            title="Critical: P0003 Stockout Risk",
            message="Current inventory (45) insufficient for forecasted demand (120) over next 7 days",
            product_id="P0003",
            product_name="Electronics Item A",
            category="Electronics",
            metric_value=45,
            threshold=120,
            recommended_action="Order 200 units immediately"
        ),
        Alert(
            id="alert_002",
            type=AlertType.DEMAND_DROP,
            severity=AlertSeverity.WARNING,
            title="Furniture Demand Declining",
            message="Furniture category demand dropped 8.5% this week",
            category="Furniture",
            region="North",
            recommended_action="Review pricing strategy"
        ),
        Alert(
            id="alert_003",
            type=AlertType.FORECAST_UNSTABLE,
            severity=AlertSeverity.WARNING,
            title="Unstable Forecast: P0015",
            message="High variance in recent demand makes forecast less reliable",
            product_id="P0015",
            product_name="Clothing Item C",
            recommended_action="Monitor closely, consider safety stock"
        ),
        Alert(
            id="alert_004",
            type=AlertType.DEMAND_SPIKE,
            severity=AlertSeverity.INFO,
            title="Demand Spike: Toys Category",
            message="Toys category showing 18% increase, likely seasonal",
            category="Toys",
            recommended_action="Ensure adequate inventory"
        )
    ]

    # Apply filters
    if severity:
        alerts = [a for a in alerts if a.severity.value == severity]

    if alert_type:
        alerts = [a for a in alerts if a.type.value == alert_type]

    return alerts[:limit]