"""
Trust Service - Calculate confidence scores and trust layer metrics
"""

from __future__ import annotations
from typing import Dict, List
from datetime import datetime
import pandas as pd
import numpy as np

from app.insight_schemas import (
    TrustLayer,
    TrustFactor,
    TrustFactorStatus,
    ConfidenceLevel,
    VarianceStability,
    get_confidence_level,
)


class TrustCalculator:
    """
    Calculates trust layer metrics using weighted scoring.

    Formula:
        confidence_score = 0.40 * r2_score + 0.25 * freshness_score +
                          0.20 * variance_score + 0.15 * sample_score

    Thresholds:
        HIGH: score >= 0.75
        MEDIUM: score >= 0.50
        LOW: score < 0.50
    """

    WEIGHTS = {
        "r2": 0.40,
        "freshness": 0.25,
        "variance": 0.20,
        "sample_size": 0.15,
    }

    def calculate_trust_layer(
        self,
        model_metrics: Dict[str, float],
        trained_at: datetime,
        last_data_date: datetime,
        historical_demand: pd.Series,
        sample_size: int,
    ) -> TrustLayer:
        """
        Calculate complete trust layer with all metrics.

        Args:
            model_metrics: Dict with 'mae', 'rmse', 'r2' keys
            trained_at: When the model was trained
            last_data_date: Date of most recent data point
            historical_demand: Series of historical demand values
            sample_size: Number of data points used

        Returns:
            TrustLayer with all calculated metrics
        """
        # Calculate individual scores
        r2_score = self._r2_to_score(model_metrics.get("r2", 0.0))
        freshness_score, freshness_days = self._freshness_to_score(last_data_date)
        variance_score, variance_stability = self._variance_to_score(historical_demand)
        sample_score = self._sample_to_score(sample_size)

        # Calculate weighted confidence score
        confidence_score = (
            self.WEIGHTS["r2"] * r2_score +
            self.WEIGHTS["freshness"] * freshness_score +
            self.WEIGHTS["variance"] * variance_score +
            self.WEIGHTS["sample_size"] * sample_score
        )

        # Determine confidence level
        confidence = get_confidence_level(confidence_score)

        # Calculate model age
        model_age_hours = int((datetime.now() - trained_at).total_seconds() / 3600)

        # Build trust factors list
        based_on = self._build_trust_factors(
            r2_score=r2_score,
            r2_value=model_metrics.get("r2", 0.0),
            freshness_score=freshness_score,
            freshness_days=freshness_days,
            variance_score=variance_score,
            variance_stability=variance_stability,
            sample_score=sample_score,
            sample_size=sample_size,
        )

        # Generate warnings
        warnings = self._generate_warnings(
            r2_value=model_metrics.get("r2", 0.0),
            freshness_days=freshness_days,
            variance_stability=variance_stability,
            sample_size=sample_size,
            model_age_hours=model_age_hours,
        )

        # Generate explanation
        confidence_explanation = self._generate_explanation(
            confidence=confidence,
            confidence_score=confidence_score,
            based_on=based_on,
        )

        # Human-readable freshness
        if freshness_days == 0:
            data_freshness = "today"
        elif freshness_days == 1:
            data_freshness = "yesterday"
        else:
            data_freshness = f"{freshness_days} days ago"

        return TrustLayer(
            confidence=confidence,
            confidence_score=round(confidence_score, 3),
            confidence_explanation=confidence_explanation,
            data_freshness=data_freshness,
            data_freshness_days=freshness_days,
            model_updated=trained_at.strftime("%Y-%m-%d %H:%M"),
            model_age_hours=model_age_hours,
            based_on=based_on,
            warnings=warnings,
            r2_score=round(model_metrics.get("r2", 0.0), 4),
            variance_stability=variance_stability,
            sample_size=sample_size,
        )

    def _r2_to_score(self, r2: float) -> float:
        """
        Convert R2 score to normalized score (0-1).

        Thresholds:
            >0.75 = good (score 1.0)
            0.50-0.75 = acceptable (score 0.5-1.0)
            <0.50 = critical (score 0-0.5)
        """
        if r2 >= 0.75:
            return 1.0
        elif r2 >= 0.50:
            # Linear interpolation from 0.5 to 1.0
            return 0.5 + (r2 - 0.50) * 2
        elif r2 >= 0:
            # Linear interpolation from 0 to 0.5
            return r2
        else:
            return 0.0

    def _freshness_to_score(self, last_data_date: datetime) -> tuple[float, int]:
        """
        Convert data freshness to score.

        Thresholds:
            <3 days = good (score 1.0)
            3-7 days = warning (score 0.5-1.0)
            >7 days = critical (score 0-0.5)
        """
        days_old = (datetime.now() - last_data_date).days

        if days_old < 3:
            score = 1.0
        elif days_old <= 7:
            # Linear decay from 1.0 to 0.5
            score = 1.0 - (days_old - 3) * 0.125
        elif days_old <= 14:
            # Linear decay from 0.5 to 0.0
            score = 0.5 - (days_old - 7) * 0.071
        else:
            score = 0.0

        return max(0.0, min(1.0, score)), max(0, days_old)

    def _variance_to_score(self, demand: pd.Series) -> tuple[float, VarianceStability]:
        """
        Convert demand variance to score using coefficient of variation (CV).

        Thresholds:
            CV < 0.3 = stable (score 1.0)
            CV 0.3-0.5 = moderate (score 0.5-1.0)
            CV > 0.5 = volatile (score 0-0.5)
        """
        if len(demand) < 2:
            return 0.5, VarianceStability.MODERATE

        mean_demand = demand.mean()
        if mean_demand == 0:
            return 0.5, VarianceStability.MODERATE

        cv = demand.std() / mean_demand

        if cv < 0.3:
            return 1.0, VarianceStability.STABLE
        elif cv < 0.5:
            # Linear interpolation
            score = 1.0 - (cv - 0.3) * 2.5
            return score, VarianceStability.MODERATE
        else:
            # Linear decay for high variance
            score = max(0.0, 0.5 - (cv - 0.5) * 0.5)
            return score, VarianceStability.VOLATILE

    def _sample_to_score(self, sample_size: int) -> float:
        """
        Convert sample size to score.

        Thresholds:
            >90 days = good (score 1.0)
            30-90 days = acceptable (score 0.5-1.0)
            <30 days = critical (score 0-0.5)
        """
        if sample_size >= 90:
            return 1.0
        elif sample_size >= 30:
            # Linear interpolation from 0.5 to 1.0
            return 0.5 + (sample_size - 30) * (0.5 / 60)
        elif sample_size >= 10:
            # Linear interpolation from 0.0 to 0.5
            return (sample_size - 10) * (0.5 / 20)
        else:
            return 0.0

    def _get_status(self, score: float) -> TrustFactorStatus:
        """Convert score to status"""
        if score >= 0.75:
            return TrustFactorStatus.GOOD
        elif score >= 0.5:
            return TrustFactorStatus.WARNING
        else:
            return TrustFactorStatus.CRITICAL

    def _build_trust_factors(
        self,
        r2_score: float,
        r2_value: float,
        freshness_score: float,
        freshness_days: int,
        variance_score: float,
        variance_stability: VarianceStability,
        sample_score: float,
        sample_size: int,
    ) -> List[TrustFactor]:
        """Build list of trust factors with their status"""
        return [
            TrustFactor(
                name="Model Accuracy (R²)",
                value=f"{r2_value:.2%}",
                status=self._get_status(r2_score),
                weight=self.WEIGHTS["r2"],
                score=round(r2_score, 3),
            ),
            TrustFactor(
                name="Data Freshness",
                value=f"{freshness_days} days old",
                status=self._get_status(freshness_score),
                weight=self.WEIGHTS["freshness"],
                score=round(freshness_score, 3),
            ),
            TrustFactor(
                name="Demand Stability",
                value=variance_stability.value,
                status=self._get_status(variance_score),
                weight=self.WEIGHTS["variance"],
                score=round(variance_score, 3),
            ),
            TrustFactor(
                name="Sample Size",
                value=f"{sample_size} data points",
                status=self._get_status(sample_score),
                weight=self.WEIGHTS["sample_size"],
                score=round(sample_score, 3),
            ),
        ]

    def _generate_warnings(
        self,
        r2_value: float,
        freshness_days: int,
        variance_stability: VarianceStability,
        sample_size: int,
        model_age_hours: int,
    ) -> List[str]:
        """Generate warnings based on trust factors"""
        warnings = []

        if r2_value < 0.5:
            warnings.append(
                f"Model accuracy is low (R²={r2_value:.1%}). "
                "Consider retraining with more data or reviewing feature engineering."
            )

        if freshness_days > 7:
            warnings.append(
                f"Data is {freshness_days} days old. "
                "Recent trends may not be captured in the forecast."
            )

        if variance_stability == VarianceStability.VOLATILE:
            warnings.append(
                "Demand pattern is highly volatile. "
                "Forecast confidence is reduced due to unpredictable fluctuations."
            )

        if sample_size < 30:
            warnings.append(
                f"Limited training data ({sample_size} points). "
                "More historical data would improve forecast reliability."
            )

        if model_age_hours > 168:  # 7 days
            warnings.append(
                f"Model was trained {model_age_hours // 24} days ago. "
                "Consider retraining to capture recent patterns."
            )

        return warnings

    def _generate_explanation(
        self,
        confidence: ConfidenceLevel,
        confidence_score: float,
        based_on: List[TrustFactor],
    ) -> str:
        """Generate human-readable explanation of confidence"""
        # Find best and worst factors
        sorted_factors = sorted(based_on, key=lambda x: x.score or 0, reverse=True)
        best = sorted_factors[0] if sorted_factors else None
        worst = sorted_factors[-1] if sorted_factors else None

        if confidence == ConfidenceLevel.HIGH:
            base = f"High confidence ({confidence_score:.0%})"
            if best:
                return f"{base}. Strong {best.name.lower()} supports this forecast."
        elif confidence == ConfidenceLevel.MEDIUM:
            base = f"Moderate confidence ({confidence_score:.0%})"
            if worst and worst.status != TrustFactorStatus.GOOD:
                return f"{base}. {worst.name} could be improved for better accuracy."
            return f"{base}. Consider this forecast with some caution."
        else:
            base = f"Low confidence ({confidence_score:.0%})"
            issues = [f.name.lower() for f in based_on if f.status == TrustFactorStatus.CRITICAL]
            if issues:
                return f"{base}. Issues with: {', '.join(issues[:2])}."
            return f"{base}. Treat this forecast as a rough estimate only."

        return f"Confidence: {confidence_score:.0%}"
