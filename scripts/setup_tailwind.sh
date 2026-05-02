#!/bin/bash

# chmod +x setup_tailwind.sh
# ./setup_tailwind.sh



set -e

echo "🔍 Checking for Node.js and npm..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it using: brew install node"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

echo "✅ Node.js version: $(node -v)"
echo "✅ npm version: $(npm -v)"

echo "📦 Installing tailwindcss, postcss and autoprefixer..."
npm install -D tailwindcss postcss autoprefixer

echo "⚙️ Initializing Tailwind and PostCSS config files..."
npx tailwindcss init -p

echo "📁 Creating directory structure..."
mkdir -p static/src static/css

echo "📝 Creating input.css with Tailwind directives..."
cat <<EOL > static/src/input.css
@tailwind base;
@tailwind components;
@tailwind utilities;
EOL

echo "🔧 Updating package.json with build:css script..."
if [ -f "package.json" ]; then
  if ! grep -q '"build:css"' package.json; then
    npx npm-add-script -k "build:css" -v "npx tailwindcss -i ./static/src/input.css -o ./static/css/tailwind.css --watch"
  fi
else
  echo "❌ package.json not found. Run 'npm init -y' first and then rerun this script."
  exit 1
fi

echo "✅ Tailwind CSS is set up successfully!"
echo "🚀 Run this command to start watching: npm run build:css"
