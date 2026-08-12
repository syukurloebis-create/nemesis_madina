# backend/security/models.py 

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
    UUID,
    ForeignKeyConstraint,
)
from sqlalchemy.sql import func
from backend.database import Base
from backend.domain.enums.security_role import SecurityRole
import uuid


class User(Base):
    __tablename__ = "users"

    # Database canonical: VARCHAR PK with UUID default
    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    username = Column(
        String,
        nullable=False,
    )

    email = Column(
        String,
        nullable=False,
    )

    full_name = Column(
        String,
        nullable=False,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
        default=SecurityRole.VIEWER.value,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("username", name="users_username_key"),
        UniqueConstraint("email", name="users_email_key"),
        ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
    )

    @property
    def hashed_password(self) -> str:
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, value: str):
        self.password_hash = value

    def __repr__(self):
        return f"<User {self.username}>"