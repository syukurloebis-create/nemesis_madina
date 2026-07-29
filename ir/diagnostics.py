# ir/diagnostics.py

from enum import Enum
from typing import Optional, List, Sequence


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Diagnostic:
    def __init__(self, severity: Severity, code: str, message: str,
                 location_id: Optional[int] = None,
                 module_id: Optional[int] = None) -> None:
        self.severity = severity
        self.code = code
        self.message = message
        self.location_id = location_id
        self.module_id = module_id


class DiagnosticCollector:
    def __init__(self) -> None:
        self._messages: List[Diagnostic] = []

    def add(self, diagnostic: Diagnostic) -> None:
        self._messages.append(diagnostic)

    def add_error(self, code: str, message: str,
                  location_id: Optional[int] = None,
                  module_id: Optional[int] = None) -> None:
        self.add(Diagnostic(Severity.ERROR, code, message, location_id, module_id))

    def add_warning(self, code: str, message: str,
                    location_id: Optional[int] = None,
                    module_id: Optional[int] = None) -> None:
        self.add(Diagnostic(Severity.WARNING, code, message, location_id, module_id))

    def add_info(self, code: str, message: str,
                 location_id: Optional[int] = None,
                 module_id: Optional[int] = None) -> None:
        self.add(Diagnostic(Severity.INFO, code, message, location_id, module_id))

    def get_messages(self) -> Sequence[Diagnostic]:
        return tuple(self._messages)

    def get_errors(self) -> List[Diagnostic]:
        return [m for m in self._messages if m.severity == Severity.ERROR]

    def get_warnings(self) -> List[Diagnostic]:
        return [m for m in self._messages if m.severity == Severity.WARNING]

    def has_errors(self) -> bool:
        return len(self.get_errors()) > 0

    def count(self) -> int:
        return len(self._messages)

    def clear(self) -> None:
        self._messages.clear()