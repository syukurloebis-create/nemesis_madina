#!/bin/bash
echo "🔧 FIXING FRONTEND STRUCTURE"
echo "============================"

# Navigate to project root
cd ~/nemesis_madina

# Check current structure
echo "📁 Current structure:"
ls -la | grep -E "frontend|src"

# If src exists and frontend doesn't, move src to frontend
if [ -d "src" ] && [ ! -d "frontend" ]; then
    echo "📦 Moving src to frontend..."
    mv src frontend
fi

# If both exist, check which one has package.json
if [ -d "src" ] && [ -d "frontend" ]; then
    echo "⚠️ Both src and frontend exist"
    
    # Check which has package.json
    if [ -f "src/package.json" ] && [ ! -f "frontend/package.json" ]; then
        echo "📦 src has package.json, moving to frontend..."
        rm -rf frontend
        mv src frontend
    elif [ -f "frontend/package.json" ] && [ ! -f "src/package.json" ]; then
        echo "📦 frontend has package.json, removing src..."
        rm -rf src
    else
        echo "⚠️ Both have package.json, keeping frontend..."
        rm -rf src
    fi
fi

# Verify final structure
echo ""
echo "✅ Final structure:"
ls -la | grep -E "frontend|src"

# Test frontend
cd frontend
if [ -f "package.json" ]; then
    echo "✅ package.json found"
    npm install 2>&1 | tail -5
else
    echo "❌ package.json not found in frontend/"
fi

echo ""
echo "✅ Frontend structure fixed!"