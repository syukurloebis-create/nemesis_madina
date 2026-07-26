# scripts/scanner/plugins/python_plugin.py

"""
Legacy compatibility shim - redirects to new location.
This file will be removed after all imports are migrated.

Target Removal: Phase 1
"""

import warnings
from scripts.scanner.core.plugins.python_plugin import PythonPlugin

warnings.warn(
    "scripts.scanner.plugins is deprecated. Use scripts.scanner.core.plugins instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["PythonPlugin"]