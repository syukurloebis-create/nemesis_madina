#!/usr/bin/env python3
"""
NEMESIS FASE 6 - Validation Script
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def validate():
    print("\n" + "="*60)
    print("FASE 6: VALIDATION")
    print("="*60)
    
    errors = []
    
    # 1. Check test structure
    print("\n[1/4] Checking test structure...")
    
    required_dirs = [
        "tests/unit",
        "tests/integration",
        "tests/performance",
    ]
    
    for dir_path in required_dirs:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists():
            print(f"  [OK] {dir_path}/")
        else:
            errors.append(f"Missing directory: {dir_path}")
    
    # 2. Check test files
    print("\n[2/4] Checking test files...")
    
    test_files = [
        "tests/conftest.py",
        "tests/unit/test_evidence.py",
        "tests/unit/test_intelligence.py",
        "tests/unit/test_telemetry.py",
        "tests/integration/test_event_to_projection.py",
        "tests/integration/test_evidence_lineage.py",
        "tests/performance/test_load.py",
        "tests/performance/test_concurrency.py",
    ]
    
    for test_file in test_files:
        full_path = PROJECT_ROOT / test_file
        if full_path.exists():
            print(f"  [OK] {test_file}")
        else:
            errors.append(f"Missing test file: {test_file}")
    
    # 3. Check pytest configuration
    print("\n[3/4] Checking pytest configuration...")
    
    pytest_ini = PROJECT_ROOT / "pytest.ini"
    if pytest_ini.exists():
        content = pytest_ini.read_text()
        if "asyncio_mode = auto" in content:
            print("  [OK] pytest.ini configured")
        else:
            errors.append("pytest.ini missing asyncio configuration")
    else:
        errors.append("Missing pytest.ini")
    
    # 4. Try to run a simple test
    print("\n[4/4] Running basic test...")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/test_telemetry.py", "-k", "test_counter_increment", "--tb=short"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  [OK] Basic test passes")
    else:
        errors.append(f"Basic test failed: {result.stderr[:200]}")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"[ERR] Validation failed: {len(errors)} errors")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("[OK] All validations passed!")
        print("="*60)
        return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)