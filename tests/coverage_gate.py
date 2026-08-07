# scripts/tests/coverage_gate.py
"""
Coverage gate with threshold enforcement.
"""

import subprocess
import sys
from pathlib import Path


def run_coverage_gate():
    """Run coverage with threshold."""
    threshold = 95
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "scripts/tests/",
        "--cov=metadata_inventory",
        "--cov-report=term",
        "--cov-fail-under=" + str(threshold)
    ])
    
    if result.returncode != 0:
        print(f"\n❌ Coverage below {threshold}% threshold")
        sys.exit(1)
    
    print(f"\n✅ Coverage above {threshold}% threshold")
    sys.exit(0)


if __name__ == "__main__":
    run_coverage_gate()