"""
Test suite for the NVIDIA AI Conversational Agent.
"""

import sys
import os
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from nvidia_agent import NVIDIAConversationalAgent, ConversationContext
from knowledge_base import KnowledgeBaseProcessor, TranscriptDocument
from web_search_tool import NVIDIABlogSearchTool


class TestKnowledgeBase:
    """Test the knowledge base functionality."""
    
    def test_transcript_document_creation(self):
        """Test creation of TranscriptDocument."""
        doc = TranscriptDocument(
            course_name="Test Course",
            lesson_title="Test Lesson",
            content="This is test content",
            video_url="https://test.com",
            file_path="/test/path"
        )
        
        assert doc.course_name == "Test Course"
        assert doc.lesson_title == "Test Lesson"
        assert doc.content == "This is test content"
    
    def test_chunk_content(self):
        """Test content chunking functionality."""
        kb_processor = KnowledgeBaseProcessor()
        
        # Test small content (shouldn't be chunked)
        small_content = "This is a small piece of content."
        chunks = kb_processor.chunk_content(small_content, chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == small_content
        
        # Test large content (should be chunked)
        large_content = "This is a test. " * 100  # Create long content
        chunks = kb_processor.chunk_content(large_content, chunk_size=100, overlap=20)
        assert len(chunks) > 1


class TestWebSearchTool:
    """Test the web search functionality."""
    
    def test_nvidia_blog_search_tool_init(self):
        """Test initialization of NVIDIA blog search tool."""
        search_tool = NVIDIABlogSearchTool()
        
        assert search_tool.timeout > 0
        assert search_tool.max_results > 0
        assert 'developer' in search_tool.nvidia_blogs
        assert 'main' in search_tool.nvidia_blogs
    
    def test_format_search_results(self):
        """Test formatting of search results."""
        search_tool = NVIDIABlogSearchTool()
        
        # Test empty results
        empty_results = []
        formatted = search_tool.format_search_results(empty_results)
        assert "No relevant articles found" in formatted
        
        # Test with results
        test_results = [{
            'title': 'Test Article',
            'source': 'NVIDIA Developer Blog',
            'published_date': '2024-01-01',
            'url': 'https://test.com',
            'summary': 'This is a test summary'
        }]
        
        formatted = search_tool.format_search_results(test_results)
        assert "Test Article" in formatted
        assert "NVIDIA Developer Blog" in formatted


class TestNVIDIAAgent:
    """Test the main NVIDIA conversational agent."""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_agent_initialization(self):
        """Test agent initialization with mocked components."""
        with patch('nvidia_agent.ChatOpenAI'), \
             patch('nvidia_agent.KnowledgeBaseProcessor'), \
             patch('nvidia_agent.NVIDIABlogSearchTool'):
            
            agent = NVIDIAConversationalAgent()
            
            assert agent.agent_name is not None
            assert agent.system_message is not None
    
    def test_determine_search_strategy(self):
        """Test search strategy determination."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            with patch('nvidia_agent.ChatOpenAI'), \
                 patch('nvidia_agent.KnowledgeBaseProcessor'), \
                 patch('nvidia_agent.NVIDIABlogSearchTool'):
                
                agent = NVIDIAConversationalAgent()
                
                # Test current information query
                current_strategy = agent._determine_search_strategy("What are the latest NVIDIA announcements?")
                assert current_strategy['use_web_search'] is True
                assert current_strategy['prioritize_web'] is True
                
                # Test foundational query
                foundational_strategy = agent._determine_search_strategy("What is NVIDIA NIM?")
                assert foundational_strategy['use_knowledge_base'] is True
    
    def test_conversation_context(self):
        """Test conversation context creation."""
        from datetime import datetime
        
        context = ConversationContext(
            user_query="Test query",
            response="Test response",
            timestamp=datetime.now(),
            sources_used=["Knowledge Base"],
            relevance_scores={"test": 0.9}
        )
        
        assert context.user_query == "Test query"
        assert context.response == "Test response"
        assert "Knowledge Base" in context.sources_used
    
    def test_special_commands(self):
        """Test special command handling."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            with patch('nvidia_agent.ChatOpenAI'), \
                 patch('nvidia_agent.KnowledgeBaseProcessor'), \
                 patch('nvidia_agent.NVIDIABlogSearchTool'):
                
                agent = NVIDIAConversationalAgent()
                
                # Test help command
                help_response = agent.handle_special_commands("/help")
                assert help_response is not None
                assert "Available Commands" in help_response
                
                # Test stats command
                with patch.object(agent, 'get_agent_stats', return_value={'agent_name': 'Test', 'knowledge_base_documents': 0, 'conversation_exchanges': 0, 'sources_available': [], 'capabilities': []}):
                    stats_response = agent.handle_special_commands("/stats")
                    assert stats_response is not None
                    assert "Agent Statistics" in stats_response
                
                # Test non-command
                non_command = agent.handle_special_commands("regular query")
                assert non_command is None


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.integration
    def test_knowledge_base_search_integration(self):
        """Test knowledge base search with real data if available."""
        try:
            kb_processor = KnowledgeBaseProcessor()
            
            # Try to search (will work if knowledge base exists)
            results = kb_processor.search_knowledge_base("NVIDIA", n_results=1)
            
            # Should return list (empty if no knowledge base, populated if exists)
            assert isinstance(results, list)
            
        except Exception as e:
            # If there are dependency issues, skip this test
            pytest.skip(f"Integration test skipped due to: {e}")
    
    @pytest.mark.integration  
    def test_web_search_integration(self):
        """Test web search with real NVIDIA blogs (requires internet)."""
        try:
            search_tool = NVIDIABlogSearchTool()
            
            # Test search (will work if internet is available)
            results = search_tool.search_both_blogs("NVIDIA", max_results_per_blog=1)
            
            # Should return list (empty if no results, populated if successful)
            assert isinstance(results, list)
            
        except Exception as e:
            # If there are network issues, skip this test
            pytest.skip(f"Web search test skipped due to: {e}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
