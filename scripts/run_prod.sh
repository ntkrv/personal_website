#!/bin/bash

# chmod +x run_prod.sh
# ./run_prod.sh

set -e

echo "📦 Loading environment variables..."
export $(grep -v '^#' .env | xargs)

echo "📦 Installing Python packages..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "🎨 Building Tailwind CSS for production..."
npm run build:css:prod

echo "🧬 Running migrations..."
export FLASK_APP=app.py
export FLASK_ENV=production

# Ensure instance folder exists
mkdir -p instance

# Ensure production database exists
touch instance/ntkrv.db

# Initialize migrations if needed
if [ ! -d "migrations" ]; then
  flask db init
fi

flask db migrate -m "Production migration"
flask db upgrade

echo "🚀 Starting Flask app on 0.0.0.0:8000..."
flask run --host=0.0.0.0 --port=8000
