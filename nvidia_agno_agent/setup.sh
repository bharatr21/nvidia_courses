#!/bin/bash

set -e

echo "🔧 Setting up NVIDIA Agno Agent environment..."

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.template .env
  echo "✅ Created .env. Please edit it and add your OPENAI_API_KEY."
fi

mkdir -p data logs

echo "✅ Setup complete. Next steps:"
echo "1) Edit .env to add your API keys"
echo "2) Start AgentOS API: ./run_agentos.sh"
echo "3) Start Agno Agent UI (see below)"

