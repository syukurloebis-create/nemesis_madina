from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from database import get_db

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/{case_id}/explain")
async def get_risk_explanation(
    case_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed explanation of why a case is flagged as risky."""
    try:
        try:
            uuid.UUID(case_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid case_id format")
        
        # Get case basic info
        case_result = await db.execute(
            text("""
                SELECT id, title, priority, status, risk_score, risk_level
                FROM cases 
                WHERE id = :case_id
            """),
            {"case_id": case_id}
        )
        case_row = case_result.fetchone()
        
        if not case_row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Convert row to dict
        case = {
            "id": str(case_row[0]),
            "title": case_row[1],
            "priority": case_row[2],
            "status": case_row[3],
            "risk_score": float(case_row[4]) if case_row[4] else 0,
            "risk_level": case_row[5] if case_row[5] else "LOW"
        }
        
        # Get risk explanations
        explain_result = await db.execute(
            text("""
                SELECT factor, score, weight, contribution, description, evidence_reference
                FROM risk_explanations
                WHERE case_id = :case_id
                ORDER BY contribution DESC
            """),
            {"case_id": case_id}
        )
        explanation_rows = explain_result.fetchall()
        
        explanations = []
        for row in explanation_rows:
            explanations.append({
                "factor": row[0],
                "score": float(row[1]),
                "weight": float(row[2]),
                "contribution": float(row[3]),
                "description": row[4],
                "evidence_reference": row[5]
            })
        
        if not explanations:
            explanations = await generate_simple_explanation(case_id, case["risk_score"], db)
        
        confidence = calculate_confidence(explanations)
        recommendations = generate_recommendations(explanations)
        
        return {
            "case_id": case_id,
            "title": case["title"],
            "priority": case["priority"],
            "status": case["status"],
            "total_risk_score": case["risk_score"],
            "risk_level": case["risk_level"],
            "confidence_score": confidence,
            "risk_contributors": explanations,
            "recommendations": recommendations,
            "explanation_available": len(explanations) > 0
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e), "case_id": case_id}


@router.post("/{case_id}/explain/generate")
async def generate_and_store_risk_explanation(
    case_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Generate and store risk explanation for a case."""
    try:
        case_result = await db.execute(
            text("SELECT id, risk_score FROM cases WHERE id = :case_id"),
            {"case_id": case_id}
        )
        case = case_result.fetchone()
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        await db.execute(
            text("DELETE FROM risk_explanations WHERE case_id = :case_id"),
            {"case_id": case_id}
        )
        
        explanations = await generate_and_save_simple_explanations(case_id, float(case[1]) if case[1] else 0, db)
        
        return {
            "success": True,
            "case_id": case_id,
            "explanations_generated": len(explanations),
            "message": "Risk explanation generated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

async def generate_simple_explanation(case_id: str, risk_score: float, db: AsyncSession) -> List:
    """Generate simple risk explanation based on case data"""
    explanations = []
    
    # Factor berdasarkan priority
    priority_result = await db.execute(
        text("SELECT priority FROM cases WHERE id = :case_id"),
        {"case_id": case_id}
    )
    priority = priority_result.scalar()
    
    if priority in ['HIGH', 'CRITICAL']:
        explanations.append({
            "factor": "priority_level",
            "score": 35.0 if priority == 'HIGH' else 50.0,
            "weight": 0.35,
            "contribution": 0.0,
            "description": f"Kasus memiliki prioritas {priority} yang memerlukan perhatian segera",
            "evidence_reference": "cases.priority"
        })
    
    # Evidence count
    evidence_result = await db.execute(
        text("SELECT COUNT(*) FROM evidence WHERE case_id = :case_id"),
        {"case_id": case_id}
    )
    evidence_count = evidence_result.scalar() or 0
    
    if evidence_count == 0:
        explanations.append({
            "factor": "insufficient_evidence",
            "score": 20.0,
            "weight": 0.20,
            "contribution": 0.0,
            "description": "Belum ada bukti digital yang diunggah untuk kasus ini",
            "evidence_reference": "evidence"
        })
    elif evidence_count < 3:
        explanations.append({
            "factor": "limited_evidence",
            "score": 10.0,
            "weight": 0.10,
            "contribution": 0.0,
            "description": f"Hanya {evidence_count} bukti yang tersedia, perlu pengumpulan tambahan",
            "evidence_reference": "evidence"
        })
    
    # Collusion relationships
    collusion_result = await db.execute(
        text("SELECT COUNT(*) FROM graph_relationships WHERE relationship_type IN ('collusion', 'financial')")
    )
    collusion_count = collusion_result.scalar() or 0
    
    if collusion_count > 0:
        explanations.append({
            "factor": "collusion_network",
            "score": min(30.0, 15.0 + collusion_count * 3),
            "weight": 0.30,
            "contribution": 0.0,
            "description": f"Terlibat dalam jaringan kolusi dengan {collusion_count} hubungan terdeteksi",
            "evidence_reference": "graph_relationships"
        })
    
    # Calculate contributions
    total_weighted = sum(e["score"] * e["weight"] for e in explanations)
    for e in explanations:
        e["contribution"] = round((e["score"] * e["weight"]) / max(total_weighted, 1) * 100, 1)
    
    return explanations


async def generate_and_save_simple_explanations(case_id: str, risk_score: float, db: AsyncSession) -> List:
    """Generate and save simple risk explanations"""
    explanations = []
    
    # Priority factor
    priority_result = await db.execute(
        text("SELECT priority FROM cases WHERE id = :case_id"),
        {"case_id": case_id}
    )
    priority = priority_result.scalar()
    
    if priority in ['HIGH', 'CRITICAL']:
        score = 35.0 if priority == 'HIGH' else 50.0
        explanation = {
            "factor": "priority_level",
            "score": score,
            "weight": 0.35,
            "contribution": 0.0,
            "description": f"Kasus memiliki prioritas {priority} yang memerlukan perhatian segera",
            "evidence_reference": "cases.priority"
        }
        explanations.append(explanation)
        await save_explanation(case_id, explanation, db)
    
    # Evidence factor
    evidence_result = await db.execute(
        text("SELECT COUNT(*) FROM evidence WHERE case_id = :case_id"),
        {"case_id": case_id}
    )
    evidence_count = evidence_result.scalar() or 0
    
    if evidence_count == 0:
        explanation = {
            "factor": "insufficient_evidence",
            "score": 20.0,
            "weight": 0.20,
            "contribution": 0.0,
            "description": "Belum ada bukti digital yang diunggah untuk kasus ini",
            "evidence_reference": "evidence"
        }
        explanations.append(explanation)
        await save_explanation(case_id, explanation, db)
    
    # Collusion factor
    collusion_result = await db.execute(
        text("SELECT COUNT(*) FROM graph_relationships WHERE relationship_type IN ('collusion', 'financial')")
    )
    collusion_count = collusion_result.scalar() or 0
    
    if collusion_count > 0:
        explanation = {
            "factor": "collusion_network",
            "score": min(30.0, 15.0 + collusion_count * 3),
            "weight": 0.30,
            "contribution": 0.0,
            "description": f"Terlibat dalam jaringan kolusi dengan {collusion_count} hubungan terdeteksi",
            "evidence_reference": "graph_relationships"
        }
        explanations.append(explanation)
        await save_explanation(case_id, explanation, db)
    
    # Calculate contributions
    total_weighted = sum(e["score"] * e["weight"] for e in explanations)
    for e in explanations:
        e["contribution"] = round((e["score"] * e["weight"]) / max(total_weighted, 1) * 100, 1)
        await db.execute(
            text("""
                UPDATE risk_explanations 
                SET contribution = :contribution
                WHERE case_id = :case_id AND factor = :factor
            """),
            {"contribution": e["contribution"], "case_id": case_id, "factor": e["factor"]}
        )
    
    await db.commit()
    return explanations


async def save_explanation(case_id: str, explanation: Dict, db: AsyncSession):
    """Save single explanation to database"""
    await db.execute(
        text("""
            INSERT INTO risk_explanations (case_id, factor, score, weight, contribution, description, evidence_reference)
            VALUES (:case_id, :factor, :score, :weight, :contribution, :description, :evidence)
        """),
        {
            "case_id": case_id,
            "factor": explanation["factor"],
            "score": explanation["score"],
            "weight": explanation["weight"],
            "contribution": 0,
            "description": explanation["description"],
            "evidence": explanation["evidence_reference"]
        }
    )


def calculate_confidence(explanations: List) -> int:
    """Calculate confidence score based on available explanations"""
    if not explanations:
        return 50
    base_confidence = min(95, 60 + len(explanations) * 10)
    return base_confidence


def generate_recommendations(explanations: List) -> List[Dict[str, Any]]:
    """Generate recommendations based on risk factors"""
    recommendations = []
    
    for exp in explanations:
        factor = exp.get("factor", "")
        
        if factor == "priority_level":
            recommendations.append({
                "action": "Segera lakukan investigasi mendalam",
                "priority": "CRITICAL",
                "reason": "Kasus prioritas tinggi membutuhkan tindakan segera"
            })
        elif factor == "collusion_network":
            recommendations.append({
                "action": "Petakan semua hubungan dalam jaringan kolusi",
                "priority": "HIGH",
                "reason": "Multiple collusion connections detected"
            })
        elif factor == "insufficient_evidence":
            recommendations.append({
                "action": "Upload bukti tambahan untuk verifikasi",
                "priority": "MEDIUM",
                "reason": "Current evidence insufficient for investigation"
            })
        elif factor == "limited_evidence":
            recommendations.append({
                "action": "Kumpulkan bukti tambahan",
                "priority": "MEDIUM",
                "reason": "Evidence masih terbatas untuk investigasi lengkap"
            })
    
    if not recommendations:
        recommendations.append({
            "action": "Lanjutkan monitoring",
            "priority": "LOW",
            "reason": "Tidak ada faktor risiko tinggi terdeteksi"
        })
    
    return recommendations


@router.get("/explain/summary")
async def get_risk_explanation_summary(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get summary of risk explanations across all cases"""
    try:
        result = await db.execute(
            text("""
                SELECT 
                    factor,
                    COUNT(*) as occurrence,
                    AVG(score) as avg_score,
                    AVG(contribution) as avg_contribution
                FROM risk_explanations
                GROUP BY factor
                ORDER BY avg_contribution DESC
            """)
        )
        rows = result.fetchall()
        
        case_count_result = await db.execute(
            text("SELECT COUNT(DISTINCT case_id) FROM risk_explanations")
        )
        cases_with_explanations = case_count_result.scalar() or 0
        
        factor_distribution = []
        for row in rows:
            factor_distribution.append({
                "factor": row[0],
                "occurrence": row[1],
                "average_score": round(float(row[2]), 1) if row[2] else 0,
                "average_contribution": round(float(row[3]), 1) if row[3] else 0
            })
        
        return {
            "cases_with_explanations": cases_with_explanations,
            "total_explanations": sum(r[1] for r in rows),
            "factor_distribution": factor_distribution
        }
    except Exception as e:
        return {"error": str(e)}
