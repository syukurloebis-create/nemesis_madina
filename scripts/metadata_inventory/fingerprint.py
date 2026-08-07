# scripts/metadata_inventory/fingerprint.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import hashlib
import json

@dataclass(frozen=True)
class Fingerprint:
    """Fingerprint dengan version dan algorithm."""
    version: str  # Fingerprint algorithm version
    algorithm: str  # Hash algorithm used
    value: str  # Actual fingerprint value
    timestamp: str  # When generated
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fingerprint_version": self.version,
            "algorithm": self.algorithm,
            "value": self.value,
            "generated_at": self.timestamp
        }
    
    @classmethod
    def generate(cls, structure: Dict[str, Any], version: str = "v1") -> 'Fingerprint':
        """Generate fingerprint with version."""
        algorithm = "sha256-canonical"
        
        # Canonical serialization
        canonical = json.dumps(structure, sort_keys=True, default=str)
        value = hashlib.sha256(canonical.encode()).hexdigest()[:12]
        
        return cls(
            version=version,
            algorithm=algorithm,
            value=value,
            timestamp=datetime.now().isoformat()
        )

@dataclass(frozen=True)
class ColumnFingerprint:
    name: str
    type: str
    nullable: bool

@dataclass(frozen=True)
class TableFingerprint:
    fullname: str
    columns: List[ColumnFingerprint]
    primary_key: List[str]
    foreign_keys: List[Dict[str, str]]
    indexes: List[Dict[str, Any]]

@dataclass(frozen=True)
class MetadataFingerprint:
    """Fingerprint berdasarkan struktur, bukan runtime id()."""
    module: str
    base_name: str
    tables: List[TableFingerprint]
    fingerprint: str
    
    @classmethod
    def from_metadata(cls, module: str, base_name: str, metadata) -> 'MetadataFingerprint':
        """Generate fingerprint dari metadata tanpa menggunakan id()."""
        tables = []
        for table in metadata.tables.values():
            columns = [
                ColumnFingerprint(
                    name=col.name,
                    type=str(col.type),
                    nullable=col.nullable
                )
                for col in table.columns
            ]
            
            fks = [
                {"source": f"{fk.parent.table.fullname}.{fk.parent.name}",
                 "target": f"{fk.column.table.fullname}.{fk.column.name}"}
                for fk in table.foreign_keys
            ]
            
            indexes = [
                {"name": idx.name,
                 "columns": [col.name for col in idx.columns],
                 "unique": idx.unique}
                for idx in table.indexes
            ]
            
            tables.append(TableFingerprint(
                fullname=table.fullname,
                columns=columns,
                primary_key=[col.name for col in table.primary_key.columns] if table.primary_key else [],
                foreign_keys=fks,
                indexes=indexes
            ))
        
        # Generate fingerprint dari struktur
        structure = {
            "module": module,
            "base_name": base_name,
            "tables": [
                {
                    "fullname": t.fullname,
                    "columns": [(c.name, c.type, c.nullable) for c in t.columns],
                    "primary_key": t.primary_key,
                    "foreign_keys": t.foreign_keys,
                    "indexes": t.indexes
                }
                for t in tables
            ]
        }
        
        fingerprint = hashlib.sha256(
            json.dumps(structure, sort_keys=True, default=str).encode()
        ).hexdigest()[:12]
        
        return cls(
            module=module,
            base_name=base_name,
            tables=tables,
            fingerprint=fingerprint
        )

    def generate_metadata_fingerprint(metadata) -> str:
        """
        Generate fingerprint dengan canonical ordering.
        Semua koleksi di-sort sebelum hashing.
        """
        structure = {}
    
        # Sort tables by fullname
        for table in sorted(metadata.tables.values(), key=lambda t: t.fullname):
            table_info = {
                "columns": [],
                "primary_key": [],
                "foreign_keys": [],
                "indexes": []
            }
        
            # Sort columns by name
            for col in sorted(table.columns, key=lambda c: c.name):
                col_info = {
                    "name": col.name,
                    "type": str(col.type),
                    "nullable": col.nullable
                }
                table_info["columns"].append(col_info)
        
            # Primary Key (already deterministic)
            if table.primary_key:
                table_info["primary_key"] = [col.name for col in table.primary_key.columns]
        
            # Sort foreign keys
            for fk in sorted(table.foreign_keys, key=lambda f: f.name or ""):
                table_info["foreign_keys"].append({
                    "source": f"{fk.parent.table.fullname}.{fk.parent.name}",
                    "target": f"{fk.column.table.fullname}.{fk.column.name}"
                })
        
            # Sort indexes by name
            for idx in sorted(table.indexes, key=lambda i: i.name or ""):
                table_info["indexes"].append({
                    "name": idx.name,
                    "columns": sorted([col.name for col in idx.columns]),
                    "unique": idx.unique
                })
        
            structure[table.fullname] = table_info
    
        # JSON with sorted keys
        structure_json = json.dumps(structure, sort_keys=True, default=str)
        fingerprint = hashlib.sha256(structure_json.encode()).hexdigest()[:12]
    
        return fingerprint