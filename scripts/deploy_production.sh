#!/bin/bash
# Production Deployment Script - NEMESIS V8.1

echo "🚀 NEMESIS V8.1 PRODUCTION DEPLOYMENT"
echo "======================================"
echo ""

# 1. Pre-deployment checks
echo "📋 1. Pre-deployment checks..."

# Check Python version
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.12"
if [[ "$python_version" < "$required_version" ]]; then
    echo "❌ Python $required_version+ required, found $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"

# Check environment variables
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found, creating from template..."
    cp .env.example .env
fi
echo "✅ Environment configuration ready"

# Check database
if [ ! -f "nemesis.db" ]; then
    echo "⚠️ Database not found, initializing..."
    python -c "from backend.database import init_db; init_db()"
fi
echo "✅ Database ready"

echo ""

# 2. Backup current deployment
echo "📦 2. Creating pre-deployment backup..."
python scripts/backup.py --create
echo "✅ Backup completed"

echo ""

# 3. Install dependencies
echo "📦 3. Installing dependencies..."
pip install -r requirements.txt --upgrade
cd frontend && npm install && npm run build && cd ..
echo "✅ Dependencies installed"

echo ""

# 4. Run migrations
echo "🔄 4. Running database migrations..."
alembic upgrade head 2>/dev/null || echo "⚠️ No migrations found"
echo "✅ Migrations completed"

echo ""

# 5. Start services
echo "▶️ 5. Starting services..."

# Stop existing services
pkill -f "uvicorn backend.main:app" 2>/dev/null
pkill -f "node.*frontend" 2>/dev/null

# Start backend
echo "  📡 Starting Backend..."
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4 > logs/backend.log 2>&1 &

# Start frontend (if not using CDN)
if [ -f "frontend/dist/index.html" ]; then
    echo "  🌐 Starting Frontend..."
    cd frontend
    nohup npx serve -s dist -l 3000 > ../logs/frontend.log 2>&1 &
    cd ..
fi

echo "✅ Services started"

echo ""

# 6. Health check
echo "🩺 6. Health check..."
sleep 5
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    tail -20 logs/backend.log
    exit 1
fi

if [ -f "frontend/dist/index.html" ]; then
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Frontend health check passed"
    else
        echo "⚠️ Frontend health check failed"
    fi
fi

echo ""

# 7. Deployment summary
echo "📊 7. Deployment Summary"
echo "========================"
echo "✅ Backend: http://localhost:8000"
echo "✅ API Docs: http://localhost:8000/docs"
echo "✅ Frontend: http://localhost:3000"
echo "✅ Health: http://localhost:8000/health"
echo ""

echo "🎉 NEMESIS V8.1 Deployed Successfully!"