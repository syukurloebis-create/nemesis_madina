"""
Rate Limiting Middleware
"""
import time
from typing import Dict, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from fastapi import Request, HTTPException, status


# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - window

        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if t > window_start]

        # Check limit
        if len(self.requests[key]) >= limit:
            return False, int(self.requests[key][0] + window - now)

        # Add current request
        self.requests[key].append(now)
        return True, 0

    def reset(self, key: str | None = None) -> None:
        """Reset rate limit state.

        Intended for deterministic test isolation.
        Does not affect production behavior.

        Args:
            key: Optional specific key to reset. If None, reset all.
        """
        if key is None:
            self.requests.clear()
        else:
            self.requests.pop(key, None)


# Global rate limiter instance
_rate_limiter = RateLimiter()

def rate_limit(limit: int = 5, window: int = 60):
    """
    Rate limiting decorator
    limit: number of requests allowed in window
    window: time window in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Try to find Request in kwargs
                request = kwargs.get('request')
            
            if not request:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)
            
            # Get client IP
            client_ip = request.client.host if request.client else "unknown"
            
            # Create rate limit key
            key = f"{client_ip}:{func.__name__}"
            
            # Check rate limit
            allowed, retry_after = _rate_limiter.is_allowed(key, limit, window)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {retry_after} seconds",
                    headers={"Retry-After": str(retry_after)}
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator