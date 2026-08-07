"""
Event Router Interface
======================

Defines the IEventRouter interface for routing jobs.

ADR Reference: ADR-033
Requirements: REQ-ROU-001
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class RoutingDestination(str, Enum):
    """Predefined routing destinations."""
    WORKER = "worker"
    IMMEDIATE = "immediate"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    DEAD_LETTER = "dead_letter"


@dataclass(frozen=True)
class RoutingDecision:
    """
    The result of a routing decision.

    Contains the destination and any additional metadata.
    Immutable by design.
    """
    destination: RoutingDestination
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})

    def __repr__(self) -> str:
        return f"<RoutingDecision(destination={self.destination})>"


@dataclass(frozen=True)
class Job:
    """
    A job to be routed.

    Contains the event and any job-specific metadata.
    Immutable by design.
    """
    event_type: str
    payload: Any
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})
        if not self.event_type:
            raise ValueError("event_type cannot be empty")

    def __repr__(self) -> str:
        return f"<Job(type={self.event_type})>"


class IEventRouter(ABC):
    """
    Event Router Contract.

    Routes a job to an execution destination.

    Semantics (ADR-032):
    - Route: Select an execution destination for a job
    - Destination: Worker queue, immediate, analytics, etc.
    - Pure routing: No side effects
    """

    @abstractmethod
    def route(self, job: Job) -> RoutingDecision:
        """
        Route a job to an execution destination.

        Precondition: job is not None
        Precondition: job.event_type is not empty
        Postcondition: routing decision is returned
        Postcondition: no side effects during routing

        Args:
            job: The job to route

        Returns:
            RoutingDecision: The routing decision

        Raises:
            ValueError: If job is None or event_type is empty
        """
        pass

    @abstractmethod
    def get_default_destination(self) -> RoutingDestination:
        """
        Get the default destination for unknown event types.

        Returns:
            The default routing destination
        """
        pass