#!/usr/bin/env python3
"""
AgentOS Application for NVIDIA Agno Agents.
This provides the AgentOS API and web interface.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project to Python path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from agentos import AgentOS
from agentos.config import AgentOSConfig

# Load environment
load_dotenv()

# Initialize AgentOS
agent_os = AgentOS(
    config=AgentOSConfig.from_file("config/agentos.yaml")
)

# This creates the FastAPI app that serves the AgentOS API
app = agent_os.api

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("AGENTOS_API_HOST", "0.0.0.0")
    port = int(os.getenv("AGENTOS_API_PORT", 8000))
    
    print(f"🚀 Starting AgentOS API at http://{host}:{port}")
    print("📖 Docs available at http://localhost:8000/docs")
    print("🎯 UI available at http://localhost:8501 (after starting UI)")
    
    uvicorn.run(app, host=host, port=port)
