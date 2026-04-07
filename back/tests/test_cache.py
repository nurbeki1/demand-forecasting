"""
Tests for Cache Service
"""
import pytest
import time

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.cache_service import CacheService


@pytest.fixture
def cache():
    """Create a fresh cache instance for each test"""
    # Create instance without Redis (will use in-memory)
    service = CacheService()
    service.redis = None  # Force in-memory mode
    service.local_cache = {}
    return service


class TestCacheBasicOperations:
    """Tests for basic cache operations"""

    def test_set_and_get(self, cache):
        """Should set and get values"""
        cache.set("test_key", {"data": "value"})
        result = cache.get("test_key")

        assert result is not None
        assert result["data"] == "value"

    def test_get_nonexistent_key(self, cache):
        """Should return None for nonexistent key"""
        result = cache.get("nonexistent_key")
        assert result is None

    def test_delete_key(self, cache):
        """Should delete key"""
        cache.set("to_delete", "value")
        assert cache.get("to_delete") is not None

        cache.delete("to_delete")
        assert cache.get("to_delete") is None

    def test_clear_cache(self, cache):
        """Should clear all cache entries"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_set_with_ttl(self, cache):
        """Should respect TTL"""
        cache.set("ttl_key", "value", ttl=1)

        # Should exist immediately
        assert cache.get("ttl_key") == "value"

        # Wait for TTL to expire
        time.sleep(1.5)

        # Should be expired
        assert cache.get("ttl_key") is None


class TestCacheDataTypes:
    """Tests for different data types"""

    def test_cache_dict(self, cache):
        """Should cache dictionaries"""
        data = {"key": "value", "nested": {"a": 1}}
        cache.set("dict_key", data)

        result = cache.get("dict_key")
        assert result == data

    def test_cache_list(self, cache):
        """Should cache lists"""
        data = [1, 2, 3, {"nested": True}]
        cache.set("list_key", data)

        result = cache.get("list_key")
        assert result == data

    def test_cache_string(self, cache):
        """Should cache strings"""
        cache.set("string_key", "hello world")

        result = cache.get("string_key")
        assert result == "hello world"

    def test_cache_number(self, cache):
        """Should cache numbers"""
        cache.set("int_key", 42)
        cache.set("float_key", 3.14)

        assert cache.get("int_key") == 42
        assert cache.get("float_key") == 3.14

    def test_cache_boolean(self, cache):
        """Should cache booleans"""
        cache.set("bool_true", True)
        cache.set("bool_false", False)

        assert cache.get("bool_true") is True
        assert cache.get("bool_false") is False


class TestCacheKeyGeneration:
    """Tests for key generation helpers"""

    def test_make_chat_key(self, cache):
        """Should generate consistent chat keys"""
        key1 = cache.make_chat_key(1, "hello")
        key2 = cache.make_chat_key(1, "hello")
        key3 = cache.make_chat_key(2, "hello")
        key4 = cache.make_chat_key(1, "world")

        # Same user and message = same key
        assert key1 == key2

        # Different user = different key
        assert key1 != key3

        # Different message = different key
        assert key1 != key4

    def test_make_forecast_key(self, cache):
        """Should generate consistent forecast keys"""
        key1 = cache.make_forecast_key("P0001", None, 7)
        key2 = cache.make_forecast_key("P0001", None, 7)
        key3 = cache.make_forecast_key("P0001", "S001", 7)
        key4 = cache.make_forecast_key("P0001", None, 14)

        assert key1 == key2
        assert key1 != key3
        assert key1 != key4


class TestChatResponseCache:
    """Tests for chat response caching"""

    def test_set_and_get_chat_response(self, cache):
        """Should cache and retrieve chat responses"""
        response = {
            "reply": "Hello!",
            "intent": "greeting",
        }

        cache.set_chat_response(1, "hi", response)
        result = cache.get_chat_response(1, "hi")

        assert result == response

    def test_chat_response_isolation(self, cache):
        """Chat responses should be isolated by user"""
        cache.set_chat_response(1, "test", {"reply": "user1"})
        cache.set_chat_response(2, "test", {"reply": "user2"})

        assert cache.get_chat_response(1, "test")["reply"] == "user1"
        assert cache.get_chat_response(2, "test")["reply"] == "user2"


class TestForecastCache:
    """Tests for forecast caching"""

    def test_set_and_get_forecast(self, cache):
        """Should cache and retrieve forecasts"""
        forecast = {
            "product_id": "P0001",
            "predictions": [100, 110, 120],
        }

        cache.set_forecast("P0001", None, 7, forecast)
        result = cache.get_forecast("P0001", None, 7)

        assert result == forecast

    def test_forecast_with_store(self, cache):
        """Should cache forecasts with store_id"""
        forecast = {"product_id": "P0001", "store_id": "S001"}

        cache.set_forecast("P0001", "S001", 7, forecast)
        result = cache.get_forecast("P0001", "S001", 7)

        assert result == forecast
        assert cache.get_forecast("P0001", None, 7) is None


class TestCacheHealthCheck:
    """Tests for health check"""

    def test_health_check_in_memory(self, cache):
        """Should report healthy in memory mode"""
        health = cache.health_check()

        assert health["healthy"] is True
        assert health["backend"] == "memory"

    def test_health_check_has_info(self, cache):
        """Should include info in health check"""
        cache.set("test", "value")
        health = cache.health_check()

        assert "info" in health
        assert health["info"]["entries"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])