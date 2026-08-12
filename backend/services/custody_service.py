"""
Custody Service
Handles evidence custody chain logic
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class CustodyService:
    """Service for managing evidence custody chain"""

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def record_transfer(
        self,
        evidence_id: str,
        from_custodian: str,
        to_custodian: str,
        reason: str,
        transferred_by: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record custody transfer with semantic and concurrency integrity."""

        # ============================================================
        # H3/H4 — INPUT VALIDATION
        # ============================================================

        if not evidence_id:
            raise ValueError("evidence_id is required")

        if not from_custodian:
            raise ValueError("from_custodian is required")

        if not to_custodian:
            raise ValueError("to_custodian is required")

        if from_custodian == to_custodian:
            raise ValueError(
                "from_custodian and to_custodian must be different"
            )

        if not reason:
            raise ValueError("reason is required")

        if not transferred_by:
            raise ValueError("transferred_by is required")

        # ============================================================
        # TRANSACTIONAL STATE VALIDATION
        #
        # Lock the current active custody row before validating
        # from_custodian. This closes the race window between:
        #   read current state -> validate -> update state.
        # ============================================================

        current_query = text("""
            SELECT
                id,
                to_custodian,
                transferred_at
            FROM custody_chain
            WHERE evidence_id = :evidence_id
              AND tenant_id = :tenant_id
              AND status = 'active'
            ORDER BY transferred_at DESC, id DESC
            LIMIT 1
            FOR UPDATE
        """)

        result = await self.db.execute(
            current_query,
            {
                "evidence_id": evidence_id,
                "tenant_id": self.tenant_id,
            },
        )

        current_row = result.fetchone()

        # ============================================================
        # H3 — FROM CUSTODIAN CONSISTENCY
        # ============================================================

        if current_row is None:
            raise ValueError(
                f"No active custody record exists for evidence "
                f"'{evidence_id}'"
            )

        current_custodian = current_row[1]

        if from_custodian != current_custodian:
            raise ValueError(
                f"from_custodian '{from_custodian}' does not match "
                f"current custodian '{current_custodian}'"
            )

        # ============================================================
        # H4 — TRANSITION INTEGRITY
        # ============================================================

        if to_custodian == current_custodian:
            raise ValueError(
                "to_custodian must differ from current custodian"
            )

        # ============================================================
        # CREATE TRANSFER
        # ============================================================

        transfer_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # Close current active record.
        close_query = text("""
            UPDATE custody_chain
            SET
                status = 'closed',
                updated_at = :updated_at
            WHERE id = :id
              AND evidence_id = :evidence_id
              AND tenant_id = :tenant_id
              AND status = 'active'
        """)

        close_result = await self.db.execute(
            close_query,
            {
                "id": current_row[0],
                "evidence_id": evidence_id,
                "tenant_id": self.tenant_id,
                "updated_at": now,
            },
        )

        # Defensive invariant check.
        if close_result.rowcount != 1:
            await self.db.rollback()
            raise RuntimeError(
                "Custody state changed unexpectedly while recording transfer"
            )

        # Create new active custody record.
        insert_query = text("""
            INSERT INTO custody_chain (
                id,
                evidence_id,
                from_custodian,
                to_custodian,
                reason,
                transferred_by,
                transferred_at,
                status,
                notes,
                tenant_id,
                created_at,
                updated_at
            )
            VALUES (
                :id,
                :evidence_id,
                :from_custodian,
                :to_custodian,
                :reason,
                :transferred_by,
                :transferred_at,
                'active',
                :notes,
                :tenant_id,
                :created_at,
                :updated_at
            )
        """)

        await self.db.execute(
            insert_query,
            {
                "id": transfer_id,
                "evidence_id": evidence_id,
                "from_custodian": from_custodian,
                "to_custodian": to_custodian,
                "reason": reason,
                "transferred_by": transferred_by,
                "transferred_at": now,
                "notes": notes,
                "tenant_id": self.tenant_id,
                "created_at": now,
                "updated_at": now,
            },
        )

        # ============================================================
        # ATOMIC COMMIT
        # ============================================================

        await self.db.commit()

        return {
            "id": transfer_id,
            "evidence_id": evidence_id,
            "from_custodian": from_custodian,
            "to_custodian": to_custodian,
            "reason": reason,
            "transferred_by": transferred_by,
            "transferred_at": now.isoformat(),
            "status": "active",
            "notes": notes,
        }

    async def get_current_custodian(self, evidence_id: str) -> Optional[str]:
        """Get current custodian for evidence"""
        query = text("""
            SELECT to_custodian
            FROM custody_chain
            WHERE evidence_id = :evidence_id
              AND tenant_id = :tenant_id
              AND status = 'active'
            ORDER BY transferred_at DESC, id DESC
            LIMIT 1
        """)

        result = await self.db.execute(query, {
            "evidence_id": evidence_id,
            "tenant_id": self.tenant_id
        })
        row = result.fetchone()
        return row[0] if row else None

    async def get_custody_history(self, evidence_id: str) -> List[Dict[str, Any]]:
        """Get complete custody history"""
        query = text("""
            SELECT
                id,
                from_custodian,
                to_custodian,
                reason,
                transferred_by,
                transferred_at,
                status,
                notes
            FROM custody_chain
            WHERE evidence_id = :evidence_id
              AND tenant_id = :tenant_id
            ORDER BY transferred_at ASC, id ASC
        """)

        result = await self.db.execute(query, {
            "evidence_id": evidence_id,
            "tenant_id": self.tenant_id
        })
        rows = result.fetchall()

        return [
            {
                "id": row[0],
                "from_custodian": row[1],
                "to_custodian": row[2],
                "reason": row[3],
                "transferred_by": row[4],
                "transferred_at": row[5].isoformat() if row[5] else None,
                "status": row[6],
                "notes": row[7]
            }
            for row in rows
        ]

    async def record_access(
        self,
        evidence_id: str,
        accessed_by: str,
        access_type: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """Record evidence access"""
        access_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        query = text("""
            INSERT INTO access_log (
                id, evidence_id, accessed_by, access_type,
                reason, duration, accessed_at,
                status, tenant_id, created_at
            ) VALUES (
                :id, :evidence_id, :accessed_by, :access_type,
                :reason, :duration, :accessed_at, 'recorded',
                :tenant_id, :created_at
            )
        """)

        await self.db.execute(query, {
            "id": access_id,
            "evidence_id": evidence_id,
            "accessed_by": accessed_by,
            "access_type": access_type,
            "reason": reason,
            "duration": duration,
            "accessed_at": now,
            "tenant_id": self.tenant_id,
            "created_at": now
        })

        await self.db.commit()

        return {
            "id": access_id,
            "evidence_id": evidence_id,
            "accessed_by": accessed_by,
            "access_type": access_type,
            "reason": reason,
            "duration": duration,
            "accessed_at": now.isoformat(),
            "status": "recorded"
        }

    async def get_access_history(self, evidence_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get access history"""
        query = text("""
            SELECT
                id,
                accessed_by,
                access_type,
                reason,
                duration,
                accessed_at,
                status
            FROM access_log
            WHERE evidence_id = :evidence_id
              AND tenant_id = :tenant_id
            ORDER BY accessed_at DESC
            LIMIT :limit
        """)

        result = await self.db.execute(query, {
            "evidence_id": evidence_id,
            "tenant_id": self.tenant_id,
            "limit": limit
        })
        rows = result.fetchall()

        return [
            {
                "id": row[0],
                "accessed_by": row[1],
                "access_type": row[2],
                "reason": row[3],
                "duration": row[4],
                "accessed_at": row[5].isoformat() if row[5] else None,
                "status": row[6]
            }
            for row in rows
        ]