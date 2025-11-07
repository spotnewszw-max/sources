from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Improved NewZimbabwe scraper with better error handling, summary on top, separator,
paywalled original content, and featured images.
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import random
import re
from urllib.parse import urljoin
import cloudscraper

# Ensure project utils are available
import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Shared utils
from src.scrapers.base_scraper import (
    extract_content_paragraphs,
    render_paragraphs_html,
    extract_featured_image,
    build_source_attribution,
)

# Configure logging
logger = logging.getLogger(__name__)

# ===== Deterministic extractive summarizer (no external APIs) =====
_def_sentence_splitter = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9(\["\'])')

def _split_sentences(text: str):
    try:
        t = re.sub(r"\s+", " ", (text or "").strip())
        if not t:
            return []
        raw = _def_sentence_splitter.split(t)
        out = []
        for s in raw:
            s = s.strip()
            if not s:
                continue
            if len(s) < 30:
                continue
            out.append(s)
        return out
    except Exception:
        return []

def _build_summary_from_paragraphs(paragraphs):
    """Return two HTML <p> blocks, 5–7 sentences each when possible."""
    if not paragraphs:
        return ""
    text = " ".join([re.sub(r"\s+", " ", p).strip() for p in paragraphs if p and len(p.strip()) > 0])
    sentences = _split_sentences(text)

    if len(sentences) >= 12:
        selected = sentences[:12]
    elif len(sentences) >= 10:
        selected = sentences[:10]
    else:
        selected = sentences[:min(len(sentences), 10)]

    if not selected:
        para1 = paragraphs[0].strip()
        para2 = (paragraphs[1] if len(paragraphs) > 1 else paragraphs[0]).strip()
        return f"<p>{para1}</p>\n\n<p>{para2}</p>"

    n = len(selected)
    p1_count = max(5, min(7, (n + 1) // 2))
    p1 = selected[:p1_count]
    p2 = selected[p1_count:]
    if len(p2) < 5 and n > 8:
        shift = min(len(p1) - 5, 5 - len(p2))
        if shift > 0:
            p2 = selected[p1_count - shift:]
            p1 = selected[:p1_count - shift]

    def endcap(s):
        return s if s.endswith(('.', '!', '?')) else s + '.'

    para1_html = " ".join(endcap(s) for s in p1)
    para2_html = " ".join(endcap(s) for s in p2) if p2 else ""

    if not para2_html:
        mid = max(1, len(p1) // 2)
        para1_html = " ".join(endcap(s) for s in p1[:mid])
        para2_html = " ".join(endcap(s) for s in p1[mid:])

    return f"<p>{para1_html}</p>\n\n<p>{para2_html}</p>"


def scrape_newzimbabwe_improved(max_articles=10):
    """
    Improved NewZimbabwe scraper with better error handling
    and requested content structure (summary + separator + paywalled original + image).
    """
    articles = []
    
    # Multiple URLs to try
    urls_to_try = [
        "https://www.newzimbabwe.com/category/news/",
        "https://www.newzimbabwe.com/",
        "https://newzimbabwe.com/category/news/",
        "https://newzimbabwe.com/"
    ]
    
    # Use CloudScraper to bypass potential blocking
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Enhanced headers
        scraper.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        
    except Exception as e:
        logger.warning(f"CloudScraper failed, using regular requests: {e}")
        scraper = requests.Session()
        scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    soup = None
    successful_url = None
    
    # Try different URLs until one works
    for url in urls_to_try:
        try:
            logger.info(f"Trying NewZimbabwe URL: {url}")
            time.sleep(random.uniform(2, 5))
            response = scraper.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                successful_url = url
                logger.info(f"Successfully accessed NewZimbabwe: {url}")
                break
            else:
                logger.warning(f"Failed to access {url}: Status {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error accessing {url}: {e}")
            continue
    
    if not soup:
        logger.error("Could not access any NewZimbabwe URLs")
        return articles
    
    try:
        # Multiple selectors to try for article containers
        article_selectors = [
            "article",
            ".post",
            ".entry",
            ".news-item",
            ".story",
            "[class*='post']",
            "[class*='article']",
            "[class*='news']",
            ".wp-block-post",
            ".entry-summary"
        ]
        
        article_containers = []
        
        for selector in article_selectors:
            containers = soup.select(selector)
            if containers and len(containers) > 2:
                article_containers = containers
                logger.info(f"Using selector '{selector}' - found {len(containers)} containers")
                break
        
        if not article_containers:
            logger.warning("No article containers found, trying fallback approach")
            all_links = soup.find_all('a', href=True)
            potential_articles = []
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if (text and 20 < len(text) < 200 and
                    ('newzimbabwe.com' in href or href.startswith('/')) and
                    not any(skip in href.lower() for skip in ['/category/', '/tag/', '/author/', '/page/', '/search/', '/contact', '/about'])):
                    potential_articles.append(link)
            article_containers = potential_articles[:max_articles * 2]
            logger.info(f"Fallback approach found {len(article_containers)} potential articles")
        
        if not article_containers:
            logger.error("No articles found with any method")
            return articles
        
        processed_urls = set()
        
        for i, container in enumerate(article_containers):
            if len(articles) >= max_articles:
                break
            try:
                if container.name == 'a':
                    link_element = container
                else:
                    link_element = container.find("a", href=True)
                if not link_element:
                    continue
                link = link_element.get("href", "")
                if not link:
                    continue
                if link.startswith('/'):
                    link = urljoin(successful_url, link)
                elif not link.startswith('http'):
                    continue
                if (any(skip in link.lower() for skip in ['/category/', '/tag/', '/author/', '/page/', '/search/', '/contact', '/about']) or
                    link in processed_urls):
                    continue
                processed_urls.add(link)

                title = link_element.get_text(strip=True)
                if not title or len(title) < 10:
                    for tag in ['h1', 'h2', 'h3', 'h4', '.title', '.headline', '.entry-title']:
                        title_elem = container.find(tag) if not tag.startswith('.') else container.select_one(tag)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            break
                if not title or len(title) < 10 or len(title) > 300:
                    continue
                if any(skip in title.lower() for skip in ['home', 'contact', 'about', 'privacy', 'terms', 'subscribe', 'follow']):
                    continue

                logger.info(f"Processing NewZimbabwe article: {title[:50]}...")
                result = get_newzimbabwe_article_content(link, scraper)
                if not result:
                    logger.warning(f"Insufficient content for: {title[:50]}...")
                    continue
                content_html, image_url = result

                data = {
                    "title": title,
                    "content": content_html,
                    "source_url": link,
                    "source": "NewZimbabwe",
                }
                if image_url:
                    data["image_url"] = image_url

                articles.append(data)
                time.sleep(random.uniform(3, 6))

            except Exception as e:
                logger.warning(f"Error processing NewZimbabwe article {i}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(articles)} articles from NewZimbabwe")
        return articles
        
    except Exception as e:
        logger.error(f"Error scraping NewZimbabwe: {e}")
        return articles


def get_newzimbabwe_article_content(url, scraper):
    """Fetch article page and build final HTML with summary, separator, paywall, and image.
    Returns tuple: (content_html, image_url) or None on failure.
    """
    max_retries = 2
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(2, 4))
            response = scraper.get(url, timeout=25)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract core parts via shared utils
            try:
                parts = extract_content_paragraphs(soup)
            except Exception:
                parts = []

            # Render original body with fallback
            body_html = ""
            try:
                body_html = render_paragraphs_html(parts) if parts else ""
            except Exception:
                body_html = ""
            if not body_html:
                # Fallback: use page paragraphs
                fallback_parts = []
                for p in soup.find_all('p'):
                    t = p.get_text(strip=True)
                    if t and len(t) > 40:
                        fallback_parts.append(t)
                if fallback_parts:
                    body_html = "\n\n".join(f"<p>{x}</p>" for x in fallback_parts[:12])
            if not body_html:
                return None

            # Featured image
            image_url = None
            try:
                image_url = extract_featured_image(soup, url)
            except Exception:
                image_url = None

            # Build top summary
            try:
                summary_paragraphs = parts if parts else [
                    p.get_text(strip=True) for p in soup.find_all('p')
                    if p and p.get_text(strip=True) and len(p.get_text(strip=True)) > 40
                ][:12]
                summary_html = _build_summary_from_paragraphs(summary_paragraphs)
            except Exception:
                summary_html = ""

            # Visible image at top if available
            image_html = f"<p><img src=\"{image_url}\" alt=\"\" /></p>" if image_url else ""

            # Separator text
            separator_html = "<hr /><p><strong>Below is the original article from the original source.</strong></p><hr />"

            # Paywalled original with source attribution inside
            paywalled_html = (
                "[paywall]\n" + body_html + "\n" + build_source_attribution(url, "NewZimbabwe") + "\n[/paywall]"
            )

            content_html = "\n".join(x for x in [image_html, summary_html, separator_html, paywalled_html] if x)
            return content_html, image_url

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 10))
            continue
    return None

def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_newzimbabwe_improved(max_articles=max_articles)
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

# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    articles = scrape_newzimbabwe_improved(max_articles=5)
    print(f"Found {len(articles)} articles from NewZimbabwe")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Content length: {len(article['content'])}")
        print(f"   URL: {article['source_url']}")
        print(f"   Image: {article.get('image_url')}")
        print("-" * 50)
