# run_tests.py
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

import pytest

def run_tests():
    result = pytest.main([
        "tests/test_determinism.py",
        "tests/test_concurrency.py", 
        "tests/test_ledger.py",
        "-v",
        "-x",
        "--tb=short"
    ])
    return result

if __name__ == "__main__":
    sys.exit(run_tests())