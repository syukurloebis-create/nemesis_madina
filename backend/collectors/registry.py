from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, Mapping, Iterator, List

from backend.collectors.interfaces.collector import ICollector
from backend.collectors.exceptions import CollectorNotFoundError


@dataclass(frozen=True)
class CollectorRegistry:

    _collectors: Mapping[str, ICollector] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __init__(self, collectors: Dict[str, ICollector]):
        object.__setattr__(
            self,
            "_collectors",
            MappingProxyType(dict(collectors)),
        )

    def get(self, name: str) -> ICollector:
        if name not in self._collectors:
            raise CollectorNotFoundError(name)
        return self._collectors[name]

    def get_all(self):
        return list(self._collectors.values())

    def keys(self):
        return list(self._collectors.keys())

    def __iter__(self):
        return iter(self._collectors)

    def __contains__(self, name):
        return name in self._collectors

    def __len__(self):
        return len(self._collectors)