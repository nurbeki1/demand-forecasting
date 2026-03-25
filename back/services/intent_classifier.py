"""
Intent Classifier for AI Chat
Classifies user messages into intents and extracts entities
"""
import re
from typing import Tuple, Dict, List, Any, Optional
from enum import Enum


class Intent(str, Enum):
    FORECAST = "forecast"
    PRODUCT_INFO = "product_info"
    PRODUCT_SEARCH = "product_search"  # NEW: Search by product name
    PRODUCT_ANALYSIS = "product_analysis"  # NEW: Full comprehensive analysis
    COMPARISON = "comparison"
    TRENDS = "trends"
    RECOMMENDATIONS = "recommendations"
    CATEGORY_STATS = "category_stats"
    REGION_STATS = "region_stats"
    SEASONALITY = "seasonality"
    WEATHER_IMPACT = "weather_impact"
    TOP_PRODUCTS = "top_products"
    LOW_PERFORMERS = "low_performers"
    DATASET_INFO = "dataset_info"
    SMART_FORECAST = "smart_forecast"  # NEW: Forecast with factors
    GENERAL = "general"


# Patterns for intent classification
INTENT_PATTERNS = {
    Intent.FORECAST: [
        r"прогноз",
        r"forecast",
        r"predict",
        r"предсказ",
        r"на (\d+) (дн|day)",
        r"что будет",
        r"ожида",
        r"спрогнозируй",
    ],
    Intent.PRODUCT_INFO: [
        r"что знаешь о",
        r"расскажи о",
        r"информаци[яю] о",
        r"info about",
        r"tell me about",
        r"what (is|about)",
        r"подробнее о",
        r"данные (по|о)",
    ],
    Intent.PRODUCT_ANALYSIS: [
        r"полный анализ",
        r"анализ продукт",
        r"full analysis",
        r"comprehensive",
        r"analyze",
        r"проанализируй",
        r"всё (о|про)",
        r"все (о|про)",
        r"детальн",
        r"подробн",
    ],
    Intent.SMART_FORECAST: [
        r"умный прогноз",
        r"smart forecast",
        r"прогноз с факторами",
        r"точный прогноз",
        r"детальный прогноз",
        r"advanced forecast",
    ],
    Intent.COMPARISON: [
        r"сравни",
        r"compare",
        r"vs\.?",
        r"versus",
        r"difference",
        r"разниц",
        r"отличи",
        r"лучше.*или",
        r"что лучше",
        r"между",
    ],
    Intent.TRENDS: [
        r"тренд",
        r"trend",
        r"динамик",
        r"изменен",
        r"растёт|растет",
        r"падает|снижает",
        r"рост|падени",
        r"growth|decline",
    ],
    Intent.RECOMMENDATIONS: [
        r"посовет",
        r"рекоменд",
        r"recommend",
        r"suggest",
        r"что делать",
        r"как улучшить",
        r"совет",
        r"advice",
        r"помоги",
        r"help me",
    ],
    Intent.CATEGORY_STATS: [
        r"категори[яю]",
        r"category",
        r"electronics",
        r"clothing",
        r"food",
        r"по категории",
        r"статистик[ау] (по )?категори",
    ],
    Intent.REGION_STATS: [
        r"регион",
        r"region",
        r"east|west|north|south",
        r"восток|запад|север|юг",
        r"по региону",
        r"в регионе",
        r"продажи в",
    ],
    Intent.SEASONALITY: [
        r"сезон",
        r"season",
        r"зима|весна|лето|осень",
        r"winter|spring|summer|fall|autumn",
        r"сезонност",
        r"seasonal",
    ],
    Intent.WEATHER_IMPACT: [
        r"погод",
        r"weather",
        r"дождь|снег|солнц",
        r"rain|snow|sunny|cloudy",
        r"влияние погоды",
    ],
    Intent.TOP_PRODUCTS: [
        r"топ|top",
        r"лучши[ех]",
        r"best",
        r"популярн",
        r"popular",
        r"лидер",
        r"хорошо продаётся|продается",
    ],
    Intent.LOW_PERFORMERS: [
        r"плох[ои]",
        r"худши[ех]",
        r"worst",
        r"проблемн",
        r"не продаётся|не продается",
        r"упал|снизил",
        r"declining",
        r"слаб",
    ],
    Intent.DATASET_INFO: [
        r"датасет|dataset",
        r"сколько (всего|продуктов|записей)",
        r"общая информаци",
        r"overview",
        r"обзор",
        r"какие (есть )?продукт",
        r"какие (есть )?категори",
        r"какие (есть )?регион",
    ],
}

