#!/bin/bash
# NEMESIS V8+ - Frontend Configuration Auto-Fix Script
# Memperbaiki base URL dari localhost:8000 ke localhost:80

set -e

echo "=========================================="
echo "  NEMESIS V8+ - Frontend Auto-Fix"
echo "=========================================="
echo ""

FRONTEND_DIR="./frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

cd $FRONTEND_DIR

# 1. Backup current configuration
echo "📁 1. Backing up current configuration..."
mkdir -p .backup
cp .env .backup/.env.bak 2>/dev/null || true
cp .env.development .backup/.env.development.bak 2>/dev/null || true
cp src/services/api.ts .backup/api.ts.bak 2>/dev/null || true
cp src/hooks/useWebSocket.tsx .backup/useWebSocket.tsx.bak 2>/dev/null || true
cp vite.config.ts .backup/vite.config.ts.bak 2>/dev/null || true
echo "   ✅ Backup completed"

# 2. Fix .env files
echo -e "\n📁 2. Fixing environment files..."
cat > .env << 'ENVEOF'
VITE_API_URL=http://localhost
VITE_WS_URL=ws://localhost
ENVEOF
cat > .env.development << 'ENVEOF'
VITE_API_URL=http://localhost
VITE_WS_URL=ws://localhost
ENVEOF
cat > .env.production << 'ENVEOF'
VITE_API_URL=http://localhost
VITE_WS_URL=ws://localhost
ENVEOF
echo "   ✅ Environment files fixed"

# 3. Fix api.ts base URL
echo -e "\n📁 3. Fixing API service..."
# Remove any hardcoded localhost:8000
sed -i 's|http://localhost:8000|http://localhost|g' src/services/api.ts 2>/dev/null || true
sed -i 's|const API_URL = .*|const API_URL = import.meta.env.VITE_API_URL || "http://localhost";|g' src/services/api.ts 2>/dev/null || true
echo "   ✅ API service fixed"

# 4. Fix WebSocket URL
echo -e "\n📁 4. Fixing WebSocket hook..."
sed -i 's|ws://localhost:8000|ws://localhost|g' src/hooks/useWebSocket.tsx 2>/dev/null || true
echo "   ✅ WebSocket hook fixed"

# 5. Clear cache
echo -e "\n📁 5. Clearing Vite cache..."
rm -rf node_modules/.vite
rm -rf .vite
echo "   ✅ Cache cleared"

# 6. Verify changes
echo -e "\n📁 6. Verifying changes..."
echo "   API_URL in .env: $(grep VITE_API_URL .env)"
echo "   WS_URL in .env: $(grep VITE_WS_URL .env)"
echo "   Hardcoded ports in api.ts: $(grep -c 'localhost:8000' src/services/api.ts || echo '0')"
echo "   Hardcoded ports in useWebSocket: $(grep -c 'localhost:8000' src/hooks/useWebSocket.tsx || echo '0')"

echo -e "\n=========================================="
echo "  ✅ Frontend configuration fixed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. cd frontend"
echo "  2. npm run dev"
echo "  3. Open http://localhost:5173"
echo "  4. Login with admin/admin123"
echo ""
