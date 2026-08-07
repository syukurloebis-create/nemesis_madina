# scripts/metadata_inventory/discovery/model_discovery.py
"""
Model Discovery - Menemukan semua ORM models dengan metadata lengkap.
Phase 2 - Discovery Runtime (Revised)
"""

import gc
import sys
import inspect
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field

from ..canonical_serializer import Fingerprint


@dataclass(frozen=True)
class ColumnInfo:
    """Informasi lengkap tentang sebuah kolom."""
    name: str
    type: str
    nullable: bool
    unique: bool
    default: Optional[str] = None
    server_default: Optional[str] = None
    primary_key: bool = False


@dataclass(frozen=True)
class ModelMetadata:
    """Lengkap metadata untuk sebuah model."""
    name: str
    module: str
    qualname: str
    tablename: Optional[str] = None
    schema: Optional[str] = None
    is_abstract: bool = False
    is_mixin: bool = False
    is_joined_inheritance: bool = False
    columns: List[ColumnInfo] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[Dict[str, str]] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    mapper_args: Dict[str, Any] = field(default_factory=dict)
    fingerprint: str = ""
    
    def __post_init__(self):
        # Generate fingerprint from metadata (includes column types)
        content = {
            "name": self.name,
            "module": self.module,
            "tablename": self.tablename,
            "schema": self.schema,
            "columns": [
                {
                    "name": c.name,
                    "type": c.type,
                    "nullable": c.nullable,
                    "unique": c.unique
                }
                for c in self.columns
            ],
            "primary_keys": sorted(self.primary_keys),
            "foreign_keys": sorted(self.foreign_keys, key=lambda x: str(x)),
            "relationships": sorted(self.relationships, key=lambda x: str(x)),
            "indexes": sorted(self.indexes),
            "constraints": sorted(self.constraints)
        }
        object.__setattr__(self, 'fingerprint', Fingerprint.generate(content))


class ModelDiscovery:
    """
    Menemukan semua ORM models dengan metadata lengkap.
    """
    
    def __init__(self):
        self._models: Dict[str, ModelMetadata] = {}
    
    def discover_all(self, registry) -> Dict[str, ModelMetadata]:
        """Discover all models from a registry."""
        
        for mapper in registry.mappers:
            try:
                class_obj = mapper.class_
                if not class_obj:
                    continue
                
                name = class_obj.__name__
                module = class_obj.__module__
                qualname = class_obj.__qualname__
                
                # Table info
                tablename = None
                schema = None
                if hasattr(mapper, 'local_table') and mapper.local_table:
                    tablename = mapper.local_table.name
                    schema = getattr(mapper.local_table, 'schema', None)
                
                # Check abstract
                is_abstract = False
                if hasattr(class_obj, '__abstract__'):
                    is_abstract = bool(class_obj.__abstract__)
                if not is_abstract and hasattr(mapper, 'is_abstract'):
                    is_abstract = mapper.is_abstract
                
                # Check mixin
                is_mixin = False
                if hasattr(class_obj, '__mixin__'):
                    is_mixin = bool(class_obj.__mixin__)
                
                # Check inheritance
                is_joined_inheritance = False
                if hasattr(mapper, 'inherits') and mapper.inherits:
                    is_joined_inheritance = True
                
                # Columns with full info
                columns = []
                for col in mapper.columns:
                    column_info = ColumnInfo(
                        name=col.name,
                        type=str(col.type),
                        nullable=col.nullable,
                        unique=col.unique,
                        default=str(col.default) if col.default else None,
                        server_default=str(col.server_default) if col.server_default else None,
                        primary_key=col.primary_key
                    )
                    columns.append(column_info)
                
                # Primary keys
                primary_keys = []
                if hasattr(mapper, 'primary_key'):
                    primary_keys = [c.name for c in mapper.primary_key]
                
                # Foreign keys
                foreign_keys = []
                for col in mapper.columns:
                    for fk in col.foreign_keys:
                        foreign_keys.append({
                            "source": f"{col.table.name}.{col.name}",
                            "target": f"{fk.column.table.name}.{fk.column.name}"
                        })
                
                # Relationships
                relationships = []
                for rel in mapper.relationships:
                    rel_info = {
                        "key": rel.key,
                        "target": rel.mapper.class_.__name__ if hasattr(rel.mapper, 'class_') else "unknown",
                        "uselist": rel.uselist,
                        "lazy": rel.lazy
                    }
                    relationships.append(rel_info)
                
                # Indexes
                indexes = []
                if hasattr(mapper, 'tables'):
                    for table in mapper.tables:
                        for idx in table.indexes:
                            idx_name = idx.name or "unnamed"
                            idx_cols = [c.name for c in idx.columns]
                            indexes.append(f"{idx_name}:{','.join(idx_cols)}")
                
                # Constraints
                constraints = []
                if hasattr(mapper, 'tables'):
                    for table in mapper.tables:
                        for constr in table.constraints:
                            constraints.append(str(constr))
                
                # Mapper args
                mapper_args = {}
                if hasattr(class_obj, '__mapper_args__'):
                    mapper_args = class_obj.__mapper_args__
                
                # Create ModelMetadata
                metadata = ModelMetadata(
                    name=name,
                    module=module,
                    qualname=qualname,
                    tablename=tablename,
                    schema=schema,
                    is_abstract=is_abstract,
                    is_mixin=is_mixin,
                    is_joined_inheritance=is_joined_inheritance,
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys,
                    relationships=relationships,
                    indexes=indexes,
                    constraints=constraints,
                    mapper_args=mapper_args
                )
                
                self._models[name] = metadata
                    
            except Exception as e:
                print(f"  ⚠️ Error processing mapper: {e}")
        
        return self._models