"""
Profit Calculator Service

Calculates profitability for products across Kazakhstan cities:
- Cost breakdown (wholesale + shipping + logistics)
- Optimal pricing based on local purchasing power
- Demand estimation by city
- Profit projections with status indicators

Formula: profit = (price - cost - logistics) × demand
"""

from __future__ import annotations
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from services.kz_market_service import kz_market_service, City
from services.web_search_service import web_search_service, ProductPriceInfo


class ProfitStatus(Enum):
    """Profitability status indicators"""
    PROFITABLE = "profitable"      # 🟢 Good margin
    RISKY = "risky"                # 🟡 Low margin or uncertain
    UNPROFITABLE = "unprofitable"  # 🔴 Loss or very low margin


@dataclass
class CityProfitAnalysis:
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
    status: ProfitStatus
    status_icon: str

    # Additional metrics
    affordability_index: float  # 0-1, how affordable for local buyers
    competition_factor: float   # 0-1, market saturation
    purchasing_power_index: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "city_id": self.city_id,
            "city_name": self.city_name,
            "city_name_en": self.city_name_en,
            "region": self.region,
            "tier": self.tier,
            "product_cost_kzt": self.product_cost_kzt,
            "logistics_cost_kzt": self.logistics_cost_kzt,
            "total_cost_kzt": self.total_cost_kzt,
            "recommended_price_kzt": self.recommended_price_kzt,
            "markup_percent": self.markup_percent,
            "margin_percent": round(self.margin_percent, 1),
            "profit_per_unit_kzt": self.profit_per_unit_kzt,
            "estimated_monthly_demand": self.estimated_monthly_demand,
            "total_monthly_profit_kzt": self.total_monthly_profit_kzt,
            "status": self.status.value,
            "status_icon": self.status_icon,
            "affordability_index": round(self.affordability_index, 2),
            "competition_factor": round(self.competition_factor, 2),
            "purchasing_power_index": self.purchasing_power_index,
        }


@dataclass
class InvestmentSummary:
    """Investment and ROI breakdown"""
    total_investment_usd: float
    total_investment_kzt: float
    shipping_cost_usd: float
    recommended_quantity: int
    expected_revenue_kzt: float
    expected_profit_kzt: float
    roi_percent: float
    payback_months: float
    break_even_units: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_investment_usd": round(self.total_investment_usd, 2),
            "total_investment_kzt": round(self.total_investment_kzt, 2),
            "shipping_cost_usd": round(self.shipping_cost_usd, 2),
            "recommended_quantity": self.recommended_quantity,
            "expected_revenue_kzt": round(self.expected_revenue_kzt, 2),
            "expected_profit_kzt": round(self.expected_profit_kzt, 2),
            "roi_percent": round(self.roi_percent, 1),
            "payback_months": round(self.payback_months, 2),
            "break_even_units": self.break_even_units,
        }


@dataclass
class RiskAnalysis:
    """Risk assessment"""
    overall_risk: str  # "low", "medium", "high"
    risk_score: float  # 0-100
    factors: List[Dict[str, Any]] = field(default_factory=list)
    seasonality_note: str = ""
    currency_risk: str = ""
    competition_risk: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_risk": self.overall_risk,
            "risk_score": round(self.risk_score, 1),
            "factors": self.factors,
            "seasonality_note": self.seasonality_note,
            "currency_risk": self.currency_risk,
            "competition_risk": self.competition_risk,
        }


@dataclass
class CompetitorAnalysis:
    """Competitor pricing analysis"""
    avg_price_kzt: float
    min_price_kzt: float
    max_price_kzt: float
    our_price_vs_market: float  # percentage difference
    price_position: str  # "below", "at", "above"
    competitor_count: int
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "avg_price_kzt": round(self.avg_price_kzt, 2),
            "min_price_kzt": round(self.min_price_kzt, 2),
            "max_price_kzt": round(self.max_price_kzt, 2),
            "our_price_vs_market": round(self.our_price_vs_market, 1),
            "price_position": self.price_position,
            "competitor_count": self.competitor_count,
            "source": self.source,
        }


