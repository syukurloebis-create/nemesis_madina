# scripts/architecture/models/inventory.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class InventorySnapshot:
    """Snapshot of inventory state"""
    timestamp: datetime
    total_modules: int
    total_relations: int
    modules_by_type: Dict[str, int]
    modules_by_language: Dict[str, int]
    legacy_imports_count: int
    version: str = "1.0.0"