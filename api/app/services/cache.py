import os
import json
from typing import Any, Optional
import asyncio
from datetime import datetime, timedelta

class CacheService:
    """Simple cache service with in-memory fallback and Redis support"""

    def __init__(self):
        self.use_redis = os.getenv("USE_REDIS_CACHE", "false") == "true"
        self._memory_cache = {}
        self._redis_client = None

        if self.use_redis:
            try:
                import redis
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                self._redis_client = redis.from_url(redis_url)
            except ImportError:
                print("Redis not available, falling back to memory cache")
                self.use_redis = False

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self.use_redis and self._redis_client:
            try:
                value = self._redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception:
                pass

        # Fallback to memory cache
        entry = self._memory_cache.get(key)
        if entry and self._is_valid(entry):
            return entry["value"]

        return None

    async def set(self, key: str, value: Any, ttl: int = 60) -> bool:
        """Set value in cache with TTL in seconds"""
        if self.use_redis and self._redis_client:
            try:
                self._redis_client.setex(key, ttl, json.dumps(value))
                return True
            except Exception:
                pass

        # Fallback to memory cache
        self._memory_cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl)
        }
        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if self.use_redis and self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception:
                pass

        if key in self._memory_cache:
            del self._memory_cache[key]

        return True

    def _is_valid(self, entry: dict) -> bool:
        """Check if cache entry is still valid"""
        return datetime.now() < entry["expires_at"]

    async def clear_expired(self):
        """Clear expired entries from memory cache"""
        current_time = datetime.now()
        expired_keys = [
            key for key, entry in self._memory_cache.items()
            if current_time >= entry["expires_at"]
        ]
        for key in expired_keys:
            del self._memory_cache[key]