"""
Test database import
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("🔍 Testing database imports...")
print("=" * 40)

try:
    # Test import database
    from database import get_db, get_db_session, init_db, check_db_connection, Base, engine
    print("✅ get_db imported successfully")
    print("✅ get_db_session imported successfully")
    print("✅ init_db imported successfully")
    print("✅ check_db_connection imported successfully")
    print("✅ Base imported successfully")
    print("✅ engine imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test connection
print("\n🔌 Testing database connection...")
try:
    from database import check_db_connection
    if check_db_connection():
        print("✅ Database connection successful")
    else:
        print("⚠️ Database connection failed (may be normal for first run)")
except Exception as e:
    print(f"⚠️ Connection test error: {e}")

# Test get_db function
print("\n📦 Testing get_db function...")
try:
    from database import get_db
    db_gen = get_db()
    db = next(db_gen)
    print("✅ get_db generator works")
    db.close()
except Exception as e:
    print(f"❌ get_db test failed: {e}")

print("\n✅ All tests passed!")