# 🚀 NVIDIA AI Conversational Agent

A sophisticated AI assistant specializing in NVIDIA technologies, powered by Retrieval Augmented Generation (RAG) and live web search capabilities. Built using the NVIDIA NeMo Agent Toolkit with both CLI and modern web interfaces.

## ✨ Features

### 🧠 Core Capabilities
- **Multi-source Knowledge Retrieval**: Combines local course transcripts with live NVIDIA blog search
- **RAG-Powered Responses**: Uses advanced RAG techniques for accurate, contextual answers
- **Conversation Memory**: Maintains context across conversation sessions
- **Real-time Web Search**: Live search of NVIDIA Developer Blog and NVIDIA Blog
- **Smart Source Selection**: Automatically determines the best sources based on query type

### 🎯 Specialization Areas
- **NVIDIA NIM (Inference Microservices)**: Architecture, deployment, optimization
- **Generative AI & LLMs**: Implementation, best practices, frameworks
- **RAG Systems**: Design patterns, evaluation, optimization
- **NVIDIA AI Ecosystem**: Tools, SDKs, platforms, enterprise solutions
- **GPU Computing**: Performance tuning, acceleration strategies
- **Current NVIDIA News**: Latest announcements, product releases, technical updates

### 💻 Interface Options
1. **🌐 Web Interface**: Modern Streamlit-based web application with chat interface
2. **💻 CLI Interface**: Command-line tool for terminal-based interactions
3. **🧪 API Interface**: Programmatic access for integration

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to the project
cd nvidia_ai_agent

# Run the setup script
./setup.sh

# Edit your environment variables
cp .env.template .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Launch Web Interface (Recommended)

```bash
# Start the web application
./run_web_app.sh

# Open your browser to: http://localhost:8501
```

### 3. Alternative: CLI Interface

```bash
# Activate environment
source venv/bin/activate

# Start interactive chat
python src/main.py chat

# Or ask a single question
python src/main.py ask -q "What is NVIDIA NIM?"

# Setup knowledge base
python src/main.py setup

# View agent statistics
python src/main.py stats
```

## 🏗️ Architecture

```
nvidia_ai_agent/
├── src/
│   ├── nvidia_agent.py          # Core conversational agent
│   ├── knowledge_base.py        # RAG knowledge base processor
│   ├── web_search_tool.py       # NVIDIA blog search functionality
│   └── main.py                  # CLI interface
├── streamlit_app.py             # Web interface application
├── tests/                       # Test suite
├── config/                      # Configuration files
├── data/                        # Knowledge base storage
└── docs/                        # Additional documentation
```

### 🔧 Core Components

1. **NVIDIA Conversational Agent** (`nvidia_agent.py`)
   - Main agent orchestration
   - Multi-source information synthesis
   - Conversation memory management
   - Response generation with source attribution

2. **Knowledge Base Processor** (`knowledge_base.py`)
   - Course transcript parsing and chunking
   - Vector embedding generation
   - ChromaDB vector database management
   - Semantic search capabilities

3. **Web Search Tool** (`web_search_tool.py`)
   - NVIDIA Developer Blog RSS monitoring
   - NVIDIA Blog content retrieval
   - Real-time article search and ranking
   - Content extraction and summarization

4. **Streamlit Web Interface** (`streamlit_app.py`)
   - Modern chat interface
   - Real-time conversation analytics
   - Source attribution and tracking
   - Conversation export capabilities

## 📊 Web Interface Features

### 💬 Chat Interface
- **Real-time Conversations**: Interactive chat with typing indicators
- **Source Attribution**: See which sources (Knowledge Base, NVIDIA Blogs) were used
- **Message Timestamps**: Track conversation flow
- **Quick Actions**: Preset questions for common topics

### 📈 Analytics Dashboard
- **Conversation Metrics**: Message counts, response times, source usage
- **Source Distribution**: Visual charts showing information source usage
- **Timeline Analysis**: Conversation flow and message length patterns
- **Export Functionality**: Download conversation history as JSON

