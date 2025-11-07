from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Al Jazeera Africa scraper - covers Zimbabwe news
"""

import requests
import cloudscraper
from bs4 import BeautifulSoup
import time
import logging
import random
from urllib.parse import urljoin, urlparse

# Configure logging
logger = logging.getLogger(__name__)

def scrape_aljazeera(max_articles=6):
    """
    Scrape Al Jazeera Africa news with Zimbabwe focus
    """
    articles = []
    
    # Al Jazeera Africa URLs
    urls_to_try = [
        "https://www.aljazeera.com/where/africa/",
        "https://www.aljazeera.com/news/",
        "https://www.aljazeera.com/africa/"
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
    
    try:
        session = cloudscraper.create_scraper()
    except:
        session = requests.Session()
    session.headers.update(headers)
    
    soup = None
    successful_url = None
    
    # Try different URLs until one works
    for url in urls_to_try:
        try:
            logger.info(f"Trying Al Jazeera URL: {url}")
            
            # Random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                successful_url = url
                logger.info(f"Successfully accessed Al Jazeera: {url}")
                break
            else:
                logger.warning(f"Failed to access {url}: Status {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error accessing {url}: {e}")
            continue
    
    if not soup:
        logger.error("Could not access any Al Jazeera URLs")
        return articles
    
    # Multiple selectors to try
    selectors_to_try = [
        'article',
        '.gc__content',
        '.featured-articles-list article',
        '.topics-sec-item',
        '[data-testid="post-teaser"]'
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
            title_elem = container.select_one('h1, h2, h3, h4, .gc__title, [data-testid="post-teaser-title"]')
            if not title_elem:
                continue
                
            title = title_elem.get_text(strip=True)
            if not title or len(title) < 10:
                continue
            
            # Filter for Zimbabwe/Africa relevant content
            title_lower = title.lower()
            if not any(keyword in title_lower for keyword in [
                'zimbabwe', 'africa', 'southern africa', 'harare', 'bulawayo',
                'mugabe', 'mnangagwa', 'zanu', 'mdc', 'sadc'
            ]):
                continue
            
            # Extract URL
            link_elem = container.select_one('a[href]')
            if not link_elem:
                continue
                
            article_url = link_elem.get('href')
            if article_url:
                if article_url.startswith('/'):
                    article_url = urljoin(successful_url, article_url)
                elif not article_url.startswith('http'):
                    continue
            else:
                continue
            
            # Extract summary/content
            summary_elem = container.select_one('.gc__excerpt, .gc__body-text, p')
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Extract image
            img_elem = container.select_one('img')
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
                if image_url and image_url.startswith('/'):
                    image_url = urljoin(successful_url, image_url)
            
            # Get full article content
            full_content = get_full_article_content(article_url, session)
            content = full_content if full_content else summary
            
            if content and len(content) > 50:
                article_data = {
                    'title': title,
                    'content': content,
                    'url': article_url,
                    'source': 'Al Jazeera',
                    'source_url': article_url
                }
                
                if image_url:
                    article_data['image_url'] = image_url
                
                articles.append(article_data)
                processed_count += 1
                logger.info(f"Processing Al Jazeera article: {title[:50]}...")
                
                if processed_count >= max_articles:
                    break
                    
                # Delay between articles
                time.sleep(random.uniform(1, 2))
                
        except Exception as e:
            logger.error(f"Error processing Al Jazeera article: {e}")
            continue
    
    logger.info(f"Successfully scraped {len(articles)} articles from Al Jazeera")
    return articles

def get_full_article_content(url, session):
    """Get full article content from Al Jazeera article page"""
    try:
        time.sleep(random.uniform(1, 2))
        response = session.get(url, timeout=15)
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try different content selectors
        content_selectors = [
            '.wysiwyg',
            '.article-body',
            '.main-article-body',
            '[data-testid="article-body"]',
            '.gc__content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for unwanted in content_elem.select('script, style, .ad, .advertisement'):
                    unwanted.decompose()
                
                content = content_elem.get_text(strip=True)
                if content and len(content) > 100:
                    return content[:2000]  # Limit content length
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting full content from {url}: {e}")
        return None


def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    return scrape_aljazeera(max_articles=max_articles)


if __name__ == "__main__":
    # Test the scraper
    articles = scrape_aljazeera(3)
    print(f"Found {len(articles)} articles")
    for article in articles:
        print(f"- {article['title']}")
        print(f"  URL: {article['url']}")
        if 'image_url' in article:
            print(f"  Image: {article['image_url']}")
        print()