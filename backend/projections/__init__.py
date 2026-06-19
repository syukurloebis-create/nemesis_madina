# backend/projections/__init__.py
from .engine import ProjectionEngine
from .case_projection import CaseProjection

__all__ = ['ProjectionEngine', 'CaseProjection']


def register_all_projections(engine: ProjectionEngine, session, tenant_id: str):
    """Register all projection handlers"""
    case_proj = CaseProjection(session, tenant_id)
    
    engine.register_handler("CASE_CREATED", case_proj.handle_case_created)
    engine.register_handler("CASE_UPDATED", case_proj.handle_case_updated)
    engine.register_handler("CASE_STATUS_CHANGED", case_proj.handle_case_status_changed)
    engine.register_handler("CASE_ASSIGNED", case_proj.handle_case_assigned)
    engine.register_handler("CASE_CLOSED", case_proj.handle_case_closed)