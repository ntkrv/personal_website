# PowerShell setup script for Windows environment (no WSL required)

Write-Host "Checking virtual environment..."

# Create venv if it doesn't exist
if (-Not (Test-Path ".\venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists."
}

# Activate venv
Write-Host "Activating virtual environment..."
. .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file..."
    $secret = python -c "import secrets; print(secrets.token_hex(32))"

    $envContent = @"
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=$secret
DATABASE_URL=sqlite:///ntkrv.db
TEST_DATABASE_URI=sqlite:///test.db
ADMIN_USERNAME=
ADMIN_PASSWORD=
"@

    $envContent | Out-File -Encoding UTF8 .env
    Write-Host ".env file created."
} else {
    Write-Host ".env file already exists."
}

# Initialize database using Flask shell
Write-Host "Initializing database..."
$env:FLASK_APP = "app.py"
flask shell -c "from models import db; db.create_all()"

Write-Host "Setup complete. You can now run the application with: python app.py"
Set-ExecutionPolicy RemoteSigned -Scope Process
