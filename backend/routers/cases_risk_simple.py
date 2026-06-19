# ============================================================
# SIMPLE RISK INTELLIGENCE ENDPOINTS (tanpa tabel yang tidak ada)
# ============================================================

@router.get("/{case_id}/risk-simple")
async def get_case_risk_simple(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get risk score for a case (simple version)"""
    try:
        # Get case data
        result = await db.execute(
            text("""
                SELECT id, title, priority, status
                FROM cases WHERE id = :case_id
            """),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Simple risk calculation based on priority
        priority_scores = {"LOW": 25, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 95}
        risk_score = priority_scores.get(row[2], 50)
        
        if risk_score >= 75:
            risk_level = "HIGH"
        elif risk_score >= 50:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "case_id": case_id,
            "title": row[1],
            "priority": row[2],
            "status": row[3],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "note": "Simple risk calculation based on priority"
        }
    except Exception as e:
        return {"case_id": case_id, "error": str(e)}


@router.get("/risk-stats")
async def get_risk_stats_simple(
    db: AsyncSession = Depends(get_db)
):
    """Get simple risk statistics"""
    try:
        # Get all cases
        result = await db.execute(
            text("""
                SELECT priority, COUNT(*) as count
                FROM cases
                GROUP BY priority
            """)
        )
        rows = result.fetchall()
        
        priority_counts = {r[0]: r[1] for r in rows}
        
        # Calculate risk levels
        total = sum(priority_counts.values())
        high_risk = priority_counts.get("HIGH", 0) + priority_counts.get("CRITICAL", 0)
        
        return {
            "total_cases": total,
            "high_risk_cases": high_risk,
            "medium_risk_cases": priority_counts.get("MEDIUM", 0),
            "low_risk_cases": priority_counts.get("LOW", 0),
            "risk_percentage": round((high_risk / total * 100), 1) if total > 0 else 0
        }
    except Exception as e:
        return {"error": str(e)}
