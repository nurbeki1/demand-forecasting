"""
Test cases for Intent Classifier
"""
import pytest
from services.intent_classifier import (
    classify_intent,
    Intent,
    extract_product_ids,
    extract_days,
    extract_category,
    extract_region,
    extract_top_n,
    get_follow_up_suggestions,
)


class TestExtractProductIds:
    """Tests for extract_product_ids()"""

    def test_single_product_uppercase(self):
        """Should extract uppercase product ID"""
        result = extract_product_ids("Forecast for P0001")
        assert result == ["P0001"]

    def test_single_product_lowercase(self):
        """Should extract lowercase product ID and convert to upper"""
        result = extract_product_ids("forecast for p0001")
        assert result == ["P0001"]

    def test_multiple_products(self):
        """Should extract multiple product IDs"""
        result = extract_product_ids("Compare P0001 and P0002")
        assert "P0001" in result
        assert "P0002" in result

    def test_no_product(self):
        """Should return empty list when no product"""
        result = extract_product_ids("What are the trends?")
        assert result == []

    def test_product_in_sentence(self):
        """Should find product ID anywhere in sentence"""
        result = extract_product_ids("Tell me about the product P0003 please")
        assert result == ["P0003"]


class TestExtractDays:
    """Tests for extract_days()"""

    def test_with_days_word(self):
        """Should extract days with 'days' word"""
        assert extract_days("Forecast for 7 days") == 7
        assert extract_days("Predict for 14 days") == 14

    def test_with_day_word(self):
        """Should extract with 'day' word"""
        assert extract_days("Forecast for 1 day") == 1

    def test_russian_days(self):
        """Should extract Russian 'дней'"""
        assert extract_days("Прогноз на 7 дней") == 7

    def test_default_value(self):
        """Should return default when no days found"""
        assert extract_days("What is the forecast?") == 7
        assert extract_days("What is the forecast?", default=10) == 10

    def test_standalone_number(self):
        """Should extract standalone reasonable numbers"""
        result = extract_days("Forecast P0001 30")
        assert result == 30


class TestExtractCategory:
    """Tests for extract_category()"""

    def test_electronics(self):
        """Should extract Electronics category"""
        assert extract_category("Stats for Electronics") == "Electronics"

    def test_case_insensitive(self):
        """Should be case insensitive"""
        assert extract_category("stats for electronics") == "Electronics"
        assert extract_category("ELECTRONICS category") == "Electronics"

    def test_no_category(self):
        """Should return None when no category"""
        assert extract_category("What are the trends?") is None

    def test_multiple_categories(self):
        """Should return first matched category"""
        result = extract_category("electronics and clothing")
        assert result in ["Electronics", "Clothing"]


class TestExtractRegion:
    """Tests for extract_region()"""

    def test_english_regions(self):
        """Should extract English region names"""
        assert extract_region("Sales in East") == "East"
        assert extract_region("Sales in West") == "West"
        assert extract_region("Sales in North") == "North"
        assert extract_region("Sales in South") == "South"

    def test_russian_regions(self):
        """Should extract Russian region names"""
        assert extract_region("Продажи на востоке") == "East"
        assert extract_region("Продажи на западе") == "West"

    def test_case_insensitive(self):
        """Should be case insensitive"""
        assert extract_region("sales in EAST") == "East"

    def test_no_region(self):
        """Should return None when no region"""
        assert extract_region("What are the trends?") is None


class TestExtractTopN:
    """Tests for extract_top_n()"""

    def test_top_n_format(self):
        """Should extract top-N format"""
        assert extract_top_n("Top 5 products") == 5
        assert extract_top_n("top-10 items") == 10

    def test_with_best_word(self):
        """Should extract N from 'N best products'"""
        assert extract_top_n("5 best products") == 5

    def test_default_value(self):
        """Should return default when no N found"""
        assert extract_top_n("Show top products") == 5


