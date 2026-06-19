#!/bin/bash
# NEMESIS Setup Script

set -e

echo "=== NEMESIS V8+ Setup ==="

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/Scripts/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p /keys
mkdir -p logs
mkdir -p data/evidence

# Generate development key
echo "Generating development signing key..."
python -c "
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
key = Ed25519PrivateKey.generate()
with open('/keys/dev_signing_key.pem', 'wb') as f:
    f.write(key.private_bytes_raw())
"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://nemesis:password@localhost:5432/nemesis_db
REDIS_URL=redis://localhost:6379/0
NEMESIS_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
EOF

echo "=== Setup complete ==="
echo "Run 'docker-compose up -d' to start services"
echo "Run 'uvicorn backend.main:app --reload' to start API"