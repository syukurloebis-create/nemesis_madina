# backend/dashboard/pipelines/registry.py

from typing import Mapping, Optional, List, Any
from types import MappingProxyType

from backend.dashboard.pipelines.constants import PipelineName, DEFAULT_PIPELINES
from backend.dashboard.pipelines.descriptor import PipelineDescriptor
from backend.dashboard.pipelines.exceptions import UnknownPipelineException
from backend.dashboard.pipelines.base import Pipeline


class PipelineRegistry:
    """
    Immutable registry for pipelines.
    """
    
    def __init__(
        self,
        pipelines: Mapping[PipelineName, Pipeline[Any, Any]],
        descriptors: Mapping[PipelineName, PipelineDescriptor[Any]]
    ):
        self._pipelines = MappingProxyType(dict(pipelines))
        self._descriptors = MappingProxyType(dict(descriptors))
    
    def get(self, name: PipelineName) -> Pipeline[Any, Any]:
        try:
            return self._pipelines[name]
        except KeyError:
            raise UnknownPipelineException(
                requested=name,
                available=list(self._pipelines.keys())
            )
    
    def get_descriptor(self, name: PipelineName) -> PipelineDescriptor[Any]:
        try:
            return self._descriptors[name]
        except KeyError:
            raise UnknownPipelineException(
                requested=name,
                available=list(self._descriptors.keys())
            )
    
    def get_or_none(self, name: PipelineName) -> Optional[Pipeline[Any, Any]]:
        return self._pipelines.get(name)
    
    def get_selected(self, names: List[PipelineName]) -> List[Pipeline[Any, Any]]:
        """
        Get pipelines in the order of names provided.
        Preserves execution order for orchestrator.
        """
        return [
            self._pipelines[name]
            for name in names
            if name in self._pipelines
        ]
    
    def get_all(self) -> List[Pipeline[Any, Any]]:
        return list(self._pipelines.values())
    
    def get_default(self) -> tuple[PipelineName, ...]:
        return DEFAULT_PIPELINES
    
    # Collection protocol
    def __iter__(self):
        return iter(self._pipelines)
    
    def __contains__(self, name: PipelineName) -> bool:
        return name in self._pipelines
    
    def __len__(self) -> int:
        return len(self._pipelines)