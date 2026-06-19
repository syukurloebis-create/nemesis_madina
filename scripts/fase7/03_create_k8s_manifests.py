#!/usr/bin/env python3
"""
NEMESIS FASE 7 - Create Kubernetes Manifests
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def create_k8s_directory():
    """Create k8s directory"""
    print("\n[1/6] Creating k8s directory...")
    k8s_dir = PROJECT_ROOT / "k8s"
    k8s_dir.mkdir(parents=True, exist_ok=True)
    return True

def create_deployment():
    """Create deployment.yaml"""
    print("\n[2/6] Creating deployment.yaml...")
    
    content = '''# NEMESIS Kubernetes Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nemesis-api
  namespace: nemesis
  labels:
    app: nemesis
    component: api
    version: v2
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: nemesis
      component: api
  template:
    metadata:
      labels:
        app: nemesis
        component: api
        version: v2
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: api
        image: nemesis/api:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: nemesis-secrets
              key: database_url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: nemesis-secrets
              key: redis_url
        - name: NATS_URL
          valueFrom:
            secretKeyRef:
              name: nemesis-secrets
              key: nats_url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: nemesis-secrets
              key: secret_key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nemesis-websocket
  namespace: nemesis
  labels:
    app: nemesis
    component: websocket
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nemesis
      component: websocket
  template:
    metadata:
      labels:
        app: nemesis
        component: websocket
    spec:
      containers:
      - name: websocket
        image: nemesis/websocket:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8001
          name: ws
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: nemesis-secrets
              key: redis_url
        - name: NATS_URL
          valueFrom:
            secretKeyRef:
              name: nemesis-secrets
              key: nats_url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          tcpSocket:
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nemesis-worker
  namespace: nemesis
  labels:
    app: nemesis
    component: worker
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nemesis
      component: worker
  template:
    metadata:
      labels:
        app: nemesis
        component: worker
    spec:
      containers:
      - name: worker
        image: nemesis/worker:latest
        imagePullPolicy: Always
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: nemesis-secrets
              key: database_url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: nemesis-secrets
              key: redis_url
        - name: NATS_URL
          valueFrom:
            secretKeyRef:
              name: nemesis-secrets
              key: nats_url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
'''
    
    file_path = PROJECT_ROOT / "k8s" / "deployment.yaml"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_service():
    """Create service.yaml"""
    print("\n[3/6] Creating service.yaml...")
    
    content = '''# NEMESIS Kubernetes Services
apiVersion: v1
kind: Service
metadata:
  name: nemesis-api
  namespace: nemesis
  labels:
    app: nemesis
    component: api
spec:
  selector:
    app: nemesis
    component: api
  ports:
  - port: 80
    targetPort: 8000
    name: http
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: nemesis-websocket
  namespace: nemesis
  labels:
    app: nemesis
    component: websocket
spec:
  selector:
    app: nemesis
    component: websocket
  ports:
  - port: 80
    targetPort: 8001
    name: ws
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: nemesis-api-external
  namespace: nemesis
  labels:
    app: nemesis
    component: api
spec:
  selector:
    app: nemesis
    component: api
  ports:
  - port: 80
    targetPort: 8000
    name: http
  type: LoadBalancer
---
apiVersion: v1
kind: Service
metadata:
  name: nemesis-websocket-external
  namespace: nemesis
  labels:
    app: nemesis
    component: websocket
spec:
  selector:
    app: nemesis
    component: websocket
  ports:
  - port: 80
    targetPort: 8001
    name: ws
  type: LoadBalancer
'''
    
    file_path = PROJECT_ROOT / "k8s" / "service.yaml"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_configmap():
    """Create configmap.yaml"""
    print("\n[4/6] Creating configmap.yaml...")
    
    content = '''# NEMESIS ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: nemesis-config
  namespace: nemesis
data:
  APP_NAME: "NEMESIS"
  APP_ENV: "production"
  APP_VERSION: "2.0.0"
  LOG_LEVEL: "INFO"
  LOG_JSON_FORMAT: "true"
  METRICS_ENABLED: "true"
  RATE_LIMIT_REQUESTS: "100"
  RATE_LIMIT_PERIOD: "60"
  WS_MAX_CONNECTIONS: "1000"
  WS_PING_INTERVAL: "20"
  WS_PING_TIMEOUT: "10"
  ML_BATCH_SIZE: "100"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nemesis-config-app
  namespace: nemesis
data:
  app.yaml: |
    app:
      name: NEMESIS
      version: 2.0.0
      environment: production
    
    logging:
      level: INFO
      json_format: true
    
    metrics:
      enabled: true
      port: 8000
    
    websocket:
      max_connections: 1000
      ping_interval: 20
      ping_timeout: 10
    
    ml:
      batch_size: 100
      model_path: /app/models
'''
    
    file_path = PROJECT_ROOT / "k8s" / "configmap.yaml"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_secret():
    """Create secret.yaml template"""
    print("\n[5/6] Creating secret.yaml template...")
    
    content = '''# NEMESIS Secrets Template
# NOTE: This file should not be committed to git!
# Use sealed-secrets or external secrets operator in production

apiVersion: v1
kind: Secret
metadata:
  name: nemesis-secrets
  namespace: nemesis
type: Opaque
data:
  # Generate with: echo -n "value" | base64
  database_url: <base64-encoded-postgres-url>
  redis_url: <base64-encoded-redis-url>
  nats_url: <base64-encoded-nats-url>
  secret_key: <base64-encoded-secret-key>
---
# Example: Create secret with kubectl
# kubectl create secret generic nemesis-secrets \\
#   --from-literal=database_url="postgresql://user:pass@host:5432/db" \\
#   --from-literal=redis_url="redis://redis:6379" \\
#   --from-literal=nats_url="nats://nats:4222" \\
#   --from-literal=secret_key="your-secret-key-here" \\
#   -n nemesis
'''
    
    file_path = PROJECT_ROOT / "k8s" / "secret.yaml"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_ingress():
    """Create ingress.yaml"""
    print("\n[6/6] Creating ingress.yaml...")
    
    content = '''# NEMESIS Ingress Configuration
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nemesis-ingress
  namespace: nemesis
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/websocket-services: nemesis-websocket
spec:
  tls:
  - hosts:
    - api.nemesis.com
    - ws.nemesis.com
    secretName: nemesis-tls
  rules:
  - host: api.nemesis.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nemesis-api
            port:
              number: 80
  - host: ws.nemesis.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nemesis-websocket
            port:
              number: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nemesis-monitoring-ingress
  namespace: nemesis
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: monitor.nemesis.com
    http:
      paths:
      - path: /prometheus
        pathType: Prefix
        backend:
          service:
            name: prometheus
            port:
              number: 9090
      - path: /grafana
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 3000
'''
    
    file_path = PROJECT_ROOT / "k8s" / "ingress.yaml"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 7: CREATE KUBERNETES MANIFESTS")
    print("="*60)
    
    create_k8s_directory()
    create_deployment()
    create_service()
    create_configmap()
    create_secret()
    create_ingress()
    
    print("\n" + "="*60)
    print("[OK] Kubernetes manifests created")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())