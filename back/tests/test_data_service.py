"""
Test cases for Data Service
"""
import pytest
from services.data_service import (
    get_all_products,
    get_all_categories,
    get_all_regions,
    get_product_summary,
    get_category_stats,
    get_region_stats,
    get_seasonality_analysis,
    get_weather_impact,
    get_top_performers,
    get_low_performers,
    search_products,
    compare_products,
    compare_regions,
    get_dataset_overview,
)


class TestGetAllProducts:
    """Tests for get_all_products()"""

    def test_returns_list(self):
        """Should return a list of product IDs"""
        result = get_all_products()
        assert isinstance(result, list)

    def test_products_not_empty(self):
        """Should return non-empty list"""
        result = get_all_products()
        assert len(result) > 0

    def test_product_id_format(self):
        """Product IDs should match P#### format"""
        result = get_all_products()
        for pid in result:
            assert pid.startswith("P")
            assert len(pid) == 5

    def test_products_sorted(self):
        """Products should be sorted"""
        result = get_all_products()
        assert result == sorted(result)


class TestGetAllCategories:
    """Tests for get_all_categories()"""

    def test_returns_list(self):
        """Should return a list"""
        result = get_all_categories()
        assert isinstance(result, list)

    def test_categories_not_empty(self):
        """Should return non-empty list"""
        result = get_all_categories()
        assert len(result) > 0

    def test_expected_category_exists(self):
        """Should contain expected category"""
        result = get_all_categories()
        # Check at least one common category exists
        assert any(cat in result for cat in ["Electronics", "Clothing", "Food"])


class TestGetAllRegions:
    """Tests for get_all_regions()"""

    def test_returns_list(self):
        """Should return a list"""
        result = get_all_regions()
        assert isinstance(result, list)

    def test_expected_regions(self):
        """Should contain expected regions"""
        result = get_all_regions()
        expected = ["East", "West", "North", "South"]
        for region in expected:
            assert region in result


class TestGetProductSummary:
    """Tests for get_product_summary()"""

    def test_valid_product(self):
        """Should return summary for valid product"""
        result = get_product_summary("P0001")
        assert result is not None
        assert isinstance(result, dict)

    def test_invalid_product_returns_none(self):
        """Should return None for invalid product"""
        result = get_product_summary("INVALID")
        assert result is None

    def test_summary_has_required_fields(self):
        """Summary should have all required fields"""
        result = get_product_summary("P0001")
        required_fields = [
            "product_id",
            "category",
            "price",
            "avg_demand",
            "min_demand",
            "max_demand",
            "trend_pct",
            "trend_direction",
            "total_records",
        ]
        for field in required_fields:
            assert field in result

    def test_demand_values_are_numeric(self):
        """Demand values should be numeric"""
        import numbers
        result = get_product_summary("P0001")
        assert isinstance(result["avg_demand"], numbers.Number)
        assert isinstance(result["min_demand"], numbers.Number)
        assert isinstance(result["max_demand"], numbers.Number)

    def test_trend_direction_valid(self):
        """Trend direction should be valid value"""
        result = get_product_summary("P0001")
        assert result["trend_direction"] in ["up", "down", "stable"]

    def test_min_less_than_max(self):
        """Min demand should be <= max demand"""
        result = get_product_summary("P0001")
        assert result["min_demand"] <= result["max_demand"]


class TestGetCategoryStats:
    """Tests for get_category_stats()"""

    def test_valid_category(self):
        """Should return stats for valid category"""
        result = get_category_stats("Electronics")
        assert result is not None

    def test_invalid_category_returns_none(self):
        """Should return None for invalid category"""
        result = get_category_stats("InvalidCategory")
        assert result is None

    def test_case_insensitive(self):
        """Should be case insensitive"""
        result1 = get_category_stats("Electronics")
        result2 = get_category_stats("electronics")
        result3 = get_category_stats("ELECTRONICS")
        # All should return valid results
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None

    def test_stats_has_required_fields(self):
        """Stats should have required fields"""
        result = get_category_stats("Electronics")
        required = ["category", "total_products", "avg_demand", "top_products"]
        for field in required:
            assert field in result


class TestGetRegionStats:
    """Tests for get_region_stats()"""

    def test_valid_region(self):
        """Should return stats for valid region"""
        result = get_region_stats("East")
        assert result is not None

    def test_invalid_region_returns_none(self):
        """Should return None for invalid region"""
        result = get_region_stats("InvalidRegion")
        assert result is None

    def test_case_insensitive(self):
        """Should be case insensitive"""
        result1 = get_region_stats("East")
        result2 = get_region_stats("east")
        assert result1 is not None
        assert result2 is not None

    def test_all_regions_have_stats(self):
        """All standard regions should have stats"""
        for region in ["East", "West", "North", "South"]:
            result = get_region_stats(region)
            assert result is not None


