@router.get("/risk/trend")
async def get_risk_trend(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get risk trend over time"""
    try:
        # Gunakan CAST untuk parameter interval
        result = await db.execute(
            text(f"""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total_cases,
                    COUNT(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 END) as high_risk_cases
                FROM cases
                WHERE created_at >= NOW() - INTERVAL '{days} days'
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """)
        )
        rows = result.fetchall()
        
        return {
            "historical": [
                {
                    "date": str(r[0]) if r[0] else None,
                    "total_cases": r[1],
                    "high_risk_cases": r[2],
                    "risk_percentage": round((r[2] / r[1] * 100), 1) if r[1] > 0 else 0
                }
                for r in rows
            ],
            "trend_direction": "increasing" if len(rows) >= 2 and rows[-1][2] > rows[-2][2] else "decreasing" if len(rows) >= 2 else "stable"
        }
    except Exception as e:
        return {"error": str(e), "historical": []}
