#!/bin/bash

echo "Setting up NVIDIA AI Agent environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "Created .env file from template. Please edit it with your API keys."
fi

# Create necessary directories
mkdir -p data/chromadb
mkdir -p data/transcripts
mkdir -p logs

echo "Setup complete! Don't forget to:"
echo "1. Edit .env file with your API keys"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the agent: python src/main.py"
