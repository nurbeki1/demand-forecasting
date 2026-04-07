"""
Web Search Service

Provides real-time market data using Tavily API:
- Product wholesale prices (AliExpress, Amazon)
- Competitor prices (Kaspi.kz)
- Currency exchange rates
- Market trends

Requires: TAVILY_API_KEY environment variable
"""

from __future__ import annotations
import os
import re
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import httpx


@dataclass
class ProductPriceInfo:
    """Product price information from web search"""
    product_name: str
    price_usd: float
    price_range: Optional[Dict[str, float]]  # {"min": x, "max": y}
    source: str  # "aliexpress", "amazon", etc.
    url: Optional[str]
    currency: str
    found: bool
    search_query: str
    timestamp: str


@dataclass
class CompetitorPrice:
    """Competitor price on Kazakhstan market"""
    product_name: str
    price_kzt: float
    seller: str
    platform: str  # "kaspi", "olx", etc.
    url: Optional[str]
    rating: Optional[float]
    reviews_count: Optional[int]


@dataclass
class CurrencyRate:
    """Currency exchange rate"""
    currency: str
    rate_to_kzt: float
    source: str
    timestamp: str


@dataclass
class MarketTrend:
    """Market trend information"""
    category: str
    trend_direction: str  # "up", "down", "stable"
    trend_description: str
    key_products: List[str]
    source: str


