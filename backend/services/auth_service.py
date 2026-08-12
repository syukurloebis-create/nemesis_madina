"""
Authentication Service - Canonical Implementation

SEC-4.7 & SEC-5 Contract:
- AsyncSession (canonical NEMESIS persistence)
- SecurityRole (single source of truth)
- JWT sub = User.id (immutable identity)
- password_hash (canonical field)
- User has 8 fields only (id, username, email, full_name, password_hash, role, is_active, created_at)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

import bcrypt

from backend.security.models import User
from backend.domain.enums.security_role import SecurityRole
from backend.schemas.auth import UserCreate, UserUpdate, AdminUserUpdate
from backend.services.jwt_service import JWTService


class AuthService:
    """Authentication business logic - Canonical Async Implementation"""

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password using bcrypt."""
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against bcrypt hash."""
        plain_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hash_bytes)

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

        if not AuthService.verify_password(password, user.password_hash):
            return None

        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create new user."""
        # Check if username already exists
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user - role is FORCED to VIEWER for public registration
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=AuthService.get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=SecurityRole.VIEWER.value,
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_data: UserUpdate) -> User:
        """Update user information (self-service only)."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update fields
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.password is not None:
            user.password_hash = AuthService.get_password_hash(user_data.password)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def admin_update_user(db: AsyncSession, user_id: str, user_data: AdminUserUpdate) -> User:
        """Administrative user update - allows role and is_active changes."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update administrative fields
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.password is not None:
            user.password_hash = AuthService.get_password_hash(user_data.password)
        if user_data.role is not None:
            try:
                user.role = SecurityRole.from_legacy(user_data.role).value
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role: {user_data.role}"
                )
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        await db.commit()
        await db.refresh(user)
        return user


    @staticmethod
    def create_tokens(user: User) -> Dict[str, Any]:
        """Create access and refresh tokens."""
        token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role,
            "user_id": user.id,
            "tenant_id": str(user.tenant_id),
        }

        access_token = JWTService.create_access_token(token_data)
        refresh_token = JWTService.create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60,
            "user": user,
        }