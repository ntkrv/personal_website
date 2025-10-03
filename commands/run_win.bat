@echo off

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Loading environment variables from .env...
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    set "%%A=%%B"
)

echo Upgrading pip...
python -m pip install --upgrade pip

echo Updating requirements.txt...
pip freeze > requirements.txt

echo Running black formatter...
black .

echo Running flake8 linter...
flake8 .

echo Applying database migrations...
set FLASK_APP=app.py
set FLASK_ENV=development
flask db upgrade
flask db migrate -m "Auto migration"

echo Creating admin user...
python utils\create_admin.py

echo Building Tailwind CSS...
start cmd /k "npm run build:css"

echo Starting Flask server...
flask run
