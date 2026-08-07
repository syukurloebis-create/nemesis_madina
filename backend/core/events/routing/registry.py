"""
Routing Registry
================

Registry for event type to destination mappings.

ADR Reference: ADR-033
"""

from typing import Dict, Optional
from dataclasses import dataclass, field

from backend.core.events.interfaces.router import RoutingDestination


@dataclass(frozen=True)
class RoutingRule:
    """
    A routing rule mapping an event type to a destination.
    """
    event_type: str
    destination: RoutingDestination
    priority: int = 0

    def __post_init__(self):
        if not self.event_type:
            raise ValueError("event_type cannot be empty")


class RoutingRegistry:
    """
    Registry for event type to destination mappings.

    Maintains a mapping of event types to routing destinations.
    Supports wildcard matching and priority ordering.
    """

    def __init__(self):
        self._rules: Dict[str, RoutingRule] = {}
        self._wildcard_rules: Dict[str, RoutingRule] = {}
        self._default_destination: RoutingDestination = RoutingDestination.IMMEDIATE

    def register(
        self,
        event_type: str,
        destination: RoutingDestination,
        priority: int = 0,
    ) -> None:
        """
        Register a routing rule.

        Args:
            event_type: The event type to route
            destination: The destination to route to
            priority: Priority (higher = more specific)
        """
        rule = RoutingRule(event_type, destination, priority)

        if "*" in event_type:
            self._wildcard_rules[event_type] = rule
        else:
            self._rules[event_type] = rule

    def unregister(self, event_type: str) -> bool:
        """
        Unregister a routing rule.

        Args:
            event_type: The event type to unregister

        Returns:
            True if removed, False if not found
        """
        if event_type in self._rules:
            del self._rules[event_type]
            return True
        if event_type in self._wildcard_rules:
            del self._wildcard_rules[event_type]
            return True
        return False

    def get_destination(self, event_type: str) -> RoutingDestination:
        """
        Get the destination for an event type.

        Args:
            event_type: The event type to look up

        Returns:
            The routing destination
        """
        # Exact match first
        if event_type in self._rules:
            return self._rules[event_type].destination

        # Wildcard match (most specific first)
        for pattern, rule in sorted(
            self._wildcard_rules.items(),
            key=lambda x: x[1].priority,
            reverse=True,
        ):
            if self._match_wildcard(pattern, event_type):
                return rule.destination

        return self._default_destination

    def set_default_destination(self, destination: RoutingDestination) -> None:
        """
        Set the default destination for unknown event types.

        Args:
            destination: The default destination
        """
        self._default_destination = destination

    def get_default_destination(self) -> RoutingDestination:
        """
        Get the default destination.

        Returns:
            The default destination
        """
        return self._default_destination

    def _match_wildcard(self, pattern: str, event_type: str) -> bool:
        """
        Match a wildcard pattern against an event type.

        Supports:
        - * : matches any sequence
        - ? : matches any single character

        Args:
            pattern: The pattern to match
            event_type: The event type to test

        Returns:
            True if matches, False otherwise
        """
        import fnmatch
        return fnmatch.fnmatch(event_type, pattern)

    def clear(self) -> None:
        """Clear all routing rules."""
        self._rules.clear()
        self._wildcard_rules.clear()

    def get_all_rules(self) -> Dict[str, RoutingRule]:
        """Get all routing rules."""
        return {**self._rules, **self._wildcard_rules}