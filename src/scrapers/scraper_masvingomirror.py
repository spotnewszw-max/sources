from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Masvingomirror scraper
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import random
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

def scrape_masvingomirror(max_articles=10):
    """Scrape Masvingomirror"""
    articles = []
    
    try:
        url = "https://masvingomirror.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
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
                    "source": "Masvingomirror"
                }
                
                articles.append(article)
                
            except Exception as e:
                logger.debug(f"Error processing article: {e}")
                continue
        
        return articles
        
    except Exception as e:
        logger.error(f"Error scraping Masvingomirror: {e}")
        return articles

if __name__ == "__main__":
    articles = scrape_masvingomirror(max_articles=5)
    print(f"Found {len(articles)} articles")
    for article in articles:
        print(f"  - {article['title'][:60]}")