# Patterns for entity extraction
PRODUCT_ID_PATTERN = re.compile(r"P\d{4}", re.IGNORECASE)
DAYS_PATTERN = re.compile(r"(\d+)\s*(дн|day|дней|days?)", re.IGNORECASE)
NUMBER_PATTERN = re.compile(r"\b(\d+)\b")

CATEGORIES = ["electronics", "clothing", "food", "home", "sports", "beauty"]
REGIONS = ["east", "west", "north", "south"]

# Known product brand/name patterns for search
PRODUCT_NAME_PATTERNS = [
    # Phones
    r"iphone\s*\d*\s*(pro|max|plus)?",
    r"айфон\s*\d*\s*(про|макс|плюс)?",
    r"samsung\s*(galaxy)?",
    r"самсунг",
    r"xiaomi|сяоми",
    r"pixel\s*\d*",
    r"huawei",
    # Laptops/Computers
    r"macbook\s*(pro|air)?",
    r"макбук",
    r"laptop|ноутбук",
    r"dell|hp|lenovo|asus|acer",
    # Headphones/Audio
    r"airpods?\s*(pro)?",
    r"наушники",
    r"headphones?",
    r"earbuds?",
    r"boult|jbl|sony",
    # TV
    r"телевизор|tv\b",
    r"lg\s*(tv|телевизор)?",
    # Appliances
    r"кондиционер|air\s*conditioner",
    r"холодильник|refrigerator",
    r"стиральн|washing\s*machine",
    # Clothing/Shoes
    r"nike|найк",
    r"adidas|адидас",
    r"кроссовки|sneakers?|shoes?",
    # General tech
    r"playstation|ps\s*\d|xbox",
    r"ipad|айпад",
    r"watch|часы",
    r"camera|камера",
    r"printer|принтер",
]

PRODUCT_NAME_REGEX = re.compile("|".join(PRODUCT_NAME_PATTERNS), re.IGNORECASE)


def extract_product_ids(text: str) -> List[str]:
    """Extract all product IDs from text"""
    matches = PRODUCT_ID_PATTERN.findall(text)
    return [m.upper() for m in matches]


def extract_product_name(text: str) -> Optional[str]:
    """Extract product name/brand from text for search"""
    match = PRODUCT_NAME_REGEX.search(text)
    if match:
        return match.group(0).strip()
    return None


def extract_days(text: str, default: int = 7) -> int:
    """Extract number of days from text"""
    match = DAYS_PATTERN.search(text)
    if match:
        return int(match.group(1))

    # Try to find standalone numbers that might be days
    numbers = NUMBER_PATTERN.findall(text)
    for num in numbers:
        n = int(num)
        if 1 <= n <= 365:
            return n

    return default


def extract_category(text: str) -> Optional[str]:
    """Extract category from text"""
    text_lower = text.lower()
    for cat in CATEGORIES:
        if cat in text_lower:
            return cat.capitalize()
    return None


def extract_region(text: str) -> Optional[str]:
    """Extract region from text"""
    text_lower = text.lower()

    # Russian to English mapping
    region_map = {
        "восток": "east",
        "запад": "west",
        "север": "north",
        "юг": "south",
    }

    for ru, en in region_map.items():
        if ru in text_lower:
            return en.capitalize()

    for region in REGIONS:
        if region in text_lower:
            return region.capitalize()

    return None


