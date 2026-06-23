# ============================================================
# FIX: /nodes ENDPOINT - MENGGUNAKAN KOLOM YANG BENAR
# ============================================================

@router.get("/nodes")
async def get_graph_nodes(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get graph nodes (entities)"""
    try:
        query = """
            SELECT 
                id, 
                name, 
                entity_type, 
                risk_score,
                case_id,
                confidence,
                first_seen
            FROM graph_entities
            WHERE entity_type = 'vendor'
            ORDER BY risk_score DESC NULLS LAST
            LIMIT :limit
        """
        result = await db.execute(text(query), {"limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "risk_score": float(row[3]) if row[3] else 0,
                "case_id": row[4],
                "confidence": float(row[5]) if row[5] else 0,
                "first_seen": row[6].isoformat() if row[6] else None
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
