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
