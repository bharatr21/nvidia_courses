"""
Web search tool for NVIDIA Developer Blog and NVIDIA Blog.
This module provides functionality to search and retrieve current information from NVIDIA's official blogs.
"""

import re
import logging
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode, urlparse, parse_qs
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NVIDIABlogSearchTool:
    """Tool for searching NVIDIA Developer Blog and NVIDIA Blog for current information."""
    
    def __init__(self):
        """Initialize the NVIDIA blog search tool."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.timeout = int(os.getenv('SEARCH_TIMEOUT', 30))
        self.max_results = int(os.getenv('MAX_SEARCH_RESULTS', 5))
        
        # NVIDIA blog URLs and RSS feeds
        self.nvidia_blogs = {
            'developer': {
                'base_url': 'https://developer.nvidia.com',
                'blog_url': 'https://developer.nvidia.com/blog',
                'rss_feed': 'https://developer.nvidia.com/blog/feed',
                'search_url': 'https://developer.nvidia.com/search/site'
            },
            'main': {
                'base_url': 'https://blogs.nvidia.com',
                'blog_url': 'https://blogs.nvidia.com',
                'rss_feed': 'https://blogs.nvidia.com/feed',
                'search_url': 'https://blogs.nvidia.com/search'
            }
        }
    
    def search_nvidia_developer_blog(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """Search NVIDIA Developer Blog for relevant articles."""
        max_results = max_results or self.max_results
        results = []
        
        try:
            # First try RSS feed for recent articles
            logger.info(f"Searching NVIDIA Developer Blog for: {query}")
            
            # Parse RSS feed
            feed_url = self.nvidia_blogs['developer']['rss_feed']
            feed = feedparser.parse(feed_url)
            
            # Filter entries by query relevance
            for entry in feed.entries[:20]:  # Check recent 20 entries
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                content = f"{title} {summary}".lower()
                
                # Simple relevance check
                query_words = query.lower().split()
                relevance_score = sum(1 for word in query_words if word in content)
                
                if relevance_score > 0:
                    published = entry.get('published_parsed')
                    pub_date = datetime(*published[:6]) if published else datetime.now()
                    
                    results.append({
                        'title': title,
                        'url': entry.get('link', ''),
                        'summary': summary,
                        'published_date': pub_date.strftime('%Y-%m-%d'),
                        'source': 'NVIDIA Developer Blog',
                        'relevance_score': relevance_score
                    })
            
            # Sort by relevance and recency
            results.sort(key=lambda x: (x['relevance_score'], x['published_date']), reverse=True)
            
        except Exception as e:
            logger.error(f"Error searching NVIDIA Developer Blog: {e}")
        
        return results[:max_results]
    
    def search_nvidia_main_blog(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """Search NVIDIA main blog for relevant articles."""
        max_results = max_results or self.max_results
        results = []
        
        try:
            logger.info(f"Searching NVIDIA Main Blog for: {query}")
            
            # Parse RSS feed
            feed_url = self.nvidia_blogs['main']['rss_feed']
            feed = feedparser.parse(feed_url)
            
            # Filter entries by query relevance
            for entry in feed.entries[:20]:  # Check recent 20 entries
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                content = f"{title} {summary}".lower()
                
                # Simple relevance check
                query_words = query.lower().split()
                relevance_score = sum(1 for word in query_words if word in content)
                
                if relevance_score > 0:
                    published = entry.get('published_parsed')
                    pub_date = datetime(*published[:6]) if published else datetime.now()
                    
                    results.append({
                        'title': title,
                        'url': entry.get('link', ''),
                        'summary': summary,
                        'published_date': pub_date.strftime('%Y-%m-%d'),
                        'source': 'NVIDIA Blog',
                        'relevance_score': relevance_score
                    })
            
            # Sort by relevance and recency
            results.sort(key=lambda x: (x['relevance_score'], x['published_date']), reverse=True)
            
        except Exception as e:
            logger.error(f"Error searching NVIDIA Main Blog: {e}")
        
        return results[:max_results]
    
    def get_article_content(self, url: str) -> Optional[str]:
        """Extract full content from an NVIDIA blog article."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common content selectors for NVIDIA blogs
            content_selectors = [
                '.post-content',
                '.entry-content', 
                '.article-content',
                '.content',
                'main article',
                '.post-body'
            ]
            
            content = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator=' ', strip=True)
                    break
            
            if not content:
                # Fallback: get all paragraph text
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            return content[:2000] if content else None  # Limit content length
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def search_both_blogs(self, query: str, max_results_per_blog: int = 3) -> List[Dict[str, Any]]:
        """Search both NVIDIA Developer Blog and NVIDIA main blog."""
        all_results = []
        
        # Search developer blog
        dev_results = self.search_nvidia_developer_blog(query, max_results_per_blog)
        all_results.extend(dev_results)
        
        # Search main blog
        main_results = self.search_nvidia_main_blog(query, max_results_per_blog)
        all_results.extend(main_results)
        
        # Remove duplicates and sort by relevance
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        # Sort by relevance score and date
        unique_results.sort(key=lambda x: (x['relevance_score'], x['published_date']), reverse=True)
        
        return unique_results[:self.max_results]
    
    def search_with_content_extraction(self, query: str, extract_full_content: bool = False) -> List[Dict[str, Any]]:
        """Search blogs and optionally extract full content from top results."""
        results = self.search_both_blogs(query)
        
        if extract_full_content:
            for result in results[:2]:  # Only extract content for top 2 results
                full_content = self.get_article_content(result['url'])
                if full_content:
                    result['full_content'] = full_content
        
        return results
    
    def get_recent_nvidia_news(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent NVIDIA news from both blogs."""
        results = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            # Get from both RSS feeds
            for blog_type in ['developer', 'main']:
                feed_url = self.nvidia_blogs[blog_type]['rss_feed']
                feed = feedparser.parse(feed_url)
                
                source_name = 'NVIDIA Developer Blog' if blog_type == 'developer' else 'NVIDIA Blog'
                
                for entry in feed.entries:
                    published = entry.get('published_parsed')
                    if published:
                        pub_date = datetime(*published[:6])
                        if pub_date >= cutoff_date:
                            results.append({
                                'title': entry.get('title', ''),
                                'url': entry.get('link', ''),
                                'summary': entry.get('summary', ''),
                                'published_date': pub_date.strftime('%Y-%m-%d'),
                                'source': source_name,
                                'relevance_score': 1  # All are recent
                            })
            
            # Sort by date
            results.sort(key=lambda x: x['published_date'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting recent NVIDIA news: {e}")
        
        return results[:self.max_results]
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for display to the agent."""
        if not results:
            return "No relevant articles found in NVIDIA blogs."
        
        formatted_output = "Here are the most relevant NVIDIA blog articles:\\n\\n"
        
        for i, result in enumerate(results, 1):
            formatted_output += f"{i}. **{result['title']}**\\n"
            formatted_output += f"   Source: {result['source']}\\n"
            formatted_output += f"   Published: {result['published_date']}\\n"
            formatted_output += f"   URL: {result['url']}\\n"
            formatted_output += f"   Summary: {result['summary'][:200]}...\\n"
            
            if 'full_content' in result:
                formatted_output += f"   Content: {result['full_content'][:300]}...\\n"
            
            formatted_output += "\\n"
        
        return formatted_output


def main():
    """Test the NVIDIA blog search tool."""
    search_tool = NVIDIABlogSearchTool()
    
    # Test searches
    test_queries = [
        "NVIDIA NIM microservices",
        "RAG retrieval augmented generation",
        "generative AI"
    ]
    
    for query in test_queries:
        print(f"\\n{'='*50}")
        print(f"Testing search for: {query}")
        print('='*50)
        
        results = search_tool.search_with_content_extraction(query, extract_full_content=False)
        formatted_results = search_tool.format_search_results(results)
        print(formatted_results)
        
        # Test recent news
        print(f"\\n{'='*50}")
        print("Recent NVIDIA News (last 7 days)")
        print('='*50)
        
        recent_results = search_tool.get_recent_nvidia_news(7)
        formatted_recent = search_tool.format_search_results(recent_results)
        print(formatted_recent)
        break  # Only test first query for demo


if __name__ == "__main__":
    main()
