#!/usr/bin/env python3
"""
Backend Structure & Condition Audit Tool

Usage:
    python scripts/audit_backend.py

This script performs a comprehensive audit of the NEMESIS backend:
- Directory structure
- Key files and their contents
- Database connection and schema
- Environment configuration
- Dependencies
- Code quality metrics
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import importlib.util
import ast

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)


@dataclass
class AuditResult:
    """Audit result for a single check."""
    name: str
    status: str  # PASS, FAIL, WARN, SKIP
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggestion: Optional[str] = None


@dataclass
class AuditReport:
    """Complete audit report."""
    timestamp: str
    project_root: str
    results: List[AuditResult] = field(default_factory=list)
    
    def add_result(self, result: AuditResult) -> None:
        self.results.append(result)
    
    def summary(self) -> Dict[str, int]:
        summary = {"PASS": 0, "FAIL": 0, "WARN": 0, "SKIP": 0}
        for r in self.results:
            summary[r.status] = summary.get(r.status, 0) + 1
        return summary
    
    def to_json(self) -> str:
        return json.dumps({
            "timestamp": self.timestamp,
            "project_root": self.project_root,
            "summary": self.summary(),
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "suggestion": r.suggestion,
                }
                for r in self.results
            ]
        }, indent=2, default=str)
    
    def print_report(self) -> None:
        """Print human-readable report."""
        print("\n" + "=" * 80)
        print(f"📊 BACKEND AUDIT REPORT")
        print(f"Timestamp: {self.timestamp}")
        print(f"Project Root: {self.project_root}")
        print("=" * 80)
        
        summary = self.summary()
        print(f"\n📈 SUMMARY:")
        print(f"  ✅ PASS: {summary.get('PASS', 0)}")
        print(f"  ❌ FAIL: {summary.get('FAIL', 0)}")
        print(f"  ⚠️  WARN: {summary.get('WARN', 0)}")
        print(f"  ⏭️  SKIP: {summary.get('SKIP', 0)}")
        
        print("\n" + "-" * 80)
        for result in self.results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARN": "⚠️",
                "SKIP": "⏭️",
            }.get(result.status, "❓")
            
            print(f"{status_icon} {result.name}")
            print(f"   {result.message}")
            
            if result.details:
                for key, value in result.details.items():
                    print(f"   ├─ {key}: {value}")
            
            if result.suggestion:
                print(f"   💡 Suggestion: {result.suggestion}")
            print()


class BackendAuditor:
    """Backend structure and condition auditor."""
    
    REQUIRED_DIRS = [
        "backend",
        "backend/core",
        "backend/domain",
        "backend/infrastructure",
        "backend/services",
        "backend/repositories",
        "backend/routers",
        "backend/collectors",
        "backend/calculators",
        "backend/mappers",
        "backend/presenters",
        "backend/factories",
        "backend/dtos",
        "backend/bootstrap",
        "backend/graph",
        "backend/graph/domain",
        "backend/graph/application",
        "backend/graph/infrastructure",
        "tests",
        "tests/unit",
        "tests/integration",
        "scripts",
    ]
    
    REQUIRED_FILES = [
        "backend/main.py",
        "backend/core/container.py",
        "backend/core/version.py",
        "backend/core/logging_config.py",
        "backend/bootstrap/container_builder.py",
        "backend/bootstrap/functions.py",
        "backend/infrastructure/unit_of_work.py",
        "backend/infrastructure/event_bus.py",
        "backend/infrastructure/parallel_executor.py",
        "backend/infrastructure/sql_repository.py",
        "backend/repositories/interfaces/__init__.py",
        "backend/graph/domain/aggregate.py",
        "backend/graph/domain/node.py",
        "backend/graph/domain/edge.py",
        "backend/graph/infrastructure/models.py",
        "backend/graph/infrastructure/mappers/to_orm.py",
        "backend/graph/infrastructure/mappers/to_domain.py",
        "backend/graph/infrastructure/repositories/postgres.py",
        "backend/graph/infrastructure/repositories/metadata.py",
        "docker-compose.yml",
        ".env.example",
        "requirements.txt",
    ]
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.report = AuditReport(
            timestamp=datetime.now().isoformat(),
            project_root=str(self.project_root)
        )
    
    def run(self) -> AuditReport:
        """Run all audit checks."""
        self._check_directories()
        self._check_files()
        self._check_imports()
        self._check_database()
        self._check_environment()
        self._check_dependencies()
        self._check_code_quality()
        return self.report
    
    def _check_directories(self) -> None:
        """Check required directories exist."""
        for dir_path in self.REQUIRED_DIRS:
            full_path = self.project_root / dir_path
            exists = full_path.exists() and full_path.is_dir()
            
            self.report.add_result(AuditResult(
                name=f"Directory: {dir_path}",
                status="PASS" if exists else "FAIL",
                message=f"{'Exists' if exists else 'Missing'}",
                details={"path": str(full_path)},
                suggestion=None if exists else f"Create directory: {dir_path}"
            ))
    
    def _check_files(self) -> None:
        """Check required files exist."""
        for file_path in self.REQUIRED_FILES:
            full_path = self.project_root / file_path
            exists = full_path.exists() and full_path.is_file()
            
            size = None
            if exists:
                size = full_path.stat().st_size
            
            self.report.add_result(AuditResult(
                name=f"File: {file_path}",
                status="PASS" if exists else "FAIL",
                message=f"{'Exists' if exists else 'Missing'}",
                details={
                    "path": str(full_path),
                    "size": size,
                } if exists else {"path": str(full_path)},
                suggestion=None if exists else f"Create file: {file_path}"
            ))
    
    def _check_imports(self) -> None:
        """Check critical imports work."""
        critical_imports = [
            "backend.core.container",
            "backend.core.version",
            "backend.bootstrap.container_builder",
            "backend.graph.domain.aggregate",
            "backend.graph.infrastructure.models",
            "backend.graph.infrastructure.repositories.postgres",
            "backend.infrastructure.unit_of_work",
        ]
        
        for import_path in critical_imports:
            try:
                spec = importlib.util.find_spec(import_path)
                if spec is not None:
                    self.report.add_result(AuditResult(
                        name=f"Import: {import_path}",
                        status="PASS",
                        message="Import successful",
                        details={"spec": str(spec) if spec else "Not found"},
                    ))
                else:
                    self.report.add_result(AuditResult(
                        name=f"Import: {import_path}",
                        status="FAIL",
                        message="Import failed - module not found",
                        suggestion=f"Check module path: {import_path}"
                    ))
            except Exception as e:
                self.report.add_result(AuditResult(
                    name=f"Import: {import_path}",
                    status="FAIL",
                    message=f"Import failed: {str(e)}",
                    details={"error": str(e)},
                    suggestion=f"Fix import: {import_path}"
                ))
    
    def _check_database(self) -> None:
        """Check database connection and schema."""
        try:
            import asyncpg
            from backend.core.settings import Settings
            
            settings = Settings()
            db_url = settings.DATABASE_URL
            
            self.report.add_result(AuditResult(
                name="Database Connection",
                status="PASS",
                message="Database URL configured",
                details={"url": db_url.replace("://", "://***@") if "://" in db_url else "configured"},
            ))
            
            # Try to connect
            try:
                import asyncio
                
                async def check_db():
                    conn = await asyncpg.connect(db_url)
                    version = await conn.fetchval("SELECT version()")
                    await conn.close()
                    return version
                
                version = asyncio.run(check_db())
                self.report.add_result(AuditResult(
                    name="Database Connectivity",
                    status="PASS",
                    message="Connected to database",
                    details={"version": version[:50] + "..." if len(version) > 50 else version},
                ))
                
                # Check tables
                async def check_tables():
                    conn = await asyncpg.connect(db_url)
                    tables = await conn.fetch(
                        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                    )
                    await conn.close()
                    return [t[0] for t in tables]
                
                tables = asyncio.run(check_tables())
                
                critical_tables = [
                    "cases", "graph_entities", "graph_relationships",
                    "risk_scores", "graph_metadata"
                ]
                
                for table in critical_tables:
                    exists = table in tables
                    self.report.add_result(AuditResult(
                        name=f"Table: {table}",
                        status="PASS" if exists else "WARN",
                        message=f"{'Exists' if exists else 'Missing'}",
                        suggestion=None if exists else f"Create table: {table}"
                    ))
                
            except Exception as e:
                self.report.add_result(AuditResult(
                    name="Database Connectivity",
                    status="WARN",
                    message=f"Cannot connect: {str(e)[:100]}",
                    details={"error": str(e)[:200]},
                    suggestion="Check database is running and credentials are correct"
                ))
                
        except ImportError as e:
            self.report.add_result(AuditResult(
                name="Database Connection",
                status="SKIP",
                message=f"asyncpg not installed: {str(e)}",
                suggestion="Install asyncpg: pip install asyncpg"
            ))
        except Exception as e:
            self.report.add_result(AuditResult(
                name="Database Connection",
                status="FAIL",
                message=f"Check failed: {str(e)[:100]}",
                suggestion="Check database configuration"
            ))
    
    def _check_environment(self) -> None:
        """Check environment configuration."""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        # Check .env exists
        if env_file.exists():
            self.report.add_result(AuditResult(
                name="Environment: .env",
                status="PASS",
                message=".env file exists",
                details={"path": str(env_file)},
            ))
            
            # Check critical env vars
            critical_vars = [
                "DATABASE_URL",
                "SECRET_KEY",
                "ENABLE_HEALTH",
                "VERSION",
            ]
            
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    env_vars = {}
                    for line in content.split('\n'):
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, val = line.split('=', 1)
                                env_vars[key.strip()] = val.strip()
                    
                    for var in critical_vars:
                        exists = var in env_vars
                        self.report.add_result(AuditResult(
                            name=f"ENV: {var}",
                            status="PASS" if exists else "WARN",
                            message=f"{'Set' if exists else 'Not set'}",
                            suggestion=None if exists else f"Add {var} to .env"
                        ))
            except Exception as e:
                self.report.add_result(AuditResult(
                    name="Environment: .env parsing",
                    status="WARN",
                    message=f"Could not parse: {str(e)[:100]}",
                ))
        else:
            self.report.add_result(AuditResult(
                name="Environment: .env",
                status="WARN",
                message=".env file missing",
                suggestion="Copy .env.example to .env and configure"
            ))
        
        # Check .env.example
        if env_example.exists():
            self.report.add_result(AuditResult(
                name="Environment: .env.example",
                status="PASS",
                message=".env.example exists",
            ))
        else:
            self.report.add_result(AuditResult(
                name="Environment: .env.example",
                status="WARN",
                message=".env.example missing",
                suggestion="Create .env.example with required variables"
            ))
    
    def _check_dependencies(self) -> None:
        """Check Python dependencies."""
        req_file = self.project_root / "requirements.txt"
        
        if req_file.exists():
            self.report.add_result(AuditResult(
                name="Dependencies: requirements.txt",
                status="PASS",
                message="requirements.txt exists",
            ))
            
            # Read requirements
            try:
                with open(req_file, 'r') as f:
                    reqs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                self.report.add_result(AuditResult(
                    name="Dependencies: Count",
                    status="PASS",
                    message=f"{len(reqs)} dependencies listed",
                    details={"count": len(reqs)},
                ))
                
                # Check critical packages
                critical_packages = [
                    "fastapi",
                    "uvicorn",
                    "sqlalchemy",
                    "asyncpg",
                    "pydantic",
                    "alembic",
                    "prometheus-client",
                    "python-dotenv",
                ]
                
                for pkg in critical_packages:
                    installed = False
                    try:
                        spec = importlib.util.find_spec(pkg)
                        if spec is not None:
                            installed = True
                    except Exception:
                        pass
                    
                    self.report.add_result(AuditResult(
                        name=f"Package: {pkg}",
                        status="PASS" if installed else "WARN",
                        message=f"{'Installed' if installed else 'Not installed'}",
                        suggestion=None if installed else f"Install: pip install {pkg}"
                    ))
                    
            except Exception as e:
                self.report.add_result(AuditResult(
                    name="Dependencies: Parse",
                    status="WARN",
                    message=f"Could not parse: {str(e)[:100]}",
                ))
        else:
            self.report.add_result(AuditResult(
                name="Dependencies: requirements.txt",
                status="WARN",
                message="requirements.txt missing",
                suggestion="Create requirements.txt with dependencies"
            ))
    
    def _check_code_quality(self) -> None:
        """Check code quality basics."""
        # Check for Python files
        py_files = list(self.project_root.rglob("*.py"))
        py_files_count = len(py_files)
        
        self.report.add_result(AuditResult(
            name="Code: Python files",
            status="PASS",
            message=f"{py_files_count} Python files found",
            details={"count": py_files_count},
        ))
        
        # Check for __init__.py files
        init_files = list(self.project_root.rglob("__init__.py"))
        init_count = len(init_files)
        
        self.report.add_result(AuditResult(
            name="Code: __init__.py files",
            status="PASS" if init_count > 0 else "WARN",
            message=f"{init_count} __init__.py files found",
            details={"count": init_count},
            suggestion="Add __init__.py to make packages importable" if init_count == 0 else None
        ))
        
        # Check for type hints (basic)
        type_hinted = 0
        for py_file in py_files[:100]:  # Check first 100 files
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if node.returns is not None:
                                type_hinted += 1
                                break
            except Exception:
                pass
        
        self.report.add_result(AuditResult(
            name="Code: Type hints",
            status="PASS" if type_hinted > 0 else "WARN",
            message=f"Type hints found in {type_hinted} files",
            details={"files_with_type_hints": type_hinted},
            suggestion="Add type hints to functions" if type_hinted == 0 else None
        ))
        
        # Check for docstrings
        docstring_count = 0
        for py_file in py_files[:100]:  # Check first 100 files
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            if ast.get_docstring(node):
                                docstring_count += 1
                                break
            except Exception:
                pass
        
        self.report.add_result(AuditResult(
            name="Code: Docstrings",
            status="PASS" if docstring_count > 0 else "WARN",
            message=f"Docstrings found in {docstring_count} files",
            details={"files_with_docstrings": docstring_count},
            suggestion="Add docstrings to functions and classes" if docstring_count == 0 else None
        ))


def main():
    """Run the audit."""
    print("🔍 NEMESIS Backend Audit Tool")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    
    # Run audit
    auditor = BackendAuditor()
    report = auditor.run()
    
    # Print report
    report.print_report()
    
    # Save JSON report
    report_path = auditor.project_root / "audit_report.json"
    with open(report_path, 'w') as f:
        f.write(report.to_json())
    print(f"\n📄 Full report saved to: {report_path}")
    
    # Return exit code
    summary = report.summary()
    if summary.get('FAIL', 0) > 0:
        print("\n❌ Audit found failures. Please fix the issues above.")
        return 1
    else:
        print("\n✅ Audit completed successfully.")
        return 0


if __name__ == "__main__":
    sys.exit(main())