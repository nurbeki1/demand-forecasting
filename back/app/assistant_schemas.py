"""
Enhanced Assistant Response Schemas
Action-oriented chat with structured outputs
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime


# =============================================================================
# ENUMS
# =============================================================================

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertType(str, Enum):
    STOCKOUT_RISK = "stockout_risk"
    DEMAND_SPIKE = "demand_spike"
    DEMAND_DROP = "demand_drop"
    CATEGORY_DECLINE = "category_decline"
    REGION_ANOMALY = "region_anomaly"
    FORECAST_UNSTABLE = "forecast_unstable"
    REPLENISHMENT_NEEDED = "replenishment_needed"


class ResponseBlockType(str, Enum):
    SUMMARY = "summary"
    METRICS = "metrics"
    EXPLANATION = "explanation"
    COMPARISON = "comparison"
    RANKED_LIST = "ranked_list"
    TREND = "trend"
    ALERT = "alert"
    CHART_DATA = "chart_data"
    ACTIONS = "actions"


# =============================================================================
# METRICS & DATA BLOCKS
# =============================================================================

class MetricItem(BaseModel):
    """Single metric display"""
    label: str
    value: Any
    unit: Optional[str] = None
    change: Optional[float] = None  # percentage change
    change_direction: Optional[Literal["up", "down", "stable"]] = None
    is_good: Optional[bool] = None  # green/red indicator


class RankedItem(BaseModel):
    """Item in a ranked list"""
    rank: int
    product_id: Optional[str] = None
    name: str
    value: Any
    metric_label: str
    risk_level: Optional[ConfidenceLevel] = None
    trend: Optional[Literal["rising", "falling", "stable"]] = None
    details: Optional[Dict[str, Any]] = None


class ComparisonRow(BaseModel):
    """Single comparison dimension"""
    dimension: str
    value_a: Any
    value_b: Any
    winner: Optional[Literal["a", "b", "tie"]] = None
    note: Optional[str] = None


class TrendPoint(BaseModel):
    """Data point for trend visualization"""
    date: str
    value: float
    is_forecast: bool = False


class ChartData(BaseModel):
    """Chart-ready data structure"""
    chart_type: Literal["line", "bar", "pie", "comparison"]
    title: str
    data: List[Dict[str, Any]]
    x_key: str = "date"
    y_keys: List[str] = ["value"]
    colors: Optional[Dict[str, str]] = None


# =============================================================================
# FORECAST INTELLIGENCE
# =============================================================================

class ForecastDriver(BaseModel):
    """Factor affecting forecast"""
    factor: str
    impact: Literal["high", "medium", "low"]
    direction: Literal["increases", "decreases", "stabilizes"]
    value: Optional[Any] = None
    explanation: str


class ForecastExplanation(BaseModel):
    """Human-readable forecast explanation"""
    summary: str
    top_drivers: List[ForecastDriver]
    seasonal_effect: Optional[str] = None
    trend_effect: Optional[str] = None
    promotion_effect: Optional[str] = None
    region_effect: Optional[str] = None
    confidence_reasoning: str


class EnhancedForecastPoint(BaseModel):
    """Single forecast point with intelligence"""
    date: str
    predicted_demand: float
    confidence: ConfidenceLevel
    confidence_score: float  # 0-1
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


class EnhancedForecastResponse(BaseModel):
    """Full forecast response with explainability"""
    product_id: str
    product_name: Optional[str] = None
    store_id: Optional[str] = None

    # Predictions
    forecast: List[EnhancedForecastPoint]

    # Metrics
    total_predicted: float
    average_daily: float
    peak_day: str
    peak_demand: float

    # Intelligence
    confidence: ConfidenceLevel
    confidence_score: float
    explanation: ForecastExplanation

    # Alerts
    alerts: List["Alert"] = []

    # History for comparison
    recent_history: Optional[List[TrendPoint]] = None

    # Model info
    model_metrics: Optional[Dict[str, float]] = None


# =============================================================================
# ALERTS
# =============================================================================

class Alert(BaseModel):
    """Actionable alert"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    metric_value: Optional[Any] = None
    threshold: Optional[Any] = None
    recommended_action: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# SCENARIO ANALYSIS
# =============================================================================

class ScenarioInput(BaseModel):
    """What-if scenario parameters"""
    product_id: str
    store_id: Optional[str] = None
    horizon_days: int = 7

    # Modifiable parameters
    price_change_percent: Optional[float] = None
    discount_change_percent: Optional[float] = None
    promotion_active: Optional[bool] = None
    inventory_change_percent: Optional[float] = None
    competitor_price_change_percent: Optional[float] = None


