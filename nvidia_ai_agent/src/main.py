#!/usr/bin/env python3
"""
Main CLI interface for the NVIDIA AI Conversational Agent.
This provides an interactive command-line interface to chat with the agent.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from nvidia_agent import NVIDIAConversationalAgent
from knowledge_base import KnowledgeBaseProcessor

# Load environment variables
load_dotenv()

# Setup rich console for better output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NVIDIAAgentCLI:
    """Command-line interface for the NVIDIA AI Agent."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.agent: Optional[NVIDIAConversationalAgent] = None
        self.console = Console()
    
    def display_welcome(self):
        """Display welcome message and instructions."""
        welcome_text = Text()
        welcome_text.append("🚀 NVIDIA AI Assistant", style="bold green")
        welcome_text.append("\\n\\nAn intelligent assistant specializing in NVIDIA technologies, powered by:")
        welcome_text.append("\\n• Course transcripts from NVIDIA AI courses")
        welcome_text.append("\\n• Live search of NVIDIA Developer Blog and NVIDIA Blog")
        welcome_text.append("\\n• Advanced RAG (Retrieval Augmented Generation) capabilities")
        
        welcome_text.append("\\n\\nAvailable Commands:", style="bold cyan")
        welcome_text.append("\\n/help    - Show available commands")
        welcome_text.append("\\n/stats   - Show agent statistics")
        welcome_text.append("\\n/recent  - Get recent NVIDIA news")
        welcome_text.append("\\n/history - Show conversation history")
        welcome_text.append("\\n/clear   - Clear conversation history")
        welcome_text.append("\\n/exit    - Exit the assistant")
        
        welcome_text.append("\\n\\nJust ask me anything about NVIDIA technologies!", style="bold yellow")
        
        self.console.print(Panel(welcome_text, title="Welcome", border_style="blue"))
    
    def initialize_agent(self) -> bool:
        """Initialize the NVIDIA agent with error handling."""
        try:
            self.console.print("🔧 Initializing NVIDIA AI Agent...", style="yellow")
            
            # Check for required API keys
            if not os.getenv('OPENAI_API_KEY'):
                self.console.print(
                    "❌ Error: OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.", 
                    style="red"
                )
                return False
            
            # Initialize the agent
            self.agent = NVIDIAConversationalAgent()
            
            # Get agent stats to verify initialization
            stats = self.agent.get_agent_stats()
            
            self.console.print("✅ Agent initialized successfully!", style="green")
            self.console.print(f"📚 Knowledge Base: {stats['knowledge_base_documents']} documents loaded", style="blue")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error initializing agent: {e}", style="red")
            logger.error(f"Agent initialization failed: {e}")
            return False
    
    def setup_knowledge_base(self) -> bool:
        """Set up the knowledge base if it doesn't exist."""
        try:
            kb_processor = KnowledgeBaseProcessor()
            
            # Check if knowledge base exists
            stats = kb_processor.get_collection_stats()
            if stats.get('total_documents', 0) == 0:
                self.console.print("📖 Setting up knowledge base from course transcripts...", style="yellow")
                
                # Process transcripts
                documents = kb_processor.process_all_transcripts("../")  # Go up to repo root
                
                if documents:
                    kb_processor.add_documents_to_knowledge_base(documents)
                    self.console.print(f"✅ Knowledge base created with {len(documents)} documents", style="green")
                else:
                    self.console.print("⚠️  No transcript files found. Agent will work with web search only.", style="yellow")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error setting up knowledge base: {e}", style="red")
            logger.error(f"Knowledge base setup failed: {e}")
            return False
    
    def process_user_input(self, user_input: str) -> bool:
        """Process user input and return whether to continue."""
        user_input = user_input.strip()
        
        # Handle exit commands
        if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
            return False
        
        # Handle empty input
        if not user_input:
            return True
        
        try:
            # Show thinking indicator
            with self.console.status("[bold green]Thinking..."):
                # Check for special commands
                special_response = self.agent.handle_special_commands(user_input)
                
                if special_response:
                    response = special_response
                else:
                    response = self.agent.process_query(user_input)
            
            # Display response in a nice panel
            response_panel = Panel(
                response,
                title="🤖 NVIDIA AI Assistant",
                title_align="left",
                border_style="green"
            )
            self.console.print(response_panel)
            
        except Exception as e:
            self.console.print(f"❌ Error processing query: {e}", style="red")
            logger.error(f"Query processing failed: {e}")
        
        return True
    
    def run_interactive_mode(self):
        """Run the interactive chat interface."""
        self.display_welcome()
        
        # Setup knowledge base
        if not self.setup_knowledge_base():
            return
        
        # Initialize agent
        if not self.initialize_agent():
            return
        
        self.console.print("\\n💬 Chat started! Type '/exit' to quit.\\n", style="bold cyan")
        
        # Main interaction loop
        while True:
            try:
                # Get user input with rich prompt
                user_input = Prompt.ask("\\n[bold blue]You[/bold blue]")
                
                # Process input
                should_continue = self.process_user_input(user_input)
                
                if not should_continue:
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\\n\\n👋 Goodbye!", style="bold yellow")
                break
            except EOFError:
                break
        
        # Show goodbye message
        self.console.print("\\n✨ Thank you for using NVIDIA AI Assistant!", style="bold green")


