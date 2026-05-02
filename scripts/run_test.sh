#!/bin/bash

# chmod +x run_test.sh
# ./run_test.sh

set -e

echo "📦 Loading environment variables for testing..."
export $(grep -v '^#' .env | xargs)

echo "🔁 Preparing testing environment..."
export FLASK_APP=app.py
export FLASK_ENV=testing

# Clean instance and test database
rm -f instance/test.db
mkdir -p instance
touch instance/test.db

# Clean migrations
rm -rf migrations

echo "🧬 Re-initializing database and migrations..."
flask db init
flask db migrate -m "Test migration"
flask db upgrade

echo "✅ Creating admin user..."
flask create-admin

echo "🧪 Running tests with coverage..."
coverage run -m pytest
coverage report -m
