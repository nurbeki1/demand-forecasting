"""
Scenario Service - What-if analysis for demand forecasting

Simulates changes to:
- Price
- Discount
- Promotion/Holiday
- Inventory level
- Competitor pricing

Compares baseline forecast with scenario forecast.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

from services.model_service import (
    get_or_train_model,
    predict,
    DATE_COL,
    TARGET_COL,
)


@dataclass
class ScenarioChange:
    """Single change to apply in scenario"""
    feature: str
    change_type: str  # "absolute" | "percent" | "set"
    value: float


@dataclass
class ScenarioResult:
    """Result of scenario simulation"""
    baseline_predictions: List[Dict[str, Any]]
    scenario_predictions: List[Dict[str, Any]]
    total_baseline: float
    total_scenario: float
    change_percent: float
    change_absolute: float
    impact_explanation: str
    feature_impacts: List[Dict[str, Any]]


class ScenarioService:
    """
    Simulates what-if scenarios by modifying input features
    and comparing predictions against baseline.

    Example usage:
        changes = [
            ScenarioChange("Price", "percent", -10),  # 10% price reduction
            ScenarioChange("Discount", "absolute", 15),  # Add 15% discount
        ]
        result = scenario_service.simulate_scenario(
            product_id="P001",
            df=product_data,
            horizon_days=7,
            changes=changes,
        )
    """

    # Feature elasticity coefficients (approximate impacts)
    ELASTICITIES = {
        "Price": -0.5,           # 10% price increase -> ~5% demand decrease
        "Discount": 0.8,         # 10% more discount -> ~8% demand increase
        "Holiday/Promotion": 0.25,  # Promotion active -> ~25% demand increase
        "Competitor Pricing": 0.3,  # 10% competitor price up -> ~3% our demand up
        "Inventory Level": 0.1,  # Low inventory can signal scarcity
    }

    # Human-readable feature names (Russian)
    FEATURE_NAMES_RU = {
        "Price": "Цена",
        "Discount": "Скидка",
        "Holiday/Promotion": "Акция/Праздник",
        "Competitor Pricing": "Цена конкурента",
        "Inventory Level": "Уровень запасов",
    }

    def simulate_scenario(
        self,
        product_id: str,
        df: pd.DataFrame,
        horizon_days: int,
        changes: List[ScenarioChange],
        store_id: Optional[str] = None,
    ) -> ScenarioResult:
        """
        Run scenario simulation.

        Args:
            product_id: Product to simulate
            df: Historical data for the product (already filtered)
            horizon_days: Forecast horizon (1-30 days)
            changes: List of changes to apply
            store_id: Optional store filter

        Returns:
            ScenarioResult with baseline vs scenario comparison
        """
        # 1. Get trained model
        trained = get_or_train_model(df, product_id, store_id)

        # 2. Get baseline predictions
        future_df_baseline, baseline_preds = predict(trained, horizon_days)

        # 3. Copy last_row and apply changes
        modified_last_row = dict(trained["last_row"])
        feature_impacts = []

        for change in changes:
            if change.feature not in modified_last_row:
                continue

            original_value = modified_last_row.get(change.feature, 0)
            if original_value is None:
                original_value = 0

            # Apply change based on type
            if change.change_type == "percent":
                new_value = float(original_value) * (1 + change.value / 100)
            elif change.change_type == "absolute":
                new_value = float(original_value) + change.value
            else:  # "set"
                new_value = change.value

            modified_last_row[change.feature] = new_value

            # Calculate expected impact based on elasticity
            elasticity = self.ELASTICITIES.get(change.feature, 0)
            if change.change_type == "percent":
                pct_change = change.value
            else:
                if original_value != 0:
                    pct_change = ((new_value - float(original_value)) / abs(float(original_value))) * 100
                else:
                    pct_change = 100 if new_value > 0 else 0

            expected_demand_impact = pct_change * elasticity

            feature_impacts.append({
                "feature": change.feature,
                "feature_name_ru": self.FEATURE_NAMES_RU.get(change.feature, change.feature),
                "original": round(float(original_value), 2) if original_value else 0,
                "modified": round(float(new_value), 2),
                "change_type": change.change_type,
                "change_value": change.value,
                "change_percent": round(pct_change, 2),
                "expected_demand_impact_percent": round(expected_demand_impact, 2),
            })

        # 4. Create modified trained dict for prediction
        modified_trained = dict(trained)
        modified_trained["last_row"] = modified_last_row

        # 5. Get scenario predictions
        future_df_scenario, scenario_preds = predict(modified_trained, horizon_days)

        # 6. Build results
        baseline_list = [
            {"date": str(d.date()), "predicted_units_sold": round(float(p), 2)}
            for d, p in zip(future_df_baseline[DATE_COL], baseline_preds)
        ]

        scenario_list = [
            {"date": str(d.date()), "predicted_units_sold": round(float(p), 2)}
            for d, p in zip(future_df_scenario[DATE_COL], scenario_preds)
        ]

        total_baseline = sum(p["predicted_units_sold"] for p in baseline_list)
        total_scenario = sum(p["predicted_units_sold"] for p in scenario_list)
        change_absolute = total_scenario - total_baseline
        change_percent = (change_absolute / max(total_baseline, 1)) * 100

        # 7. Generate explanation
        impact_explanation = self._generate_explanation(
            changes=changes,
            feature_impacts=feature_impacts,
            total_change_percent=change_percent,
            total_change_absolute=change_absolute,
            horizon_days=horizon_days,
        )

        return ScenarioResult(
            baseline_predictions=baseline_list,
            scenario_predictions=scenario_list,
            total_baseline=round(total_baseline, 2),
            total_scenario=round(total_scenario, 2),
            change_percent=round(change_percent, 2),
            change_absolute=round(change_absolute, 2),
            impact_explanation=impact_explanation,
            feature_impacts=feature_impacts,
        )

    def _generate_explanation(
        self,
        changes: List[ScenarioChange],
        feature_impacts: List[Dict[str, Any]],
        total_change_percent: float,
        total_change_absolute: float,
        horizon_days: int,
    ) -> str:
        """Generate human-readable explanation of scenario impact"""
        # Build summary
        if total_change_percent > 5:
            direction = "увеличит"
            impact_word = "рост"
        elif total_change_percent < -5:
            direction = "снизит"
            impact_word = "снижение"
        else:
            direction = "практически не изменит"
            impact_word = "изменение"

        summary = (
            f"Данный сценарий {direction} спрос на {abs(total_change_percent):.1f}% "
            f"({total_change_absolute:+.0f} ед.) за {horizon_days} дней."
        )

        # Build factor descriptions
        factor_descriptions = []
        for impact in feature_impacts:
            feature_name = impact["feature_name_ru"]
            change_pct = impact["change_percent"]
            demand_impact = impact["expected_demand_impact_percent"]

            if change_pct > 0:
                change_word = "увеличение"
            else:
                change_word = "снижение"

            if demand_impact > 0:
                effect_word = "повысит"
            elif demand_impact < 0:
                effect_word = "снизит"
            else:
                effect_word = "не повлияет на"

            factor_descriptions.append(
                f"{feature_name}: {change_word} на {abs(change_pct):.1f}% "
                f"ожидаемо {effect_word} спрос на ~{abs(demand_impact):.1f}%"
            )

        if factor_descriptions:
            factors_text = ". ".join(factor_descriptions) + "."
            return f"{summary} {factors_text}"

        return summary

    def get_available_features(self) -> List[Dict[str, Any]]:
        """Get list of features available for scenario simulation"""
        return [
            {
                "feature": "Price",
                "name_ru": "Цена",
                "description": "Изменение цены товара",
                "elasticity": self.ELASTICITIES["Price"],
                "recommended_range": {"min": -30, "max": 30, "unit": "%"},
            },
            {
                "feature": "Discount",
                "name_ru": "Скидка",
                "description": "Процент скидки на товар",
                "elasticity": self.ELASTICITIES["Discount"],
                "recommended_range": {"min": 0, "max": 50, "unit": "%"},
            },
            {
                "feature": "Holiday/Promotion",
                "name_ru": "Акция",
                "description": "Активна ли промо-акция (0 или 1)",
                "elasticity": self.ELASTICITIES["Holiday/Promotion"],
                "recommended_range": {"min": 0, "max": 1, "unit": "flag"},
            },
            {
                "feature": "Competitor Pricing",
                "name_ru": "Цена конкурента",
                "description": "Изменение цены у конкурентов",
                "elasticity": self.ELASTICITIES["Competitor Pricing"],
                "recommended_range": {"min": -30, "max": 30, "unit": "%"},
            },
        ]


# Singleton instance
scenario_service = ScenarioService()
