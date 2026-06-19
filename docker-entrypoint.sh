#!/bin/bash
set -e

# Generate secret key if not exists
if [ ! -f /keys/secret.key ]; then
    echo "Generating secret key..."
    python /tmp/generate_key.py
fi

# Run database migrations (if needed)
# alembic upgrade head

# Start uvicorn
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