@dataclass
class MarketInsights:
    """Market insights and tips"""
    best_selling_months: List[str] = field(default_factory=list)
    kaspi_installment_impact: str = ""
    target_audience: str = ""
    marketing_tips: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "best_selling_months": self.best_selling_months,
            "kaspi_installment_impact": self.kaspi_installment_impact,
            "target_audience": self.target_audience,
            "marketing_tips": self.marketing_tips,
        }


@dataclass
class RegionalAnalysisResult:
    """Full regional analysis across all cities"""
    product_name: str
    product_cost_usd: float
    product_cost_kzt: float
    currency_rate: float
    category: str

    # City analyses
    cities: List[CityProfitAnalysis] = field(default_factory=list)

    # Summary
    best_cities: List[str] = field(default_factory=list)
    avoid_cities: List[str] = field(default_factory=list)
    total_potential_profit_kzt: float = 0.0
    total_demand: int = 0
    profitable_cities_count: int = 0
    risky_cities_count: int = 0

    # Wholesale recommendation
    recommended_quantity: int = 0
    recommended_investment_usd: float = 0.0
    expected_roi_percent: float = 0.0

    # Extended analysis
    investment: Optional[InvestmentSummary] = None
    risk_analysis: Optional[RiskAnalysis] = None
    competitor_analysis: Optional[CompetitorAnalysis] = None
    market_insights: Optional[MarketInsights] = None

    # Price info
    retail_price_usd: float = 0.0  # Original retail price before wholesale discount
    wholesale_discount_applied: bool = False

    # Warnings
    warnings: List[str] = field(default_factory=list)
    is_profitable: bool = True

    # Text recommendation
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_name": self.product_name,
            "product_cost_usd": self.product_cost_usd,
            "product_cost_kzt": self.product_cost_kzt,
            "currency_rate": self.currency_rate,
            "category": self.category,
            "cities": [c.to_dict() for c in self.cities],
            "best_cities": self.best_cities,
            "avoid_cities": self.avoid_cities,
            "total_potential_profit_kzt": self.total_potential_profit_kzt,
            "total_demand": self.total_demand,
            "profitable_cities_count": self.profitable_cities_count,
            "risky_cities_count": self.risky_cities_count,
            "recommended_quantity": self.recommended_quantity,
            "recommended_investment_usd": self.recommended_investment_usd,
            "expected_roi_percent": round(self.expected_roi_percent, 1),
            "investment": self.investment.to_dict() if self.investment else None,
            "risk_analysis": self.risk_analysis.to_dict() if self.risk_analysis else None,
            "competitor_analysis": self.competitor_analysis.to_dict() if self.competitor_analysis else None,
            "market_insights": self.market_insights.to_dict() if self.market_insights else None,
            "retail_price_usd": self.retail_price_usd,
            "wholesale_discount_applied": self.wholesale_discount_applied,
            "warnings": self.warnings,
            "is_profitable": self.is_profitable,
            "recommendation": self.recommendation,
        }


