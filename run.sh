#!/bin/bash

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

# Only run `db init` if migrations folder doesn't exist
if [ ! -d "migrations" ]; then
  flask db init
fi

flask db migrate -m "Auto migration"
flask db upgrade

echo "🚀 Starting Flask app..."
flask run
