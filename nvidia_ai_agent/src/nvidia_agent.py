"""
NVIDIA AI Conversational Agent with RAG and Web Search capabilities.
This is the core agent that combines knowledge base retrieval with live web search.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

from dotenv import load_dotenv
from knowledge_base import KnowledgeBaseProcessor
from web_search_tool import NVIDIABlogSearchTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Represents the context of a conversation."""
    user_query: str
    response: str
    timestamp: datetime
    sources_used: List[str]
    relevance_scores: Dict[str, float]


class NVIDIAConversationalAgent:
    """
    NVIDIA AI Conversational Agent that can answer questions about NVIDIA using
    both local knowledge base (course transcripts) and live web search.
    """
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the NVIDIA conversational agent."""
        
        # Setup API keys
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Initialize components
        self.llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model=os.getenv('OPENAI_MODEL', 'gpt-4'),
            temperature=0.7,
            max_tokens=1500
        )
        
        # Initialize knowledge base and web search
        self.knowledge_base = KnowledgeBaseProcessor()
        self.web_search_tool = NVIDIABlogSearchTool()
        
        # Initialize conversation memory
        self.memory = ConversationBufferWindowMemory(
            k=int(os.getenv('MAX_CONVERSATION_HISTORY', 10)),
            return_messages=True
        )
        
        # Conversation context
        self.conversation_history: List[ConversationContext] = []
        
        # Agent configuration
        self.agent_name = os.getenv('AGENT_NAME', 'NVIDIA AI Assistant')
        
        # System message for the agent
        self.system_message = self._create_system_message()
        
        logger.info(f"Initialized {self.agent_name}")
    
    def _create_system_message(self) -> str:
        """Create the system message that defines the agent's behavior."""
        return f\"\"\"You are the {self.agent_name}, a knowledgeable AI assistant specializing in NVIDIA technologies, products, and services.

Your primary expertise includes:
- NVIDIA NIM (NVIDIA Inference Microservices)
- Generative AI and Large Language Models
- Retrieval Augmented Generation (RAG) systems
- NVIDIA AI frameworks and tools
- GPU computing and acceleration
- NVIDIA's enterprise AI solutions

You have access to two main sources of information:
1. A comprehensive knowledge base built from NVIDIA course transcripts and educational materials
2. Live search capabilities for NVIDIA's official blogs and recent announcements

Guidelines for responses:
- Always be accurate and cite your sources
- When using course transcript information, mention the specific course and lesson
- When using web search results, provide URLs and publication dates
- If you're unsure about current information, use web search to find the latest details
- Maintain a helpful, professional, and knowledgeable tone
- Focus specifically on NVIDIA-related topics
- If asked about non-NVIDIA topics, politely redirect to NVIDIA-relevant aspects

