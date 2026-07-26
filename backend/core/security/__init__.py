# backend/core/security/__init__.py

"""
Legacy compatibility shim - redirects to new location.
This file will be removed after all imports are migrated.

Target Removal: Phase 1
Owner: Security Team
"""

import warnings
from typing import Any

warnings.warn(
    "backend.core.security is deprecated. Use backend.security.auth_core instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Lazy imports
_LAZY_IMPORTS = {
    "verify_hash_chain": ("backend.security.auth_core", "verify_hash_chain"),
    "HashVerifier": ("backend.security.auth_core", "HashVerifier"),
}


def __getattr__(name: str) -> Any:
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module {__name__} has no attribute {name}")
    
    module_path, attr_name = _LAZY_IMPORTS[name]
    try:
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    except (ImportError, AttributeError) as e:
        raise RuntimeError(
            f"Failed to resolve '{name}' from '{module_path}'. "
            f"Please migrate to new location."
        ) from e


__all__ = [
    "verify_hash_chain",
    "HashVerifier",
]