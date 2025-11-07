from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Bulawayo24 scraper with enhanced features and image support
"""

from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import cloudscraper
import time
import random
import logging

# Ensure project root is on sys.path when running as a script
import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Configure logging
logger = logging.getLogger(__name__)

def clean_article_html(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove bylines, share buttons, ads, and other non-article elements."""
    selectors = [
        ".byline", ".author", ".post-meta", ".entry-meta",
        ".share", ".social", ".article-share", ".article-author",
        ".advertisement", ".ad", ".adsbygoogle", ".promo", ".wp-block-button",
        "#jp-post-flair", "#sharing", "#share-buttons", "#social-share", "#author-info"
    ]
    for sel in selectors:
        for tag in soup.select(sel):
            tag.decompose()
    return soup

def fetch_with_retry(url, headers, timeout=15, retries=1):
    for attempt in range(retries + 1):
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except requests.exceptions.Timeout:
            if attempt == retries:
                raise
            time.sleep(2)

def scrape_bulawayo24(max_articles=10) -> List[Dict]:
    """Scrape Bulawayo24 for latest articles with robust fallbacks."""
    articles = []
    start_urls = [
        "https://bulawayo24.com/index-id-news.html",
        "https://bulawayo24.com/index-id-business.html",
        "https://bulawayo24.com/index-id-sports.html",
        "https://bulawayo24.com/index-id-entertainment.html",
        "https://bulawayo24.com/index-id-opinion.html",
        "https://bulawayo24.com/",
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    seen = set()

    logger.info("Scraping Bulawayo24 with improved selectors")

    try:
        for url in start_urls:
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                print(f"Fetched {url} with status {resp.status_code}")
                soup = BeautifulSoup(resp.text, "html.parser")
                # Improved selectors for main, featured, and latest stories
                link_elems = []
                selectors_to_try = [
                    ".main_story a[href*='-byo-']",
                    ".featured_item h2 a[href*='-byo-']",
                    ".two_featured_stories h2 a[href*='-byo-']",
                    "#latest li a[href*='-byo-']",
                    "a[href*='-byo-']",  # More general fallback
                    "article a[href]",   # Very general fallback
                ]

                for selector in selectors_to_try:
                    found = soup.select(selector)
                    if found:
                        link_elems.extend(found)
                        logger.info(f"Selector '{selector}' found {len(found)} links")

                if not link_elems:
                    logger.warning(f"No link elements found on {url}")
                    continue
                # Remove duplicates
                links = []
                for a in link_elems:
                    href = a.get("href")
                    # Accept article-like links broadly (not only 'index-id-')
                    if not href or href in seen:
                        continue
                    # Keep only reasonable article paths
                    low = href.lower()
                    if not any(p in low for p in ['-byo-', '/news/', '/business/', '/sports/', '/entertainment/', '/opinion/', 'index-id-']):
                        continue
                    seen.add(href)
                    links.append(a)
                for a in links:
                    if len(articles) >= max_articles:
                        break
                    href = a.get("href")
                    low_href = (href or '').lower()
                    if any(x in low_href for x in ['/category', '/tag', '/author', '/contact', '/about', '/advert', '/advertise', '/page/']):
                        continue
                    from utils.scraper import clean_headline, is_valid_headline
                    raw_title = a.get_text(strip=True)
                    title = clean_headline(raw_title)
                    if not is_valid_headline(title):
                        continue
                    article_url = urljoin(url, href)
                    try:
                        ar = fetch_with_retry(article_url, headers, timeout=15, retries=2)
                    except Exception:
                        continue
                    if ar.status_code != 200 or not ar.text:
                        continue
                    art_soup = BeautifulSoup(ar.text, "html.parser")
                    art_soup = clean_article_html(art_soup)
                    content_div = art_soup.find("div", class_="article-content") or \
                                  art_soup.find("div", id="article") or \
                                  art_soup.find("div", class_="content") or \
                                  art_soup.find("div", class_="news-content") or \
                                  art_soup.find("div", class_="post-content") or \
                                  art_soup.find("article") or \
                                  art_soup.find("main")
                    if content_div:
                        paragraphs = [p.get_text(strip=True) for p in content_div.find_all("p") if len(p.get_text(strip=True)) > 20]
                    else:
                        paragraphs = [p.get_text(strip=True) for p in art_soup.find_all("p") if len(p.get_text(strip=True)) > 20]
                    if not paragraphs or len(paragraphs) < 2:
                        logger.warning(f"Insufficient content for {article_url}")
                        continue
                    body_html = "\n\n".join(f"<p>{x}</p>" for x in paragraphs[:15])
                    img = art_soup.find("img", {"class": "img-fluid"}) or art_soup.find("img", {"class": "article-image"}) or art_soup.find("img", class_="wp-post-image")
                    image_url = img.get("data-src") or img.get("src") if img else None
                    articles.append({
                        "title": title,
                        "content": body_html,
                        "source_url": article_url,
                        "source": "Bulawayo24",
                        "image_url": image_url
                    })
                    if len(articles) >= max_articles:
                        break
                if len(articles) >= max_articles:
                    break
            except Exception as e:
                logger.warning(f"Error processing listing {url}: {e}")
                continue

        logger.info(f"Total Bulawayo24 articles scraped: {len(articles)}")
        return articles

    except Exception as e:
        logger.error(f"Bulawayo24 scraping error: {e}")
        return []






def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_bulawayo24(max_articles=max_articles)
    
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
    items = scrape_bulawayo24(8)
    print(f"Found {len(items)} Bulawayo24 articles")
    for i, it in enumerate(items, 1):
        print(i, it["title"][:90])
        print("URL:", it.get("source_url"))
        print("Image:", it.get("image_url"))