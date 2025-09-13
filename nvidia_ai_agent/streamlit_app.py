#!/usr/bin/env python3
"""
Streamlit Web Application for NVIDIA AI Conversational Agent.
A modern, interactive web interface for chatting with the NVIDIA AI Agent.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_chat import message
import pandas as pd
import glob
import time

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from nvidia_agent import NVIDIAConversationalAgent
    from knowledge_base import KnowledgeBaseProcessor
    from web_search_tool import NVIDIABlogSearchTool
    from cloud_webhook_handler import cloud_webhook_handler
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please make sure all dependencies are installed and the project is set up correctly.")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="NVIDIA AI Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #76B900, #00A86B);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-stats {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #76B900;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 5px solid #9c27b0;
    }
    
    .source-badge {
        background-color: #76B900;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .stButton > button {
        background-color: #76B900;
        color: white;
        border: none;
        border-radius: 5px;
    }
    
    .stButton > button:hover {
        background-color: #5a8a00;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitNVIDIAAgent:
    """Streamlit wrapper for the NVIDIA AI Agent."""
    
    def __init__(self):
        """Initialize the Streamlit agent wrapper."""
        self.agent = None
        self.kb_processor = None
        self.web_search_tool = None
    
    def initialize_components(self):
        """Initialize all components with error handling."""
        try:
            # Check API key
            if not os.getenv('OPENAI_API_KEY'):
                st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
                return False
            
            # Initialize components
            if self.agent is None:
                with st.spinner("🔧 Initializing NVIDIA AI Agent..."):
                    self.agent = NVIDIAConversationalAgent()
                    self.kb_processor = KnowledgeBaseProcessor()
                    self.web_search_tool = NVIDIABlogSearchTool()
                
                st.success("✅ NVIDIA AI Agent initialized successfully!")
                return True
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error initializing agent: {e}")
            logger.error(f"Agent initialization failed: {e}")
            return False
    
    def setup_knowledge_base(self):
        """Set up knowledge base if needed."""
        try:
            if self.kb_processor:
                stats = self.kb_processor.get_collection_stats()
                if stats.get('total_documents', 0) == 0:
                    with st.spinner("📖 Setting up knowledge base from course transcripts..."):
                        documents = self.kb_processor.process_all_transcripts("./")
                        if documents:
                            self.kb_processor.add_documents_to_knowledge_base(documents)
                            st.success(f"✅ Knowledge base created with {len(documents)} documents")
                            return len(documents)
                        else:
                            st.warning("⚠️ No transcript files found. Agent will work with web search only.")
                            return 0
                else:
                    return stats.get('total_documents', 0)
            return 0
        except Exception as e:
            st.error(f"❌ Error setting up knowledge base: {e}")
            return 0


def check_webhook_events():
    """Check for new webhook events and update session state (cloud-compatible)."""
    try:
        # Check if we need to update (avoid checking too frequently)
        current_time = time.time()
        if current_time - st.session_state.last_webhook_check < 86400:  # Check once per day (86400 seconds)
            return
        
        st.session_state.last_webhook_check = current_time
        
        # Use cloud-compatible webhook handler
        recent_events = cloud_webhook_handler.get_webhook_events()
        
        # Update session state if we have new events
        if recent_events != st.session_state.webhook_events:
            st.session_state.webhook_events = recent_events
            
            # Show notification for new events
            new_events = [e for e in recent_events if e not in st.session_state.get('seen_events', [])]
            for event in new_events:
                if event.get('status') == 'success':
                    st.sidebar.success(f"🔔 New blog post: {event['title'][:50]}...")
                else:
                    st.sidebar.error(f"❌ Webhook error: {event.get('error', 'Unknown')}")
            
            st.session_state.seen_events = recent_events.copy()
            
    except Exception as e:
        pass  # Silently handle errors


def display_webhook_status():
    """Display webhook status for both local and cloud deployments."""
    try:
        # Display cloud-specific webhook setup if in cloud
        cloud_webhook_handler.display_cloud_webhook_setup()
        
        # If not in cloud, show local webhook server status
        if not os.getenv('STREAMLIT_CLOUD', 'false').lower() == 'true':
            import requests
            webhook_port = os.getenv('WEBHOOK_PORT', '5000')
            try:
                response = requests.get(f"http://localhost:{webhook_port}/health", timeout=2)
                if response.status_code == 200:
                    st.sidebar.success(f"🔗 Webhook server running on port {webhook_port}")
                    
                    # Show webhook URL for Zapier
                    webhook_url = f"http://localhost:{webhook_port}/webhook/nvidia-blog"
                    public_url = os.getenv('WEBHOOK_PUBLIC_URL')
                    if public_url:
                        webhook_url = public_url.replace(':5000', f':{webhook_port}') + '/webhook/nvidia-blog'
                    
                    with st.sidebar.expander("📡 Webhook Info"):
                        st.code(webhook_url)
                        st.caption("Use this URL in Zapier webhook")
                else:
                    st.sidebar.warning("🔗 Webhook server not responding")
            except requests.RequestException:
                st.sidebar.info("🔗 Webhook server not running")
                st.sidebar.caption("Start with: python src/webhook_server.py")
        
        # Display recent webhook events
        if st.session_state.webhook_events:
            with st.sidebar.expander(f"📬 Recent Events ({len(st.session_state.webhook_events)})"):
                for event in st.session_state.webhook_events[-5:]:
                    status_icon = "✅" if event.get('status') == 'success' else "❌"
                    st.markdown(f"{status_icon} **{event.get('title', 'Unknown')[:30]}...**")
                    st.caption(f"{event.get('source', 'Unknown')} - {event.get('processed_at', '')[:16]}")
                    if event.get('status') == 'error':
                        st.error(f"Error: {event.get('error', 'Unknown error')}")
    
    except Exception:
        pass  # Silently handle errors


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'agent_wrapper' not in st.session_state:
        st.session_state.agent_wrapper = StreamlitNVIDIAAgent()
    
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    
    if 'kb_documents' not in st.session_state:
        st.session_state.kb_documents = 0
    
    if 'conversation_stats' not in st.session_state:
        st.session_state.conversation_stats = {
            'total_queries': 0,
            'sources_used': {},
            'topics_discussed': []
        }
    
    if 'webhook_events' not in st.session_state:
        st.session_state.webhook_events = []
    
    if 'last_webhook_check' not in st.session_state:
        st.session_state.last_webhook_check = 0


def display_header():
    """Display the main application header."""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 NVIDIA AI Assistant</h1>
        <p>Your intelligent guide to NVIDIA technologies, powered by RAG and live web search</p>
    </div>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Display the application sidebar with controls and stats."""
    with st.sidebar:
        st.header("🎛️ Agent Control Panel")
        
        # Agent initialization
        if not st.session_state.agent_initialized:
            if st.button("🚀 Initialize Agent", type="primary"):
                if st.session_state.agent_wrapper.initialize_components():
                    st.session_state.kb_documents = st.session_state.agent_wrapper.setup_knowledge_base()
                    st.session_state.agent_initialized = True
                    st.rerun()
        else:
            st.success("✅ Agent Ready")
            
            # Agent statistics
            if st.session_state.agent_wrapper.agent:
                stats = st.session_state.agent_wrapper.agent.get_agent_stats()
                
                st.markdown("### 📊 Agent Statistics")
                st.markdown(f"""
                <div class="agent-stats">
                    <strong>Knowledge Base:</strong> {st.session_state.kb_documents} documents<br>
                    <strong>Conversations:</strong> {len(st.session_state.messages) // 2}<br>
                    <strong>Total Queries:</strong> {st.session_state.conversation_stats['total_queries']}<br>
                    <strong>Capabilities:</strong> {len(stats.get('capabilities', []))}
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick actions
        st.header("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📰 Recent News"):
                if st.session_state.agent_initialized:
                    add_sample_query("What are the latest NVIDIA announcements?")
        
        with col2:
            if st.button("🔍 About NIM"):
                if st.session_state.agent_initialized:
                    add_sample_query("What is NVIDIA NIM and how does it work?")
        
        if st.button("🤖 About RAG"):
            if st.session_state.agent_initialized:
                add_sample_query("Explain Retrieval Augmented Generation")
        
        if st.button("💡 Gen AI Basics"):
            if st.session_state.agent_initialized:
                add_sample_query("Tell me about generative AI fundamentals")
        
        st.divider()
        
        # Conversation management
        st.header("💬 Conversation")
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            if st.session_state.agent_wrapper.agent:
                st.session_state.agent_wrapper.agent.conversation_history.clear()
                st.session_state.agent_wrapper.agent.memory.clear()
            st.session_state.conversation_stats = {
                'total_queries': 0,
                'sources_used': {},
                'topics_discussed': []
            }
            st.rerun()
        
        # Export conversation
        if st.session_state.messages and st.button("📥 Export Chat"):
            export_conversation()
        
        st.divider()
        
        # Display webhook status
        display_webhook_status()
        
        st.divider()
        
        # Display sources used
        if st.session_state.conversation_stats['sources_used']:
            st.header("📚 Sources Used")
            for source, count in st.session_state.conversation_stats['sources_used'].items():
                st.markdown(f"""
                <span class="source-badge">{source}: {count}</span>
                """, unsafe_allow_html=True)


def add_sample_query(query: str):
    """Add a sample query to the chat."""
    st.session_state.messages.append({"role": "user", "content": query, "timestamp": datetime.now()})
    st.rerun()


def export_conversation():
    """Export conversation history."""
    if st.session_state.messages:
        conversation_data = {
            'timestamp': datetime.now().isoformat(),
            'total_messages': len(st.session_state.messages),
            'conversation': st.session_state.messages,
            'stats': st.session_state.conversation_stats
        }
        
        st.download_button(
            label="📥 Download Conversation",
            data=json.dumps(conversation_data, indent=2, default=str),
            file_name=f"nvidia_ai_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def display_chat_interface():
    """Display the main chat interface."""
    st.header("💬 Chat with NVIDIA AI Assistant")
    
    if not st.session_state.agent_initialized:
        st.info("👆 Please initialize the agent using the sidebar control panel first.")
        return
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display conversation history
        for i, message_data in enumerate(st.session_state.messages):
            with st.chat_message(message_data["role"]):
                st.write(message_data["content"])
                
                # Show timestamp and sources if available
                if "timestamp" in message_data:
                    st.caption(f"🕒 {message_data['timestamp'].strftime('%H:%M:%S')}")
                
                if "sources" in message_data and message_data["sources"]:
                    st.caption("📚 Sources: " + ", ".join(message_data["sources"]))
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about NVIDIA technologies..."):
        # Add user message
        user_message = {
            "role": "user", 
            "content": prompt, 
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(f"🕒 {user_message['timestamp'].strftime('%H:%M:%S')}")
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Get response from agent
                    response = st.session_state.agent_wrapper.agent.process_query(prompt)
                    
                    # Get conversation context for sources
                    sources_used = []
                    if st.session_state.agent_wrapper.agent.conversation_history:
                        last_context = st.session_state.agent_wrapper.agent.conversation_history[-1]
                        sources_used = last_context.sources_used
                    
                    # Display response
                    st.write(response)
                    
                    # Update statistics
                    st.session_state.conversation_stats['total_queries'] += 1
                    for source in sources_used:
                        if source in st.session_state.conversation_stats['sources_used']:
                            st.session_state.conversation_stats['sources_used'][source] += 1
                        else:
                            st.session_state.conversation_stats['sources_used'][source] = 1
                    
                    # Add assistant message to history
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now(),
                        "sources": sources_used
                    }
                    st.session_state.messages.append(assistant_message)
                    
                    # Show sources and timestamp
                    st.caption(f"🕒 {assistant_message['timestamp'].strftime('%H:%M:%S')}")
                    if sources_used:
                        st.caption("📚 Sources: " + ", ".join(sources_used))
                    
                except Exception as e:
                    st.error(f"❌ Error generating response: {e}")
                    logger.error(f"Response generation failed: {e}")


def display_analytics_tab():
    """Display analytics and insights about the conversation."""
    st.header("📊 Conversation Analytics")
    
    if not st.session_state.messages:
        st.info("Start a conversation to see analytics!")
        return
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Messages", len(st.session_state.messages))
    
    with col2:
        st.metric("User Queries", len([m for m in st.session_state.messages if m["role"] == "user"]))
    
    with col3:
        st.metric("Assistant Responses", len([m for m in st.session_state.messages if m["role"] == "assistant"]))
    
    with col4:
        total_sources = sum(st.session_state.conversation_stats['sources_used'].values())
        st.metric("Sources Used", total_sources)
    
    # Sources usage chart
    if st.session_state.conversation_stats['sources_used']:
        st.subheader("📚 Sources Usage Distribution")
        
        sources_df = pd.DataFrame(
            list(st.session_state.conversation_stats['sources_used'].items()),
            columns=['Source', 'Usage Count']
        )
        
        fig = px.pie(
            sources_df, 
            values='Usage Count', 
            names='Source',
            title="Information Sources Used in Conversation"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Conversation timeline
    if len(st.session_state.messages) > 2:
        st.subheader("⏱️ Conversation Timeline")
        
        timeline_data = []
        for msg in st.session_state.messages:
            if "timestamp" in msg:
                timeline_data.append({
                    'Time': msg['timestamp'],
                    'Role': msg['role'].title(),
                    'Message Length': len(msg['content'])
                })
        
        if timeline_data:
            timeline_df = pd.DataFrame(timeline_data)
            
            fig = px.scatter(
                timeline_df,
                x='Time',
                y='Message Length',
                color='Role',
                title="Message Length Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)


def display_help_tab():
    """Display help and usage information."""
    st.header("❓ Help & Usage Guide")
    
    st.markdown("""
    ## Welcome to NVIDIA AI Assistant! 🚀
    
    This intelligent assistant specializes in NVIDIA technologies and can help you with:
    
    ### 🎯 What I Can Help With:
    - **NVIDIA NIM (Inference Microservices)**: Architecture, deployment, use cases
    - **Generative AI & LLMs**: Concepts, applications, best practices  
    - **RAG Systems**: Retrieval Augmented Generation implementation
    - **NVIDIA AI Frameworks**: Tools, SDKs, and development platforms
    - **GPU Computing**: Acceleration, optimization, performance tuning
    - **Enterprise AI Solutions**: Deployment strategies, scaling considerations
    
    ### 📚 Knowledge Sources:
    1. **Course Transcripts**: Comprehensive educational content from NVIDIA courses
    2. **NVIDIA Developer Blog**: Latest technical articles and tutorials
    3. **NVIDIA Blog**: Recent announcements and industry insights
    
    ### 💬 How to Use:
    1. **Initialize the Agent**: Click "Initialize Agent" in the sidebar
    2. **Ask Questions**: Type your questions in the chat input
    3. **Use Quick Actions**: Try the preset questions in the sidebar
    4. **View Analytics**: Check the Analytics tab for conversation insights
    
    ### 🔧 Special Commands:
    - `/help` - Show available commands
    - `/stats` - Display agent statistics
    - `/recent` - Get recent NVIDIA news
    - `/history` - Show conversation history
    - `/clear` - Clear conversation memory
    
    ### 📝 Example Questions:
    """)
    
    # Example questions in expandable sections
    with st.expander("🤖 About NVIDIA NIM"):
        st.code("""
        • What is NVIDIA NIM and how does it work?
        • How do I deploy NIM microservices?
        • What are the benefits of using NIM for AI inference?
        • Can you compare NIM with other inference solutions?
        """)
    
    with st.expander("🧠 Generative AI & RAG"):
        st.code("""
        • Explain Retrieval Augmented Generation
        • How do I build a RAG system with NVIDIA tools?
        • What are the best practices for RAG evaluation?
        • How does embedding work in RAG systems?
        """)
    
    with st.expander("🚀 Latest NVIDIA News"):
        st.code("""
        • What are the latest NVIDIA announcements?
        • Tell me about recent NVIDIA AI developments
        • What's new in NVIDIA's AI platform?
        • Recent updates in NVIDIA developer tools?
        """)
    
    st.markdown("""
    ### 🔑 Setup Requirements:
    - **OpenAI API Key**: Required for LLM responses
    - **Internet Connection**: For web search capabilities
    - **Course Transcripts**: Automatically loaded from repository
    
    ### 🆘 Need Help?
    If you encounter any issues:
    1. Check that your OpenAI API key is set correctly
    2. Ensure internet connectivity for web search
    3. Try reinitializing the agent
    4. Clear conversation history and restart
    """)


def main():
    """Main Streamlit application."""
    # Initialize session state
    initialize_session_state()
    
    # Check for webhook events
    check_webhook_events()
    
    # Display header
    display_header()
    
    # Create main tabs
    main_tab, analytics_tab, help_tab = st.tabs(["💬 Chat", "📊 Analytics", "❓ Help"])
    
    with main_tab:
        # Create columns for main content and sidebar
        col1, col2 = st.columns([3, 1])
        
        with col1:
            display_chat_interface()
        
        with col2:
            # This will be empty since we use the actual sidebar
            pass
    
    with analytics_tab:
        display_analytics_tab()
    
    with help_tab:
        display_help_tab()
    
    # Display sidebar (always visible)
    display_sidebar()


if __name__ == "__main__":
    main()
