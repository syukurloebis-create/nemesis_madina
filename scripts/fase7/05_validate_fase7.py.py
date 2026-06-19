#!/usr/bin/env python3
"""
NEMESIS FASE 7 - Validation Script
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def validate():
    print("\n" + "="*60)
    print("FASE 7: VALIDATION")
    print("="*60)
    
    errors = []
    
    # 1. Check Docker files
    print("\n[1/5] Checking Docker configuration...")
    
    docker_files = [
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        "prometheus.yml",
        ".env.production"
    ]
    
    for file_name in docker_files:
        file_path = PROJECT_ROOT / file_name
        if file_path.exists():
            print(f"  [OK] {file_name}")
        else:
            errors.append(f"Missing: {file_name}")
    
    # 2. Check GitHub Actions
    print("\n[2/5] Checking GitHub Actions...")
    
    github_files = [
        ".github/workflows/ci.yml",
        ".github/workflows/deploy.yml",
        ".github/dependabot.yml"
    ]
    
    for file_name in github_files:
        file_path = PROJECT_ROOT / file_name
        if file_path.exists():
            print(f"  [OK] {file_name}")
        else:
            errors.append(f"Missing: {file_name}")
    
    # 3. Check Kubernetes manifests
    print("\n[3/5] Checking Kubernetes manifests...")
    
    k8s_files = [
        "k8s/deployment.yaml",
        "k8s/service.yaml",
        "k8s/configmap.yaml",
        "k8s/secret.yaml",
        "k8s/ingress.yaml"
    ]
    
    for file_name in k8s_files:
        file_path = PROJECT_ROOT / file_name
        if file_path.exists():
            print(f"  [OK] {file_name}")
        else:
            errors.append(f"Missing: {file_name}")
    
    # 4. Check deployment scripts
    print("\n[4/5] Checking deployment scripts...")
    
    script_files = [
        "scripts/build.sh",
        "scripts/deploy.sh",
        "scripts/healthcheck.sh",
        "scripts/rollback.sh",
        "scripts/worker.py"
    ]
    
    for file_name in script_files:
        file_path = PROJECT_ROOT / file_name
        if file_path.exists():
            print(f"  [OK] {file_name}")
        else:
            errors.append(f"Missing: {file_name}")
    
    # 5. Validate Dockerfile syntax
    print("\n[5/5] Validating Dockerfile...")
    
    dockerfile_path = PROJECT_ROOT / "Dockerfile"
    if dockerfile_path.exists():
        content = dockerfile_path.read_text()
        if "FROM python" in content and "CMD" in content:
            print("  [OK] Dockerfile syntax valid")
        else:
            errors.append("Dockerfile invalid syntax")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"[ERR] Validation failed: {len(errors)} errors")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("[OK] All validations passed!")
        print("="*60)
        return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)