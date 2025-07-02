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
export FLASK_ENV=testing
coverage run -m pytest
coverage report -m

echo "🧬 Running migrations..."
export FLASK_APP=app.py
export FLASK_ENV=development

# Удаление старых миграций и базы
rm -rf migrations
rm -f instance/ntkrv.db

# Убедимся, что instance существует
mkdir -p instance

flask db init
flask db migrate -m "Initial migration"
flask db upgrade

echo "👤 Creating admin user..."
python3 create_admin.py


echo "🎨 Building Tailwind CSS..."
npm run build:css &

echo "🚀 Starting Flask app..."
flask run
