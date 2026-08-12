"""
Authentication Router - Canonical SEC-6 Implementation

Contract:
- AsyncSession (canonical NEMESIS persistence)
- AuthService (async, SecurityRole, JWT sub=User.id)
- JWTService (single issuer/decoder)
- UserResponse schema (id=str, no last_login)
- No UserRole, no Session, no db.query()
- No locked_until, no updated_at, no is_superuser
- Route prefix handled by main.py (/api/v1/auth)
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.security.models import User
from backend.schemas.auth import (
    LoginRequest, LoginResponse, UserCreate, UserResponse,
    UserUpdate, RefreshTokenRequest, RefreshTokenResponse,
    ChangePasswordRequest, AdminUserUpdate
)
from backend.services.auth_service import AuthService
from backend.services.jwt_service import JWTService
from backend.dependencies.auth import get_current_user, require_admin
from backend.middleware.rate_limit import rate_limit

# Prefix is added in main.py: /api/v1/auth
router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
@rate_limit(limit=5, window=60)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    user = await AuthService.authenticate_user(
        db, login_data.username, login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    tokens = AuthService.create_tokens(user)

    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        expires_in=30 * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    result = JWTService.refresh_access_token(refresh_data.refresh_token)
    return RefreshTokenResponse(**result)


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register new user (public endpoint)"""
    user = await AuthService.create_user(db, user_data)
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user information"""
    updated_user = await AuthService.update_user(db, current_user.id, user_data)
    return UserResponse.model_validate(updated_user)


@router.post("/me/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change current user's password"""
    if not AuthService.verify_password(
        password_data.current_password,
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    current_user.password_hash = AuthService.get_password_hash(
        password_data.new_password
    )
    await db.commit()

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout current user"""
    return {"message": "Logged out successfully"}


# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin)
):
    """List all users (admin only)"""
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    return [UserResponse.model_validate(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get user by ID (admin only)"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: str,
    user_data: AdminUserUpdate,  # ← ADMIN SCHEMA
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Update user by ID (admin only)"""
    updated_user = await AuthService.admin_update_user(db, user_id, user_data)
    return UserResponse.model_validate(updated_user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete user (admin only)"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}