# scripts/architecture/models/scan_result.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class ScanResult:
    """Result of a scan operation"""
    timestamp: datetime
    total_files: int
    total_modules: int
    total_relations: int
    modules: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]
    errors: List[str] = None
    warnings: List[str] = None
    duration: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []