"""
Authentication Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from backend.services.password_validator import PasswordValidator

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(default="viewer")
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, error = PasswordValidator.validate(v)
        if not is_valid:
            raise ValueError(error)
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError("Username must contain only alphanumeric characters and underscore")
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            is_valid, error = PasswordValidator.validate(v)
            if not is_valid:
                raise ValueError(error)
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    
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
    user_id: int

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=72)
    
    @validator('new_password')
    def validate_password(cls, v):
        is_valid, error = PasswordValidator.validate(v)
        if not is_valid:
            raise ValueError(error)
        return v