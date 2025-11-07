from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Robust NewZimbabwe scraper
- Uses multiple homepage URLs and selectors
- Extracts full content and featured image via shared utils
- Standardizes output keys: title, content, source_url, source, image_url
"""

import logging
import random
import time
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

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

# Import SSL fix utilities
try:
    from utils.ssl_fix import create_ssl_bypass_session, create_robust_session
except ImportError:
    create_ssl_bypass_session = None
    create_robust_session = None

logger = logging.getLogger(__name__)


# ===== Deterministic extractive summarizer (no external APIs) =====
_def_sentence_splitter = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9(\["])')

def _split_sentences(text: str) -> List[str]:
    # Simple, deterministic sentence splitter; avoids heavy NLP deps
    try:
        # Normalize whitespace
        t = re.sub(r"\s+", " ", (text or "").strip())
        if not t:
            return []
        # Split on punctuation boundaries
        raw = _def_sentence_splitter.split(t)
        out: List[str] = []
        for s in raw:
            s = s.strip()
            if not s:
                continue
            # Filter very short or boilerplate lines
            if len(s) < 30:
                continue
            out.append(s)
        return out
    except Exception:
        return []


def _build_summary_from_paragraphs(paragraphs: List[str]) -> str:
    """Return two HTML <p> blocks, 5–7 sentences each when possible.
    Deterministic extractive approach using lead sentences.
    """
    if not paragraphs:
        return ""
    # Join paragraphs to a single text for sentence splitting
    text = " ".join([re.sub(r"\s+", " ", p).strip() for p in paragraphs if p and len(p.strip()) > 0])
    sentences = _split_sentences(text)

    # Best-effort to reach 10–12 sentences total
    if len(sentences) >= 12:
        selected = sentences[:12]
    elif len(sentences) >= 10:
        selected = sentences[:10]
    else:
        selected = sentences[:min(len(sentences), 10)]

    if not selected:
        # Fallback: build from first two input paragraphs if sentence split failed
        para1 = paragraphs[0].strip()
        para2 = (paragraphs[1] if len(paragraphs) > 1 else paragraphs[0]).strip()
        return f"<p>{para1}</p>\n\n<p>{para2}</p>"

    # Split into 2 paragraphs, aiming for 5–7 sentences each
    n = len(selected)
    p1_count = max(5, min(7, (n + 1) // 2))
    p1 = selected[:p1_count]
    p2 = selected[p1_count:]
    if len(p2) < 5 and n > 8:
        # Try to rebalance if second paragraph is too short
        shift = min(len(p1) - 5, 5 - len(p2))
        if shift > 0:
            p2 = selected[p1_count - shift:]
            p1 = selected[:p1_count - shift]

    para1_html = " ".join([s if s.endswith(('.', '!', '?')) else s + '.' for s in p1])
    para2_html = " ".join([s if s.endswith(('.', '!', '?')) else s + '.' for s in p2]) if p2 else ""

    if not para2_html:
        # Ensure two paragraphs even if content is short
        mid = max(1, len(p1) // 2)
        para1_html = " ".join([s if s.endswith(('.', '!', '?')) else s + '.' for s in p1[:mid]])
        para2_html = " ".join([s if s.endswith(('.', '!', '?')) else s + '.' for s in p1[mid:]])

    return f"<p>{para1_html}</p>\n\n<p>{para2_html}</p>"


def clean_article_html(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove bylines, share buttons, ads, and other non-article elements."""
    try:
        selectors = [
            '.byline', '.author', '.post-meta', '.entry-meta',
            '.share', '.social', '.article-share', '.article-author',
            '.advertisement', '.ad', '.adsbygoogle', '.promo', '.wp-block-button',
            '#jp-post-flair', '#sharing', '#share-buttons', '#social-share', '#author-info'
        ]
        for sel in selectors:
            for tag in soup.select(sel):
                try:
                    tag.decompose()
                except Exception:
                    pass
    except Exception:
        pass
    return soup


