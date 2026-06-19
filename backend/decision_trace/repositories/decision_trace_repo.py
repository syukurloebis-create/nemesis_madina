"""Decision Trace Repository - Database operations"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
import json
from datetime import datetime

from backend.decision_trace.models import DecisionTrace, DecisionType


class DecisionTraceRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create(self, trace: DecisionTrace) -> DecisionTrace:
        """Create new decision trace"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO decision_trace (
                    trace_id, entity_id, entity_type, decision_type, score,
                    confidence, reasons, evidence_ids, lineage_ids,
                    feature_importance, model_version, created_by, created_at, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """,
                trace.trace_id,
                trace.entity_id,
                trace.entity_type,
                trace.decision_type.value if hasattr(trace.decision_type, 'value') else trace.decision_type,
                trace.score,
                trace.confidence,
                json.dumps(trace.reasons),
                [str(eid) for eid in trace.evidence_ids],
                trace.lineage_ids,
                json.dumps(trace.feature_importance),
                trace.model_version,
                trace.created_by,
                trace.created_at,
                json.dumps(trace.metadata)
            )
            return trace
    
    async def get_by_id(self, trace_id: UUID) -> Optional[DecisionTrace]:
        """Get decision trace by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM decision_trace WHERE trace_id = $1",
                trace_id
            )
            if row:
                return self._row_to_trace(row)
            return None
    
    async def get_by_entity(
        self,
        entity_id: str,
        limit: int = 50,
        decision_type: Optional[str] = None
    ) -> List[DecisionTrace]:
        """Get decision traces by entity"""
        query = "SELECT * FROM decision_trace WHERE entity_id = $1"
        params = [entity_id]
        param_index = 2
        
        if decision_type:
            query += f" AND decision_type = ${param_index}"
            params.append(decision_type)
            param_index += 1
        
        query += f" ORDER BY created_at DESC LIMIT ${param_index}"
        params.append(limit)
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_trace(row) for row in rows]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get decision trace statistics"""
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM decision_trace")
            by_type = await conn.fetch("""
                SELECT decision_type, COUNT(*) FROM decision_trace 
                GROUP BY decision_type
            """)
            
            return {
                "total_traces": total,
                "by_decision_type": {row['decision_type']: row['count'] for row in by_type}
            }
    
    def _row_to_trace(self, row) -> DecisionTrace:
        return DecisionTrace(
            trace_id=row['trace_id'],
            entity_id=row['entity_id'],
            entity_type=row['entity_type'],
            decision_type=row['decision_type'],
            score=row['score'],
            confidence=row['confidence'],
            reasons=json.loads(row['reasons']) if row['reasons'] else [],
            evidence_ids=[UUID(eid) for eid in row['evidence_ids']] if row['evidence_ids'] else [],
            lineage_ids=row['lineage_ids'] or [],
            feature_importance=json.loads(row['feature_importance']) if row['feature_importance'] else {},
            model_version=row['model_version'],
            created_by=row['created_by'],
            created_at=row['created_at'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
