"""
Auth Simple - Endpoint login untuk testing
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
import psycopg2
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

class LoginRequest(BaseModel):
    username: str
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/login")
async def login(request: LoginRequest):
    """Login endpoint - menggunakan SHA256"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Cari user
        cur.execute("""
            SELECT id, username, password_hash, role, is_active
            FROM users 
            WHERE username = %s
        """, (request.username,))
        user = cur.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verifikasi password (SHA256)
        hashed_input = hash_password(request.password)
        if user[2] != hashed_input:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "access_token": f"token_{uuid.uuid4().hex}",
            "token_type": "bearer",
            "user_id": user[0],
            "username": user[1],
            "role": user[3]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@router.get("/health")
async def health():
    return {"status": "ok"}