@click.group()
def cli():
    """NVIDIA AI Conversational Agent CLI."""
    pass


@cli.command()
def chat():
    """Start interactive chat with the NVIDIA AI Agent."""
    cli_app = NVIDIAAgentCLI()
    cli_app.run_interactive_mode()


@cli.command()
@click.option('--query', '-q', required=True, help='Query to ask the agent')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def ask(query: str, verbose: bool):
    """Ask a single question to the NVIDIA AI Agent."""
    try:
        console.print(f"🤖 Processing query: {query}", style="blue")
        
        # Initialize agent
        agent = NVIDIAConversationalAgent()
        
        # Get response
        response = agent.process_query(query)
        
        # Display response
        if verbose:
            stats = agent.get_agent_stats()
            console.print(f"📊 Knowledge Base: {stats['knowledge_base_documents']} documents", style="dim")
        
        console.print("\\n" + "="*60)
        console.print(response)
        console.print("="*60)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@cli.command()
def setup():
    """Set up the knowledge base from course transcripts."""
    try:
        console.print("🔧 Setting up NVIDIA AI Agent knowledge base...", style="yellow")
        
        # Process transcripts
        kb_processor = KnowledgeBaseProcessor()
        documents = kb_processor.process_all_transcripts("../")
        
        if documents:
            kb_processor.add_documents_to_knowledge_base(documents)
            console.print(f"✅ Knowledge base created with {len(documents)} documents", style="green")
        else:
            console.print("❌ No transcript files found", style="red")
            
    except Exception as e:
        console.print(f"❌ Setup failed: {e}", style="red")


@cli.command()
def stats():
    """Show agent statistics and capabilities."""
    try:
        agent = NVIDIAConversationalAgent()
        stats_info = agent.get_agent_stats()
        
        stats_text = Text()
        stats_text.append(f"Agent Name: {stats_info['agent_name']}\\n", style="bold")
        stats_text.append(f"Knowledge Base Documents: {stats_info['knowledge_base_documents']}\\n")
        stats_text.append(f"Conversation Exchanges: {stats_info['conversation_exchanges']}\\n")
        stats_text.append("\\nAvailable Sources:\\n", style="bold")
        for source in stats_info['sources_available']:
            stats_text.append(f"• {source}\\n")
        stats_text.append("\\nCapabilities:\\n", style="bold")
        for capability in stats_info['capabilities']:
            stats_text.append(f"• {capability}\\n")
        
        console.print(Panel(stats_text, title="Agent Statistics", border_style="blue"))
        
    except Exception as e:
        console.print(f"❌ Error getting stats: {e}", style="red")


@cli.command()
def test():
    """Run test queries to verify agent functionality."""
    test_queries = [
        "What is NVIDIA NIM?",
        "How does RAG work with LLMs?",
        "Tell me about generative AI",
        "What are the latest NVIDIA announcements?"
    ]
    
    try:
        console.print("🧪 Running agent tests...", style="yellow")
        agent = NVIDIAConversationalAgent()
        
        for i, query in enumerate(test_queries, 1):
            console.print(f"\\n[bold blue]Test {i}:[/bold blue] {query}")
            
            with console.status(f"[bold green]Processing test {i}..."):
                response = agent.process_query(query)
            
            # Show abbreviated response
            short_response = response[:200] + "..." if len(response) > 200 else response
            console.print(f"[green]Response:[/green] {short_response}\\n")
        
        console.print("✅ All tests completed!", style="green")
        
    except Exception as e:
        console.print(f"❌ Test failed: {e}", style="red")


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Run CLI
    cli()
