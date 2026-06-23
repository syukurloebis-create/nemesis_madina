"""
Advanced Features API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime

from infrastructure.database import get_db
from cases.service import CaseService
from intelligence.graph.service import GraphIntelligenceService
from ml.anomaly_detection import anomaly_service
from websocket.alerts import alert_engine, manager
from legal.court_report import report_generator
from graph.visualization import visualizer
from security.dependencies import get_current_user
from security.models import User

router = APIRouter(prefix="/advanced", tags=["Advanced Features"])


@router.post("/cases/{case_id}/anomaly-detect")
async def detect_anomalies(
    case_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Run ML-based anomaly detection on case transactions"""
    case_service = CaseService(session)
    case = await case_service.get_case(case_id)
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Extract transactions from case metadata
    transactions = case.case_metadata.get("transactions", [])
    
    if not transactions:
        return {"case_id": case_id, "message": "No transactions found", "anomalies": []}
    
    # Run anomaly detection
    result = await anomaly_service.analyze_case(case_id, transactions)
    
    # Send alerts for high anomaly scores
    if result["anomaly_score"] >= 70:
        alerts = await alert_engine.check_anomaly(case_id, result["anomaly_score"])
        await alert_engine.process_and_send(case_id, alerts, current_user.id)
    
    return result


@router.post("/cases/{case_id}/train-anomaly")
async def train_anomaly_detector(
    case_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Train ML model on case transactions"""
    case_service = CaseService(session)
    case = await case_service.get_case(case_id)
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    transactions = case.case_metadata.get("transactions", [])
    
    if len(transactions) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 10 transactions for training (found {len(transactions)})"
        )
    
    result = await anomaly_service.train_for_case(case_id, transactions)
    
    return result


@router.post("/cases/{case_id}/generate-court-report")
async def generate_court_report(
    case_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Generate court-ready PDF report"""
    case_service = CaseService(session)
    graph_service = GraphIntelligenceService(session)
    
    # Get case data
    case = await case_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get events
    events = await case_service.get_case_events(case_id)
    
    # Get collusion analysis
    collusion_result = await graph_service.analyze_collusion(case_id)
    
    # Generate report
    case_data = {
        "id": case.id,
        "title": case.title,
        "description": case.description,
        "status": case.status.value,
        "priority": case.priority.value