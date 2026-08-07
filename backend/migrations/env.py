# backend/migrations/env.py

import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add project root to path
sys.path.insert(0, '.')

from backend.config.settings import settings
from backend.persistence_inventory import get_alembic_managed_tables, validate_database_against_inventory

# Validate inventory on startup
validate_database_against_inventory()

# Get active ORM tables (Alembic managed)
ACTIVE_ORM_TABLES = get_alembic_managed_tables()


def include_object(obj, name, type_, reflected, compare_to):
    if type_ != "table":
        return True
    if reflected and compare_to is None:
        return False
    if name not in ACTIVE_ORM_TABLES:
        return False
    return True


def run_migrations_offline():
    from backend.bootstrap.models import bootstrap_models
    from backend.database import Base
    bootstrap_models()
    target_metadata = Base.metadata
    
    context.configure(
        url=settings.DATABASE_SYNC_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    from backend.bootstrap.models import bootstrap_models
    from backend.database import Base
    bootstrap_models()
    target_metadata = Base.metadata
    
    alembic_config = context.config
    configuration = alembic_config.get_section(alembic_config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_SYNC_URL
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )
        
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()