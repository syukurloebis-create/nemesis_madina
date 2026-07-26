#!/bin/bash
# Rollback Script

echo "🔄 ROLLBACK"
echo "==========="

# 1. Check current revision
echo "📊 Current revision:"
kubectl rollout history deployment/nemesis-api -n nemesis

# 2. Rollback to previous
echo ""
echo "⏪ Rolling back..."
kubectl rollout undo deployment/nemesis-api -n nemesis

# 3. Wait for rollback
echo ""
echo "⏳ Waiting for rollback..."
kubectl rollout status deployment/nemesis-api -n nemesis

# 4. Verify
echo ""
echo "🩺 Verifying..."
kubectl get pods -n nemesis -l app=nemesis

echo ""
echo "✅ Rollback complete!"