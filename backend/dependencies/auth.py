"""
Authentication Dependencies for FastAPI
"""
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from backend.database import get_db
from backend.security.models import User
from backend.security.enums import UserRole
from backend.services.jwt_service import JWTService
from backend.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """Get current authenticated user from JWT token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        payload = JWTService.verify_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return current_user

def require_roles(*allowed_roles: UserRole):
    """Dependency factory for role-based access control"""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        if current_user.role not in allowed_roles and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    return role_checker

# Pre-defined role dependencies
require_admin = require_roles(UserRole.ADMIN)
require_investigator = require_roles(UserRole.ADMIN, UserRole.INVESTIGATOR)
require_analyst = require_roles(UserRole.ADMIN, UserRole.INVESTIGATOR, UserRole.ANALYST)

# Optional auth (for endpoints that can work without auth)
async def get_optional_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    if not token:
        return None
    
    try:
        payload = JWTService.verify_access_token(token)
        username = payload.get("sub")
        if username:
            user = db.query(User).filter(User.username == username).first()
            return user if user and user.is_active else None
    except:
        return None