"""
Cache Service - Redis with in-memory fallback

Provides caching for:
- Chat responses (by user_id + message hash)
- Forecast results (by product_id + horizon)
- API responses
"""

from __future__ import annotations
import json
import hashlib
import logging
from typing import Optional, Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class CacheService:
    """
    Caching service with Redis support and in-memory fallback.

    If REDIS_URL is not set or Redis is unavailable, falls back to
    in-memory dictionary cache.
    """

    def __init__(self):
        self.redis = None
        self.local_cache: Dict[str, Dict[str, Any]] = {}
        self._connect_redis()

    def _connect_redis(self) -> None:
        """Attempt to connect to Redis if REDIS_URL is set"""
        import os
        redis_url = os.environ.get("REDIS_URL")

        if not redis_url:
            logger.info("REDIS_URL not set, using in-memory cache")
            return

        try:
            import redis
            self.redis = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis.ping()
            logger.info("Connected to Redis cache")
        except ImportError:
            logger.warning("redis package not installed, using in-memory cache")
            self.redis = None
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory cache")
            self.redis = None

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            if self.redis:
                value = self.redis.get(key)
                if value:
                    return json.loads(value)
                return None
            else:
                entry = self.local_cache.get(key)
                if entry:
                    # Check TTL for local cache
                    if entry.get("expires_at"):
                        if datetime.now().timestamp() > entry["expires_at"]:
                            del self.local_cache[key]
                            return None
                    return entry.get("value")
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds (default: 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis:
                serialized = json.dumps(value, default=str)
                self.redis.setex(key, ttl, serialized)
            else:
                self.local_cache[key] = {
                    "value": value,
                    "expires_at": datetime.now().timestamp() + ttl,
                }
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        try:
            if self.redis:
                self.redis.delete(key)
            else:
                self.local_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            if self.redis:
                self.redis.flushdb()
            else:
                self.local_cache.clear()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Check cache health status.

        Returns:
            Dict with 'healthy', 'backend', and 'info' keys
        """
        try:
            if self.redis:
                info = self.redis.info("memory")
                return {
                    "healthy": True,
                    "backend": "redis",
                    "info": {
                        "used_memory_human": info.get("used_memory_human", "N/A"),
                        "connected_clients": info.get("connected_clients", 0),
                    },
                }
            else:
                return {
                    "healthy": True,
                    "backend": "memory",
                    "info": {
                        "entries": len(self.local_cache),
                    },
                }
        except Exception as e:
            return {
                "healthy": False,
                "backend": "redis" if self.redis else "memory",
                "error": str(e),
            }

    # Convenience methods for common cache patterns

    def make_chat_key(self, user_id: int, message: str) -> str:
        """Generate cache key for chat response"""
        message_hash = hashlib.md5(message.encode()).hexdigest()[:12]
        return f"chat:{user_id}:{message_hash}"

    def make_forecast_key(self, product_id: str, store_id: Optional[str], horizon: int) -> str:
        """Generate cache key for forecast result"""
        store_part = store_id or "all"
        return f"forecast:{product_id}:{store_part}:{horizon}"

    def get_chat_response(self, user_id: int, message: str) -> Optional[Dict]:
        """Get cached chat response"""
        key = self.make_chat_key(user_id, message)
        return self.get(key)

    def set_chat_response(self, user_id: int, message: str, response: Dict, ttl: int = 300) -> bool:
        """Cache chat response"""
        key = self.make_chat_key(user_id, message)
        return self.set(key, response, ttl)

    def get_forecast(self, product_id: str, store_id: Optional[str], horizon: int) -> Optional[Dict]:
        """Get cached forecast result"""
        key = self.make_forecast_key(product_id, store_id, horizon)
        return self.get(key)

    def set_forecast(
        self,
        product_id: str,
        store_id: Optional[str],
        horizon: int,
        result: Dict,
        ttl: int = 600,
    ) -> bool:
        """Cache forecast result (default: 10 min TTL)"""
        key = self.make_forecast_key(product_id, store_id, horizon)
        return self.set(key, result, ttl)


# Global singleton instance
cache_service = CacheService()
