"""
NEMESIS Madina - Canonical Tenant ORM Model

Canonical persistence model for the tenants table.

The database schema is defined by Alembic migration:
    4c60c838bdd2_create_canonical_tenants_table.py

This ORM model MUST remain structurally aligned with that frozen schema.
"""

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=sa.text("gen_random_uuid()"),
    )

    name = Column(
        String(255),
        nullable=False,
    )

    code = Column(
        String(50),
        nullable=False,
        unique=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Tenant {self.code}: {self.name}>"