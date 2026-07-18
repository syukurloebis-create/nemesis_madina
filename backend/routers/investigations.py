from fastapi import APIRouter, Query
from typing import Optional
import uuid
from datetime import datetime, timedelta

router = APIRouter()

# Mock investigations data
MOCK_INVESTIGATIONS = [
    {
        "id": "inv-001",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Vendor X - Kolusi",
        "description": "Deteksi pola kolusi antara Vendor X dengan pegawai internal",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "assigned_to": "Tim Investigasi Fraud",
        "progress": 65,
        "evidence_count": 12,
        "tags": ["Kolusi", "Vendor", "Internal"]
    },
    {
        "id": "inv-002",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Transaksi Mencurigakan",
        "description": "Pola transaksi tidak wajar pada pengadaan IT",
        "status": "REVIEW",
        "priority": "MEDIUM",
        "assigned_to": "Tim Analisis Keuangan",
        "progress": 85,
        "evidence_count": 8,
        "tags": ["Transaksi", "Keuangan", "IT"]
    },
    {
        "id": "inv-003",
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "title": "Investigasi Pengadaan Fiktif",
        "description": "Indikasi pengadaan fiktif pada proyek infrastruktur",
        "status": "PENDING",
        "priority": "CRITICAL",
        "assigned_to": "Tim Khusus Anti-Korupsi",
        "progress": 20,
        "evidence_count": 5,
        "tags": ["Fiktif", "Infrastruktur", "Korupsi"]
    }
]

@router.get("/case/{case_id}")
async def get_investigations_by_case(case_id: str):
    """Get all investigations for a case"""
    result = [inv for inv in MOCK_INVESTIGATIONS if inv["case_id"] == case_id]
    return result

@router.get("/stats")
async def get_investigations_stats(case_id: str = Query(...)):
    """Get investigation statistics"""
    investigations = [inv for inv in MOCK_INVESTIGATIONS if inv["case_id"] == case_id]
    
    return {
        "total": len(investigations),
        "in_progress": len([i for i in investigations if i["status"] == "IN_PROGRESS"]),
        "pending": len([i for i in investigations if i["status"] == "PENDING"]),
        "review": len([i for i in investigations if i["status"] == "REVIEW"]),
        "completed": len([i for i in investigations if i["status"] == "COMPLETED"])
    }

@router.get("/{investigation_id}")
async def get_investigation(investigation_id: str):
    """Get investigation by ID"""
    for inv in MOCK_INVESTIGATIONS:
        if inv["id"] == investigation_id:
            return inv
    return {"error": "Investigation not found"}

@router.patch("/{investigation_id}/status")
async def update_investigation_status(investigation_id: str, status: str = Query(...)):
    """Update investigation status"""
    for inv in MOCK_INVESTIGATIONS:
        if inv["id"] == investigation_id:
            inv["status"] = status
            return {"message": f"Status updated to {status}", "investigation": inv}
    return {"error": "Investigation not found"}

@router.post("/{investigation_id}/notes")
async def add_investigation_note(investigation_id: str, note: str = Query(...)):
    """Add note to investigation"""
    return {
        "message": "Note added successfully",
        "investigation_id": investigation_id,
        "note": note,
        "timestamp": datetime.now().isoformat()
    }
