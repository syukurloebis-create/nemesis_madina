# backend/bootstrap/models.py - COMPLETE VERSION

"""
ORM Model Bootstrap Module

Imports all canonical ORM models for registration.
"""

import logging

logger = logging.getLogger(__name__)
_bootstrapped = False


def bootstrap_models(force: bool = False) -> None:
    """Bootstrap all ORM models."""
    global _bootstrapped
    
    if _bootstrapped and not force:
        return
    
    logger.info("Bootstrapping ORM models...")
    
    # ============================================
    # CANONICAL MODELS (Single Source of Truth)
    # ============================================
    
    # Core models - User is still in models/user.py
    # (We're not changing this yet - Phase 2)
    import backend.security.models
    import backend.models.user
    import backend.models.event         # events, snapshots
    import backend.cases.models         # cases (canonical)
    
    # Infrastructure models
    import backend.infrastructure.models.read_models
    import backend.infrastructure.models.projection_checkpoint
    import backend.infrastructure.models.outbox
    import backend.infrastructure.models.procurement
    
    # Domain models
    import backend.evidence.models
    import backend.graph.models
    import backend.intelligence.models
    
    # Security models (skip User duplicate - handled in Phase 2)
    # import backend.security.models  # Contains duplicate User - skip for now
    
    # Legacy compatibility
    import backend.models.existing
    
    # Verification
    from backend.database import Base
    table_count = len(Base.metadata.tables)
    logger.info(f"ORM models bootstrapped: {table_count} tables registered")
    
    if table_count == 0:
        logger.warning("No tables registered after bootstrap - check model imports")
    
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
