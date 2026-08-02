from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .version import DEFAULT_HASH_ALGORITHM

@dataclass(frozen=True)
class IRConfig:
    hash_algorithm: str = DEFAULT_HASH_ALGORITHM
    project_root: Path = field(default_factory=lambda: Path("."))
    skip_dirs: List[str] = field(default_factory=lambda: [
        "tests", "scripts", "migrations", "__pycache__", "venv", "env", ".venv"
    ])
    emit_locations: bool = True
    emit_blocks: bool = True
    emit_docstrings: bool = False
    strict_mode: bool = True
    deterministic: bool = True