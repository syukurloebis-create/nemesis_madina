from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
import hashlib
import uuid
import os
import psycopg2

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



# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/login")
async def login(request: LoginRequest):
    """Login endpoint - returns JWT token"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Cari user
        cur.execute("""
            SELECT id, username, password_hash, role, is_active
            FROM users WHERE username = %s
        """, (request.username,))
        user = cur.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verifikasi password (support bcrypt & SHA256)
        is_valid = False
        if user[2].startswith('$2b$') or user[2].startswith('$2a$'):
            is_valid = bcrypt.checkpw(request.password.encode(), user[2].encode())
        else:
            # SHA256 fallback
            sha256_hash = hashlib.sha256(request.password.encode()).hexdigest()
            is_valid = sha256_hash == user[2]
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check active
        if user[4] != 'true':
            raise HTTPException(status_code=403, detail="User account is disabled")
        
        # Create token
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
        # Check if user exists
        cur.execute("SELECT COUNT(*) FROM users WHERE username = %s OR email = %s", 
                   (request.username, request.email))
        if cur.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Hash password with bcrypt
        hashed = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode()
        user_id = str(uuid.uuid4())
        
        # Insert user
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
# ADDITIONAL FUNCTIONS FOR COMPATIBILITY
# ============================================================

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

async def get_current_user(token: str = Depends(security)):
    """Get current user from token - compatibility function"""
    from fastapi import HTTPException, status
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

async def authenticate_user(db, username: str, password: str):
    """Authenticate user - compatibility function"""
    import psycopg2
    try:
        conn = psycopg2.connect(
            host='postgres',
            port=5432,
            database='nemesis_db',
            user='nemesis',
            password='nemesis123'
        )
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user:
            return False
        
        if not verify_password(password, user[2]):
            return False
        
        return {"id": str(user[0]), "username": user[1]}
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token - compatibility function"""
    import os
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "nemesis-secret-key-change-in-production")
    ALGORITHM = "HS256"
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60*24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """
    Decode JWT token and return payload.
    Compatibility function for routers.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.PyJWTError:
        return None