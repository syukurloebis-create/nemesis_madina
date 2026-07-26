#!/usr/bin/env python3
"""
Quick Backend Check - Fast health check for CI/CD.
"""

import sys
import os
from pathlib import Path

def check_critical_files():
    """Check critical files exist."""
    critical = [
        "backend/main.py",
        "backend/core/container.py",
        "backend/bootstrap/container_builder.py",
        "backend/infrastructure/unit_of_work.py",
        "backend/graph/domain/aggregate.py",
    ]
    
    missing = []
    for f in critical:
        if not Path(f).exists():
            missing.append(f)
    
    return missing

def check_imports():
    """Check critical imports."""
    critical_imports = [
        "backend.core.container",
        "backend.bootstrap.container_builder",
        "backend.infrastructure.unit_of_work",
        "backend.graph.domain.aggregate",
    ]
    
    missing = []
    for imp in critical_imports:
        try:
            __import__(imp)
        except ImportError:
            missing.append(imp)
    
    return missing

def main():
    print("🔍 Quick Backend Check")
    print("=" * 40)
    
    # Check files
    missing_files = check_critical_files()
    if missing_files:
        print("❌ Missing files:")
        for f in missing_files:
            print(f"   - {f}")
    else:
        print("✅ All critical files present")
    
    # Check imports
    missing_imports = check_imports()
    if missing_imports:
        print("❌ Missing imports:")
        for imp in missing_imports:
            print(f"   - {imp}")
    else:
        print("✅ All critical imports work")
    
    if missing_files or missing_imports:
        return 1
    
    print("✅ Quick check passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())