"""
JWT Token Service
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from backend.config.auth import auth_settings

class JWTService:
    """JWT token management service"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        return jwt.encode(
            to_encode,
            auth_settings.JWT_SECRET_KEY,
            algorithm=auth_settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=auth_settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
        return jwt.encode(
            to_encode,
            auth_settings.JWT_SECRET_KEY,
            algorithm=auth_settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                auth_settings.JWT_SECRET_KEY,
                algorithms=[auth_settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """Verify access token is valid and not expired"""
        payload = JWTService.decode_token(token)
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return payload
    
    @staticmethod
    def verify_refresh_token(token: str) -> Dict[str, Any]:
        """Verify refresh token is valid and not expired"""
        payload = JWTService.decode_token(token)
        
        # Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        
        return payload
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
        """Generate new access token from refresh token"""
        payload = JWTService.verify_refresh_token(refresh_token)
        
        # Create new access token
        user_data = {
            "sub": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role"),
            "user_id": payload.get("user_id")
        }
        
        access_token = JWTService.create_access_token(user_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }