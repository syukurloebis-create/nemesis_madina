imdocker exec -it nemesis_madina-api-1 bash
  cat >> auth.py << 'EOF' << 'EOF'
imdocker exec -it nemesis_madina-api-1 bash
  cat >> auth.py << 'EOF' << 'EOF'
import re

with open('auth.py', 'r') as f:
    content = f.read()

# Cek apakah register sudah ada
if '@router.post("/register")' in content:
    print("✅ Register endpoint already exists")
else:
    # Tambahkan register endpoint sebelum class AuthService
    register_code = '''
@router.post("/register")
async def register_user_endpoint(request: RegisterRequest):
    """Register new user"""
    conn = psycopg2.connect(DB_CONFIG)
    cur = conn.cursor()

    try:
        # Check if user exists
        cur.execute("SELECT COUNT(*) FROM users WHERE username = %s OR email = %s",
                   (request.username, request.email))
        if cur.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="Username or email already exists")

        # Hash password with bcrypt
        import bcrypt
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
'''

