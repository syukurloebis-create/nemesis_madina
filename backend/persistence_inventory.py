# backend/persistence_inventory.py
"""
Persistence Inventory - Single Source of Truth

This module defines the persistence strategy for all tables in the database.
It serves as the authoritative source for Alembic migration decisions.

Lifecycle States:
- ORM_EXISTING: SQLAlchemy ORM, table exists in database
- ORM_PENDING: SQLAlchemy ORM, table does NOT exist in database yet
- SQL_REPOSITORY: Managed via raw SQL through repository layer
- SQL_ASSET: Managed via SQL files (reports, analytics)
- MIGRATION_ONLY: Created by migration but no runtime usage
- UNKNOWN: Business state not yet confirmed
- SYSTEM: Internal Alembic/system tables
"""

from enum import Enum
from typing import Set, Dict, Optional


class PersistenceType(str, Enum):
    ORM_EXISTING = "orm_existing"
    ORM_PENDING = "orm_pending"
    SQL_REPOSITORY = "sql_repository"
    SQL_ASSET = "sql_asset"
    MIGRATION_ONLY = "migration_only"
    UNKNOWN = "unknown"
    SYSTEM = "system"


# ============================================
# SINGLE SOURCE OF TRUTH
# ============================================

PERSISTENCE_INVENTORY: Dict[str, PersistenceType] = {
    # ============================================
    # ORM EXISTING (19 tables)
    # ============================================
    "alerts": PersistenceType.ORM_EXISTING,
    "anomaly_detections": PersistenceType.ORM_EXISTING,
    "audit_log": PersistenceType.ORM_EXISTING,
    "cases": PersistenceType.ORM_EXISTING,
    "collusion_detections": PersistenceType.ORM_EXISTING,
    "dashboard_view": PersistenceType.ORM_EXISTING,
    "events": PersistenceType.ORM_EXISTING,
    "evidence": PersistenceType.ORM_EXISTING,
    "findings": PersistenceType.ORM_EXISTING,
    "tenants": PersistenceType.ORM_EXISTING,
    "graph_entities": PersistenceType.ORM_EXISTING,
    "graph_metadata": PersistenceType.ORM_EXISTING,
    "graph_relationships": PersistenceType.ORM_EXISTING,
    "intelligence_reports": PersistenceType.ORM_EXISTING,
    "processed_events": PersistenceType.ORM_EXISTING,
    "projection_checkpoints": PersistenceType.ORM_EXISTING,
    "risk_scores": PersistenceType.ORM_EXISTING,
    "rup_paket_detailed": PersistenceType.ORM_EXISTING,
    "snapshots": PersistenceType.ORM_EXISTING,
    "users": PersistenceType.ORM_EXISTING,
    
    # ============================================
    # ORM PENDING (3 tables - need business decision)
    # ============================================
    "chain_of_custody": PersistenceType.ORM_PENDING,
    "fraud_detections": PersistenceType.ORM_PENDING,
    "outbox_messages": PersistenceType.ORM_PENDING,
    
    # ============================================
    # SQL REPOSITORY (16 tables)
    # ============================================
    "access_log": PersistenceType.SQL_REPOSITORY,
    "approvals": PersistenceType.SQL_REPOSITORY,
    "assignments": PersistenceType.SQL_REPOSITORY,
    "custody_chain": PersistenceType.SQL_REPOSITORY,
    "evidence_files": PersistenceType.SQL_REPOSITORY,
    "finding_action_logs": PersistenceType.SQL_REPOSITORY,
    "finding_assignments": PersistenceType.SQL_REPOSITORY,
    "finding_events": PersistenceType.SQL_REPOSITORY,
    "finding_review_decisions": PersistenceType.SQL_REPOSITORY,
    "graph_clusters": PersistenceType.SQL_REPOSITORY,
    "graph_node_scores": PersistenceType.SQL_REPOSITORY,
    "investigation_findings": PersistenceType.SQL_REPOSITORY,
    "investigation_timeline": PersistenceType.SQL_REPOSITORY,
    "outcome": PersistenceType.SQL_REPOSITORY,
    "recovery_actions": PersistenceType.SQL_REPOSITORY,
    "risk_explanations": PersistenceType.SQL_REPOSITORY,
    
    # ============================================
    # SQL ASSET (1 table)
    # ============================================
    "pattern_detections": PersistenceType.SQL_ASSET,
    
    # ============================================
    # MIGRATION ONLY (5 tables)
    # ============================================
    "finding_comments": PersistenceType.MIGRATION_ONLY,
    "fraud_evidence": PersistenceType.MIGRATION_ONLY,
    "graph_entity_metrics": PersistenceType.MIGRATION_ONLY,
    "model_metrics": PersistenceType.SQL_REPOSITORY,
    
    # ============================================
    # UNKNOWN (2 tables - need business confirmation)
    # ============================================
    
    "investigation_recommendations": PersistenceType.SQL_REPOSITORY,
    
    # ============================================
    # SYSTEM (1 table)
    # ============================================
    "alembic_version": PersistenceType.SYSTEM,
}