class TestClassifyIntentForecast:
    """Tests for FORECAST intent classification"""

    def test_forecast_english(self):
        """Should classify English forecast requests"""
        intent, _ = classify_intent("Forecast for P0001")
        assert intent == Intent.FORECAST

    def test_forecast_russian(self):
        """Should classify Russian forecast requests"""
        intent, _ = classify_intent("Прогноз для P0001")
        assert intent == Intent.FORECAST

    def test_predict_keyword(self):
        """Should classify 'predict' as forecast"""
        intent, _ = classify_intent("Predict demand for P0001")
        assert intent == Intent.FORECAST

    def test_forecast_with_days(self):
        """Should extract days for forecast"""
        intent, entities = classify_intent("Forecast P0001 for 14 days")
        assert intent == Intent.FORECAST
        assert entities.get("days") == 14
        assert "P0001" in entities.get("product_ids", [])


class TestClassifyIntentProductInfo:
    """Tests for PRODUCT_INFO intent classification"""

    def test_info_english(self):
        """Should classify product info requests"""
        intent, _ = classify_intent("Tell me about P0001")
        assert intent == Intent.PRODUCT_INFO

    def test_info_russian(self):
        """Should classify Russian info requests"""
        intent, _ = classify_intent("Что знаешь о P0001?")
        assert intent == Intent.PRODUCT_INFO

    def test_info_what_is(self):
        """Should classify 'what is' questions"""
        intent, _ = classify_intent("What is P0001?")
        assert intent == Intent.PRODUCT_INFO


class TestClassifyIntentComparison:
    """Tests for COMPARISON intent classification"""

    def test_compare_english(self):
        """Should classify comparison requests"""
        intent, _ = classify_intent("Compare P0001 and P0002")
        assert intent == Intent.COMPARISON

    def test_compare_russian(self):
        """Should classify Russian comparison"""
        intent, _ = classify_intent("Сравни P0001 и P0002")
        assert intent == Intent.COMPARISON

    def test_vs_comparison(self):
        """Should classify 'vs' comparison"""
        intent, _ = classify_intent("P0001 vs P0002")
        assert intent == Intent.COMPARISON

    def test_multiple_products_as_comparison(self):
        """Multiple products should suggest comparison"""
        intent, entities = classify_intent("P0001 P0002 P0003")
        assert intent == Intent.COMPARISON
        assert len(entities.get("product_ids", [])) == 3


class TestClassifyIntentTrends:
    """Tests for TRENDS intent classification"""

    def test_trends_english(self):
        """Should classify trend requests"""
        intent, _ = classify_intent("What are the trends?")
        assert intent == Intent.TRENDS

    def test_trends_russian(self):
        """Should classify Russian trend requests"""
        intent, _ = classify_intent("Какие тренды?")
        assert intent == Intent.TRENDS

    def test_growth_decline(self):
        """Should classify growth/decline as trends"""
        intent, _ = classify_intent("Какой тренд роста?")
        assert intent == Intent.TRENDS


class TestClassifyIntentRecommendations:
    """Tests for RECOMMENDATIONS intent classification"""

    def test_recommend_english(self):
        """Should classify recommendation requests"""
        intent, _ = classify_intent("What do you recommend?")
        assert intent == Intent.RECOMMENDATIONS

    def test_recommend_russian(self):
        """Should classify Russian recommendations"""
        intent, _ = classify_intent("Что посоветуешь?")
        assert intent == Intent.RECOMMENDATIONS

    def test_advice_keyword(self):
        """Should classify advice requests"""
        intent, _ = classify_intent("Give me some advice")
        assert intent == Intent.RECOMMENDATIONS


class TestClassifyIntentCategoryStats:
    """Tests for CATEGORY_STATS intent classification"""

    def test_category_stats(self):
        """Should classify category stats requests"""
        intent, entities = classify_intent("Statistics for Electronics category")
        assert intent == Intent.CATEGORY_STATS
        assert entities.get("category") == "Electronics"

    def test_category_mention(self):
        """Should classify when category mentioned"""
        intent, _ = classify_intent("How is Electronics performing?")
        assert intent == Intent.CATEGORY_STATS


class TestClassifyIntentRegionStats:
    """Tests for REGION_STATS intent classification"""

    def test_region_stats(self):
        """Should classify region stats requests"""
        intent, entities = classify_intent("Sales in East region")
        assert intent == Intent.REGION_STATS
        assert entities.get("region") == "East"

    def test_region_comparison(self):
        """Should classify region queries - region_stats when region mentioned"""
        intent, _ = classify_intent("Sales in East region")
        assert intent == Intent.REGION_STATS


