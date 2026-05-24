#!/bin/bash

echo "🚀 Starting AI Financial Research Assistant (Development Mode)"
echo "=============================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Set development mode
export DEBUG=true

# Start services
echo "📡 Starting API server..."
python -m uvicorn src.api.routes:app --reload --host 0.0.0.0 --port 8001 &
API_PID=$!

echo "🎨 Starting Streamlit UI..."
streamlit run ui/streamlit_app.py --server.port 8501 &
UI_PID=$!

echo ""
echo "✅ Services started!"
echo "   API: http://localhost:8001"
echo "   UI:  http://localhost:8501"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C and kill background processes
trap "kill $API_PID $UI_PID; exit" SIGINT SIGTERM

# Wait for processes
wait