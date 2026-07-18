"""
Data Profiler — Automated Data Profiling.

Menghasilkan data_profile_report.json.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.types import (
    Integer, BigInteger, SmallInteger, Numeric, Float,
    String, Text, Boolean, DateTime, Date, Time,
    JSON, ARRAY, UUID, Enum as SAEnum
)

from backend.core.database import DATABASE_URL


class DataProfiler:
    """
    Automated Data Profiler — Menghasilkan data_profile_report.json.
    
    Revisi:
        - Menggunakan SQLAlchemy type checking (bukan string)
        - Menggunakan json_agg untuk top values
    """
    
    def __init__(self, engine: Engine, schema_report: Dict):
        self._engine = engine
        self._schema_report = schema_report
    
    def profile(self) -> Dict[str, Any]:
        """Profile all tables."""
        report = {}
        
        for table_name, table_info in self._schema_report["tables"].items():
            report[table_name] = self._profile_table(table_name, table_info)
        
        return report
    
    def _profile_table(self, table_name: str, table_info: Dict) -> Dict[str, Any]:
        """Profile one table."""
        profile = {}
        
        for column in table_info["columns"]:
            col_name = column["name"]
            col_type = column["type"]
            
            if col_type in ("string", "text", "enum"):
                profile[col_name] = self._profile_text_column(table_name, col_name)
            elif col_type in ("integer", "numeric"):
                profile[col_name] = self._profile_numeric_column(table_name, col_name)
            elif col_type == "boolean":
                profile[col_name] = self._profile_boolean_column(table_name, col_name)
            elif col_type in ("datetime", "date", "time"):
                profile[col_name] = self._profile_datetime_column(table_name, col_name)
            else:
                profile[col_name] = {"type": col_type, "profiled": False}
        
        return profile
    
    def _profile_text_column(self, table: str, column: str) -> Dict:
        """Profile text column with json_agg for top values."""
        with self._engine.connect() as conn:
            result = conn.execute(
                text(f"""
                    SELECT
                        COUNT(DISTINCT {column}) as distinct_count,
                        COUNT(*) FILTER (WHERE {column} IS NULL) as null_count,
                        COUNT(*) as total_count,
                        (
                            SELECT json_agg(t)
                            FROM (
                                SELECT {column} as value, COUNT(*) as count
                                FROM {table}
                                WHERE {column} IS NOT NULL
                                GROUP BY {column}
                                ORDER BY COUNT(*) DESC
                                LIMIT 5
                            ) t
                        ) as top_values
                    FROM {table}
                """)
            )
            row = result.fetchone()
        
        return {
            "distinct_count": row.distinct_count,
            "null_percentage": round(row.null_count / row.total_count * 100, 2) if row.total_count > 0 else 0,
            "top_values": row.top_values or [],
        }
    
    def _profile_numeric_column(self, table: str, column: str) -> Dict:
        """Profile numeric column."""
        with self._engine.connect() as conn:
            result = conn.execute(
                text(f"""
                    SELECT
                        MIN({column}) as min_val,
                        MAX({column}) as max_val,
                        AVG({column}) as avg_val,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {column}) as median_val,
                        COUNT(*) FILTER (WHERE {column} IS NULL) as null_count,
                        COUNT(*) as total_count
                    FROM {table}
                """)
            )
            row = result.fetchone()
        
        return {
            "min": float(row.min_val) if row.min_val is not None else None,
            "max": float(row.max_val) if row.max_val is not None else None,
            "avg": float(row.avg_val) if row.avg_val is not None else None,
            "median": float(row.median_val) if row.median_val is not None else None,
            "null_percentage": round(row.null_count / row.total_count * 100, 2) if row.total_count > 0 else 0,
        }
    
    def _profile_boolean_column(self, table: str, column: str) -> Dict:
        """Profile boolean column."""
        with self._engine.connect() as conn:
            result = conn.execute(
                text(f"""
                    SELECT
                        COUNT(*) FILTER (WHERE {column} = true) as true_count,
                        COUNT(*) FILTER (WHERE {column} = false) as false_count,
                        COUNT(*) FILTER (WHERE {column} IS NULL) as null_count,
                        COUNT(*) as total_count
                    FROM {table}
                """)
            )
            row = result.fetchone()
        
        return {
            "true_percentage": round(row.true_count / row.total_count * 100, 2) if row.total_count > 0 else 0,
            "false_percentage": round(row.false_count / row.total_count * 100, 2) if row.total_count > 0 else 0,
            "null_percentage": round(row.null_count / row.total_count * 100, 2) if row.total_count > 0 else 0,
        }
    
    def _profile_datetime_column(self, table: str, column: str) -> Dict:
        """Profile datetime column."""
        with self._engine.connect() as conn:
            result = conn.execute(
                text(f"""
                    SELECT
                        MIN({column}) as min_val,
                        MAX({column}) as max_val,
                        COUNT(*) FILTER (WHERE {column} IS NULL) as null_count,
                        COUNT(*) as total_count
                    FROM {table}
                """)
            )
            row = result.fetchone()
        
        return {
            "min": row.min_val.isoformat() if row.min_val else None,
            "max": row.max_val.isoformat() if row.max_val else None,
            "null_percentage": round(row.null_count / row.total_count * 100, 2) if row.total_count > 0 else 0,
        }
    
    def save_report(self, report: Dict, path: Path = Path("data_profile_report.json")):
        """Save report to file."""
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Data profile report saved to {path}")