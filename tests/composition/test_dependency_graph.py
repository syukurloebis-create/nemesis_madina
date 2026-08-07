# tests/composition/test_dependency_graph.py
"""
Dependency Graph Tests
======================

Ensures no manual instantiation of event components outside the composition root.

ADR Reference: ADR-035
"""

import ast
import inspect
import pytest
from pathlib import Path
from typing import List, Set

import backend.bootstrap.events
import backend.core.events


class TestDependencyGraph:
    """Tests for dependency graph rules."""

    # Types that MUST be instantiated in composition root
    FORBIDDEN_TYPES = {
        "DefaultRouter",
        "DefaultRetryPolicy",
        "ExponentialBackoffRetryPolicy",
        "InMemoryDeadLetterStore",
        "FileBasedDeadLetterStore",
        "InfrastructureEventBusAdapter",
        "EventBusFacade",
        "LegacyEventBusWrapper",
    }

    # Types that are ALLOWED anywhere (value objects, DTOs, entities)
    ALLOWED_TYPES = {
        "RoutingDecision",
        "Job",
        "RoutingDestination",
        "DeadLetterEntry",
        "FailureClassification",
        "RetryDecision",
        "DomainEvent",
        "BaseEvent",
        "Event",
    }

    # Null Objects are ALLOWED
    NULL_OBJECT_TYPES = {
        "NullEventRouter",
        "NullEventRetryPolicy",
        "NullDeadLetterStore",
    }

    # Composition roots (files where forbidden instantiations ARE allowed)
    # Use Path for cross-platform compatibility
    COMPOSITION_ROOTS = {
        Path("bootstrap") / "events.py",
    }

    def _is_composition_root(self, filepath: Path, backend_dir: Path) -> bool:
        """Check if a file is a composition root."""
        try:
            relative = filepath.relative_to(backend_dir)
            # Normalize to forward slashes for comparison
            relative_str = str(relative).replace("\\", "/")
            for root in self.COMPOSITION_ROOTS:
                root_str = str(root).replace("\\", "/")
                if relative_str == root_str or relative_str.endswith(root_str):
                    return True
        except ValueError:
            pass
        return False

    def _is_test_file(self, filepath: Path) -> bool:
        """Check if a file is a test file."""
        return "tests" in filepath.parts or "test_" in filepath.name

    def _is_interface_file(self, filepath: Path) -> bool:
        """Check if a file is an interface definition file."""
        return "interfaces" in filepath.parts

    def _is_null_objects_file(self, filepath: Path) -> bool:
        """Check if a file is the null objects file."""
        return filepath.name == "null_objects.py"

    def _is_forbidden_instantiation(self, node: ast.Call, class_names: Set[str]) -> bool:
        """Check if a call is a forbidden instantiation."""
        if not isinstance(node.func, ast.Name):
            return False
        
        class_name = node.func.id
        
        # Allow value objects and DTOs
        if class_name in self.ALLOWED_TYPES:
            return False
        
        # Allow Null Objects (Null Object Pattern)
        if class_name in self.NULL_OBJECT_TYPES:
            return False
        
        # Check if it's a forbidden type
        if class_name in self.FORBIDDEN_TYPES:
            return True
        
        return False

    def _check_file_for_instantiation(self, filepath: Path, backend_dir: Path) -> List[str]:
        """Check a file for manual instantiation of forbidden event classes."""
        violations = []

        # Skip composition roots
        if self._is_composition_root(filepath, backend_dir):
            return violations

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if self._is_forbidden_instantiation(node, self.FORBIDDEN_TYPES):
                        violations.append(
                            f"{filepath}:{node.lineno}: "
                            f"Manual instantiation of {node.func.id}() "
                            f"(should only be in composition root)"
                        )
        except Exception:
            # Skip files that can't be parsed
            pass

        return violations

    def test_no_manual_instantiation_outside_bootstrap(self):
        """
        Ensure no manual instantiation of event components outside bootstrap.

        Rules:
        - Infrastructure components should only be instantiated in composition roots
        - Value objects and DTOs are exempt
        - Null Objects are exempt (Null Object Pattern)
        - Test files are exempt
        """
        backend_dir = Path(__file__).parent.parent.parent / "backend"

        violations = []

        for py_file in backend_dir.rglob("*.py"):
            # Skip test files
            if self._is_test_file(py_file):
                continue

            # Skip __init__.py files
            if py_file.name == "__init__.py":
                continue

            # Skip interface files
            if self._is_interface_file(py_file):
                continue

            # Skip null_objects.py
            if self._is_null_objects_file(py_file):
                continue

            violations.extend(self._check_file_for_instantiation(py_file, backend_dir))

        # Build detailed error message
        if violations:
            error_msg = f"Found {len(violations)} violations:\n"
            for v in violations:
                error_msg += f"  {v}\n"
            error_msg += "\nAllowed types (value objects, DTOs, Null Objects):\n"
            error_msg += f"  {', '.join(sorted(self.ALLOWED_TYPES))}\n"
            error_msg += f"  {', '.join(sorted(self.NULL_OBJECT_TYPES))}\n"
            error_msg += "\nForbidden types (must be in composition root):\n"
            error_msg += f"  {', '.join(sorted(self.FORBIDDEN_TYPES))}"
            pytest.fail(error_msg)

        assert len(violations) == 0

    def test_facade_does_not_instantiate_dependencies(self):
        """
        Ensure EventBusFacade does not instantiate its own dependencies.
        
        Null Objects are allowed as they are part of the Null Object Pattern.
        """
        facade_file = Path(__file__).parent.parent.parent / "backend" / "core" / "events" / "facade.py"

        if not facade_file.exists():
            pytest.skip("facade.py not found")

        with open(facade_file, "r", encoding="utf-8") as f:
            content = f.read()

        # These patterns should NOT be in facade.py
        forbidden_patterns = [
            "DefaultRetryPolicy(",
            "DefaultRouter(",
            "InMemoryDeadLetterStore(",
            "FileBasedDeadLetterStore(",
            "InfrastructureEventBusAdapter(",
        ]

        violations = []
        for pattern in forbidden_patterns:
            if pattern in content:
                violations.append(f"Found '{pattern}' in facade.py")

        assert len(violations) == 0, f"Violations found:\n" + "\n".join(violations)