from .base_scraper import BaseScraper
import requests
import cloudscraper
from bs4 import BeautifulSoup
import time
import logging
import re
from urllib.parse import urljoin
from src.scrapers.base_scraper import SmartCrawler
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)

def scrape_bbc():
    """
    Scrape BBC News articles with improved content extraction
    Returns list of articles with title and content
    """
    articles = []
    
    # BBC News sections to scrape
    sections = [
        {
            'url': "https://www.bbc.com/news/world/africa",
            'name': 'Africa'
        },
        {
            'url': "https://www.bbc.com/news/world",
            'name': 'World'
        },
        {
            'url': "https://www.bbc.com/news/business",
            'name': 'Business'
        }
    ]
    
    # Headers to avoid being blocked
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache'
    }

    crawler = SmartCrawler(obey_robots="best_effort", default_delay=1.0)

    for section in sections:
        try:
            logger.info(f"Scraping BBC {section['name']}: {section['url']}")
            soup = crawler.get_soup(section['url'])
            if soup is None:
                logger.warning(f"Failed to fetch section: {section['url']}")
                continue
            
            # Extract articles from this section
            section_articles = extract_articles_from_page(soup, crawler, section['name'], headers)
            articles.extend(section_articles)
            
            logger.info(f"Found {len(section_articles)} articles from BBC {section['name']}")
            
            # Rate limiting between sections handled by crawler; add small pause
            time.sleep(1)
            
            # Limit total articles to prevent overwhelming
            if len(articles) >= 15:
                break
                
        except Exception as e:
            logger.error(f"Error scraping BBC section {section['url']}: {e}")
            continue
    
    logger.info(f"Total BBC articles scraped: {len(articles)}")
    return articles[:10]  # Limit to 10 articles

def extract_articles_from_page(soup, crawler, section_name, headers):
    """Extract articles from a BBC page"""
    articles = []
    
    # Different selectors for different page layouts
    article_selectors = [
        'div[data-testid="edinburgh-card"]',
        'div[data-testid="liverpool-card"]', 
        'article',
        'div.gs-c-promo',
        'div.media',
        'div[class*="promo"]'
    ]
    
    article_containers = []
    
    # Try each selector
    for selector in article_selectors:
        containers = soup.select(selector)
        if containers:
            article_containers = containers
            logger.info(f"Using selector '{selector}' - found {len(containers)} containers")
            break
    
    if not article_containers:
        logger.warning("No article containers found, trying fallback approach")
        # Fallback: look for links in common BBC article patterns
        all_links = soup.find_all('a', href=True)
        article_containers = [link for link in all_links if is_likely_article_link(link.get('href', ''))][:10]
    
    for container in article_containers[:8]:  # Limit per section
        try:
            article_data = extract_article_data(container, crawler, section_name, headers)
            if article_data:
                articles.append(article_data)
                
            # Small pause; crawler also enforces per-host pacing
            time.sleep(0.5)
            
        except Exception as e:
            logger.warning(f"Error processing article container: {e}")
            continue
    
    return articles

def extract_article_data(container, crawler, section_name, headers):
    """Extract article data from a container element"""
    try:
        # Extract link
        if container.name == 'a':
            link_element = container
        else:
            link_element = container.find('a', href=True)
        
        if not link_element:
            return None
        
        link = link_element.get('href', '')
        if not link:
            return None
        
        # Make URL absolute
        if link.startswith('/'):
            link = 'https://www.bbc.com' + link
        elif not link.startswith('http'):
            return None
        
        # Skip non-article links
        if not is_likely_article_link(link):
            return None
        
        # Extract title
        title = extract_title(container, link_element)
        if not title or len(title) < 10:
            return None
        
        # Try to extract image URL from container
        image_url = None
        try:
            img = container.find('img') if container else None
            if img and (img.get('src') or img.get('data-src')):
                image_url = img.get('src') or img.get('data-src')
                if image_url and image_url.startswith('/'):
                    image_url = urljoin('https://www.bbc.com', image_url)
        except Exception:
            image_url = None
        
        logger.info(f"Processing: {title[:60]}...")
        
        # Get article content using crawler
        content = get_full_article_content(link, crawler, headers)
        if not content or len(content) < 100:
            logger.warning(f"Insufficient content for: {title[:50]}...")
            return None
        
        data = {
            'title': title,
            'content': content,
            'source_url': link,
            'section': section_name
        }
        if image_url:
            data['image_url'] = image_url
        return data
        
    except Exception as e:
        logger.error(f"Error extracting article data: {e}")
        return None

def extract_title(container, link_element):
    """Extract title from various possible locations"""
    title_selectors = [
        'h3',
        'h2', 
        'h1',
        '[data-testid="card-headline"]',
        '[data-testid="card-text-wrapper"] h3',
        '.gs-c-promo-heading__title',
        '.media__title',
        '.gs-c-promo-summary',
        'p'
    ]
    
    # Try structured selectors first
    for selector in title_selectors:
        element = container.select_one(selector)
        if element:
            title = element.get_text(strip=True)
            if title and len(title) > 10:
                return title
    
    # Fallback to link text
    title = link_element.get_text(strip=True)
    if title and len(title) > 10:
        return title
    
    return None

def is_likely_article_link(url):
    """Check if URL is likely an article"""
    if not url:
        return False
    
    # Must contain /news/
    if '/news/' not in url:
        return False
    
    # Skip certain patterns
    skip_patterns = [
        '/live/',
        '/av/',
        '/video/',
        '/programmes/',
        '/sport/',
        '/weather/'
    ]
    
    for pattern in skip_patterns:
        if pattern in url:
            return False
    
    return True

def get_full_article_content(url, crawler, headers):
    """Get full article content from article page using SmartCrawler."""
    try:
        soup = crawler.get_soup(url)
        if soup is None:
            return None
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
            element.decompose()
        
        # BBC article content selectors
        content_selectors = [
            '[data-component="text-block"]',
            '[data-component="unordered-list-block"]',
            '.story-body__inner',
            '[data-testid="article-text"]',
            '.post-content',
            'div[class*="RichTextContainer"]'
        ]
        
        content_parts = []
        
        # Try structured content first
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 20:
                        content_parts.append(f"<p>{clean_text(text)}</p>")
                break
        
        # Fallback to paragraphs
        if not content_parts:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 30:
                    # Skip certain patterns
                    if not any(skip in text.lower() for skip in ['follow us', 'subscribe', 'newsletter', 'cookie']):
                        content_parts.append(f"<p>{clean_text(text)}</p>")
        
        if content_parts:
            # Limit content and add source
            content_html = '\n'.join(content_parts[:10])  # First 10 paragraphs
            
            # Add source attribution
            source_attribution = f"<p><em>Source: <a href='{url}' target='_blank'>BBC News</a></em></p>"
            
            return content_html + '\n' + source_attribution
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting article content from {url}: {e}")
        return None

def clean_text(text):
    """Clean text content"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common BBC patterns
    text = re.sub(r'Getty Images.*?$', '', text)
    text = re.sub(r'BBC.*?correspondent', '', text)
    
    return text

def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    articles = scrape_bbc()
    # Convert to expected format
    result = []
    for article in articles[:max_articles]:
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
    articles = scrape_bbc(max_articles=max_articles)
    
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
    articles = scrape_bbc()
    print(f"Scraped {len(articles)} articles")
    for i, article in enumerate(articles[:3], 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"Content length: {len(article['content'])}")
        print(f"URL: {article['source_url']}")
        print("-" * 80)
