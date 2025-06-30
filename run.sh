#!/bin/bash

echo "⬆️  Updating pip..."
python3 -m pip install --upgrade pip

echo "🔁 Updating requirements.txt..."
pip freeze > requirements.txt

echo "🔍 Running flake8..."
flake8 .

echo "🎨 Running black..."
black .

echo "🧪 Running tests with coverage..."
coverage run -m pytest
coverage report -m

echo "🧬 Running migrations..."
export FLASK_APP=app.py
export FLASK_ENV=development

# Run `db init` only if migrations folder doesn't exist
if [ ! -d "migrations" ]; then
  flask db init
fi

flask db migrate -m "Auto migration"
flask db upgrade

echo "🎨 Building Tailwind CSS..."
npm run build:css &

echo "🚀 Starting Flask app..."
flask run
