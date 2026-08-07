"""
Event System Bootstrap
======================

Composition Root for the canonical event system.
"""

import logging
from typing import Optional, Dict

# ===== Explicit imports — NOT from root package =====
from backend.core.events.facade import EventBusFacade
from backend.core.events.routing import DefaultRouter, RoutingDestination
from backend.core.events.retry import DefaultRetryPolicy, ExponentialBackoffRetryPolicy
from backend.core.events.dead_letter import InMemoryDeadLetterStore, FileBasedDeadLetterStore
from backend.core.events.adapters import InfrastructureEventBusAdapter

logger = logging.getLogger(__name__)


class EventSystemConfig:
    def __init__(
        self,
        enable_routing: bool = True,
        default_destination: Optional[RoutingDestination] = None,
        routing_rules: Optional[Dict[str, RoutingDestination]] = None,
        enable_retry: bool = True,
        max_retry_attempts: int = 3,
        retry_delay_ms: int = 100,
        use_exponential_backoff: bool = False,
        exponential_backoff_multiplier: float = 2.0,
        exponential_backoff_max_delay_ms: Optional[int] = None,
        retry_jitter: bool = False,
        enable_dead_letter: bool = True,
        dead_letter_filepath: Optional[str] = None,
        enable_legacy_compat: bool = True,
    ):
        self.enable_routing = enable_routing
        self.default_destination = default_destination or RoutingDestination.IMMEDIATE
        self.routing_rules = routing_rules or {}
        self.enable_retry = enable_retry
        self.max_retry_attempts = max_retry_attempts
        self.retry_delay_ms = retry_delay_ms
        self.use_exponential_backoff = use_exponential_backoff
        self.exponential_backoff_multiplier = exponential_backoff_multiplier
        self.exponential_backoff_max_delay_ms = exponential_backoff_max_delay_ms
        self.retry_jitter = retry_jitter
        self.enable_dead_letter = enable_dead_letter
        self.dead_letter_filepath = dead_letter_filepath
        self.enable_legacy_compat = enable_legacy_compat


class EventSystemFactory:
    """
    Factory for building the event system.
    Uses singleton pattern with proper cache invalidation.
    """
    _instance = None
    _facade = None
    _legacy_wrapper = None
    _shared_retry_policy = None
    _shared_dead_letter_store = None

    def __new__(cls, config: Optional[EventSystemConfig] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = None
            cls._instance._initialized = False
            cls._instance._shared_adapter = None
        return cls._instance

    def __init__(self, config: Optional[EventSystemConfig] = None):
        """
        Initialize or update the factory instance.
        
        If config is provided and different from current config,
        invalidate cached facade and shared components.
        """
        # Check if config has changed
        if config is not None and config is not self._config:
            self._config = config
            # Invalidate all cached state
            self._facade = None
            self._legacy_wrapper = None
            self._shared_retry_policy = None
            self._shared_dead_letter_store = None
            self._shared_adapter = None
            self._initialized = True
        elif self._config is None:
            self._config = config or EventSystemConfig()
            self._initialized = True

    def _get_retry_policy(self):
        """Get or create the shared retry policy."""
        if self._shared_retry_policy is None:
            self._shared_retry_policy = self._build_retry_policy()
        return self._shared_retry_policy

    def _get_dead_letter_store(self):
        """Get or create the shared dead letter store."""
        if self._shared_dead_letter_store is None:
            self._shared_dead_letter_store = self._build_dead_letter_store()
        return self._shared_dead_letter_store

    def _get_shared_adapter(self) -> InfrastructureEventBusAdapter:
        """Get or create the shared adapter instance."""
        if self._shared_adapter is None:
            # Get shared retry policy and dead letter store (SAME instances)
            retry_policy = self._get_retry_policy()
            dead_letter_store = self._get_dead_letter_store()

            logger.info(f"Configuring adapter with retry={retry_policy is not None}, dlq={dead_letter_store is not None}")

            # Configure the adapter class with retry and dead letter
            InfrastructureEventBusAdapter.configure(
                retry_policy=retry_policy,
                dead_letter_store=dead_letter_store,
            )

            self._shared_adapter = InfrastructureEventBusAdapter()
            logger.info("Shared InfrastructureEventBusAdapter created")
        return self._shared_adapter

    def build(self) -> EventBusFacade:
        if self._facade is not None:
            return self._facade

        self._validate_config()

        shared_adapter = self._get_shared_adapter()
        publisher = shared_adapter
        subscriber = shared_adapter

        router = self._build_router()

        # Use the SAME shared retry policy and dead letter store
        retry_policy = self._get_retry_policy()
        dead_letter_store = self._get_dead_letter_store()

        self._facade = EventBusFacade(
            publisher=publisher,
            subscriber=subscriber,
            router=router,
            retry_policy=retry_policy,
            dead_letter_store=dead_letter_store,  # SAME instance as bus!
            use_null_objects=not self._config.enable_routing
            or not self._config.enable_retry
            or not self._config.enable_dead_letter,
        )

        if self._config.enable_legacy_compat:
            from backend.core.events.legacy_compat import LegacyEventBusWrapper
            self._legacy_wrapper = LegacyEventBusWrapper(self._facade)
            LegacyEventBusWrapper._instance = self._legacy_wrapper

        logger.info(f"Event system built successfully with shared adapter (dlq={dead_letter_store is not None})")
        return self._facade

    def _validate_config(self) -> None:
        if self._config.max_retry_attempts < 0:
            raise ValueError("max_retry_attempts must be >= 0")

    def _build_router(self):
        if not self._config.enable_routing:
            return None
        router = DefaultRouter(default_destination=self._config.default_destination)
        for event_type, destination in self._config.routing_rules.items():
            router.register_route(event_type, destination)
        return router

    def _build_retry_policy(self):
        if not self._config.enable_retry:
            return None
        if self._config.use_exponential_backoff:
            return ExponentialBackoffRetryPolicy(
                max_attempts=self._config.max_retry_attempts,
                base_delay_ms=self._config.retry_delay_ms,
                multiplier=self._config.exponential_backoff_multiplier,
                max_delay_ms=self._config.exponential_backoff_max_delay_ms,
                jitter=self._config.retry_jitter,
            )
        return DefaultRetryPolicy(
            max_attempts=self._config.max_retry_attempts,
            delay_ms=self._config.retry_delay_ms,
        )

    def _build_dead_letter_store(self):
        if not self._config.enable_dead_letter:
            return None
        if self._config.dead_letter_filepath:
            return FileBasedDeadLetterStore(self._config.dead_letter_filepath)
        return InMemoryDeadLetterStore()

    @classmethod
    def reset(cls):
        """Reset the singleton state. Used for testing."""
        cls._instance = None
        cls._facade = None
        cls._legacy_wrapper = None
        cls._shared_retry_policy = None
        cls._shared_dead_letter_store = None
        # Also reset LegacyEventBusWrapper
        from backend.core.events.legacy_compat import LegacyEventBusWrapper
        LegacyEventBusWrapper._instance = None


def create_event_system(config: Optional[EventSystemConfig] = None) -> EventBusFacade:
    factory = EventSystemFactory(config)
    return factory.build()

