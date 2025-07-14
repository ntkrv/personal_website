#!/bin/bash

# 1. chmod +x install.sh
# 2. ./install.sh


echo "📦 Checking virtual environment..."

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🛠 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# Activate venv
echo "⚙️  Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Check if Flask is installed
if python -c "import flask" &> /dev/null; then
    echo "✅ Flask is already installed."
else
    echo "📦 Flask not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat <<EOF > .env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=$(openssl rand -hex 16)
DATABASE_URL=sqlite:///ntkrv.db
TEST_DATABASE_URI=sqlite:///test.db
ADMIN_USERNAME=
ADMIN_PASSWORD=
EOF
    echo "✅ .env created with default values."
else
    echo "✅ .env file already exists."
fi

# Initialize the database
echo "🗄  Initializing database with db.create_all()..."
export FLASK_APP=app.py
flask shell <<EOF
from models import db
db.create_all()
EOF

echo "🎉 Setup complete. Create ADMIN_USERNAME & ADMIN_PASSWORD in .env file, create admin using python create_admin.py and after you can run the app"