def _create_client():
    """Return a HTTP client with robust SSL handling for problematic sites."""
    # Priority: SSL Bypass > Mobile Session > Plain requests
    # Skip CloudScraper as it has SSL issues with newzimbabwe.com
    
    # Try SSL bypass session first (most reliable for newzimbabwe.com)
    try:
        if create_ssl_bypass_session:
            s = create_ssl_bypass_session()
            logger.debug("Created SSL bypass session")
            return s
    except Exception as e:
        logger.debug(f"SSL bypass session failed: {e}")
    
    # Try robust session without CloudScraper
    try:
        if create_robust_session:
            s = create_robust_session(use_cloudscraper=False, verify_ssl=False)
            logger.debug("Created robust session (no CloudScraper, no SSL verification)")
            return s
    except Exception as e2:
        logger.debug(f"Robust session failed: {e2}")
    
    # Ultimate fallback: plain requests with SSL bypass
    logger.warning("Using plain requests with SSL bypass (newzimbabwe.com SSL issues)")
    import ssl
    from requests.adapters import HTTPAdapter
    
    class LegacyHTTPSAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            try:
                ctx.set_ciphers('DEFAULT@SECLEVEL=1')
            except Exception:
                pass
            kwargs['ssl_context'] = ctx
            return super().init_poolmanager(*args, **kwargs)
    
    s = requests.Session()
    s.verify = False
    s.mount('https://', LegacyHTTPSAdapter())
    s.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
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
        "div.td-post-content",
        ".single-content",
        ".entry-content",
        ".post-content",
        ".content",
        ".article-content",
        "article",
        "main",
    ]:
        container = soup.select_one(sel)
        if not container:
            continue
        parts: List[str] = []
        for p in container.find_all(["p"], recursive=True):
            t = p.get_text(strip=True)
            if t and len(t) > 25:
                parts.append(t)
        if parts and len(parts) >= 2:
            return "\n\n".join(f"<p>{x}</p>" for x in parts[:15])
    parts = []
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if t and len(t) > 25:
            parts.append(t)
    if parts and len(parts) >= 2:
        return "\n\n".join(f"<p>{x}</p>" for x in parts[:15])
    return ""


