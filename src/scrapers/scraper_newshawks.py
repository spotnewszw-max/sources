from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
The NewsHawks scraper with enhanced features and image support
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import random
from urllib.parse import urljoin, urlparse
from src.scrapers.base_scraper import RobustSession
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)

def scrape_newshawks(max_articles=10):
    """
    Scrape The NewsHawks with image support
    """
    articles = []
    
    # Multiple URLs to try
    urls_to_try = [
        "https://thenewshawks.com/",
        "https://www.thenewshawks.com/",
        "https://thenewshawks.com/category/news/",
        "https://www.thenewshawks.com/category/news/"
    ]
    
    # Use RobustSession (prefers cloudscraper if available)
    session_helper = RobustSession("The NewsHawks")
    scraper = session_helper.session
    
    soup = None
    successful_url = None
    
    # Try different URLs
    for url in urls_to_try:
        try:
            logger.info(f"Trying NewsHawks URL: {url}")
            time.sleep(random.uniform(2, 4))
            
            response = scraper.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                successful_url = url
                logger.info(f"Successfully accessed NewsHawks: {url}")
                break
            else:
                logger.warning(f"Failed to access {url}: Status {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error accessing {url}: {e}")
            continue
    
    if not soup:
        logger.error("Could not access any NewsHawks URLs")
        return articles
    
    try:
        # Multiple selectors for article containers
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
            ".elementor-post",
            ".td-module-container"
        ]
        
        article_containers = []
        
        for selector in article_selectors:
            containers = soup.select(selector)
            if containers and len(containers) > 2:
                article_containers = containers
                logger.info(f"Using selector '{selector}' - found {len(containers)} containers")
                break
        
        if not article_containers:
            # Fallback: look for links that might be articles
            all_links = soup.find_all('a', href=True)
            potential_articles = []
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if (text and len(text) > 20 and len(text) < 200 and
                    ('thenewshawks.com' in href or href.startswith('/')) and
                    not any(skip in href.lower() for skip in ['/category/', '/tag/', '/author/', '/contact', '/about'])):
                    potential_articles.append(link)
            
            article_containers = potential_articles[:max_articles * 2]
            logger.info(f"Fallback approach found {len(article_containers)} potential articles")
        
        if not article_containers:
            logger.error("No articles found")
            return articles
        
        # Process articles
        processed_urls = set()
        
        for i, container in enumerate(article_containers):
            if len(articles) >= max_articles:
                break
                
            try:
                # Find link
                if container.name == 'a':
                    link_element = container
                else:
                    # Prefer anchors that look like post links within the container
                    cand_links = container.find_all("a", href=True)
                    link_element = None
                    for la in cand_links:
                        h = (la.get("href", "") or "").lower()
                        if not h:
                            continue
                        if any(x in h for x in ['/category/', '/tag/', '/author/', '/page/']):
                            continue
                        # Likely article if it has year or '/news/'
                        if any(x in h for x in ['/20', '/news/']):
                            link_element = la
                            break
                    if not link_element and cand_links:
                        link_element = cand_links[0]
                
                if not link_element:
                    continue
                
                link = link_element.get("href", "")
                if not link:
                    continue
                
                # Make URL absolute
                if link.startswith('/'):
                    link = urljoin(successful_url, link)
                elif not link.startswith('http'):
                    continue
                
                low_link = link.lower()
                # Skip taxonomy/section/advert pages
                if any(x in low_link for x in [
                    '/category/', '/tag/', '/author/', '/topics/', '/topic/', '/contact', '/about', '/advert', '/advertise', '/page/'
                ]):
                    continue
                
                if link in processed_urls:
                    continue
                processed_urls.add(link)
                
                # Get title with normalization/validation
                from utils.scraper import clean_headline, is_valid_headline
                title = clean_headline(link_element.get_text(strip=True))
                if not is_valid_headline(title):
                    for tag in ['h1', 'h2', 'h3', 'h4', '.title', '.headline', '.entry-title']:
                        title_elem = container.find(tag) if not tag.startswith('.') else container.select_one(tag)
                        if title_elem:
                            title = clean_headline(title_elem.get_text(strip=True))
                            if is_valid_headline(title):
                                break
                
                if not is_valid_headline(title):
                    continue
                
                logger.info(f"Processing NewsHawks article: {title[:50]}...")
                
                # Get article content and image
                content, image_url = get_newshawks_article_content(link, scraper)
                if not content or len(content) < 100:
                    logger.warning(f"Insufficient content for: {title[:50]}...")
                    continue
                
                article_data = {
                    "title": title,
                    "content": content,
                    "source_url": link,
                    "source": "The NewsHawks"
                }
                
                if image_url:
                    article_data["image_url"] = image_url
                
                articles.append(article_data)
                
                # Rate limiting
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                logger.warning(f"Error processing NewsHawks article {i}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(articles)} articles from NewsHawks")
        return articles
        
    except Exception as e:
        logger.error(f"Error scraping NewsHawks: {e}")
        return articles

