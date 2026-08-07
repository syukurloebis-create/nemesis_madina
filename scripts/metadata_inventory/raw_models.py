# scripts/metadata_inventory/raw_models.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class RawColumn:
    """Collector output untuk kolom (tanpa SQLAlchemy)."""
    name: str
    type: str
    nullable: bool
    primary_key: bool
    default: Optional[str] = None

@dataclass(frozen=True)
class RawTable:
    """Collector output untuk tabel (tanpa SQLAlchemy)."""
    fullname: str
    columns: List[RawColumn]
    primary_key: List[str]
    foreign_keys: List[Dict[str, str]]
    indexes: List[Dict[str, Any]]

@dataclass(frozen=True)
class RawMetadata:
    """Collector output untuk metadata (tanpa SQLAlchemy)."""
    module: str
    base_name: str
    metadata_type: str
    tables: List[RawTable]
    mapper_count: int

@dataclass(frozen=True)
class RawRelationship:
    """Collector output untuk relationship (tanpa SQLAlchemy)."""
    source_module: str
    source_model: str
    source_attribute: str
    target_model: str
    uselist: bool
    lazy: str

@dataclass(frozen=True)
class RawForeignKey:
    """Collector output untuk foreign key (tanpa SQLAlchemy)."""
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    name: Optional[str] = None

@dataclass(frozen=True)
class RawCollection:
    """Hasil collection (tanpa SQLAlchemy)."""
    metadata: List[RawMetadata]
    relationships: List[RawRelationship]
    foreign_keys: List[RawForeignKey]