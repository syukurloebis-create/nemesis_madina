# backend/routers/graph.py
"""
Graph Intelligence API — F3.3 Contract v1 (LOCKED — HYBRID)

Canonical (case-scoped):
  GET /api/v1/graph/cases/{case_id}                 full graph
  GET /api/v1/graph/cases/{case_id}/summary         summary
  GET /api/v1/graph/cases/{case_id}/metrics         distribution
  GET /api/v1/graph/cases/{case_id}/entities        paginated
  GET /api/v1/graph/cases/{case_id}/relationships   paginated
  GET /api/v1/graph/cases/{case_id}/key-actors      structural
  GET /api/v1/graph/cases/{case_id}/collusion       edges only
  GET /api/v1/graph/collusion/{case_id}             legacy → 410

Legacy (flat, DEPRECATED):
  GET /api/v1/graph?case_id=...                     → 410 Gone
  GET /api/v1/graph/stats?case_id=...               → 301 canonical /summary
  GET /api/v1/graph/metrics?case_id=...             → 301 canonical /metrics
  GET /api/v1/graph/entities?case_id=...            → 301 canonical /entities
  GET /api/v1/graph/relationships?case_id=...       → 301 canonical /relationships
  GET /api/v1/graph/key-actors?case_id=...          → 301 canonical /key-actors
  GET /api/v1/graph/collusion/{case_id}             → 410 Gone

Boundary:
  - Read-only.
  - Does NOT touch risk_scores, dashboard_view, risk.py.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from backend.dependencies.auth import get_current_active_user
from backend.security.models import User
from backend.services.graph_read_service import GraphReadService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Graph"])


# =====================================================================
# Dependencies
# =====================================================================

def _get_graph_read_service(request: Request) -> GraphReadService:
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Container not initialized",
        )

    graph_repository = getattr(container.services, "graph_repository", None)
    if graph_repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Graph repository not available",
        )

    return GraphReadService(graph_repository=graph_repository)


def _get_uow_factory(request: Request):
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Container not initialized",
        )
    return container.infrastructure.uow_factory


def _gone(old: str, new: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail={
            "error": "endpoint_deprecated",
            "old": old,
            "new": new,
            "contract": "F3.3_GRAPH_CONTRACT.md",
        },
    )


# =====================================================================
# CANONICAL
# =====================================================================

@router.get("/cases/{case_id}")
async def get_case_graph(
    case_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    service = _get_graph_read_service(request)
    uow_factory = _get_uow_factory(request)
    async with uow_factory.create() as uow:
        return await service.get_graph(uow=uow, case_id=case_id)


@router.get("/cases/{case_id}/summary")
async def get_case_summary(
    case_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    service = _get_graph_read_service(request)
    uow_factory = _get_uow_factory(request)
    async with uow_factory.create() as uow:
        return await service.get_stats(uow=uow, case_id=case_id)


@router.get("/cases/{case_id}/metrics")
async def get_case_metrics(
    case_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    service = _get_graph_read_service(request)
    uow_factory = _get_uow_factory(request)
    async with uow_factory.create() as uow:
        return await service.get_metrics(uow=uow, case_id=case_id)


@router.get("/cases/{case_id}/entities")
async def list_case_entities(
    case_id: UUID,
    request: Request,
    limit: int = Query(1000, ge=1, le=5000),
    current_user: User = Depends(get_current_active_user),
):
    service = _get_graph_read_service(request)
    uow_factory = _get_uow_factory(request)
    async with uow_factory.create() as uow:
        entities = await service.get_entities(uow=uow, case_id=case_id, limit=limit)
    return {
        "case_id": str(case_id),
        "entities": entities,
        "count": len(entities),
        "limit": limit,
    }


@router.get("/cases/{case_id}/relationships")
async def list_case_relationships(
    case_id: UUID,
    request: Request,
    limit: int = Query(5000, ge=1, le=10000),
    current_user: User = Depends(get_current_active_user),
):
    service = _get_graph_read_service(request)
    uow_factory = _get_uow_factory(request)
    async with uow_factory.create() as uow:
        rels = await service.get_relationships(uow=uow, case_id=case_id, limit=limit)
    return {
        "case_id": str(case_id),
        "relationships": rels,
        "count": len(rels),
        "limit": limit,
    }


@router.get("/cases/{case_id}/key-actors")
async def list_case_key_actors(
    case_id: UUID,
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
):
    service = _get_graph_read_service(request)
    uow_factory = _get_uow_factory(request)
    async with uow_factory.create() as uow:
        actors = await service.get_key_actors(uow=uow, case_id=case_id, limit=limit)
    return {
        "case_id": str(case_id),
        "actors": actors,
        "count": len(actors),
    }


@router.get("/cases/{case_id}/collusion")
async def get_case_collusion(
    case_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """
    Return Graph COLLUSION relationship edges for a case.

    Semantics (F3.3 LOCKED):
      COLLUSION relationship edges  ≠  COLLUSION detections
    """
    uow_factory = _get_uow_factory(request)
    service = _get_graph_read_service(request)

    async with uow_factory.create() as uow:
        relationships = await service.get_relationships(
            uow=uow, case_id=case_id, limit=10000
        )

    collusion_edges = [
        r for r in relationships
        if str(r.get("relationship_type", "")).upper() == "COLLUSION"
    ]

    return {
        "case_id": str(case_id),
        "collusion_relationships": collusion_edges,
        "collusion_relationship_count": len(collusion_edges),
        # Detection persistence intentionally decoupled from graph read.
        "detection_backed": False,
    }


# =====================================================================
# LEGACY — 301 redirect (case_id present)
# =====================================================================

@router.get("/stats", deprecated=True)
async def legacy_stats(case_id: UUID = Query(...)):
    return RedirectResponse(
        url=f"/api/v1/graph/cases/{case_id}/summary", status_code=301
    )


@router.get("/metrics", deprecated=True)
async def legacy_metrics(case_id: UUID = Query(...)):
    return RedirectResponse(
        url=f"/api/v1/graph/cases/{case_id}/metrics", status_code=301
    )


@router.get("/entities", deprecated=True)
async def legacy_entities(case_id: UUID = Query(...)):
    return RedirectResponse(
        url=f"/api/v1/graph/cases/{case_id}/entities", status_code=301
    )


@router.get("/relationships", deprecated=True)
async def legacy_relationships(case_id: UUID = Query(...)):
    return RedirectResponse(
        url=f"/api/v1/graph/cases/{case_id}/relationships", status_code=301
    )


@router.get("/key-actors", deprecated=True)
async def legacy_key_actors(case_id: UUID = Query(...)):
    return RedirectResponse(
        url=f"/api/v1/graph/cases/{case_id}/key-actors", status_code=301
    )


# =====================================================================
# LEGACY — 410 Gone (no target / ambiguous)
# =====================================================================

@router.get("", deprecated=True)
async def legacy_root():
    _gone("/api/v1/graph", "/api/v1/graph/cases/{case_id}")


@router.get("/collusion/{case_id}", deprecated=True)
async def legacy_collusion(case_id: UUID):
    _gone(
        f"/api/v1/graph/collusion/{case_id}",
        f"/api/v1/graph/cases/{case_id}/collusion",
    )