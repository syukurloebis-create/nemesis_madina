@router.get("/prediction/case/{case_id}")
async def predict_case_outcome(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Predict case outcome"""
    try:
        # Cast string ke UUID
        result = await db.execute(
            text("""
                SELECT priority, status,
                       (SELECT COUNT(*) FROM evidence WHERE case_id = CAST(:case_id AS UUID)) as evidence_count
                FROM cases WHERE id = CAST(:case_id AS UUID)
            """),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        if not row:
            return {"error": "Case not found"}
        
        priority = row[0]
        evidence_count = row[2] or 0
        
        priority_scores = {"LOW": 25, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 95}
        risk_likelihood = priority_scores.get(priority, 50)
        
        # Adjust based on evidence
        if evidence_count >= 5:
            risk_likelihood = min(100, risk_likelihood + 15)
        elif evidence_count == 0:
            risk_likelihood = max(0, risk_likelihood - 10)
        
        estimated_duration = {"LOW": 14, "MEDIUM": 30, "HIGH": 60, "CRITICAL": 90}.get(priority, 30)
        
        return {
            "case_id": case_id,
            "predictions": {
                "high_risk_likelihood": risk_likelihood,
                "estimated_duration_days": estimated_duration,
                "evidence_sufficiency": "adequate" if evidence_count >= 3 else "insufficient",
                "recommended_action": "escalate" if risk_likelihood > 75 else "monitor" if risk_likelihood > 50 else "review"
            },
            "confidence_score": 75 + min(20, evidence_count * 2)
        }
    except Exception as e:
        return {"error": str(e)}
