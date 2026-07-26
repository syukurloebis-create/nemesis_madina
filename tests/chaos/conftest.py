"""
Chaos Test Configuration
Environment-based skip using collection hook.
"""

import os
import pytest


def pytest_collection_modifyitems(config, items):
    """Skip chaos tests if environment not enabled."""
    if os.getenv("ENABLE_CHAOS_TESTS") == "true":
        return

    skip = pytest.mark.skip(
        reason=(
            "Chaos environment not enabled "
            "(set ENABLE_CHAOS_TESTS=true to run)"
        )
    )

    for item in items:
        if item.get_closest_marker("requires_chaos_environment"):
            item.add_marker(skip)