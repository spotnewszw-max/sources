from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Improved NewsDay scraper refactored to use BaseScraper with RSS + generic fallbacks.
- Uses RobustSession from utils.scraper_enhanced (cloudscraper optional)
- Uses BaseScraper._fetch_full_article which leverages SmartFetcher/SmartExtractor
- Broader homepage selectors and URL validation
"""

import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Ensure project root is on sys.path when running as a script
import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class NewsDayScraper(BaseScraper):
    def __init__(self, max_articles: int = 12):
        base_urls = [
            "https://www.newsday.co.zw/category/news/",
            "https://www.newsday.co.zw/",
            "https://newsday.co.zw/category/news/",
            "https://newsday.co.zw/",
        ]
        super().__init__("NewsDay", base_urls, max_articles)

    def scrape_webpage(self):
        articles = []

        for base_url in self.base_urls:
            try:
                r = self.session.get(base_url, timeout=20)
                if getattr(r, "status_code", 0) != 200 or not getattr(r, "content", b""):
                    continue
                soup = BeautifulSoup(r.content, "html.parser")

                link_selectors = [
                    ".td-module-title a",
                    ".entry-title a",
                    "article h2 a",
                    ".wp-block-post-title a",
                    ".elementor-post__title a",
                    "h3 a",
                ]

                found_links = []
                for sel in link_selectors:
                    links = soup.select(sel)
                    if links and len(links) >= 3:
                        found_links = links
                        break

                if not found_links:
                    # Fallback: any anchors that look like article links
                    for a in soup.find_all("a", href=True):
                        href = a.get("href", "")
                        title = a.get_text(strip=True)
                        if not href or not title or len(title) < 10:
                            continue
                        low = href.lower()
                        if any(x in low for x in ["/category/", "/tag/", "/author/", "/page/"]):
                            continue
                        if "/20" in low or "/news/" in low:
                            found_links.append(a)

                for a in found_links:
                    if len(articles) >= self.max_articles:
                        break
                    href = a.get("href", "")
                    title = a.get_text(strip=True)
                    if not href or not title or len(title) < 10:
                        continue

                    url = urljoin(base_url, href)
                    if not self._is_valid_newsday_url(url):
                        continue

                    art = self._fetch_full_article(url, title)
                    if art:
                        articles.append(art)

                if articles:
                    break

            except Exception as e:
                logger.warning(f"NewsDay webpage scraping failed for {base_url}: {e}")
                continue

        return articles

    def _is_valid_newsday_url(self, url: str) -> bool:
        u = (url or "").lower()
        if "newsday.co.zw" not in u:
            return False
        if any(x in u for x in ["/category/", "/tag/", "/author/", "/page/"]):
            return False
        return any(x in u for x in ["/news/", "/20"])  # date or news section in URL


def scrape_newsday_improved(max_articles: int = 10):
    scraper = NewsDayScraper(max_articles)
    return scraper.scrape()


def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_newsday_improved(max_articles=max_articles)
    
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    items = scrape_newsday_improved(6)
    print(f"Found {len(items)} NewsDay articles")
    for i, it in enumerate(items, 1):
        print(i, it["title"][:90])
        print("URL:", it.get("source_url"))
