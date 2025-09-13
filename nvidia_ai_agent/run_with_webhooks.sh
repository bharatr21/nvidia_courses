#!/bin/bash

echo "🚀 Starting NVIDIA AI Assistant with Webhook Support..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one from .env.template"
    echo "   Make sure to set your OPENAI_API_KEY!"
fi

# Install additional webhook dependencies if not present
pip install flask flask-cors waitress > /dev/null 2>&1

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping services..."
    jobs -p | xargs -r kill
    exit 0
}

# Trap cleanup function on script exit
trap cleanup EXIT INT TERM

# Start webhook server in background
echo "🔗 Starting webhook server on port 5000..."
python src/webhook_server.py --port 5000 > logs/webhook.log 2>&1 &
WEBHOOK_PID=$!

# Wait a moment for webhook server to start
sleep 3

# Check if webhook server started successfully
if kill -0 $WEBHOOK_PID 2>/dev/null; then
    echo "✅ Webhook server started successfully (PID: $WEBHOOK_PID)"
    echo "📡 Webhook endpoint: http://localhost:5000/webhook/nvidia-blog"
else
    echo "❌ Failed to start webhook server"
    exit 1
fi

# Start Streamlit app
echo "🌐 Starting Streamlit app on port 8501..."
echo "📝 Logs: webhook.log, streamlit.log"
echo ""
echo "🎯 Open your browser to: http://localhost:8501"
echo "📡 Webhook URL for Zapier: http://localhost:5000/webhook/nvidia-blog"
echo ""
echo "Press Ctrl+C to stop both services"

# Run Streamlit with logging
streamlit run streamlit_app.py --logger.level info 2>&1 | tee logs/streamlit.log
