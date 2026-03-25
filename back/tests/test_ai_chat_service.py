"""
Test cases for AI Chat Service
"""
import pytest
from unittest.mock import patch, MagicMock
from services.ai_chat_service import (
    handle_ai_chat,
    build_rag_context,
    get_chart_data,
    get_chat_history,
    clear_chat_history,
    get_analytics_summary,
    get_analytics_trends,
)
from services.intent_classifier import Intent


class TestBuildRagContext:
    """Tests for build_rag_context()"""

    def test_forecast_context(self):
        """Should build context for forecast intent"""
        context = build_rag_context(
            Intent.FORECAST,
            {"product_ids": ["P0001"], "days": 7}
        )
        assert len(context) > 0
        assert "P0001" in context or "Product" in context

    def test_comparison_context(self):
        """Should build context for comparison intent"""
        context = build_rag_context(
            Intent.COMPARISON,
            {"product_ids": ["P0001", "P0002"]}
        )
        assert len(context) > 0

    def test_category_context(self):
        """Should build context for category stats"""
        context = build_rag_context(
            Intent.CATEGORY_STATS,
            {"category": "Electronics"}
        )
        assert len(context) > 0

    def test_region_context(self):
        """Should build context for region stats"""
        context = build_rag_context(
            Intent.REGION_STATS,
            {"region": "East"}
        )
        assert len(context) > 0

    def test_top_products_context(self):
        """Should build context for top products"""
        context = build_rag_context(
            Intent.TOP_PRODUCTS,
            {"top_n": 5}
        )
        assert len(context) > 0

    def test_trends_context(self):
        """Should build context for trends"""
        context = build_rag_context(
            Intent.TRENDS,
            {}
        )
        assert len(context) > 0

    def test_general_context(self):
        """Should build context for general intent"""
        context = build_rag_context(
            Intent.GENERAL,
            {}
        )
        assert len(context) > 0

    def test_empty_entities(self):
        """Should handle empty entities"""
        context = build_rag_context(Intent.FORECAST, {})
        # Should return fallback overview
        assert len(context) > 0


class TestGetChartData:
    """Tests for get_chart_data()"""

    def test_forecast_returns_data(self):
        """Should return chart data for forecast"""
        data = get_chart_data(
            Intent.FORECAST,
            {"product_ids": ["P0001"], "days": 7}
        )
        # May be None if product doesn't exist
        if data:
            assert "product_id" in data
            assert "history" in data
            assert "forecast" in data

    def test_product_info_returns_data(self):
        """Should return chart data for product info"""
        data = get_chart_data(
            Intent.PRODUCT_INFO,
            {"product_ids": ["P0001"]}
        )
        if data:
            assert "product_id" in data

    def test_no_data_for_trends(self):
        """Should not return chart data for trends"""
        data = get_chart_data(Intent.TRENDS, {})
        assert data is None

    def test_no_data_without_product(self):
        """Should not return data without product ID"""
        data = get_chart_data(Intent.FORECAST, {})
        assert data is None


class TestHandleAiChat:
    """Tests for handle_ai_chat()"""

    @patch("services.ai_chat_service.ask_llm")
    def test_returns_reply(self, mock_llm):
        """Should return a reply"""
        mock_llm.return_value = "Test response"

        result = handle_ai_chat("Hello", user_id=1)

        assert "reply" in result
        assert result["reply"] == "Test response"

    @patch("services.ai_chat_service.ask_llm")
    def test_returns_intent(self, mock_llm):
        """Should return classified intent"""
        mock_llm.return_value = "Response"

        result = handle_ai_chat("Forecast for P0001", user_id=1)

        assert "intent" in result
        assert result["intent"] == "forecast"

    @patch("services.ai_chat_service.ask_llm")
    def test_returns_entities(self, mock_llm):
        """Should return extracted entities"""
        mock_llm.return_value = "Response"

        result = handle_ai_chat("Forecast for P0001 for 14 days", user_id=1)

        assert "entities" in result
        assert "P0001" in result["entities"].get("product_ids", [])

    @patch("services.ai_chat_service.ask_llm")
    def test_returns_suggestions(self, mock_llm):
        """Should return suggestions"""
        mock_llm.return_value = "Response"

        result = handle_ai_chat("Hello", user_id=1)

        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)

    @patch("services.ai_chat_service.ask_llm")
    def test_stores_messages(self, mock_llm):
        """Should store messages in memory"""
        mock_llm.return_value = "Response"

        # Clear first
        clear_chat_history(user_id=99)

        handle_ai_chat("Test message", user_id=99)

        history = get_chat_history(user_id=99)
        assert len(history) >= 2  # User + Assistant

    @patch("services.ai_chat_service.ask_llm")
    def test_handles_llm_error(self, mock_llm):
        """Should handle LLM errors gracefully"""
        mock_llm.side_effect = Exception("LLM Error")

        result = handle_ai_chat("Hello", user_id=1)

        assert "reply" in result
        assert "error" in result["reply"].lower()

    @patch("services.ai_chat_service.ask_llm")
    def test_includes_data_for_forecast(self, mock_llm):
        """Should include chart data for forecast"""
        mock_llm.return_value = "Forecast response"

        result = handle_ai_chat("Forecast for P0001", user_id=1)

        # Data may be present if product exists
        if "data" in result:
            assert "product_id" in result["data"]


