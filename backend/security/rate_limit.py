"""
Rate Limiting Module
"""

import time
from typing import Dict, Tuple, Optional, Callable
from collections import defaultdict
from threading import Lock
from fastapi import Request, HTTPException, status
from functools import wraps


class RateLimiter:
    """In-memory rate limiter"""
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
    
    def is_allowed(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """Check if request is allowed"""
        now = time.time()
        window_start = now - window_seconds
        
        with self._lock:
            self._requests[key] = [ts for ts in self._requests[key] if ts > window_start]
            
            if len(self._requests[key]) >= limit:
                return False, 0
            
            self._requests[key].append(now)
            remaining = limit - len(self._requests[key])
            return True, remaining
    
    def get_remaining(self, key: str, limit: int, window_seconds: int) -> int:
        """Get remaining requests for key"""
        now = time.time()
        window_start = now - window_seconds
        recent = [ts for ts in self._requests.get(key, []) if ts > window_start]
        return max(0, limit - len(recent))
    
    def reset(self, key: str):
        """Reset rate limit for a key"""
        with self._lock:
            if key in self._requests:
                del self._requests[key]


# Global rate limiter
rate_limiter = RateLimiter()


def rate_limit(limit: int, window_seconds: int, key_func: Optional[Callable] = None):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request in args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request and 'request' in kwargs:
                request = kwargs['request']
            
            if request is None:
                return await func(*args, **kwargs)
            
            # Get rate limit key
            if key_func:
                key = key_func(request)
            else:
                key = request.client.host if request.client else "unknown"
            
            # Check rate limit
            allowed, remaining = rate_limiter.is_allowed(key, limit, window_seconds)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Limit: {limit} requests per {window_seconds}s"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit_by_user(limit: int = 100, window_seconds: int = 60):
    """Rate limit by user ID"""
    def key_func(request: Request):
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        return f"ip:{request.client.host if request.client else 'unknown'}"
    
    return rate_limit(limit, window_seconds, key_func)


def rate_limit_by_ip(limit: int = 10, window_seconds: int = 60):
    """Rate limit by IP address"""
    def key_func(request: Request):
        return f"ip:{request.client.host if request.client else 'unknown'}"
    
    return rate_limit(limit, window_seconds, key_func)


def rate_limit_login(limit: int = 5, window_seconds: int = 60):
    """Rate limit for login attempts"""
    def key_func(request: Request):
        # Try to get username from body
        return f"login:{request.client.host if request.client else 'unknown'}"
    
    return rate_limit(limit, window_seconds, key_func)
