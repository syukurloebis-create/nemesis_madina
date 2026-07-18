from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

from backend.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["Dashboard Metrics"])


@router.get("/timeline/cases")
async def get_cases_timeline(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db)
):
    """Get cases created per day for time series chart"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await session.execute(
        text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM cases
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
        "total_cases": sum(d["count"] for d in data)
    }


@router.get("/timeline/events")
async def get_events_timeline(
    days: int = Query(30, ge=1, le=365),
    aggregate_type: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db)
):
    """Get events per day for time series chart"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    try:
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
    except Exception as e:
        logger.error(f"Error in events timeline: {e}")
        return {
            "data": [],
            "total_days": days,
            "total_events": 0,
            "error": str(e)
        }


@router.get("/timeline/risks")
async def get_risks_timeline(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db)
):
    """Get risk scores over time"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await session.execute(
        text("""
            SELECT 
                DATE(calculated_at) as date,
                AVG(overall_score) as avg_score,
                COUNT(*) as count
            FROM risk_scores
            WHERE calculated_at >= :start_date
            GROUP BY DATE(calculated_at)
            ORDER BY date ASC
        """),
        {"start_date": start_date}
    )
    
    rows = result.fetchall()
    
    data = []
    for row in rows:
        date_val = row[0]
        avg_score = row[1]
        count_val = row[2]
        data.append({
            "date": date_val.isoformat() if date_val else None,
            "avg_score": float(avg_score) if avg_score else 0,
            "count": count_val if count_val else 0
        })
    
    return {"data": data}


@router.get("/integrity/hash-chain")
async def get_hash_chain_status(
    session: AsyncSession = Depends(get_db)
):
    """Get hash chain integrity status for all aggregates"""
    
    result = await session.execute(
        text("""
            SELECT 
                aggregate_type,
                aggregate_id,
                COUNT(*) as event_count,
                MAX(event_version) as max_version
            FROM events
            GROUP BY aggregate_type, aggregate_id
            ORDER BY aggregate_type
        """)
    )
    aggregates = result.fetchall()
    
    total_events = 0
    verified_count = 0
    
    for agg in aggregates:
        agg_id = agg[1]
        agg_type = agg[0]
        event_count = agg[2]
        total_events += event_count
        
        events_result = await session.execute(
            text("""
                SELECT event_hash, previous_hash, event_version
                FROM events
                WHERE aggregate_id = :agg_id AND aggregate_type = :agg_type
                ORDER BY event_version
            """),
            {"agg_id": agg_id, "agg_type": agg_type}
        )
        events = events_result.fetchall()
        
        chain_valid = True
        for i, event in enumerate(events):
            if i > 0 and event[1] != events[i-1][0]:
                chain_valid = False
                break
        
        if chain_valid:
            verified_count += 1
    
    return {
        "total_aggregates": len(aggregates),
        "verified_aggregates": verified_count,
        "total_events": total_events,
        "chain_integrity": verified_count == len(aggregates) if aggregates else True,
        "status": "HEALTHY" if verified_count == len(aggregates) else "COMPROMISED"
    }


@router.get("/alerts/recent")
async def get_recent_alerts(
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db)
):
    """Get recent alerts for live feed"""
    
    query = text("""
        SELECT 
            id, case_id, title, description, severity, status, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT :limit
    """)
    
    result = await session.execute(query, {"limit": limit})
    alerts = result.fetchall()
    
    alert_list = []
    for a in alerts:
        alert_list.append({
            "id": str(a[0]),
            "case_id": str(a[1]),
            "title": a[2],
            "description": a[3],
            "severity": a[4],
            "status": a[5],
            "timestamp": a[6].isoformat() if a[6] else None
        })
    
    if severity:
        alert_list = [a for a in alert_list if a["severity"] == severity]
    
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    alert_list.sort(key=lambda x: severity_order.get(x["severity"], 99))
    
    return {
        "alerts": alert_list,
        "total": len(alert_list),
        "severity_filter": severity
    }


@router.get("/system/health")
async def get_system_health(session: AsyncSession = Depends(get_db)):
    """Get comprehensive system health status"""
    
    try:
        await session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"
    
    result = await session.execute(text("SELECT COUNT(*) FROM events"))
    event_count = result.scalar() or 0
    
    result = await session.execute(text("SELECT COUNT(*) FROM cases"))
    case_count = result.scalar() or 0
    
    return {
        "status": "operational",
        "database": db_status,
        "metrics": {
            "total_events": event_count,
            "total_cases": case_count
        },
        "timestamp": datetime.utcnow().isoformat()
    }
