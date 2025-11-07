from .base_scraper import BaseScraper
import requests
import logging
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class HeraldScraper(BaseScraper):
    def __init__(self, max_articles: int = 10):
        super().__init__(
            "The Herald",
            [
                "https://www.heraldonline.co.zw/category/news/",
                "https://www.heraldonline.co.zw/",
                "https://www.herald.co.zw/category/news/",
                "https://www.herald.co.zw/",
            ],
            max_articles=max_articles,
        )

    def _is_valid_article_url(self, url: str) -> bool:
        L = (url or "").lower()
        if not ("heraldonline.co.zw" in L or "herald.co.zw" in L):
            return False
        # Exclude obvious non-articles
        skip = [
            "/category/",
            "/tag/",
            "/author/",
            "/page/",
            "/topics/",
            "/section/",
            "/contact",
            "/about",
            "/sundaynews",
            "/sunday-news",
            "/?s=",
            "/search",
        ]
        if any(p in L for p in skip):
            return False
        # Prefer dated permalinks
        if "/20" in L:
            return True
        # Accept deep slugs under common sections
        sections = [
            "/news/",
            "/business/",
            "/politics/",
            "/sport/",
            "/sports/",
            "/opinion/",
            "/crime/",
            "/technology/",
            "/international/",
            "/local-news/",
        ]
        if any(sec in L for sec in sections) and len(L.strip("/").split("/")) >= 5:
            return True
        # Fallback heuristic: sufficiently deep path
        return len(L.strip("/").split("/")) >= 6

    def scrape_webpage(self) -> List[Dict]:
        articles: List[Dict] = []
        try:
            for base in self.base_urls:
                if len(articles) >= self.max_articles:
                    break
                # Prefer rendered snapshot; fallback to non-render
                html = self.fetcher.get_html(base, render=True, timeout=15) or self.fetcher.get_html(
                    base, render=False, timeout=20
                )
                if not html:
                    continue
                soup = BeautifulSoup(html, "html.parser")

                # Broad link selectors for WP/TagDiv/Jeg/block themes
                link_selectors = [
                    "h2.entry-title a",
                    "h3.entry-title a",
                    ".td-module-title a",
                    "article h2 a",
                    ".jeg_post_title a",
                    ".jeg_block_content a",
                    ".wp-block-post-title a",
                    "a[href*='/20']",
                ]
                link_elems = []
                for sel in link_selectors:
                    try:
                        elems = soup.select(sel)
                        if elems:
                            link_elems.extend(elems)
                            logger.info(f"Selector '{sel}' -> {len(elems)} elements")
                    except Exception:
                        continue

                if not link_elems:
                    # Fallback: all anchors
                    link_elems = soup.find_all("a", href=True)

                seen = set()
                for a in link_elems:
                    if len(articles) >= self.max_articles:
                        break
                    href = (a.get("href", "") or "").strip()
                    if not href:
                        continue
                    url = urljoin(base, href)
                    if url in seen:
                        continue
                    seen.add(url)

                    title = (a.get_text(strip=True) or "").strip()
                    if not title or len(title) < 8:
                        continue

                    if not self._is_valid_article_url(url):
                        continue

                    art = self._fetch_full_article(url, title)
                    if art:
                        articles.append(art)

            return articles
        except Exception as e:
            logger.warning(f"Herald custom scrape failed: {e}")
            return articles


def scrape_herald(max_articles: int = 10) -> List[Dict]:
    return HeraldScraper(max_articles=max_articles).scrape()


def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    articles = scrape_herald(max_articles=max_articles)
    
    # Convert field names from BaseScraper format to expected format
    result = []
    for article in articles:
        if isinstance(article, dict):
            result.append({
                "title": article.get("title", ""),
                "url": article.get("source_url", "") or article.get("url", ""),
                "html": article.get("content", "") or article.get("html", ""),
                "image_url": article.get("image_url", "")
            })
    
    return result
