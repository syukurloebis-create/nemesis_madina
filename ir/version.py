# ir/version.py
"""Version constants for IR module.

This module exists to break circular imports between __init__.py and hashing.py.
All version-related constants are defined here as a single source of truth.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IRVersion:
    schema: str
    ir: str

    @property
    def builder(self) -> str:
        """Compatibility property for CP1 tests."""
        return "1.0.0"


# Current IR version (metadata)
CURRENT_VERSION = IRVersion(
    schema="1.0.0",
    ir="0.2.0",
)

# Hash compatibility schema (for stable IDs - CP1 baseline)
HASHING_SCHEMA_VERSION = "3.1-candidate"

# Convenience aliases
SCHEMA_VERSION = CURRENT_VERSION.schema
DEFAULT_HASH_ALGORITHM = "sha256"