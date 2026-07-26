#!/bin/bash
echo "🔧 QUICK FIX INFRASTRUCTURE"
echo "==========================="

cd ~/nemesis_madina

# 1. Create infrastructure directory if missing
echo "📁 Creating infrastructure directory..."
mkdir -p infrastructure

# 2. Create __init__.py
echo "📝 Creating infrastructure/__init__.py..."
cat > infrastructure/__init__.py << 'EOF'
"""
Infrastructure Module
"""
from .database import get_db, init_db, get_db_session, get_pool, AsyncSessionLocal
__all__ = ['get_db', 'init_db', 'get_db_session', 'get_pool', 'AsyncSessionLocal']
EOF

# 3. Create database.py in infrastructure
echo "📝 Creating infrastructure/database.py..."
cat > infrastructure/database.py << 'EOF'
"""
Infrastructure Database
Re-exports from main database
"""
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from database import get_db, get_db_session, init_db, check_db_connection, SessionLocal
    from database import Base, engine
    get_pool = SessionLocal
    AsyncSessionLocal = SessionLocal
    print("✅ infrastructure.database loaded")
except ImportError as e:
    print(f"⚠️ Could not load database: {e}")
    
    def get_db():
        return None
    
    def init_db():
        pass
    
    get_pool = None
    AsyncSessionLocal = None
    SessionLocal = None
    Base = None
    engine = None
EOF

# 4. Test import
echo ""
echo "🧪 Testing import..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from infrastructure.database import get_db, init_db, get_pool, AsyncSessionLocal
    print('✅ All imports successful')
    print(f'   get_db: {get_db}')
    print(f'   init_db: {init_db}')
    print(f'   get_pool: {get_pool}')
    print(f'   AsyncSessionLocal: {AsyncSessionLocal}')
except Exception as e:
    print(f'❌ Import failed: {e}')
"

echo ""
echo "✅ Infrastructure fixed!"