"""
API Integration Tests for Chat Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the app
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import app
from app.deps import get_current_user


@pytest.fixture
def mock_user():
    """Mock user object"""
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    return user


@pytest.fixture
def client(mock_user):
    """Create test client with mocked auth"""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client():
    """Create test client without auth"""
    app.dependency_overrides.clear()
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create mock auth headers - in real tests, get actual token"""
    return {"Authorization": "Bearer test_token"}


class TestChatEndpointUnauthenticated:
    """Tests for unauthenticated requests"""

    def test_chat_requires_auth(self, unauthenticated_client):
        """Chat endpoint should require authentication"""
        response = unauthenticated_client.post("/chat", json={"message": "Hello"})
        assert response.status_code == 401

    def test_chat_history_requires_auth(self, unauthenticated_client):
        """Chat history should require authentication"""
        response = unauthenticated_client.get("/chat/history")
        assert response.status_code == 401

    def test_delete_history_requires_auth(self, unauthenticated_client):
        """Delete history should require authentication"""
        response = unauthenticated_client.delete("/chat/history")
        assert response.status_code == 401


class TestChatEndpointAuthenticated:
    """Tests for authenticated chat endpoint (client fixture has mocked auth)"""

    def test_chat_with_forecast_intent(self, client):
        """Should handle forecast requests"""
        response = client.post(
            "/chat",
            json={"message": "Forecast for P0001 for 7 days"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "reply" in data
        assert "intent" in data
        assert "suggestions" in data
        assert data["intent"] == "forecast"

    def test_chat_with_product_info(self, client):
        """Should handle product info requests"""
        response = client.post(
            "/chat",
            json={"message": "Tell me about P0001"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["intent"] == "product_info"

    def test_chat_with_comparison(self, client):
        """Should handle comparison requests"""
        response = client.post(
            "/chat",
            json={"message": "Compare P0001 and P0002"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["intent"] == "comparison"

    def test_chat_with_trends(self, client):
        """Should handle trends requests"""
        response = client.post(
            "/chat",
            json={"message": "What are the current trends?"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["intent"] == "trends"

    def test_chat_with_recommendations(self, client):
        """Should handle recommendation requests"""
        response = client.post(
            "/chat",
            json={"message": "What do you recommend?"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["intent"] == "recommendations"

    def test_chat_with_top_products(self, client):
        """Should handle top products requests"""
        response = client.post(
            "/chat",
            json={"message": "Show me top 5 products"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["intent"] == "top_products"

    def test_chat_with_category_stats(self, client):
        """Should handle category stats requests"""
        response = client.post(
            "/chat",
            json={"message": "Electronics statistics"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["intent"] == "category_stats"

    def test_chat_with_region_stats(self, client):
        """Should handle region stats requests"""
        response = client.post(
            "/chat",
            json={"message": "Sales in East region"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["intent"] == "region_stats"

    def test_chat_returns_suggestions(self, client):
        """Should return follow-up suggestions"""
        response = client.post(
            "/chat",
            json={"message": "Forecast for P0001"}
        )

        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_chat_returns_entities(self, client):
        """Should return extracted entities"""
        response = client.post(
            "/chat",
            json={"message": "Forecast for P0001 for 14 days"}
        )

        data = response.json()
        assert "entities" in data
        if data["entities"]:
            assert "product_ids" in data["entities"]

    def test_chat_with_empty_message(self, client):
        """Should handle empty messages"""
        response = client.post(
            "/chat",
            json={"message": ""}
        )

        # Should still return a response
        assert response.status_code == 200

    def test_chat_russian_language(self, client):
        """Should handle Russian language"""
        response = client.post(
            "/chat",
            json={"message": "Прогноз для P0001 на 7 дней"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "forecast"


class TestChatHistoryEndpoint:
    """Tests for chat history endpoint (client fixture has mocked auth)"""

    def test_get_empty_history(self, client):
        """Should return empty list for new user"""
        # Clear any existing history first
        client.delete("/chat/history")

        response = client.get("/chat/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_history_after_chat(self, client):
        """Should return messages after chatting"""
        # Clear history
        client.delete("/chat/history")

        # Send a message
        client.post("/chat", json={"message": "Hello"})

        # Get history
        response = client.get("/chat/history")
        data = response.json()

        # Should have at least user message and assistant response
        assert len(data) >= 2

    def test_get_history_with_limit(self, client):
        """Should respect limit parameter"""
        # Clear history
        client.delete("/chat/history")

        # Send multiple messages
        for i in range(5):
            client.post("/chat", json={"message": f"Message {i}"})

        # Get limited history
        response = client.get("/chat/history?limit=4")
        data = response.json()

        assert len(data) <= 4

    def test_history_message_format(self, client):
        """History messages should have correct format"""
        client.delete("/chat/history")
        client.post("/chat", json={"message": "Test"})

        response = client.get("/chat/history")
        data = response.json()

        if len(data) > 0:
            msg = data[0]
            assert "role" in msg
            assert "content" in msg
            assert "timestamp" in msg


class TestDeleteHistoryEndpoint:
    """Tests for delete history endpoint (client fixture has mocked auth)"""

    def test_delete_history(self, client):
        """Should clear history"""
        # Add some messages
        client.post("/chat", json={"message": "Test"})

        # Delete
        response = client.delete("/chat/history")
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "cleared_messages" in data

    def test_history_empty_after_delete(self, client):
        """History should be empty after delete"""
        client.post("/chat", json={"message": "Test"})
        client.delete("/chat/history")

        response = client.get("/chat/history")
        data = response.json()

        assert len(data) == 0


class TestAnalyticsEndpoints:
    """Tests for analytics endpoints (client fixture has mocked auth)"""

    def test_analytics_summary(self, client):
        """Should return analytics summary"""
        response = client.get("/analytics/summary")

        assert response.status_code == 200
        data = response.json()

        assert "overview" in data
        assert "top_by_demand" in data
        assert "top_by_growth" in data
        assert "declining" in data

    def test_analytics_summary_overview_fields(self, client):
        """Analytics summary should have overview fields"""
        response = client.get("/analytics/summary")
        data = response.json()

        overview = data.get("overview", {})
        assert "total_records" in overview
        assert "total_products" in overview

    def test_analytics_trends(self, client):
        """Should return analytics trends"""
        response = client.get("/analytics/trends")

        assert response.status_code == 200
        data = response.json()

        assert "growing" in data
        assert "declining" in data
        assert "stable" in data


class TestChatResponseStructure:
    """Tests for chat response structure (client fixture has mocked auth)"""

    def test_response_has_reply(self, client):
        """Response should always have reply"""
        response = client.post("/chat", json={"message": "Any message"})
        data = response.json()

        assert "reply" in data
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 0

    def test_response_has_intent(self, client):
        """Response should always have intent"""
        response = client.post("/chat", json={"message": "Any message"})
        data = response.json()

        assert "intent" in data
        assert isinstance(data["intent"], str)

    def test_response_may_have_data(self, client):
        """Forecast response may include chart data"""
        response = client.post("/chat", json={"message": "Forecast for P0001"})
        data = response.json()

        # Data is optional but when present should have structure
        if "data" in data and data["data"]:
            assert "product_id" in data["data"]
            assert "history" in data["data"]
            assert "forecast" in data["data"]


class TestChatEdgeCases:
    """Tests for edge cases (client fixture has mocked auth)"""

    def test_invalid_product_id(self, client):
        """Should handle invalid product ID gracefully"""
        response = client.post(
            "/chat",
            json={"message": "Forecast for INVALID_PRODUCT"}
        )

        # Should not crash
        assert response.status_code == 200

    def test_very_long_message(self, client):
        """Should handle very long messages"""
        long_message = "Hello " * 1000

        response = client.post(
            "/chat",
            json={"message": long_message}
        )

        assert response.status_code == 200

    def test_special_characters(self, client):
        """Should handle special characters"""
        response = client.post(
            "/chat",
            json={"message": "Test <script>alert('xss')</script> P0001"}
        )

        assert response.status_code == 200

    def test_unicode_message(self, client):
        """Should handle unicode"""
        response = client.post(
            "/chat",
            json={"message": "Прогноз 预测 forecast"}
        )

        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
