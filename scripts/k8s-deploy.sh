#!/bin/bash
# Deploy NEMESIS MADINA to Kubernetes

set -e

NAMESPACE="nemesis"

echo "🚀 Deploying NEMESIS MADINA to Kubernetes..."

# Create namespace
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets and configmaps
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml

# Deploy PostgreSQL (with replication)
kubectl apply -f k8s/postgres/statefulset.yaml
kubectl apply -f k8s/postgres/service.yaml
kubectl apply -f k8s/postgres/replication.yaml

# Deploy Redis
kubectl apply -f k8s/redis/deployment.yaml
kubectl apply -f k8s/redis/service.yaml

# Deploy NATS
kubectl apply -f k8s/nats/deployment.yaml
kubectl apply -f k8s/nats/service.yaml

# Deploy API (with HPA)
kubectl apply -f k8s/api/deployment.yaml
kubectl apply -f k8s/api/service.yaml
kubectl apply -f k8s/api/hpa.yaml
kubectl apply -f k8s/api/ingress.yaml
kubectl apply -f k8s/api/loadbalancer.yaml

# Deploy monitoring
kubectl apply -f k8s/monitoring/prometheus-config.yaml
kubectl apply -f k8s/monitoring/grafana.yaml

# Deploy backup cron
kubectl apply -f k8s/backup/cronjob.yaml

echo "✅ Deployment complete!"

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=nemesis-api -n $NAMESPACE --timeout=300s

echo "📊 Checking status..."
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE
kubectl get hpa -n $NAMESPACE

echo "🎉 NEMESIS MADINA deployed successfully!"