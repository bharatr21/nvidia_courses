"""
Agno-compatible NVIDIA blog search tools.
Provides search capabilities for NVIDIA Developer Blog and NVIDIA Blog.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import feedparser
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv()

@dataclass
class BlogResult:
    title: str
    url: str
    summary: str
    published_date: str
    source: str
    relevance_score: float
    full_content: Optional[str] = None


class NVIDIABlogTool:
    """Search NVIDIA blogs and return structured results."""

    def __init__(self):
        self.max_results = int(os.getenv('MAX_SEARCH_RESULTS', 8))
        self.timeout = int(os.getenv('SEARCH_TIMEOUT', 30))
        self.feeds = {
            'developer': os.getenv('NVIDIA_DEV_BLOG_RSS', 'https://developer.nvidia.com/blog/feed'),
            'main': os.getenv('NVIDIA_BLOG_RSS', 'https://blogs.nvidia.com/feed')
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127 Safari/537.36'
        })

    async def search(self, query: str, include_content: bool = False) -> List[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        dev = await loop.run_in_executor(None, self._search_feed, self.feeds['developer'], query, 'NVIDIA Developer Blog')
        main = await loop.run_in_executor(None, self._search_feed, self.feeds['main'], query, 'NVIDIA Blog')
        all_results = (dev or []) + (main or [])

        # Deduplicate by URL and sort
        seen = set()
        unique = []
        for r in all_results:
            if r.url not in seen:
                seen.add(r.url)
                unique.append(r)
        unique.sort(key=lambda x: (x.relevance_score, x.published_date), reverse=True)
        unique = unique[: self.max_results]

        if include_content:
            # fetch top 2 articles' content
            tasks = [self._fetch_content(r) for r in unique[:2]]
            await asyncio.gather(*tasks)

        return [r.__dict__ for r in unique]

    def _search_feed(self, feed_url: str, query: str, source_name: str) -> List[BlogResult]:
        parsed = feedparser.parse(feed_url)
        out: List[BlogResult] = []
        q = query.lower().split()
        for entry in parsed.entries[:30]:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            content_lc = f"{title} {summary}".lower()
            score = sum(1 for w in q if w in content_lc)
            if score > 0:
                published = entry.get('published', '')
                out.append(BlogResult(
                    title=title,
                    url=entry.get('link', ''),
                    summary=summary,
                    published_date=published,
                    source=source_name,
                    relevance_score=float(score)
                ))
        return out

    async def _fetch_content(self, result: BlogResult):
        try:
            resp = self.session.get(result.url, timeout=self.timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            content_selectors = ['.post-content', '.entry-content', '.article-content', 'main article', '.content']
            text = None
            for sel in content_selectors:
                node = soup.select_one(sel)
                if node:
                    text = node.get_text(" ", strip=True)
                    break
            if not text:
                text = " ".join([p.get_text(" ", strip=True) for p in soup.find_all('p')])
            result.full_content = (text or '')[:3000]
        except Exception:
            result.full_content = None

