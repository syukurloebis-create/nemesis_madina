# backend/application/dto/search_options.py

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SearchOptions:
    """Pagination and sorting options."""
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    sort_by: Optional[str] = None
    sort_desc: bool = False