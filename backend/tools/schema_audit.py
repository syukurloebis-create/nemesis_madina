"""
Schema Audit Tool — Automated Schema Discovery.

Menggunakan SQLAlchemy 2.x compatible.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy import inspect
from sqlalchemy.types import (
    Integer, BigInteger, SmallInteger, Numeric, Float,
    String, Text, Boolean, DateTime, Date, Time,
    JSON, ARRAY, UUID, Enum as SAEnum
)

from backend.core.database import DATABASE_URL


class SchemaAudit:
    """
    Automated Schema Audit — Menghasilkan schema_report.json.
    
    SQLAlchemy 2.x compatible:
        - Menggunakan engine.connect() untuk execute
        - Menggunakan Inspector untuk metadata
    """
    
    def __init__(self, engine: Engine):
        self._engine = engine
        self._inspector = inspect(engine)
    
    def audit(self) -> Dict[str, Any]:
        """Audit seluruh schema dan return report."""
        report = {
            "database": self._get_database_info(),
            "tables": {},
            "views": {},
            "summary": {}
        }
        
        # BASE TABLES only (not views, foreign tables)
        for table_name in self._inspector.get_table_names():
            report["tables"][table_name] = self._audit_table(table_name)
        
        # Views
        for view_name in self._inspector.get_view_names():
            report["views"][view_name] = self._audit_view(view_name)
        
        report["summary"] = self._generate_summary(report)
        return report
    
    def _audit_table(self, table_name: str) -> Dict[str, Any]:
        """Audit satu tabel."""
        return {
            "type": "table",
            "columns": self._get_columns_info(table_name),
            "primary_key": self._inspector.get_pk_constraint(table_name),
            "foreign_keys": self._inspector.get_foreign_keys(table_name),
            "indexes": self._get_indexes_info(table_name),
            "unique_constraints": self._inspector.get_unique_constraints(table_name),
            "check_constraints": self._get_check_constraints(table_name),
            "row_count_estimate": self._get_row_count_estimate(table_name),
            "sample": self._get_sample(table_name),
            "comment": self._get_table_comment(table_name),
        }
    
    def _get_columns_info(self, table_name: str) -> List[Dict]:
        """Get columns with type info."""
        columns = []
        for col in self._inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": self._get_type_name(col["type"]),
                "nullable": col["nullable"],
                "default": str(col["default"]) if col.get("default") else None,
                "autoincrement": col.get("autoincrement", False),
                "comment": col.get("comment"),
            })
        return columns
    
    def _get_type_name(self, type_obj) -> str:
        """Get type name from SQLAlchemy type."""
        if isinstance(type_obj, (Integer, BigInteger, SmallInteger)):
            return "integer"
        elif isinstance(type_obj, (Numeric, Float)):
            return "numeric"
        elif isinstance(type_obj, (String, Text)):
            return "string"
        elif isinstance(type_obj, Boolean):
            return "boolean"
        elif isinstance(type_obj, (DateTime, Date, Time)):
            return "datetime"
        elif isinstance(type_obj, JSON):
            return "json"
        elif isinstance(type_obj, ARRAY):
            return "array"
        elif isinstance(type_obj, UUID):
            return "uuid"
        elif isinstance(type_obj, SAEnum):
            return "enum"
        else:
            return str(type_obj)
    
    def _get_indexes_info(self, table_name: str) -> List[Dict]:
        """Get indexes with details."""
        indexes = []
        for idx in self._inspector.get_indexes(table_name):
            indexes.append({
                "name": idx["name"],
                "unique": idx["unique"],
                "columns": idx["column_names"],
                "definition": idx.get("dialect_options", {}).get("postgresql_using"),
            })
        return indexes
    
    def _get_check_constraints(self, table_name: str) -> List[Dict]:
        """Get check constraints."""
        with self._engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT
                        conname as name,
                        pg_get_constraintdef(oid) as definition
                    FROM pg_constraint
                    WHERE conrelid = :table_oid
                      AND contype = 'c'
                """),
                {"table_oid": self._inspector.get_table_oid(table_name)}
            )
            return [{"name": row.name, "definition": row.definition} for row in result]
    
    def _get_row_count_estimate(self, table_name: str) -> int:
        """Get row count estimate from pg_class."""
        with self._engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT reltuples::bigint as estimate
                    FROM pg_class
                    WHERE relname = :table_name
                """),
                {"table_name": table_name}
            )
            return result.scalar() or 0
    
    def _get_sample(self, table_name: str, limit: int = 10) -> List[Dict]:
        """Get sample data (BASE TABLE only)."""
        # Hanya untuk BASE TABLE
        with self._engine.connect() as conn:
            try:
                result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
                return [dict(row._mapping) for row in result]
            except Exception:
                return []
    
    def _get_table_comment(self, table_name: str) -> Optional[str]:
        """Get table comment."""
        with self._engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT obj_description(:table_oid) as comment
                """),
                {"table_oid": self._inspector.get_table_oid(table_name)}
            )
            return result.scalar()
    
    def _audit_view(self, view_name: str) -> Dict[str, Any]:
        """Audit satu view."""
        return {
            "type": "view",
            "columns": self._get_columns_info(view_name),
            "definition": self._get_view_definition(view_name),
        }
    
    def _get_view_definition(self, view_name: str) -> str:
        """Get view definition."""
        with self._engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT pg_get_viewdef(:view_oid) as definition
                """),
                {"view_oid": self._inspector.get_table_oid(view_name)}
            )
            return result.scalar() or ""
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get database version and info."""
        with self._engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            return {
                "version": result.scalar(),
                "engine": "postgresql",
            }
    
    def _generate_summary(self, report: Dict) -> Dict:
        """Generate summary statistics."""
        tables = report["tables"]
        return {
            "total_tables": len(tables),
            "total_views": len(report.get("views", {})),
            "total_rows_estimate": sum(t.get("row_count_estimate", 0) for t in tables.values()),
            "tables_with_case_id": [
                name for name, data in tables.items()
                if any(c["name"] == "case_id" for c in data["columns"])
            ],
        }
    
    def save_report(self, report: Dict, path: Path = Path("schema_report.json")):
        """Save report to file."""
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Schema report saved to {path}")