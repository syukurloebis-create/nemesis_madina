#!/usr/bin/env python3
"""
NEMESIS FASE 8 - Generate Documentation
"""

import sys
import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "fase8"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def generate_readme() -> str:
    """Generate README.md"""
    readme = []
    readme.append("# NEMESIS Intelligence Platform")
    readme.append("")
    readme.append("## Overview")
    readme.append("Advanced threat detection and intelligence platform.")
    readme.append("")
    readme.append("## Quick Start")
    readme.append("")
    readme.append("### Run Locally")
    readme.append("```bash")
    readme.append("cd nemesis_madina")
    readme.append("export PYTHONPATH=$PWD")
    readme.append("pip install -r requirements.txt")
    readme.append("python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000")
    readme.append("```")
    readme.append("")
    readme.append("### Run with Docker")
    readme.append("```bash")
    readme.append("docker build -t nemesis:latest -f Dockerfile.simple .")
    readme.append("docker run -p 8000:8000 nemesis:latest")
    readme.append("```")
    readme.append("")
    readme.append("## API Documentation")
    readme.append("- Swagger UI: http://localhost:8000/docs")
    readme.append("- Health: http://localhost:8000/health")
    readme.append("- Metrics: http://localhost:8000/metrics")
    readme.append("")
    readme.append("## Architecture")
    readme.append("```")
    readme.append("backend/")
    readme.append("├── api/          # REST API endpoints")
    readme.append("├── core/         # Business logic")
    readme.append("├── evidence/     # Evidence management")
    readme.append("├── intelligence/ # AI/ML capabilities")
    readme.append("├── lineage/      # Data lineage")
    readme.append("├── schema/       # Schema registry")
    readme.append("├── telemetry/    # Observability")
    readme.append("└── websocket/    # Real-time communication")
    readme.append("```")
    readme.append("")
    readme.append("## Testing")
    readme.append("```bash")
    readme.append("pytest tests/unit -v")
    readme.append("```")
    
    return "\n".join(readme)


def generate_api_doc() -> str:
    """Generate API documentation"""
    doc = []
    doc.append("# NEMESIS API Documentation")
    doc.append("")
    doc.append(f"**Version:** 2.0.0")
    doc.append(f"**Generated:** {datetime.now().isoformat()}")
    doc.append("")
    doc.append("## Base URL")
    doc.append("```")
    doc.append("http://localhost:8000")
    doc.append("```")
    doc.append("")
    doc.append("## Endpoints")
    doc.append("")
    doc.append("| Method | Endpoint | Description |")
    doc.append("|--------|----------|-------------|")
    doc.append("| GET | `/` | Root information |")
    doc.append("| GET | `/health` | Health status |")
    doc.append("| GET | `/health/live` | Liveness probe |")
    doc.append("| GET | `/health/ready` | Readiness probe |")
    doc.append("| GET | `/metrics` | Prometheus metrics |")
    doc.append("| GET | `/docs` | Swagger UI |")
    doc.append("")
    doc.append("## Response Examples")
    doc.append("")
    doc.append("### Health Check")
    doc.append("```json")
    doc.append('{"status": "healthy", "version": "2.0.0"}')
    doc.append("```")
    
    return "\n".join(doc)


def main():
    print("\n" + "="*60)
    print("FASE 8: GENERATE DOCUMENTATION")
    print("="*60)
    
    # Generate README
    readme = generate_readme()
    readme_path = PROJECT_ROOT / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)
    print(f"\n  [OK] README: {readme_path}")
    
    # Generate API documentation
    api_doc = generate_api_doc()
    api_path = REPORT_DIR / "api_documentation.md"
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(api_doc)
    print(f"  [OK] API documentation: {api_path}")
    
    print("\n" + "="*60)
    print("[OK] Documentation generated")
    print("="*60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
