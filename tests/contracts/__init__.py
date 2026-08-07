# tests/contracts/__init__.py
"""
Contract Tests - Verify all components satisfy their contracts.
"""

# Only import files that actually exist
from .test_artifact_contract import TestArtifactContract

# These files are missing - commented out until they are created
# from .test_rule_contract import TestRuleContract
# from .test_result_contract import TestResultContract
# from .test_finding_contract import TestFindingContract

__all__ = [
    'TestArtifactContract',
    # 'TestRuleContract',
    # 'TestResultContract',
    # 'TestFindingContract',
]