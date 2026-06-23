from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Dict, Any
import pandas as pd
import json
import io
import uuid
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from infrastructure.database import get_db
from security.dependencies import get_current_user

router = APIRouter(prefix="/upload/procurement", tags=["procurement"])

async def process_excel(content: bytes) -> List[Dict]:
    """Process Excel file"""
    df = pd.read_excel(io.BytesIO(content))
    return df.to_dict(orient='records')

async def process_csv(content: bytes) -> List[Dict]:
    """Process CSV file"""
    df = pd.read_csv(io.BytesIO(content))
    return df.to_dict(orient='records')

async def process_json(content: bytes) -> List[Dict]:
    """Process JSON file"""
    return json.loads(content.decode('utf-8'))

def normalize_record(record: Dict) -> Dict:
    """Normalize record fields"""
    return {
        "procurement_id": str(record.get('procurement_id') or record.get('id') or record.get('kode_paket') or uuid.uuid4()),
        "title": str(record.get('title') or record.get('nama_paket') or record.get('name') or 'Unknown'),
        "vendor": str(record.get('vendor') or record.get('penyedia') or record.get('supplier') or 'Unknown'),
        "amount": float(record.get('amount') or record.get('nilai_kontrak') or record.get('value') or 0),
        "date": record.get('date') or record.get('tanggal') or datetime.now().strftime('%Y-%m-%d')
    }

@router.post("/")
async def upload_procurement(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload procurement data from Excel, CSV, or JSON"""
    content = await file.read()
    filename = file.filename.lower()
    
    # Process based on file type
    if filename.endswith(('.xlsx', '.xls')):
        records = await process_excel(content)
    elif filename.endswith('.csv'):
        records = await process_csv(content)
    elif filename.endswith('.json'):
        records = await process_json(content)
    else:
        raise HTTPException(400, "Format tidak didukung. Gunakan .xlsx, .csv, atau .json")
    
    inserted = 0
    duplicates = 0
    errors = 0
    
    for record in records[:5000]:  # Limit 5000 records
        try:
            normalized = normalize_record(record)
            
            # Check for duplicate
            check_query = text("SELECT id FROM procurement_records WHERE procurement_id = :proc_id")
            result = await db.execute(check_query, {"proc_id": normalized["procurement_id"]})
            if result.fetchone():
                duplicates += 1
                continue
            
            # Insert record
            insert_query = text("""
                INSERT INTO procurement_records (id, procurement_id, title, vendor, amount, date, source_file, created_at)
                VALUES (:id, :proc_id, :title, :vendor, :amount, :date, :source_file, NOW())
            """)
            
            await db.execute(insert_query, {
                "id": str(uuid.uuid4()),
                "proc_id": normalized["procurement_id"],
                "title": normalized["title"][:500],
                "vendor": normalized["vendor"][:255],
                "amount": normalized["amount"],
                "date": normalized["date"],
                "source_file": file.filename
            })
            inserted += 1
            
        except Exception as e:
            errors += 1
            print(f"Error processing record: {e}")
    
    await db.commit()
    
    return {
        "success": True,
        "total_records": len(records),
        "inserted": inserted,
        "duplicates": duplicates,
        "errors": errors,
        "message": f"Berhasil upload {inserted} data procurement dari {file.filename}"
    }

@router.get("/list")
async def list_procurement(
    skip: int = 0, 
    limit: int = 100,
    vendor: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all procurement records with optional vendor filter"""
    query = "SELECT id, procurement_id, title, vendor, amount, date, created_at FROM procurement_records"
    params = {}
    
    if vendor:
        query += " WHERE vendor ILIKE :vendor"
        params["vendor"] = f"%{vendor}%"
    
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
    params["limit"] = limit
    params["skip"] = skip
    
    result = await db.execute(text(query), params)
    records = [dict(r._mapping) for r in result.fetchall()]
    
    # Get total count
    count_query = "SELECT COUNT(*) as total FROM procurement_records"
    if vendor:
        count_query += " WHERE vendor ILIKE :vendor"
    count_result = await db.execute(text(count_query), {"vendor": f"%{vendor}%"})
    total = count_result.scalar()
    
    # Get statistics
    stats_query = """
        SELECT 
            COUNT(*) as total_records,
            COALESCE(SUM(amount), 0) as total_amount,
            COUNT(DISTINCT vendor) as unique_vendors
        FROM procurement_records
    """
    if vendor:
        stats_query += " WHERE vendor ILIKE :vendor"
    stats_result = await db.execute(text(stats_query), {"vendor": f"%{vendor}%"})
    stats = dict(stats_result.fetchone()._mapping)
    
    return {
        "records": records,
        "total": total,
        "skip": skip,
        "limit": limit,
        "statistics": stats
    }

@router.get("/vendors")
async def list_vendors(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all unique vendors with statistics"""
    query = """
        SELECT 
            vendor,
            COUNT(*) as contract_count,
            COALESCE(SUM(amount), 0) as total_amount,
            AVG(amount) as avg_amount
        FROM procurement_records
        GROUP BY vendor
        ORDER BY total_amount DESC
    """
    result = await db.execute(text(query))
    vendors = [dict(r._mapping) for r in result.fetchall()]
    return {"vendors": vendors, "total": len(vendors)}

@router.post("/deduplicate")
async def deduplicate_procurement(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Remove duplicate procurement records based on procurement_id"""
    # Delete duplicates keeping the oldest
    delete_query = text("""
        DELETE FROM procurement_records
        WHERE id NOT IN (
            SELECT MIN(id) FROM procurement_records
            GROUP BY procurement_id
        )
    """)
    result = await db.execute(delete_query)
    await db.commit()
    
    # Get remaining count
    count_result = await db.execute(text("SELECT COUNT(*) as total FROM procurement_records"))
    count = count_result.scalar()
    
    return {
        "success": True, 
        "remaining_records": count,
        "deleted_records": result.rowcount,
        "message": f"Bersihkan duplikasi selesai. Tersisa {count} records"
    }

@router.delete("/{record_id}")
async def delete_procurement(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a specific procurement record"""
    result = await db.execute(text("DELETE FROM procurement_records WHERE id = :id"), {"id": record_id})
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(404, "Record not found")
    
    return {"success": True, "message": "Record deleted"}
