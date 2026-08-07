# scripts/tests/mutation/test_mutation.py
"""
Mutation testing to verify test quality.
"""

import subprocess
import sys
from pathlib import Path


def run_mutation_testing():
    """Run mutation testing using mutmut."""
    print("\n" + "="*80)
    print(" MUTATION TESTING")
    print("="*80 + "\n")
    
    # Check if mutmut is installed
    try:
        import mutmut
    except ImportError:
        print("⚠️ mutmut not installed. Install with: pip install mutmut")
        print("   Skipping mutation testing.")
        return 0
    
    # Run mutmut
    result = subprocess.run([
        sys.executable, "-m", "mutmut",
        "run",
        "--paths-to-mutate", "scripts/metadata_inventory",
        "--tests-dir", "scripts/tests"
    ])
    
    if result.returncode != 0:
        print("❌ Mutation testing failed")
        return 1
    
    # Get mutation score
    result = subprocess.run([
        sys.executable, "-m", "mutmut",
        "results"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    
    # Check mutation score
    # Target: >80% mutation score
    # This would parse the output to check score
    
    return 0


if __name__ == "__main__":
    sys.exit(run_mutation_testing())