from .base_scraper import BaseScraper
import requests
# scraper_fixes.py
"""
Fixes for NewsDay and NewsHawks link extraction issues
"""

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from typing import List, Dict

def fix_newsday_link_extraction(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """Enhanced NewsDay link extraction with specific selectors"""
    candidates = []
    
    # NewsDay-specific selectors (updated based on current site structure)
    newsday_selectors = [
        # Primary article containers
        '.td-module-container a[href]',
        '.td-block-span12 a[href]',
        '.td-module-thumb a[href]',
        '.entry-title a[href]',
        
        # Secondary selectors
        'article h3 a[href]',
        'article .entry-title a[href]',
        '.td-module-meta-info a[href]',
        '.td-post-category a[href]',
        
        # Fallback selectors
        'h1 a[href], h2 a[href], h3 a[href]',
        '.headline a[href]',
        '.post-title a[href]',
        
        # Broad search with filtering
        'a[href*="/local-news/"]',
        'a[href*="/news/"]',
        'a[href*="/breaking/"]',
        'a[href*="/top-stories/"]',
        'a[href*="/business/"]',
        'a[href*="/sport/"]',
        'a[href*="/opinion/"]'
    ]
    
    print(f"🔍 Analyzing NewsDay page structure...")
    
    # Debug: Show what we found
    all_links = soup.find_all('a', href=True)
    newsday_links = [a for a in all_links if 'newsday.co.zw' in a.get('href', '')]
    print(f"   Found {len(all_links)} total links, {len(newsday_links)} NewsDay links")
    
    for selector in newsday_selectors:
        try:
            links = soup.select(selector)
            print(f"   Selector '{selector}': {len(links)} matches")
            
            for link in links:
                href = link.get('href', '').strip()
                title_text = link.get_text(strip=True)
                
                # Get title from link or nearby elements
                title = title_text
                if not title or len(title) < 10:
                    # Look for title in parent elements
                    parent = link.find_parent(['article', 'div', 'section'])
                    if parent:
                        title_elem = parent.find(['h1', 'h2', 'h3', 'h4'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                
                if not href or not title or len(title) < 10:
                    continue
                
                # Make URL absolute
                if href.startswith('/'):
                    href = urljoin(base_url, href)
                elif not href.startswith('http'):
                    continue
                
                # Validate it's a NewsDay article
                if 'newsday.co.zw' not in href.lower():
                    continue
                
                # Skip non-article pages
                skip_patterns = [
                    '/tag/', '/category/', '/author/', '/page/', '/wp-admin/',
                    '/contact', '/about', '/privacy', '/terms', '/search',
                    '.jpg', '.png', '.pdf', '#', 'javascript:', 'mailto:'
                ]
                
                if any(pattern in href.lower() for pattern in skip_patterns):
                    continue
                
                # Must look like an article URL
                article_patterns = [
                    '/local-news/', '/news/', '/breaking/', '/top-stories/',
                    '/business/', '/sport/', '/opinion/', '/world/', '/africa/',
                    '/politics/', '/entertainment/', '/life/', '/health/'
                ]
                
                is_article = any(pattern in href.lower() for pattern in article_patterns)
                
                # Also check URL structure (NewsDay uses date-based URLs sometimes)
                date_pattern = re.search(r'/\d{4}/\d{2}/', href)
                if date_pattern:
                    is_article = True
                
                if is_article and len(title) >= 10:
                    candidates.append({
                        'url': href,
                        'title': title[:200],  # Limit title length
                        'selector': selector
                    })
                    print(f"   ✅ Found: {title[:50]}...")
                    
        except Exception as e:
            print(f"   ❌ Selector '{selector}' failed: {e}")
            continue
    
    # Remove duplicates
    seen = set()
    unique_candidates = []
    for candidate in candidates:
        if candidate['url'] not in seen:
            seen.add(candidate['url'])
            unique_candidates.append(candidate)
    
    print(f"🎯 NewsDay: Found {len(unique_candidates)} unique articles")
    return unique_candidates[:15]


def fix_newshawks_link_extraction(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """Enhanced NewsHawks link extraction with specific selectors"""
    candidates = []
    
    # NewsHawks-specific selectors
    newshawks_selectors = [
        # WordPress/Elementor common patterns
        '.elementor-post a[href]',
        '.wp-block-post a[href]',
        '.post-item a[href]',
        '.entry-title a[href]',
        
        # News-specific patterns
        'article a[href]',
        '.news-item a[href]',
        '.story a[href]',
        '.post a[href]',
        
        # Heading links
        'h1 a[href], h2 a[href], h3 a[href]',
        '.headline a[href]',
        '.title a[href]',
        
        # Category-based links
        'a[href*="/news/"]',
        'a[href*="/business/"]',
        'a[href*="/politics/"]',
        'a[href*="/investigation/"]',
        'a[href*="/opinion/"]',
        'a[href*="/analysis/"]',
        
        # Fallback: all links with meaningful text
        'a[href]'
    ]
    
    print(f"🔍 Analyzing NewsHawks page structure...")
    
    # Debug info
    all_links = soup.find_all('a', href=True)
    newshawks_links = [a for a in all_links if 'newshawks' in a.get('href', '').lower()]
    print(f"   Found {len(all_links)} total links, {len(newshawks_links)} NewsHawks links")
    
    for selector in newshawks_selectors:
        try:
            links = soup.select(selector)
            print(f"   Selector '{selector}': {len(links)} matches")
            
            for link in links:
                href = link.get('href', '').strip()
                title = link.get_text(strip=True)
                
                # Enhanced title extraction
                if not title or len(title) < 10:
                    # Check for title attribute
                    title = link.get('title', '').strip()
                    
                    # Look in parent containers
                    if not title:
                        parent = link.find_parent(['article', 'div', 'section', 'li'])
                        if parent:
                            title_elem = parent.find(['h1', 'h2', 'h3', 'h4', '.title', '.headline'])
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                
                if not href or not title or len(title) < 10:
                    continue
                
                # Make URL absolute
                if href.startswith('/'):
                    href = urljoin(base_url, href)
                elif not href.startswith('http'):
                    continue
                
                # Must be NewsHawks URL
                if 'thenewshawks.com' not in href.lower():
                    continue
                
                # Skip non-articles
                skip_patterns = [
                    '/tag/', '/category/', '/author/', '/page/', '/wp-admin/',
                    '/contact', '/about', '/privacy', '/terms', '/search',
                    '.jpg', '.png', '.pdf', '#', 'javascript:', 'mailto:',
                    '/feed/', '/rss/', '/sitemap'
                ]
                
                if any(pattern in href.lower() for pattern in skip_patterns):
                    continue
                
                # Check if it looks like an article
                is_article = False
                
                # Check URL patterns
                article_indicators = [
                    '/news/', '/business/', '/politics/', '/investigation/',
                    '/opinion/', '/analysis/', '/breaking/', '/exclusive/',
                    '/feature/', '/interview/', '/report/'
                ]
                
                if any(indicator in href.lower() for indicator in article_indicators):
                    is_article = True
                
                # Check title patterns
                if len(title) > 30 and not any(x in title.lower() for x in ['home', 'about', 'contact']):
                    is_article = True
                
                # Check URL structure (year pattern)
                if re.search(r'/\d{4}/', href):
                    is_article = True
                
                if is_article:
                    candidates.append({
                        'url': href,
                        'title': title[:200],
                        'selector': selector
                    })
                    print(f"   ✅ Found: {title[:50]}...")
                    
        except Exception as e:
            print(f"   ❌ Selector '{selector}' failed: {e}")
            continue
    
    # Remove duplicates
    seen = set()
    unique_candidates = []
    for candidate in candidates:
        if candidate['url'] not in seen:
            seen.add(candidate['url'])
            unique_candidates.append(candidate)
    
    print(f"🎯 NewsHawks: Found {len(unique_candidates)} unique articles")
    return unique_candidates[:15]


def fix_image_extraction(soup: BeautifulSoup, base_url: str) -> str:
    """Enhanced image extraction that actually works"""
    
    # Strategy 1: Meta tags (most reliable)
    meta_selectors = [
        'meta[property="og:image"]',
        'meta[name="twitter:image"]',
        'meta[name="twitter:image:src"]',
        'meta[itemprop="image"]'
    ]
    
    for selector in meta_selectors:
        meta = soup.select_one(selector)
        if meta:
            img_url = meta.get('content')
            if img_url:
                return _normalize_image_url(img_url, base_url)
    
    # Strategy 2: Featured images
    image_selectors = [
        'img.wp-post-image',
        '.featured-image img',
        '.post-image img',
        '.article-image img',
        'img[class*="featured"]',
        'img[class*="hero"]',
        '.elementor-widget-image img',
        'figure img',
        '.attachment-full',
        'img[src*="upload"]'
    ]
    
    for selector in image_selectors:
        img = soup.select_one(selector)
        if img:
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if img_url and not any(skip in img_url.lower() for skip in ['placeholder', 'loading', 'blank']):
                return _normalize_image_url(img_url, base_url)
    
    # Strategy 3: First large image in content
    content_imgs = soup.find_all('img')
    for img in content_imgs:
        img_url = img.get('src') or img.get('data-src')
        if not img_url:
            continue
            
        # Skip small/icon images
        width = img.get('width')
        height = img.get('height')
        
        # If dimensions are specified, check they're reasonable
        if width and height:
            try:
                w, h = int(width), int(height)
                if w < 200 or h < 150:
                    continue
            except:
                pass
        
        # Skip obvious non-content images
        if any(skip in img_url.lower() for skip in [
            'logo', 'icon', 'avatar', 'ad', 'banner', 'button',
            'loading', 'placeholder', 'blank'
        ]):
            continue
        
        return _normalize_image_url(img_url, base_url)
    
    return None


def _normalize_image_url(img_url: str, base_url: str) -> str:
    """Make image URL absolute"""
    if img_url.startswith('//'):
        return 'https:' + img_url
    elif img_url.startswith('/'):
        return urljoin(base_url, img_url)
    elif not img_url.startswith('http'):
        return urljoin(base_url, img_url)
    return img_url


# Quick test function
def test_link_extraction():
    """Test the fixed link extraction on actual websites"""
    from enhanced_scrapers import EnhancedScraper
    
    scraper = EnhancedScraper()
    
    # Test NewsDay
    print("🧪 Testing NewsDay link extraction...")
    newsday_content = scraper.get_content("https://newsday.co.zw/local-news/")
    if newsday_content:
        soup = BeautifulSoup(newsday_content, 'html.parser')
        links = fix_newsday_link_extraction(soup, "https://newsday.co.zw/local-news/")
        print(f"NewsDay: Found {len(links)} articles")
        for i, link in enumerate(links[:3], 1):
            print(f"  {i}. {link['title'][:60]}...")
    
    print("\n🧪 Testing NewsHawks link extraction...")
    newshawks_content = scraper.get_content("https://thenewshawks.com/")
    if newshawks_content:
        soup = BeautifulSoup(newshawks_content, 'html.parser')
        links = fix_newshawks_link_extraction(soup, "https://thenewshawks.com/")
        print(f"NewsHawks: Found {len(links)} articles")
        for i, link in enumerate(links[:3], 1):
            print(f"  {i}. {link['title'][:60]}...")
    
    scraper.close()


if __name__ == "__main__":
    test_link_extraction()


def scrape_fixes(max_articles=10):
    """
    Utility module for scraper fixes - not a real scraper.
    This function exists for compatibility with the testing framework.
    """
    return []

if __name__ == "__main__":
    print("Fixes utility module - not a scraper")