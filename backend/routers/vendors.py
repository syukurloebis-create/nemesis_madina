from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.security.dependencies import get_current_active_user
from backend.security.models import User

router = APIRouter(prefix="/vendors", tags=["vendors"])

# Mock data
MOCK_VENDORS = [
    {"id": "1", "name": "PT. Maju Jaya", "risk_score": 92, "status": "active"},
    {"id": "2", "name": "CV. Karya Mandiri", "risk_score": 88, "status": "active"},
    {"id": "3", "name": "PT. Bangun Nusantara", "risk_score": 78, "status": "active"},
]

MOCK_COLLUSIONS = [
    {"id": "1", "vendor_ids": ["1", "2"], "pattern_type": "address", "confidence": 92, "severity": "high"},
    {"id": "2", "vendor_ids": ["1", "3"], "pattern_type": "bid_rigging", "confidence": 88, "severity": "critical"},
]


@router.get("/")
async def get_vendors(
    current_user: User = Depends(get_current_active_user)
):
    """Get all vendors"""
    return {"data": MOCK_VENDORS, "total": len(MOCK_VENDORS)}


@router.get("/collusions")
async def get_collusions(
    vendor_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get collusion patterns"""
    result = MOCK_COLLUSIONS
    if vendor_id:
        result = [c for c in result if vendor_id in c["vendor_ids"]]
    return {"data": result, "total": len(result)}


@router.get("/{vendor_id}")
async def get_vendor(
    vendor_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get vendor by ID"""
    vendor = next((v for v in MOCK_VENDORS if v["id"] == vendor_id), None)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.get("/{vendor_id}/contracts")
async def get_vendor_contracts(
    vendor_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get vendor contracts"""
    mock_contracts = [
        {"id": "c1", "contract_number": "CON-001", "title": "Project Alpha", "value": 150, "status": "active"},
        {"id": "c2", "contract_number": "CON-002", "title": "Project Beta", "value": 200, "status": "completed"},
    ]
    return {"data": mock_contracts}


@router.get("/{vendor_id}/risk-factors")
async def get_vendor_risk_factors(
    vendor_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get vendor risk factors"""
    mock_factors = [
        {"factor": "Transaction Pattern", "weight": 35, "severity": "high"},
        {"factor": "Vendor Concentration", "weight": 25, "severity": "medium"},
    ]
    return {"data": mock_factors}
