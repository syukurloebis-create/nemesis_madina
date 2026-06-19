#!/usr/bin/env python3
"""
NEMESIS FASE 7 - Create GitHub Actions Workflows
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def create_ci_workflow():
    """Create CI workflow for GitHub Actions"""
    print("\n[1/3] Creating CI workflow...")
    
    # Create .github/workflows directory
    workflows_dir = PROJECT_ROOT / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    content = '''# NEMESIS CI/CD Pipeline
name: NEMESIS CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:

env:
  PYTHON_VERSION: '3.12'

jobs:
  # Test Job
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run Import Guard
      run: python scripts/fase0/05_import_guard.py || true
    
    - name: Run unit tests
      run: |
        python -m pytest tests/unit -v --cov=backend --cov-report=xml --cov-fail-under=0
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Run security scan
      run: |
        pip install bandit
        bandit -r backend -f json -o bandit_report.json || true
    
    - name: Upload security report
      uses: actions/upload-artifact@v3
      with:
        name: security-report
        path: bandit_report.json

  # Lint Job
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install linters
      run: |
        pip install ruff black mypy
    
    - name: Run Ruff linter
      run: ruff check backend/ || true
    
    - name: Run Black formatter check
      run: black --check backend/ || true
    
    - name: Run MyPy type check
      run: mypy backend/ --ignore-missing-imports || true

  # Build Job
  build:
    runs-on: ubuntu-latest
    needs: [test, lint]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/nemesis:latest
          ${{ secrets.DOCKER_USERNAME }}/nemesis:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  # Deploy Job
  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Kubernetes
      uses: azure/k8s-deploy@v4
      with:
        namespace: nemesis
        manifests: |
          k8s/deployment.yaml
          k8s/service.yaml
          k8s/ingress.yaml
        images: ${{ secrets.DOCKER_USERNAME }}/nemesis:${{ github.sha }}
    
    - name: Verify deployment
      run: |
        kubectl rollout status deployment/nemesis-api -n nemesis --timeout=5m
        kubectl rollout status deployment/nemesis-websocket -n nemesis --timeout=5m
        kubectl rollout status deployment/nemesis-worker -n nemesis --timeout=5m
    
    - name: Run smoke tests
      run: |
        curl -f https://api.nemesis.com/health || exit 1
        curl -f https://api.nemesis.com/metrics || exit 1

  # Notify
  notify:
    runs-on: ubuntu-latest
    needs: [deploy]
    if: always()
    
    steps:
    - name: Notify Slack
      uses: slackapi/slack-github-action@v1.24
      with:
        payload: |
          {
            "text": "NEMESIS Deployment: ${{ job.status }}\nCommit: ${{ github.sha }}\nBranch: ${{ github.ref }}"
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
'''
    
    file_path = workflows_dir / "ci.yml"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_deploy_workflow():
    """Create deploy workflow for production"""
    print("\n[2/3] Creating deploy workflow...")
    
    workflows_dir = PROJECT_ROOT / ".github" / "workflows"
    
    content = '''# NEMESIS Deployment Workflow
name: NEMESIS Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      version:
        description: 'Version to deploy'
        required: false
        default: 'latest'

jobs:
  deploy-staging:
    if: github.event.inputs.environment == 'staging'
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBE_CONFIG_STAGING }}" | base64 --decode > $HOME/.kube/config
    
    - name: Deploy to staging
      run: |
        kubectl set image deployment/nemesis-api api=${{ secrets.DOCKER_USERNAME }}/nemesis:${{ github.event.inputs.version || github.sha }} -n staging
        kubectl rollout status deployment/nemesis-api -n staging
  
  deploy-production:
    if: github.event.inputs.environment == 'production'
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      run: |
        mkdir -p $HOME/.kube
        echo "${{ secrets.KUBE_CONFIG_PROD }}" | base64 --decode > $HOME/.kube/config
    
    - name: Backup current deployment
      run: |
        kubectl get deployment nemesis-api -n production -o yaml > backup_api.yaml
        kubectl get deployment nemesis-websocket -n production -o yaml > backup_ws.yaml
    
    - name: Deploy to production (blue/green)
      run: |
        # Deploy green version
        kubectl apply -f k8s/deployment-green.yaml -n production
        kubectl rollout status deployment/nemesis-api-green -n production --timeout=5m
        
        # Switch traffic
        kubectl patch service nemesis-api -n production -p '{"spec":{"selector":{"version":"green"}}}'
        
        # Verify
        sleep 10
        curl -f https://api.nemesis.com/health || (kubectl rollout undo deployment/nemesis-api-green -n production && exit 1)
        
        # Remove blue
        kubectl delete deployment nemesis-api-blue -n production || true
    
    - name: Notify deployment status
      run: |
        echo "Deployment to production completed successfully"
'''
    
    file_path = workflows_dir / "deploy.yml"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_dependabot_config():
    """Create Dependabot configuration"""
    print("\n[3/3] Creating Dependabot config...")
    
    content = '''# Dependabot Configuration
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "python"
  
  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
  
  # Docker
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"
'''
    
    file_path = PROJECT_ROOT / ".github" / "dependabot.yml"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 7: CREATE GITHUB ACTIONS")
    print("="*60)
    
    create_ci_workflow()
    create_deploy_workflow()
    create_dependabot_config()
    
    print("\n" + "="*60)
    print("[OK] GitHub Actions created")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())