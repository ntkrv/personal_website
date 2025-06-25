#!/bin/bash

# 1. chmod +x install.sh
# 2. ./run.sh

echo "🔍 Running flake8..."
flake8 .

echo "🎨 Running black..."
black .

echo "🚀 Starting Flask app..."
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
