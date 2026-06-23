from fastapi import APIRouter, Query
from typing import Optional
import uuid
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/")
async def get_cases(
    status: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """Get cases - simple implementation"""
    now = datetime.now()
    cases = []
    
    titles = [
        "Investigasi Vendor X - Kolusi",
        "Investigasi Transaksi Mencurigakan",
        "Investigasi Pengadaan Fiktif",
        "Investigasi Vendor Y - Konflik Kepentingan",
        "Investigasi Mark-up Harga"
    ]
    
    for i in range(min(limit, len(titles))):
        cases.append({
            "id": f"case-{uuid.uuid4().hex[:8]}",
            "title": titles[i],
            "description": f"Deskripsi kasus {titles[i]}",
            "status": ["OPEN", "INVESTIGATING", "REVIEW", "CLOSED"][i % 4],
            "priority": ["LOW", "MEDIUM", "HIGH", "CRITICAL"][i % 4],
            "risk_score": round(random.uniform(20, 95), 1),
            "created_at": (now - timedelta(days=i * 3 + 1)).isoformat(),
            "updated_at": (now - timedelta(hours=i * 2 + 1)).isoformat(),
            "assigned_to": "Tim Investigasi Fraud",
            "evidence_count": random.randint(3, 20),
            "tags": ["Vendor", "Internal", "Keuangan"]
        })
    
    if status:
        cases = [c for c in cases if c["status"] == status]
    
    total = len(cases)
    cases = cases[offset:offset + limit]
    
    return {
        "items": cases,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }

@router.get("/stats")
async def get_cases_stats():
    """Get cases statistics - simple implementation"""
    return {
        "total": 5,
        "open": 2,
        "investigating": 1,
        "review": 1,
        "closed": 1,
        "critical": 1,
        "high": 2,
        "medium": 1,
        "low": 1,
        "avg_risk_score": 65.5
    }

@router.get("/{case_id}")
async def get_case(case_id: str):
    """Get case by ID - simple implementation"""
    return {
        "id": case_id,
        "title": "Investigasi Vendor X - Kolusi",
        "description": "Deteksi pola kolusi antara Vendor X dengan pegawai internal",
        "status": "INVESTIGATING",
        "priority": "HIGH",
        "risk_score": 85.5,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "assigned_to": "Tim Investigasi Fraud",
        "evidence_count": 12,
        "tags": ["Vendor", "Internal", "Kolusi"]
    }
