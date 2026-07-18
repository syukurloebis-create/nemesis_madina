"""
Simple in-memory cache for frequently accessed data
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json


class CacheService:
    """Simple in-memory cache"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 60  # seconds

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() < entry["expires_at"]:
                return entry["value"]
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """Cache value with TTL"""
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl)
        }

    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()


cache = CacheService()