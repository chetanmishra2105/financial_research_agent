#!/bin/bash

echo "🔧 Setting up AI Financial Research Assistant..."
echo "================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
echo "Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p chroma_db
mkdir -p .cache

# Copy environment file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your API keys"
fi

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v

echo ""
echo "✅ Setup complete!"
echo ""
echo "To get started:"
echo "  1. Update .env with your API keys"
echo "  2. Run: source venv/bin/activate"
echo "  3. Start API: python -m src.main api"
echo "  4. Start UI: python -m src.main ui"
echo ""
echo "Or use Docker: docker-compose up --build"