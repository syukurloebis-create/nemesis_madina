# scripts/architecture/models/module.py
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ModuleType(Enum):
    DOMAIN = "domain"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    API = "api"
    FRONTEND = "frontend"
    TEST = "test"
    LEGACY = "legacy"
    UNKNOWN = "unknown"

class Language(Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    SQL = "sql"
    YAML = "yaml"
    DOCKER = "docker"
    UNKNOWN = "unknown"

@dataclass
class Module:
    id: str
    name: str
    path: str
    type: ModuleType
    language: Language
    lines: int = 0
    complexity: int = 0
    imports: List[str] = None
    classes: List[str] = None
    functions: List[str] = None
    test_coverage: Optional[float] = None
    deprecated: bool = False
    
    def __post_init__(self):
        if self.imports is None:
            self.imports = []
        if self.classes is None:
            self.classes = []
        if self.functions is None:
            self.functions = []

@dataclass
class Relation:
    source: str
    target: str
    type: str
    weight: int = 1

@dataclass
class Violation:
    rule_id: str
    message: str
    severity: str
    module: Optional[str] = None
    details: Optional[dict] = None

@dataclass
class Metric:
    name: str
    value: float
    unit: str
    timestamp: Optional[str] = None