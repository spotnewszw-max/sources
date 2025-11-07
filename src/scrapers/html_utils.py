from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from src.utils.cache import cache
import hashlib
import logging

logger = logging.getLogger(__name__)

class HTMLParser:
    """HTML parsing utility with caching support"""
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
    
    def _generate_cache_key(self, html: str, parser: str) -> str:
        """Generate cache key for parsed HTML"""
        content_hash = hashlib.md5(html.encode()).hexdigest()[:12]
        return f"html:parsed:{parser}:{content_hash}"
    
    def parse(self, html: str, parser: str = 'lxml', use_cache: bool = True) -> BeautifulSoup:
        """Parse HTML with caching support"""
        if use_cache:
            cache_key = self._generate_cache_key(html, parser)
            cached = cache.get(cache_key)
            if cached:
                logger.debug("Using cached parsed HTML")
                return cached
        
        soup = BeautifulSoup(html, parser)
        
        if use_cache:
            cache.set(cache_key, soup, self.cache_ttl)
            
        return soup
    
    def extract_text(self, element: BeautifulSoup, strip: bool = True) -> str:
        """Safely extract text from BS4 element"""
        if not element:
            return ""
        text = element.get_text()
        return text.strip() if strip else text
    
    def extract_attribute(self, element: BeautifulSoup, attr: str, default: str = "") -> str:
        """Safely extract attribute from BS4 element"""
        return element.get(attr, default) if element else default
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract common metadata from HTML"""
        metadata = {
            'title': '',
            'description': '',
            'keywords': '',
            'author': '',
            'published_date': '',
            'modified_date': ''
        }
        
        # Extract metadata from meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description' or property == 'og:description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
            elif name == 'author':
                metadata['author'] = content
            elif property == 'article:published_time':
                metadata['published_date'] = content
            elif property == 'article:modified_time':
                metadata['modified_date'] = content
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = self.extract_text(title_tag)
        
        return metadata

    def extract_article_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract article content with common patterns"""
        article = {
            'title': '',
            'content': '',
            'images': [],
            'links': [],
            'extracted_at': datetime.now().isoformat()
        }
        
        # Try common article containers
        article_elem = (
            soup.find('article') or
            soup.find('div', class_=['article', 'post', 'entry'])
        )
        
        if article_elem:
            # Extract title
            title_elem = article_elem.find(['h1', 'h2'])
            if title_elem:
                article['title'] = self.extract_text(title_elem)
            
            # Extract content
            content_elem = article_elem.find(['div', 'section'], class_=[
                'content', 'article-content', 'entry-content'
            ])
            if content_elem:
                article['content'] = self.extract_text(content_elem)
            
            # Extract images
            for img in article_elem.find_all('img'):
                src = self.extract_attribute(img, 'src')
                if src:
                    article['images'].append({
                        'src': src,
                        'alt': self.extract_attribute(img, 'alt')
                    })
            
            # Extract links
            for link in article_elem.find_all('a'):
                href = self.extract_attribute(link, 'href')
                if href:
                    article['links'].append({
                        'url': href,
                        'text': self.extract_text(link)
                    })
        
        return article