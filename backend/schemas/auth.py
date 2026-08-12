"""
Authentication Schemas - Canonical SEC-6 Contract
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator
from backend.services.password_validator import PasswordValidator


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., max_length=100)
    # REMOVED: role (forced in service)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)

    @validator("password")
    def validate_password(cls, v):
        is_valid, error = PasswordValidator.validate(v)
        if not is_valid:
            raise ValueError(error)
        return v

    @validator("username")
    def validate_username(cls, v):
        if not v.replace("_", "").isalnum():
            raise ValueError(
                "Username must contain only alphanumeric characters and underscore"
            )
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    # REMOVED: role
    # REMOVED: is_active

    @validator("password")
    def validate_password(cls, v):
        if v is not None:
            is_valid, error = PasswordValidator.validate(v)
            if not is_valid:
                raise ValueError(error)
        return v


class AdminUserUpdate(BaseModel):
    """Administrative user update - requires admin privileges."""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    role: Optional[str] = None
    is_active: Optional[bool] = None
    tenant_id: Optional[UUID] = None

    @validator("password")
    def validate_password(cls, v):
        if v is not None:
            is_valid, error = PasswordValidator.validate(v)
            if not is_valid:
                raise ValueError(error)
        return v


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    tenant_id: UUID
    is_active: bool
    created_at: datetime  # ← FIXED: datetime, not object

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    sub: str
    username: str
    role: str
    user_id: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=72)

    @validator("new_password")
    def validate_password(cls, v):
        is_valid, error = PasswordValidator.validate(v)
        if not is_valid:
            raise ValueError(error)
        return v