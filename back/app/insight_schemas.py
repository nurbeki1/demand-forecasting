"""
Insight Schemas - Pydantic models for Decision Assistant with Trust Layer
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


# =========================================================
# ENUMS
# =========================================================

class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TrustFactorStatus(str, Enum):
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"


class VarianceStability(str, Enum):
    STABLE = "stable"
    MODERATE = "moderate"
    VOLATILE = "volatile"


# =========================================================
# TRUST LAYER SCHEMAS
# =========================================================

class TrustFactor(BaseModel):
    """Individual factor contributing to trust score"""
    name: str
    value: str
    status: TrustFactorStatus
    weight: Optional[float] = None
    score: Optional[float] = None


class TrustLayer(BaseModel):
    """Trust layer with confidence metrics and data quality indicators"""
    confidence: ConfidenceLevel
    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_explanation: str
    data_freshness: str  # Human readable: "2 days ago"
    data_freshness_days: int
    model_updated: str  # "2024-12-31 14:30"
    model_age_hours: int
    based_on: List[TrustFactor]
    warnings: List[str]
    r2_score: float
    variance_stability: VarianceStability
    sample_size: int


# =========================================================
# INSIGHT BLOCK SCHEMAS
# =========================================================

class InsightSummary(BaseModel):
    """Summary of the forecast with key highlights"""
    headline: str
    detail: str
    metric_highlight: str


class SecondaryDriver(BaseModel):
    """Secondary factor affecting the forecast"""
    driver: str
    explanation: str
    impact: str  # "positive" | "negative" | "neutral"


class WhyItHappened(BaseModel):
    """Explanation of forecast drivers"""
    primary_driver: str
    primary_explanation: str
    secondary_drivers: List[SecondaryDriver]


class RiskFactor(BaseModel):
    """Individual risk factor"""
    factor: str
    severity: RiskLevel
    description: str


class RiskAssessment(BaseModel):
    """Risk assessment for the forecast"""
    level: RiskLevel
    score: float = Field(ge=0.0, le=1.0)
    primary_risk: str
    risk_factors: List[RiskFactor]


class ActionItem(BaseModel):
    """Recommended action based on forecast"""
    priority: int = Field(ge=1, le=5)
    action: str
    reason: str
    deadline: Optional[str] = None


class FollowUpQuestion(BaseModel):
    """Suggested follow-up question for deeper analysis"""
    question: str
    category: str  # "inventory", "pricing", "supply_chain", "marketing"


class InsightBlock(BaseModel):
    """Complete insight block with all analysis components"""
    summary: InsightSummary
    why_it_happened: WhyItHappened
    risk: RiskAssessment
    what_to_do: List[ActionItem]
    follow_up_questions: List[FollowUpQuestion]


# =========================================================
# PREDICTION POINT (for backward compatibility)
# =========================================================

class PredictionPoint(BaseModel):
    """Single prediction point"""
    date: str
    predicted_units_sold: float


# =========================================================
# DECISION ASSISTANT RESPONSE
# =========================================================

class DecisionAssistantResponse(BaseModel):
    """
    Complete response from Decision Assistant.
    Backward compatible with ForecastResponse but includes insights and trust.
    """
    # Backward compatible fields
    product_id: str
    store_id: Optional[str] = None
    horizon_days: int
    last_date_in_history: str
    predictions: List[PredictionPoint]
    model_metrics: Dict[str, float]

    # New Decision Assistant fields
    insights: InsightBlock
    trust: TrustLayer
    alert_level: Optional[RiskLevel] = None

    # Additional context
    category: Optional[str] = None
    current_inventory: Optional[int] = None
    total_predicted_demand: float
    avg_daily_demand: float

    # Alerts and suggestions
    alerts: List[Dict[str, Any]] = []
    suggestions: List[Dict[str, Any]] = []
    has_critical_alert: bool = False


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_confidence_level(score: float) -> ConfidenceLevel:
    """Convert confidence score to level"""
    if score >= 0.75:
        return ConfidenceLevel.HIGH
    elif score >= 0.50:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW


def get_risk_level(score: float) -> RiskLevel:
    """Convert risk score to level"""
    if score >= 0.7:
        return RiskLevel.HIGH
    elif score >= 0.4:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW
