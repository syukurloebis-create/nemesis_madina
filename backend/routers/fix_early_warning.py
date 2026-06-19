@router.get("/early-warning")
async def get_early_warnings(
    db: AsyncSession = Depends(get_db)
):
    try:
        # Stale cases
        stale_result = await db.execute(
            text("""
                SELECT id, title, created_at
                FROM cases
                WHERE status != 'CLOSED'
                ORDER BY created_at ASC
                LIMIT 5
            """)
        )
        stale_cases = stale_result.fetchall()
        
        return {
            "early_warnings": {
                "stale_cases": [
                    {"id": str(r[0]), "title": r[1], "created_at": r[2].isoformat() if r[2] else None}
                    for r in stale_cases
                ]
            },
            "alert_summary": {
                "total_warnings": len(stale_cases),
                "critical_count": 0
            }
        }
    except Exception as e:
        return {"error": str(e)}
