#!/bin/bash

echo "🚀 Starting NVIDIA AI Assistant Web Application..."

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

# Check for required dependencies
python -c "import streamlit" 2>/dev/null || {
    echo "❌ Streamlit not installed. Installing frontend dependencies..."
    pip install -r requirements.txt
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Launch Streamlit app
echo "🌐 Launching web interface at http://localhost:8501"
echo "📝 Logs will be written to logs/streamlit.log"

# Run Streamlit with logging
streamlit run streamlit_app.py --logger.level info 2>&1 | tee logs/streamlit.log
