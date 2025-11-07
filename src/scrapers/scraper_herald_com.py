from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Herald Com scraper
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import random
from urllib.parse import urljoin
import os
import sys

# Add project root to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.utils.ssl_utils import smart_get, safe_decode

logger = logging.getLogger(__name__)

def scrape_herald_com(max_articles=10):
    """Scrape Herald Com"""
    articles = []
    
    try:
        url = "https://www.herald.co.zw/"
        
        # Use smart_get with SSL bypass and mobile/cloudscraper fallbacks for this protected site
        response = smart_get(url, max_retries=3, timeout=15, try_ssl_bypass=True)
        
        if response is None:
            logger.error("Could not access herald.co.zw")
            return articles
        
        if response.status_code != 200:
            logger.error(f"Herald returned status {response.status_code}")
            return articles
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract articles (generic fallback for common CMS patterns)
        # Try multiple common patterns
        article_elements = (
            soup.find_all('article') or
            soup.select('.post') or
            soup.select('[role="article"]') or
            soup.select('.entry') or
            soup.select('.item')
        )
        
        for element in article_elements[:max_articles]:
            try:
                # Try to extract title
                title = None
                for title_selector in ['h1', 'h2', 'h3', '.title', '.entry-title']:
                    title_elem = element.select_one(title_selector) if hasattr(element, 'select_one') else None
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                if not title:
                    continue
                
                # Try to extract URL
                url_elem = element.find('a', href=True)
                article_url = url_elem['href'] if url_elem else None
                
                if not article_url:
                    continue
                
                article_url = urljoin(url, article_url)
                
                # Try to extract content
                content = None
                for content_selector in ['.content', '.entry-content', '.post-content', 'p']:
                    content_elem = element.select_one(content_selector) if hasattr(element, 'select_one') else None
                    if content_elem:
                        content = content_elem.get_text(strip=True)[:500]
                        break
                
                article = {
                    "title": title,
                    "url": article_url,
                    "content": content or title,
                    "source": "Herald Com"
                }
                
                articles.append(article)
                
            except Exception as e:
                logger.debug(f"Error processing article: {e}")
                continue
        
        return articles
        
    except Exception as e:
        logger.error(f"Error scraping Herald Com: {e}")
        return articles

if __name__ == "__main__":
    articles = scrape_herald_com(max_articles=5)
    print(f"Found {len(articles)} articles")
    for article in articles:
        print(f"  - {article['title'][:60]}")