class ScenarioResult(BaseModel):
    """Scenario analysis result"""
    scenario_name: str
    baseline_forecast: List[EnhancedForecastPoint]
    scenario_forecast: List[EnhancedForecastPoint]

    # Impact summary
    total_demand_change: float
    total_demand_change_percent: float

    # Explanation
    impact_explanation: str
    key_changes: List[Dict[str, Any]]

    # Recommendation
    recommendation: str


# =============================================================================
# STRUCTURED RESPONSE BLOCKS
# =============================================================================

class ResponseBlock(BaseModel):
    """Generic response block for structured output"""
    type: ResponseBlockType
    title: Optional[str] = None
    content: Any  # Type depends on block type
    priority: int = 0  # For ordering blocks


class SuggestedAction(BaseModel):
    """Follow-up action suggestion"""
    label: str
    query: str  # Pre-filled query to send
    icon: Optional[str] = None  # Icon name for UI
    category: Literal["explore", "compare", "forecast", "alert", "insight"] = "explore"


# =============================================================================
# MAIN ASSISTANT RESPONSE
# =============================================================================

class AssistantResponse(BaseModel):
    """
    Enhanced assistant response with structured blocks
    This is the main response schema for the chat endpoint
    """
    # Core response
    reply: str  # Natural language summary (always present)
    intent: str

    # Structured content blocks
    blocks: List[ResponseBlock] = []

    # Data for visualization
    chart_data: Optional[ChartData] = None

    # Product data (for carousels, cards)
    products: Optional[List[Dict[str, Any]]] = None

    # Alerts relevant to the query
    alerts: Optional[List[Alert]] = None

    # Follow-up suggestions
    suggested_actions: List[SuggestedAction] = []

    # Entities extracted
    entities: Dict[str, Any] = {}

    # Metadata
    confidence: Optional[ConfidenceLevel] = None
    processing_time_ms: Optional[int] = None


# =============================================================================
# ADMIN DASHBOARD SCHEMAS
# =============================================================================

class DashboardMetric(BaseModel):
    """Executive dashboard metric card"""
    id: str
    label: str
    value: Any
    unit: Optional[str] = None
    change: Optional[float] = None
    change_period: str = "vs last week"
    trend: Optional[Literal["up", "down", "stable"]] = None
    is_positive: Optional[bool] = None  # Is the trend good?
    icon: Optional[str] = None


class RiskProduct(BaseModel):
    """Product with risk indicators"""
    product_id: str
    name: str
    category: str
    region: Optional[str] = None
    risk_type: AlertType
    risk_score: float  # 0-1
    risk_level: AlertSeverity
    current_inventory: Optional[int] = None
    predicted_demand_7d: Optional[float] = None
    days_until_stockout: Optional[int] = None
    recommended_action: str


class CategoryInsight(BaseModel):
    """Category performance insight"""
    category: str
    total_products: int
    avg_demand: float
    trend: Literal["growing", "declining", "stable"]
    change_percent: float
    top_product: str
    alert_count: int


class AIInsight(BaseModel):
    """LLM-generated insight"""
    id: str
    title: str
    description: str
    category: Literal["trend", "risk", "opportunity", "anomaly"]
    severity: AlertSeverity
    affected_items: List[str]  # Product IDs or categories
    generated_at: datetime
    action_query: Optional[str] = None  # Query to explore this insight


class ExecutiveDashboard(BaseModel):
    """Complete executive dashboard data"""
    # Key metrics
    metrics: List[DashboardMetric]

    # Risk overview
    high_risk_products: List[RiskProduct]
    total_risk_count: int

    # Category performance
    category_insights: List[CategoryInsight]

    # AI-generated insights
    ai_insights: List[AIInsight]

    # Alerts
    active_alerts: List[Alert]

    # Last updated
    last_updated: datetime
    data_freshness: str  # "2 hours ago"


class ForecastExplorerRequest(BaseModel):
    """Request for forecast explorer"""
    product_ids: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    stores: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    horizon_days: int = 7
    include_alerts: bool = True
    include_explanation: bool = True


class ForecastExplorerResponse(BaseModel):
    """Response for forecast explorer"""
    forecasts: List[EnhancedForecastResponse]
    summary: Dict[str, Any]
    alerts: List[Alert]
    filters_applied: Dict[str, Any]


class DataOperationsStatus(BaseModel):
    """Data operations dashboard"""
    # Dataset info
    total_rows: int
    total_products: int
    total_stores: int
    date_range: Dict[str, str]
    last_upload: Optional[datetime] = None

    # Model info
    models_cached: int
    last_training: Optional[datetime] = None
    model_version: str = "1.0"

    # Data quality
    missing_values_percent: float
    data_freshness_days: int
    quality_score: float  # 0-100
    quality_issues: List[str]

    # Actions available
    can_retrain: bool = True
    can_upload: bool = True


# Update forward references
EnhancedForecastResponse.model_rebuild()
