"""
Deterministic Jitter - Reproducible retry delays.
Phase 1 - Core Infrastructure
"""

import hashlib


class DeterministicJitter:
    """Deterministic jitter based on execution context."""
    
    @staticmethod
    def compute(attempt: int, execution_id: str, max_jitter: float = 0.1) -> float:
        seed_string = f"{execution_id}_{attempt}"
        seed_hash = hashlib.sha256(seed_string.encode()).hexdigest()
        seed_int = int(seed_hash[:8], 16)
        return (seed_int % 10000) / 10000 * max_jitter