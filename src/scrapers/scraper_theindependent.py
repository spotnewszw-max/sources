from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
The Zimbabwe Independent scraper
- Extracts article links with /YYYY/MM/DD/ pattern
- Fetches title, content and optional featured image
"""

import logging
import time
import random
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.theindependent.co.zw"


def _create_session():
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
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
    )
    return s


def _absolute(u: str) -> str:
    if not u:
        return u
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("/"):
        return urljoin(BASE_URL, u)
    if not u.startswith("http"):
        return urljoin(BASE_URL, u)
    return u


def _extract_image(soup: BeautifulSoup) -> Optional[str]:
    meta = soup.find("meta", attrs={"property": "og:image"}) or soup.find(
        "meta", attrs={"name": "twitter:image"}
    )
    if meta:
        src = meta.get("content")
        if src:
            return _absolute(src)
    img = soup.select_one(
        "img.wp-post-image, .featured-image img, .post-image img, img[class*='featured'], img[class*='post'], img"
    )
    if img:
        for attr in ("src", "data-src", "data-lazy-src"):
            val = img.get(attr)
            if val:
                return _absolute(val)
    return None


def _extract_article_content(soup: BeautifulSoup) -> str:
    selectors = [
        "div[itemprop='articleBody']",
        ".entry-content",
        ".post-content",
        ".single-content",
        ".article-content",
        "article",
        "main",
    ]
    junk_classes = ("ad", "advert", "share", "social", "related")

    for sel in selectors:
        container = soup.select_one(sel)
        if not container:
            continue
        for el in container.find_all(["script", "style", "nav", "aside", "footer", "form"]):
            el.decompose()
        for el in container.find_all(attrs={"class": True}):
            cls = " ".join(el.get("class", [])).lower()
            if any(j in cls for j in junk_classes):
                try:
                    el.decompose()
                except Exception:
                    pass

        parts = []
        for p in container.find_all(["p", "div", "span"], recursive=True):
            t = p.get_text(strip=True)
            if t and len(t) > 30 and not any(j in t.lower() for j in ("subscribe", "advertisement")):
                parts.append(t)
        if parts:
            return "\n\n".join(f"<p>{x}</p>" for x in parts[:12])

    parts = []
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if t and len(t) > 50:
            parts.append(t)
    if parts:
        return "\n\n".join(f"<p>{x}</p>" for x in parts[:12])
    return ""


def _get_article(url: str, session) -> Optional[Tuple[str, str, Optional[str]]]:
    time.sleep(random.uniform(1.0, 2.5))
    r = session.get(url, timeout=30)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, "html.parser")

    title = None
    for sel in ("h1", ".entry-title", ".post-title", "title"):
        el = soup.select_one(sel) if sel != "title" else soup.find("title")
        if el:
            title = el.get_text(strip=True)
            if title and len(title) > 10:
                break
    if not title:
        return None

    content_html = _extract_article_content(soup)
    if not content_html:
        return None

    img = _extract_image(soup)

    content_html += f"\n\n<p><em>Source: <a href='{url}' target='_blank'>The Zimbabwe Independent</a></em></p>"
    return title, content_html, img


def scrape_theindependent(max_articles: int = 10) -> List[Dict]:
    articles: List[Dict] = []
    session = _create_session()

    try:
        resp = session.get(BASE_URL, timeout=30)
        if resp.status_code != 200:
            logger.error("Independent homepage unavailable: %s", resp.status_code)
            return articles
        soup = BeautifulSoup(resp.text, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True)
            if not href:
                continue
            if not href.startswith("http"):
                href = urljoin(BASE_URL, href)
            if re.search(r"/\d{4}/\d{2}/\d{2}/", href) and text and len(text) > 10:
                links.append((href, text))

        seen = set()
        for href, _ in links:
            if len(articles) >= max_articles:
                break
            if href in seen:
                continue
            seen.add(href)

            got = _get_article(href, session)
            if not got:
                continue
            title, content_html, img = got
            articles.append(
                {
                    "title": title,
                    "content": content_html,
                    "source_url": href,
                    "source": "The Zimbabwe Independent",
                    **({"image_url": img} if img else {}),
                }
            )

        logger.info("Found %d articles from The Independent", len(articles))
        return articles
    except Exception as e:
        logger.error("Error scraping The Independent: %s", e)
        return articles


def scrape_theindependent_nd(max_articles=10):
    articles = []
    url = "https://newsday.co.zw/theindependent/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.select("h2.entry-title a")[:max_articles]:
            link = a.get("href")
            title = a.get_text(strip=True)
            try:
                article_resp = requests.get(link, headers=headers, timeout=10)
                article_resp.raise_for_status()
                article_soup = BeautifulSoup(article_resp.text, "html.parser")
                body = article_soup.select_one("div.td-post-content")
                articles.append({
                    "title": title,
                    "url": link,
                    "html": str(body) if body else "",
                    "image_url": None
                })
            except Exception as e:
                print(f"Failed to fetch article: {link} ({e})")
    except Exception as e:
        print(f"Failed to fetch main page: {url} ({e})")
    return articles




def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_theindependent(max_articles=max_articles)
    
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
    items = scrape_theindependent(3)
    print(f"Found {len(items)} Independent articles")
    for i, it in enumerate(items, 1):
        print(i, it["title"][:80])