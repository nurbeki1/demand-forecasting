"""
Tests for Health Endpoint
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint"""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_status(self, client):
        """Health response should have status field"""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_has_version(self, client):
        """Health response should have version field"""
        response = client.get("/health")
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)

    def test_health_has_checks(self, client):
        """Health response should have component checks"""
        response = client.get("/health")
        data = response.json()

        assert "checks" in data
        checks = data["checks"]

        assert "database" in checks
        assert "cache" in checks

    def test_health_database_check_structure(self, client):
        """Database check should have status and latency"""
        response = client.get("/health")
        data = response.json()

        db_check = data["checks"]["database"]
        assert "status" in db_check
        assert db_check["status"] in ["healthy", "unhealthy"]

    def test_health_cache_check_structure(self, client):
        """Cache check should have status and backend info"""
        response = client.get("/health")
        data = response.json()

        cache_check = data["checks"]["cache"]
        assert "status" in cache_check
        assert "backend" in cache_check

    def test_health_has_timestamp(self, client):
        """Health response should have timestamp"""
        response = client.get("/health")
        data = response.json()

        assert "timestamp" in data


class TestHealthReadiness:
    """Tests for /health/ready endpoint"""

    def test_ready_returns_200(self, client):
        """Ready endpoint should return 200 when all services are up"""
        response = client.get("/health/ready")
        assert response.status_code == 200

    def test_ready_response_format(self, client):
        """Ready endpoint should return correct format"""
        response = client.get("/health/ready")
        data = response.json()

        assert "ready" in data
        assert isinstance(data["ready"], bool)


class TestHealthLiveness:
    """Tests for /health/live endpoint"""

    def test_live_returns_200(self, client):
        """Liveness endpoint should always return 200"""
        response = client.get("/health/live")
        assert response.status_code == 200

    def test_live_response_format(self, client):
        """Liveness endpoint should return correct format"""
        response = client.get("/health/live")
        data = response.json()

        assert "alive" in data
        assert data["alive"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])