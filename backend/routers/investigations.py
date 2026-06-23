from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter()

# Data investigasi (seeded)
INVESTIGATIONS_DATA = [
    {
        "id": "inv-001",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Vendor X - Kolusi",
        "description": "Deteksi pola kolusi antara Vendor X dengan pegawai internal dalam pengadaan barang",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "assigned_to": "team-fraud",
        "assigned_to_name": "Tim Investigasi Fraud",
        "created_at": "2026-06-20T00:00:00Z",
        "updated_at": "2026-06-23T00:00:00Z",
        "evidence_count": 12,
        "witness_count": 3,
        "progress": 65,
        "tags": ["Kolusi", "Vendor", "Internal"]
    },
    {
        "id": "inv-002",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Transaksi Mencurigakan",
        "description": "Pola transaksi tidak wajar pada pengadaan IT dengan nilai Rp 2.5M",
        "status": "REVIEW",
        "priority": "MEDIUM",
        "assigned_to": "team-finance",
        "assigned_to_name": "Tim Analisis Keuangan",
        "created_at": "2026-06-18T00:00:00Z",
        "updated_at": "2026-06-22T00:00:00Z",
        "evidence_count": 8,
        "witness_count": 2,
        "progress": 85,
        "tags": ["Transaksi", "Keuangan", "IT"]
    },
    {
        "id": "inv-003",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Pengadaan Fiktif",
        "description": "Indikasi pengadaan fiktif pada proyek infrastruktur dengan kerugian potensial Rp 5M",
        "status": "PENDING",
        "priority": "CRITICAL",
        "assigned_to": "team-anticorruption",
        "assigned_to_name": "Tim Khusus Anti-Korupsi",
        "created_at": "2026-06-22T00:00:00Z",
        "updated_at": "2026-06-22T00:00:00Z",
        "evidence_count": 5,
        "witness_count": 1,
        "progress": 20,
        "tags": ["Fiktif", "Infrastruktur", "Korupsi"]
    },
    {
        "id": "inv-004",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Vendor Y - Konflik Kepentingan",
        "description": "Deteksi konflik kepentingan antara Vendor Y dengan pejabat pengadaan",
        "status": "PENDING",
        "priority": "HIGH",
        "assigned_to": "team-fraud",
        "assigned_to_name": "Tim Investigasi Fraud",
        "created_at": "2026-06-21T00:00:00Z",
        "updated_at": "2026-06-21T00:00:00Z",
        "evidence_count": 3,
        "witness_count": 0,
        "progress": 10,
        "tags": ["Konflik", "Vendor", "Pejabat"]
    },
    {
        "id": "inv-005",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Mark-up Harga",
        "description": "Indikasi mark-up harga pada paket pengadaan jasa konsultan",
        "status": "COMPLETED",
        "priority": "MEDIUM",
        "assigned_to": "team-finance",
        "assigned_to_name": "Tim Analisis Keuangan",
        "created_at": "2026-06-10T00:00:00Z",
        "updated_at": "2026-06-19T00:00:00Z",
        "evidence_count": 15,
        "witness_count": 4,
        "progress": 100,
        "tags": ["Mark-up", "Konsultan", "Selesai"]
    }
]

@router.get("/case/{case_id}")
async def get_investigations_by_case(case_id: str):
    """Get all investigations for a case"""
    result = [inv for inv in INVESTIGATIONS_DATA if inv["case_id"] == case_id]
    return result

@router.get("/{investigation_id}")
async def get_investigation(investigation_id: str):
    """Get investigation by ID"""
    for inv in INVESTIGATIONS_DATA:
        if inv["id"] == investigation_id:
            return inv
    raise HTTPException(status_code=404, detail="Investigation not found")

@router.post("/")
async def create_investigation(data: dict):
    """Create new investigation"""
    new_inv = {
        "id": f"inv-{uuid.uuid4().hex[:8]}",
        "case_id": data.get("case_id"),
        "title": data.get("title"),
        "description": data.get("description", ""),
        "status": "PENDING",
        "priority": data.get("priority", "MEDIUM"),
        "assigned_to": data.get("assigned_to", ""),
        "assigned_to_name": data.get("assigned_to_name", ""),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "evidence_count": 0,
        "witness_count": 0,
        "progress": 0,
        "tags": data.get("tags", [])
    }
    INVESTIGATIONS_DATA.append(new_inv)
    return new_inv

@router.patch("/{investigation_id}/status")
async def update_status(investigation_id: str, data: dict):
    """Update investigation status"""
    for inv in INVESTIGATIONS_DATA:
        if inv["id"] == investigation_id:
            inv["status"] = data.get("status")
            if "progress" in data:
                inv["progress"] = data.get("progress")
            inv["updated_at"] = datetime.now().isoformat()
            return inv
    raise HTTPException(status_code=404, detail="Investigation not found")

@router.post("/{investigation_id}/escalate")
async def escalate_investigation(investigation_id: str, data: dict):
    """Escalate investigation"""
    for inv in INVESTIGATIONS_DATA:
        if inv["id"] == investigation_id:
            inv["status"] = "ESCALATED"
            inv["updated_at"] = datetime.now().isoformat()
            return {
                "message": f"Investigation {investigation_id} escalated", 
                "reason": data.get("reason"),
                "target_level": data.get("target_level", "HIGH")
            }
    raise HTTPException(status_code=404, detail="Investigation not found")

@router.post("/{investigation_id}/notes")
async def add_note(investigation_id: str, data: dict):
    """Add note to investigation"""
    # In production, save to database
    return {
        "message": f"Note added to {investigation_id}", 
        "note": data.get("note"),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/stats")
async def get_stats(case_id: str):
    """Get investigation stats for a case"""
    case_investigations = [inv for inv in INVESTIGATIONS_DATA if inv["case_id"] == case_id]
    return {
        "total": len(case_investigations),
        "in_progress": len([i for i in case_investigations if i["status"] == "IN_PROGRESS"]),
        "pending": len([i for i in case_investigations if i["status"] == "PENDING"]),
        "completed": len([i for i in case_investigations if i["status"] == "COMPLETED"]),
        "review": len([i for i in case_investigations if i["status"] == "REVIEW"]),
        "escalated": len([i for i in case_investigations if i["status"] == "ESCALATED"])
    }
