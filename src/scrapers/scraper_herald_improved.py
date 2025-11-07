from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Herald Improved News Scraper
Scrapes articles from https://www.herald.co.zw/

Features:
- Enhanced article discovery with multiple selectors
- Optimized image extraction using meta tags
- Connection pooling for performance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.base_scraper import BaseScraper
from src.utils.image_utils import OptimizedImageExtractor
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class HeraldScraper(BaseScraper):
    def __init__(self, max_articles=10):
        base_urls = [
            "https://www.herald.co.zw/category/news/",
            "https://www.herald.co.zw/",
            "https://herald.co.zw/"
        ]
        super().__init__("The Herald", base_urls, max_articles)
        # Initialize optimized image extractor with connection pooling
        self.image_extractor = OptimizedImageExtractor(timeout=20)
    
    def _fetch_full_article(self, url: str, title: str):
        """Override to add image extraction for Herald"""
        article = super()._fetch_full_article(url, title)
        if article:
            # Add featured image
            article = self._add_featured_image(article, url)
        return article
    
    def scrape_webpage(self):
        """Custom Herald webpage scraping logic with connection pooling"""
        articles = []
        
        # Get session with connection pooling
        from utils.image_extraction_optimizer import get_session
        session = get_session()
        
        for base_url in self.base_urls:
            try:
                response = session.get(base_url, timeout=20)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Herald-specific selectors
                article_selectors = [
                    "article h2 a",
                    ".td-module-title a", 
                    ".entry-title a",
                    "h3 a",
                    ".post-title a"
                ]
                
                for selector in article_selectors:
                    links = soup.select(selector)
                    if len(links) >= 3:
                        for link in links[:self.max_articles * 2]:
                            if len(articles) >= self.max_articles:
                                break
                            
                            url = urljoin(base_url, link.get('href', ''))
                            title = link.get_text(strip=True)
                            
                            if self._is_valid_herald_url(url) and len(title) > 10:
                                article = self._fetch_full_article(url, title)
                                if article:
                                    articles.append(article)
                            
                            self.rate_limiter.wait()
                        break  # Stop after first successful selector
                
                if articles:
                    break  # Stop after first successful URL
                    
            except Exception as e:
                logger.warning(f"Herald webpage scraping failed for {base_url}: {e}")
                continue
        
        return articles
    
    def _is_valid_herald_url(self, url):
        """Herald-specific URL validation"""
        if not url or 'herald.co.zw' not in url:
            return False
        
        url_lower = url.lower()
        
        # Skip non-articles
        if any(x in url_lower for x in ['/category/', '/tag/', '/author/', '/page/']):
            return False
        
        # Herald articles usually have these patterns
        return any(x in url_lower for x in ['/news/', '/politics/', '/business/', '/sport/', '/20'])
    
    def _add_featured_image(self, article, url):
        """Extract featured image using optimized extractor with connection pooling"""
        try:
            # Try meta tags first (fastest and most reliable)
            img_url = self.image_extractor.extract_image(url, priority='meta')
            
            if not img_url:
                # Fallback to featured images
                img_url = self.image_extractor.extract_image(url, priority='featured')
            
            if not img_url:
                # Final fallback to content images
                img_url = self.image_extractor.extract_image(url, priority='content')
            
            if img_url:
                article['image_url'] = img_url
                logger.debug(f"✓ Image extracted: {img_url[:80]}")
            else:
                logger.debug(f"No image found for: {url}")
                
        except Exception as e:
            logger.debug(f"Image extraction error for {url}: {e}")
        
        return article
    
    def _is_valid_image_url(self, url):
        """Check if image URL is valid and not a placeholder"""
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Skip data URIs and placeholders
        if url_lower.startswith('data:'):
            return False
        
        # Skip logos and common placeholders
        bad_keywords = ['logo', 'placeholder', 'default', 'avatar', 'favicon', 'sprite', 'icon']
        if any(keyword in url_lower for keyword in bad_keywords):
            return False
        
        # Accept common image extensions
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
        return url_lower.endswith(valid_extensions)

def scrape_herald_improved(max_articles=10):
    """Main function to maintain compatibility"""
    scraper = HeraldScraper(max_articles)
    return scraper.scrape()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    articles = scrape_herald_improved(5)
    print(f"Found {len(articles)} Herald articles")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title'][:60]}...")
