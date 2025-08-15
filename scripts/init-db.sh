#!/bin/bash

set -e

DB_NAME="llm_db"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"

echo "Checking if database '$DB_NAME' exists..."

if psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
  echo "Database '$DB_NAME' already exists."
else
  echo "Creating database '$DB_NAME'..."
  createdb -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" "$DB_NAME"
  echo "Created."
fi

echo "Running Alembic migrations..."
PYTHONPATH=. alembic upgrade head
echo "Database initialized and migrated."
