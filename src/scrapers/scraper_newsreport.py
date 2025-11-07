from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
NewsReport (newsreport.co.zw) scraper with robust content extraction
"""

import logging
import random
import time
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.scrapers.base_scraper import (
    extract_content_paragraphs,
    extract_featured_image,
    render_paragraphs_html,
    build_source_attribution,
)

logger = logging.getLogger(__name__)


def _create_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
    )
    return s


def scrape_newsreport(max_articles: int = 10) -> List[Dict]:
    articles: List[Dict] = []
    base_url = "http://newsreport.co.zw/"
    session = _create_session()

    try:
        r = session.get(base_url, timeout=25)
        if r.status_code != 200 or not r.text:
            logger.error("NewsReport homepage unavailable: %s", r.status_code)
            return articles
        soup = BeautifulSoup(r.text, "html.parser")

        link_selectors = [
            "h2.entry-title a",
            ".td-module-title a",
            "article h2 a",
            ".wp-block-post-title a",
        ]

        link_elems = []
        for sel in link_selectors:
            elems = soup.select(sel)
            if elems:
                link_elems = elems
                break
        if not link_elems:
            link_elems = soup.find_all("a", href=True)

        seen = set()
        for a in link_elems:
            if len(articles) >= max_articles:
                break
            href = a.get("href", "").strip()
            title = a.get_text(strip=True)
            if not href or not title or len(title) < 8:
                continue
            if href.startswith("/"):
                href = urljoin(base_url, href)
            elif not href.startswith("http"):
                continue
            if any(x in href.lower() for x in ["/category/", "/tag/", "/author/", "/page/"]):
                continue
            if href in seen:
                continue
            seen.add(href)

            time.sleep(random.uniform(0.7, 1.6))
            ar = session.get(href, timeout=25)
            if ar.status_code != 200 or not ar.text:
                continue
            art = BeautifulSoup(ar.text, "html.parser")

            parts = extract_content_paragraphs(art)
            if not parts:
                continue
            body_html = render_paragraphs_html(parts)
            image_url = extract_featured_image(art, href)
            content_html = body_html + "\n" + build_source_attribution(href, "NewsReport")

            item: Dict = {
                "title": title,
                "content": content_html,
                "source_url": href,
                "source": "NewsReport",
            }
            if image_url:
                item["image_url"] = image_url

            articles.append(item)

    except Exception as e:
        logger.error("Error scraping NewsReport: %s", e)

    return articles


def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    articles = scrape_newsreport(max_articles=max_articles)
    # Convert to expected format
    result = []
    for article in articles:
        result.append({
            "title": article.get("title", ""),
            "url": article.get("source_url", ""),
            "html": article.get("content", ""),
            "image_url": article.get("image_url")
        })
    return result




def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_newsreport(max_articles=max_articles)
    
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
    items = scrape_newsreport(5)
    print(f"Found {len(items)} NewsReport articles")
    for i, it in enumerate(items, 1):
        print(i, it["title"][:90])
        print("URL:", it.get("source_url"))
        print("Image:", it.get("image_url"))
