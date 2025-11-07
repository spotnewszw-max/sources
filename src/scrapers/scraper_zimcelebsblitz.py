from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
ZimCelebs Blitz scraper (fast + reliable)
- Prioritizes RSS for quick discovery
- Parallel article fetching with short timeouts
- Fallback to lightweight homepage parsing
- Uses shared utils for content extraction and attribution
- Output keys: title, content, source_url, source, image_url (optional)
"""

import logging
import random
import time
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin
import concurrent.futures as futures

import requests
from bs4 import BeautifulSoup

try:
    import feedparser  # type: ignore
except Exception:
    feedparser = None  # type: ignore

import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.scrapers.base_scraper import (
    extract_content_paragraphs,
    extract_featured_image,
    render_paragraphs_html,
    build_source_attribution,
)

logger = logging.getLogger(__name__)

BASE = "https://zimcelebsblitz.com"
SOURCE_NAME = "ZimCelebs Blitz"


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
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
    )
    return s


def _absolutize(href: str, base_url: str = BASE) -> str:
    if not href:
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return urljoin(base_url, href)
    if not href.startswith("http"):
        return urljoin(base_url, href)
    return href


def _extract_article_content_html(soup: BeautifulSoup) -> str:
    parts = extract_content_paragraphs(soup)
    if parts:
        return render_paragraphs_html(parts)
    tmp = []
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if t and len(t) > 40:
            tmp.append(t)
    if tmp:
        return "\n\n".join(f"<p>{x}</p>" for x in tmp[:12])
    return ""


def _fetch_article(url: str, session: requests.Session) -> Optional[Dict]:
    try:
        r = session.get(url, timeout=12)
        if r.status_code != 200 or not r.text:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        # Title
        title = None
        for sel in ("h1", ".entry-title", ".post-title", "title"):
            el = soup.select_one(sel) if sel != "title" else soup.find("title")
            if el:
                title = el.get_text(strip=True)
                if title and len(title) > 8:
                    break
        if not title:
            return None
        # Content
        content_html = _extract_article_content_html(soup)
        if not content_html:
            return None
        # Image
        img = extract_featured_image(soup, url)
        content_html += "\n" + build_source_attribution(url, SOURCE_NAME)
        data: Dict = {
            "title": title,
            "content": content_html,
            "source_url": url,
            "source": SOURCE_NAME,
        }
        if img:
            data["image_url"] = img
        return data
    except Exception as e:
        logger.debug("Article fetch failed %s: %s", url, e)
        return None


def _collect_from_rss(session: requests.Session, limit: int) -> List[str]:
    rss_urls = [
        f"{BASE}/feed/",
        f"{BASE}/category/news/feed/",
    ]
    links: List[str] = []
    for feed in rss_urls:
        try:
            if feedparser:
                d = feedparser.parse(feed)
                for e in d.entries:
                    href = _absolutize(getattr(e, "link", "") or "")
                    if href and href not in links:
                        links.append(href)
                        if len(links) >= limit:
                            return links
            else:
                r = session.get(feed, timeout=10)
                if r.status_code != 200:
                    continue
                xml = BeautifulSoup(r.text, "xml")
                for it in xml.find_all("item"):
                    href = _absolutize((it.link.get_text(strip=True) if it.link else ""))
                    if href and href not in links:
                        links.append(href)
                        if len(links) >= limit:
                            return links
        except Exception:
            continue
    return links


def _collect_from_home(session: requests.Session, limit: int) -> List[str]:
    start_urls = [
        BASE + "/",
        BASE + "/category/news/",
    ]
    selectors = [
        "h2.entry-title a",
        "h3.entry-title a",
        ".td-module-title a",
        "article h2 a",
        ".wp-block-post-title a",
        "a[href*='/20']",
    ]
    links: List[str] = []
    seen = set()
    for url in start_urls:
        try:
            r = session.get(url, timeout=12)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            for sel in selectors:
                for a in soup.select(sel):
                    href = _absolutize(a.get("href", ""))
                    title = a.get_text(strip=True)
                    if not href or not title or len(title) < 8:
                        continue
                    low = href.lower()
                    if any(x in low for x in ["/category/", "/tag/", "/author/", "/page/"]):
                        continue
                    if href in seen:
                        continue
                    seen.add(href)
                    links.append(href)
                    if len(links) >= limit:
                        return links
        except Exception:
            continue
    return links


def scrape_zimcelebsblitz(max_articles: int = 12) -> List[Dict]:
    session = _create_session()
    max_articles = max(3, max_articles)

    links = _collect_from_rss(session, max_articles * 2)
    if not links:
        links = _collect_from_home(session, max_articles * 2)

    if not links:
        logger.warning("%s: no links discovered", SOURCE_NAME)
        return []

    results: List[Dict] = []
    taken = set()

    workers = min(6, max_articles)
    with futures.ThreadPoolExecutor(max_workers=workers) as ex:
        future_map = {ex.submit(_fetch_article, u, session): u for u in links[: max_articles * 2]}
        for fut in futures.as_completed(future_map):
            item = fut.result()
            if not item:
                continue
            url = item.get("source_url")
            if url in taken:
                continue
            taken.add(url)
            results.append(item)
            if len(results) >= max_articles:
                break

    if not results:
        for href in links[:max_articles]:
            results.append(
                {
                    "title": "Latest from ZimCelebs Blitz",
                    "content": f"<p><a href='{href}' target='_blank'>Read on ZimCelebs Blitz</a></p>",
                    "source_url": href,
                    "source": SOURCE_NAME,
                }
            )

    return results


def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_zimcelebsblitz(max_articles=max_articles)
    
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
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    items = scrape_zimcelebsblitz(6)
    print(f"Found {len(items)} ZimCelebs Blitz articles")
    for i, it in enumerate(items, 1):
        print(i, it.get("title", "")[:90])
        print("URL:", it.get("source_url"))
        print("Image:", it.get("image_url"))
