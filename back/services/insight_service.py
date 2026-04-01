"""
Insight Service - Rule-based generation of actionable insights
"""

from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.insight_schemas import (
    InsightBlock,
    InsightSummary,
    WhyItHappened,
    SecondaryDriver,
    RiskAssessment,
    RiskFactor,
    RiskLevel,
    ActionItem,
    FollowUpQuestion,
    get_risk_level,
)


class InsightGenerator:
    """
    Generates rule-based insights from forecast data and historical patterns.
    """

    def generate_insights(
        self,
        product_id: str,
        predictions: List[Dict],
        historical_data: pd.DataFrame,
        model_metrics: Dict[str, float],
        feature_importances: List[Dict],
        inventory_level: Optional[int] = None,
        category: Optional[str] = None,
    ) -> InsightBlock:
        """
        Generate complete insight block from forecast and historical data.

        Args:
            product_id: Product identifier
            predictions: List of prediction dicts with 'date' and 'predicted_units_sold'
            historical_data: DataFrame with historical sales data
            model_metrics: Dict with 'mae', 'rmse', 'r2'
            feature_importances: List of dicts with 'name' and 'importance'
            inventory_level: Current inventory level (optional)
            category: Product category (optional)

        Returns:
            InsightBlock with all insight components
        """
        # Analyze patterns
        trend = self._analyze_trend(historical_data, predictions)
        seasonality = self._analyze_seasonality(historical_data)
        risk_assessment = self._assess_risk(predictions, inventory_level, trend, model_metrics)

        # Generate components
        summary = self._generate_summary(product_id, predictions, trend, category)
        why_it_happened = self._generate_why(trend, seasonality, feature_importances)
        actions = self._generate_actions(risk_assessment, predictions, inventory_level, trend)
        follow_ups = self._generate_follow_ups(product_id, category, risk_assessment, trend)

        return InsightBlock(
            summary=summary,
            why_it_happened=why_it_happened,
            risk=risk_assessment,
            what_to_do=actions,
            follow_up_questions=follow_ups,
        )

    def _analyze_trend(
        self,
        historical_data: pd.DataFrame,
        predictions: List[Dict],
    ) -> Dict:
        """Analyze trend direction and magnitude"""
        if historical_data.empty or len(predictions) == 0:
            return {
                "direction": "stable",
                "change_percent": 0.0,
                "recent_avg": 0.0,
                "predicted_avg": 0.0,
            }

        # Calculate recent historical average (last 7 days)
        demand_col = "Demand Forecast" if "Demand Forecast" in historical_data.columns else "units_sold"
        recent_data = historical_data.tail(7)[demand_col] if demand_col in historical_data.columns else pd.Series([])
        recent_avg = recent_data.mean() if len(recent_data) > 0 else 0.0

        # Calculate predicted average
        predicted_values = [p.get("predicted_units_sold", 0) for p in predictions]
        predicted_avg = np.mean(predicted_values) if predicted_values else 0.0

        # Calculate change
        if recent_avg > 0:
            change_percent = ((predicted_avg - recent_avg) / recent_avg) * 100
        else:
            change_percent = 0.0

        # Determine direction
        if change_percent > 10:
            direction = "increasing"
        elif change_percent < -10:
            direction = "decreasing"
        else:
            direction = "stable"

        return {
            "direction": direction,
            "change_percent": round(change_percent, 1),
            "recent_avg": round(recent_avg, 1),
            "predicted_avg": round(predicted_avg, 1),
        }

    def _analyze_seasonality(self, historical_data: pd.DataFrame) -> Dict:
        """Analyze seasonality patterns in historical data"""
        if historical_data.empty:
            return {"detected": False, "pattern": None}

        date_col = "Date" if "Date" in historical_data.columns else None
        if date_col is None:
            return {"detected": False, "pattern": None}

        try:
            df = historical_data.copy()
            df[date_col] = pd.to_datetime(df[date_col])

            demand_col = "Demand Forecast" if "Demand Forecast" in df.columns else "units_sold"
            if demand_col not in df.columns:
                return {"detected": False, "pattern": None}

            df["day_of_week"] = df[date_col].dt.dayofweek
            df["month"] = df[date_col].dt.month

            # Check for weekly pattern
            daily_avg = df.groupby("day_of_week")[demand_col].mean()
            if daily_avg.max() > 0:
                daily_cv = daily_avg.std() / daily_avg.mean()

                if daily_cv > 0.2:
                    peak_day = daily_avg.idxmax()
                    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    return {
                        "detected": True,
                        "pattern": "weekly",
                        "peak_day": day_names[peak_day],
                        "variation": round(daily_cv, 2),
                    }

            return {"detected": False, "pattern": None}
        except Exception:
            return {"detected": False, "pattern": None}

    def _assess_risk(
        self,
        predictions: List[Dict],
        inventory_level: Optional[int],
        trend: Dict,
        model_metrics: Dict[str, float],
    ) -> RiskAssessment:
        """Assess risk level based on multiple factors"""
        risk_factors = []
        risk_score = 0.0

        # Calculate total predicted demand
        total_demand = sum(p.get("predicted_units_sold", 0) for p in predictions)
        horizon_days = len(predictions)

        # Risk 1: Stockout risk
        if inventory_level is not None and total_demand > 0:
            coverage_days = inventory_level / (total_demand / max(horizon_days, 1))

            if coverage_days < 3:
                risk_factors.append(RiskFactor(
                    factor="Stockout Risk",
                    severity=RiskLevel.HIGH,
                    description=f"Current inventory covers only {coverage_days:.1f} days of predicted demand",
                ))
                risk_score += 0.4
            elif coverage_days < 7:
                risk_factors.append(RiskFactor(
                    factor="Low Inventory",
                    severity=RiskLevel.MEDIUM,
                    description=f"Inventory will last approximately {coverage_days:.1f} days",
                ))
                risk_score += 0.2

        # Risk 2: High demand volatility (from trend)
        if abs(trend.get("change_percent", 0)) > 30:
            severity = RiskLevel.HIGH if abs(trend["change_percent"]) > 50 else RiskLevel.MEDIUM
            direction = "spike" if trend["change_percent"] > 0 else "drop"
            risk_factors.append(RiskFactor(
                factor=f"Demand {direction.title()}",
                severity=severity,
                description=f"Predicted demand shows {abs(trend['change_percent']):.0f}% {direction}",
            ))
            risk_score += 0.3 if severity == RiskLevel.HIGH else 0.15

        # Risk 3: Low model accuracy
        r2 = model_metrics.get("r2", 0.0)
        if r2 < 0.5:
            risk_factors.append(RiskFactor(
                factor="Forecast Uncertainty",
                severity=RiskLevel.HIGH if r2 < 0.3 else RiskLevel.MEDIUM,
                description=f"Model accuracy is low (R²={r2:.1%}), predictions may be unreliable",
            ))
            risk_score += 0.25 if r2 < 0.3 else 0.1

        # Normalize risk score
        risk_score = min(1.0, risk_score)
        risk_level = get_risk_level(risk_score)

        # Determine primary risk
        if risk_factors:
            primary_risk = max(risk_factors, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x.severity.value])
            primary_risk_text = primary_risk.description
        else:
            primary_risk_text = "No significant risks identified"

        return RiskAssessment(
            level=risk_level,
            score=round(risk_score, 2),
            primary_risk=primary_risk_text,
            risk_factors=risk_factors,
        )

    def _generate_summary(
        self,
        product_id: str,
        predictions: List[Dict],
        trend: Dict,
        category: Optional[str] = None,
    ) -> InsightSummary:
        """Generate summary with headline and metrics"""
        total_demand = sum(p.get("predicted_units_sold", 0) for p in predictions)
        avg_daily = total_demand / len(predictions) if predictions else 0
        horizon = len(predictions)

        # Generate headline based on trend
        if trend["direction"] == "increasing":
            headline = f"Demand expected to rise {abs(trend['change_percent']):.0f}%"
        elif trend["direction"] == "decreasing":
            headline = f"Demand expected to drop {abs(trend['change_percent']):.0f}%"
        else:
            headline = "Demand expected to remain stable"

        # Generate detail
        category_text = f" for {category}" if category else ""
        detail = (
            f"Over the next {horizon} days, {product_id}{category_text} "
            f"is forecasted to sell approximately {total_demand:.0f} units "
            f"(avg {avg_daily:.1f}/day)."
        )

        # Metric highlight
        if trend["direction"] != "stable":
            metric_highlight = f"{abs(trend['change_percent']):.0f}% {trend['direction']}"
        else:
            metric_highlight = f"{avg_daily:.1f} units/day"

        return InsightSummary(
            headline=headline,
            detail=detail,
            metric_highlight=metric_highlight,
        )

    def _generate_why(
        self,
        trend: Dict,
        seasonality: Dict,
        feature_importances: List[Dict],
    ) -> WhyItHappened:
        """Generate explanation of forecast drivers"""
        secondary_drivers = []

        # Primary driver from feature importance
        if feature_importances:
            top_feature = feature_importances[0]
            primary_driver = top_feature.get("name", "Historical patterns")
            importance = top_feature.get("importance", 0)
            primary_explanation = (
                f"The model relies heavily on {primary_driver} "
                f"(importance: {importance:.1%}) to generate forecasts."
            )

            # Add secondary drivers from other top features
            for feat in feature_importances[1:4]:
                name = feat.get("name", "")
                imp = feat.get("importance", 0)
                if imp > 0.05:
                    secondary_drivers.append(SecondaryDriver(
                        driver=name,
                        explanation=f"Contributes {imp:.1%} to prediction",
                        impact="neutral",
                    ))
        else:
            primary_driver = "Historical demand patterns"
            primary_explanation = "Forecast is based on historical sales trends and seasonal patterns."

        # Add seasonality as a driver if detected
        if seasonality.get("detected"):
            peak_day = seasonality.get("peak_day", "weekends")
            secondary_drivers.insert(0, SecondaryDriver(
                driver="Weekly seasonality",
                explanation=f"Demand typically peaks on {peak_day}",
                impact="positive" if trend["direction"] == "increasing" else "neutral",
            ))

        # Add trend as a driver
        if trend["direction"] != "stable":
            secondary_drivers.insert(0, SecondaryDriver(
                driver=f"{trend['direction'].title()} trend",
                explanation=f"Recent average: {trend['recent_avg']:.1f} → Predicted: {trend['predicted_avg']:.1f}",
                impact="positive" if trend["direction"] == "increasing" else "negative",
            ))

        return WhyItHappened(
            primary_driver=primary_driver,
            primary_explanation=primary_explanation,
            secondary_drivers=secondary_drivers[:5],  # Limit to 5
        )

    def _generate_actions(
        self,
        risk_assessment: RiskAssessment,
        predictions: List[Dict],
        inventory_level: Optional[int],
        trend: Dict,
    ) -> List[ActionItem]:
        """Generate prioritized action items"""
        actions = []
        total_demand = sum(p.get("predicted_units_sold", 0) for p in predictions)
        horizon = len(predictions)

        # Action 1: Inventory-based
        if inventory_level is not None:
            coverage_days = inventory_level / (total_demand / max(horizon, 1)) if total_demand > 0 else float('inf')

            if coverage_days < 7:
                reorder_qty = max(0, int(total_demand * 1.2 - inventory_level))
                actions.append(ActionItem(
                    priority=1,
                    action=f"Reorder {reorder_qty} units",
                    reason=f"Current stock covers only {coverage_days:.1f} days",
                    deadline="Within 2 days",
                ))

        # Action 2: Based on trend
        if trend["direction"] == "increasing" and trend["change_percent"] > 20:
            actions.append(ActionItem(
                priority=2 if actions else 1,
                action="Prepare for demand surge",
                reason=f"Predicted {trend['change_percent']:.0f}% increase in demand",
                deadline=f"Before {predictions[0]['date']}" if predictions else None,
            ))
        elif trend["direction"] == "decreasing" and trend["change_percent"] < -20:
            actions.append(ActionItem(
                priority=2 if actions else 1,
                action="Review inventory levels",
                reason=f"Demand may drop {abs(trend['change_percent']):.0f}% - avoid overstocking",
                deadline="This week",
            ))

        # Action 3: Based on risk
        for risk in risk_assessment.risk_factors:
            if risk.severity == RiskLevel.HIGH and len(actions) < 4:
                if "stockout" in risk.factor.lower():
                    continue  # Already handled above
                actions.append(ActionItem(
                    priority=len(actions) + 1,
                    action=f"Address: {risk.factor}",
                    reason=risk.description,
                    deadline="Urgent",
                ))

        # Default action if none
        if not actions:
            actions.append(ActionItem(
                priority=1,
                action="Monitor demand patterns",
                reason="No immediate action required based on current forecast",
                deadline=None,
            ))

        return sorted(actions, key=lambda x: x.priority)[:5]

    def _generate_follow_ups(
        self,
        product_id: str,
        category: Optional[str],
        risk_assessment: RiskAssessment,
        trend: Dict,
    ) -> List[FollowUpQuestion]:
        """Generate relevant follow-up questions"""
        questions = []

        # Inventory-related
        questions.append(FollowUpQuestion(
            question=f"What is the current stock level for {product_id}?",
            category="inventory",
        ))

        # Trend-related
        if trend["direction"] != "stable":
            questions.append(FollowUpQuestion(
                question=f"What's driving the {trend['direction']} trend?",
                category="supply_chain",
            ))

        # Category-related
        if category:
            questions.append(FollowUpQuestion(
                question=f"How is the {category} category performing overall?",
                category="marketing",
            ))

        # Risk-related
        if risk_assessment.level in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
            questions.append(FollowUpQuestion(
                question="What mitigation options are available?",
                category="supply_chain",
            ))

        # Pricing
        questions.append(FollowUpQuestion(
            question="Should we adjust pricing based on demand forecast?",
            category="pricing",
        ))

        return questions[:5]
