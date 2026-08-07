# tests/e2e/test_e2e_sample_project.py
"""
End-to-end sample project tests.
"""

import pytest

pytestmark = pytest.mark.e2e


class TestE2ESampleProject:
    """E2E tests for sample project."""
    
    def test_sample_project_loads(self):
        """Test that sample project loads."""
        from metadata_inventory.phase2_runner import Phase2Runner
        runner = Phase2Runner()
        assert runner is not None