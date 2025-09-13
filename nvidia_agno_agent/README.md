# 🚀 NVIDIA AI Agent - Agno 2.0 Edition

An advanced NVIDIA AI assistant built with **Agno 2.0** framework and **AgentOS**, featuring the beautiful Agno Agent UI. This implementation provides specialized agents for different NVIDIA domains that work individually or as teams.

## ✨ Features

### 🧠 Multi-Agent Architecture
- **Specialist Agents**: Individual experts for NIM, RAG, GenAI, and general NVIDIA topics
- **Team Coordination**: Agents can work together on complex queries
- **Shared Knowledge**: All agents access the same NVIDIA knowledge base
- **Memory & Context**: Persistent conversation history across sessions

### 📚 Knowledge Sources
- **NVIDIA Course Transcripts**: Building RAG Agents, GenAI Explained, NIM Microservices, LLM Sizing
- **Live Web Search**: Real-time NVIDIA Developer Blog and NVIDIA Blog search
- **Vector Knowledge Base**: Qdrant or ChromaDB for semantic search
- **Smart Retrieval**: Automated source selection based on query type

### 🎯 Agent Specialists
1. **NVIDIA Generalist**: Broad NVIDIA knowledge and general queries
2. **NIM Expert**: NVIDIA Inference Microservices specialist
3. **RAG Expert**: Retrieval Augmented Generation specialist  
4. **GenAI Expert**: Generative AI foundations and frameworks

### 🌟 Agno Agent UI Features
- **Beautiful Interface**: Modern, responsive chat interface
- **Agent Selection**: Choose specific experts or let the system decide
- **Source Attribution**: See which knowledge sources were used
- **Memory Visualization**: View conversation history and context
- **Real-time Updates**: Live agent responses and thinking process

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd nvidia_agno_agent
./setup.sh
```

### 2. Configure API Keys
Edit `.env` file and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start AgentOS API
```bash
./run_agentos.sh
```
This starts the AgentOS API at `http://localhost:8000`

### 4. Launch Agno Agent UI
In a separate terminal, install and start the Agno Agent UI:
```bash
# Install Agno Agent UI (if not already installed)
npm install -g @agno/agent-ui
# OR
pip install agno-ui

# Start the UI and connect to your AgentOS
agno-ui --api-url http://localhost:8000
```

The beautiful Agno Agent UI will open at `http://localhost:8501`

## 🏗️ Architecture

```
nvidia_agno_agent/
├── agents/
│   └── nvidia_agents.py        # Specialist agent definitions
├── knowledge/
│   └── nvidia_knowledge.py     # Agno Knowledge integration
├── tools/
│   └── nvidia_blog_tool.py     # Web search capabilities
├── config/
│   └── agentos.yaml            # AgentOS configuration
├── workflows/                  # Complex multi-agent workflows
├── agentos_app.py             # AgentOS FastAPI application
└── data/                      # Knowledge base and memory storage
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
OPENAI_API_KEY=your_key_here

# AgentOS Configuration
AGENTOS_DATABASE_URL=sqlite:///data/agentos.db
AGENTOS_API_HOST=0.0.0.0
AGENTOS_API_PORT=8000
AGENTOS_UI_PORT=8501

# Vector Database (Qdrant preferred, ChromaDB fallback)
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=nvidia_knowledge

# Knowledge Base
TRANSCRIPT_PATH=../
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Web Search
MAX_SEARCH_RESULTS=10
NVIDIA_DEV_BLOG_RSS=https://developer.nvidia.com/blog/feed
NVIDIA_BLOG_RSS=https://blogs.nvidia.com/feed
```

## 🎯 Using the Agents

### Through Agno Agent UI
1. Open `http://localhost:8501` in your browser
2. Select an agent or use auto-routing
3. Ask questions about NVIDIA technologies
4. View source attribution and conversation history

### Available Agents
- **nvidia-generalist**: General NVIDIA questions and broad topics
- **nvidia-nim**: NIM microservices, deployment, architecture
- **nvidia-rag**: RAG systems, evaluation, best practices
- **nvidia-genai**: Generative AI, LLMs, NVIDIA AI ecosystem

### Example Queries
```
🔍 "What is NVIDIA NIM and how do I deploy it?"
→ Routes to NIM Expert + knowledge base + web search

🔍 "Explain RAG evaluation methodologies"
→ Routes to RAG Expert + course transcripts

🔍 "Latest NVIDIA AI announcements"
→ Web search + Generalist agent

🔍 "How to optimize GenAI performance on GPUs"
→ GenAI Expert + knowledge base + web search
```

## 🧠 Knowledge Base

### Automatic Loading
The system automatically processes NVIDIA course transcripts:
- Extracts content and metadata
- Creates semantic chunks
- Generates embeddings
- Stores in vector database

### Vector Database Options
1. **Qdrant** (Recommended for production)
   - High performance
   - Advanced filtering
   - Scalable
   
2. **ChromaDB** (Fallback)
   - Simple setup
   - Good for development
   - Local storage

