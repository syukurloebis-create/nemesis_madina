# backend/__init__.py
"""
Event Bus V2 – Unified Router for All Events
Abstraction layer over scheduler + outbox
"""

import logging
from typing import Dict, Any, Callable, Awaitable
from enum import Enum

from orchestrator.models import EventType, ExecutionJob

logger = logging.getLogger(__name__)


class RoutingDecision(str, Enum):
    """Where to route the event"""
    WORKER_QUEUE = "WORKER_QUEUE"
    ANALYTICS_WORKER = "ANALYTICS_WORKER"
    REPLAY_ENGINE = "REPLAY_ENGINE"
    IMMEDIATE = "IMMEDIATE"


class EventBusV2:
    """
    Unified event router – only routing, no execution logic
    
    Design constraint:
    Event bus tidak boleh execute logic, hanya routing
    """
    
    def __init__(self):
        self._routes: Dict[EventType, RoutingDecision] = {
            EventType.TRUST_MUTATION: RoutingDecision.WORKER_QUEUE,
            EventType.RISK_UPDATE: RoutingDecision.ANALYTICS_WORKER,
            EventType.REPLAY: RoutingDecision.REPLAY_ENGINE,
            EventType.ANOMALY_DETECTION: RoutingDecision.WORKER_QUEUE,
            EventType.SCORE_REFRESH: RoutingDecision.IMMEDIATE,
            EventType.FEDERATION_SYNC: RoutingDecision.WORKER_QUEUE,
        }
        
        # Custom handlers for immediate execution
        self._immediate_handlers: Dict[EventType, Callable] = {}
        
        logger.info("EventBusV2 initialized with %d routes", len(self._routes))
    
    def route(self, job: ExecutionJob) -> RoutingDecision:
        """
        Determine routing destination for a job
        
        Pure routing logic – no side effects
        """
        event_type = job.event_type
        
        if event_type in self._routes:
            decision = self._routes[event_type]
            logger.debug("Routed job %s (%s) -> %s", 
                        job.job_id, event_type.value, decision.value)
            return decision
        
        # Default to worker queue
        logger.warning("No route defined for %s, defaulting to WORKER_QUEUE", event_type)
        return RoutingDecision.WORKER_QUEUE
    
    def register_route(self, event_type: EventType, decision: RoutingDecision):
        """Register or override a route"""
        self._routes[event_type] = decision
        logger.info("Registered route: %s -> %s", event_type.value, decision.value)
    
    def register_immediate_handler(self, event_type: EventType, handler: Callable[[ExecutionJob], Awaitable[Any]]):
        """Register handler for immediate execution (bypass queue)"""
        self._immediate_handlers[event_type] = handler
        self._routes[event_type] = RoutingDecision.IMMEDIATE
        logger.info("Registered immediate handler for %s", event_type.value)
    
    async def execute_immediate(self, job: ExecutionJob) -> Any:
        """Execute job immediately using registered handler"""
        handler = self._immediate_handlers.get(job.event_type)
        if not handler:
            raise ValueError(f"No immediate handler for {job.event_type}")
        
        logger.info("Executing immediate job %s (%s)", job.job_id, job.event_type.value)
        return await handler(job)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            "total_routes": len(self._routes),
            "immediate_handlers": len(self._immediate_handlers),
            "routes": {k.value: v.value for k, v in self._routes.items()}
        }