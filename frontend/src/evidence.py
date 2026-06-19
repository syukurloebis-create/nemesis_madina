
@router.get("/top")
async def get_top_evidence(
    limit: int = Query(5, ge=1, le=20),
    session: AsyncSession = Depends(get_db)
):
    """Get top evidence by trust score"""
    try:
        result = await session.execute(
            text("""
                SELECT 
                    id,
                    filename,
                    status,
                    trust_score,
                    confidence_level,
                    uploaded_at
                FROM evidence
                WHERE trust_score IS NOT NULL
                ORDER BY trust_score DESC
                LIMIT :limit
            """),
            {"limit": limit}
        )
        rows = result.fetchall()
        return [
            {
                "id": row[0],
                "filename": row[1],
                "status": row[2],
                "trust_score": float(row[3]) if row[3] else 0,
                "confidence_level": row[4] or "LOW",
                "uploaded_at": row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]
    except Exception as e:
        return []
