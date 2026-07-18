from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from backend.infrastructure.database import get_db
from backend.security.models import User, Institution
from backend.security.auth import create_access_token
from backend.security.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    institution_id: str


@router.post("/login")
async def login(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_db),
):
    logger.info(f"Login attempt: {login_data.username}")
    
    result = await session.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        logger.error(f"User not found: {login_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        logger.error(f"User inactive: {login_data.username}")
        raise HTTPException(status_code=401, detail="User is inactive")
    
    token_data = {
        "sub": user.id,
        "username": user.username,
        "role": user.role.value,
        "institution_id": user.institution_id,
    }
    access_token = create_access_token(token_data)
    
    logger.info(f"Login successful: {user.username}")
    
    return {"access_token": access_token, "token_type": "bearer", "expires_in": 86400}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        institution_id=current_user.institution_id,
    )
