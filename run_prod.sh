#!/bin/bash

# chmod +x run_prod.sh
# ./run_prod.sh


echo "📦 Installing Python packages..."
python3 -m pip install -r requirements.txt

echo "🎨 Building Tailwind CSS for production..."
npm run build:css:prod

echo "🧬 Running migrations..."
export FLASK_APP=app.py
export FLASK_ENV=production

# Run `db init` only if migrations folder doesn't exist
if [ ! -d "migrations" ]; then
  flask db init
fi

flask db migrate -m "Production migration"
flask db upgrade

echo "🚀 Starting Flask app..."
flask run --host=0.0.0.0 --port=8000
