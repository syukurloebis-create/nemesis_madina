# backend/security/models.py

from backend.security.enums import UserRole
from backend.database import Base
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
import uuid


class User(Base):
    __tablename__ = "users"
    
    # Canonical fields (match database)
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=True)  # Will be replaced with Enum after migration
    is_active = Column(String, nullable=True)  # VARCHAR as per database
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Compatibility property for legacy code
    @property
    def hashed_password(self) -> str:
        """Legacy compatibility - maps to password_hash."""
        return self.password_hash
    
    @hashed_password.setter
    def hashed_password(self, value: str):
        self.password_hash = value
    
    def __repr__(self):
        return f"<User {self.username}>"