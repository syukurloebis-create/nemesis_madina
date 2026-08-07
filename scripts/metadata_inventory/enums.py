# scripts/metadata_inventory/enums.py
from enum import Enum

class FindingID(Enum):
    """Finding ID hanya sebagai identifier, tanpa metadata tambahan."""
    ORM001 = "ORM001"
    ORM002 = "ORM002"
    ORM003 = "ORM003"
    # ... semua finding IDs ...
    
    def __str__(self):
        return self.value