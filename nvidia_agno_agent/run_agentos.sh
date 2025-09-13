#!/bin/bash

set -e

if [ ! -d venv ]; then
  echo "❌ Virtual environment not found. Run ./setup.sh first."
  exit 1
fi

source venv/bin/activate

if [ ! -f .env ]; then
  echo "❌ .env file not found. Copy from .env.template and edit it."
  exit 1
fi

echo "🚀 Starting NVIDIA AgentOS API..."
echo "📖 API docs: http://localhost:8000/docs"
echo "🎯 Connect Agno UI to: http://localhost:8000"

python agentos_app.py
