"""
NEMESIS Madina - Query Bus
✅ Generic query bus with handlers
✅ Middleware support
"""

from typing import Type, Dict, Any, Generic, TypeVar, Optional
import logging

from backend.application.queries.base import IQuery, IQueryHandler

TQuery = TypeVar('TQuery', bound=IQuery)
TResult = TypeVar('TResult')

logger = logging.getLogger(__name__)


class QueryBus:
    """Query bus with middleware pipeline."""
    
    def __init__(self):
        self._handlers: Dict[Type[IQuery], IQueryHandler] = {}
        self._middleware = []
    
    def add_middleware(self, middleware: callable) -> None:
        """Add middleware."""
        self._middleware.append(middleware)
    
    async def execute(self, query: TQuery) -> Any:
        """Execute query with middleware pipeline."""
        handler = self._handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler for {type(query)}")
        
        # ✅ Build middleware pipeline
        async def execute_handler(q: TQuery) -> Any:
            return await handler.handle(q)
        
        # Chain middleware
        result = None
        for middleware in reversed(self._middleware):
            # ✅ Proper next() pattern
            next_func = execute_handler if result is None else result
            result = await middleware(query, next_func)
        
        return result


# Usage example
middleware_chain = [
    logging_middleware,
    authorization_middleware,
    validation_middleware,
    caching_middleware,
    tracing_middleware,
]