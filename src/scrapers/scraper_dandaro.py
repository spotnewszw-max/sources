from .base_scraper import BaseScraper
import logging
from typing import List, Dict
from src.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class DandaroScraper(BaseScraper):
    """Scraper for Dandaro news website"""
    def __init__(self, max_articles: int = 10):
        super().__init__("Dandaro", [
            "https://www.dandaro.online/"
        ], max_articles=max_articles)

    def scrape_webpage(self) -> List[Dict]:
        """Use base scraper's generic scraping (works well for this site)"""
        return self._try_generic_scraping()


def scrape_dandaro(max_articles: int = 10) -> List[Dict]:
    """Scrape Dandaro news articles"""
    scraper = DandaroScraper(max_articles=max_articles)
    return scraper.scrape()


def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    articles = scrape_dandaro(max_articles=max_articles)
    
    # Convert to expected format
    result = []
    for article in articles:
        if isinstance(article, dict):
            result.append({
                "title": article.get("title", ""),
                "url": article.get("source_url", "") or article.get("url", "") or article.get("link", ""),
                "html": article.get("content", "") or article.get("html", "") or article.get("original_html", ""),
                "image_url": article.get("image_url") or article.get("featured_image_url", "")
            })
    
    return result
