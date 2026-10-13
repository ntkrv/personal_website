#!/bin/bash

# Production start: install deps, build CSS, apply migrations, serve
# via Gunicorn. Run from the repo root:
#   ./scripts/run_prod.sh
#
# Migrations are applied, never generated, here: create them locally
# with `flask db migrate`, review, and commit them with the code.

set -euo pipefail

echo "📦 Loading environment variables..."
if [ -f .env ]; then
  # Sourcing (instead of `export $(... | xargs)`) keeps quoted values
  # with spaces or special characters intact.
  set -a
  . ./.env
  set +a
fi

export FLASK_APP=wsgi.py
export FLASK_ENV=production

echo "📦 Installing Python packages..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "🎨 Building Tailwind CSS..."
npm ci
npm run build:css

echo "🧬 Applying migrations..."
mkdir -p instance
flask db upgrade

BIND="${GUNICORN_BIND:-0.0.0.0:8000}"
WORKERS="${GUNICORN_WORKERS:-2}"

echo "🚀 Starting Gunicorn on ${BIND} (${WORKERS} workers)..."
exec gunicorn --bind "${BIND}" --workers "${WORKERS}" \
  --access-logfile - --error-logfile - wsgi:app
