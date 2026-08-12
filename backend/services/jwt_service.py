"""
JWT Token Service
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import HTTPException, status
from jose import JWTError, jwt

from backend.config.auth import auth_settings


class JWTService:
    """JWT token management service."""

    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(
            minutes=auth_settings.access_token_expire_minutes
        )

        to_encode = data.copy()
        to_encode.update(
            {
                "exp": expire,
                "type": "access",
                "iat": now,
            }
        )

        return jwt.encode(
            to_encode,
            auth_settings.secret_key,
            algorithm=auth_settings.algorithm,
        )

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(
            days=auth_settings.refresh_token_expire_days
        )

        to_encode = data.copy()
        to_encode.update(
            {
                "exp": expire,
                "type": "refresh",
                "iat": now,
            }
        )

        return jwt.encode(
            to_encode,
            auth_settings.secret_key,
            algorithm=auth_settings.algorithm,
        )

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(
                token,
                auth_settings.secret_key,
                algorithms=[auth_settings.algorithm],
            )
            return payload
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(exc)}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """Verify access token is valid and not expired."""
        payload = JWTService.decode_token(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    @staticmethod
    def verify_refresh_token(token: str) -> Dict[str, Any]:
        """Verify refresh token is valid and not expired."""
        payload = JWTService.decode_token(token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
        """Generate a new access token from a refresh token."""
        payload = JWTService.verify_refresh_token(refresh_token)

        user_data = {
            "sub": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role"),
            "tenant_id": payload.get("tenant_id"),
            "user_id": payload.get("user_id"),
        }

        access_token = JWTService.create_access_token(user_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_settings.access_token_expire_minutes * 60,
        }