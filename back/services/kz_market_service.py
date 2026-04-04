"""
Kazakhstan Market Service

Provides access to Kazakhstan market data:
- Cities with economic indicators
- Logistics costs
- Currency rates
- Category information
"""

from __future__ import annotations
import json
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class City:
    """Kazakhstan city with economic data"""
    id: str
    name: str
    name_en: str
    region: str
    population: int
    avg_salary_kzt: float
    purchasing_power_index: float
    logistics_cost_from_almaty_kzt: float
    competition_level: str  # "high", "medium", "low"
    e_commerce_penetration: float
    tier: int  # 1, 2, 3
    coordinates: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_en": self.name_en,
            "region": self.region,
            "population": self.population,
            "avg_salary_kzt": self.avg_salary_kzt,
            "purchasing_power_index": self.purchasing_power_index,
            "logistics_cost_from_almaty_kzt": self.logistics_cost_from_almaty_kzt,
            "competition_level": self.competition_level,
            "e_commerce_penetration": self.e_commerce_penetration,
            "tier": self.tier,
            "coordinates": self.coordinates,
        }


@dataclass
class Category:
    """Product category with market characteristics"""
    id: str
    name_ru: str
    demand_multiplier: float
    typical_margin_percent: float
    price_sensitivity: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name_ru": self.name_ru,
            "demand_multiplier": self.demand_multiplier,
            "typical_margin_percent": self.typical_margin_percent,
            "price_sensitivity": self.price_sensitivity,
        }


class KZMarketService:
    """
    Kazakhstan Market Data Service

    Provides:
    - City economic data (population, salaries, purchasing power)
    - Logistics costs between cities
    - Currency conversion rates
    - Product category information
    """

    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            # Default path relative to this file
            current_dir = Path(__file__).parent.parent
            data_path = current_dir / "data" / "kz_cities.json"

        self._data_path = Path(data_path)
        self._data: Dict = {}
        self._cities: List[City] = []
        self._categories: Dict[str, Category] = {}
        self._load_data()

    def _load_data(self):
        """Load data from JSON file"""
        if not self._data_path.exists():
            raise FileNotFoundError(f"KZ market data not found: {self._data_path}")

        with open(self._data_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

        # Parse cities
        self._cities = [
            City(
                id=c["id"],
                name=c["name"],
                name_en=c["name_en"],
                region=c["region"],
                population=c["population"],
                avg_salary_kzt=c["avg_salary_kzt"],
                purchasing_power_index=c["purchasing_power_index"],
                logistics_cost_from_almaty_kzt=c["logistics_cost_from_almaty_kzt"],
                competition_level=c["competition_level"],
                e_commerce_penetration=c["e_commerce_penetration"],
                tier=c["tier"],
                coordinates=c["coordinates"],
            )
            for c in self._data.get("cities", [])
        ]

        # Parse categories
        for cat_id, cat_data in self._data.get("categories", {}).items():
            self._categories[cat_id] = Category(
                id=cat_id,
                name_ru=cat_data["name_ru"],
                demand_multiplier=cat_data["demand_multiplier"],
                typical_margin_percent=cat_data["typical_margin_percent"],
                price_sensitivity=cat_data["price_sensitivity"],
            )

    # =========================================================
    # CITIES
    # =========================================================

    def get_cities(self) -> List[City]:
        """Get all Kazakhstan cities"""
        return self._cities

    def get_cities_dict(self) -> List[Dict[str, Any]]:
        """Get all cities as dictionaries"""
        return [c.to_dict() for c in self._cities]

    def get_city_by_id(self, city_id: str) -> Optional[City]:
        """Get city by ID"""
        for city in self._cities:
            if city.id == city_id:
                return city
        return None

    def get_city_by_name(self, name: str) -> Optional[City]:
        """Get city by name (Russian or English)"""
        name_lower = name.lower()
        for city in self._cities:
            if city.name.lower() == name_lower or city.name_en.lower() == name_lower:
                return city
        return None

    def get_cities_by_tier(self, tier: int) -> List[City]:
        """Get cities by tier (1 = major, 2 = large, 3 = small)"""
        return [c for c in self._cities if c.tier == tier]

    def get_top_cities(self, limit: int = 5) -> List[City]:
        """Get top cities by purchasing power and population"""
        sorted_cities = sorted(
            self._cities,
            key=lambda c: c.purchasing_power_index * c.population,
            reverse=True
        )
        return sorted_cities[:limit]

    # =========================================================
    # LOGISTICS
    # =========================================================

    def get_logistics_cost(
        self,
        from_city: str,
        to_city: str,
        weight_kg: float = 1.0,
        is_express: bool = False,
        is_bulky: bool = False,
    ) -> float:
        """
        Calculate logistics cost between cities.

        Args:
            from_city: Origin city ID (default: almaty)
            to_city: Destination city ID
            weight_kg: Package weight in kg
            is_express: Use express delivery
            is_bulky: Bulky item requiring special handling

        Returns:
            Logistics cost in KZT
        """
        # Currently only from Almaty is supported
        to_city_obj = self.get_city_by_id(to_city)
        if to_city_obj is None:
            return 0.0

        # Base cost from Almaty
        base_cost = to_city_obj.logistics_cost_from_almaty_kzt

        # Weight-based cost
        logistics_config = self._data.get("logistics", {})
        per_kg_cost = logistics_config.get("base_cost_per_kg_kzt", 150)
        weight_cost = per_kg_cost * max(weight_kg - 1, 0)  # First kg included

        total = base_cost + weight_cost

        # Express multiplier
        if is_express:
            express_mult = logistics_config.get("express_multiplier", 2.5)
            total *= express_mult

        # Bulky surcharge
        if is_bulky:
            bulky_surcharge = logistics_config.get("bulky_item_surcharge_kzt", 5000)
            total += bulky_surcharge

        return round(total, 2)

    # =========================================================
    # CURRENCY
    # =========================================================

    def get_currency_rate(self, currency: str = "USD") -> float:
        """
        Get currency exchange rate to KZT.

        Args:
            currency: Currency code (USD, RUB, CNY)

        Returns:
            Exchange rate (1 unit = X KZT)
        """
        currency_data = self._data.get("currency", {})

        key = f"{currency.lower()}_to_kzt"
        return currency_data.get(key, 450.0)  # Default USD rate

    def convert_to_kzt(self, amount: float, currency: str = "USD") -> float:
        """Convert amount to KZT"""
        rate = self.get_currency_rate(currency)
        return round(amount * rate, 2)

    def get_all_currency_rates(self) -> Dict[str, float]:
        """Get all available currency rates"""
        currency_data = self._data.get("currency", {})
        return {
            "USD": currency_data.get("usd_to_kzt", 450),
            "RUB": currency_data.get("rub_to_kzt", 5),
            "CNY": currency_data.get("cny_to_kzt", 62),
        }

    # =========================================================
    # CATEGORIES
    # =========================================================

    def get_categories(self) -> List[Category]:
        """Get all product categories"""
        return list(self._categories.values())

    def get_category(self, category_id: str) -> Optional[Category]:
        """Get category by ID"""
        return self._categories.get(category_id)

    def get_category_demand_multiplier(self, category_id: str) -> float:
        """Get demand multiplier for category"""
        cat = self.get_category(category_id)
        return cat.demand_multiplier if cat else 1.0

    def get_typical_margin(self, category_id: str) -> float:
        """Get typical margin percent for category"""
        cat = self.get_category(category_id)
        return cat.typical_margin_percent if cat else 25.0

    # =========================================================
    # PURCHASING POWER
    # =========================================================

    def get_purchasing_power(self, city_id: str) -> float:
        """Get purchasing power index for city (1.0 = Almaty baseline)"""
        city = self.get_city_by_id(city_id)
        return city.purchasing_power_index if city else 0.5

    def get_affordability_index(self, city_id: str, price_kzt: float) -> float:
        """
        Calculate affordability index for a price in a city.

        Returns:
            0-1 where 1 = very affordable, 0 = unaffordable
        """
        city = self.get_city_by_id(city_id)
        if city is None:
            return 0.5

        # Price as percentage of monthly salary
        price_to_salary = price_kzt / city.avg_salary_kzt

        if price_to_salary <= 0.05:  # 5% of salary
            return 1.0
        elif price_to_salary <= 0.10:  # 10%
            return 0.9
        elif price_to_salary <= 0.20:  # 20%
            return 0.7
        elif price_to_salary <= 0.50:  # 50%
            return 0.4
        elif price_to_salary <= 1.0:  # 100%
            return 0.2
        else:
            return 0.1

    # =========================================================
    # MARKET ANALYSIS HELPERS
    # =========================================================

    def estimate_market_size(self, city_id: str, category: str) -> int:
        """
        Estimate monthly market size (potential customers) for category in city.

        Simple heuristic based on:
        - Population
        - E-commerce penetration
        - Category demand multiplier
        - Purchasing power
        """
        city = self.get_city_by_id(city_id)
        if city is None:
            return 0

        cat = self.get_category(category)
        demand_mult = cat.demand_multiplier if cat else 1.0

        # Base: 1% of population shops online for this category monthly
        base_customers = city.population * 0.01

        # Adjust by e-commerce penetration
        adjusted = base_customers * city.e_commerce_penetration

        # Adjust by category demand
        adjusted *= demand_mult

        # Adjust by purchasing power
        adjusted *= city.purchasing_power_index

        return int(adjusted)

    def get_competition_factor(self, city_id: str) -> float:
        """
        Get competition factor (affects achievable market share).

        Returns:
            0.3-1.0 where higher = less competition
        """
        city = self.get_city_by_id(city_id)
        if city is None:
            return 0.5

        competition_factors = {
            "high": 0.3,    # Almaty, Astana - many competitors
            "medium": 0.5,  # Regional centers
            "low": 0.7,     # Small cities - less competition
        }

        return competition_factors.get(city.competition_level, 0.5)


# Singleton instance
kz_market_service = KZMarketService()