# ============================================
# QUERY FUNCTIONS
# ============================================

def get_orm_existing_tables() -> Set[str]:
    """ORM tables that exist in database."""
    return {
        table for table, type_ in PERSISTENCE_INVENTORY.items()
        if type_ == PersistenceType.ORM_EXISTING
    }


def get_orm_pending_tables() -> Set[str]:
    """ORM tables that do NOT exist in database yet."""
    return {
        table for table, type_ in PERSISTENCE_INVENTORY.items()
        if type_ == PersistenceType.ORM_PENDING
    }


def get_orm_tables() -> Set[str]:
    """All ORM tables (existing + pending)."""
    return get_orm_existing_tables() | get_orm_pending_tables()


def get_sql_repository_tables() -> Set[str]:
    """SQL Repository managed tables."""
    return {
        table for table, type_ in PERSISTENCE_INVENTORY.items()
        if type_ == PersistenceType.SQL_REPOSITORY
    }


def get_sql_asset_tables() -> Set[str]:
    """SQL Asset managed tables."""
    return {
        table for table, type_ in PERSISTENCE_INVENTORY.items()
        if type_ == PersistenceType.SQL_ASSET
    }


def get_migration_only_tables() -> Set[str]:
    """Migration-only tables."""
    return {
        table for table, type_ in PERSISTENCE_INVENTORY.items()
        if type_ == PersistenceType.MIGRATION_ONLY
    }


def get_unknown_tables() -> Set[str]:
    """Unknown tables needing business confirmation."""
    return {
        table for table, type_ in PERSISTENCE_INVENTORY.items()
        if type_ == PersistenceType.UNKNOWN
    }


def get_system_tables() -> Set[str]:
    """System tables."""
    return {
        table for table, type_ in PERSISTENCE_INVENTORY.items()
        if type_ == PersistenceType.SYSTEM
    }


def get_non_orm_tables() -> Set[str]:
    """All tables that should be excluded from Alembic."""
    return {
        table for table, type_ in PERSISTENCE_INVENTORY.items()
        if type_ not in (PersistenceType.ORM_EXISTING, PersistenceType.ORM_PENDING)
    }


def get_alembic_managed_tables() -> Set[str]:
    """
    Tables allowed for Alembic schema management.
    Only ORM_EXISTING tables are actively managed.
    ORM_PENDING tables are tracked but NOT yet managed.
    """
    return get_orm_existing_tables()


# ============================================
# VALIDATION
# ============================================

