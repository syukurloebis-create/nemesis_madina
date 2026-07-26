"""
Legacy compatibility shim - redirects to new location.
This file will be removed after all imports are migrated.

Target Removal: Phase 1
Owner: Security Team
"""

import warnings
from backend.security.auth_core import verify_hash_chain

warnings.warn(
    "backend.core.security.hash_verifier is deprecated. Use backend.security.auth_core instead.",
    DeprecationWarning,
    stacklevel=2,
)

verify_chain = verify_hash_chain

__all__ = [
    "verify_hash_chain",
    "verify_chain",
]