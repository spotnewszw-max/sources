import requests
import feedparser
from typing import List, Dict, Optional
from datetime import datetime
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class FeedFetcher:
    """Fetches and parses RSS feeds from various news sources"""
    
    def __init__(self, timeout: int = 30, user_agent: str = None):
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 News Aggregator"
        )
    
    def fetch_rss_feed(self, url: str, source_name: str = "") -> List[Dict]:
        """
        Fetch and parse an RSS feed
        
        Args:
            url: RSS feed URL
            source_name: Name of the source for logging
            
        Returns:
            List of article dictionaries
        """
        try:
            # Fetch the feed
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, timeout=self.timeout, headers=headers)
            response.raise_for_status()
            
            # Parse with feedparser
            feed = feedparser.parse(response.content)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parse warning for {source_name} ({url}): {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries:
                article = self._parse_entry(entry, source_name, url)
                if article:
                    articles.append(article)
            
            logger.info(f"Successfully fetched {len(articles)} articles from {source_name}")
            return articles
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {source_name} from {url}")
            return []
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error fetching {source_name} from {url}")
            return []
        except Exception as e:
            logger.error(f"Error fetching RSS from {source_name}: {str(e)}")
            return []
    
    def _parse_entry(self, entry: Dict, source_name: str, source_url: str) -> Optional[Dict]:
        """Parse a single RSS entry into article format"""
        try:
            # Extract fields with fallbacks
            title = entry.get('title', 'No Title').strip()
            if not title:
                return None
            
            # Get content (try summary first, then content)
            summary = entry.get('summary', '')
            if 'content' in entry and entry['content']:
                content = entry['content'][0].get('value', summary)
            else:
                content = summary
            
            # Remove HTML tags from content
            content = self._clean_html(content)
            
            # Parse date
            published = self._parse_date(entry)
            
            # Extract URLs and images
            article_url = entry.get('link', '')
            image_url = self._extract_image(entry)
            
            # Extract author
            author = None
            if 'author_detail' in entry:
                author = entry['author_detail'].get('name')
            elif 'author' in entry:
                author = entry['author']
            
            article = {
                'title': title,
                'content': content[:1000],  # Truncate to 1000 chars
                'summary': content[:200],   # First 200 chars as summary
                'url': article_url,
                'source': source_name,
                'source_url': source_url,
                'author': author,
                'published_at': published,
                'image_url': image_url,
                'fetched_at': datetime.utcnow().isoformat(),
                'language': 'en'  # TODO: Add language detection
            }
            
            return article
            
        except Exception as e:
            logger.warning(f"Error parsing entry from {source_name}: {str(e)}")
            return None
    
    def _parse_date(self, entry: Dict) -> str:
        """Parse published date from entry"""
        try:
            if 'published_parsed' in entry and entry['published_parsed']:
                dt = datetime(*entry['published_parsed'][:6])
                return dt.isoformat()
            elif 'updated_parsed' in entry and entry['updated_parsed']:
                dt = datetime(*entry['updated_parsed'][:6])
                return dt.isoformat()
        except Exception as e:
            logger.debug(f"Error parsing date: {str(e)}")
        
        return datetime.utcnow().isoformat()
    
    def _extract_image(self, entry: Dict) -> Optional[str]:
        """Extract image URL from entry"""
        try:
            # Check media_content
            if 'media_content' in entry and entry['media_content']:
                return entry['media_content'][0].get('url')
            
            # Check media_thumbnail
            if 'media_thumbnail' in entry and entry['media_thumbnail']:
                return entry['media_thumbnail'][0].get('url')
            
            # Check image field
            if 'image' in entry:
                return entry['image'].get('href')
            
            # Try to extract from content
            if 'summary' in entry:
                # Simple extraction of img src (not foolproof)
                import re
                match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry['summary'])
                if match:
                    return match.group(1)
        except Exception as e:
            logger.debug(f"Error extracting image: {str(e)}")
        
        return None
    
    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from content"""
        import re
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        # Remove all HTML tags
        html = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        import html as html_lib
        html = html_lib.unescape(html)
        # Clean up whitespace
        html = re.sub(r'\s+', ' ', html).strip()
        return html
    
    def fetch_from_sources(self, sources: List[Dict]) -> List[Dict]:
        """
        Fetch articles from multiple sources
        
        Args:
            sources: List of source dicts with 'name', 'url', 'type' fields
            
        Returns:
            List of all articles from all sources
        """
        all_articles = []
        for source in sources:
            if not source.get('enabled', True):
                logger.debug(f"Skipping disabled source: {source.get('name')}")
                continue
            
            source_name = source.get('name', 'Unknown')
            source_url = source.get('url', '')
            source_type = source.get('type', 'rss')
            
            if source_type == 'rss':
                articles = self.fetch_rss_feed(source_url, source_name)
                all_articles.extend(articles)
            else:
                logger.warning(f"Unsupported source type '{source_type}' for {source_name}")
        
        return all_articles


# Convenience functions for backward compatibility
fetcher = FeedFetcher()

def fetch_articles(url: str) -> List[Dict]:
    """Fetch articles from JSON API endpoint"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        articles = response.json()
        return articles if isinstance(articles, list) else []
    except Exception as e:
        logger.error(f"Error fetching JSON from {url}: {str(e)}")
        return []

def fetch_rss_feed(url: str, source_name: str = "Unknown") -> List[Dict]:
    """Fetch and parse RSS feed"""
    return fetcher.fetch_rss_feed(url, source_name)

def fetch_html_content(url: str) -> str:
    """Fetch raw HTML content from URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error fetching HTML from {url}: {str(e)}")
        return ""

def fetch_articles_from_sources(sources: List[Dict]) -> List[Dict]:
    """Fetch articles from a list of sources"""
    return fetcher.fetch_from_sources(sources)