def validate_inventory(
    db_tables: Optional[Set[str]] = None,
    orm_tables: Optional[Set[str]] = None
) -> Dict[str, any]:
    """
    Validate inventory against actual database and ORM metadata.
    
    Args:
        db_tables: Set of table names from PostgreSQL
        orm_tables: Set of table names from Base.metadata
    
    Returns:
        Validation results dictionary
    """
    results = {
        "status": "PASS",
        "errors": [],
        "warnings": [],
        "summary": {}
    }
    
    # Check for duplicates in inventory
    all_inventory = set(PERSISTENCE_INVENTORY.keys())
    if len(all_inventory) != len(PERSISTENCE_INVENTORY):
        results["errors"].append("Duplicate entries in inventory")
        results["status"] = "FAIL"
    
    # Check category overlaps
    categories = [
        get_orm_existing_tables(),
        get_orm_pending_tables(),
        get_sql_repository_tables(),
        get_sql_asset_tables(),
        get_migration_only_tables(),
        get_unknown_tables(),
        get_system_tables(),
    ]
    
    for i, cat1 in enumerate(categories):
        for j, cat2 in enumerate(categories):
            if i < j:
                overlap = cat1 & cat2
                if overlap:
                    results["errors"].append(f"Overlap between categories: {overlap}")
                    results["status"] = "FAIL"
    
    # Validate against database if provided
    if db_tables is not None:
        # Tables in database but not in inventory
        extra = db_tables - all_inventory
        if extra:
            results["errors"].append(f"Tables in database but not in inventory: {extra}")
            results["status"] = "FAIL"
        
        # Tables in inventory but not in database
        missing = all_inventory - db_tables
        if missing:
            orm_pending = get_orm_pending_tables()
            actual_missing = missing - orm_pending  # ORM_PENDING are expected to be missing
            if actual_missing:
                results["warnings"].append(f"Tables in inventory but not in database: {actual_missing}")
    
    # Validate against ORM metadata if provided
    if orm_tables is not None:
        # ORM tables in metadata but not in inventory
        extra_orm = orm_tables - all_inventory
        if extra_orm:
            results["errors"].append(f"ORM tables not in inventory: {extra_orm}")
            results["status"] = "FAIL"
        
        # ORM tables in inventory but not in metadata
        missing_orm = get_orm_tables() - orm_tables
        if missing_orm:
            results["errors"].append(f"ORM inventory tables not in metadata: {missing_orm}")
            results["status"] = "FAIL"
    
    # Summary
    results["summary"] = {
        "total_inventory": len(all_inventory),
        "orm_existing": len(get_orm_existing_tables()),
        "orm_pending": len(get_orm_pending_tables()),
        "sql_repository": len(get_sql_repository_tables()),
        "sql_asset": len(get_sql_asset_tables()),
        "migration_only": len(get_migration_only_tables()),
        "unknown": len(get_unknown_tables()),
        "system": len(get_system_tables()),
    }
    
    return results


def validate_database_against_inventory() -> bool:
    """
    Validate database against inventory.
    
    This function uses synchronous SQLAlchemy engine because it is called
    from Alembic (synchronous runtime) and from pytest (async runtime).
    Using sync engine avoids event loop conflicts.
    """
    from sqlalchemy import create_engine, text
    from backend.config import settings

    def get_db_tables():
        """Get tables using synchronous connection."""
        # Use sync URL (remove +asyncpg if present)
        sync_url = settings.DATABASE_SYNC_URL
        if "+asyncpg" in sync_url:
            sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(
            sync_url,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
        )
        
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
            )
            tables = {row[0] for row in result}
        
        engine.dispose()
        return tables

    db_tables = get_db_tables()

    # Get ORM metadata
    from backend.bootstrap.models import bootstrap_models
    from backend.database import Base
    bootstrap_models()
    orm_tables = set(Base.metadata.tables.keys())

    results = validate_inventory(db_tables, orm_tables)

    print("=" * 60)
    print("PERSISTENCE INVENTORY VALIDATION")
    print("=" * 60)
    print(f"Status: {results['status']}")
    print(f"Total inventory: {results['summary']['total_inventory']}")
    print(f"  ORM Existing: {results['summary']['orm_existing']}")
    print(f"  ORM Pending: {results['summary']['orm_pending']}")
    print(f"  SQL Repository: {results['summary']['sql_repository']}")
    print(f"  SQL Asset: {results['summary']['sql_asset']}")
    print(f"  Migration Only: {results['summary']['migration_only']}")
    print(f"  Unknown: {results['summary']['unknown']}")
    print(f"  System: {results['summary']['system']}")
    print()

    if results["errors"]:
        print("❌ ERRORS:")
        for err in results["errors"]:
            print(f"  {err}")

    if results["warnings"]:
        print("⚠️ WARNINGS:")
        for warn in results["warnings"]:
            print(f"  {warn}")

    if not results["errors"] and not results["warnings"]:
        print("✅ All tables accounted for. Inventory is complete.")

    print("=" * 60)

    return results["status"] == "PASS"


# ============================================
# EXPORTS
# ============================================

__all__ = [
    "PersistenceType",
    "PERSISTENCE_INVENTORY",
    "get_orm_existing_tables",
    "get_orm_pending_tables",
    "get_orm_tables",
    "get_sql_repository_tables",
    "get_sql_asset_tables",
    "get_migration_only_tables",
    "get_unknown_tables",
    "get_system_tables",
    "get_non_orm_tables",
    "get_alembic_managed_tables",
    "validate_inventory",
    "validate_database_against_inventory",
]