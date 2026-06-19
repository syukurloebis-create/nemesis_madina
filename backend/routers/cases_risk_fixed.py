# ============================================================
# FIXED RISK INTELLIGENCE ENDPOINTS
# ============================================================

@router.get("/risk/dashboard")
async def get_risk_dashboard_fixed(
    db: AsyncSession = Depends(get_db)
):
    """Get risk distribution dashboard (fixed)"""
    try:
        # Get risk distribution from cases
        result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN risk_level = 'CRITICAL' THEN 1 END) as critical,
                    COUNT(CASE WHEN risk_level = 'HIGH' THEN 1 END) as high,
                    COUNT(CASE WHEN risk_level = 'MEDIUM' THEN 1 END) as medium,
                    COUNT(CASE WHEN risk_level = 'LOW' THEN 1 END) as low,
                    AVG(CAST(risk_score AS DECIMAL)) as avg_risk_score
                FROM cases
            """)
        )
        row = result.fetchone()
        
        # Get high risk cases
        high_risk_result = await db.execute(
            text("""
                SELECT id, title, COALESCE(risk_score, 0) as risk_score, 
                       COALESCE(risk_level, 'LOW') as risk_level, priority
                FROM cases
                WHERE COALESCE(risk_level, 'LOW') IN ('HIGH', 'CRITICAL')
                ORDER BY COALESCE(risk_score, 0) DESC
                LIMIT 10
            """)
        )
        high_risk_cases = high_risk_result.fetchall()
        
        return {
            "risk_distribution": {
                "total_cases": row[0] or 0,
                "critical": row[1] or 0,
                "high": row[2] or 0,
                "medium": row[3] or 0,
                "low": row[4] or 0,
                "average_risk_score": round(float(row[5] or 0), 1)
            },
            "high_risk_cases": [
                {
                    "id": str(c[0]),
                    "title": c[1],
                    "risk_score": float(c[2]),
                    "risk_level": c[3],
                    "priority": c[4]
                }
                for c in high_risk_cases
            ],
            "total_exposure": 0,
            "exposure_formatted": "Rp0"
        }
    except Exception as e:
        return {"error": str(e), "risk_distribution": {"total_cases": 0}}


@router.get("/risk/entities")
async def get_high_risk_entities_fixed(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get high risk entities from procurement data (fixed)"""
    try:
        # Query langsung dari rup_paket_detailed
        result = await db.execute(
            text("""
                SELECT 
                    vendor_name,
                    COUNT(*) as package_count,
                    SUM(CAST(pagu AS DECIMAL)) as total_value
                FROM rup_paket_detailed
                WHERE vendor_name IS NOT NULL
                GROUP BY vendor_name
                ORDER BY total_value DESC
                LIMIT :limit
            """),
            {"limit": limit}
        )
        rows = result.fetchall()
        
        return {
            "entities": [
                {
                    "name": r[0],
                    "package_count": r[1],
                    "total_value": float(r[2]) if r[2] else 0,
                    "risk_score": 50,  # Default score
                    "risk_level": "MEDIUM"
                }
                for r in rows
            ],
            "total": len(rows)
        }
    except Exception as e:
        return {"entities": [], "error": str(e)}
