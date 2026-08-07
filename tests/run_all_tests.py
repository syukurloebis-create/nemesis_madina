# tests/run_all_tests.py
"""
Run all test layers with proper configuration.
"""

import sys
import subprocess
from pathlib import Path


def run_all_tests():
    """Run all test layers."""
    # Project root
    project_root = Path(__file__).parent.parent
    
    # Set PYTHONPATH to include scripts directory
    scripts_dir = project_root / "scripts"
    env = dict(subprocess.os.environ)
    pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(scripts_dir) + (":" + pythonpath if pythonpath else "")
    
    # Test directories
    tests_dir = Path(__file__).parent
    
    # Layers to run
    layers = [
        ("Unit", "unit"),
        ("Rule", "rules"),
        ("Integration", "integration"),
        ("E2E", "e2e"),
        ("Regression", "regression"),
        ("Golden", "golden"),
        ("Property", "property"),
        ("Performance", "performance"),
    ]
    
    print("\n" + "="*80)
    print(" RUNNING METADATA INVENTORY TESTS")
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    for name, layer in layers:
        layer_path = tests_dir / layer
        
        if not layer_path.exists():
            print(f"\n⚠️ {name} Tests - directory not found: {layer_path}")
            continue
        
        print(f"\n📋 {name} Tests...")
        
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            str(layer_path),
            "-v",
            "--tb=short",
            "-p", "no:json-report"  # Disable json-report for cleaner output
        ], env=env)
        
        if result.returncode == 0:
            print(f"  ✅ {name} Tests PASSED")
            passed += 1
        else:
            print(f"  ❌ {name} Tests FAILED")
            failed += 1
    
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print("="*80 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())