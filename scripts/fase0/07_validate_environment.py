#!/usr/bin/env python3
"""
NEMESIS Environment Validator - Phase 0
Memvalidasi environment development
"""

import sys
import subprocess
import importlib
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

PROJECT_ROOT = Path(".").resolve()
REQUIRED_PACKAGES = [
    'fastapi', 'uvicorn', 'sqlalchemy', 'alembic', 'pydantic',
    'pytest', 'pytest-asyncio', 'pytest-cov', 'httpx', 'aiohttp',
    'websockets', 'prometheus-client', 'python-dotenv', 'psycopg2-binary',
    'asyncpg', 'redis', 'numpy', 'pandas', 'scikit-learn', 'joblib'
]

class EnvironmentValidator:
    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        
    def check_python_version(self):
        """Check Python version"""
        version = sys.version_info
        is_ok = version.major >= 3 and version.minor >= 10
        self.results.append((
            "Python Version",
            is_ok,
            f"{version.major}.{version.minor}.{version.micro}"
        ))
        
    def check_pip_packages(self):
        """Check required pip packages"""
        installed = {}
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True, check=True
            )
            packages = json.loads(result.stdout)
            installed = {pkg['name'].lower(): pkg['version'] for pkg in packages}
        except:
            pass
            
        for package in REQUIRED_PACKAGES:
            is_installed = package in installed
            version = installed.get(package, 'Not installed')
            self.results.append((
                f"Package: {package}",
                is_installed,
                version
            ))
            
    def check_environment_variables(self):
        """Check required environment variables"""
        from dotenv import load_dotenv
        import os
        
        env_file = PROJECT_ROOT / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            
        required_vars = ['DATABASE_URL', 'REDIS_URL', 'SECRET_KEY']
        
        for var in required_vars:
            value = os.getenv(var)
            is_set = bool(value)
            self.results.append((
                f"ENV: {var}",
                is_set,
                "Set" if is_set else "Missing"
            ))
            
    def check_database_connection(self):
        """Check database connectivity"""
        try:
            import psycopg2
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'nemesis_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                connect_timeout=5
            )
            conn.close()
            self.results.append(("Database Connection", True, "Connected"))
        except Exception as e:
            self.results.append(("Database Connection", False, str(e)))
            
    def check_redis_connection(self):
        """Check Redis connectivity"""
        try:
            import redis
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True,
                socket_connect_timeout=5
            )
            r.ping()
            self.results.append(("Redis Connection", True, "Connected"))
        except Exception as e:
            self.results.append(("Redis Connection", False, str(e)))
            
    def check_disk_space(self):
        """Check available disk space"""
        try:
            import psutil
            disk = psutil.disk_usage(str(PROJECT_ROOT))
            free_gb = disk.free / (1024**3)
            is_ok = free_gb > 5
            self.results.append((
                "Disk Space",
                is_ok,
                f"{free_gb:.2f} GB free"
            ))
        except:
            self.results.append(("Disk Space", True, "Unable to check"))
            
    def check_git_status(self):
        """Check git repository status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd=PROJECT_ROOT
            )
            has_uncommitted = bool(result.stdout.strip())
            self.results.append((
                "Git Status",
                not has_uncommitted,
                "Clean" if not has_uncommitted else "Uncommitted changes"
            ))
        except:
            self.results.append(("Git Status", True, "Not a git repo"))
            
    def run_all(self):
        """Run all checks"""
        print("\n" + "="*60)
        print("ENVIRONMENT VALIDATION")
        print("="*60 + "\n")
        
        self.check_python_version()
        self.check_pip_packages()
        self.check_environment_variables()
        self.check_database_connection()
        self.check_redis_connection()
        self.check_disk_space()
        self.check_git_status()
        
    def print_results(self):
        """Print validation results"""
        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for name, status, detail in self.results:
            icon = "✅" if status else "❌"
            print(f"{icon} {name}: {detail}")
            if status:
                passed += 1
            else:
                failed += 1
                
        print("\n" + "="*60)
        print(f"SUMMARY: {passed} passed, {failed} failed")
        print("="*60)
        
        return failed == 0
        
    def save_report(self):
        """Save report to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'checks': [
                {'name': name, 'passed': passed, 'detail': detail}
                for name, passed, detail in self.results
            ],
            'summary': {
                'total': len(self.results),
                'passed': sum(1 for _, p, _ in self.results if p),
                'failed': sum(1 for _, p, _ in self.results if not p)
            }
        }
        
        report_dir = PROJECT_ROOT / "reports" / "fase0"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / "environment_validation.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Report saved to: {report_file}")

def main():
    validator = EnvironmentValidator()
    validator.run_all()
    validator.print_results()
    validator.save_report()
    
    return 0 if validator.print_results() else 1

if __name__ == "__main__":
    sys.exit(main())