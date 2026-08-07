# tests/test_cp2/conftest.py

import pytest
from ir.config import IRConfig
from ir.context import IRContext
from ir.models import Module


def make_test_context(module_id: int = 1, name: str = "test") -> IRContext:
    """Create a test context with a module pre-configured.
    
    NOTE:
    Do not create scopes or traversal state here.
    Visitor tests verify that IRVisitor creates the initial module scope
    and root block itself.
    
    Only Module and current_module_id are set.
    """
    context = IRContext(config=IRConfig())
    module = Module(
        module_id=module_id,
        name=name,
        file="test.py",
        file_hash="hash",
    )
    context.modules.insert(module)
    context.current_module_id = module.module_id
    return context


@pytest.fixture
def test_context() -> IRContext:
    """Pytest fixture for test context."""
    return make_test_context()