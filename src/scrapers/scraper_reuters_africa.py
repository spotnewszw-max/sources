from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Reuters Africa scraper - covers Zimbabwe and Southern Africa news
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import random
from urllib.parse import urljoin, urlparse

# Configure logging
logger = logging.getLogger(__name__)

def scrape_reuters_africa(max_articles=6):
    """
    Scrape Reuters Africa news with Zimbabwe focus
    """
    articles = []
    
    # Reuters Africa URLs
    urls_to_try = [
        "https://www.reuters.com/world/africa/",
        "https://www.reuters.com/places/africa/",
        "https://www.reuters.com/world/"
    ]
    
    # Enhanced headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    soup = None
    successful_url = None
    
    # Try different URLs until one works
    for url in urls_to_try:
        try:
            logger.info(f"Trying Reuters URL: {url}")
            
            # Random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                successful_url = url
                logger.info(f"Successfully accessed Reuters: {url}")
                break
            else:
                logger.warning(f"Failed to access {url}: Status {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error accessing {url}: {e}")
            continue
    
    if not soup:
        logger.error("Could not access any Reuters URLs")
        return articles
    
    # Multiple selectors to try
    selectors_to_try = [
        '[data-testid="MediaStoryCard"]',
        '.story-card',
        'article',
        '.media-story-card',
        '[data-module="MediaStory"]'
    ]
    
    article_containers = []
    used_selector = None
    
    for selector in selectors_to_try:
        containers = soup.select(selector)
        if containers and len(containers) > 3:
            article_containers = containers
            used_selector = selector
            logger.info(f"Using selector '{selector}' - found {len(containers)} containers")
            break
    
    if not article_containers:
        logger.warning("No article containers found")
        return articles
    
    # Process articles
    processed_count = 0
    for container in article_containers[:max_articles * 2]:  # Get more to filter
        try:
            # Extract title
            title_elem = container.select_one('h1, h2, h3, h4, [data-testid="Heading"], .story-title')
            if not title_elem:
                continue
                
            title = title_elem.get_text(strip=True)
            if not title or len(title) < 10:
                continue
            
            # Filter for Zimbabwe/Africa relevant content
            title_lower = title.lower()
            content_text = container.get_text().lower()
            
            if not any(keyword in title_lower or keyword in content_text for keyword in [
                'zimbabwe', 'africa', 'southern africa', 'harare', 'bulawayo',
                'mugabe', 'mnangagwa', 'zanu', 'mdc', 'sadc', 'zambia', 'botswana',
                'south africa', 'mozambique', 'malawi'
            ]):
                continue
            
            # Extract URL
            link_elem = container.select_one('a[href]')
            if not link_elem:
                continue
                
            article_url = link_elem.get('href')
            if article_url:
                if article_url.startswith('/'):
                    article_url = urljoin('https://www.reuters.com', article_url)
                elif not article_url.startswith('http'):
                    continue
            else:
                continue
            
            # Extract summary/content
            summary_elem = container.select_one('[data-testid="Body"], .story-body, p')
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Extract image
            img_elem = container.select_one('img')
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
                if image_url and image_url.startswith('/'):
                    image_url = urljoin('https://www.reuters.com', image_url)
            
            # Get full article content
            full_content = get_full_article_content(article_url, session)
            content = full_content if full_content else summary
            
            if content and len(content) > 50:
                article_data = {
                    'title': title,
                    'content': content,
                    'url': article_url,
                    'source': 'Reuters Africa',
                    'source_url': article_url
                }
                
                if image_url:
                    article_data['image_url'] = image_url
                
                articles.append(article_data)
                processed_count += 1
                logger.info(f"Processing Reuters article: {title[:50]}...")
                
                if processed_count >= max_articles:
                    break
                    
                # Delay between articles
                time.sleep(random.uniform(1, 2))
                
        except Exception as e:
            logger.error(f"Error processing Reuters article: {e}")
            continue
    
    logger.info(f"Successfully scraped {len(articles)} articles from Reuters Africa")
    return articles

def get_full_article_content(url, session):
    """Get full article content from Reuters article page"""
    try:
        time.sleep(random.uniform(1, 2))
        response = session.get(url, timeout=15)
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try different content selectors
        content_selectors = [
            '[data-testid="paragraph"]',
            '.article-body',
            '.story-body',
            '[data-testid="ArticleBody"]',
            '.paywall-article'
        ]
        
        content_parts = []
        for selector in content_selectors:
            content_elems = soup.select(selector)
            if content_elems:
                for elem in content_elems:
                    # Remove unwanted elements
                    for unwanted in elem.select('script, style, .ad, .advertisement'):
                        unwanted.decompose()
                    
                    text = elem.get_text(strip=True)
                    if text and len(text) > 20:
                        content_parts.append(text)
                
                if content_parts:
                    full_content = ' '.join(content_parts)
                    if len(full_content) > 100:
                        return full_content[:2000]  # Limit content length
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting full content from {url}: {e}")
        return None

def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_reuters_africa(max_articles=max_articles)
    # Convert to expected format
    result = []
    for article in articles:
        result.append({
            "title": article.get("title", ""),
            "url": article.get("source_url", "") or article.get("url", ""),
            "html": article.get("content", ""),
            "image_url": article.get("image_url")
        })
    return result

if __name__ == "__main__":
    # Test the scraper
    articles = scrape_reuters_africa(3)
    print(f"Found {len(articles)} articles")
    for article in articles:
        print(f"- {article['title']}")
        print(f"  URL: {article['url']}")
        if 'image_url' in article:
            print(f"  Image: {article['image_url']}")
        print()