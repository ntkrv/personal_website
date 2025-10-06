Write-Output "Loading environment variables..."
Get-Content .env | ForEach-Object {
    if ($_ -notmatch '^#' -and $_ -match '=') {
        $name, $value = $_ -split '=', 2
        Set-Item -Path Env:$name -Value $value
    }
}

# === Clean Python cache files ===
Write-Output "Cleaning Python cache files..."
Get-ChildItem -Path . -Include __pycache__, *.pyc -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Output "Python cache cleared."

Write-Output "Updating pip..."
python -m pip install --upgrade pip

Write-Output "Updating requirements.txt..."
pip freeze > requirements.txt

Write-Output "Running black formatter..."
black .

Write-Output "Running flake8 linter..."
flake8 .

Write-Output "Running database migrations..."
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

try {
    flask db migrate -m "Auto migration"
} catch {
    Write-Output "No model changes detected, skipping migration."
}

flask db upgrade

Write-Output "Checking and creating admin user if necessary..."
try {
    python utils/create_admin.py
    Write-Host "Admin verification and creation completed successfully." -ForegroundColor Green
} catch {
    Write-Host "Could not verify or create admin user. Check utils/create_admin.py for issues." -ForegroundColor Yellow
}

Write-Output "Building Tailwind CSS..."
npm run build:css

# === Validate .icon CSS Class ===
$cssPath = "static/css/styles.css"
if (Test-Path $cssPath) {
    $content = Get-Content $cssPath -Raw
    if ($content -match "\.icon") {
        Write-Host ".icon class found in CSS" -ForegroundColor Green
    } else {
        Write-Host "WARNING: .icon class not found in styles.css!" -ForegroundColor Yellow
        Write-Host "Ensure 'safelist' includes 'icon' in tailwind.config.js" -ForegroundColor DarkYellow
        Write-Host "Example: safelist: ['icon']" -ForegroundColor DarkGray
    }
} else {
    Write-Host "CSS file not found! Check if Tailwind build was successful." -ForegroundColor Red
}

Write-Output "Starting Flask app..."
flask run