### 🎛️ Control Panel
- **Agent Initialization**: One-click setup and configuration
- **Knowledge Base Status**: Real-time status of loaded documents
- **Conversation Management**: Clear history, export chats
- **Quick Topic Access**: Fast access to popular NVIDIA topics

### ❓ Help System
- **Interactive Guide**: Comprehensive usage instructions
- **Example Questions**: Categorized sample queries
- **Troubleshooting**: Common issues and solutions

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required: OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Optional: Agent Configuration
AGENT_NAME=NVIDIA AI Assistant
MAX_CONVERSATION_HISTORY=10

# Optional: Vector Database Configuration
CHROMADB_PERSIST_DIRECTORY=./data/chromadb
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional: Search Configuration
MAX_SEARCH_RESULTS=5
SEARCH_TIMEOUT=30
```

### Streamlit Configuration
The web interface uses custom NVIDIA-themed styling and is configured via `.streamlit/config.toml`:
- NVIDIA green color scheme (#76B900)
- Optimized for wide layouts
- Error reporting enabled for development
- CORS and XSRF protection for security

## 📚 Knowledge Sources

### 1. Course Transcripts (Local Knowledge Base)
- **Building RAG Agents with LLMs**: Comprehensive RAG implementation guide
- **Generative AI Explained**: Foundational generative AI concepts
- **Introduction to NVIDIA NIM**: Microservices architecture and deployment
- **Sizing LLM Inference Systems**: Performance optimization and scaling

### 2. Live Web Sources
- **NVIDIA Developer Blog**: Latest technical articles, tutorials, SDK updates
- **NVIDIA Blog**: Company announcements, industry insights, product releases

## 🧪 Usage Examples

### Web Interface Examples

1. **Getting Started**
   ```
   User: "What is NVIDIA NIM and how does it work?"
   
   Assistant: Based on the NVIDIA course materials, NIM (NVIDIA Inference 
   Microservices) is a set of containerized AI model inference services...
   [Sources: Knowledge Base - Introduction to NVIDIA NIM Microservices]
   ```

2. **Current Information**
   ```
   User: "What are the latest NVIDIA AI announcements?"
   
   Assistant: Here are the most recent NVIDIA AI developments I found:
   1. NVIDIA Announces New AI Supercomputing Platform...
   [Sources: NVIDIA Developer Blog, NVIDIA Blog]
   ```

### CLI Examples

```bash
# Interactive chat session
python src/main.py chat

# Single question mode
python src/main.py ask -q "Explain RAG system architecture" -v

# Test the agent functionality
python src/main.py test

# Get agent statistics
python src/main.py stats
```

### Programmatic Usage

```python
from src.nvidia_agent import NVIDIAConversationalAgent

# Initialize agent
agent = NVIDIAConversationalAgent()

# Process queries
response = agent.process_query("How do I optimize NIM performance?")

# Get conversation statistics
stats = agent.get_agent_stats()
```

## 🔍 Advanced Features

### Smart Query Routing
The agent intelligently determines information sources based on query analysis:
- **Current/Recent Keywords**: Routes to web search for latest information
- **Foundational Keywords**: Prioritizes knowledge base for educational content
- **Mixed Queries**: Combines both sources for comprehensive responses

### Conversation Analytics
Track and analyze conversation patterns:
- Source usage distribution
- Query complexity over time
- Response accuracy metrics
- User engagement patterns

### Memory Management
- **Short-term Memory**: Maintains context within conversations
- **Long-term Learning**: Adapts to user preferences and common queries
- **Context Windows**: Configurable conversation history limits

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
cd tests
python -m pytest test_agent.py -v

# Run specific test categories
python -m pytest test_agent.py::TestKnowledgeBase -v
python -m pytest test_agent.py::TestNVIDIAAgent -v
```

