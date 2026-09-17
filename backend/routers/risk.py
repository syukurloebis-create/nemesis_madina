"""
Risk Router - Canonical Risk API

All risk data comes from the canonical risk_scores table.
NO hardcoded values.

Canonical flow:
    SOURCE DATA (findings, graph, fraud, evidence)
        |
        v
    IntelligenceService.calculate()
        |
        v
    risk_scores (persistence)
        |
        v
    dashboard_view (read model)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.dependencies.auth import require_intelligence_view

router = APIRouter(
    tags=["Risk"],
    dependencies=[Depends(require_intelligence_view)],
)


@router.get("/stats")
async def get_risk_stats(db: AsyncSession = Depends(get_db)):
    """Get risk statistics from canonical risk_scores table."""
    try:
        from sqlalchemy import text
        result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN risk_level::text = 'CRITICAL' THEN 1 END) as critical,
                COUNT(CASE WHEN risk_level::text = 'HIGH' THEN 1 END) as high,
                COUNT(CASE WHEN risk_level::text = 'MEDIUM' THEN 1 END) as medium,
                COUNT(CASE WHEN risk_level::text = 'LOW' THEN 1 END) as low,
                COALESCE(AVG(overall_score), 0) as avg_score
            FROM risk_scores
        """))
        row = result.fetchone()

        if not row or row[0] == 0:
            return {
                "status": "NO_DATA",
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "avg_score": 0,
                "message": "No risk assessments have been computed",
                "timestamp": datetime.now().isoformat()
            }

        return {
            "status": "OK",
            "total": int(row[0]),
            "critical": int(row[1]),
            "high": int(row[2]),
            "medium": int(row[3]),
            "low": int(row[4]),
            "avg_score": round(float(row[5]), 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/explanations/{case_id}")
async def get_risk_explanations(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get risk explanations from canonical risk_scores table."""
    try:
        from sqlalchemy import text
        result = await db.execute(text("""
            SELECT
                overall_score,
                risk_level::text,
                anomaly_score,
                collusion_score,
                financial_score,
                temporal_score,
                factors,
                recommendations,
                calculated_at
            FROM risk_scores
            WHERE case_id = CAST(:case_id AS uuid)
            ORDER BY calculated_at DESC
            LIMIT 1
        """), {"case_id": case_id})

        row = result.fetchone()

        if not row:
            return {
                "case_id": case_id,
                "status": "NO_DATA",
                "score": None,
                "risk_level": "NO_DATA",
                "factors": [],
                "recommendations": [],
                "message": "No risk assessment has been computed for this case",
                "timestamp": datetime.now().isoformat()
            }

        return {
            "case_id": case_id,
            "status": "OK",
            "score": float(row[0]),
            "risk_level": row[1],
            "anomaly_score": float(row[2]) if row[2] else 0,
            "collusion_score": float(row[3]) if row[3] else 0,
            "financial_score": float(row[4]) if row[4] else 0,
            "temporal_score": float(row[5]) if row[5] else 0,
            "factors": row[6] or [],
            "recommendations": row[7] or [],
            "calculated_at": row[8].isoformat() if row[8] else None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "case_id": case_id,
            "status": "ERROR",
            "message": str(e),
            "score": None,
            "risk_level": "ERROR",
            "factors": [],
            "timestamp": datetime.now().isoformat()
        }


@router.post("/calculate/{case_id}")
async def calculate_risk(
    case_id: str,
    fraud_score: float = Query(0, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate and persist risk for a case.

    Uses IntelligenceService.calculate() as CANONICAL risk engine.
    """
    try:
        from sqlalchemy import text
        from backend.intelligence.service import IntelligenceService
        import json

        # Step 1: Get graph data from latest_graph JSON
        graph_result = await db.execute(text("""
            SELECT latest_graph
            FROM dashboard_view
            WHERE case_id = :case_id
        """), {"case_id": case_id})
        graph_row = graph_result.fetchone()

        graph_entities = 0
        graph_relationships = 0

        if graph_row and graph_row[0]:
            graph_data = graph_row[0]
            if isinstance(graph_data, str):
                graph_data = json.loads(graph_data)
            graph_entities = int(graph_data.get('entities', 0))
            graph_relationships = int(graph_data.get('relationships', 0))

        if graph_entities > 0:
            density = graph_relationships / graph_entities
            graph_risk = min(100, (graph_entities * 0.05) + (density * 10))
        else:
            graph_risk = 0

        # Step 2: Get evidence trust
        evidence_result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN LOWER(status) = 'verified' THEN 1 END) as verified,
                COALESCE(AVG(trust_score), 0) as avg_trust
            FROM evidence
            WHERE case_id = :case_id
        """), {"case_id": case_id})
        ev_row = evidence_result.fetchone()

        total_ev = int(ev_row[0]) if ev_row and ev_row[0] else 0
        verified_ev = int(ev_row[1]) if ev_row and ev_row[1] else 0
        avg_trust = float(ev_row[2]) if ev_row and ev_row[2] else 0

        if total_ev > 0:
            evidence_trust = (avg_trust * 0.7) + ((verified_ev / total_ev) * 100 * 0.3)
        else:
            evidence_trust = 0

        # Step 3: Compute findings_risk (SOURCE-BASED)
        findings_result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN severity = 'CRITICAL' THEN 1 END) as critical,
                COUNT(CASE WHEN severity = 'HIGH' THEN 1 END) as high
            FROM findings
            WHERE case_id = :case_id
        """), {"case_id": case_id})
        find_row = findings_result.fetchone()

        total_findings = int(find_row[0]) if find_row and find_row[0] else 0
        critical_findings = int(find_row[1]) if find_row and find_row[1] else 0
        high_findings = int(find_row[2]) if find_row and find_row[2] else 0

        if total_findings == 0:
            findings_risk = 0
        else:
            findings_risk = min(100, (critical_findings * 30) + (high_findings * 15))

        # Step 4: Semantic inversion - trust to risk
        # NO_DATA: evidence tidak tersedia, BUKAN berarti maximum risk.
        # Ini koreksi false positive: 0 evidence → evidence_risk = 0,
        # bukan 100. Redistribusi bobot akan diimplementasikan di P1.
        if total_ev > 0:
            evidence_risk = 100 - evidence_trust
        else:
            evidence_risk = 0

        # Step 5: Calculate via CANONICAL Risk Engine
        result = IntelligenceService.calculate(
            findings_risk=findings_risk,
            graph_risk=graph_risk,
            fraud_risk=fraud_score,
            evidence_risk=evidence_risk,
        )

        # Step 6: Persist to risk_scores (atomic upsert)
        components = result.components
        weights = result.weights

        await db.execute(text("""
            INSERT INTO risk_scores (
                id, case_id, overall_score, risk_level,
                findings_risk, graph_risk, fraud_risk, evidence_risk,
                components, weights,
                anomaly_score, collusion_score, financial_score, temporal_score,
                factors, recommendations, calculated_at, calculated_by
            ) VALUES (
                gen_random_uuid()::text,
                CAST(:case_id AS uuid),
                :score,
                CAST(:level AS risklevel),
                :findings_risk, :graph_risk, :fraud_risk, :evidence_risk,
                CAST(:components AS json), CAST(:weights AS json),
                :findings_risk, :graph_risk, :fraud_risk, 0,
                CAST(:factors AS json), CAST(:recommendations AS json),
                NOW(), 'API'
            )
            ON CONFLICT (case_id) DO UPDATE SET
                overall_score = EXCLUDED.overall_score,
                risk_level = EXCLUDED.risk_level,
                findings_risk = EXCLUDED.findings_risk,
                graph_risk = EXCLUDED.graph_risk,
                fraud_risk = EXCLUDED.fraud_risk,
                evidence_risk = EXCLUDED.evidence_risk,
                components = EXCLUDED.components,
                weights = EXCLUDED.weights,
                anomaly_score = EXCLUDED.anomaly_score,
                collusion_score = EXCLUDED.collusion_score,
                financial_score = EXCLUDED.financial_score,
                temporal_score = EXCLUDED.temporal_score,
                factors = EXCLUDED.factors,
                recommendations = EXCLUDED.recommendations,
                calculated_at = NOW(),
                calculated_by = 'API'
        """), {
            "case_id": case_id,
            "score": result.score,
            "level": result.level,
            "findings_risk": components.get("findings_risk", 0),
            "graph_risk": components.get("graph_risk", 0),
            "fraud_risk": components.get("fraud_risk", 0),
            "evidence_risk": components.get("evidence_risk", 0),
            "components": json.dumps(components),
            "weights": json.dumps(weights),
            "factors": json.dumps(result.factors),
            "recommendations": json.dumps(result.recommendations),
        })

        # Step 7: Update dashboard_view
        latest_risk_json = json.dumps({
            "score": result.score,
            "level": result.level,
            "findings_risk": result.components.get("findings_risk", 0),
            "graph_risk": result.components.get("graph_risk", 0),
            "fraud_risk": result.components.get("fraud_risk", 0),
            "evidence_risk": result.components.get("evidence_risk", 0),
            "recommendations": result.recommendations,
        })

        await db.execute(text("""
            UPDATE dashboard_view
            SET
                latest_risk = CAST(:latest_risk AS json),
                risk_score = :score,
                risk_level = :level,
                last_updated = NOW()
            WHERE case_id = :case_id
        """), {
            "case_id": case_id,
            "score": result.score,
            "level": result.level,
            "latest_risk": latest_risk_json,
        })

        await db.commit()

        return {
            "status": "OK",
            "case_id": case_id,
            "result": result.to_dict(),
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(500, detail=str(e))
