# run_win.ps1 — clean working version

Write-Host "Loading environment variables from .env..."

Get-Content .env | ForEach-Object {
    if ($_ -match '^(?!#)([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim('"').Trim()
        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

Write-Host "Updating pip..."
python -m pip install --upgrade pip

Write-Host "Updating requirements.txt..."
pip freeze > requirements.txt

Write-Host "Running black formatter..."
black .

Write-Host "Running flake8 linter..."
flake8 .

Write-Host "Applying database migrations..."
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

flask db upgrade
try {
    flask db migrate -m "Auto migration"
} catch {
    Write-Host "No changes detected or migration failed."
}

Write-Host "Creating admin user (if not exists)..."
python utils/create_admin.py

Write-Host "Building Tailwind CSS (watch mode)..."
Start-Process powershell -ArgumentList "npm run build:css"

Write-Host "Starting Flask app..."
flask run
