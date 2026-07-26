"""
Security module - Authentication and Authorization (FastAPI layer).
"""
import os
import jwt
import bcrypt
import hashlib
import psycopg2
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext

from backend.security.auth_core import (
    create_access_token,
    decode_token,
    verify_token,
    authenticate_user,
    get_user,
)

from backend.security.auth_handler import (
    verify_websocket_token,
    decode_jwt_token,
    create_jwt_token,
)


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

# ============================================================
# CONFIGURATION
# ============================================================

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "nemesis-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# MODELS
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str = "investigator"


# ============================================================
# PASSWORD HELPERS
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


# ============================================================
# DEPENDENCIES
# ============================================================

async def get_current_user(token: str = Depends(security)):
    """Get current user from token - compatibility function"""
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return {"username": username}
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user - compatibility function"""
    return current_user


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/login")
async def login(request: LoginRequest):
    """Login endpoint - returns JWT token"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, username, password_hash, role, is_active
            FROM users WHERE username = %s
        """, (request.username,))
        user = cur.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        is_valid = False
        if user[2].startswith('$2b$') or user[2].startswith('$2a$'):
            is_valid = bcrypt.checkpw(request.password.encode(), user[2].encode())
        else:
            sha256_hash = hashlib.sha256(request.password.encode()).hexdigest()
            is_valid = sha256_hash == user[2]
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user[4] != 'true':
            raise HTTPException(status_code=403, detail="User account is disabled")
        
        token_data = {
            "sub": user[0],
            "username": user[1],
            "role": user[3]
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user[0],
            "username": user[1],
            "role": user[3]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.post("/register")
async def register(request: RegisterRequest):
    """Register new user"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM users WHERE username = %s OR email = %s", 
                   (request.username, request.email))
        if cur.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        hashed = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode()
        user_id = str(uuid.uuid4())
        
        cur.execute("""
            INSERT INTO users (id, username, email, full_name, password_hash, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, request.username, request.email, request.full_name, hashed, request.role, 'true'))
        conn.commit()
        
        return {
            "id": user_id,
            "username": request.username,
            "email": request.email,
            "role": request.role,
            "message": "User registered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


# ============================================================
# COMPATIBILITY PROXY
# ============================================================

class AuthHandlerProxy:
    """Compatibility proxy for legacy auth_handler imports."""
    
    @staticmethod
    def verify_token(token: str):
        return verify_token(token)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        return create_access_token(data, expires_delta)


__all__ = [
    # From auth_core
    "create_access_token",
    "decode_token",
    "verify_token",
    "authenticate_user",
    "get_user",
    # From auth_handler
    "verify_websocket_token",
    "decode_jwt_token",
    "create_jwt_token",
    # Proxy
    "AuthHandlerProxy",
    # FastAPI
    "LoginRequest",
    "RegisterRequest",
    "auth_handler",
]
