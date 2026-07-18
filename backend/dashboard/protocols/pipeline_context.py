# backend/dashboard/protocols/pipeline_context.py

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Optional, Any, Mapping
from types import MappingProxyType
import uuid

_EMPTY_FEATURE_FLAGS: Mapping[str, bool] = MappingProxyType({})
_EMPTY_METADATA: Mapping[str, Any] = MappingProxyType({})


@dataclass(slots=True, frozen=True)
class PipelineContext:
    """Pipeline execution context - fully immutable."""
    
    case_id: str
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    locale: str = "id"
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    feature_flags: Mapping[str, bool] = field(default_factory=lambda: _EMPTY_FEATURE_FLAGS)
    metadata: Mapping[str, Any] = field(default_factory=lambda: _EMPTY_METADATA)

    @classmethod
    def from_case(cls, case_id: str, **kwargs) -> "PipelineContext":
        return cls(case_id=case_id, **kwargs)
    
    def with_tenant(self, tenant_id: str) -> "PipelineContext":
        return replace(self, tenant_id=tenant_id)

    def with_user(self, user_id: str) -> "PipelineContext":
        return replace(self, user_id=user_id)

    def with_feature(self, key: str, value: bool) -> "PipelineContext":
        new_flags = dict(self.feature_flags)
        new_flags[key] = value
        return replace(self, feature_flags=MappingProxyType(new_flags))

    def with_metadata(self, key: str, value: Any) -> "PipelineContext":
        new_metadata = dict(self.metadata)
        new_metadata[key] = value
        return replace(self, metadata=MappingProxyType(new_metadata))

    def get_feature(self, key: str, default: bool = True) -> bool:
        return self.feature_flags.get(key, default)
    
    def elapsed_ms(self) -> float:
        now = datetime.now(timezone.utc)
        return (now - self.started_at).total_seconds() * 1000