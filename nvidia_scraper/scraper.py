"""
NVIDIA Blog Scraper - Core scraping functionality
"""

import os
import re
import time
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import feedparser

console = Console()


class NVIDIABlogScraper:
    """Scraper for NVIDIA developer and corporate blogs."""
    
    def __init__(self, config_path: str = "scraper_config.yaml"):
        """Initialize the scraper with configuration."""
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self._setup_session()
        self._setup_logging()
        self.scraped_urls: Set[str] = set()
        self.base_output_dir = Path(self.config["output"]["base_directory"])
        self.base_output_dir.mkdir(exist_ok=True)
        self._load_scraped_urls()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            console.print(f"[red]Configuration file {config_path} not found![/red]")
            raise
        except yaml.YAMLError as e:
            console.print(f"[red]Error parsing configuration file: {e}[/red]")
            raise
    
    def _setup_session(self):
        """Setup requests session with headers and timeouts."""
        headers = {
            'User-Agent': self.config["scraping"]["user_agent"],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)
        self.session.timeout = self.config["scraping"]["timeout"]
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config["monitoring"]["log_level"].upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config["monitoring"]["log_file"]),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_scraped_urls(self):
        """Load previously scraped URLs to avoid duplicates."""
        scraped_file = self.base_output_dir / "scraped_urls.txt"
        if scraped_file.exists():
            with open(scraped_file, 'r') as f:
                self.scraped_urls = set(line.strip() for line in f if line.strip())
    
    def _save_scraped_url(self, url: str):
        """Save a scraped URL to avoid future duplicates."""
        scraped_file = self.base_output_dir / "scraped_urls.txt"
        with open(scraped_file, 'a') as f:
            f.write(f"{url}\n")
        self.scraped_urls.add(url)
    
    def _get_all_keywords(self) -> List[str]:
        """Get all keywords from all categories."""
        all_keywords = []
        for category_keywords in self.config["keywords"].values():
            all_keywords.extend([kw.lower() for kw in category_keywords])
        return all_keywords
    
    def _categorize_article(self, title: str, content: str) -> List[str]:
        """Categorize an article based on its title and content."""
        categories = []
        text = f"{title} {content}".lower()
        
        for category, keywords in self.config["keywords"].items():
            if any(keyword.lower() in text for keyword in keywords):
                categories.append(category)
        
        return categories if categories else ["general"]
    
    def _extract_rss_articles(self, rss_url: str) -> List[Tuple[str, str]]:
        """Extract article links from RSS/Atom feeds."""
        try:
            self.logger.info(f"Parsing RSS feed: {rss_url}")
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                self.logger.warning(f"RSS feed may have parsing issues: {rss_url}")
            
            article_links = []
            for entry in feed.entries:
                url = entry.get('link', '')
                title = entry.get('title', '')
                
                if url and title and self._is_relevant_article(title, url):
                    article_links.append((url, title))
            
            self.logger.info(f"Found {len(article_links)} relevant articles from RSS feed")
            return article_links
            
        except Exception as e:
            self.logger.error(f"Error parsing RSS feed {rss_url}: {e}")
            return []
    
    def _extract_article_links(self, url: str) -> List[Tuple[str, str]]:
        """Extract article links from a blog page."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            article_links = []
            
            # Different selectors for different NVIDIA blog sites
            if "developer.nvidia.com" in url:
                # Developer blog selectors
                article_selectors = [
                    'a[href*="/blog/"]',
                    '.post-card a',
                    '.blog-post a',
                    'h2 a',
                    'h3 a'
                ]
            else:
                # Corporate blog selectors
                article_selectors = [
                    'a[href*="/blog/"]',
                    '.post a',
                    '.entry-title a',
                    'h2 a',
                    'h3 a'
                ]
            
            for selector in article_selectors:
                links = soup.select(selector)
                for link in links:
                    if link.get('href'):
                        full_url = urljoin(url, link.get('href'))
                        title = link.get_text(strip=True) or link.get('title', '')
                        if title and self._is_relevant_article(title, full_url):
                            article_links.append((full_url, title))
            
            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link, title in article_links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append((link, title))
            
            return unique_links
            
        except Exception as e:
            self.logger.error(f"Error extracting links from {url}: {e}")
            return []
    
    def _is_relevant_article(self, title: str, url: str) -> bool:
        """Check if an article is relevant based on title and URL."""
        if url in self.scraped_urls:
            return False
            
        text = f"{title} {url}".lower()
        keywords = self._get_all_keywords()
        
        return any(keyword in text for keyword in keywords)
    
    def _extract_article_content(self, url: str) -> Optional[Dict]:
        """Extract content from a single article."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_selectors = ['h1.entry-title', 'h1.post-title', 'h1', '.entry-title', '.post-title']
            title = ""
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # Extract date
            date_selectors = [
                'time[datetime]',
                '.entry-date',
                '.post-date',
                '.published',
                '[class*="date"]'
            ]
            date_published = None
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                    try:
                        date_published = date_parser.parse(date_text)
                        break
                    except:
                        continue
            
            # Extract content
            content_selectors = [
                '.entry-content',
                '.post-content',
                '.article-content',
                'main article',
                '[class*="content"]'
            ]
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(["script", "style"]):
                        script.extract()
                    content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            # Extract author
            author_selectors = [
                '.author',
                '.by-author',
                '[class*="author"]',
                '.entry-author'
            ]
            author = ""
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    break
            
            if not title or not content:
                self.logger.warning(f"Could not extract complete content from {url}")
                return None
                
            return {
                'url': url,
                'title': title,
                'author': author,
                'date_published': date_published,
                'content': content,
                'categories': self._categorize_article(title, content),
                'scraped_at': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def _save_article(self, article: Dict):
        """Save an article to disk."""
        try:
            # Create filename from title
            safe_title = re.sub(r'[^\w\s-]', '', article['title'])
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            safe_title = safe_title.strip('-')[:100]  # Limit length
            
            # Add date prefix if available
            if article['date_published']:
                date_str = article['date_published'].strftime('%Y-%m-%d')
                filename = f"{date_str}_{safe_title}"
            else:
                filename = safe_title
            
            # Create category directories
            for category in article['categories']:
                category_dir = self.base_output_dir / category
                category_dir.mkdir(exist_ok=True)
                
                if self.config["output"]["article_format"] == "markdown":
                    filepath = category_dir / f"{filename}.md"
                    self._save_as_markdown(filepath, article)
                else:
                    filepath = category_dir / f"{filename}.txt"
                    self._save_as_text(filepath, article)
            
            self._save_scraped_url(article['url'])
            self.logger.info(f"Saved article: {article['title']}")
            
        except Exception as e:
            self.logger.error(f"Error saving article {article['title']}: {e}")
    
    def _save_as_markdown(self, filepath: Path, article: Dict):
        """Save article as markdown file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {article['title']}\n\n")
            f.write(f"**URL:** {article['url']}\n\n")
            if article['author']:
                f.write(f"**Author:** {article['author']}\n\n")
            if article['date_published']:
                f.write(f"**Published:** {article['date_published'].strftime('%Y-%m-%d')}\n\n")
            f.write(f"**Categories:** {', '.join(article['categories'])}\n\n")
            f.write(f"**Scraped:** {article['scraped_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("---\n\n")
            f.write(article['content'])
    
    def _save_as_text(self, filepath: Path, article: Dict):
        """Save article as text file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("-" * 100 + "\n")
            f.write(f"{article['title']}\n")
            f.write(f"URL: {article['url']}\n")
            if article['author']:
                f.write(f"Author: {article['author']}\n")
            if article['date_published']:
                f.write(f"Published: {article['date_published'].strftime('%Y-%m-%d')}\n")
            f.write(f"Categories: {', '.join(article['categories'])}\n")
            f.write(f"Scraped: {article['scraped_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write("-" * 100 + "\n")
            f.write(article['content'])
    
    def scrape_blog(self, max_articles: Optional[int] = None) -> int:
        """Main scraping function."""
        if max_articles is None:
            max_articles = self.config["output"]["max_articles_per_run"]
        
        console.print("[bold green]Starting NVIDIA Blog Scraping...[/bold green]")
        
        all_article_links = []
        
        # First try RSS feeds for efficiency
        if "rss_feeds" in self.config and self.config["rss_feeds"]:
            console.print("[bold blue]Collecting articles from RSS feeds...[/bold blue]")
            for rss_url in self.config["rss_feeds"]:
                console.print(f"Parsing RSS: {rss_url}")
                links = self._extract_rss_articles(rss_url)
                all_article_links.extend(links)
                time.sleep(self.config["scraping"]["delay_between_requests"])
        
        # Then fallback to scraping base URLs if needed
        console.print("[bold blue]Collecting additional articles from web pages...[/bold blue]")
        for base_url in self.config["base_urls"]:
            console.print(f"Scanning: {base_url}")
            links = self._extract_article_links(base_url)
            all_article_links.extend(links)
            time.sleep(self.config["scraping"]["delay_between_requests"])
        
        # Remove duplicates and filter out already scraped
        unique_links = []
        seen = set()
        for url, title in all_article_links:
            if url not in seen and url not in self.scraped_urls:
                seen.add(url)
                unique_links.append((url, title))
        
        # Limit articles if specified
        if max_articles and len(unique_links) > max_articles:
            unique_links = unique_links[:max_articles]
        
        console.print(f"[bold yellow]Found {len(unique_links)} new articles to scrape[/bold yellow]")
        
        if not unique_links:
            console.print("[bold green]No new articles to scrape![/bold green]")
            return 0
        
        # Scrape articles with progress bar
        articles_scraped = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Scraping articles...", total=len(unique_links))
            
            for url, title in unique_links:
                progress.update(task, description=f"Scraping: {title[:50]}...")
                
                article = self._extract_article_content(url)
                if article:
                    self._save_article(article)
                    articles_scraped += 1
                
                progress.advance(task)
                time.sleep(self.config["scraping"]["delay_between_requests"])
        
        console.print(f"[bold green]Successfully scraped {articles_scraped} articles![/bold green]")
        return articles_scraped
