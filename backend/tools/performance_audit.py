"""
Performance Audit — EXPLAIN (ANALYZE) semua query.

Revisi:
    - Menggunakan bindparam untuk parameter
    - Mode SAFE (EXPLAIN) dan FULL (EXPLAIN ANALYZE)
"""

import json
from pathlib import Path
from typing import Dict, Any, Literal
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.engine import Engine

from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.sql_keys import SQLKey
from backend.core.database import DATABASE_URL


class PerformanceAudit:
    """
    Performance Audit — Menghasilkan explain_report.json.
    
    Modes:
        - safe: EXPLAIN only (no actual execution)
        - full: EXPLAIN ANALYZE (executes query)
    """
    
    def __init__(self, engine: Engine, mode: Literal["safe", "full"] = "safe"):
        self._engine = engine
        self._mode = mode
        self._sql_repo = SQLRepository().initialize()
        self._case_id = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    
    def audit(self) -> Dict[str, Any]:
        """Audit semua query."""
        report = {}
        
        for sql_key in SQLKey:
            report[sql_key.name] = self._explain(sql_key)
        
        return report
    
    def _explain(self, sql_key: SQLKey) -> Dict[str, Any]:
        """EXPLAIN for one query."""
        sql = self._sql_repo.load(sql_key)
        
        # Build explain command
        if self._mode == "full":
            explain_cmd = "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)"
        else:
            explain_cmd = "EXPLAIN (FORMAT JSON)"
        
        # Use bindparam for safety
        stmt = text(f"{explain_cmd} {sql}")
        stmt = stmt.bindparams(bindparam("case_id", self._case_id))
        
        with self._engine.connect() as conn:
            result = conn.execute(stmt)
            explain = result.fetchone()[0]
        
        return {
            "sql": sql,
            "mode": self._mode,
            "explain": explain,
            "cost": self._extract_cost(explain),
            "rows": self._extract_rows(explain),
            "time_ms": self._extract_time(explain) if self._mode == "full" else None,
        }
    
    def _extract_cost(self, explain: List) -> float:
        """Extract cost from explain plan."""
        try:
            return float(explain[0]["Plan"]["Total Cost"])
        except (IndexError, KeyError):
            return 0.0
    
    def _extract_rows(self, explain: List) -> int:
        """Extract rows from explain plan."""
        try:
            return int(explain[0]["Plan"]["Plan Rows"])
        except (IndexError, KeyError):
            return 0
    
    def _extract_time(self, explain: List) -> float:
        """Extract time from explain plan."""
        try:
            return float(explain[0]["Execution Time"])
        except (IndexError, KeyError):
            return 0.0
    
    def save_report(self, report: Dict, path: Path = Path("explain_report.json")):
        """Save report to file."""
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"EXPLAIN report saved to {path}")