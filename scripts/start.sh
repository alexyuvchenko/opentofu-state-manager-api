#!/bin/sh

echo "Checking if database migrations are needed..."
CURRENT_REV=$(alembic current 2>/dev/null || echo "No current revision")
HEAD_REV=$(alembic heads | head -n1)

if [ "$CURRENT_REV" != "$HEAD_REV" ]; then
    echo "Running database migrations..."
    alembic upgrade head
else
    echo "Database is up to date, no migrations needed."
fi

echo "Starting application..."
exec gunicorn src.main:app --worker-class uvicorn.workers.UvicornWorker --reload --workers 1 -b 0.0.0.0:8000 
