#!/bin/bash

set -e

MESSAGE=${1:-"auto migration"}
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FULL_MESSAGE="${MESSAGE} ${TIMESTAMP}"

echo "Ensuring database is at latest migration..."
PYTHONPATH=. alembic upgrade head

echo "Generating new Alembic migration: \"$FULL_MESSAGE\""
PYTHONPATH=. alembic revision --autogenerate -m "$FULL_MESSAGE"

echo "Migration file created."