from .base_scraper import BaseScraper
import requests
import logging
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class ZBCScraper(BaseScraper):
    def __init__(self, max_articles: int = 10):
        super().__init__("ZBC News", [
            "https://www.zbcnews.co.zw/",
            "https://www.zbc.co.zw/"
        ], max_articles=max_articles)

    def scrape_webpage(self) -> List[Dict]:
        articles: List[Dict] = []
        try:
            # Try each base URL for homepage
            for base in self.base_urls:
                if len(articles) >= self.max_articles:
                    break
                # Try rendered first to bypass basic blocks; fallback to normal
                resp = self.fetcher.get_html(base, render=True, timeout=25) or self.fetcher.get_html(base, render=False, timeout=20)
                if not resp:
                    continue
                soup = BeautifulSoup(resp, 'html.parser')

                # Broad set of selectors for article links
                link_selectors = [
                    'h2 a', 'h3 a', '.entry-title a', '.post-title a',
                    'article a[href]', '.wp-block-post a[href]', '.elementor-post a[href]'
                ]
                link_elems = []
                for sel in link_selectors:
                    link_elems = soup.select(sel)
                    if len(link_elems) >= 3:
                        break

                # Fallback: any anchor that looks like an article
                if not link_elems:
                    link_elems = [a for a in soup.find_all('a', href=True)
                                  if len(a.get_text(strip=True)) > 15 and '/category/' not in a['href'].lower()]

                seen = set()
                for a in link_elems:
                    if len(articles) >= self.max_articles:
                        break
                    href = a.get('href', '').strip()
                    if not href:
                        continue
                    url = urljoin(base, href)
                    if url in seen:
                        continue
                    seen.add(url)

                    title = a.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue

                    article = self._fetch_full_article(url, title)
                    if article:
                        articles.append(article)

            return articles
        except Exception as e:
            logger.warning(f"ZBC custom scrape failed: {e}")
            return articles

def scrape_zbc(max_articles: int = 10) -> List[Dict]:
    return ZBCScraper(max_articles=max_articles).scrape()

def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_zbc(max_articles=max_articles)
    
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
