#!/bin/bash

# Stop script if any command fails
set -e

# Activate virtual environment if needed
# source venv/bin/activate

# Run the Python script to create admin user
echo "Creating admin user..."
export FLASK_APP=app.py
flask create-admin

# Done
echo "Done."
