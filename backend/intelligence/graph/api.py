from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from backend.database import get_db
from backend.intelligence.graph.service import GraphIntelligenceService
from backend.intelligence.graph.graph_store import graph_store
from backend.cases.service import CaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["Graph Intelligence"])


def get_graph_service(session: AsyncSession = Depends(get_db)) -> GraphIntelligenceService:
    return GraphIntelligenceService(session)


@router.post("/cases/{case_id}/extract-entities")
async def extract_entities(case_id: str, service: GraphIntelligenceService = Depends(get_graph_service)) -> dict:
    logger.info(f"Extracting for {case_id}")

    # Extract entities
    entities = await service.extract_entities_from_case(case_id)
    stored_entities = graph_store.add_entities(case_id, entities)

    # Get transactions from case metadata
    case_service = CaseService(service.session)
    case = await case_service.get_case(case_id)

    stored_tx = 0
    if case and case.case_metadata:
        transactions = case.case_metadata.get("transactions", [])
        for tx in transactions:
            frm = tx.get("from")
            to = tx.get("to")
            amt = tx.get("amount", 0)
            if frm and to:
                from_node = f"company:{frm}"
                to_node = f"company:{to}"
                graph_store.add_node(case_id, from_node, "company", frm)
                graph_store.add_node(case_id, to_node, "company", to)
                graph_store.add_edge(case_id, from_node, to_node, "financial", amount=amt)
                stored_tx += 1

    summary = graph_store.get_graph_summary(case_id)
    return {
        "case_id": case_id,
        "entities": len(entities),
        "entities_stored": stored_entities,
        "transactions_stored": stored_tx,
        "nodes": summary.get("node_count", 0),
        "edges": summary.get("edge_count", 0),
    }


@router.post("/cases/{case_id}/analyze-collusion")
async def analyze_collusion(case_id: str, force: bool = True, service: GraphIntelligenceService = Depends(get_graph_service)) -> dict:
    if force:
        await extract_entities(case_id, service)
    return await service.analyze_collusion(case_id, force)


@router.get("/cases/{case_id}/collusion-summary")
async def collusion_summary(case_id: str, service: GraphIntelligenceService = Depends(get_graph_service)) -> dict:
    return await service.get_collusion_summary(case_id)


@router.get("/cases/{case_id}/graph-summary")
async def graph_summary(case_id: str) -> dict:
    return graph_store.get_graph_summary(case_id)


@router.get("/cases/{case_id}/graph")
async def get_full_graph(case_id: str) -> dict:
    if not graph_store.case_exists(case_id):
        return {"case_id": case_id, "nodes": [], "edges": [], "has_data": False}
    return {
        "case_id": case_id,
        "nodes": graph_store.get_nodes(case_id),
        "edges": graph_store.get_edges(case_id),
        "has_data": True,
    }


@router.delete("/cases/{case_id}/graph")
async def clear_graph(case_id: str) -> dict:
    graph_store.clear_case(case_id)
    return {"case_id": case_id, "cleared": True}
