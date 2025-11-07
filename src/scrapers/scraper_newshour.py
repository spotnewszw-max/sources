from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Robust NewsHour Zimbabwe scraper
- Multi-URL homepage probing
- Multi-selector link discovery
- Full article content extraction with shared utils and local fallback
- Featured image support
- Standardized output keys: title, content, source_url, source, image_url
"""

import logging
import random
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Ensure project root is on sys.path when running as a script
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
    crawler,
)

logger = logging.getLogger(__name__)


def _create_client():
    """Return a HTTP client; prefer CloudScraper when available."""
    try:
        import cloudscraper
        s = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "desktop": True}
        )
        s.headers.update(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
            }
        )
        return s
    except Exception as e:
        logger.warning(f"CloudScraper unavailable, using requests: {e}")
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


def _absolutize(href: str, base_url: str) -> str:
    if not href:
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return urljoin(base_url, href)
    if not href.startswith("http"):
        return urljoin(base_url, href)
    return href


def _fallback_article_content(soup: BeautifulSoup) -> str:
    """Local fallback if shared extractor fails."""
    for sel in [
        "div[itemprop='articleBody']",
        ".td-post-content",
        ".single-content",
        ".entry-content",
        ".post-content",
        "article",
        "main",
    ]:
        container = soup.select_one(sel)
        if not container:
            continue
        parts: List[str] = []
        for p in container.find_all(["p", "div", "span"], recursive=True):
            t = p.get_text(strip=True)
            if t and len(t) > 25:
                parts.append(t)
        if parts:
            return "\n\n".join(f"<p>{x}</p>" for x in parts[:12])
    parts = []
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if t and len(t) > 40:
            parts.append(t)
    if parts:
        return "\n\n".join(f"<p>{x}</p>" for x in parts[:12])
    return ""


def scrape_newshour(max_articles: int = 12) -> List[Dict]:
    from utils.scraper_enhanced import discover_articles_via_rss

    articles: List[Dict] = []

    start_urls = [
        "https://newshour.co.zw/",
        "https://www.newshour.co.zw/",
        "https://newshour.co.zw/category/news/",
        "http://newshour.co.zw/",
    ]

    client = _create_client()

    # 1) Fast path: try RSS discovery first
    try:
        rss_items = discover_articles_via_rss([start_urls[0], start_urls[1]], max_articles * 2)
        seen_links = set()
        for item in rss_items:
            if len(articles) >= max_articles:
                break
            href = (item.get("url") or item.get("link") or "").strip()
            title = (item.get("title") or "").strip()
            if not href or not title or len(title) < 8:
                continue
            if href in seen_links:
                continue
            seen_links.add(href)

            # Fetch article (rendered fallback first for reliability)
            try:
                time.sleep(random.uniform(0.6, 1.2))
                ar = crawler.get(href, render=True)
                if ar.status_code != 200 or not ar.text:
                    ar = client.get(href, timeout=25)
                    if ar.status_code != 200 or not ar.text:
                        continue
                art_soup = BeautifulSoup(ar.text if hasattr(ar, "text") else ar.text, "html.parser")
                parts = extract_content_paragraphs(art_soup)
                body_html = render_paragraphs_html(parts) if parts else _fallback_article_content(art_soup)
                if not body_html:
                    continue
                image_url = extract_featured_image(art_soup, href)
                content_html = body_html + "\n" + build_source_attribution(href, "NewsHour")
                data: Dict = {
                    "title": title,
                    "content": content_html,
                    "source_url": href,
                    "source": "NewsHour",
                }
                if image_url:
                    data["image_url"] = image_url
                articles.append(data)
            except Exception:
                continue
    except Exception:
        pass

    if len(articles) >= max_articles:
        return articles

    soup: Optional[BeautifulSoup] = None
    base_url: Optional[str] = None

    # 2) Try multiple landing pages
    for url in start_urls:
        try:
            time.sleep(random.uniform(0.8, 1.6))
            r = crawler.get(url, render=True)
            if r.status_code != 200 or not r.text:
                r = client.get(url, timeout=25)
            if r.status_code == 200 and r.text:
                soup = BeautifulSoup(r.text, "html.parser")
                base_url = url
                logger.info(f"Homepage OK: {url}")
                break
            else:
                logger.warning(f"Landing failed {url}: {getattr(r, 'status_code', 'no_status')}")
        except Exception as e:
            logger.warning(f"Error loading {url}: {e}")

    if not soup or not base_url:
        logger.error("NewsHour: no homepage accessible")
        return articles

    link_selectors = [
        "h2.entry-title a",
        ".td-module-title a",
        "article h2 a",
        ".wp-block-post-title a",
        ".elementor-post__title a",
        ".jeg_post_title a",
        ".jeg_block_content .jeg_post a",
        "h3 a",
        "article a[href*='/20']",
    ]

    link_elems = []
    for sel in link_selectors:
        try:
            elems = soup.select(sel)
            if elems:
                link_elems = elems
                logger.info(f"Selector '{sel}' -> {len(elems)} elements")
                break
        except Exception:
            continue

    if not link_elems:
        anchors = soup.find_all("a", href=True)
        host = urlparse(base_url).netloc.lower()
        for a in anchors:
            href = (a.get("href", "") or "").strip()
            txt = a.get_text(strip=True)
            if not href or not txt or len(txt) < 8:
                continue
            h = href.lower()
            if any(x in h for x in ["/category/", "/tag/", "/author/", "/page/"]):
                continue
            if (host in h or "newshour.co.zw" in h) and ("/20" in h or "/news/" in h):
                link_elems.append(a)
        logger.info(f"Fallback anchors -> {len(link_elems)} potential links")

    if not link_elems:
        logger.warning("No link elements found on homepage")
        return articles

    seen = set()
    for a in link_elems:
        if len(articles) >= max_articles:
            break
        try:
            href = (a.get("href", "") or "").strip()
            title = a.get_text(strip=True)
            if not href or not title or len(title) < 8:
                continue

            href = _absolutize(href, base_url)
            low = href.lower()
            if any(x in low for x in ["/category/", "/tag/", "/author/", "/page/"]):
                continue
            if href in seen:
                continue
            seen.add(href)

            time.sleep(random.uniform(0.8, 1.6))
            ar = crawler.get(href, render=True)
            if ar.status_code != 200 or not ar.text:
                ar = client.get(href, timeout=25)
                if ar.status_code != 200 or not ar.text:
                    continue
            art_soup = BeautifulSoup(ar.text if hasattr(ar, 'text') else ar.text, "html.parser")

            parts = extract_content_paragraphs(art_soup)
            body_html = render_paragraphs_html(parts) if parts else ""
            if not body_html:
                alt = _fallback_article_content(art_soup)
                if not alt:
                    continue
                body_html = alt

            image_url = extract_featured_image(art_soup, href)
            content_html = body_html + "\n" + build_source_attribution(href, "NewsHour")

            data: Dict = {
                "title": title,
                "content": content_html,
                "source_url": href,
                "source": "NewsHour",
            }
            if image_url:
                data["image_url"] = image_url

            articles.append(data)
        except Exception as e:
            logger.warning(f"NewsHour item failed: {e}")
            continue

    return articles


def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    articles = scrape_newshour(max_articles=max_articles)
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
    articles = scrape_newshour(max_articles=max_articles)
    
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
    items = scrape_newshour(8)
    print(f"Found {len(items)} NewsHour articles")
    for i, it in enumerate(items, 1):
        print(i, it["title"][:90])
        print("URL:", it.get("source_url"))
        print("Image:", it.get("image_url"))
