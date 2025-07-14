#!/bin/bash

set -e

echo "📦 Loading environment variables..."
export $(grep -v '^#' .env | xargs)

echo "⬆️  Updating pip..."
python3 -m pip install --upgrade pip

echo "🔁 Updating requirements.txt..."
pip freeze > requirements.txt

echo "🎨 Running black formatter..."
black .

echo "🔍 Running flake8 linter..."
flake8 .

echo "🧬 Checking and applying database migrations..."
export FLASK_APP=app.py
export FLASK_ENV=development

flask db upgrade
flask db migrate -m "Auto migration" || echo "No changes detected."

echo "👤 Creating admin user (if not exists)..."
python3 utils/create_admin.py

echo "🎨 Building Tailwind CSS..."
npm run build:css &

echo "🚀 Starting Flask app..."
flask run