class TestGetChatHistory:
    """Tests for get_chat_history()"""

    def test_returns_list(self):
        """Should return a list"""
        result = get_chat_history(user_id=1)
        assert isinstance(result, list)

    def test_respects_limit(self):
        """Should respect limit parameter"""
        # Add some messages first
        from memory.chat_memory import chat_memory
        for i in range(10):
            chat_memory.add_message(888, "user", f"Message {i}")

        result = get_chat_history(user_id=888, limit=5)
        assert len(result) <= 5


class TestClearChatHistory:
    """Tests for clear_chat_history()"""

    def test_returns_result(self):
        """Should return clear result"""
        result = clear_chat_history(user_id=1)

        assert "message" in result
        assert "cleared_messages" in result

    def test_history_empty_after_clear(self):
        """History should be empty after clear"""
        # Add a message
        from memory.chat_memory import chat_memory
        chat_memory.add_message(777, "user", "Test")

        clear_chat_history(user_id=777)

        history = get_chat_history(user_id=777)
        assert len(history) == 0


class TestGetAnalyticsSummary:
    """Tests for get_analytics_summary()"""

    def test_returns_overview(self):
        """Should return overview"""
        result = get_analytics_summary()

        assert "overview" in result

    def test_returns_top_by_demand(self):
        """Should return top by demand"""
        result = get_analytics_summary()

        assert "top_by_demand" in result
        assert isinstance(result["top_by_demand"], list)

    def test_returns_top_by_growth(self):
        """Should return top by growth"""
        result = get_analytics_summary()

        assert "top_by_growth" in result

    def test_returns_declining(self):
        """Should return declining products"""
        result = get_analytics_summary()

        assert "declining" in result


class TestGetAnalyticsTrends:
    """Tests for get_analytics_trends()"""

    def test_returns_growing(self):
        """Should return growing products"""
        result = get_analytics_trends()

        assert "growing" in result
        assert isinstance(result["growing"], list)

    def test_returns_declining(self):
        """Should return declining products"""
        result = get_analytics_trends()

        assert "declining" in result

    def test_returns_stable(self):
        """Should return stable products"""
        result = get_analytics_trends()

        assert "stable" in result


class TestUserIsolation:
    """Tests for user isolation in chat"""

    @patch("services.ai_chat_service.ask_llm")
    def test_different_users_separate_history(self, mock_llm):
        """Different users should have separate histories"""
        mock_llm.return_value = "Response"

        clear_chat_history(user_id=111)
        clear_chat_history(user_id=222)

        handle_ai_chat("User 111 message", user_id=111)
        handle_ai_chat("User 222 message", user_id=222)

        history_111 = get_chat_history(user_id=111)
        history_222 = get_chat_history(user_id=222)

        # Each user should have their own messages
        assert any("111" in h["content"] for h in history_111)
        assert any("222" in h["content"] for h in history_222)


class TestContextBuilding:
    """Tests for context building with different intents"""

    def test_seasonality_context(self):
        """Should build seasonality context"""
        context = build_rag_context(
            Intent.SEASONALITY,
            {"product_ids": ["P0001"]}
        )
        assert len(context) > 0

    def test_weather_context(self):
        """Should build weather impact context"""
        context = build_rag_context(
            Intent.WEATHER_IMPACT,
            {"product_ids": ["P0001"]}
        )
        assert len(context) > 0

    def test_low_performers_context(self):
        """Should build low performers context"""
        context = build_rag_context(
            Intent.LOW_PERFORMERS,
            {}
        )
        assert len(context) > 0

    def test_dataset_info_context(self):
        """Should build dataset info context"""
        context = build_rag_context(
            Intent.DATASET_INFO,
            {}
        )
        assert len(context) > 0
        assert "Records" in context or "Product" in context

    def test_recommendations_context(self):
        """Should build recommendations context"""
        context = build_rag_context(
            Intent.RECOMMENDATIONS,
            {}
        )
        assert len(context) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
