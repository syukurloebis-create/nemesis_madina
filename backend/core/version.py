"""
Version Information — Immutable, Hashable, with Slots.

Architecture Decision:
- VersionInfo is infrastructure metadata
- NOT part of DTO (DTO is pure business data)
- Used in ExecutionContext for observability
- Hashable for cache keys
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import os


@dataclass(frozen=True, slots=True)
class VersionInfo:
    """
    Version Information — Infrastructure Metadata.
    
    Characteristics:
    - Immutable (frozen=True)
    - Hashable (for cache keys)
    - Slots (memory efficient)
    - Comprehensive version fields
    """
    
    build: str
    commit: str
    branch: str
    api_version: str
    schema_version: str
    engine_version: str
    calculator_version: str
    sql_version: str
    built_at: datetime = field(default_factory=datetime.now)
    
    def __hash__(self) -> int:
        """Hash for cache keys."""
        return hash((
            self.build,
            self.commit,
            self.branch,
            self.api_version,
            self.schema_version,
            self.engine_version,
            self.calculator_version,
            self.sql_version
        ))
    
    @classmethod
    def default(cls) -> "VersionInfo":
        """Default version for development."""
        return cls(
            build="dev",
            commit="dev",
            branch="main",
            api_version="v1",
            schema_version="v3.2",
            engine_version="v1.0",
            calculator_version="v1.0",
            sql_version="v3.2"
        )
    
    @classmethod
    def from_environment(cls) -> "VersionInfo":
        """Load version from environment variables."""
        return cls(
            build=os.getenv("BUILD_NUMBER", "unknown"),
            commit=os.getenv("GIT_COMMIT", "unknown"),
            branch=os.getenv("GIT_BRANCH", "unknown"),
            api_version=os.getenv("API_VERSION", "v1"),
            schema_version=os.getenv("SCHEMA_VERSION", "v3.2"),
            engine_version=os.getenv("ENGINE_VERSION", "v1.0"),
            calculator_version=os.getenv("CALCULATOR_VERSION", "v1.0"),
            sql_version=os.getenv("SQL_VERSION", "v3.2")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dict for logging."""
        return {
            "build": self.build,
            "commit": self.commit,
            "branch": self.branch,
            "api_version": self.api_version,
            "schema_version": self.schema_version,
            "engine_version": self.engine_version,
            "calculator_version": self.calculator_version,
            "sql_version": self.sql_version,
            "built_at": self.built_at.isoformat()
        }
    
    def short(self) -> str:
        """Short version string for display."""
        return f"{self.api_version}-{self.build[:8]}"