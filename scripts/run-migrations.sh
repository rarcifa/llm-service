#!/bin/bash

set -e

echo "Checking for pending Alembic migrations..."

# Ensure PYTHONPATH is set so Alembic can find 'app'
export PYTHONPATH=.

# Check current and head revision
CURRENT_REV=$(alembic current --verbose | grep 'Rev:' | awk '{print $2}')
HEAD_REV=$(alembic heads | awk '{print $1}')

if [ "$CURRENT_REV" != "$HEAD_REV" ]; then
  echo "Migrations pending. Running upgrade..."
  alembic upgrade head
  echo "Migrations applied successfully."
else
  echo "No migrations needed. Database is up to date."
fi
