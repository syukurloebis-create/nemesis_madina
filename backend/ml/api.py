"""ML Detection API Endpoints - Simple Version"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

# Create router
router = APIRouter(prefix="/ml", tags=["ml"])


class DetectionRequest(BaseModel):
    procurement_data: Dict[str, Any]


@router.get("/")
async def ml_root():
    """ML API root endpoint"""
    return {
        "message": "ML API is active",
        "endpoints": {
            "detect": "POST /ml/detect",
            "confidence": "GET /ml/confidence/{id}",
            "model_info": "GET /ml/model/info"
        }
    }


@router.post("/detect")
async def detect_anomaly(request: DetectionRequest):
    """Detect anomalies in procurement data"""
    data = request.procurement_data
    
    contract_value = data.get("contract_value", 0)
    market_average = data.get("market_average", contract_value)
    vendor_history = data.get("vendor_history", "unknown")
    procurement_method = data.get("procurement_method", "unknown")
    
    # Simple calculation
    if market_average > 0:
        price_markup = (contract_value - market_average) / market_average
    else:
        price_markup = 0
    
    # Risk scoring
    vendor_risk = {"low": 0.1, "medium": 0.4, "high": 0.7, "critical": 0.9}.get(vendor_history, 0.3)
    method_risk = {"tender": 0.1, "direct": 0.7, "emergency": 0.5}.get(procurement_method, 0.4)
    
    score = (min(max(price_markup, 0), 1) * 0.5) + (vendor_risk * 0.3) + (method_risk * 0.2)
    
    # Calibrated risk level
    if score >= 0.75:
        risk_level = "critical"
    elif score >= 0.60:
        risk_level = "high"
    elif score >= 0.40:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    findings = []
    if price_markup > 0.3:
        findings.append(f"Harga {price_markup*100:.0f}% di atas pasar")
    if vendor_history in ["high", "critical"]:
        findings.append(f"Vendor berisiko {vendor_history}")
    if procurement_method == "direct":
        findings.append("Penunjukan langsung tanpa tender")
    
    confidence = 0.5 + (abs(score - 0.5) * 0.8)
    
    return {
        "anomaly_id": str(uuid.uuid4()),
        "score": round(score, 3),
        "risk_level": risk_level,
        "findings": findings,
        "confidence": round(confidence, 3),
        "details": {
            "price_markup": round(price_markup, 3),
            "vendor_risk_score": vendor_risk,
            "method_risk_score": method_risk,
            "contract_value": contract_value,
            "market_average": market_average
        },
        "recommendation": "Perlu verifikasi lebih lanjut" if risk_level in ["high", "critical"] else "Monitoring rutin",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/model/info")
async def get_model_info():
    return {
        "model_name": "procurement_anomaly_detector",
        "version": "2.1.0",
        "features": ["price_markup", "vendor_risk", "procurement_method"]
    }
