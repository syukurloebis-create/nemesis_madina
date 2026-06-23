"""
Investigasi Router - NEMESIS V8+
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid

# ============================================
# ROUTER - TANPA PREFIX (sudah di main.py)
# ============================================
router = APIRouter(prefix="/api/v1/investigation", tags=["Investigation"])

print("[Router] Investigation router initialized with prefix: /api/v1/investigation")

# ============================================
# MODELS
# ============================================

class InvestigationBase(BaseModel):
    case_id: str
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    assigned_to: Optional[str] = None
    department: Optional[str] = None
    estimated_value: Optional[str] = None
    tags: Optional[List[str]] = []

class InvestigationCreate(InvestigationBase):
    pass

class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    progress: Optional[int] = None
    assigned_to: Optional[str] = None
    department: Optional[str] = None
    estimated_value: Optional[str] = None
    tags: Optional[List[str]] = None

class StatusUpdate(BaseModel):
    status: str
    progress: int

class EscalateRequest(BaseModel):
    reason: str
    target_level: str

# ============================================
# MOCK DATA
# ============================================

mock_investigations = {
    "446e216d-eb0e-487e-8e6b-ec943468ea20": [
        {
            "id": "inv-001",
            "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
            "title": "Investigasi Vendor X - Kolusi",
            "description": "Deteksi pola kolusi antara Vendor X dengan pegawai internal",
            "status": "IN_PROGRESS",
            "priority": "HIGH",
            "assigned_to": "Tim Investigasi Fraud",
            "department": "Pengadaan",
            "estimated_value": "Rp 3.2M",
            "tags": ["Kolusi", "Vendor", "Internal"],
            "progress": 65,
            "evidence_count": 12,
            "witnesses_count": 3,
            "risk_score": 85,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": "system"
        },
        {
            "id": "inv-002",
            "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
            "title": "Investigasi Transaksi Mencurigakan",
            "description": "Pola transaksi tidak wajar pada pengadaan IT",
            "status": "REVIEW",
            "priority": "MEDIUM",
            "assigned_to": "Tim Analisis Keuangan",
            "department": "IT",
            "estimated_value": "Rp 2.5M",
            "tags": ["Transaksi", "Keuangan", "IT"],
            "progress": 85,
            "evidence_count": 8,
            "witnesses_count": 2,
            "risk_score": 65,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": "system"
        },
        {
            "id": "inv-003",
            "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
            "title": "Investigasi Pengadaan Fiktif",
            "description": "Indikasi pengadaan fiktif pada proyek infrastruktur",
            "status": "PENDING",
            "priority": "CRITICAL",
            "assigned_to": "Tim Khusus Anti-Korupsi",
            "department": "Infrastruktur",
            "estimated_value": "Rp 5M",
            "tags": ["Fiktif", "Infrastruktur", "Korupsi"],
            "progress": 20,
            "evidence_count": 5,
            "witnesses_count": 1,
            "risk_score": 92,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": "system"
        },
        {
            "id": "inv-004",
            "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
            "title": "Investigasi Vendor Y - Konflik Kepentingan",
            "description": "Deteksi konflik kepentingan antara Vendor Y dengan pejabat pengadaan",
            "status": "PENDING",
            "priority": "HIGH",
            "assigned_to": "Tim Investigasi Fraud",
            "department": "Pengadaan",
            "estimated_value": "Rp 1.8M",
            "tags": ["Konflik", "Vendor", "Pejabat"],
            "progress": 10,
            "evidence_count": 3,
            "witnesses_count": 0,
            "risk_score": 78,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": "system"
        },
        {
            "id": "inv-005",
            "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
            "title": "Investigasi Mark-up Harga",
            "description": "Indikasi mark-up harga pada paket pengadaan jasa konsultan",
            "status": "COMPLETED",
            "priority": "MEDIUM",
            "assigned_to": "Tim Analisis Keuangan",
            "department": "Konsultan",
            "estimated_value": "Rp 800Jt",
            "tags": ["Mark-up", "Konsultan", "Selesai"],
            "progress": 100,
            "evidence_count": 15,
            "witnesses_count": 4,
            "risk_score": 55,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": "system"
        }
    ]
}

# ============================================
# ENDPOINTS
# ============================================

@router.get("/stats")
async def get_stats(case_id: str = Query(...)):
    """Get investigation statistics"""
    print(f"[Router] GET /stats for case: {case_id}")
    
    if case_id not in mock_investigations:
        return {
            "total": 0,
            "in_progress": 0,
            "review": 0,
            "completed": 0,
            "pending": 0,
            "escalated": 0
        }
    
    invs = mock_investigations[case_id]
    return {
        "total": len(invs),
        "in_progress": len([i for i in invs if i["status"] == "IN_PROGRESS"]),
        "review": len([i for i in invs if i["status"] == "REVIEW"]),
        "completed": len([i for i in invs if i["status"] == "COMPLETED"]),
        "pending": len([i for i in invs if i["status"] == "PENDING"]),
        "escalated": len([i for i in invs if i["status"] == "ESCALATED"])
    }

@router.get("/case/{case_id}")
async def get_investigations(case_id: str):
    """Get all investigations for a case"""
    print(f"[Router] GET /case/{case_id}")
    
    if case_id not in mock_investigations:
        return []
    return mock_investigations[case_id]

@router.get("/{investigation_id}")
async def get_investigation(investigation_id: str):
    """Get investigation by ID"""
    print(f"[Router] GET /{investigation_id}")
    
    for case_id, invs in mock_investigations.items():
        for inv in invs:
            if inv["id"] == investigation_id:
                return inv
    raise HTTPException(status_code=404, detail="Investigation not found")

@router.post("/")
async def create_investigation(data: InvestigationCreate):
    """Create new investigation"""
    print(f"[Router] POST / with data: {data}")
    
    inv_id = f"inv-{uuid.uuid4().hex[:8]}"
    
    new_inv = {
        "id": inv_id,
        "case_id": data.case_id,
        "title": data.title,
        "description": data.description,
        "status": "PENDING",
        "priority": data.priority,
        "assigned_to": data.assigned_to,
        "department": data.department or "Umum",
        "estimated_value": data.estimated_value or "Rp 0",
        "tags": data.tags or [],
        "progress": 0,
        "evidence_count": 0,
        "witnesses_count": 0,
        "risk_score": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "created_by": "system"
    }
    
    if data.case_id not in mock_investigations:
        mock_investigations[data.case_id] = []
    mock_investigations[data.case_id].append(new_inv)
    
    return new_inv

@router.patch("/{investigation_id}/status")
async def update_status(investigation_id: str, data: StatusUpdate):
    """Update investigation status"""
    print(f"[Router] PATCH /{investigation_id}/status with data: {data}")
    
    for case_id, invs in mock_investigations.items():
        for idx, inv in enumerate(invs):
            if inv["id"] == investigation_id:
                inv["status"] = data.status
                inv["progress"] = data.progress
                inv["updated_at"] = datetime.now().isoformat()
                mock_investigations[case_id][idx] = inv
                return {"message": "Status updated", "status": data.status, "progress": data.progress}
    raise HTTPException(status_code=404, detail="Investigation not found")

@router.post("/{investigation_id}/escalate")
async def escalate_investigation(investigation_id: str, data: EscalateRequest):
    """Escalate investigation"""
    print(f"[Router] POST /{investigation_id}/escalate with data: {data}")
    
    for case_id, invs in mock_investigations.items():
        for idx, inv in enumerate(invs):
            if inv["id"] == investigation_id:
                inv["status"] = "ESCALATED"
                inv["priority"] = "CRITICAL"
                inv["updated_at"] = datetime.now().isoformat()
                mock_investigations[case_id][idx] = inv
                return {"message": "Escalated", "reason": data.reason, "target_level": data.target_level}
    raise HTTPException(status_code=404, detail="Investigation not found")

@router.get("/{investigation_id}/evidence")
async def get_evidence(investigation_id: str):
    """Get evidence"""
    return [
        {"id": f"ev-{i}", "title": f"Evidence {i}", "type": "DOCUMENT"}
        for i in range(1, 6)
    ]

@router.get("/{investigation_id}/team")
async def get_team(investigation_id: str):
    """Get team members"""
    return [
        {"id": f"member-{i}", "name": f"Member {i}", "role": ["LEAD", "ANALYST", "INVESTIGATOR"][i % 3]}
        for i in range(1, 4)
    ]

@router.post("/{investigation_id}/notes")
async def add_note(investigation_id: str, data: dict):
    """Add note"""
    return {
        "id": f"note-{uuid.uuid4().hex[:8]}",
        "content": data.get("content", ""),
        "created_at": datetime.now().isoformat(),
        "created_by_name": "System"
    }

@router.get("/{investigation_id}/notes")
async def get_notes(investigation_id: str):
    """Get notes"""
    return [
        {"id": f"note-{i}", "content": f"Note {i}", "created_at": datetime.now().isoformat()}
        for i in range(1, 3)
    ]

print("[OK] Investigation endpoints registered:")
print("  GET    /api/v1/investigation/stats")
print("  GET    /api/v1/investigation/case/{case_id}")
print("  GET    /api/v1/investigation/{id}")
print("  POST   /api/v1/investigation/")
print("  PATCH  /api/v1/investigation/{id}/status")
print("  POST   /api/v1/investigation/{id}/escalate")
print("  GET    /api/v1/investigation/{id}/evidence")
print("  GET    /api/v1/investigation/{id}/team")
print("  POST   /api/v1/investigation/{id}/notes")
