"""Decision Trace API Endpoints"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID

from backend.decision_trace.services.decision_trace_service import DecisionTraceService
from backend.decision_trace.repositories.decision_trace_repo import DecisionTraceRepository
from backend.decision_trace.models import DecisionTrace, DecisionTraceCreate, ExplainabilityResult

router = APIRouter(prefix="/decision-traces", tags=["decision-traces"])


async def get_decision_trace_service():
    from backend.infrastructure.database import get_pool
    pool = await get_pool()
    repo = DecisionTraceRepository(pool)
    return DecisionTraceService(repo)


@router.post("/", response_model=DecisionTrace)
async def create_decision_trace(
    trace_data: DecisionTraceCreate,
    service: DecisionTraceService = Depends(get_decision_trace_service)
):
    """Create a new decision trace"""
    return await service.create_trace(trace_data)


@router.get("/{trace_id}", response_model=DecisionTrace)
async def get_decision_trace(
    trace_id: UUID,
    service: DecisionTraceService = Depends(get_decision_trace_service)
):
    """Get decision trace by ID"""
    trace = await service.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Decision trace not found")
    return trace


@router.get("/{trace_id}/explain", response_model=ExplainabilityResult)
async def explain_decision(
    trace_id: UUID,
    top_k: int = Query(5, ge=1, le=10),
    service: DecisionTraceService = Depends(get_decision_trace_service)
):
    """Get explanation for a decision"""
    return await service.explain_decision(trace_id, top_k)


@router.get("/entity/{entity_id}", response_model=List[DecisionTrace])
async def get_entity_decisions(
    entity_id: str,
    limit: int = 50,
    service: DecisionTraceService = Depends(get_decision_trace_service)
):
    """Get all decisions for an entity"""
    return await service.get_entity_decisions(entity_id, limit)


@router.get("/statistics/summary")
async def get_decision_statistics(
    service: DecisionTraceService = Depends(get_decision_trace_service)
):
    """Get decision trace statistics"""
    return await service.get_statistics()
