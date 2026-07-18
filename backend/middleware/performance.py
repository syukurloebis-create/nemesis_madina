# backend/middleware/performance.py
class PerformanceMiddleware:
    async def __call__(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        
        if duration > 500:
            logger.warning(f"Slow response: {request.url.path} - {duration:.0f}ms")
        
        return response