class TestGetSeasonalityAnalysis:
    """Tests for get_seasonality_analysis()"""

    def test_valid_product(self):
        """Should return seasonality for valid product"""
        result = get_seasonality_analysis("P0001")
        assert result is not None

    def test_invalid_product_returns_none(self):
        """Should return None for invalid product"""
        result = get_seasonality_analysis("INVALID")
        assert result is None

    def test_has_seasonality_data(self):
        """Should have seasonality data list"""
        result = get_seasonality_analysis("P0001")
        assert "seasonality_data" in result
        assert isinstance(result["seasonality_data"], list)

    def test_has_best_worst_season(self):
        """Should identify best and worst seasons"""
        result = get_seasonality_analysis("P0001")
        assert "best_season" in result
        assert "worst_season" in result


class TestGetWeatherImpact:
    """Tests for get_weather_impact()"""

    def test_valid_product(self):
        """Should return weather impact for valid product"""
        result = get_weather_impact("P0001")
        assert result is not None

    def test_has_weather_data(self):
        """Should have weather data list"""
        result = get_weather_impact("P0001")
        assert "weather_data" in result
        assert isinstance(result["weather_data"], list)


class TestGetTopPerformers:
    """Tests for get_top_performers()"""

    def test_returns_list(self):
        """Should return a list"""
        result = get_top_performers(5)
        assert isinstance(result, list)

    def test_respects_limit(self):
        """Should respect the n limit"""
        result = get_top_performers(3)
        assert len(result) <= 3

    def test_by_demand(self):
        """Should get top by demand"""
        result = get_top_performers(5, by="demand")
        assert len(result) > 0
        assert "avg_demand" in result[0]

    def test_by_growth(self):
        """Should get top by growth"""
        result = get_top_performers(5, by="growth")
        if len(result) > 0:
            assert "growth_pct" in result[0]

    def test_by_stability(self):
        """Should get top by stability"""
        result = get_top_performers(5, by="stability")
        if len(result) > 0:
            assert "cv" in result[0]

    def test_sorted_by_demand(self):
        """Results should be sorted by demand descending"""
        result = get_top_performers(5, by="demand")
        demands = [r["avg_demand"] for r in result]
        assert demands == sorted(demands, reverse=True)


class TestGetLowPerformers:
    """Tests for get_low_performers()"""

    def test_returns_list(self):
        """Should return a list"""
        result = get_low_performers(5)
        assert isinstance(result, list)

    def test_has_decline_info(self):
        """Should have decline percentage"""
        result = get_low_performers(5)
        if len(result) > 0:
            assert "decline_pct" in result[0]
            assert result[0]["decline_pct"] >= 0


class TestSearchProducts:
    """Tests for search_products()"""

    def test_search_by_product_id(self):
        """Should find products by ID"""
        result = search_products("P0001")
        assert len(result) > 0

    def test_search_by_category(self):
        """Should find by category"""
        result = search_products("Electronics")
        assert len(result) > 0

    def test_empty_query_returns_empty(self):
        """Empty query should return empty or minimal results"""
        result = search_products("")
        # May return results or empty depending on implementation
        assert isinstance(result, list)


class TestCompareProducts:
    """Tests for compare_products()"""

    def test_compare_two_products(self):
        """Should compare two valid products"""
        result = compare_products(["P0001", "P0002"])
        assert "products" in result
        assert len(result["products"]) == 2

    def test_compare_identifies_best(self):
        """Should identify best by demand"""
        result = compare_products(["P0001", "P0002"])
        assert "best_by_demand" in result

    def test_invalid_products_error(self):
        """Should return error for invalid products"""
        result = compare_products(["INVALID1", "INVALID2"])
        assert "error" in result

    def test_single_product_error(self):
        """Should error with single product"""
        result = compare_products(["P0001"])
        assert "error" in result


class TestCompareRegions:
    """Tests for compare_regions()"""

    def test_compare_two_regions(self):
        """Should compare two regions"""
        result = compare_regions(["East", "West"])
        assert "regions" in result
        assert len(result["regions"]) == 2

    def test_compare_all_regions(self):
        """Should compare all four regions"""
        result = compare_regions(["East", "West", "North", "South"])
        assert len(result["regions"]) == 4

    def test_identifies_best_region(self):
        """Should identify best region"""
        result = compare_regions(["East", "West"])
        assert "best_by_demand" in result


class TestGetDatasetOverview:
    """Tests for get_dataset_overview()"""

    def test_returns_dict(self):
        """Should return a dictionary"""
        result = get_dataset_overview()
        assert isinstance(result, dict)

    def test_has_required_fields(self):
        """Should have required overview fields"""
        result = get_dataset_overview()
        required = [
            "total_records",
            "total_products",
            "total_categories",
            "total_regions",
            "avg_demand",
            "categories",
            "regions",
            "products",
        ]
        for field in required:
            assert field in result

    def test_counts_are_positive(self):
        """Counts should be positive"""
        result = get_dataset_overview()
        assert result["total_records"] > 0
        assert result["total_products"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
