from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from datetime import datetime, timedelta
from typing import Optional
from infrastructure.database import get_db
from security.auth import decode_token

router = APIRouter(prefix="/forensic", tags=["Forensic Dashboard"])

def get_user_info(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, None, None
    token = auth_header[7:]
    payload = decode_token(token)
    if not payload:
        return None, None, None
    return payload.get("institution_id"), payload.get("sub"), payload.get("role")


@router.get("/dashboard/unified")
async def get_unified_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Unified Forensic Dashboard - Satu endpoint untuk semua data dashboard"""
    institution_id, user_id, role = get_user_info(request)
    
    try:
        # Case statistics
        total_cases = 0
        cases_by_status = {}
        cases_by_priority = {}
        
        try:
            result = await db.execute(select(func.count()).select_from(text("cases")))
            total_cases = result.scalar() or 0
            
            result = await db.execute(text("SELECT status, COUNT(*) FROM cases GROUP BY status"))
            for row in result.fetchall():
                cases_by_status[row[0]] = row[1]
            
            result = await db.execute(text("SELECT priority, COUNT(*) FROM cases GROUP BY priority"))
            for row in result.fetchall():
                cases_by_priority[row[0]] = row[1]
        except Exception as e:
            print(f"Case stats error: {e}")
        
        # Integrity statistics
        total_events = 0
        hashed_events = 0
        integrity_score = 100
        
        try:
            result = await db.execute(select(func.count()).select_from(text("events")))
            total_events = result.scalar() or 0
            
            result = await db.execute(text("SELECT COUNT(*) FROM events WHERE event_hash IS NOT NULL"))
            hashed_events = result.scalar() or 0
            
            if total_events > 0:
                integrity_score = round((hashed_events / total_events) * 100, 2)
        except Exception as e:
            print(f"Integrity stats error: {e}")
        
        # Alert statistics
        alerts = {"total": 0, "critical": 0, "high": 0, "avg_risk_score": 0}
        try:
            result = await db.execute(text("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical,
                       COUNT(CASE WHEN severity = 'high' THEN 1 END) as high
                FROM alerts WHERE resolved = false
            """))
            row = result.fetchone()
            if row:
                alerts = {
                    "total": row[0] or 0,
                    "critical": row[1] or 0,
                    "high": row[2] or 0,
                    "avg_risk_score": 0
                }
        except Exception as e:
            print(f"Alert stats error: {e}")
        
        # Findings statistics
        findings = {"total": 0, "avg_risk_score": 0, "critical": 0, "high": 0}
        try:
            result = await db.execute(text("""
                SELECT COUNT(*) as total,
                       AVG(risk_score) as avg_risk,
                       COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical,
                       COUNT(CASE WHEN severity = 'high' THEN 1 END) as high
                FROM findings
            """))
            row = result.fetchone()
            if row:
                findings = {
                    "total": row[0] or 0,
                    "avg_risk_score": round(row[1] or 0, 1),
                    "critical": row[2] or 0,
                    "high": row[3] or 0
                }
        except Exception as e:
            print(f"Findings stats error: {e}")
        
        # Graph statistics
        graph_stats = {"total_entities": 0, "cases_with_graph": 0, "collusion_patterns": 0}
        try:
            result = await db.execute(text("SELECT COUNT(*) FROM graph_entities"))
            graph_stats["total_entities"] = result.scalar() or 0
            
            result = await db.execute(text("SELECT COUNT(*) FROM collusion_detections"))
            graph_stats["collusion_patterns"] = result.scalar() or 0
        except Exception as e:
            print(f"Graph stats error: {e}")
        
        # Recent activity
        recent_events = []
        try:
            result = await db.execute(text("""
                SELECT event_type, user_id, timestamp, data
                FROM events
                ORDER BY timestamp DESC
                LIMIT 10
            """))
            for row in result.fetchall():
                recent_events.append({
                    "event_type": row[0],
                    "user_id": row[1],
                    "timestamp": row[2].isoformat() if row[2] else None,
                    "data": row[3]
                })
        except Exception as e:
            print(f"Recent events error: {e}")
        
        # System health
        system_health = {
            "status": "healthy",
            "api_instances": 3,
            "database_connected": True,
            "websocket_active": True,
            "last_check": datetime.now().isoformat()
        }
        
        # Active cases
        active_cases = cases_by_status.get("OPEN", 0) + cases_by_status.get("INVESTIGATING", 0)
        critical_cases = cases_by_priority.get("CRITICAL", 0) + cases_by_priority.get("HIGH", 0)
        
        return {
            "success": True,
            "data": {
                "cases": {
                    "total": total_cases,
                    "active": active_cases,
                    "critical": critical_cases,
                    "by_status": cases_by_status,
                    "by_priority": cases_by_priority
                },
                "integrity": {
                    "score": integrity_score,
                    "total_events": total_events,
                    "hashed_events": hashed_events,
                    "status": "ok" if integrity_score >= 90 else "degraded"
                },
                "alerts": alerts,
                "findings": findings,
                "graph": graph_stats,
                "recent_activity": recent_events,
                "system_health": system_health
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/stats/overview")
async def get_stats_overview(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Quick overview statistics for dashboard cards"""
    institution_id, user_id, role = get_user_info(request)
    
    try:
        # Case stats
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status IN ('OPEN', 'INVESTIGATING') THEN 1 END) as active,
                COUNT(CASE WHEN priority IN ('CRITICAL', 'HIGH') THEN 1 END) as high_priority
            FROM cases
        """))
        row = result.fetchone()
        case_stats = {
            "total": row[0] or 0,
            "active": row[1] or 0,
            "high_priority": row[2] or 0
        }
        
        # Alert stats
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as active,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical
            FROM alerts WHERE resolved = false
        """))
        row = result.fetchone()
        alert_stats = {
            "active": row[0] or 0,
            "critical": row[1] or 0
        }
        
        # Integrity
        result = await db.execute(text("SELECT COUNT(*) as total, COUNT(event_hash) as hashed FROM events"))
        row = result.fetchone()
        total_events = row[0] or 1
        hashed_events = row[1] or 0
        integrity_score = round((hashed_events / total_events) * 100, 2) if total_events > 0 else 100
        
        return {
            "success": True,
            "data": {
                "cases": case_stats,
                "alerts": alert_stats,
                "integrity_score": integrity_score
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/timeline/recent")
async def get_recent_timeline(
    request: Request,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """Recent activity timeline for dashboard"""
    institution_id, user_id, role = get_user_info(request)
    
    try:
        result = await db.execute(text("""
            SELECT 
                e.event_id,
                e.event_type,
                e.case_id,
                c.title as case_title,
                e.user_id,
                e.timestamp,
                e.data
            FROM events e
            LEFT JOIN cases c ON e.case_id = c.id
            ORDER BY e.timestamp DESC
            LIMIT :limit
        """), {"limit": limit})
        
        timeline = []
        for row in result.fetchall():
            timeline.append({
                "id": row[0],
                "type": row[1],
                "case_id": row[2],
                "case_title": row[3],
                "user_id": row[4],
                "timestamp": row[5].isoformat() if row[5] else None,
                "details": row[6]
            })
        
        return {
            "success": True,
            "data": {
                "timeline": timeline,
                "total": len(timeline),
                "limit": limit
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
