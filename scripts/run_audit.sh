#!/bin/bash
# Run backend audit

echo "🔍 Running NEMESIS Backend Audit..."
echo "========================================"

# Check Python version
python_version=$(python3 --version 2>&1)
echo "Python: $python_version"

# Run audit script
python3 scripts/audit_backend.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Audit completed successfully!"
else
    echo ""
    echo "❌ Audit found issues. Check report above."
fi