class WebSearchService:
    """
    Web Search Service using Tavily API.

    Features:
    - Search for wholesale prices on global marketplaces
    - Get competitor prices on local marketplaces
    - Fetch current currency rates
    - Analyze market trends
    """

    TAVILY_API_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not self.api_key:
            print("Warning: TAVILY_API_KEY not set. Web search will return mock data.")

    async def _search(
        self,
        query: str,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        max_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute Tavily search.

        Args:
            query: Search query
            search_depth: "basic" or "advanced"
            include_domains: List of domains to search
            max_results: Maximum results to return
        """
        if not self.api_key:
            return self._mock_search_result(query)

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
        }

        if include_domains:
            payload["include_domains"] = include_domains

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.TAVILY_API_URL, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Tavily search error: {e}")
                return self._mock_search_result(query)

    def _mock_search_result(self, query: str) -> Dict[str, Any]:
        """Return mock search results when API is unavailable"""
        return {
            "results": [
                {
                    "title": f"Mock result for: {query}",
                    "url": "https://example.com",
                    "content": f"This is mock data for query: {query}. Price: $100-500",
                    "score": 0.9,
                }
            ],
            "query": query,
        }

    # =========================================================
    # PRODUCT PRICE SEARCH
    # =========================================================

    async def search_product_price(
        self,
        product_name: str,
        sources: Optional[List[str]] = None,
    ) -> ProductPriceInfo:
        """
        Search for wholesale price of a product.

        Args:
            product_name: Product name to search
            sources: List of sources to search (aliexpress, amazon, etc.)

        Returns:
            ProductPriceInfo with price data
        """
        if sources is None:
            sources = ["aliexpress", "amazon"]

        # Build search query
        query = f"{product_name} wholesale price USD"

        # Domain filtering
        domains = []
        if "aliexpress" in sources:
            domains.append("aliexpress.com")
        if "amazon" in sources:
            domains.append("amazon.com")

        result = await self._search(
            query=query,
            include_domains=domains if domains else None,
            max_results=5,
        )

        # Parse price from results
        price_usd, price_range, source, url = self._extract_price_from_results(
            result.get("results", []),
            product_name
        )

        return ProductPriceInfo(
            product_name=product_name,
            price_usd=price_usd,
            price_range=price_range,
            source=source,
            url=url,
            currency="USD",
            found=price_usd > 0,
            search_query=query,
            timestamp=datetime.now().isoformat(),
        )

    def _extract_price_from_results(
        self,
        results: List[Dict],
        product_name: str
    ) -> tuple:
        """Extract price information from search results"""
        prices = []
        source = "estimated"
        url = None

        for result in results:
            content = result.get("content", "") + " " + result.get("title", "")

            # Try to find price patterns
            # $XXX, USD XXX, $X,XXX.XX
            price_patterns = [
                r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'USD\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|\$)',
            ]

            for pattern in price_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    try:
                        price = float(match.replace(",", ""))
                        if 1 < price < 100000:  # Reasonable price range
                            prices.append(price)
                            if url is None:
                                url = result.get("url")
                                if "aliexpress" in (url or ""):
                                    source = "AliExpress"
                                elif "amazon" in (url or ""):
                                    source = "Amazon"
                    except ValueError:
                        pass

        if not prices:
            # Return estimated price based on product category
            estimated = self._estimate_price(product_name)
            return estimated, None, "estimated", None

        avg_price = sum(prices) / len(prices)
        price_range = {"min": min(prices), "max": max(prices)} if len(prices) > 1 else None

        return round(avg_price, 2), price_range, source, url

    def _estimate_price(self, product_name: str) -> float:
        """Estimate price based on product keywords"""
        name_lower = product_name.lower()

        # Price estimates by product type
        estimates = {
            "iphone": 800,
            "samsung galaxy": 600,
            "macbook": 1200,
            "airpods": 150,
            "xiaomi": 300,
            "headphones": 50,
            "watch": 200,
            "tablet": 400,
            "laptop": 700,
            "camera": 500,
            "tv": 400,
            "refrigerator": 600,
            "washing machine": 400,
        }

        for keyword, price in estimates.items():
            if keyword in name_lower:
                return float(price)

        return 100.0  # Default estimate

    # =========================================================
    # COMPETITOR PRICES
    # =========================================================

    async def get_competitor_prices(
        self,
        product_name: str,
        market: str = "kaspi",
    ) -> List[CompetitorPrice]:
        """
        Get competitor prices on local Kazakhstan marketplaces.

        Args:
            product_name: Product to search
            market: Marketplace (kaspi, olx)

        Returns:
            List of competitor prices
        """
        query = f"{product_name} цена site:kaspi.kz"

        result = await self._search(
            query=query,
            include_domains=["kaspi.kz"],
            max_results=5,
        )

        competitors = []
        for r in result.get("results", []):
            price_kzt = self._extract_kzt_price(r.get("content", ""))
            if price_kzt > 0:
                competitors.append(CompetitorPrice(
                    product_name=product_name,
                    price_kzt=price_kzt,
                    seller="Kaspi Seller",
                    platform="kaspi",
                    url=r.get("url"),
                    rating=None,
                    reviews_count=None,
                ))

        # If no results, add estimated competitor price
        if not competitors:
            estimated_usd = self._estimate_price(product_name)
            estimated_kzt = estimated_usd * 450 * 1.3  # 30% markup
            competitors.append(CompetitorPrice(
                product_name=product_name,
                price_kzt=round(estimated_kzt, -3),  # Round to thousands
                seller="Estimated",
                platform="kaspi",
                url=None,
                rating=None,
                reviews_count=None,
            ))

        return competitors

    def _extract_kzt_price(self, content: str) -> float:
        """Extract KZT price from content"""
        patterns = [
            r'(\d{1,3}(?:\s?\d{3})*)\s*(?:₸|тг|тенге|KZT)',
            r'(?:₸|тг|тенге|KZT)\s*(\d{1,3}(?:\s?\d{3})*)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match.replace(" ", "").replace(",", ""))
                    if 1000 < price < 10000000:  # Reasonable KZT range
                        return price
                except ValueError:
                    pass

        return 0.0

    # =========================================================
    # CURRENCY RATES
    # =========================================================

    async def get_currency_rate(self, currency: str = "USD") -> CurrencyRate:
        """
        Get current currency exchange rate to KZT.

        Args:
            currency: Currency code (USD, RUB, CNY, EUR)

        Returns:
            CurrencyRate with current rate
        """
        query = f"{currency} to KZT exchange rate today"

        result = await self._search(query=query, max_results=3)

        rate = self._extract_currency_rate(
            result.get("results", []),
            currency
        )

        return CurrencyRate(
            currency=currency,
            rate_to_kzt=rate,
            source="web_search" if rate != self._default_rate(currency) else "default",
            timestamp=datetime.now().isoformat(),
        )

    def _extract_currency_rate(self, results: List[Dict], currency: str) -> float:
        """Extract currency rate from search results"""
        for result in results:
            content = result.get("content", "")

            # Pattern: 1 USD = XXX KZT or XXX tenge
            patterns = [
                rf'1\s*{currency}\s*=?\s*(\d{{3,}}(?:[.,]\d+)?)\s*(?:KZT|тенге|₸)',
                rf'{currency}.*?(\d{{3,}}(?:[.,]\d+)?)\s*(?:KZT|тенге|₸)',
            ]

            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    try:
                        rate = float(match.group(1).replace(",", "."))
                        if 1 < rate < 10000:  # Reasonable rate
                            return round(rate, 2)
                    except ValueError:
                        pass

        return self._default_rate(currency)

    def _default_rate(self, currency: str) -> float:
        """Default currency rates"""
        defaults = {
            "USD": 450.0,
            "EUR": 490.0,
            "RUB": 5.0,
            "CNY": 62.0,
            "GBP": 570.0,
        }
        return defaults.get(currency.upper(), 450.0)

    # =========================================================
    # MARKET TRENDS
    # =========================================================

    async def get_market_trends(self, category: str) -> MarketTrend:
        """
        Get market trends for a category.

        Args:
            category: Product category (electronics, clothing, etc.)

        Returns:
            MarketTrend with trend information
        """
        query = f"{category} market trends Kazakhstan 2024"

        result = await self._search(query=query, max_results=3)

        # Analyze results for trend direction
        trend_info = self._analyze_trend(result.get("results", []), category)

        return MarketTrend(
            category=category,
            trend_direction=trend_info["direction"],
            trend_description=trend_info["description"],
            key_products=trend_info["products"],
            source="web_search",
        )

    def _analyze_trend(self, results: List[Dict], category: str) -> Dict:
        """Analyze search results for trend information"""
        content = " ".join([r.get("content", "") for r in results])

        # Simple keyword-based trend analysis
        positive_words = ["growth", "increase", "rising", "boom", "popular", "demand"]
        negative_words = ["decline", "decrease", "falling", "drop", "slow"]

        positive_count = sum(1 for w in positive_words if w in content.lower())
        negative_count = sum(1 for w in negative_words if w in content.lower())

        if positive_count > negative_count:
            direction = "up"
            description = f"Рынок {category} показывает рост в Казахстане"
        elif negative_count > positive_count:
            direction = "down"
            description = f"Рынок {category} замедляется"
        else:
            direction = "stable"
            description = f"Рынок {category} стабилен"

        # Default trending products by category
        trending = {
            "electronics": ["iPhone 15", "Samsung Galaxy S24", "AirPods Pro"],
            "clothing": ["Nike", "Adidas", "Zara"],
            "home": ["Xiaomi пылесос", "Dyson", "IKEA"],
            "beauty": ["Корейская косметика", "Dyson Airwrap"],
        }

        return {
            "direction": direction,
            "description": description,
            "products": trending.get(category, []),
        }


    # =========================================================
    # COMPREHENSIVE PRODUCT ANALYSIS
    # =========================================================

    async def search_product_info(self, product_name: str) -> Dict[str, Any]:
        """
        Get comprehensive product information.

        Returns:
            Dict with specs, description, variants, release info
        """
        query = f"{product_name} specifications features review"

        result = await self._search(query=query, max_results=5)

        info = {
            "product_name": product_name,
            "description": "",
            "specs": [],
            "key_features": [],
            "variants": [],
            "brand": "",
            "category": "",
        }

        for r in result.get("results", []):
            content = r.get("content", "")

            # Extract brand
            if not info["brand"]:
                brand_match = re.search(r"(?:by|from|brand:?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", content)
                if brand_match:
                    info["brand"] = brand_match.group(1)

            # Collect content for description
            if len(info["description"]) < 500:
                info["description"] += content[:200] + " "

        info["description"] = info["description"][:500].strip()

        return info

    async def search_product_reviews(self, product_name: str) -> Dict[str, Any]:
        """
        Get product reviews and rating analysis.

        Returns:
            Dict with rating, review count, pros, cons, common complaints
        """
        query = f"{product_name} reviews rating pros cons"

        result = await self._search(query=query, max_results=5)

        reviews = {
            "product_name": product_name,
            "avg_rating": 0.0,
            "review_count": 0,
            "rating_source": "estimated",
            "pros": [],
            "cons": [],
            "common_issues": [],
            "recommendation_rate": 0,
        }

        all_content = ""
        ratings = []

        for r in result.get("results", []):
            content = r.get("content", "")
            all_content += content + " "

            # Extract ratings (e.g., "4.5/5", "4.5 out of 5", "4.5 stars")
            rating_patterns = [
                r'(\d+\.?\d*)\s*/\s*5',
                r'(\d+\.?\d*)\s*out of\s*5',
                r'(\d+\.?\d*)\s*stars?',
                r'rating:?\s*(\d+\.?\d*)',
            ]

            for pattern in rating_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for m in matches:
                    try:
                        rating = float(m)
                        if 1 <= rating <= 5:
                            ratings.append(rating)
                    except:
                        pass

            # Extract review count
            count_match = re.search(r'(\d+(?:,\d+)*)\s*(?:reviews?|ratings?|отзыв)', content, re.IGNORECASE)
            if count_match and reviews["review_count"] == 0:
                try:
                    reviews["review_count"] = int(count_match.group(1).replace(",", ""))
                except:
                    pass

        if ratings:
            reviews["avg_rating"] = round(sum(ratings) / len(ratings), 1)
            reviews["rating_source"] = "web_search"

        # Extract pros/cons using keywords
        pros_keywords = ["excellent", "great", "love", "best", "amazing", "perfect", "good quality", "recommend"]
        cons_keywords = ["problem", "issue", "disappointing", "broken", "defect", "poor", "bad", "doesn't work"]

        for keyword in pros_keywords:
            if keyword in all_content.lower():
                reviews["pros"].append(keyword.title())

        for keyword in cons_keywords:
            if keyword in all_content.lower():
                reviews["cons"].append(keyword.title())

        reviews["pros"] = reviews["pros"][:5]
        reviews["cons"] = reviews["cons"][:5]

        # Estimate recommendation rate
        if reviews["avg_rating"] >= 4.5:
            reviews["recommendation_rate"] = 95
        elif reviews["avg_rating"] >= 4.0:
            reviews["recommendation_rate"] = 85
        elif reviews["avg_rating"] >= 3.5:
            reviews["recommendation_rate"] = 70
        else:
            reviews["recommendation_rate"] = 50

        return reviews

    async def search_demand_trends(self, product_name: str) -> Dict[str, Any]:
        """
        Analyze demand trends for a product.

        Returns:
            Dict with trend direction, search popularity, seasonality
        """
        query = f"{product_name} demand popularity trend 2024"

        result = await self._search(query=query, max_results=5)

        trends = {
            "product_name": product_name,
            "trend_direction": "stable",  # up, down, stable
            "popularity_score": 50,  # 0-100
            "search_interest": "medium",  # low, medium, high
            "seasonality": None,
            "peak_season": None,
            "trend_description": "",
        }

        all_content = " ".join([r.get("content", "") for r in result.get("results", [])])
        content_lower = all_content.lower()

        # Analyze trend direction
        positive_indicators = ["trending", "popular", "best seller", "high demand", "sold out", "growing", "increase"]
        negative_indicators = ["declining", "low demand", "outdated", "discontinued", "decrease", "dropping"]

        positive_count = sum(1 for ind in positive_indicators if ind in content_lower)
        negative_count = sum(1 for ind in negative_indicators if ind in content_lower)

        if positive_count > negative_count + 1:
            trends["trend_direction"] = "up"
            trends["popularity_score"] = min(90, 60 + positive_count * 5)
            trends["search_interest"] = "high"
        elif negative_count > positive_count + 1:
            trends["trend_direction"] = "down"
            trends["popularity_score"] = max(20, 50 - negative_count * 5)
            trends["search_interest"] = "low"
        else:
            trends["trend_direction"] = "stable"
            trends["popularity_score"] = 55
            trends["search_interest"] = "medium"

        # Check for seasonality mentions
        seasons = {
            "winter": ["winter", "christmas", "new year", "холод"],
            "summer": ["summer", "vacation", "лето"],
            "back to school": ["school", "september", "сентябрь"],
            "holiday": ["black friday", "cyber monday", "holiday", "christmas"],
        }

        for season, keywords in seasons.items():
            if any(kw in content_lower for kw in keywords):
                trends["seasonality"] = season
                break

        # Build trend description
        if trends["trend_direction"] == "up":
            trends["trend_description"] = f"{product_name} показывает растущий спрос"
        elif trends["trend_direction"] == "down":
            trends["trend_description"] = f"Спрос на {product_name} снижается"
        else:
            trends["trend_description"] = f"Спрос на {product_name} стабилен"

        return trends

    async def search_similar_products(self, product_name: str) -> List[Dict[str, Any]]:
        """
        Find similar/competing products.

        Returns:
            List of similar products with prices
        """
        query = f"{product_name} alternatives competitors similar products vs"

        result = await self._search(query=query, max_results=5)

        similar = []
        seen_products = set()

        # Common product patterns to extract
        product_patterns = [
            r"(?:vs|versus|or|alternative:?|competitor:?|similar:?)\s+([A-Z][a-z]+(?:\s+[A-Z0-9][a-z0-9]*){0,3})",
            r"([A-Z][a-z]+\s+[A-Z0-9][a-z0-9]*(?:\s+[A-Z0-9][a-z0-9]*)?)\s+(?:is|are)\s+(?:similar|alternative|competitor)",
        ]

        for r in result.get("results", []):
            content = r.get("content", "") + " " + r.get("title", "")

            for pattern in product_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    product = match.strip()
                    if (
                        product.lower() != product_name.lower()
                        and len(product) > 3
                        and product.lower() not in seen_products
                    ):
                        seen_products.add(product.lower())
                        similar.append({
                            "name": product,
                            "relation": "competitor",
                        })

        # Add some default competitors based on product type
        product_lower = product_name.lower()
        if "iphone" in product_lower:
            for p in ["Samsung Galaxy", "Google Pixel", "Xiaomi"]:
                if p.lower() not in seen_products:
                    similar.append({"name": p, "relation": "competitor"})
        elif "samsung" in product_lower:
            for p in ["iPhone", "Xiaomi", "OnePlus"]:
                if p.lower() not in seen_products:
                    similar.append({"name": p, "relation": "competitor"})
        elif "nike" in product_lower:
            for p in ["Adidas", "Puma", "New Balance"]:
                if p.lower() not in seen_products:
                    similar.append({"name": p, "relation": "competitor"})

        return similar[:5]

    async def comprehensive_product_analysis(self, product_name: str) -> Dict[str, Any]:
        """
        Run comprehensive analysis for a product using multiple searches.

        This is the main method for full product analysis.

        Returns:
            Complete analysis with prices, reviews, trends, competitors
        """
        # Run all searches in parallel
        results = await asyncio.gather(
            self.search_product_price(product_name),
            self.get_competitor_prices(product_name),
            self.search_product_reviews(product_name),
            self.search_demand_trends(product_name),
            self.search_similar_products(product_name),
            self.get_currency_rate("USD"),
            return_exceptions=True,
        )

        # Unpack results
        price_info = results[0] if not isinstance(results[0], Exception) else None
        competitors = results[1] if not isinstance(results[1], Exception) else []
        reviews = results[2] if not isinstance(results[2], Exception) else {}
        trends = results[3] if not isinstance(results[3], Exception) else {}
        similar = results[4] if not isinstance(results[4], Exception) else []
        currency = results[5] if not isinstance(results[5], Exception) else None

        # Calculate profitability
        wholesale_usd = price_info.price_usd if price_info else 0
        usd_rate = currency.rate_to_kzt if currency else 450
        wholesale_kzt = wholesale_usd * usd_rate

        competitor_prices = [c.price_kzt for c in competitors if c.price_kzt > 0]
        avg_retail_kzt = sum(competitor_prices) / len(competitor_prices) if competitor_prices else wholesale_kzt * 1.3

        potential_profit_kzt = avg_retail_kzt - wholesale_kzt
        profit_margin = (potential_profit_kzt / wholesale_kzt * 100) if wholesale_kzt > 0 else 0

        # Build risk assessment
        risks = []
        if trends.get("trend_direction") == "down":
            risks.append("Спрос снижается")
        if reviews.get("avg_rating", 5) < 4.0:
            risks.append(f"Низкий рейтинг: {reviews.get('avg_rating')}")
        if len(competitors) > 5:
            risks.append("Высокая конкуренция")
        if profit_margin < 15:
            risks.append("Низкая маржа")

        risk_level = "low" if len(risks) == 0 else "medium" if len(risks) <= 2 else "high"

        return {
            "product_name": product_name,
            "timestamp": datetime.now().isoformat(),

            # Pricing
            "wholesale_price_usd": wholesale_usd,
            "wholesale_price_kzt": round(wholesale_kzt, 0),
            "avg_retail_price_kzt": round(avg_retail_kzt, 0),
            "potential_profit_kzt": round(potential_profit_kzt, 0),
            "profit_margin_percent": round(profit_margin, 1),
            "price_source": price_info.source if price_info else "estimated",

            # Currency
            "usd_kzt_rate": usd_rate,

            # Competition
            "competitor_count": len(competitors),
            "competitor_prices": competitor_prices[:5],
            "similar_products": [s["name"] for s in similar],

            # Reviews & Rating
            "avg_rating": reviews.get("avg_rating", 0),
            "review_count": reviews.get("review_count", 0),
            "pros": reviews.get("pros", []),
            "cons": reviews.get("cons", []),
            "recommendation_rate": reviews.get("recommendation_rate", 0),

            # Demand & Trends
            "trend_direction": trends.get("trend_direction", "stable"),
            "popularity_score": trends.get("popularity_score", 50),
            "search_interest": trends.get("search_interest", "medium"),
            "seasonality": trends.get("seasonality"),
            "trend_description": trends.get("trend_description", ""),

            # Risk Assessment
            "risk_level": risk_level,
            "risks": risks,

            # Recommendation
            "recommendation": self._generate_recommendation(profit_margin, risk_level, trends.get("trend_direction")),
        }

    def _generate_recommendation(self, profit_margin: float, risk_level: str, trend: str) -> str:
        """Generate recommendation based on analysis"""
        if profit_margin > 30 and risk_level == "low" and trend == "up":
            return "Өте жақсы мүмкіндік! Сатуға кеңес беріледі."
        elif profit_margin > 20 and risk_level != "high":
            return "Жақсы мүмкіндік. Сатуға болады."
        elif profit_margin > 10:
            return "Орташа мүмкіндік. Мұқият талдаңыз."
        elif risk_level == "high":
            return "Жоғары тәуекел. Сақ болыңыз."
        else:
            return "Төмен маржа. Басқа өнімдерді қарастырыңыз."


# Singleton instance
web_search_service = WebSearchService()
