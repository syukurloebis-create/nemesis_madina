# backend/dashboard/protocols/feature_flags.py

from typing import Protocol, Dict, Any, Optional


class FeatureFlagProvider(Protocol):
    def is_enabled(self, flag: str, default: bool = True, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if feature flag is enabled."""
        ...

    def get_value(self, flag: str, default: Any = None, context: Optional[Dict[str, Any]] = None) -> Any:
        """Get feature flag value."""
        ...

    def exists(self, flag: str) -> bool:
        """Check if flag exists (not default)."""
        ...


class MemoryFeatureFlagProvider:
    """Simple in-memory feature flag provider for testing/development."""

    def __init__(self, flags: Optional[Dict[str, bool]] = None):
        self._flags = flags or {}

    def is_enabled(self, flag: str, default: bool = True, context: Optional[Dict[str, Any]] = None) -> bool:
        return self._flags.get(flag, default)

    def get_value(self, flag: str, default: Any = None, context: Optional[Dict[str, Any]] = None) -> Any:
        return self._flags.get(flag, default)

    def set_flag(self, flag: str, value: bool) -> None:
        """Set a feature flag value."""
        self._flags[flag] = value

    def exists(self, flag: str) -> bool:
        return flag in self._flags


class NoOpFeatureFlagProvider:
    """No-op feature flag provider (all flags enabled)."""

    def is_enabled(self, flag: str, default: bool = True, context: Optional[Dict[str, Any]] = None) -> bool:
        return default

    def get_value(self, flag: str, default: Any = None, context: Optional[Dict[str, Any]] = None) -> Any:
        return default