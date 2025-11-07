from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
The Standard Zimbabwe scraper with enhanced features
"""

from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import time
import random
import logging
from src.scrapers.base_scraper import RobustSession

from src.scrapers.base_scraper import (
    extract_published_date, extract_featured_image,
    render_paragraphs_html, build_source_attribution, extract_content_paragraphs,
)

# Configure logging
logger = logging.getLogger(__name__)

def clean_article_html(soup: BeautifulSoup) -> BeautifulSoup:
    selectors = [
        ".byline", ".author", ".post-meta", ".entry-meta",
        ".share", ".social", ".advertisement", ".ad", ".adsbygoogle",
        ".promo", ".wp-block-button", "#jp-post-flair", "#sharing",
        "#share-buttons", "#social-share", "#author-info"
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

def scrape_standard(max_articles=10) -> List[Dict]:
    articles = []
    start_urls = [
        "https://www.thestandard.co.zw/",
        "https://www.thestandard.co.zw/news",
        "https://www.thestandard.co.zw/business",
        "https://www.thestandard.co.zw/sport",
        "https://www.thestandard.co.zw/standard-people",
        "https://www.thestandard.co.zw/standard-style",
        "https://www.thestandard.co.zw/technology",
        "https://www.thestandard.co.zw/agriculture",
        "https://www.thestandard.co.zw/education",
        "https://www.thestandard.co.zw/opinion-and-analysis",
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    seen = set()

    logger.info("Scraping The Standard")

    try:
        for url in start_urls:
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                print(f"Fetched {url} with status {resp.status_code}")
                soup = BeautifulSoup(resp.text, "html.parser")
                link_elems = []
                # Main/top stories
                link_elems += soup.select(".mb-4 > a.text-dark")
                link_elems += soup.select(".card .card-body a.text-dark")
                link_elems += soup.select(".boda-bottom > a.text-dark")
                link_elems += soup.select(".mt-3.boda-bottom > a.text-dark")
                # Sidebar/trending
                link_elems += soup.select(".sub-title a.text-dark")
                link_elems += soup.select(".sub-title.mb-2")
                link_elems += soup.select(".sub-title.mb-3")
                # Remove duplicates
                links = []
                for a in link_elems:
                    href = a.get("href")
                    if not href or href in seen or not href.startswith("http"):
                        continue
                    seen.add(href)
                    links.append(a)
                for a in links:
                    if len(articles) >= max_articles:
                        break
                    href = a.get("href")
                    title = a.get_text(strip=True)
                    if not title or len(title) < 8:
                        continue
                    article_url = href
                    # Fetch article page with retry
                    try:
                        ar = fetch_with_retry(article_url, headers, timeout=15, retries=1)
                    except Exception:
                        continue
                    if ar.status_code != 200 or not ar.text:
                        continue
                    art_soup = BeautifulSoup(ar.text, "html.parser")
                    art_soup = clean_article_html(art_soup)
                    # Main content: try main content div, fallback to all <p>
                    content_div = art_soup.find("div", class_="article-content") or \
                                  art_soup.find("div", id="article") or \
                                  art_soup.find("div", class_="content") or \
                                  art_soup.find("div", class_="row") or \
                                  art_soup.find("div", class_="card-body")
                    if content_div:
                        paragraphs = [p.get_text(strip=True) for p in content_div.find_all("p") if len(p.get_text(strip=True)) > 30]
                    else:
                        paragraphs = [p.get_text(strip=True) for p in art_soup.find_all("p") if len(p.get_text(strip=True)) > 30]
                    if not paragraphs:
                        continue
                    body_html = "\n\n".join(f"<p>{x}</p>" for x in paragraphs[:12])
                    # Featured image
                    img = art_soup.find("img", class_="img-fluid") or art_soup.find("img", class_="style-image") or art_soup.find("img")
                    image_url = img["src"] if img and img.has_attr("src") else None
                    articles.append({
                        "title": title,
                        "url": article_url,
                        "html": body_html,
                        "image_url": image_url
                    })
                    if len(articles) >= max_articles:
                        break
                if len(articles) >= max_articles:
                    break
            except Exception as e:
                logger.warning(f"Error processing listing {url}: {e}")
                continue

        logger.info(f"Total Standard articles scraped: {len(articles)}")
        return articles

    except Exception as e:
        logger.error(f"Standard scraping error: {e}")
        return []

def scrape_thestandard(max_articles=10):
    """
    Scrape The Standard Zimbabwe news with image support
    """
    articles = []
    urls_to_try = [
        "https://www.thestandard.co.zw/",
        "https://thestandard.co.zw/",
        "https://www.thestandard.co.zw/category/local-news/",
        "https://thestandard.co.zw/category/local-news/"
    ]
    # Use RobustSession (prefers cloudscraper if available)
    session_helper = RobustSession("The Standard")
    scraper = session_helper.session

    soup = None
    successful_url = None
    for url in urls_to_try:
        try:
            logger.info(f"Trying The Standard URL: {url}")
            time.sleep(random.uniform(2, 4))
            response = scraper.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                successful_url = url
                logger.info(f"Successfully accessed The Standard: {url}")
                break
            else:
                logger.warning(f"Failed to access {url}: Status {response.status_code}")
        except Exception as e:
            logger.warning(f"Error accessing {url}: {e}")
            continue

    if not soup:
        logger.error("Could not access any The Standard URLs")
        return articles

    # Use link selectors instead of container selectors
    link_selectors = [
        ".mb-4 > a.text-dark",
        ".card .card-body a.text-dark",
        ".boda-bottom > a.text-dark",
        ".mt-3.boda-bottom > a.text-dark",
        ".sub-title a.text-dark"
    ]
    link_elems = []
    for selector in link_selectors:
        link_elems += soup.select(selector)

    seen = set()
    links = []
    for a in link_elems:
        href = a.get("href")
        if not href or href in seen or not href.startswith("http"):
            continue
        seen.add(href)
        links.append(a)

    logger.info(f"Found {len(links)} article links")
    processed_urls = set()
    for a in links:
        if len(articles) >= max_articles:
            break
        href = a.get("href")
        title = a.get_text(strip=True)
        if not title or len(title) < 10:
            continue
        link = href
        if link in processed_urls:
            continue
        processed_urls.add(link)
        logger.info(f"Processing The Standard article: {title[:50]}...")
        content, image_url = get_thestandard_article_content(link, scraper)
        if not content or len(content) < 100:
            logger.warning(f"Insufficient content for: {title[:50]}...")
            continue
        article_data = {
            "title": title,
            "content": content,
            "source_url": link,
            "source": "The Standard"
        }
        if image_url:
            article_data["image_url"] = image_url
        articles.append(article_data)
        time.sleep(random.uniform(3, 6))

    logger.info(f"Successfully scraped {len(articles)} articles from The Standard")
    return articles

def get_thestandard_article_content(url, scraper):
    """Get article content and image with retry logic"""
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(2, 4))
            
            response = scraper.get(url, timeout=25)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header', 'form']):
                element.decompose()
            
            # Extract image and published
            image_url = extract_featured_image(soup, url)
            published = extract_published_date(soup)
            
            # Prefer shared content extractor, fallback to local
            parts = extract_content_paragraphs(soup)
            content_html = ''
            if parts:
                content_html = render_paragraphs_html(parts)
            else:
                # Try different content selectors
                content_selectors = [
                    ".entry-content",
                    ".post-content",
                    ".article-content",
                    ".content",
                    ".story-content",
                    ".news-content",
                    "div[class*='content']",
                    ".single-content",
                    ".td-post-content",
                    ".elementor-widget-theme-post-content"
                ]
                
                content_parts = []
                for selector in content_selectors:
                    content_div = soup.select_one(selector)
                    if content_div:
                        text_elements = content_div.find_all(['p', 'div'], recursive=True)
                        for element in text_elements:
                            text = element.get_text(strip=True)
                            if text and len(text) > 30:
                                if not any(skip in text.lower() for skip in [
                                    'advertisement', 'subscribe', 'follow us', 'share this',
                                    'related articles', 'read more', 'continue reading',
                                    'newsletter', 'social media'
                                ]):
                                    content_parts.append(text)
                        break
                if not content_parts:
                    paragraphs = soup.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 50:
                            if not any(skip in text.lower() for skip in ['advertisement', 'subscribe']):
                                content_parts.append(text)
                if content_parts:
                    content_html = '\n\n'.join([f"<p>{part}</p>" for part in content_parts[:12]])
            
            if content_html:
                source_attribution = build_source_attribution(url, 'The Standard', published)
                return content_html + '\n' + source_attribution, image_url
            
            return None, None
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 10))
            continue
    
    return None, None

def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    # Try the enhanced scraper first, fallback to basic one
    try:
        articles = scrape_thestandard(max_articles=max_articles)
        if not articles:
            articles = scrape_standard(max_articles=max_articles)
    except Exception:
        articles = scrape_standard(max_articles=max_articles)
    
    # Convert to expected format
    result = []
    for article in articles:
        result.append({
            "title": article.get("title", ""),
            "url": article.get("source_url", "") or article.get("url", ""),
            "html": article.get("content", "") or article.get("html", ""),
            "image_url": article.get("image_url")
        })
    return result

# Test function


def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_thestandard(max_articles=max_articles)
    
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
    articles = scrape_thestandard(max_articles=3)
    print(f"Found {len(articles)} articles from The Standard")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Content length: {len(article['content'])}")
        print(f"   URL: {article['source_url']}")
        print(f"   Image: {article.get('image_url', 'None')}")
        print("-" * 50)
