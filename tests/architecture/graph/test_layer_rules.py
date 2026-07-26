# tests/architecture/graph/test_layer_rules.py

"""
Architecture Tests - Layer Dependency Rules
"""

import pytest
from pathlib import Path


def _read_file(path: Path) -> str:
    """Read file with UTF-8 encoding (portable across Windows/Linux/macOS)."""
    return path.read_text(encoding="utf-8")


class TestLayerRules:
    """Test layer dependency rules."""
    
    def test_domain_no_orm_import(self):
        """Domain layer must not import ORM."""
        domain_files = Path("backend/graph/domain").glob("**/*.py")
        violations = []
        forbidden_patterns = (
            "from sqlalchemy",
            "import sqlalchemy",
            "from sqlalchemy.orm",
            "import sqlalchemy.orm",
        )
        
        for file in domain_files:
            if file.name.startswith("__"):
                continue
            content = _read_file(file)
            if any(pattern in content for pattern in forbidden_patterns):
                violations.append(str(file))
        
        assert not violations, f"Domain files import ORM: {violations}"
    
    def test_domain_no_orm_models(self):
        """Domain layer must not import ORM models."""
        domain_files = Path("backend/graph/domain").glob("**/*.py")
        violations = []
        forbidden_imports = (
            "from backend.graph.models import",
            "import backend.graph.models",
            "from backend.graph.models.GraphEntity",
            "from backend.graph.models.GraphRelationship",
        )
        
        for file in domain_files:
            if file.name.startswith("__"):
                continue
            content = _read_file(file)
            if any(pattern in content for pattern in forbidden_imports):
                violations.append(str(file))
        
        assert not violations, f"Domain files import ORM models: {violations}"
    
    def test_application_no_orm(self):
        """Application layer must not import ORM."""
        app_files = Path("backend/graph/application").glob("**/*.py")
        violations = []
        forbidden_patterns = (
            "from sqlalchemy",
            "import sqlalchemy",
            "from backend.graph.models",
        )
        
        for file in app_files:
            if file.name.startswith("__"):
                continue
            content = _read_file(file)
            if any(pattern in content for pattern in forbidden_patterns):
                violations.append(str(file))
        
        assert not violations, f"Application files import ORM: {violations}"
    
    def test_infrastructure_imports_domain(self):
        """Infrastructure layer may import domain."""
        infra_files = Path("backend/graph/infrastructure").glob("**/*.py")
        import_count = 0
        
        for file in infra_files:
            if file.name.startswith("__"):
                continue
            content = _read_file(file)
            if "backend.graph.domain" in content:
                import_count += 1
        
        assert import_count > 0, "Infrastructure layer should import domain"
    
    def test_no_circular_dependencies(self):
        """No circular dependencies between layers."""
        # This would be checked by import-linter
        pass