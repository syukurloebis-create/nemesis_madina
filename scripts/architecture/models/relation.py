# scripts/architecture/models/relation.py
from dataclasses import dataclass

@dataclass
class Relation:
    """Dependency relation between modules"""
    source: str
    target: str
    type: str  # imports, depends_on, part_of, implements, tests
    weight: int = 1