class ProfitCalculatorService:
    """
    Profit Calculator for Kazakhstan Regional Market.

    Analyzes product profitability across cities considering:
    - Wholesale cost (USD) converted to KZT
    - Logistics costs per city
    - Local purchasing power
    - Competition levels
    - Estimated demand
    """

    # Minimum acceptable margin thresholds
    MIN_PROFITABLE_MARGIN = 15.0   # 15% = profitable
    MIN_RISKY_MARGIN = 5.0         # 5-15% = risky

    # Wholesale discount from retail price (Tavily returns retail prices)
    WHOLESALE_DISCOUNT = 0.20  # 20% discount for bulk orders

    # Demand reality factor (Tavily overestimates market size)
    DEMAND_REALITY_FACTOR = 0.10  # Divide by 10 for realistic single-seller demand

    def __init__(self):
        self.market_service = kz_market_service
        self.web_search = web_search_service

    def apply_wholesale_discount(self, retail_price_usd: float, quantity: int = 100) -> float:
        """
        Apply wholesale discount to retail price.

        Args:
            retail_price_usd: Retail price from search
            quantity: Order quantity (higher = more discount)

        Returns:
            Estimated wholesale price
        """
        # Base discount 20%, additional 5% for large orders
        if quantity >= 500:
            discount = self.WHOLESALE_DISCOUNT + 0.10  # 30%
        elif quantity >= 200:
            discount = self.WHOLESALE_DISCOUNT + 0.05  # 25%
        else:
            discount = self.WHOLESALE_DISCOUNT  # 20%

        return retail_price_usd * (1 - discount)

    def calculate_city_profit(
        self,
        product_cost_usd: float,
        category: str,
        city_id: str,
        markup_percent: float = 25.0,
        shipping_cost_usd: float = 0.0,
    ) -> Optional[CityProfitAnalysis]:
        """
        Calculate profitability for a product in a specific city.

        Args:
            product_cost_usd: Wholesale price in USD
            category: Product category (electronics, clothing, etc.)
            city_id: Target city ID
            markup_percent: Desired markup percentage
            shipping_cost_usd: International shipping cost per unit

        Returns:
            CityProfitAnalysis with detailed breakdown
        """
        city = self.market_service.get_city_by_id(city_id)
        if city is None:
            return None

        # Get currency rate
        currency_rate = self.market_service.get_currency_rate("USD")

        # Convert costs to KZT
        product_cost_kzt = (product_cost_usd + shipping_cost_usd) * currency_rate

        # Get logistics cost from Almaty (main distribution hub)
        logistics_cost_kzt = self.market_service.get_logistics_cost(
            from_city="almaty",
            to_city=city_id
        )

        total_cost_kzt = product_cost_kzt + logistics_cost_kzt

        # Calculate recommended price with markup
        base_price = total_cost_kzt * (1 + markup_percent / 100)

        # Adjust price based on local purchasing power
        # Higher purchasing power = can charge more
        price_adjustment = city.purchasing_power_index
        recommended_price_kzt = round(base_price * price_adjustment, -3)  # Round to thousands

        # Ensure price covers costs
        if recommended_price_kzt < total_cost_kzt * 1.05:
            recommended_price_kzt = round(total_cost_kzt * 1.10, -3)

        # Calculate actual margin
        profit_per_unit = recommended_price_kzt - total_cost_kzt
        margin_percent = (profit_per_unit / recommended_price_kzt) * 100 if recommended_price_kzt > 0 else 0

        # Estimate demand
        base_demand = self.market_service.estimate_market_size(city_id, category)

        # Adjust demand by affordability
        affordability = self.market_service.get_affordability_index(city_id, recommended_price_kzt)
        competition_factor = self.market_service.get_competition_factor(city_id)

        # Final demand = base × affordability × competition_factor × reality_factor
        # Reality factor accounts for single seller's market share (not total market)
        estimated_demand = int(base_demand * affordability * competition_factor * self.DEMAND_REALITY_FACTOR)

        # Minimum demand of 1 if city is viable
        if estimated_demand < 1 and margin_percent > self.MIN_RISKY_MARGIN:
            estimated_demand = 1

        # Total monthly profit
        total_monthly_profit = profit_per_unit * estimated_demand

        # Determine status
        status, icon = self._determine_status(margin_percent, estimated_demand)

        return CityProfitAnalysis(
            city_id=city_id,
            city_name=city.name,
            city_name_en=city.name_en,
            region=city.region,
            tier=city.tier,
            product_cost_kzt=round(product_cost_kzt, 2),
            logistics_cost_kzt=logistics_cost_kzt,
            total_cost_kzt=round(total_cost_kzt, 2),
            recommended_price_kzt=recommended_price_kzt,
            markup_percent=markup_percent,
            margin_percent=margin_percent,
            profit_per_unit_kzt=round(profit_per_unit, 2),
            estimated_monthly_demand=estimated_demand,
            total_monthly_profit_kzt=round(total_monthly_profit, 2),
            status=status,
            status_icon=icon,
            affordability_index=affordability,
            competition_factor=competition_factor,
            purchasing_power_index=city.purchasing_power_index,
        )

    def _determine_status(self, margin_percent: float, demand: int) -> tuple:
        """Determine profit status based on margin and demand"""
        if margin_percent >= self.MIN_PROFITABLE_MARGIN and demand >= 5:
            return ProfitStatus.PROFITABLE, "🟢"
        elif margin_percent >= self.MIN_RISKY_MARGIN and demand >= 2:
            return ProfitStatus.RISKY, "🟡"
        else:
            return ProfitStatus.UNPROFITABLE, "🔴"

    def analyze_all_cities(
        self,
        product_cost_usd: float,
        category: str,
        markup_percent: float = 25.0,
        product_name: str = "Product",
        shipping_cost_usd: float = 0.0,
        competitor_prices: Optional[List[float]] = None,
    ) -> RegionalAnalysisResult:
        """
        Analyze profitability across all Kazakhstan cities.

        Args:
            product_cost_usd: Wholesale price in USD
            category: Product category
            markup_percent: Desired markup percentage
            product_name: Product name for display
            shipping_cost_usd: International shipping cost per unit
            competitor_prices: Optional list of competitor prices in KZT

        Returns:
            RegionalAnalysisResult with full breakdown
        """
        cities = self.market_service.get_cities()
        currency_rate = self.market_service.get_currency_rate("USD")
        product_cost_kzt = product_cost_usd * currency_rate

        city_analyses = []
        best_cities = []
        avoid_cities = []
        risky_cities = []
        total_profit = 0.0
        total_demand = 0

        for city in cities:
            analysis = self.calculate_city_profit(
                product_cost_usd=product_cost_usd,
                category=category,
                city_id=city.id,
                markup_percent=markup_percent,
                shipping_cost_usd=shipping_cost_usd,
            )

            if analysis:
                city_analyses.append(analysis)
                total_profit += analysis.total_monthly_profit_kzt
                total_demand += analysis.estimated_monthly_demand

                if analysis.status == ProfitStatus.PROFITABLE:
                    best_cities.append(analysis.city_name)
                elif analysis.status == ProfitStatus.RISKY:
                    risky_cities.append(analysis.city_name)
                else:
                    avoid_cities.append(analysis.city_name)

        # Sort by profit
        city_analyses.sort(key=lambda x: x.total_monthly_profit_kzt, reverse=True)

        # Calculate wholesale recommendations
        recommended_qty, investment_usd, roi = self._calculate_wholesale_recommendation(
            city_analyses,
            product_cost_usd,
        )

        # === EXTENDED ANALYSIS ===

        # Investment Summary
        investment_kzt = investment_usd * currency_rate
        avg_profit_per_unit = total_profit / total_demand if total_demand > 0 else 0
        break_even_units = int(investment_kzt / avg_profit_per_unit) if avg_profit_per_unit > 0 else 0
        payback_months = investment_kzt / total_profit if total_profit > 0 else 999

        investment_summary = InvestmentSummary(
            total_investment_usd=investment_usd,
            total_investment_kzt=investment_kzt,
            shipping_cost_usd=shipping_cost_usd * recommended_qty,
            recommended_quantity=recommended_qty,
            expected_revenue_kzt=sum(c.recommended_price_kzt * c.estimated_monthly_demand for c in city_analyses if c.status == ProfitStatus.PROFITABLE),
            expected_profit_kzt=total_profit,
            roi_percent=roi,
            payback_months=payback_months,
            break_even_units=break_even_units,
        )

        # Risk Analysis
        risk_analysis = self._calculate_risk_analysis(
            city_analyses=city_analyses,
            product_cost_usd=product_cost_usd,
            category=category,
            currency_rate=currency_rate,
        )

        # Competitor Analysis (if prices provided)
        competitor_analysis = None
        if competitor_prices and len(competitor_prices) > 0:
            avg_competitor = sum(competitor_prices) / len(competitor_prices)
            our_avg_price = sum(c.recommended_price_kzt for c in city_analyses[:5]) / 5 if city_analyses else 0
            price_diff = ((our_avg_price - avg_competitor) / avg_competitor * 100) if avg_competitor > 0 else 0

            competitor_analysis = CompetitorAnalysis(
                avg_price_kzt=avg_competitor,
                min_price_kzt=min(competitor_prices),
                max_price_kzt=max(competitor_prices),
                our_price_vs_market=price_diff,
                price_position="below" if price_diff < -5 else "above" if price_diff > 5 else "at",
                competitor_count=len(competitor_prices),
                source="Kaspi.kz",
            )

        # Market Insights
        market_insights = self._generate_market_insights(category, product_name)

        # === WARNINGS ===
        warnings = []
        is_profitable = True

        # Check if we're more expensive than competitors
        if competitor_analysis:
            if competitor_analysis.our_price_vs_market > 20:
                warnings.append(f"⚠️ Твоя цена на {competitor_analysis.our_price_vs_market:.0f}% выше рынка - сложно конкурировать")
                is_profitable = False
            elif competitor_analysis.our_price_vs_market > 10:
                warnings.append(f"⚡ Цена на {competitor_analysis.our_price_vs_market:.0f}% выше рынка - нужны преимущества (гарантия, сервис)")

        # Check profitability
        if len(best_cities) == 0:
            warnings.append("🔴 Нет городов с хорошей маржой - товар не рекомендуется")
            is_profitable = False
        elif len(best_cities) < 3:
            warnings.append(f"🟡 Только {len(best_cities)} города с хорошей маржой")

        # Check if cost is too high
        if product_cost_usd > 1000:
            warnings.append("💰 Высокая стоимость товара - большие вложения и риски")

        # Check average margin
        avg_margin = sum(c.margin_percent for c in city_analyses) / len(city_analyses) if city_analyses else 0
        if avg_margin < 10:
            warnings.append(f"📉 Средняя маржа {avg_margin:.1f}% - слишком низкая для прибыльного бизнеса")
            is_profitable = False

        # Generate text recommendation
        recommendation = self._generate_recommendation(
            product_name=product_name,
            product_cost_usd=product_cost_usd,
            best_cities=best_cities[:3],
            avoid_cities=avoid_cities[:3],
            total_profit=total_profit,
            markup_percent=markup_percent,
            recommended_qty=recommended_qty,
            is_profitable=is_profitable,
        )

        return RegionalAnalysisResult(
            product_name=product_name,
            product_cost_usd=product_cost_usd,
            product_cost_kzt=round(product_cost_kzt, 2),
            currency_rate=currency_rate,
            category=category,
            cities=city_analyses,
            best_cities=best_cities[:5],
            avoid_cities=avoid_cities[:5],
            total_potential_profit_kzt=round(total_profit, 2),
            total_demand=total_demand,
            profitable_cities_count=len(best_cities),
            risky_cities_count=len(risky_cities),
            recommended_quantity=recommended_qty,
            recommended_investment_usd=round(investment_usd, 2),
            expected_roi_percent=roi,
            investment=investment_summary,
            risk_analysis=risk_analysis,
            competitor_analysis=competitor_analysis,
            market_insights=market_insights,
            warnings=warnings,
            is_profitable=is_profitable,
            recommendation=recommendation,
        )

    def _calculate_risk_analysis(
        self,
        city_analyses: List[CityProfitAnalysis],
        product_cost_usd: float,
        category: str,
        currency_rate: float,
    ) -> RiskAnalysis:
        """Calculate risk assessment"""
        factors = []
        risk_score = 0

        # Factor 1: Currency volatility
        if product_cost_usd > 500:
            risk_score += 20
            factors.append({
                "factor": "Курсовой риск",
                "level": "средний",
                "description": f"При изменении курса на 10% потеря ${product_cost_usd * 0.1:.0f}/шт"
            })
        else:
            factors.append({
                "factor": "Курсовой риск",
                "level": "низкий",
                "description": "Невысокая стоимость товара снижает валютные риски"
            })

        # Factor 2: Competition
        high_competition_cities = sum(1 for c in city_analyses if c.competition_factor < 0.4)
        if high_competition_cities >= 5:
            risk_score += 25
            factors.append({
                "factor": "Конкуренция",
                "level": "высокий",
                "description": f"Высокая конкуренция в {high_competition_cities} городах"
            })
        else:
            risk_score += 10
            factors.append({
                "factor": "Конкуренция",
                "level": "низкий",
                "description": "Умеренная конкуренция в большинстве городов"
            })

        # Factor 3: Margin risk
        low_margin_cities = sum(1 for c in city_analyses if c.margin_percent < 15)
        if low_margin_cities >= 10:
            risk_score += 30
            factors.append({
                "factor": "Маржинальность",
                "level": "высокий",
                "description": f"Низкая маржа (<15%) в {low_margin_cities} городах"
            })
        elif low_margin_cities >= 5:
            risk_score += 15
            factors.append({
                "factor": "Маржинальность",
                "level": "средний",
                "description": f"Средняя маржа в большинстве городов"
            })
        else:
            factors.append({
                "factor": "Маржинальность",
                "level": "низкий",
                "description": "Хорошая маржа в большинстве городов"
            })

        # Factor 4: Category risk
        category_risks = {
            "electronics": ("средний", 15, "Быстрое устаревание моделей"),
            "clothing": ("средний", 20, "Сезонность и размерные риски"),
            "food": ("высокий", 30, "Срок годности"),
            "beauty": ("низкий", 10, "Стабильный спрос"),
        }
        cat_info = category_risks.get(category.lower(), ("средний", 15, ""))
        risk_score += cat_info[1]
        if cat_info[2]:
            factors.append({
                "factor": f"Категория ({category})",
                "level": cat_info[0],
                "description": cat_info[2]
            })

        # Determine overall risk
        if risk_score >= 60:
            overall = "high"
        elif risk_score >= 35:
            overall = "medium"
        else:
            overall = "low"

        # Seasonality
        seasonality_notes = {
            "electronics": "📅 Пик продаж: ноябрь-декабрь (Новый год), август-сентябрь (школа)",
            "clothing": "📅 Пик: смена сезонов (март, сентябрь)",
            "beauty": "📅 Пик: 8 марта, Новый год",
            "kids": "📅 Пик: август-сентябрь (школа), Новый год",
        }

        return RiskAnalysis(
            overall_risk=overall,
            risk_score=risk_score,
            factors=factors,
            seasonality_note=seasonality_notes.get(category.lower(), "📅 Равномерный спрос в течение года"),
            currency_risk="USD/KZT волатильность ±5-10% в год",
            competition_risk=f"Высокая в Алматы/Астана, низкая в регионах",
        )

    def _generate_market_insights(self, category: str, product_name: str) -> MarketInsights:
        """Generate market insights based on category"""

        insights_by_category = {
            "electronics": {
                "best_months": ["Ноябрь", "Декабрь", "Август", "Сентябрь"],
                "kaspi": "💳 Рассрочка Kaspi Red увеличивает продажи на 40-60% для товаров >100,000₸",
                "audience": "👥 25-45 лет, средний доход+, городские жители",
                "tips": [
                    "Подключи Kaspi Магазин для доверия покупателей",
                    "Добавь гарантию 1 год - это критично для электроники",
                    "Делай распаковку/обзоры для Instagram/TikTok",
                    "Держи запас на складе в Алматы для быстрой доставки",
                ]
            },
            "clothing": {
                "best_months": ["Март", "Сентябрь", "Ноябрь", "Декабрь"],
                "kaspi": "💳 Рассрочка менее важна, но Kaspi Магазин обязателен",
                "audience": "👥 18-35 лет, женщины 70%, Instagram-аудитория",
                "tips": [
                    "Качественные фото - 80% успеха",
                    "Укажи размерную сетку и замеры",
                    "Предложи бесплатный возврат/обмен размера",
                    "Работай с блогерами для продвижения",
                ]
            },
            "beauty": {
                "best_months": ["Февраль", "Март", "Ноябрь", "Декабрь"],
                "kaspi": "💳 Рассрочка не критична для косметики",
                "audience": "👥 18-45 лет, 85% женщины",
                "tips": [
                    "Покажи сертификаты и срок годности",
                    "Делай бьюти-обзоры и tutorials",
                    "Предлагай наборы и комплекты со скидкой",
                    "8 марта - главная дата, готовься заранее",
                ]
            },
        }

        default_insights = {
            "best_months": ["Ноябрь", "Декабрь"],
            "kaspi": "💳 Kaspi Магазин увеличивает доверие покупателей",
            "audience": "👥 Широкая аудитория",
            "tips": [
                "Качественные фото и описания",
                "Быстрая доставка из Алматы",
                "Отвечай на вопросы быстро",
            ]
        }

        data = insights_by_category.get(category.lower(), default_insights)

        return MarketInsights(
            best_selling_months=data["best_months"],
            kaspi_installment_impact=data["kaspi"],
            target_audience=data["audience"],
            marketing_tips=data["tips"],
        )

    def _calculate_wholesale_recommendation(
        self,
        city_analyses: List[CityProfitAnalysis],
        product_cost_usd: float,
    ) -> tuple:
        """Calculate recommended wholesale quantity and investment"""
        # Sum demand from profitable cities only
        total_demand = sum(
            a.estimated_monthly_demand
            for a in city_analyses
            if a.status == ProfitStatus.PROFITABLE
        )

        # Recommend buying 80% of estimated demand (conservative)
        recommended_qty = int(total_demand * 0.8)

        # Investment needed
        investment_usd = recommended_qty * product_cost_usd

        # Calculate expected ROI
        expected_revenue = sum(
            a.total_monthly_profit_kzt
            for a in city_analyses
            if a.status == ProfitStatus.PROFITABLE
        )

        # ROI = (revenue - investment) / investment × 100
        investment_kzt = investment_usd * self.market_service.get_currency_rate("USD")
        roi = ((expected_revenue) / investment_kzt * 100) if investment_kzt > 0 else 0

        return recommended_qty, investment_usd, roi

    def _generate_recommendation(
        self,
        product_name: str,
        product_cost_usd: float,
        best_cities: List[str],
        avoid_cities: List[str],
        total_profit: float,
        markup_percent: float,
        recommended_qty: int,
        is_profitable: bool = True,
    ) -> str:
        """Generate human-readable recommendation"""

        if not is_profitable or not best_cities:
            return (
                f"🚫 **{product_name} НЕ РЕКОМЕНДУЕТСЯ** для продажи в Казахстане.\n\n"
                f"Причины:\n"
                f"• Оптовая цена ${product_cost_usd:.0f} слишком высокая\n"
                f"• Конкуренты на Kaspi продают дешевле\n"
                f"• Маржа не покрывает расходы\n\n"
                f"💡 Альтернативы:\n"
                f"• Найди поставщика с ценой ниже ${product_cost_usd * 0.7:.0f}\n"
                f"• Рассмотри другие товары с маржой >20%\n"
                f"• Попробуй аксессуары вместо основного товара"
            )

        # Format profit in millions/thousands
        if total_profit >= 1_000_000:
            profit_str = f"{total_profit / 1_000_000:.1f}M"
        else:
            profit_str = f"{total_profit / 1_000:.0f}K"

        cities_str = ", ".join(best_cities[:3])
        avoid_str = ", ".join(avoid_cities[:3]) if avoid_cities else "нет"

        return (
            f"✅ **{product_name} РЕКОМЕНДУЕТСЯ** для продажи!\n\n"
            f"📦 Закупка: {recommended_qty} шт по ${product_cost_usd:.0f}\n"
            f"🏙️ Продавай в: {cities_str}\n"
            f"💹 Наценка: {markup_percent}%\n"
            f"💰 Прибыль: {profit_str} тенге/месяц\n"
            f"⛔ Избегай: {avoid_str}"
        )

    async def analyze_product_from_search(
        self,
        product_name: str,
        category: str = "electronics",
        markup_percent: float = 25.0,
        apply_wholesale_discount: bool = True,
    ) -> RegionalAnalysisResult:
        """
        Full analysis pipeline: search for price, then calculate profits.

        Args:
            product_name: Product to search and analyze
            category: Product category
            markup_percent: Desired markup
            apply_wholesale_discount: Apply wholesale discount to found price

        Returns:
            RegionalAnalysisResult with web search data
        """
        # Get price from web search (usually retail price)
        price_info = await self.web_search.search_product_price(product_name)

        # Apply wholesale discount (search returns retail prices)
        if apply_wholesale_discount:
            product_cost_usd = self.apply_wholesale_discount(price_info.price_usd)
        else:
            product_cost_usd = price_info.price_usd

        # Run analysis
        result = self.analyze_all_cities(
            product_cost_usd=product_cost_usd,
            category=category,
            markup_percent=markup_percent,
            product_name=product_name,
        )

        # Store original retail price for reference
        result.retail_price_usd = price_info.price_usd
        result.wholesale_discount_applied = apply_wholesale_discount

        return result


# Singleton instance
profit_calculator = ProfitCalculatorService()
