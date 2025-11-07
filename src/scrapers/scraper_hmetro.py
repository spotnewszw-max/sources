from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
H-Metro scraper
- Targets links that look like /YYYY/MM/DD/... on the homepage
- Extracts title, content, optional featured image
"""

import logging
import time
import random
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import discover_articles_via_rss, validate_article_quality, extract_article_content
from src.utils.smart_utils import SmartFetcher, SmartExtractor

try:
    import cloudscraper
except Exception:
    cloudscraper = None  # type: ignore

logger = logging.getLogger(__name__)

# New H-Metro lives under Herald Online section
PRIMARY_BASE = "https://www.heraldonline.co.zw"
# Likely section paths used on Herald Online for H-Metro
SECTION_CANDIDATES = [
    "/hmetro/",
    "/h-metro/",
    "/hmetro-news/",
    "/h-metro-news/",
    "/category/hmetro/",
    "/category/h-metro/",
    "/category/hmetro-news/",
    "/category/h-metro-news/",
    "/section/hmetro/",
    "/section/h-metro/",
]
BASE_URLS = [
    # Herald Online (new home)
    "https://www.heraldonline.co.zw",
    "https://heraldonline.co.zw",
    "http://www.heraldonline.co.zw",
    "http://heraldonline.co.zw",
    # Herald (classic) as additional fallback
    "https://www.herald.co.zw",
    "https://herald.co.zw",
    "http://www.herald.co.zw",
    "http://herald.co.zw",
    # Legacy H-Metro domains kept as fallback
    "https://www.hmetro.co.zw",
    "https://hmetro.co.zw",
    "http://www.hmetro.co.zw",
    "http://hmetro.co.zw",
]


def _create_session():
    """Create an HTTP session with basic anti-bot headers."""
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


def _absolute(u: str, base: str = PRIMARY_BASE) -> str:
    if not u:
        return u
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("/"):
        return urljoin(base, u)
    if not u.startswith("http"):
        return urljoin(base, u)
    return u


def _extract_image(soup: BeautifulSoup) -> Optional[str]:
    # Common meta/image selectors
    meta = soup.find("meta", attrs={"property": "og:image"}) or soup.find(
        "meta", attrs={"name": "twitter:image"}
    )
    if meta:
        src = meta.get("content")
        if src:
            return _absolute(src)

    img = soup.select_one(
        # Newspaper theme common featured image containers
        "meta[property='og:image'], meta[name='twitter:image'], .td-post-featured-image img, .td-module-thumb img, img.wp-post-image, .featured-image img, .post-image img, img[class*='featured'], img[class*='post'], img"
    )
    if img:
        for attr in ("src", "data-src", "data-lazy-src"):
            val = img.get(attr)
            if val:
                return _absolute(val)
    return None


def _extract_article_content(soup: BeautifulSoup) -> str:
    selectors = [
        # Herald / Newspaper theme specific
        ".td-post-content",
        ".tdb-block-inner .tdb-single-content",
        ".td-post-content .td-fix-index",
        # Common containers
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
        # Remove common junk blocks
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

    # Fallback: paragraphs
    parts = []
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if t and len(t) > 50:
            parts.append(t)
    if parts:
        return "\n\n".join(f"<p>{x}</p>" for x in parts[:12])
    return ""


def _get_article(url: str, session, fetcher: Optional[SmartFetcher] = None) -> Optional[Tuple[str, str, Optional[str]]]:
    """Return (title, content_html, image_url) for an article page with render fallback"""
    time.sleep(random.uniform(1.0, 2.5))
    html = None
    # Fast path: session
    try:
        r = session.get(url, timeout=30)
        if r.status_code == 200:
            html = r.text
    except Exception:
        html = None

    # Render fallback if needed
    if not html and fetcher is not None:
        try:
            html = fetcher.get_html(url, render=True, timeout=35)
        except Exception:
            html = None

    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Title
    title = None
    for sel in ("h1", ".entry-title", ".post-title", "title"):
        el = soup.select_one(sel) if sel != "title" else soup.find("title")
        if el:
            title = el.get_text(strip=True)
            if title and len(title) > 10:
                break
    if not title:
        return None

    # Prefer SmartExtractor, then fallback extractor
    content_html = SmartExtractor.extract_content_html(soup, url) or extract_article_content(soup, url) or _extract_article_content(soup)
    if not content_html:
        return None

    img = _extract_image(soup)

    # Append attribution
    content_html += f"\n\n<p><em>Source: <a href='{url}' target='_blank'>H-Metro</a></em></p>"
    return title, content_html, img


def _discover_section_rss(session, fetcher: Optional[SmartFetcher], bases: List[str], sections: List[str], max_items: int = 30) -> List[Dict]:
    """Try to fetch section/category RSS feeds with anti-bot fallbacks and parse <item>s."""
    items: List[Dict] = []
    rss_suffixes = ["feed/", "?feed=rss2", "rss/", "rss.xml", "feed.xml"]

    for base in bases:
        for sec in sections:
            section_base = urljoin(base, sec)
            # Normalize to ensure trailing slash once
            section_base = section_base.rstrip("/") + "/"
            candidates = [section_base + suf for suf in rss_suffixes]
            for feed_url in candidates:
                text = None
                # 1) session first
                try:
                    r = session.get(feed_url, timeout=20)
                    if getattr(r, "status_code", 0) == 200 and getattr(r, "text", ""):
                        text = r.text
                    else:
                        logger.debug(f"RSS status {getattr(r, 'status_code', 'NA')} for {feed_url}")
                except Exception as e:
                    logger.debug(f"RSS session fetch failed for {feed_url}: {e}")
                    text = None
                # 2) SmartFetcher (cloudscraper/httpx)
                if not text and fetcher is not None:
                    try:
                        text = fetcher.get_html(feed_url, render=False, timeout=20)
                    except Exception as e:
                        logger.debug(f"RSS smart fetch failed for {feed_url}: {e}")
                        text = None
                if not text:
                    continue
                try:
                    sx = BeautifulSoup(text, "xml")
                    found = sx.find_all("item")
                    logger.info(f"Parsed {len(found)} RSS items from {feed_url}")
                    for it in found:
                        if len(items) >= max_items:
                            return items
                        title = it.find("title").get_text(strip=True) if it.find("title") else ""
                        link_el = it.find("link")
                        link = link_el.get_text(strip=True) if link_el else ""
                        if title and link:
                            items.append({"title": title, "url": link})
                    if items:
                        return items
                except Exception as e:
                    logger.debug(f"RSS parse failed for {feed_url}: {e}")
                    continue
    return items


def _get_article(url: str, session, fetcher) -> Optional[Tuple[str, str, Optional[str]]]:
    """Extract article content from a Herald Online/H-Metro article page.
    
    Returns:
        Tuple of (title, content_html, image_url) or None if extraction fails
    """
    try:
        # Try SmartFetcher with rendering first (best for Cloudflare)
        html = None
        if fetcher:
            try:
                html = fetcher.get_html(url, render=True, timeout=30)
                if html and len(html) > 1000:  # Reasonable content length
                    logger.debug(f"SmartFetcher with rendering succeeded for {url}")
                else:
                    html = None
            except Exception as e:
                logger.debug(f"SmartFetcher rendering failed for {url}: {e}")
        
        # Fallback to SmartFetcher without rendering
        if not html and fetcher:
            try:
                html = fetcher.get_html(url, render=False, timeout=20)
                if html and len(html) > 1000:
                    logger.debug(f"SmartFetcher without rendering succeeded for {url}")
                else:
                    html = None
            except Exception as e:
                logger.debug(f"SmartFetcher no-render failed for {url}: {e}")
        
        # Last resort: regular session
        if not html:
            try:
                response = session.get(url, timeout=20)
                if response.status_code == 200 and response.text and len(response.text) > 1000:
                    html = response.text
                    logger.debug(f"Session request succeeded for {url}")
                else:
                    logger.debug(f"Session request failed: status={response.status_code}, length={len(response.text) if response.text else 0}")
            except Exception as e:
                logger.debug(f"Session request failed for {url}: {e}")
        
        if not html:
            logger.debug(f"No HTML content retrieved for {url}")
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = None
        title_selectors = [
            'h1.entry-title',
            'h1.post-title', 
            'h1.article-title',
            '.entry-header h1',
            '.post-header h1',
            'article h1',
            'h1',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 10:  # Reasonable title length
                    break
        
        # Extract content
        content_html = None
        content_selectors = [
            '.entry-content',
            '.post-content',
            '.article-content',
            '.content',
            'article .content',
            '.post-body',
            '.entry-body',
            'article',
            '.main-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Clean up the content
                for unwanted in content_elem.select('script, style, .advertisement, .ads, .social-share, .related-posts'):
                    unwanted.decompose()
                
                content_html = str(content_elem)
                if content_html and len(content_html) > 200:  # Reasonable content length
                    break
        
        # Extract image
        image_url = None
        image_selectors = [
            '.entry-content img',
            '.post-content img',
            '.article-content img',
            'article img',
            '.featured-image img',
            '.post-thumbnail img'
        ]
        
        for selector in image_selectors:
            img_elem = soup.select_one(selector)
            if img_elem:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src:
                    if src.startswith('//'):
                        image_url = 'https:' + src
                    elif src.startswith('/'):
                        image_url = 'https://www.heraldonline.co.zw' + src
                    elif src.startswith('http'):
                        image_url = src
                    break
        
        if title and content_html:
            logger.debug(f"Successfully extracted article: {title[:50]}...")
            return (title, content_html, image_url)
        else:
            logger.debug(f"Article extraction incomplete - title: {bool(title)}, content: {bool(content_html)}")
            return None
            
    except Exception as e:
        logger.debug(f"Article extraction failed for {url}: {e}")
        return None


def scrape_hmetro(max_articles: int = 10) -> List[Dict]:
    articles: List[Dict] = []
    session = _create_session()
    fetcher = SmartFetcher("H-Metro")

    try:
        # Simplified approach: try only the most likely working URLs
        priority_bases = [
            "https://www.heraldonline.co.zw",
            "https://www.herald.co.zw"
        ]
        
        priority_sections = [
            "/hmetro/",
            "/category/hmetro/",
            "/h-metro/"
        ]

        # 1) Try the known working H-Metro section directly
        hmetro_url = "https://www.heraldonline.co.zw/hmetro/"
        
        # Try RSS feed first
        rss_candidates = []
        feed_urls = [
            "https://www.heraldonline.co.zw/hmetro/feed/",
            "https://www.heraldonline.co.zw/hmetro/?feed=rss2"
        ]
        
        for feed_url in feed_urls:
            try:
                # Try with fetcher first (handles anti-bot better)
                text = fetcher.get_html(feed_url, render=False, timeout=20)
                if text:
                    sx = BeautifulSoup(text, "xml")
                    items = sx.find_all("item")[:max_articles * 2]
                    for it in items:
                        title_el = it.find("title")
                        link_el = it.find("link")
                        if title_el and link_el:
                            title = title_el.get_text(strip=True)
                            link = link_el.get_text(strip=True)
                            if title and link:
                                rss_candidates.append({"title": title, "url": link})
                    if rss_candidates:
                        logger.info(f"Found {len(rss_candidates)} RSS items from {feed_url}")
                        break
            except Exception as e:
                logger.debug(f"RSS failed for {feed_url}: {e}")
                # Fallback to session
                try:
                    r = session.get(feed_url, timeout=15)
                    if r.status_code == 200 and r.text:
                        sx = BeautifulSoup(r.text, "xml")
                        items = sx.find_all("item")[:max_articles * 2]
                        for it in items:
                            title_el = it.find("title")
                            link_el = it.find("link")
                            if title_el and link_el:
                                title = title_el.get_text(strip=True)
                                link = link_el.get_text(strip=True)
                                if title and link:
                                    rss_candidates.append({"title": title, "url": link})
                        if rss_candidates:
                            logger.info(f"Found {len(rss_candidates)} RSS items from {feed_url}")
                            break
                except Exception as e2:
                    logger.debug(f"Session RSS also failed for {feed_url}: {e2}")
                    continue

        # Process RSS candidates
        for item in rss_candidates[:max_articles * 2]:
            if len(articles) >= max_articles:
                break
            url = item.get("url", "").strip()
            title = item.get("title", "").strip()
            if not url or not title:
                continue
            
            url = _absolute(url)
            try:
                got = _get_article(url, session, fetcher)
                if got:
                    atitle, content_html, img = got
                    entry = {
                        "title": atitle or title,
                        "content": content_html,
                        "source_url": url,
                        "source": "H-Metro",
                        **({"image_url": img} if img else {}),
                    }
                    if validate_article_quality(entry):
                        articles.append(entry)
            except Exception as e:
                logger.debug(f"Failed to get article {url}: {e}")
                continue

        if len(articles) >= max_articles:
            logger.info("Found %d articles from H-Metro (RSS)", len(articles))
            return articles

        # 2) Fallback: try H-Metro section page directly with rendering
        if len(articles) < max_articles:
            try:
                # Use SmartFetcher with rendering to bypass anti-bot protection
                html = fetcher.get_html(hmetro_url, render=True, timeout=30)
                if html:
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Look for article links on H-Metro page
                    links = []
                    
                    # Find all links and filter for article-like URLs
                    for a in soup.find_all("a", href=True):
                        href = a.get("href", "").strip()
                        text = a.get_text(strip=True)
                        
                        if not href or not text or len(text) < 10:
                            continue
                            
                        full_url = _absolute(href)
                        
                        # Skip obvious non-articles
                        if any(x in href.lower() for x in ['#', 'javascript:', 'mailto:', '/category/', '/tag/', '/author/', '/page/', 'single-category']):
                            continue
                        
                        # Skip homepage and section pages
                        if (full_url.rstrip('/') in ['https://www.heraldonline.co.zw', 'https://www.herald.co.zw'] or
                            href.rstrip('/') in ['/', '/hmetro', '/h-metro']):
                            continue
                        
                        # Look for article-like patterns
                        is_article_like = False
                        
                        # Pattern 1: Contains date pattern /YYYY/MM/DD/
                        if re.search(r'/\d{4}/\d{1,2}/\d{1,2}/', href):
                            is_article_like = True
                        
                        # Pattern 2: Herald Online article with slug (no query params, decent length)
                        elif ('heraldonline.co.zw' in full_url and 
                              len(full_url.split('/')) >= 4 and 
                              not any(x in href for x in ['?', '=', '&']) and
                              len(href) > 20):
                            is_article_like = True
                        
                        # Pattern 3: Ends with a slug (not just a directory)
                        elif (href.endswith('/') and 
                              len(href.split('/')) >= 2 and 
                              len(href.split('/')[-2]) > 5):
                            is_article_like = True
                        
                        if is_article_like:
                            if full_url not in [l[0] for l in links]:
                                links.append((full_url, text))
                                if len(links) >= max_articles * 3:
                                    break
                    
                    logger.info(f"Found {len(links)} potential H-Metro article links")
                    
                    # Process the found links
                    for url, title in links[:max_articles * 2]:
                        if len(articles) >= max_articles:
                            break
                        try:
                            got = _get_article(url, session, fetcher)
                            if got:
                                atitle, content_html, img = got
                                entry = {
                                    "title": atitle or title,
                                    "content": content_html,
                                    "source_url": url,
                                    "source": "H-Metro",
                                    **({"image_url": img} if img else {}),
                                }
                                if validate_article_quality(entry):
                                    articles.append(entry)
                        except Exception as e:
                            logger.debug(f"Failed to get article {url}: {e}")
                            continue
                else:
                    logger.warning("Could not access H-Metro page even with rendering")
            except Exception as e:
                logger.debug(f"H-Metro page scraping failed: {e}")

        if len(articles) == 0:
            logger.warning("No H-Metro articles found - H-Metro content may no longer be available on Herald Online")
        else:
            logger.info("Found %d articles from H-Metro", len(articles))
        return articles
    except Exception as e:
        logger.error("Error scraping H-Metro: %s", e)
        return articles


def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    articles = scrape_hmetro(max_articles=max_articles)
    
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
    items = scrape_hmetro(3)
    print(f"Found {len(items)} H-Metro articles")
    for i, it in enumerate(items, 1):
        print(i, it["title"][:80])
