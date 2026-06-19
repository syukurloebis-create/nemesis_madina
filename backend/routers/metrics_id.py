from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

from backend.infrastructure.database import get_db

router = APIRouter(prefix="/metrics", tags=["Dashboard Metrics"])

def format_rupiah(value) -> str:
    """Format angka ke Rupiah"""
    if not value or value == 0:
        return "Rp0"
    return f"Rp{value:,.0f}".replace(",", ".")

@router.get("/dashboard")
async def get_dashboard_metrics(session: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Semua metrik dashboard dalam satu endpoint (Bahasa Indonesia)"""
    
    try:
        # 1. Statistik Procurement
        proc_result = await session.execute(
            text("""
                SELECT 
                    COUNT(DISTINCT nama_penyedia) as total_vendor,
                    COUNT(*) as total_paket,
                    COALESCE(SUM(total_nilai), 0) as total_nilai
                FROM rup_paket_detailed
            """)
        )
        proc = proc_result.fetchone()
        
        # 2. Statistik Cases
        case_result = await session.execute(
            text("""
                SELECT 
                    COUNT(*) as total_kasus,
                    COUNT(CASE WHEN status = 'OPEN' THEN 1 END) as kasus_aktif,
                    COUNT(CASE WHEN priority = 'HIGH' OR priority = 'CRITICAL' THEN 1 END) as risiko_tinggi
                FROM cases
                WHERE is_deleted = FALSE
            """)
        )
        cases = case_result.fetchone()
        
        # 3. Chain Integrity
        integrity_result = await session.execute(
            text("""
                SELECT 
                    COUNT(DISTINCT aggregate_id) as total_agregat,
                    COUNT(*) as total_event
                FROM events
            """)
        )
        integrity = integrity_result.fetchone()
        
        # 4. Evidence
        evidence_result = await session.execute(
            text("SELECT COUNT(*) as total FROM evidence_files WHERE is_deleted = FALSE")
        )
        evidence = evidence_result.fetchone()
        
        # 5. Collusion
        collusion_result = await session.execute(
            text("SELECT COUNT(*) as total FROM graph_relationships WHERE relationship_type = 'collusion'")
        )
        collusion = collusion_result.fetchone()
        
        # 6. Alert
        alert_result = await session.execute(
            text("SELECT COUNT(*) as total FROM alerts ")
        )
        alerts = alert_result.fetchone()
        
        total_nilai = float(proc[2]) if proc[2] else 0
        
        return {
            "procurement": {
                "total_vendor": int(proc[0]) if proc[0] else 0,
                "total_paket": int(proc[1]) if proc[1] else 0,
                "total_nilai": total_nilai,
                "total_nilai_formatted": format_rupiah(total_nilai)
            },
            "cases": {
                "total_kasus": int(cases[0]) if cases[0] else 0,
                "kasus_aktif": int(cases[1]) if cases[1] else 0,
                "risiko_tinggi": int(cases[2]) if cases[2] else 0
            },
            "integrity": {
                "total_agregat": int(integrity[0]) if integrity[0] else 0,
                "total_event": int(integrity[1]) if integrity[1] else 0,
                "status": "TERVERIFIKASI" if integrity[0] and integrity[0] > 0 else "BELUM ADA DATA"
            },
            "evidence": {
                "total_dokumen": int(evidence[0]) if evidence[0] else 0
            },
            "collusion": {
                "total_pola": int(collusion[0]) if collusion[0] else 0
            },
            "alerts": {
                "aktif": int(alerts[0]) if alerts[0] else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "procurement": {"total_vendor": 0, "total_paket": 0, "total_nilai": 0, "total_nilai_formatted": "Rp0"},
            "cases": {"total_kasus": 0, "kasus_aktif": 0, "risiko_tinggi": 0},
            "integrity": {"total_agregat": 0, "total_event": 0, "status": "ERROR"},
            "evidence": {"total_dokumen": 0},
            "collusion": {"total_pola": 0},
            "alerts": {"aktif": 0},
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/timeline/kasus")
async def get_cases_timeline(
    hari: int = 30,
    session: AsyncSession = Depends(get_db)
):
    """Grafik kasus per hari"""
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=hari)
    
    result = await session.execute(
        text("""
            SELECT 
                DATE(created_at) as tanggal,
                COUNT(*) as jumlah
            FROM cases
            WHERE created_at >= :start_date AND is_deleted = FALSE
            GROUP BY DATE(created_at)
            ORDER BY tanggal ASC
        """),
        {"start_date": start_date}
    )
    
    rows = result.fetchall()
    
    data = []
    for row in rows:
        tgl = row[0]
        jml = row[1]
        data.append({
            "tanggal": tgl.isoformat() if tgl else None,
            "jumlah": int(jml) if jml else 0
        })
    
    return {
        "data": data,
        "periode_hari": hari,
        "total_kasus": sum(d["jumlah"] for d in data)
    }

@router.get("/integrity/chain")
async def get_chain_integrity(session: AsyncSession = Depends(get_db)):
    """Status integritas hash chain (Bahasa Indonesia)"""
    
    result = await session.execute(
        text("""
            SELECT 
                aggregate_type as tipe,
                aggregate_id as id,
                COUNT(*) as jumlah_event
            FROM events
            GROUP BY aggregate_type, aggregate_id
            ORDER BY aggregate_type
        """)
    )
    aggregates = result.fetchall()
    
    total_agregat = len(aggregates)
    total_event = sum(agg[2] for agg in aggregates) if aggregates else 0
    
    detail = []
    for agg in aggregates:
        detail.append({
            "tipe": agg[0],
            "id": str(agg[1]),
            "jumlah_event": int(agg[2])
        })
    
    return {
        "total_agregat": total_agregat,
        "total_event": total_event,
        "status": "HEALTHY" if total_agregat > 0 else "NO_DATA",
        "status_text": "Integritas Hash Chain Terverifikasi" if total_agregat > 0 else "Belum Ada Data Event",
        "detail": detail[:20]
    }

@router.get("/alerts/terkini")
async def get_alerts_terkini(
    limit: int = 10,
    session: AsyncSession = Depends(get_db)
):
    """Alert terkini (Bahasa Indonesia)"""
    
    result = await session.execute(
        text("""
            SELECT 
                id, case_id, title, description, severity, status, created_at
            FROM alerts
            ORDER BY created_at DESC
            LIMIT :limit
        """),
        {"limit": limit}
    )
    alerts = result.fetchall()
    
    tingkat = {
        "CRITICAL": "KRITIS",
        "HIGH": "TINGGI",
        "MEDIUM": "SEDANG",
        "LOW": "RENDAH"
    }
    
    alert_list = []
    for a in alerts:
        alert_list.append({
            "id": str(a[0]),
            "kasus_id": str(a[1]) if a[1] else None,
            "judul": a[2],
            "deskripsi": a[3],
            "tingkat": tingkat.get(a[4], a[4] or "TIDAK DIKENAL"),
            "tingkat_asli": a[4],
            "status": a[5],
            "waktu": a[6].isoformat() if a[6] else None
        })
    
    return {
        "alert": alert_list,
        "total": len(alert_list),
        "last_update": datetime.utcnow().isoformat()
    }
