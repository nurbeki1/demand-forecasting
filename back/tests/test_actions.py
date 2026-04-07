"""
Tests for Action Service and Action Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import app
from app.deps import get_current_user
from services.action_service import action_service, ActionType, ActionStatus


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


class TestActionServiceUnit:
    """Unit tests for ActionService"""

    def test_create_alert_success(self):
        """Should create alert successfully"""
        result = action_service.execute_action(
            action_type="create_alert",
            params={"product_id": "P0001", "alert_type": "demand_spike"},
            user_id=999,
        )

        assert result.status == ActionStatus.SUCCESS
        assert result.data is not None
        assert result.data["product_id"] == "P0001"

    def test_create_alert_missing_product_id(self):
        """Should fail without product_id"""
        result = action_service.execute_action(
            action_type="create_alert",
            params={},
            user_id=999,
        )

        assert result.status == ActionStatus.FAILED
        assert "product_id is required" in result.message

    def test_generate_report_success(self):
        """Should generate report successfully"""
        result = action_service.execute_action(
            action_type="generate_report",
            params={"product_id": "P0001", "report_type": "forecast"},
            user_id=999,
        )

        assert result.status == ActionStatus.SUCCESS
        assert result.data is not None
        assert "sections" in result.data

    def test_compare_products_success(self):
        """Should compare products successfully"""
        result = action_service.execute_action(
            action_type="compare_products",
            params={"product_ids": ["P0001", "P0002", "P0003"]},
            user_id=999,
        )

        assert result.status == ActionStatus.SUCCESS
        assert len(result.data["results"]) == 3

    def test_compare_products_needs_two(self):
        """Should fail with less than 2 products"""
        result = action_service.execute_action(
            action_type="compare_products",
            params={"product_ids": ["P0001"]},
            user_id=999,
        )

        assert result.status == ActionStatus.FAILED

    def test_add_to_watchlist_success(self):
        """Should add to watchlist successfully"""
        result = action_service.execute_action(
            action_type="add_to_watchlist",
            params={"product_id": "P0005"},
            user_id=888,
        )

        assert result.status == ActionStatus.SUCCESS
        assert result.data["product_id"] == "P0005"

    def test_add_to_watchlist_duplicate(self):
        """Should handle duplicate gracefully"""
        # Add first time
        action_service.execute_action(
            action_type="add_to_watchlist",
            params={"product_id": "P0006"},
            user_id=777,
        )

        # Add again
        result = action_service.execute_action(
            action_type="add_to_watchlist",
            params={"product_id": "P0006"},
            user_id=777,
        )

        # Should still succeed but indicate already exists
        assert result.status == ActionStatus.SUCCESS
        assert "already in your watchlist" in result.message

    def test_unknown_action_type(self):
        """Should handle unknown action type"""
        result = action_service.execute_action(
            action_type="unknown_action",
            params={},
            user_id=999,
        )

        assert result.status == ActionStatus.FAILED
        assert "Unknown action type" in result.message

    def test_get_user_alerts(self):
        """Should return user's alerts"""
        # Create alert
        action_service.execute_action(
            action_type="create_alert",
            params={"product_id": "P0007"},
            user_id=666,
        )

        alerts = action_service.get_user_alerts(666)
        assert len(alerts) >= 1
        assert any(a["product_id"] == "P0007" for a in alerts)

    def test_get_user_watchlist(self):
        """Should return user's watchlist"""
        action_service.execute_action(
            action_type="add_to_watchlist",
            params={"product_id": "P0008"},
            user_id=555,
        )

        watchlist = action_service.get_user_watchlist(555)
        assert len(watchlist) >= 1


class TestActionEndpoints:
    """Integration tests for action endpoints"""

    def test_execute_action_requires_auth(self, unauthenticated_client):
        """Action endpoint should require authentication"""
        response = unauthenticated_client.post(
            "/actions/execute",
            json={"action_type": "create_alert", "params": {"product_id": "P0001"}},
        )
        assert response.status_code == 401

    def test_execute_action_create_alert(self, client):
        """Should execute create_alert action"""
        response = client.post(
            "/actions/execute",
            json={"action_type": "create_alert", "params": {"product_id": "P0001"}},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["action_type"] == "create_alert"

    def test_execute_action_generate_report(self, client):
        """Should execute generate_report action"""
        response = client.post(
            "/actions/execute",
            json={
                "action_type": "generate_report",
                "params": {"product_id": "P0001", "report_type": "forecast"},
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "data" in data

    def test_execute_action_add_to_watchlist(self, client):
        """Should execute add_to_watchlist action"""
        response = client.post(
            "/actions/execute",
            json={"action_type": "add_to_watchlist", "params": {"product_id": "P0099"}},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"

    def test_get_user_alerts_endpoint(self, client):
        """Should return user alerts"""
        # First create an alert
        client.post(
            "/actions/execute",
            json={"action_type": "create_alert", "params": {"product_id": "P0010"}},
        )

        response = client.get("/actions/alerts")
        assert response.status_code == 200

        data = response.json()
        assert "alerts" in data
        assert isinstance(data["alerts"], list)

    def test_get_user_watchlist_endpoint(self, client):
        """Should return user watchlist"""
        response = client.get("/actions/watchlist")
        assert response.status_code == 200

        data = response.json()
        assert "watchlist" in data
        assert isinstance(data["watchlist"], list)


class TestActionValidation:
    """Tests for action parameter validation"""

    def test_action_request_validation(self, client):
        """Should validate action request format"""
        # Missing action_type
        response = client.post(
            "/actions/execute",
            json={"params": {"product_id": "P0001"}},
        )
        assert response.status_code == 422  # Validation error

    def test_action_params_optional(self, client):
        """Params should be optional"""
        response = client.post(
            "/actions/execute",
            json={"action_type": "generate_report"},
        )

        # Should not fail due to missing params
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])