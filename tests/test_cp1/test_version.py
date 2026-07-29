import sys
from ir import CURRENT_VERSION

def test_python_version():
    assert sys.version_info >= (3, 11), "Python 3.11+ required"

def test_version_consistency():
    assert CURRENT_VERSION.schema == "3.1-candidate"
    assert CURRENT_VERSION.builder == "1.0.0"