def get_newshawks_article_content(url, scraper):
    """Get article content and image with retry logic; includes rendered fallback."""
    from utils.scraper import (
        crawler,
        extract_content_paragraphs,
        render_paragraphs_html,
        build_source_attribution,
    )

    max_retries = 2

    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(2, 4))

            # Primary attempt via provided session (cloudscraper/requests)
            response = scraper.get(url, timeout=25)
            if getattr(response, "status_code", 0) == 200 and getattr(response, "content", b""):
                soup = BeautifulSoup(response.content, "html.parser")

                # Remove unwanted elements
                for element in soup.find_all([
                    "script",
                    "style",
                    "nav",
                    "aside",
                    "footer",
                    "header",
                    "form",
                ]):
                    try:
                        element.decompose()
                    except Exception:
                        pass

                # Extract image early
                image_url = extract_article_image(soup, url)

                # Try site-specific selectors first
                content_selectors = [
                    ".entry-content",
                    ".post-content",
                    ".article-content",
                    ".content",
                    ".story-content",
                    ".news-content",
                    "div[class*='content']",
                    ".single-content",
                    ".wp-block-post-content",
                    ".elementor-widget-theme-post-content",
                    ".td-post-content",
                ]

                content_parts = []
                for selector in content_selectors:
                    content_div = soup.select_one(selector)
                    if content_div:
                        text_elements = content_div.find_all(["p", "div"], recursive=True)
                        for element in text_elements:
                            text = element.get_text(strip=True)
                            if text and len(text) > 30:
                                low = text.lower()
                                if not any(
                                    skip in low
                                    for skip in (
                                        "advertisement",
                                        "subscribe",
                                        "follow us",
                                        "share this",
                                        "related articles",
                                        "read more",
                                        "continue reading",
                                        "newsletter",
                                        "social media",
                                        "whatsapp",
                                        "telegram",
                                    )
                                ):
                                    content_parts.append(text)
                        if content_parts:
                            break

                # Fallback: shared extractor from the parsed soup
                if not content_parts:
                    parts = extract_content_paragraphs(soup)
                    if parts:
                        html = render_paragraphs_html(parts)
                        return html + "\n" + build_source_attribution(url, "The NewsHawks"), image_url

                if content_parts:
                    content_html = "\n\n".join([f"<p>{part}</p>" for part in content_parts[:12]])
                    return content_html + "\n" + build_source_attribution(url, "The NewsHawks"), image_url

            # Rendered fallback via SmartCrawler if primary path failed or produced no text
            ar = crawler.get(url, render=True)
            if getattr(ar, "status_code", 0) == 200 and getattr(ar, "text", ""):
                soup = BeautifulSoup(ar.text, "html.parser")
                image_url = extract_article_image(soup, url)
                parts = extract_content_paragraphs(soup)
                if parts:
                    html = render_paragraphs_html(parts)
                    return html + "\n" + build_source_attribution(url, "The NewsHawks"), image_url

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 10))
            continue

    return None, None

def extract_article_image(soup, base_url):
    """Extract featured image from article"""
    try:
        # Try different image selectors
        image_selectors = [
            'img[class*="featured"]',
            'img[class*="article"]',
            'img[class*="post"]',
            '.featured-image img',
            '.article-image img',
            '.post-image img',
            '.wp-post-image',
            'img[src*="upload"]',
            'img[src*="wp-content"]',
            'img[alt]',
            '.td-post-featured-image img'
        ]
        
        for selector in image_selectors:
            img = soup.select_one(selector)
            if img:
                img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if img_url:
                    # Make URL absolute
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = urljoin(base_url, img_url)
                    elif not img_url.startswith('http'):
                        img_url = urljoin(base_url, img_url)
                    
                    # Check if it's a valid image
                    if img_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                        return img_url
        
        return None
        
    except Exception as e:
        logger.warning(f"Error extracting image: {e}")
        return None

def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    articles = scrape_newshawks(max_articles=max_articles)
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


def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_newshawks(max_articles=max_articles)
    
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
    articles = scrape_newshawks(max_articles=3)
    print(f"Found {len(articles)} articles from NewsHawks")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Content length: {len(article['content'])}")
        print(f"   URL: {article['source_url']}")
        print(f"   Image: {article.get('image_url', 'None')}")
        print("-" * 50)