Remember: You are representing NVIDIA's knowledge and expertise, so maintain high standards of accuracy and professionalism.\"\"\"
    
    def search_knowledge_base(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search the local knowledge base for relevant information."""
        logger.info(f"Searching knowledge base for: {query}")
        return self.knowledge_base.search_knowledge_base(query, n_results)
    
    def search_web(self, query: str, extract_content: bool = False) -> List[Dict[str, Any]]:
        """Search NVIDIA blogs for current information."""
        logger.info(f"Searching NVIDIA blogs for: {query}")
        return self.web_search_tool.search_with_content_extraction(query, extract_content)
    
    def get_recent_nvidia_news(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent NVIDIA news and announcements."""
        logger.info(f"Getting recent NVIDIA news from last {days} days")
        return self.web_search_tool.get_recent_nvidia_news(days)
    
    def _format_knowledge_base_results(self, results: List[Dict[str, Any]]) -> str:
        """Format knowledge base search results for the LLM."""
        if not results:
            return "No relevant information found in the knowledge base."
        
        formatted = "Knowledge Base Results:\\n\\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. Course: {result['course_name']}\\n"
            formatted += f"   Lesson: {result['lesson_title']}\\n"
            formatted += f"   Relevance: {result['relevance_score']:.3f}\\n"
            formatted += f"   Content: {result['content']}\\n\\n"
        
        return formatted
    
    def _format_web_results(self, results: List[Dict[str, Any]]) -> str:
        """Format web search results for the LLM."""
        if not results:
            return "No relevant articles found in NVIDIA blogs."
        
        formatted = "Recent NVIDIA Blog Articles:\\n\\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\\n"
            formatted += f"   Source: {result['source']}\\n"
            formatted += f"   Published: {result['published_date']}\\n"
            formatted += f"   URL: {result['url']}\\n"
            formatted += f"   Summary: {result['summary']}\\n"
            if 'full_content' in result:
                formatted += f"   Content: {result['full_content']}\\n"
            formatted += "\\n"
        
        return formatted
    
    def _determine_search_strategy(self, query: str) -> Dict[str, bool]:
        """Determine whether to use knowledge base, web search, or both based on the query."""
        query_lower = query.lower()
        
        # Keywords that suggest current/recent information needed
        current_keywords = ['latest', 'recent', 'new', 'current', 'today', 'now', '2024', '2025', 'announcement']
        
        # Keywords that suggest foundational knowledge
        foundational_keywords = ['what is', 'how does', 'explain', 'basics', 'fundamentals', 'course', 'learn']
        
        needs_current = any(keyword in query_lower for keyword in current_keywords)
        needs_foundational = any(keyword in query_lower for keyword in foundational_keywords)
        
        return {
            'use_knowledge_base': True,  # Always search knowledge base first
            'use_web_search': needs_current or not needs_foundational,  # Use web search for current info
            'prioritize_web': needs_current  # Prioritize web results if current info is needed
        }
    
    def process_query(self, query: str) -> str:
        """Process a user query and generate a comprehensive response."""
        logger.info(f"Processing query: {query}")
        
        # Determine search strategy
        strategy = self._determine_search_strategy(query)
        
        # Collect information from sources
        knowledge_results = []
        web_results = []
        sources_used = []
        
        # Search knowledge base
        if strategy['use_knowledge_base']:
            knowledge_results = self.search_knowledge_base(query)
            if knowledge_results:
                sources_used.append("Knowledge Base")
        
        # Search web if needed
        if strategy['use_web_search']:
            web_results = self.search_web(query, extract_content=True)
            if web_results:
                sources_used.append("NVIDIA Blogs")
        
        # Format context for the LLM
        context_parts = []
        
        if knowledge_results:
            context_parts.append(self._format_knowledge_base_results(knowledge_results))
        
        if web_results:
            context_parts.append(self._format_web_results(web_results))
        
        context = "\\n".join(context_parts) if context_parts else "No relevant information found."
        
        # Create the prompt
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=f\"\"\"User Query: {query}

Available Information:
{context}

Please provide a comprehensive and accurate response based on the available information. If you use specific sources, please cite them appropriately.\"\"\")
        ]
        
        # Get response from LLM
        try:
            response = self.llm(messages)
            response_text = response.content
            
            # Store conversation context
            conversation_ctx = ConversationContext(
                user_query=query,
                response=response_text,
                timestamp=datetime.now(),
                sources_used=sources_used,
                relevance_scores={}  # Could be enhanced with actual scores
            )
            self.conversation_history.append(conversation_ctx)
            
            # Update memory
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(response_text)
            
            logger.info(f"Generated response using sources: {sources_used}")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your query. Please try again."
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation history."""
        if not self.conversation_history:
            return "No conversation history available."
        
        summary = f"Conversation Summary ({len(self.conversation_history)} exchanges):\\n\\n"
        
        for i, ctx in enumerate(self.conversation_history[-5:], 1):  # Show last 5
            summary += f"{i}. Query: {ctx.user_query[:100]}...\\n"
            summary += f"   Sources: {', '.join(ctx.sources_used)}\\n"
            summary += f"   Time: {ctx.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\\n\\n"
        
        return summary
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent's knowledge base and performance."""
        kb_stats = self.knowledge_base.get_collection_stats()
        
        return {
            'agent_name': self.agent_name,
            'knowledge_base_documents': kb_stats.get('total_documents', 0),
            'conversation_exchanges': len(self.conversation_history),
            'sources_available': ['Knowledge Base (Course Transcripts)', 'NVIDIA Developer Blog', 'NVIDIA Blog'],
            'capabilities': [
                'Course transcript search',
                'Live NVIDIA blog search', 
                'Conversation memory',
                'Multi-source information synthesis'
            ]
        }
    
    def handle_special_commands(self, query: str) -> Optional[str]:
        """Handle special commands like /help, /stats, etc."""
        query = query.strip().lower()
        
        if query == '/help':
            return \"\"\"NVIDIA AI Assistant - Available Commands:
            
/help - Show this help message
/stats - Show agent statistics and capabilities  
/recent - Get recent NVIDIA news (last 7 days)
/history - Show conversation summary
/clear - Clear conversation history

You can ask me about:
- NVIDIA NIM microservices
- Generative AI and LLMs
- RAG (Retrieval Augmented Generation)
- NVIDIA AI frameworks and tools
- GPU computing and acceleration
- NVIDIA enterprise solutions

Just ask your question naturally!\"\"\"
        
        elif query == '/stats':
            stats = self.get_agent_stats()
            return f\"\"\"Agent Statistics:
- Name: {stats['agent_name']}
- Knowledge Base: {stats['knowledge_base_documents']} documents
- Conversation Exchanges: {stats['conversation_exchanges']}
- Available Sources: {', '.join(stats['sources_available'])}
- Capabilities: {', '.join(stats['capabilities'])}\"\"\"
        
        elif query == '/recent':
            recent_news = self.get_recent_nvidia_news()
            return self.web_search_tool.format_search_results(recent_news)
        
        elif query == '/history':
            return self.get_conversation_summary()
        
        elif query == '/clear':
            self.conversation_history.clear()
            self.memory.clear()
            return "Conversation history cleared."
        
        return None


def main():
    """Test the NVIDIA conversational agent."""
    try:
        # Initialize agent
        agent = NVIDIAConversationalAgent()
        
        # Test queries
        test_queries = [
            "What is NVIDIA NIM and how does it work?",
            "Tell me about RAG systems and how they're used with LLMs",
            "What are the latest NVIDIA announcements?",
            "/stats"
        ]
        
        print(f"\\n{'='*60}")
        print(f"Testing {agent.agent_name}")
        print('='*60)
        
        for query in test_queries:
            print(f"\\nUser: {query}")
            print("-" * 40)
            
            # Handle special commands
            special_response = agent.handle_special_commands(query)
            if special_response:
                response = special_response
            else:
                response = agent.process_query(query)
            
            print(f"Assistant: {response}")
            print("\\n" + "="*60)
            
    except Exception as e:
        logger.error(f"Error testing agent: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
