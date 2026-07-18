# backend/cache/redis_cache.py

from typing import Optional, Any
import json
import redis.asyncio as redis

from backend.cache.provider import CacheProvider


class RedisCache(CacheProvider):
    """Redis cache implementation."""
    
    def __init__(self, redis_url: str, default_ttl: int = 60):
        self._client = redis.from_url(redis_url)
        self._default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        value = await self._client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds or self._default_ttl
        await self._client.setex(
            key,
            ttl,
            json.dumps(value)
        )
    
    async def delete(self, key: str) -> None:
        await self._client.delete(key)
    
    async def clear(self) -> None:
        await self._client.flushdb()
    
    async def exists(self, key: str) -> bool:
        return await self._client.exists(key) > 0
    
    async def close(self):
        await self._client.close()