def extract_top_n(text: str, default: int = 5) -> int:
    """Extract 'top N' number from text"""
    match = re.search(r"(?:топ|top)[-\s]?(\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # Check for simple numbers
    match = re.search(r"\b(\d+)\s+(?:лучших|худших|продуктов|best|worst|products)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    return default


def extract_comparison_queries(text: str) -> List[str]:
    """
    Extract product names for comparison from text.
    E.g., "compare iPhone and Samsung" -> ["iPhone", "Samsung"]
    E.g., "iPhone vs Samsung Galaxy" -> ["iPhone", "Samsung Galaxy"]
    """
    queries = []

    # Pattern for "X vs Y" or "X versus Y"
    vs_match = re.search(r"(.+?)\s+(?:vs\.?|versus|или|or)\s+(.+?)(?:\s*$|\s+(?:что|which|какой))", text, re.IGNORECASE)
    if vs_match:
        queries.append(vs_match.group(1).strip())
        queries.append(vs_match.group(2).strip())
        return queries

    # Pattern for "compare X and Y" or "сравни X и Y"
    compare_match = re.search(r"(?:compare|сравни|сравнить)\s+(.+?)\s+(?:and|и|with|с)\s+(.+?)(?:\s*$|\s+(?:что|which|какой))", text, re.IGNORECASE)
    if compare_match:
        queries.append(compare_match.group(1).strip())
        queries.append(compare_match.group(2).strip())
        return queries

    # Pattern for "X and Y comparison" or "X и Y сравнение"
    and_match = re.search(r"(.+?)\s+(?:and|и)\s+(.+?)\s+(?:comparison|сравнение)", text, re.IGNORECASE)
    if and_match:
        queries.append(and_match.group(1).strip())
        queries.append(and_match.group(2).strip())
        return queries

    # Extract known product names if found
    matches = list(PRODUCT_NAME_REGEX.finditer(text))
    if len(matches) >= 2:
        for match in matches[:4]:
            queries.append(match.group(0).strip())

    return queries


def classify_intent(message: str) -> Tuple[Intent, Dict[str, Any]]:
    """
    Classify user intent and extract entities

    Returns:
        Tuple of (Intent, entities dict)
    """
    message_lower = message.lower()
    entities: Dict[str, Any] = {}

    # Extract entities first
    product_ids = extract_product_ids(message)
    if product_ids:
        entities["product_ids"] = product_ids

    # Extract product name for search (e.g., "iPhone 14 Pro", "наушники Boult")
    product_name = extract_product_name(message)
    if product_name:
        entities["search_query"] = product_name

    days = extract_days(message)
    entities["days"] = days  # Always include days

    category = extract_category(message)
    if category:
        entities["category"] = category

    region = extract_region(message)
    if region:
        entities["region"] = region

    top_n = extract_top_n(message)
    if top_n != 5:  # Only add if not default
        entities["top_n"] = top_n

    # Score each intent
    intent_scores: Dict[Intent, int] = {intent: 0 for intent in Intent}

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                intent_scores[intent] += 1

    # Get best matching intent
    best_intent = max(intent_scores, key=intent_scores.get)

    # IMPORTANT: Check for comparison first - it has priority over product search
    # "сравни iPhone и Samsung" should be COMPARISON, not PRODUCT_SEARCH
    if intent_scores[Intent.COMPARISON] > 0:
        best_intent = Intent.COMPARISON
    # If product name found but no product_id, use PRODUCT_SEARCH
    # This handles queries like "инфо об айфон 14 про" or "найди Samsung Galaxy"
    elif product_name and not product_ids:
        # Product name detected - this is a search request
        best_intent = Intent.PRODUCT_SEARCH
    elif intent_scores[best_intent] == 0:
        # No patterns matched, determine by entities
        if len(product_ids) >= 2:
            best_intent = Intent.COMPARISON
        elif len(product_ids) == 1:
            best_intent = Intent.PRODUCT_INFO
        elif category:
            best_intent = Intent.CATEGORY_STATS
        elif region:
            best_intent = Intent.REGION_STATS
        else:
            # No patterns and no entities - might be a product name search
            # Mark as PRODUCT_SEARCH if message looks like a product name
            words = message.strip().split()
            if 1 <= len(words) <= 6 and not any(w in message_lower for w in ['привет', 'hello', 'hi', 'как дела', 'что']):
                best_intent = Intent.PRODUCT_SEARCH
                entities["search_query"] = message.strip()
            else:
                best_intent = Intent.GENERAL

    # Special case: multiple products often means comparison
    if len(product_ids) >= 2 and best_intent not in [Intent.COMPARISON, Intent.FORECAST]:
        # Check if comparison is also mentioned
        if intent_scores[Intent.COMPARISON] > 0 or intent_scores[best_intent] <= 1:
            best_intent = Intent.COMPARISON

    # For COMPARISON intent, extract comparison queries
    if best_intent == Intent.COMPARISON:
        comparison_queries = extract_comparison_queries(message)
        if comparison_queries:
            entities["comparison_queries"] = comparison_queries
            # If no search_query set, use first comparison query
            if "search_query" not in entities:
                entities["search_query"] = comparison_queries[0]

    return best_intent, entities


def get_intent_description(intent: Intent) -> str:
    """Get human-readable description of intent"""
    descriptions = {
        Intent.FORECAST: "Generate demand forecast",
        Intent.PRODUCT_INFO: "Get product information",
        Intent.COMPARISON: "Compare products or regions",
        Intent.TRENDS: "Analyze trends",
        Intent.RECOMMENDATIONS: "Get recommendations",
        Intent.CATEGORY_STATS: "Category statistics",
        Intent.REGION_STATS: "Region statistics",
        Intent.SEASONALITY: "Seasonality analysis",
        Intent.WEATHER_IMPACT: "Weather impact analysis",
        Intent.TOP_PRODUCTS: "Top performing products",
        Intent.LOW_PERFORMERS: "Low performing products",
        Intent.DATASET_INFO: "Dataset overview",
        Intent.GENERAL: "General question",
    }
    return descriptions.get(intent, "Unknown intent")


def get_follow_up_suggestions(intent: Intent, entities: Dict[str, Any]) -> List[str]:
    """Generate follow-up suggestions based on intent and entities"""
    suggestions = []

    product_ids = entities.get("product_ids", [])
    search_query = entities.get("search_query", "")

    if intent == Intent.FORECAST and product_ids:
        suggestions.append(f"Сезонность {product_ids[0]}")
        suggestions.append(f"Влияние погоды на {product_ids[0]}")
        suggestions.append(f"Сравни {product_ids[0]} с другими")
        suggestions.append(f"Умный прогноз {product_ids[0]} на 14 дней")

    elif intent == Intent.PRODUCT_INFO and product_ids:
        suggestions.append(f"Полный анализ {product_ids[0]}")
        suggestions.append(f"Прогноз для {product_ids[0]} на 14 дней")
        suggestions.append(f"Тренды {product_ids[0]}")
        suggestions.append("Топ-5 продуктов")

    elif intent == Intent.PRODUCT_SEARCH:
        suggestions.append("Samsung Galaxy")
        suggestions.append("Nike Air Max")
        suggestions.append("MacBook Pro")
        suggestions.append("Топ-5 продуктов")

    elif intent == Intent.PRODUCT_ANALYSIS and product_ids:
        suggestions.append(f"Умный прогноз {product_ids[0]}")
        suggestions.append(f"Сравни {product_ids[0]} с конкурентами")
        suggestions.append("Рекомендации")

    elif intent == Intent.SMART_FORECAST and product_ids:
        suggestions.append(f"Полный анализ {product_ids[0]}")
        suggestions.append("Какие факторы влияют?")
        suggestions.append("Рекомендации по запасам")

    elif intent == Intent.COMPARISON:
        suggestions.append("Что посоветуешь?")
        suggestions.append("Топ-5 по росту")
        suggestions.append("Какие тренды?")

    elif intent == Intent.CATEGORY_STATS:
        category = entities.get("category")
        if category:
            suggestions.append(f"Топ продуктов в {category}")
            suggestions.append(f"Тренды в {category}")
        suggestions.append("Сравни категории")

    elif intent == Intent.REGION_STATS:
        suggestions.append("Сравни регионы")
        suggestions.append("Топ регион по продажам")

    elif intent in [Intent.TOP_PRODUCTS, Intent.LOW_PERFORMERS]:
        suggestions.append("Что посоветуешь?")
        suggestions.append("iPhone 15")
        suggestions.append("Сравни East и West")

    else:
        suggestions.append("iPhone 15")
        suggestions.append("Samsung Galaxy")
        suggestions.append("Топ-5 продуктов")
        suggestions.append("Какие категории есть?")

    return suggestions[:4]  # Max 4 suggestions