### Integration Tests
```bash
# Test with real knowledge base (requires setup)
python -m pytest test_agent.py::TestIntegration -v -m integration

# Test web search functionality (requires internet)
python -m pytest test_agent.py -v -k "web_search"
```

### Manual Testing
```bash
# Run built-in test suite
python src/main.py test

# Test knowledge base setup
python src/main.py setup

# Verify agent functionality
python src/nvidia_agent.py  # Runs built-in tests
```

## 📦 Dependencies

### Core Dependencies
- **agentiq**: NVIDIA NeMo Agent Toolkit for agent orchestration
- **langchain**: LLM framework and conversation memory
- **chromadb**: Vector database for knowledge base storage
- **sentence-transformers**: Text embedding generation
- **openai**: LLM API access

### Web Interface Dependencies
- **streamlit**: Modern web application framework
- **plotly**: Interactive analytics visualizations
- **pandas**: Data processing for analytics
- **streamlit-chat**: Enhanced chat interface components

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting and code quality

## 🚀 Deployment

### Local Development
```bash
# Development with auto-reload
streamlit run streamlit_app.py --server.runOnSave true

# Production-like local deployment
./run_web_app.sh
```

### Production Deployment

#### Docker Deployment (Recommended)
```dockerfile
# Create Dockerfile based on requirements.txt
# Include all project files and dependencies
# Set environment variables for production
# Expose port 8501 for Streamlit
```

#### Cloud Deployment Options
- **Streamlit Cloud**: Direct deployment from GitHub
- **Heroku**: Web app deployment with buildpack
- **AWS/GCP/Azure**: Container deployment with load balancing
- **NVIDIA NGC**: Deployment on NVIDIA's cloud platform

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run test suite
5. Submit pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings for all functions
- Include unit tests for new features
- Update documentation for changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Error: OpenAI API key not found
   Solution: Set OPENAI_API_KEY in your .env file
   ```

2. **Knowledge Base Setup Issues**
   ```
   Error: No transcript files found
   Solution: Ensure transcript files are in the correct directory structure
   ```

3. **Web Interface Not Loading**
   ```
   Error: Import errors in Streamlit
   Solution: Install all requirements with pip install -r requirements.txt
   ```

4. **ChromaDB Connection Issues**
   ```
   Error: Cannot connect to ChromaDB
   Solution: Clear data/chromadb directory and reinitialize
   ```

### Performance Optimization

1. **Slow Responses**
   - Adjust chunk size in knowledge base processing
   - Reduce MAX_SEARCH_RESULTS for faster web search
   - Use smaller embedding models for faster processing

2. **Memory Usage**
   - Reduce MAX_CONVERSATION_HISTORY
   - Clear conversation history regularly
   - Optimize ChromaDB persistence settings

## 🎯 Roadmap

### Upcoming Features
- [ ] **Multi-language Support**: Support for multiple languages
- [ ] **Voice Interface**: Speech-to-text and text-to-speech capabilities
- [ ] **Advanced Analytics**: Enhanced conversation insights and reporting
- [ ] **Custom Knowledge Sources**: Upload additional documents and sources
- [ ] **API Endpoints**: RESTful API for external integration
- [ ] **Enhanced Security**: Authentication and authorization features
- [ ] **NVIDIA API Integration**: Direct integration with NVIDIA's AI APIs

### Performance Improvements
- [ ] **Caching Layer**: Redis-based response caching
- [ ] **Async Processing**: Asynchronous query processing
- [ ] **Load Balancing**: Multi-instance deployment support
- [ ] **Database Optimization**: Advanced vector search optimization

---

## 📞 Support

For support, please:
1. Check the troubleshooting section above
2. Review the help documentation in the web interface
3. Create an issue on GitHub with detailed information
4. Include logs from the `logs/` directory when reporting issues

---

**Built with ❤️ using NVIDIA NeMo Agent Toolkit and Streamlit**
