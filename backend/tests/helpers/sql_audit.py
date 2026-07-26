# tests/helpers/sql_audit.py

"""
SQL Audit Helper — Untuk SQL parity test.

Mengambil expected values dari database berdasarkan query SQL yang sama
dengan yang digunakan collector.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID


class SQLAuditHelper:
    """Helper untuk SQL parity test."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_fraud_expected(self, case_id: UUID):
        """Get expected fraud summary from SQL."""
        result = await self._session.execute(
            text("""
                SELECT
                    COUNT(*) as total_patterns,
                    COUNT(*) FILTER (WHERE UPPER(severity) = 'CRITICAL') as critical,
                    COUNT(*) FILTER (WHERE UPPER(severity) = 'HIGH') as high,
                    COUNT(*) FILTER (WHERE UPPER(severity) = 'MEDIUM') as medium,
                    COUNT(*) FILTER (WHERE UPPER(severity) = 'LOW') as low
                FROM pattern_detections
                WHERE case_id = CAST(:case_id AS UUID)
            """),
            {"case_id": str(case_id)}
        )
        row = result.first()
        return row