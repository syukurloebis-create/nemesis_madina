# ir/diagnostics.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class Diagnostic:
    severity: Severity
    code: str
    message: str
    location_id: Optional[int] = None
    module_id: Optional[int] = None