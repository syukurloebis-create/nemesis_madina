from fastapi import APIRouter, Query, Response
import sqlite3
from pathlib import Path
import csv
import io
from datetime import datetime

router = APIRouter(prefix="/rup", tags=["RUP"])

RUP_DB_PATH = Path("/app/rup_database.db")

def get_db():
    if not RUP_DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(RUP_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/stats")
async def get_rup_stats():
    """Statistik RUP lengkap dalam Bahasa Indonesia"""
    conn = get_db()
    if not conn:
        return {
            "total_paket": 0,
            "total_pagu": 0,
            "total_pagu_formatted": "Rp0",
            "tahun_2025": 0,
            "tahun_2026": 0,
            "selesai": 0,
            "berjalan": 0,
            "dalam_proses": 0
        }
    
    cursor = conn.cursor()
    
    # Total paket dan pagu
    cursor.execute("SELECT COUNT(*) as total, COALESCE(SUM(pagu), 0) as total_pagu FROM rup_paket")
    row = cursor.fetchone()
    total_paket = row["total"]
    total_pagu = float(row["total_pagu"])
    
    # Per tahun
    cursor.execute("SELECT tahun, COUNT(*) FROM rup_paket WHERE tahun IN (2025, 2026) GROUP BY tahun")
    tahun_data = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Per status
    cursor.execute("SELECT status, COUNT(*) FROM rup_paket GROUP BY status")
    status_data = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    # Format Rupiah
    def format_rupiah(value):
        return f"Rp{value:,.0f}".replace(",", ".")
    
    return {
        "total_paket": total_paket,
        "total_pagu": total_pagu,
        "total_pagu_formatted": format_rupiah(total_pagu),
        "tahun_2025": tahun_data.get(2025, 0),
        "tahun_2026": tahun_data.get(2026, 0),
        "selesai": status_data.get("Selesai", 0),
        "berjalan": status_data.get("Berjalan", 0),
        "dalam_proses": status_data.get("Dalam Proses", 0)
    }

@router.get("/data")
async def get_rup_data(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    tahun: int = Query(None),
    metode: str = Query(None),
    status: str = Query(None),
    search: str = Query(None)
):
    """Data RUP dengan filter"""
    conn = get_db()
    if not conn:
        return {"data": [], "total": 0}
    
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    
    if tahun:
        where_clauses.append("tahun = ?")
        params.append(tahun)
    
    if metode:
        where_clauses.append("metode = ?")
        params.append(metode)
    
    if status:
        where_clauses.append("status = ?")
        params.append(status)
    
    if search:
        where_clauses.append("(nama_paket LIKE ? OR instansi LIKE ? OR nomor_id LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    cursor.execute(f"SELECT COUNT(*) as total FROM rup_paket WHERE {where_sql}", params)
    total = cursor.fetchone()["total"]
    
    query = f"""
        SELECT id, nomor_id, nama_paket, pagu, jenis, tahun, metode, instansi, 
               COALESCE(status, 'Dalam Proses') as status
        FROM rup_paket
        WHERE {where_sql}
        ORDER BY tahun DESC, id
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, params + [limit, offset])
    rows = cursor.fetchall()
    
    def format_rupiah(value):
        if not value:
            return "Rp0"
        return f"Rp{value:,.0f}".replace(",", ".")
    
    data = []
    for row in rows:
        data.append({
            "id": row["id"],
            "nomor_id": row["nomor_id"],
            "nama_paket": row["nama_paket"],
            "pagu": float(row["pagu"]) if row["pagu"] else 0,
            "pagu_formatted": format_rupiah(row["pagu"]),
            "jenis": row["jenis"],
            "tahun": row["tahun"],
            "metode": row["metode"],
            "instansi": row["instansi"],
            "status": row["status"]
        })
    
    conn.close()
    
    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/export")
async def export_rup_data(
    tahun: int = Query(None),
    metode: str = Query(None),
    status: str = Query(None),
    search: str = Query(None)
):
    """Export data RUP ke CSV"""
    conn = get_db()
    if not conn:
        return Response(content="Database tidak ditemukan", status_code=404)
    
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    
    if tahun:
        where_clauses.append("tahun = ?")
        params.append(tahun)
    
    if metode:
        where_clauses.append("metode = ?")
        params.append(metode)
    
    if status:
        where_clauses.append("status = ?")
        params.append(status)
    
    if search:
        where_clauses.append("(nama_paket LIKE ? OR instansi LIKE ? OR nomor_id LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    query = f"""
        SELECT id, nomor_id, nama_paket, pagu, jenis, tahun, metode, instansi, 
               COALESCE(status, 'Dalam Proses') as status
        FROM rup_paket
        WHERE {where_sql}
        ORDER BY tahun DESC, id
    """
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["ID", "Nomor ID", "Nama Paket", "Pagu (Rp)", "Jenis", "Tahun", "Metode", "Instansi", "Status"])
    
    for row in rows:
        pagu_str = f"{float(row['pagu']):,.0f}".replace(",", ".") if row["pagu"] else "0"
        writer.writerow([
            row["id"],
            row["nomor_id"],
            row["nama_paket"],
            pagu_str,
            row["jenis"],
            row["tahun"],
            row["metode"],
            row["instansi"],
            row["status"]
        ])
    
    filename = f"rup_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=output.getvalue().encode('utf-8-sig'),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/methods")
async def get_rup_methods():
    """Daftar metode pengadaan"""
    conn = get_db()
    if not conn:
        return {"metode": []}
    
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT metode FROM rup_paket WHERE metode IS NOT NULL AND metode != '' ORDER BY metode")
    metode = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return {"metode": metode}

@router.get("/statuses")
async def get_rup_statuses():
    """Daftar status paket"""
    conn = get_db()
    if not conn:
        return {"status": []}
    
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT COALESCE(status, 'Dalam Proses') as status FROM rup_paket ORDER BY status")
    statuses = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return {"status": statuses}

@router.get("/years")
async def get_rup_years():
    """Daftar tahun anggaran"""
    conn = get_db()
    if not conn:
        return {"tahun": []}
    
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tahun FROM rup_paket ORDER BY tahun DESC")
    years = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    
    return {"tahun": years}
