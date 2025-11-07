from .base_scraper import BaseScraper
import logging
import time
import requests
import ssl
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import List, Dict
from src.scrapers.base_scraper import BaseScraper

try:
    import cloudscraper
except ImportError:
    cloudscraper = None

logger = logging.getLogger(__name__)

class AllAfricaScraper(BaseScraper):
    def __init__(self, max_articles: int = 10):
        super().__init__("AllAfrica", [
            "https://allafrica.com/zimbabwe/",
            "https://allafrica.com/"
        ], max_articles=max_articles)

    def scrape_webpage(self) -> List[Dict]:
        """Auto-generated implementation for allafrica"""
        articles = []
        
        for base_url in self.base_urls:
            try:
                # Use standard session for better compatibility
                if hasattr(self, 'session'):
                    session = self.session
                else:
                    if cloudscraper:
                        try:
                            session = cloudscraper.create_scraper()
                        except Exception:
                            session = requests.Session()
                    else:
                        session = requests.Session()
                    session.headers.update({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                
                # Try with SSL verification first, fall back to no verification
                try:
                    response = session.get(base_url, timeout=25, verify=True)
                except (requests.exceptions.SSLError, ssl.SSLError):
                    # If SSL verification fails, disable it properly
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    response = session.get(base_url, timeout=25, verify=False)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Generic selectors for article links
                link_selectors = [
                    'h2 a', 'h3 a', '.entry-title a', '.post-title a',
                    'article a', '.story a', '[class*="title"] a',
                    '.jeg_post_title a', '.td-module-title a'
                ]
                
                found_links = []
                for selector in link_selectors:
                    links = soup.select(selector)
                    if len(links) >= 3:
                        found_links = links
                        break
                
                for link in found_links[:self.max_articles * 2]:
                    if len(articles) >= self.max_articles:
                        break
                    
                    url = urljoin(base_url, link.get('href', ''))
                    title = link.get_text(strip=True)
                    
                    if self._is_valid_article_url(url) and len(title) > 10:
                        article = self._fetch_full_article(url, title)
                        if article:
                            articles.append(article)
                    
                    if hasattr(self, 'rate_limiter'):
                        self.rate_limiter.wait()
                    else:
                        time.sleep(0.5)
                
                if articles:
                    break
                    
            except Exception as e:
                logger.warning(f"allafrica scraping failed for {base_url}: {e}")
                continue
        
        return articles

def scrape_allafrica(max_articles: int = 10) -> List[Dict]:
    return AllAfricaScraper(max_articles=max_articles).scrape()

def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_allafrica(max_articles=max_articles)
    
    # Convert to expected format
    result = []
    for article in articles:
        if isinstance(article, dict):
            result.append({
                "title": article.get("title", ""),
                "url": article.get("source_url", "") or article.get("url", "") or article.get("link", ""),
                "html": article.get("content", "") or article.get("html", "") or article.get("original_html", ""),
                "image_url": article.get("image_url") or article.get("featured_image_url")
            })
    
    return result
