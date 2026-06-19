#!/usr/bin/env python3
"""Simple test to verify Python can find backend module"""

import os
import sys

# Get project root
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# Add to path
sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

# Try to import
try:
    import backend
    print(f"[OK] Backend module found at: {backend.__file__}")
except ImportError as e:
    print(f"[ERR] Cannot import backend: {e}")
    
# List backend directory contents
backend_dir = os.path.join(project_root, "backend")
if os.path.exists(backend_dir):
    print(f"\nBackend directory contents:")
    for item in os.listdir(backend_dir)[:10]:
        print(f"  - {item}")