class TestClassifyIntentTopProducts:
    """Tests for TOP_PRODUCTS intent classification"""

    def test_top_products(self):
        """Should classify top products requests"""
        intent, _ = classify_intent("What are the top 5 products?")
        assert intent == Intent.TOP_PRODUCTS

    def test_best_products(self):
        """Should classify best products"""
        intent, _ = classify_intent("Show me the best products")
        assert intent == Intent.TOP_PRODUCTS

    def test_popular_products(self):
        """Should classify popular products"""
        intent, _ = classify_intent("Most popular products")
        assert intent == Intent.TOP_PRODUCTS


class TestClassifyIntentLowPerformers:
    """Tests for LOW_PERFORMERS intent classification"""

    def test_worst_products(self):
        """Should classify worst products requests"""
        intent, _ = classify_intent("Which products are performing worst?")
        assert intent == Intent.LOW_PERFORMERS

    def test_declining_products(self):
        """Should classify declining products"""
        intent, _ = classify_intent("Which products are declining?")
        assert intent == Intent.LOW_PERFORMERS

    def test_poor_performers(self):
        """Should classify poorly performing products"""
        intent, _ = classify_intent("Что плохо продаётся?")
        assert intent == Intent.LOW_PERFORMERS


class TestClassifyIntentDatasetInfo:
    """Tests for DATASET_INFO intent classification"""

    def test_dataset_overview(self):
        """Should classify dataset overview requests"""
        intent, _ = classify_intent("Give me an overview of the dataset")
        assert intent == Intent.DATASET_INFO

    def test_how_many_products(self):
        """Should classify count questions"""
        intent, _ = classify_intent("Сколько всего продуктов?")
        assert intent == Intent.DATASET_INFO

    def test_what_categories(self):
        """Should classify category listing"""
        intent, _ = classify_intent("Какие есть категории?")
        assert intent == Intent.DATASET_INFO


class TestClassifyIntentGeneral:
    """Tests for GENERAL intent classification"""

    def test_general_greeting(self):
        """Should classify greetings as general"""
        intent, _ = classify_intent("Hello")
        assert intent == Intent.GENERAL

    def test_unrecognized_query(self):
        """Should classify unrecognized queries as general"""
        intent, _ = classify_intent("Random text that means nothing")
        assert intent == Intent.GENERAL


class TestGetFollowUpSuggestions:
    """Tests for get_follow_up_suggestions()"""

    def test_returns_list(self):
        """Should return a list of suggestions"""
        result = get_follow_up_suggestions(Intent.FORECAST, {"product_ids": ["P0001"]})
        assert isinstance(result, list)

    def test_max_four_suggestions(self):
        """Should return max 4 suggestions"""
        result = get_follow_up_suggestions(Intent.GENERAL, {})
        assert len(result) <= 4

    def test_forecast_suggestions(self):
        """Should give relevant forecast follow-ups"""
        result = get_follow_up_suggestions(Intent.FORECAST, {"product_ids": ["P0001"]})
        assert len(result) > 0
        # Should suggest related actions
        assert any("P0001" in s or "сезон" in s.lower() or "погод" in s.lower() for s in result)


class TestEntityExtraction:
    """Tests for entity extraction in classify_intent()"""

    def test_extracts_product_ids(self):
        """Should extract product IDs"""
        _, entities = classify_intent("Compare P0001 and P0002")
        assert "product_ids" in entities
        assert "P0001" in entities["product_ids"]
        assert "P0002" in entities["product_ids"]

    def test_extracts_category(self):
        """Should extract category"""
        _, entities = classify_intent("Electronics stats")
        assert entities.get("category") == "Electronics"

    def test_extracts_region(self):
        """Should extract region"""
        _, entities = classify_intent("Sales in East")
        assert entities.get("region") == "East"

    def test_extracts_days(self):
        """Should extract days when not default"""
        _, entities = classify_intent("Forecast for 14 days")
        assert entities.get("days") == 14


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
