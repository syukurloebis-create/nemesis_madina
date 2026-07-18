"""
Pytest Configuration - Fixed import paths
"""
import sys
import os
from pathlib import Path

# Get the absolute path
project_root = Path(__file__).resolve().parent.parent.parent
backend_dir = project_root / 'backend'

# Add to Python path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

# Now import works
try:
    from backend.main import app
    print(f"✅ Successfully imported app")
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    # Try alternative import
    try:
        import main
        app = main.app
        print("✅ Imported using alternative method")
    except ImportError:
        print("❌ Could not import app")
        app = None