def scrape_newzimbabwe(max_articles: int = 12, fast: bool = False) -> List[Dict]:
    """Scrape NewZimbabwe articles.
    When fast=True: use smaller delays, avoid heavy JS rendering, shorter timeouts.
    """
    articles: List[Dict] = []

    start_urls = [
        "https://www.newzimbabwe.com/category/news/",
        "https://www.newzimbabwe.com/",
        "https://newzimbabwe.com/category/news/",
        "https://newzimbabwe.com/",
        "http://www.newzimbabwe.com/category/news/",
        "http://www.newzimbabwe.com/",
        "http://newzimbabwe.com/category/news/",
        "http://newzimbabwe.com/",
    ]

    if fast:
        # Cap the number of articles for speed
        max_articles = min(max_articles, 6)

    client = _create_client()
    soup: Optional[BeautifulSoup] = None
    base_url: Optional[str] = None

    # Try multiple landing pages
    for url in start_urls:
        try:
            time.sleep(random.uniform(0.1, 0.3) if fast else random.uniform(0.8, 1.6))
            if fast:
                # Fast path: no rendering, smaller timeout
                r = client.get(url, timeout=12)
            else:
                # Try SmartCrawler with Playwright rendering fallback first
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
        logger.error("NewZimbabwe: no homepage accessible")
        return articles

    # Collect candidate link elements from multiple selectors
    link_selectors = [
        "h2.entry-title a",
        ".td-module-title a",
        "article h2 a",
        ".wp-block-post-title a",
        ".elementor-post__title a",
        ".jeg_post_title a",
        ".jeg_block_content .jeg_post a",
        "h3 a",
        "article a[href*='/20']",  # year in URL
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
    # Deduplicate nodes while preserving order
    _seen_nodes = set()
    _deduped = []
    for el in link_elems:
        _id = id(el)
        if _id in _seen_nodes:
            continue
        _seen_nodes.add(_id)
        _deduped.append(el)
    link_elems = _deduped

    # Fallback: collect anchors that look like article links
    if not link_elems:
        anchors = soup.find_all("a", href=True)
        host = urlparse(base_url).netloc.lower()
        for a in anchors:
            href = (a.get("href", "") or "").strip()
            txt = a.get_text(strip=True)
            if not href or not txt or len(txt) < 8:
                continue
            h = href.lower()
            if any(x in h for x in ["/category/", "/tag/", "/author/", "/page/", "/search/", "/contact", "/about"]):
                continue
            # More permissive: allow host links with title-like text; prefer year/news patterns but don't require
            if (host in h or "newzimbabwe.com" in h):
                if ("/20" in h or "/news/" in h) or (len(txt) > 20 and len(txt) < 200):
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
            if not isinstance(a, Tag):
                continue
            href = (a.get("href", "") or "").strip()
            # Normalize and validate title
            text = a.get_text(strip=True)
            from utils.scraper import clean_headline, is_valid_headline
            title = clean_headline(text)
            if not href or not is_valid_headline(title):
                continue

            href = _absolutize(href, base_url)
            low = href.lower()
            if any(x in low for x in ["/category/", "/tag/", "/author/", "/page/"]):
                continue
            if href in seen:
                continue
            seen.add(href)

            # Fetch article
            time.sleep(random.uniform(0.1, 0.3) if fast else random.uniform(0.8, 1.6))
            # Build URL variants to try (handle HTTPS handshake issues by downgrading to HTTP)
            href_variants = [href]
            hlow = href.lower()
            if hlow.startswith("https://"):
                href_variants.append("http://" + href[8:])
            elif hlow.startswith("http://"):
                href_variants.append("https://" + href[7:])

            ar = None
            fetched = False
            for href_try in href_variants:
                try:
                    if fast:
                        # Fast path: use client only, smaller timeout
                        ar = client.get(href_try, timeout=12)
                        if ar.status_code != 200 or not ar.text:
                            # quick retry once
                            time.sleep(random.uniform(0.3, 0.8))
                            ar = client.get(href_try, timeout=14)
                        if ar.status_code == 200 and ar.text:
                            href = href_try  # use the working variant
                            fetched = True
                            break
                    else:
                        # Rendered fetch then fallback to client with retry
                        ar = crawler.get(href_try, render=True)
                        if ar.status_code != 200 or not ar.text:
                            ar = client.get(href_try, timeout=25)
                        if ar.status_code != 200 or not ar.text:
                            # one more retry with small backoff
                            time.sleep(random.uniform(0.8, 1.6))
                            ar = client.get(href_try, timeout=28)
                        if ar.status_code == 200 and ar.text:
                            href = href_try  # use the working variant
                            fetched = True
                            break
                except Exception:
                    continue

            if not fetched or not ar or ar.status_code != 200 or not ar.text:
                continue

            art_soup = BeautifulSoup(ar.text if hasattr(ar, 'text') else ar.text, "html.parser")
            art_soup = clean_article_html(art_soup)

            # Extract content with robust fallbacks
            try:
                parts = extract_content_paragraphs(art_soup)
            except Exception as ex:
                logger.warning(f"content extraction error: {ex}")
                parts = []
            body_html = ""
            try:
                body_html = render_paragraphs_html(parts) if parts else ""
            except Exception as ex:
                logger.warning(f"render error: {ex}")
                body_html = ""
            if not body_html:
                alt = _fallback_article_content(art_soup)
                if not alt:
                    continue
                body_html = alt

            # Extract image URL safely
            image_url = None
            try:
                image_url = extract_featured_image(art_soup, href)
            except Exception as ex:
                logger.warning(f"image extraction error: {ex}")
                image_url = None

            # Hand off assembly (wrapper/paywall/CTA) to the poster for consistency
            # Provide raw article HTML and plain body so the poster can extract paragraphs and wrap
            try:
                original_html = ar.text if hasattr(ar, 'text') and ar.text else ''
            except Exception:
                original_html = ''

            content_html = body_html  # plain article body; no local summary/paywall/labels

            data: Dict = {
                "title": title,
                "content": content_html,
                "original_html": original_html,
                "source_url": href,
                "source": "NewZimbabwe",
            }
            if image_url:
                data["image_url"] = image_url

            articles.append(data)
        except Exception as e:
            logger.warning(f"NewZimbabwe item failed: {e}")
            continue

    return articles


def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    return scrape_newzimbabwe(max_articles=max_articles)




def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_newzimbabwe(max_articles=max_articles)
    
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
    items = scrape_newzimbabwe(8)
    print(f"Found {len(items)} NewZimbabwe articles")
    for i, it in enumerate(items, 1):
        print(i, it["title"][:90])
        print("URL:", it.get("source_url"))
        print("Image:", it.get("image_url"))
