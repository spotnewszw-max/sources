from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
ZWNews scraper
- Extracts homepage links heuristically
"""

import logging
import time
import random
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

try:
    import cloudscraper
except Exception:
    cloudscraper = None  # type: ignore

logger = logging.getLogger(__name__)

BASE_URL = "https://zwnews.com"


def _create_session():
    if cloudscraper:
        try:
            s = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "desktop": True}
            )
        except Exception:
            s = requests.Session()
    else:
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

    for sel in selectors:
        container = soup.select_one(sel)
        if not container:
            continue
        for el in container.find_all(["script", "style", "nav", "aside", "footer", "form"]):
            el.decompose()

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

    content_html += f"\n\n<p><em>Source: <a href='{url}' target='_blank'>ZWNews</a></em></p>"
    return title, content_html, img


def scrape_zwnews(max_articles: int = 10) -> List[Dict]:
    articles: List[Dict] = []
    session = _create_session()

    try:
        resp = session.get(BASE_URL, timeout=30)
        if resp.status_code != 200:
            logger.error("ZWNews homepage unavailable: %s", resp.status_code)
            return articles
        soup = BeautifulSoup(resp.text, "html.parser")

        # Heuristic: take prominent links not pointing to categories/tags/authors
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True)
            if not href:
                continue
            if any(x in href.lower() for x in ("/category/", "/tag/", "/author/", "/contact", "/about")):
                continue
            if not href.startswith("http"):
                href = urljoin(BASE_URL, href)
            if "zwnews.com" in href and text and 10 < len(text) < 200:
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
            # Filter short content
            if len(BeautifulSoup(content_html, "html.parser").get_text(" ").split()) < 50:
                continue
            articles.append(
                {
                    "title": title,
                    "content": content_html,
                    "source_url": href,
                    "source": "ZWNews",
                    **({"image_url": img} if img else {}),
                }
            )

        logger.info("Found %d articles from ZWNews", len(articles))
        return articles
    except Exception as e:
        logger.error("Error scraping ZWNews: %s", e)
        return articles


def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_zwnews(max_articles=max_articles)
    
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
    items = scrape_zwnews(3)
    print(f"Found {len(items)} ZWNews articles")
    for i, it in enumerate(items, 1):
        print(i, it["title"][:80])