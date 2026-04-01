"""
Enhanced Assistant Service
Transforms chat into an action-oriented assistant
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import pandas as pd

from app.assistant_schemas import (
    AssistantResponse, ResponseBlock, ResponseBlockType,
    MetricItem, RankedItem, ComparisonRow, ChartData, TrendPoint,
    SuggestedAction, Alert, AlertType, AlertSeverity,
    ConfidenceLevel, ForecastDriver, ForecastExplanation,
    EnhancedForecastPoint, EnhancedForecastResponse,
    DashboardMetric, RiskProduct, CategoryInsight, AIInsight,
    ExecutiveDashboard, DataOperationsStatus
)


class EnhancedAssistantService:
    """
    Enhanced assistant that provides structured, actionable responses
    """

    def __init__(self, data_service, model_service, amazon_service):
        self.data_service = data_service
        self.model_service = model_service
        self.amazon_service = amazon_service

    # =========================================================================
    # MAIN RESPONSE BUILDER
    # =========================================================================

    def build_response(
        self,
        intent: str,
        entities: Dict[str, Any],
        raw_reply: str,
        context_data: Dict[str, Any]
    ) -> AssistantResponse:
        """
        Build structured response based on intent and data
        """
        blocks = []
        chart_data = None
        alerts = []
        products = None
        confidence = None

        # Route to specific handlers based on intent
        if intent == "TOP_PRODUCTS" or intent == "LOW_PERFORMERS":
            blocks, products = self._build_ranked_list_response(intent, entities, context_data)

        elif intent == "RISKY_PRODUCTS" or "risk" in raw_reply.lower():
            blocks, alerts = self._build_risk_response(entities, context_data)

        elif intent == "COMPARISON":
            blocks, chart_data = self._build_comparison_response(entities, context_data)

        elif intent == "FORECAST" or intent == "SMART_FORECAST":
            blocks, chart_data, confidence = self._build_forecast_response(entities, context_data)

        elif intent == "TRENDS" or intent == "REGION_STATS" or intent == "CATEGORY_STATS":
            blocks, chart_data = self._build_trend_response(intent, entities, context_data)

        elif intent == "FORECAST_CHANGE" or "why" in raw_reply.lower():
            blocks = self._build_explanation_response(entities, context_data)

        elif intent == "REPLENISHMENT":
            blocks, alerts = self._build_replenishment_response(entities, context_data)

        else:
            # Default: add summary block
            blocks.append(ResponseBlock(
                type=ResponseBlockType.SUMMARY,
                content=raw_reply,
                priority=1
            ))

        # Generate suggested actions based on intent and context
        suggested_actions = self._generate_suggested_actions(intent, entities, context_data)

        return AssistantResponse(
            reply=raw_reply,
            intent=intent,
            blocks=blocks,
            chart_data=chart_data,
            products=products,
            alerts=alerts if alerts else None,
            suggested_actions=suggested_actions,
            entities=entities,
            confidence=confidence
        )

    # =========================================================================
    # RESPONSE BUILDERS BY TYPE
    # =========================================================================

    def _build_ranked_list_response(
        self,
        intent: str,
        entities: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Tuple[List[ResponseBlock], List[Dict]]:
        """Build ranked list response for top/low performers"""
        blocks = []
        products = []

        # Get data from context
        items = context_data.get("ranked_items", [])

        if not items:
            return blocks, products

        # Build ranked items
        ranked_items = []
        for i, item in enumerate(items[:10], 1):
            ranked_items.append(RankedItem(
                rank=i,
                product_id=item.get("product_id"),
                name=item.get("name", f"Product {i}"),
                value=item.get("value", 0),
                metric_label=item.get("metric", "demand"),
                risk_level=self._calculate_risk_level(item),
                trend=item.get("trend", "stable"),
                details=item.get("details")
            ))
            products.append(item)

        # Add ranked list block
        blocks.append(ResponseBlock(
            type=ResponseBlockType.RANKED_LIST,
            title="Top Products" if intent == "TOP_PRODUCTS" else "Attention Needed",
            content=[item.model_dump() for item in ranked_items],
            priority=1
        ))

        # Add summary metrics
        if items:
            avg_value = sum(item.get("value", 0) for item in items) / len(items)
            blocks.append(ResponseBlock(
                type=ResponseBlockType.METRICS,
                title="Summary",
                content=[
                    MetricItem(label="Total Items", value=len(items)).model_dump(),
                    MetricItem(label="Average", value=round(avg_value, 2)).model_dump()
                ],
                priority=2
            ))

        return blocks, products

    def _build_risk_response(
        self,
        entities: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Tuple[List[ResponseBlock], List[Alert]]:
        """Build risk analysis response"""
        blocks = []
        alerts = []

        # Generate alerts from context
        risk_items = context_data.get("risk_items", [])

        for item in risk_items[:5]:
            alert = Alert(
                id=str(uuid.uuid4())[:8],
                type=AlertType.STOCKOUT_RISK if item.get("risk_type") == "stockout" else AlertType.DEMAND_DROP,
                severity=AlertSeverity.WARNING if item.get("risk_score", 0.5) > 0.7 else AlertSeverity.INFO,
                title=f"Risk: {item.get('name', 'Unknown')}",
                message=item.get("message", "Potential risk detected"),
                product_id=item.get("product_id"),
                product_name=item.get("name"),
                metric_value=item.get("value"),
                recommended_action=item.get("action", "Review inventory levels")
            )
            alerts.append(alert)

        # Add alerts block
        if alerts:
            blocks.append(ResponseBlock(
                type=ResponseBlockType.ALERT,
                title="Risk Alerts",
                content=[a.model_dump() for a in alerts],
                priority=1
            ))

        # Add explanation block
        blocks.append(ResponseBlock(
            type=ResponseBlockType.EXPLANATION,
            title="Risk Analysis",
            content={
                "summary": f"Found {len(alerts)} products with elevated risk",
                "factors": [
                    "Low inventory relative to predicted demand",
                    "Declining trend in recent weeks",
                    "Seasonal demand approaching peak"
                ]
            },
            priority=2
        ))

        return blocks, alerts

    def _build_comparison_response(
        self,
        entities: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Tuple[List[ResponseBlock], Optional[ChartData]]:
        """Build comparison response"""
        blocks = []

        product_a = entities.get("product_ids", [None, None])[0] if entities.get("product_ids") else None
        product_b = entities.get("product_ids", [None, None])[1] if len(entities.get("product_ids", [])) > 1 else None

        comparison_data = context_data.get("comparison", {})

        # Build comparison rows
        comparison_rows = []
        dimensions = [
            ("Category", "category"),
            ("Avg Demand", "avg_demand"),
            ("Price", "price"),
            ("Rating", "rating"),
            ("Trend", "trend"),
            ("Forecast (7d)", "forecast_7d"),
            ("Confidence", "confidence")
        ]

        for label, key in dimensions:
            val_a = comparison_data.get("product_a", {}).get(key, "N/A")
            val_b = comparison_data.get("product_b", {}).get(key, "N/A")
            winner = self._determine_winner(key, val_a, val_b)

            comparison_rows.append(ComparisonRow(
                dimension=label,
                value_a=val_a,
                value_b=val_b,
                winner=winner
            ))

        blocks.append(ResponseBlock(
            type=ResponseBlockType.COMPARISON,
            title=f"Comparison: {product_a} vs {product_b}",
            content={
                "product_a": {"id": product_a, **comparison_data.get("product_a", {})},
                "product_b": {"id": product_b, **comparison_data.get("product_b", {})},
                "rows": [row.model_dump() for row in comparison_rows]
            },
            priority=1
        ))

        # Build chart data for visual comparison
        chart_data = ChartData(
            chart_type="comparison",
            title="Demand Comparison",
            data=[
                {"metric": "Avg Demand", product_a: comparison_data.get("product_a", {}).get("avg_demand", 0),
                 product_b: comparison_data.get("product_b", {}).get("avg_demand", 0)},
                {"metric": "Forecast", product_a: comparison_data.get("product_a", {}).get("forecast_7d", 0),
                 product_b: comparison_data.get("product_b", {}).get("forecast_7d", 0)},
            ],
            x_key="metric",
            y_keys=[product_a, product_b] if product_a and product_b else ["value"]
        )

        return blocks, chart_data

    def _build_forecast_response(
        self,
        entities: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Tuple[List[ResponseBlock], Optional[ChartData], ConfidenceLevel]:
        """Build forecast response with explainability"""
        blocks = []

        forecast_data = context_data.get("forecast", {})
        product_id = entities.get("product_id")

        # Calculate confidence
        confidence = self._calculate_confidence(forecast_data)

        # Build metrics block
        metrics = [
            MetricItem(
                label="Total Forecast",
                value=round(forecast_data.get("total", 0), 0),
                unit="units"
            ),
            MetricItem(
                label="Daily Average",
                value=round(forecast_data.get("average", 0), 1),
                unit="units/day"
            ),
            MetricItem(
                label="Confidence",
                value=confidence.value,
                is_good=confidence == ConfidenceLevel.HIGH
            ),
            MetricItem(
                label="Peak Day",
                value=forecast_data.get("peak_day", "N/A")
            )
        ]

        blocks.append(ResponseBlock(
            type=ResponseBlockType.METRICS,
            title="Forecast Summary",
            content=[m.model_dump() for m in metrics],
            priority=1
        ))

        # Build explanation block
        explanation = self._generate_forecast_explanation(forecast_data, entities)
        blocks.append(ResponseBlock(
            type=ResponseBlockType.EXPLANATION,
            title="Why This Forecast?",
            content=explanation.model_dump(),
            priority=2
        ))

        # Build chart data
        history = forecast_data.get("history", [])
        predictions = forecast_data.get("predictions", [])

        chart_points = []
        for h in history[-14:]:  # Last 14 days of history
            chart_points.append({
                "date": h.get("date"),
                "history": h.get("demand"),
                "forecast": None
            })

        for p in predictions:
            chart_points.append({
                "date": p.get("date"),
                "history": None,
                "forecast": p.get("predicted_demand")
            })

        chart_data = ChartData(
            chart_type="line",
            title=f"Demand Forecast: {product_id}",
            data=chart_points,
            x_key="date",
            y_keys=["history", "forecast"],
            colors={"history": "#60a5fa", "forecast": "#34d399"}
        )

        return blocks, chart_data, confidence

    def _build_trend_response(
        self,
        intent: str,
        entities: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Tuple[List[ResponseBlock], Optional[ChartData]]:
        """Build trend analysis response"""
        blocks = []

        trend_data = context_data.get("trends", {})

        # Summary block
        blocks.append(ResponseBlock(
            type=ResponseBlockType.SUMMARY,
            content=trend_data.get("summary", "Trend analysis complete"),
            priority=1
        ))

        # Metrics
        metrics = []
        if "growing" in trend_data:
            metrics.append(MetricItem(
                label="Growing",
                value=len(trend_data["growing"]),
                change_direction="up",
                is_good=True
            ))
        if "declining" in trend_data:
            metrics.append(MetricItem(
                label="Declining",
                value=len(trend_data["declining"]),
                change_direction="down",
                is_good=False
            ))

        if metrics:
            blocks.append(ResponseBlock(
                type=ResponseBlockType.METRICS,
                content=[m.model_dump() for m in metrics],
                priority=2
            ))

        # Chart data
        chart_data = None
        if trend_data.get("chart_points"):
            chart_data = ChartData(
                chart_type="line",
                title="Trend Over Time",
                data=trend_data["chart_points"],
                x_key="date",
                y_keys=["value"]
            )

        return blocks, chart_data

    def _build_explanation_response(
        self,
        entities: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> List[ResponseBlock]:
        """Build forecast change explanation"""
        blocks = []

        explanation_data = context_data.get("explanation", {})

        # Main explanation
        blocks.append(ResponseBlock(
            type=ResponseBlockType.EXPLANATION,
            title="Forecast Change Analysis",
            content={
                "summary": explanation_data.get("summary", "Analyzing forecast changes..."),
                "factors": explanation_data.get("factors", []),
                "trend_analysis": explanation_data.get("trend", "Stable trend detected"),
                "seasonal_impact": explanation_data.get("seasonal", "No significant seasonal effect"),
                "external_factors": explanation_data.get("external", [])
            },
            priority=1
        ))

        # Key drivers
        drivers = explanation_data.get("drivers", [])
        if drivers:
            blocks.append(ResponseBlock(
                type=ResponseBlockType.METRICS,
                title="Key Drivers",
                content=[
                    MetricItem(
                        label=d.get("factor"),
                        value=d.get("impact"),
                        change_direction="up" if d.get("direction") == "increases" else "down"
                    ).model_dump() for d in drivers[:5]
                ],
                priority=2
            ))

        return blocks

    def _build_replenishment_response(
        self,
        entities: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Tuple[List[ResponseBlock], List[Alert]]:
        """Build replenishment needs response"""
        blocks = []
        alerts = []

        replenishment_items = context_data.get("replenishment", [])

        for item in replenishment_items[:10]:
            days_until_stockout = item.get("days_until_stockout", 999)
            severity = AlertSeverity.CRITICAL if days_until_stockout < 3 else (
                AlertSeverity.WARNING if days_until_stockout < 7 else AlertSeverity.INFO
            )

            alert = Alert(
                id=str(uuid.uuid4())[:8],
                type=AlertType.REPLENISHMENT_NEEDED,
                severity=severity,
                title=f"Replenishment: {item.get('name', 'Product')}",
                message=f"Stock may run out in {days_until_stockout} days",
                product_id=item.get("product_id"),
                product_name=item.get("name"),
                metric_value=item.get("current_inventory"),
                recommended_action=f"Order {item.get('recommended_order', 'N/A')} units"
            )
            alerts.append(alert)

        # Summary block
        critical_count = sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL)
        blocks.append(ResponseBlock(
            type=ResponseBlockType.SUMMARY,
            content=f"Found {len(alerts)} products needing replenishment, {critical_count} critical",
            priority=1
        ))

        # Alerts block
        blocks.append(ResponseBlock(
            type=ResponseBlockType.ALERT,
            title="Replenishment Alerts",
            content=[a.model_dump() for a in alerts],
            priority=2
        ))

        return blocks, alerts

    # =========================================================================
    # SUGGESTED ACTIONS
    # =========================================================================

    def _generate_suggested_actions(
        self,
        intent: str,
        entities: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> List[SuggestedAction]:
        """Generate contextual follow-up suggestions"""
        actions = []

        product_id = entities.get("product_id")
        category = entities.get("category")
        region = entities.get("region")

        # Intent-specific suggestions
        if intent == "FORECAST":
            actions.extend([
                SuggestedAction(
                    label="Why this forecast?",
                    query=f"Why did the forecast change for {product_id}?" if product_id else "Explain forecast factors",
                    icon="help-circle",
                    category="insight"
                ),
                SuggestedAction(
                    label="Compare with similar",
                    query=f"Compare {product_id} with top products in same category" if product_id else "Compare top products",
                    icon="git-compare",
                    category="compare"
                ),
                SuggestedAction(
                    label="Check risks",
                    query=f"Any risks for {product_id}?" if product_id else "Show risky products",
                    icon="alert-triangle",
                    category="alert"
                )
            ])

        elif intent == "TOP_PRODUCTS" or intent == "LOW_PERFORMERS":
            actions.extend([
                SuggestedAction(
                    label="Forecast top 3",
                    query="Show forecast for top 3 products",
                    icon="trending-up",
                    category="forecast"
                ),
                SuggestedAction(
                    label="Category breakdown",
                    query="Show performance by category",
                    icon="pie-chart",
                    category="explore"
                ),
                SuggestedAction(
                    label="Regional analysis",
                    query="Compare regions performance",
                    icon="map",
                    category="explore"
                )
            ])

        elif intent == "COMPARISON":
            actions.extend([
                SuggestedAction(
                    label="Forecast both",
                    query="Forecast next 7 days for both products",
                    icon="calendar",
                    category="forecast"
                ),
                SuggestedAction(
                    label="Historical trend",
                    query="Show historical demand trend comparison",
                    icon="activity",
                    category="explore"
                )
            ])

        elif intent == "TRENDS" or intent == "REGION_STATS":
            actions.extend([
                SuggestedAction(
                    label="Risky products here",
                    query=f"Which products are at risk in {region or 'this region'}?",
                    icon="alert-circle",
                    category="alert"
                ),
                SuggestedAction(
                    label="Top performers",
                    query=f"Top products in {region or category or 'this area'}",
                    icon="award",
                    category="explore"
                )
            ])

        # Always add some general suggestions
        if len(actions) < 3:
            actions.extend([
                SuggestedAction(
                    label="Executive summary",
                    query="Give me an executive summary of current state",
                    icon="briefcase",
                    category="insight"
                ),
                SuggestedAction(
                    label="What needs attention?",
                    query="What products need my attention today?",
                    icon="eye",
                    category="alert"
                )
            ])

        return actions[:4]  # Max 4 suggestions

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _calculate_risk_level(self, item: Dict) -> ConfidenceLevel:
        """Calculate risk level from item data"""
        risk_score = item.get("risk_score", 0.5)
        if risk_score > 0.7:
            return ConfidenceLevel.LOW  # Low confidence = high risk
        elif risk_score > 0.4:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.HIGH

    def _calculate_confidence(self, forecast_data: Dict) -> ConfidenceLevel:
        """Calculate forecast confidence"""
        r2 = forecast_data.get("r2", 0.5)
        variance = forecast_data.get("variance", 0.3)

        if r2 > 0.8 and variance < 0.2:
            return ConfidenceLevel.HIGH
        elif r2 > 0.6 and variance < 0.4:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def _determine_winner(self, metric: str, val_a: Any, val_b: Any) -> Optional[str]:
        """Determine winner in comparison"""
        try:
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                if metric in ["price"]:  # Lower is better
                    return "a" if val_a < val_b else "b" if val_b < val_a else "tie"
                else:  # Higher is better
                    return "a" if val_a > val_b else "b" if val_b > val_a else "tie"
        except:
            pass
        return None

    def _generate_forecast_explanation(
        self,
        forecast_data: Dict,
        entities: Dict
    ) -> ForecastExplanation:
        """Generate human-readable forecast explanation"""
        drivers = []

        # Analyze available factors
        if forecast_data.get("promotion_active"):
            drivers.append(ForecastDriver(
                factor="Promotion",
                impact="high",
                direction="increases",
                explanation="Active promotion is boosting expected demand"
            ))

        if forecast_data.get("seasonal_peak"):
            drivers.append(ForecastDriver(
                factor="Seasonality",
                impact="medium",
                direction="increases",
                value=forecast_data.get("season"),
                explanation=f"Seasonal demand peak for {forecast_data.get('season', 'current season')}"
            ))

        trend = forecast_data.get("trend", "stable")
        if trend != "stable":
            drivers.append(ForecastDriver(
                factor="Recent Trend",
                impact="medium",
                direction="increases" if trend == "rising" else "decreases",
                explanation=f"7-day demand trend is {trend}"
            ))

        # Default driver if none found
        if not drivers:
            drivers.append(ForecastDriver(
                factor="Historical Pattern",
                impact="medium",
                direction="stabilizes",
                explanation="Forecast based on historical demand patterns"
            ))

        return ForecastExplanation(
            summary=f"Forecast generated with {forecast_data.get('confidence', 'medium')} confidence",
            top_drivers=drivers,
            seasonal_effect=forecast_data.get("seasonal_note"),
            trend_effect=forecast_data.get("trend_note"),
            promotion_effect="Active promotion increases expected demand" if forecast_data.get("promotion_active") else None,
            region_effect=forecast_data.get("region_note"),
            confidence_reasoning=self._get_confidence_reasoning(forecast_data)
        )

    def _get_confidence_reasoning(self, forecast_data: Dict) -> str:
        """Generate confidence reasoning text"""
        r2 = forecast_data.get("r2", 0.5)
        if r2 > 0.8:
            return "High confidence: Strong historical pattern match and low variance"
        elif r2 > 0.6:
            return "Medium confidence: Reasonable pattern match, some variance in recent data"
        return "Low confidence: Limited historical data or high variance in demand"


# =============================================================================
# DASHBOARD SERVICE
# =============================================================================

class DashboardService:
    """Service for executive dashboard data"""

    def __init__(self, data_service, model_service):
        self.data_service = data_service
        self.model_service = model_service

    def get_executive_dashboard(self) -> ExecutiveDashboard:
        """Generate complete executive dashboard"""

        # Key metrics
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
                is_positive=False
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
                is_positive=True
            )
        ]

        # High risk products (mock data - would come from real analysis)
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
            )
        ]

        # Category insights
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
            )
        ]

        # AI insights
        ai_insights = [
            AIInsight(
                id="ins_001",
                title="Electronics Surge Expected",
                description="Electronics category showing 15% week-over-week growth. Recommend increasing stock levels for P0003 and P0005.",
                category="opportunity",
                severity=AlertSeverity.INFO,
                affected_items=["P0003", "P0005"],
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
            )
        ]

        # Active alerts
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

    def get_data_operations_status(self) -> DataOperationsStatus:
        """Get data operations dashboard status"""
        return DataOperationsStatus(
            total_rows=6200000,
            total_products=20,
            total_stores=5,
            date_range={"from": "2022-01-01", "to": "2024-12-31"},
            last_upload=datetime.utcnow() - timedelta(days=3),
            models_cached=len(self.model_service._model_cache) if hasattr(self.model_service, '_model_cache') else 0,
            last_training=datetime.utcnow() - timedelta(hours=6),
            model_version="1.0",
            missing_values_percent=0.02,
            data_freshness_days=3,
            quality_score=95.5,
            quality_issues=["Some missing competitor pricing data for Q3 2024"],
            can_retrain=True,
            can_upload=True
        )