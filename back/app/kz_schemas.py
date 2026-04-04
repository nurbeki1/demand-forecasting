"""
Kazakhstan Market Analysis Schemas

Pydantic models for KZ regional analysis API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


# ===== Enums =====

class ProfitStatusEnum(str, Enum):
    """Profitability status indicators"""
    PROFITABLE = "profitable"
    RISKY = "risky"
    UNPROFITABLE = "unprofitable"


class CompetitionLevel(str, Enum):
    """Competition level in city"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ===== City Models =====

class CityBase(BaseModel):
    """Basic city information"""
    id: str
    name: str
    name_en: str
    region: str
    tier: int = Field(ge=1, le=3, description="City tier: 1=major, 2=large, 3=small")


class CityEconomics(BaseModel):
    """City economic indicators"""
    population: int
    avg_salary_kzt: float
    purchasing_power_index: float = Field(ge=0, le=2, description="1.0 = Almaty baseline")
    e_commerce_penetration: float = Field(ge=0, le=1)
    competition_level: CompetitionLevel


class CityLogistics(BaseModel):
    """City logistics information"""
    logistics_cost_from_almaty_kzt: float
    coordinates: Dict[str, float]


class CityResponse(CityBase, CityEconomics, CityLogistics):
    """Full city response model"""
    pass


class CityListResponse(BaseModel):
    """List of cities response"""
    cities: List[CityResponse]
    total: int


# ===== Currency Models =====

class CurrencyRates(BaseModel):
    """Currency exchange rates"""
    usd_to_kzt: float
    rub_to_kzt: float
    cny_to_kzt: float
    last_updated: Optional[str] = None


# ===== Category Models =====

class CategoryInfo(BaseModel):
    """Product category information"""
    id: str
    name_ru: str
    demand_multiplier: float
    typical_margin_percent: float
    price_sensitivity: float = Field(ge=0, le=1)


class CategoryListResponse(BaseModel):
    """List of categories response"""
    categories: List[CategoryInfo]


# ===== Analysis Request Models =====

class AnalyzeProductRequest(BaseModel):
    """Request to analyze product profitability"""
    product_name: str = Field(min_length=1, max_length=200)
    product_cost_usd: Optional[float] = Field(
        None,
        ge=0,
        description="Wholesale price in USD. If not provided, will search online."
    )
    category: str = Field(default="electronics")
    markup_percent: float = Field(default=25.0, ge=0, le=200)
    shipping_cost_usd: float = Field(default=0.0, ge=0)


class AnalyzeCityRequest(BaseModel):
    """Request to analyze specific city"""
    product_cost_usd: float = Field(ge=0)
    category: str = Field(default="electronics")
    markup_percent: float = Field(default=25.0, ge=0, le=200)
    shipping_cost_usd: float = Field(default=0.0, ge=0)


# ===== Analysis Response Models =====

class CityProfitAnalysisResponse(BaseModel):
    """Profit analysis for a single city"""
    city_id: str
    city_name: str
    city_name_en: str
    region: str
    tier: int

    # Costs
    product_cost_kzt: float
    logistics_cost_kzt: float
    total_cost_kzt: float

    # Pricing
    recommended_price_kzt: float
    markup_percent: float
    margin_percent: float

    # Profit
    profit_per_unit_kzt: float
    estimated_monthly_demand: int
    total_monthly_profit_kzt: float

    # Status
    status: ProfitStatusEnum
    status_icon: str

    # Metrics
    affordability_index: float
    competition_factor: float
    purchasing_power_index: float


class WholesalePriceInfo(BaseModel):
    """Wholesale price information from search"""
    price_usd: float
    price_kzt: float
    source: str
    url: Optional[str] = None
    found: bool


class RegionalAnalysisResponse(BaseModel):
    """Full regional analysis response"""
    product_name: str
    product_cost_usd: float
    product_cost_kzt: float
    currency_rate: float
    category: str

    # Price info
    wholesale_info: Optional[WholesalePriceInfo] = None

    # City analyses
    cities: List[CityProfitAnalysisResponse]

    # Summary
    best_cities: List[str]
    avoid_cities: List[str]
    total_potential_profit_kzt: float

    # Recommendations
    recommended_quantity: int
    recommended_investment_usd: float
    expected_roi_percent: float
    recommendation: str


# ===== Competitor Models =====

class CompetitorPriceResponse(BaseModel):
    """Competitor price information"""
    product_name: str
    price_kzt: float
    seller: str
    platform: str
    url: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None


class CompetitorAnalysisResponse(BaseModel):
    """Competitor analysis response"""
    product_name: str
    competitors: List[CompetitorPriceResponse]
    avg_price_kzt: float
    min_price_kzt: float
    max_price_kzt: float


# ===== Market Trends Models =====

class MarketTrendResponse(BaseModel):
    """Market trend information"""
    category: str
    trend_direction: str  # "up", "down", "stable"
    trend_description: str
    key_products: List[str]
    source: str


# ===== Logistics Models =====

class LogisticsCostRequest(BaseModel):
    """Request to calculate logistics cost"""
    from_city: str = Field(default="almaty")
    to_city: str
    weight_kg: float = Field(default=1.0, ge=0)
    is_express: bool = False
    is_bulky: bool = False


class LogisticsCostResponse(BaseModel):
    """Logistics cost calculation response"""
    from_city: str
    to_city: str
    base_cost_kzt: float
    weight_cost_kzt: float
    total_cost_kzt: float
    is_express: bool
    is_bulky: bool
