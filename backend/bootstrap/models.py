# backend/bootstrap/models.py - COMPLETE VERSION

"""
ORM Model Bootstrap Module

Imports all canonical ORM models for registration.
"""

import logging

logger = logging.getLogger(__name__)
_bootstrapped = False


def bootstrap_models(force: bool = False) -> None:
    """
    Bootstrap all ORM models.
    
    This function should ONLY register models with Base.metadata.
    It should NOT create tables, run DDL, or have side effects.
    """
    global _bootstrapped
    
    if _bootstrapped and not force:
        return
    
    # Import all model modules to register with Base.metadata
    import backend.models.tenant
    import backend.models.user
    import backend.models.event
    import backend.cases.models
    import backend.infrastructure.models.read_models
    import backend.infrastructure.models.projection_checkpoint
    import backend.infrastructure.models.outbox
    import backend.infrastructure.models.procurement
    import backend.evidence.models
    import backend.graph.models
    import backend.intelligence.models

    from backend.models.existing import AuditLog 
    
    # Do NOT call create_all() here
    # Do NOT run any DDL
    # Do NOT connect to database
    
    _bootstrapped = True


def is_bootstrapped() -> bool:
    """Check if models have been bootstrapped."""
    return _bootstrapped


def get_registry_summary() -> dict:
    """Get summary of registered models."""
    from backend.database import Base
    
    return {
        "bootstrapped": _bootstrapped,
        "table_count": len(Base.metadata.tables),
        "mapper_count": len(Base.registry.mappers) if hasattr(Base, 'registry') else 0,
        "tables": sorted(list(Base.metadata.tables.keys()))
    }
