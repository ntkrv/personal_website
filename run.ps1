Write-Output "Running flake8..."
flake8 .

Write-Output "Running black..."
black .

Write-Output "Starting Flask app..."
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
flask run