## 🔍 Advanced Features

### Multi-Agent Workflows
```python
# Example: Complex query requiring multiple specialists
query = "How to build a RAG system with NIM for GenAI applications?"
# → Involves RAG Expert + NIM Expert + GenAI Expert
```

### Memory & Context
- **Persistent Memory**: SQLite-based conversation storage
- **Context Windows**: Configurable history length
- **Cross-Session**: Remember previous conversations
- **Agent-Specific**: Each agent maintains its own context

### Real-time Search
- **Live Blog Search**: Current NVIDIA announcements and tutorials
- **Content Extraction**: Full article content for detailed answers
- **Source Ranking**: Relevance-based result ordering

## 🛠️ Development

### Adding New Agents
```python
# In agents/nvidia_agents.py
custom_expert = Agent(
    name="Custom Expert",
    model=build_base_model(),
    tools=[blog_tool],
    instructions=[
        "You are a specialist in [domain]",
        "Focus on [specific expertise]"
    ]
)
```

### Custom Tools
```python
# Create new tool in tools/
class CustomAgnoTool(AgnoTool):
    name = "custom_tool"
    description = "Tool description"
    
    async def run(self, param: str) -> Dict[str, Any]:
        # Tool implementation
        return {"result": "data"}
```

### Knowledge Sources
```python
# Add custom knowledge in knowledge/
await knowledge.add_web_content(
    title="Custom Document",
    content="Document content",
    source_url="https://example.com",
    metadata={"type": "custom"}
)
```

## 📊 Monitoring & Analytics

### AgentOS Dashboard
- **Agent Performance**: Response times, success rates
- **Knowledge Usage**: Source utilization statistics
- **Memory Patterns**: Conversation flow analysis
- **System Health**: API status, database metrics

### Logging
- **Structured Logging**: JSON-formatted logs
- **Agent Actions**: Detailed agent decision tracking
- **Error Tracking**: Exception handling and reporting
- **Performance Metrics**: Response time analysis

## 🚀 Deployment

### Local Development
```bash
# Start API
./run_agentos.sh

# Start UI (separate terminal)
agno-ui --api-url http://localhost:8000
```

### Production Deployment
```bash
# With Docker
docker-compose up -d

# With systemd
systemctl start nvidia-agentos
```

### Scaling Options
- **Load Balancing**: Multiple AgentOS instances
- **Database Scaling**: External Qdrant cluster  
- **Memory Distribution**: Redis-based shared memory
- **API Gateway**: Route requests across agents

## 🔗 Integration

### API Access
```python
import requests

# Chat with specific agent
response = requests.post("http://localhost:8000/agents/nvidia-nim/chat", 
    json={"message": "How do I deploy NIM?"})
```

### Webhook Integration
```python
# Receive agent responses
@app.post("/webhook")
async def agent_webhook(data: dict):
    agent_response = data["response"]
    # Process response
```

## 🆘 Troubleshooting

### Common Issues

1. **AgentOS API Won't Start**
   ```bash
   # Check dependencies
   pip install -r requirements.txt
   
   # Verify environment
   cat .env
   ```

2. **Agent UI Connection Failed**
   ```bash
   # Verify API is running
   curl http://localhost:8000/health
   
   # Check UI configuration
   agno-ui --api-url http://localhost:8000 --debug
   ```

3. **Knowledge Base Empty**
   ```bash
   # Check transcript path
   ls ../*/Transcript.txt
   
   # Verify database
   sqlite3 data/agentos.db ".tables"
   ```

4. **Vector Database Issues**
   ```bash
   # Test Qdrant connection
   curl http://localhost:6333/collections
   
   # Fallback to ChromaDB
   rm -rf data/chromadb && restart
   ```

## 🎯 Roadmap

### Upcoming Features
- [ ] **Multi-Modal Support**: Image and document upload
- [ ] **Voice Interface**: Speech-to-text integration
- [ ] **Custom Workflows**: Visual workflow builder
- [ ] **Enterprise Features**: SSO, RBAC, audit logs
- [ ] **Advanced Analytics**: Usage patterns, insights
- [ ] **API Gateway**: Rate limiting, authentication

### Performance Improvements
- [ ] **Caching Layer**: Response caching for common queries
- [ ] **Async Processing**: Parallel agent execution
- [ ] **Smart Routing**: ML-based agent selection
- [ ] **Knowledge Optimization**: Hybrid search strategies

## 📞 Support

### Getting Help
1. **Documentation**: Check Agno docs at https://docs.agno.com
2. **GitHub Issues**: Report bugs and feature requests
3. **Community**: Join the Agno Discord/Slack
4. **Logs**: Check `logs/` directory for detailed information

### Performance Tips
- Use Qdrant for better search performance
- Configure appropriate memory limits
- Monitor agent response times
- Optimize knowledge base chunking

---

**Built with ❤️ using Agno 2.0, AgentOS, and the beautiful Agno Agent UI**

This implementation showcases the power of the Agno framework for building sophisticated multi-agent systems with beautiful, production-ready interfaces.
