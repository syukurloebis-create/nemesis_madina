[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "orm-verification-platform"
version = "1.0.0"
description = "ORM Verification Platform L4 Adaptive Verification Platform"
authors = [{name = "NEMESIS Team"}]
requires-python = ">=3.11"
dependencies = [
    "sqlalchemy>=2.0.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[project.scripts]
verification-runner = "scripts.metadata_inventory.verification_runner:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --cov=scripts.metadata_inventory --cov-report=term --cov-report=html"

[tool.coverage.run]
source = ["scripts/metadata_inventory"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]