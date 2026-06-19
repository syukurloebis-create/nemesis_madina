@router.get("/timeline/events")
async def get_events_timeline(
    days: int = Query(30, ge=1, le=365),
    aggregate_type: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db)
):
    """Get events per day for time series chart"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query safely
    if aggregate_type:
        result = await session.execute(
            text("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM events
                WHERE created_at >= :start_date AND aggregate_type = :agg_type
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """),
            {"start_date": start_date, "agg_type": aggregate_type}
        )
    else:
        result = await session.execute(
            text("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM events
                WHERE created_at >= :start_date
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """),
            {"start_date": start_date}
        )
    
    rows = result.fetchall()
    
    data = []
    for row in rows:
        date_val = row[0]
        count_val = row[1]
        data.append({
            "date": date_val.isoformat() if date_val else None,
            "count": count_val if count_val else 0
        })
    
    return {
        "data": data,
        "total_days": days,
        "total_events": sum(d["count"] for d in data)
    }
