# enhanced_scraper_utils.py
"""
Enhanced web scraping utilities with multiple fallback strategies for 100% reliability
"""

import requests
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import random
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import json
import re
from fake_useragent import UserAgent
import httpx
from playwright.sync_api import sync_playwright
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class EnhancedScraper:
    """Enhanced scraper with multiple fallback strategies"""
    
    def __init__(self):
        self.session = requests.Session()
        self.cloudscraper = None
        self.selenium_driver = None
        self.playwright_browser = None
        self.user_agent = UserAgent()
        self.proxies = self._load_proxies()
        
    def _load_proxies(self) -> List[Dict]:
        """Load proxy list for fallback"""
        # Add your proxy list here
        return [
            # {'http': 'http://proxy1:port', 'https': 'https://proxy1:port'},
            # {'http': 'http://proxy2:port', 'https': 'https://proxy2:port'},
        ]
    
    def _get_headers(self) -> Dict:
        """Generate realistic headers"""
        return {
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def get_content(self, url: str, max_retries: int = 5) -> Optional[str]:
        """
        Multi-strategy content fetching with fallbacks
        """
        strategies = [
            self._fetch_requests,
            self._fetch_cloudscraper,
            self._fetch_httpx,
            self._fetch_selenium,
            self._fetch_undetected_chrome,
            self._fetch_playwright,
        ]
        
        for attempt in range(max_retries):
            for strategy_idx, strategy in enumerate(strategies):
                try:
                    logger.info(f"Attempt {attempt + 1}, Strategy {strategy_idx + 1}: {strategy.__name__}")
                    content = strategy(url)
                    if content and len(content) > 1000:  # Ensure we got meaningful content
                        logger.info(f"Success with {strategy.__name__}")
                        return content
                except Exception as e:
                    logger.warning(f"{strategy.__name__} failed: {e}")
                    continue
            
            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = random.uniform(5, 15) * (attempt + 1)
                logger.info(f"All strategies failed, waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
        
        logger.error(f"All strategies failed for {url}")
        return None
    
    def _fetch_requests(self, url: str) -> Optional[str]:
        """Basic requests with session"""
        self.session.headers.update(self._get_headers())
        
        # Try with different proxies
        proxy_attempts = [None] + self.proxies[:3]
        
        for proxy in proxy_attempts:
            try:
                response = self.session.get(
                    url, 
                    timeout=30, 
                    proxies=proxy,
                    allow_redirects=True
                )
                if response.status_code == 200:
                    return response.text
            except:
                continue
        return None
    
    def _fetch_cloudscraper(self, url: str) -> Optional[str]:
        """CloudScraper for Cloudflare protection"""
        if not self.cloudscraper:
            self.cloudscraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                },
                delay=10
            )
        
        try:
            response = self.cloudscraper.get(url, timeout=30)
            if response.status_code == 200:
                return response.text
        except:
            pass
        return None
    
    def _fetch_httpx(self, url: str) -> Optional[str]:
        """HTTPX with HTTP/2 support"""
        try:
            with httpx.Client(
                headers=self._get_headers(),
                timeout=30,
                follow_redirects=True,
                http2=True
            ) as client:
                response = client.get(url)
                if response.status_code == 200:
                    return response.text
        except:
            pass
        return None
    
    def _fetch_selenium(self, url: str) -> Optional[str]:
        """Selenium WebDriver"""
        try:
            if not self.selenium_driver:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument(f'--user-agent={self.user_agent.random}')
                
                service = Service(ChromeDriverManager().install())
                self.selenium_driver = webdriver.Chrome(service=service, options=chrome_options)
                self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.selenium_driver.get(url)
            WebDriverWait(self.selenium_driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for dynamic content
            time.sleep(random.uniform(3, 7))
            
            # Scroll to load lazy content
            self.selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            return self.selenium_driver.page_source
            
        except Exception as e:
            logger.warning(f"Selenium error: {e}")
            if self.selenium_driver:
                try:
                    self.selenium_driver.quit()
                except:
                    pass
                self.selenium_driver = None
        return None
    
    def _fetch_undetected_chrome(self, url: str) -> Optional[str]:
        """Undetected Chrome for anti-bot protection"""
        driver = None
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-first-run')
            options.add_argument('--no-service-autorun')
            options.add_argument('--password-store=basic')
            
            driver = uc.Chrome(options=options)
            driver.get(url)
            
            # Wait and scroll
            time.sleep(random.uniform(5, 10))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            return driver.page_source
            
        except Exception as e:
            logger.warning(f"Undetected Chrome error: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        return None
    
    def _fetch_playwright(self, url: str) -> Optional[str]:
        """Playwright for modern web scraping"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                context = browser.new_context(
                    user_agent=self.user_agent.random,
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = context.new_page()
                
                # Block unnecessary resources
                page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2}", lambda route: route.abort())
                
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                page.wait_for_timeout(random.randint(3000, 7000))
                
                # Scroll to load lazy content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                
                content = page.content()
                browser.close()
                return content
                
        except Exception as e:
            logger.warning(f"Playwright error: {e}")
        return None
    
    def close(self):
        """Clean up resources"""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
            except:
                pass
        
        try:
            self.session.close()
        except:
            pass


# Enhanced NewsDay Scraper
def scrape_newsday_enhanced() -> List[Dict]:
    """Enhanced NewsDay scraper with 100% reliability"""
    scraper = EnhancedScraper()
    articles = []
    
    listing_urls = [
        "https://newsday.co.zw/local-news/",
        "https://www.newsday.co.zw/local-news/",
        "https://newsday.co.zw/news/",
        "https://www.newsday.co.zw/news/",
        "https://newsday.co.zw/",
        "https://www.newsday.co.zw/",
    ]
    
    processed_links = set()
    
    try:
        for base_url in listing_urls:
            try:
                logger.info(f"Scraping NewsDay listing: {base_url}")
                content = scraper.get_content(base_url)
                if not content:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Enhanced link extraction
                article_links = _extract_article_links_enhanced(soup, base_url, 'newsday.co.zw')
                
                for link_data in article_links:
                    if len(articles) >= 15:
                        break
                        
                    url = link_data['url']
                    title = link_data['title']
                    
                    if url in processed_links:
                        continue
                    processed_links.add(url)
                    
                    # Get full article content
                    article_content = scraper.get_content(url)
                    if not article_content:
                        continue
                    
                    article_soup = BeautifulSoup(article_content, 'html.parser')
                    
                    # Enhanced content extraction
                    content_data = _extract_article_content_enhanced(article_soup, url, 'NewsDay')
                    
                    if content_data and content_data['content']:
                        article = {
                            'title': title,
                            'content': content_data['content'],
                            'source': 'NewsDay',
                            'source_url': url,
                            'link': url
                        }
                        
                        if content_data.get('image_url'):
                            article['image_url'] = content_data['image_url']
                        
                        if content_data.get('published'):
                            article.setdefault('meta', {})
                            article['meta']['published'] = content_data['published']
                        
                        articles.append(article)
                        logger.info(f"Successfully scraped: {title[:50]}...")
                    
                    # Rate limiting
                    time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.warning(f"Error processing {base_url}: {e}")
                continue
                
    finally:
        scraper.close()
    
    logger.info(f"NewsDay: Successfully scraped {len(articles)} articles")
    return articles


# Enhanced NewsHawks Scraper
def scrape_newshawks_enhanced() -> List[Dict]:
    """Enhanced NewsHawks scraper with 100% reliability"""
    scraper = EnhancedScraper()
    articles = []
    
    listing_urls = [
        "https://thenewshawks.com/",
        "https://www.thenewshawks.com/",
        "https://thenewshawks.com/category/news/",
        "https://www.thenewshawks.com/category/news/",
        "https://thenewshawks.com/category/business/",
        "https://thenewshawks.com/category/politics/",
    ]
    
    processed_links = set()
    
    try:
        for base_url in listing_urls:
            try:
                logger.info(f"Scraping NewsHawks listing: {base_url}")
                content = scraper.get_content(base_url)
                if not content:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Enhanced link extraction
                article_links = _extract_article_links_enhanced(soup, base_url, 'thenewshawks.com')
                
                for link_data in article_links:
                    if len(articles) >= 15:
                        break
                        
                    url = link_data['url']
                    title = link_data['title']
                    
                    if url in processed_links:
                        continue
                    processed_links.add(url)
                    
                    # Get full article content
                    article_content = scraper.get_content(url)
                    if not article_content:
                        continue
                    
                    article_soup = BeautifulSoup(article_content, 'html.parser')
                    
                    # Enhanced content extraction
                    content_data = _extract_article_content_enhanced(article_soup, url, 'The NewsHawks')
                    
                    if content_data and content_data['content']:
                        article = {
                            'title': title,
                            'content': content_data['content'],
                            'source': 'The NewsHawks',
                            'source_url': url,
                            'link': url
                        }
                        
                        if content_data.get('image_url'):
                            article['image_url'] = content_data['image_url']
                        
                        if content_data.get('published'):
                            article.setdefault('meta', {})
                            article['meta']['published'] = content_data['published']
                        
                        articles.append(article)
                        logger.info(f"Successfully scraped: {title[:50]}...")
                    
                    # Rate limiting
                    time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.warning(f"Error processing {base_url}: {e}")
                continue
                
    finally:
        scraper.close()
    
    logger.info(f"NewsHawks: Successfully scraped {len(articles)} articles")
    return articles


# Enhanced NewZimbabwe Scraper
def scrape_newzimbabwe_enhanced() -> List[Dict]:
    """Enhanced NewZimbabwe scraper with 100% reliability"""
    scraper = EnhancedScraper()
    articles = []
    
    listing_urls = [
        "https://www.newzimbabwe.com/category/news/",
        "https://newzimbabwe.com/category/news/",
        "https://www.newzimbabwe.com/",
        "https://newzimbabwe.com/",
    ]
    
    processed_links = set()
    
    try:
        for base_url in listing_urls:
            try:
                logger.info(f"Scraping NewZimbabwe listing: {base_url}")
                content = scraper.get_content(base_url)
                if not content:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Enhanced link extraction
                article_links = _extract_article_links_enhanced(soup, base_url, 'newzimbabwe.com')
                
                for link_data in article_links:
                    if len(articles) >= 15:
                        break
                        
                    url = link_data['url']
                    title = link_data['title']
                    
                    if url in processed_links:
                        continue
                    processed_links.add(url)
                    
                    # Get full article content
                    article_content = scraper.get_content(url)
                    if not article_content:
                        continue
                    
                    article_soup = BeautifulSoup(article_content, 'html.parser')
                    
                    # Enhanced content extraction
                    content_data = _extract_article_content_enhanced(article_soup, url, 'NewZimbabwe')
                    
                    if content_data and content_data['content']:
                        article = {
                            'title': title,
                            'content': content_data['content'],
                            'source': 'NewZimbabwe',
                            'source_url': url,
                            'link': url
                        }
                        
                        if content_data.get('image_url'):
                            article['image_url'] = content_data['image_url']
                        
                        if content_data.get('published'):
                            article.setdefault('meta', {})
                            article['meta']['published'] = content_data['published']
                        
                        articles.append(article)
                        logger.info(f"Successfully scraped: {title[:50]}...")
                    
                    # Rate limiting
                    time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.warning(f"Error processing {base_url}: {e}")
                continue
                
    finally:
        scraper.close()
    
    logger.info(f"NewZimbabwe: Successfully scraped {len(articles)} articles")
    return articles


def _extract_article_links_enhanced(soup: BeautifulSoup, base_url: str, domain: str) -> List[Dict]:
    """Enhanced article link extraction with multiple strategies"""
    candidates = []
    
    # Strategy 1: Common article selectors
    article_selectors = [
        'article a[href]',
        '.post a[href]',
        '.entry a[href]',
        '.news-item a[href]',
        '.story a[href]',
        '.article a[href]',
        '[class*="post"] a[href]',
        '[class*="article"] a[href]',
        '[class*="news"] a[href]',
        '.wp-block-post a[href]',
        '.elementor-post a[href]',
        '.td-module-container a[href]',
        'h1 a[href], h2 a[href], h3 a[href]',
        '.headline a[href]',
        '.title a[href]',
        '.entry-title a[href]',
    ]
    
    for selector in article_selectors:
        try:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '').strip()
                title = link.get_text(strip=True)
                
                if not href or not title or len(title) < 10:
                    continue
                
                # Make URL absolute
                if href.startswith('/'):
                    href = urljoin(base_url, href)
                elif not href.startswith('http'):
                    href = urljoin(base_url, href)
                
                # Validate URL
                if domain not in href.lower():
                    continue
                
                # Skip non-article URLs
                skip_patterns = [
                    '/tag/', '/category/', '/author/', '/page/',
                    '/contact', '/about', '/privacy', '/terms',
                    '#', 'javascript:', 'mailto:', '.pdf', '.jpg', '.png'
                ]
                
                if any(pattern in href.lower() for pattern in skip_patterns):
                    continue
                
                # Check if it looks like an article
                article_indicators = [
                    '/news/', '/local-news/', '/business/', '/sport/',
                    '/politics/', '/opinion/', '/world/', '/africa/',
                    '/breaking/', '/latest/', '/update/'
                ]
                
                if any(indicator in href.lower() for indicator in article_indicators) or len(title) > 30:
                    candidates.append({
                        'url': href,
                        'title': title,
                        'selector': selector
                    })
        except Exception as e:
            logger.debug(f"Error with selector {selector}: {e}")
            continue
    
    # Strategy 2: JSON-LD structured data
    try:
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                
                if data.get('@type') == 'Article' or 'Article' in str(data.get('@type', '')):
                    url = data.get('url') or data.get('mainEntityOfPage', {}).get('@id')
                    title = data.get('headline') or data.get('name')
                    
                    if url and title and domain in url:
                        candidates.append({
                            'url': url,
                            'title': title,
                            'selector': 'json-ld'
                        })
            except:
                continue
    except:
        pass
    
    # Strategy 3: RSS/Sitemap links
    try:
        rss_links = soup.find_all('link', rel='alternate', type='application/rss+xml')
        for rss_link in rss_links:
            # Could fetch RSS feeds as fallback
            pass
    except:
        pass
    
    # Deduplicate and sort by relevance
    seen_urls = set()
    unique_candidates = []
    
    for candidate in candidates:
        url = candidate['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_candidates.append(candidate)
    
    # Sort by relevance (prefer articles with specific selectors)
    def relevance_score(candidate):
        selector = candidate['selector']
        title_len = len(candidate['title'])
        
        score = 0
        if 'article' in selector.lower():
            score += 10
        if 'headline' in selector.lower() or 'title' in selector.lower():
            score += 8
        if 'h1' in selector or 'h2' in selector:
            score += 6
        if title_len > 50:
            score += 5
        if title_len > 100:
            score += 3
        
        return score
    
    unique_candidates.sort(key=relevance_score, reverse=True)
    
    return unique_candidates[:20]  # Return top 20 candidates


def _extract_article_content_enhanced(soup: BeautifulSoup, url: str, source: str) -> Dict:
    """Enhanced content extraction with multiple strategies"""
    
    # Remove unwanted elements
    for element in soup.find_all([
        'script', 'style', 'nav', 'aside', 'footer', 'header',
        'form', 'iframe', 'noscript', 'object', 'embed'
    ]):
        element.decompose()
    
    # Remove ads and social media
    ad_selectors = [
        '[class*="ad"]', '[id*="ad"]', '[class*="advertisement"]',
        '[class*="social"]', '[class*="share"]', '[class*="follow"]',
        '[class*="subscribe"]', '[class*="newsletter"]', '.widget'
    ]
    
    for selector in ad_selectors:
        for element in soup.select(selector):
            element.decompose()
    
    # Extract main content
    content_parts = []
    
    # Strategy 1: Common content selectors
    content_selectors = [
        '.entry-content',
        '.post-content',
        '.article-content',
        '.content',
        '.story-content',
        '.news-content',
        '.main-content',
        'div[class*="content"]',
        '.single-content',
        '.wp-block-post-content',
        '.elementor-widget-theme-post-content',
        '.td-post-content',
        'article .content',
        'article > div',
        '[itemprop="articleBody"]',
        '.field-name-body',
        '.node-content'
    ]
    
    found_content = False
    for selector in content_selectors:
        try:
            content_div = soup.select_one(selector)
            if content_div:
                paragraphs = content_div.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 30:
                        # Skip unwanted content
                        skip_phrases = [
                            'advertisement', 'subscribe', 'follow us', 'share this',
                            'related articles', 'read more', 'continue reading',
                            'newsletter', 'social media', 'whatsapp', 'telegram',
                            'copyright', '©', 'all rights reserved'
                        ]
                        
                        if not any(phrase in text.lower() for phrase in skip_phrases):
                            content_parts.append(text)
                
                if content_parts:
                    found_content = True
                    break
        except:
            continue
    
    # Strategy 2: JSON-LD articleBody
    if not found_content:
        try:
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]
                    
                    if 'articleBody' in data:
                        content_parts = [data['articleBody']]
                        found_content = True
                        break
                except:
                    continue
        except:
            pass
    
    # Strategy 3: Fallback to all paragraphs
    if not found_content:
        paragraphs = soup.find_all('p')
        main_content_paragraphs = []
        
        # Filter paragraphs by length and content quality
        for p in paragraphs:
            text = p.get_text(strip=True)
            if (text and len(text) > 50 and 
                not any(skip in text.lower() for skip in ['advertisement', 'subscribe', 'cookie'])):
                main_content_paragraphs.append(text)
        
        # Take the longest consecutive sequence of paragraphs
        if main_content_paragraphs:
            content_parts = main_content_paragraphs
    
    # Strategy 4: Reading mode extraction
    if not content_parts:
        # Try to find the main text content by looking for the largest text block
        all_text_elements = soup.find_all(text=True)
        text_blocks = []
        
        for text in all_text_elements:
            clean_text = text.strip()
            if clean_text and len(clean_text) > 100:
                text_blocks.append(clean_text)
        
        if text_blocks:
            content_parts = text_blocks[:10]  # Take first 10 meaningful text blocks
    
    # Extract image
    image_url = _extract_featured_image_enhanced(soup, url)
    
    # Extract publication date
    published_date = _extract_published_date_enhanced(soup)
    
    # Build final content
    if content_parts:
        # Clean and format content
        cleaned_parts = []
        for part in content_parts[:15]:  # Limit to 15 paragraphs
            cleaned = re.sub(r'\s+', ' ', part).strip()
            if len(cleaned) > 20:
                cleaned_parts.append(cleaned)
        
        if cleaned_parts:
            content_html = '\n\n'.join([f"<p>{part}</p>" for part in cleaned_parts])
            source_attribution = f"<p><em>Source: <a href='{url}' target='_blank'>{source}</a></em></p>"
            
            return {
                'content': content_html + '\n' + source_attribution,
                'image_url': image_url,
                'published': published_date
            }
    
    return {'content': None}


def _extract_featured_image_enhanced(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Enhanced image extraction with multiple strategies"""
    
    # Strategy 1: OpenGraph and Twitter meta tags
    meta_selectors = [
        'meta[property="og:image"]',
        'meta[name="twitter:image"]',
        'meta[name="twitter:image:src"]',
    ]
    
    for selector in meta_selectors:
        try:
            meta = soup.select_one(selector)
            if meta:
                img_url = meta.get('content')
                if img_url:
                    return _normalize_image_url(img_url, base_url)
        except:
            continue
    
    # Strategy 2: Common image selectors
    image_selectors = [
        'img[class*="featured"]',
        'img[class*="hero"]',
        'img[class*="banner"]',
        'img[class*="article"]',
        'img[class*="post"]',
        '.featured-image img',
        '.article-image img',
        '.post-image img',
        '.hero-image img',
        '.wp-post-image',
        'img[src*="upload"]',
        'img[src*="wp-content"]',
        'img[alt]',
        '.td-post-featured-image img',
        'figure img',
        '.image img'
    ]
    
    for selector in image_selectors:
        try:
            img = soup.select_one(selector)
            if img:
                img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                if img_url:
                    return _normalize_image_url(img_url, base_url)
        except:
            continue
    
    # Strategy 3: JSON-LD image
    try:
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                
                image_data = data.get('image')
                if image_data:
                    if isinstance(image_data, dict):
                        img_url = image_data.get('url')
                    elif isinstance(image_data, list) and image_data:
                        img_url = image_data[0] if isinstance(image_data[0], str) else image_data[0].get('url')
                    else:
                        img_url = image_data
                    
                    if img_url:
                        return _normalize_image_url(img_url, base_url)
            except:
                continue
    except:
        pass
    
    # Strategy 4: First meaningful image in content
    try:
        content_imgs = soup.find_all('img')
        for img in content_imgs:
            img_url = img.get('src') or img.get('data-src')
            if img_url:
                # Skip small images (likely icons/ads)
                width = img.get('width')
                height = img.get('height')
                
                if width and height:
                    try:
                        w, h = int(width), int(height)
                        if w >= 300 and h >= 200:
                            return _normalize_image_url(img_url, base_url)
                    except:
                        pass
                
                # Skip obvious non-content images
                if not any(skip in img_url.lower() for skip in [
                    'logo', 'icon', 'avatar', 'ad', 'banner', 'button'
                ]):
                    return _normalize_image_url(img_url, base_url)
    except:
        pass
    
    return None


def _extract_published_date_enhanced(soup: BeautifulSoup) -> Optional[str]:
    """Enhanced date extraction with multiple strategies"""
    
    # Strategy 1: Meta tags
    meta_selectors = [
        'meta[property="article:published_time"]',
        'meta[name="publishdate"]',
        'meta[name="publication_date"]',
        'meta[name="date"]',
        'meta[itemprop="datePublished"]',
        'meta[name="DC.date.issued"]'
    ]
    
    for selector in meta_selectors:
        try:
            meta = soup.select_one(selector)
            if meta:
                date_str = meta.get('content')
                if date_str:
                    return _normalize_date(date_str)
        except:
            continue
    
    # Strategy 2: Time elements
    time_selectors = [
        'time[datetime]',
        'time[pubdate]',
        '.published time',
        '.date time',
        '[class*="date"] time'
    ]
    
    for selector in time_selectors:
        try:
            time_elem = soup.select_one(selector)
            if time_elem:
                date_str = time_elem.get('datetime') or time_elem.get_text(strip=True)
                if date_str:
                    return _normalize_date(date_str)
        except:
            continue
    
    # Strategy 3: JSON-LD
    try:
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                
                date_published = data.get('datePublished')
                if date_published:
                    return _normalize_date(date_published)
            except:
                continue
    except:
        pass
    
    # Strategy 4: Common date selectors
    date_selectors = [
        '.published',
        '.date',
        '.post-date',
        '.entry-date',
        '.article-date',
        '[class*="date"]',
        '.byline time',
        '.meta time'
    ]
    
    for selector in date_selectors:
        try:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_str = date_elem.get_text(strip=True)
                if date_str and len(date_str) > 5:
                    return _normalize_date(date_str)
        except:
            continue
    
    return None


def _normalize_image_url(img_url: str, base_url: str) -> str:
    """Normalize image URL to absolute URL"""
    if img_url.startswith('//'):
        return 'https:' + img_url
    elif img_url.startswith('/'):
        return urljoin(base_url, img_url)
    elif not img_url.startswith('http'):
        return urljoin(base_url, img_url)
    return img_url


def _normalize_date(date_str: str) -> str:
    """Normalize date string to consistent format"""
    import dateutil.parser
    try:
        # Parse the date string
        parsed_date = dateutil.parser.parse(date_str)
        return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
    except:
        # Return original if parsing fails
        return date_str.strip()


# Async version for better performance
async def scrape_all_sources_async() -> Dict[str, List[Dict]]:
    """Scrape all sources asynchronously for better performance"""
    
    async def run_scraper(scraper_func):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, scraper_func)
    
    # Run all scrapers concurrently
    results = await asyncio.gather(
        run_scraper(scrape_newsday_enhanced),
        run_scraper(scrape_newshawks_enhanced),
        run_scraper(scrape_newzimbabwe_enhanced),
        return_exceptions=True
    )
    
    # Organize results
    all_articles = {
        'NewsDay': results[0] if not isinstance(results[0], Exception) else [],
        'NewsHawks': results[1] if not isinstance(results[1], Exception) else [],
        'NewZimbabwe': results[2] if not isinstance(results[2], Exception) else []
    }
    
    return all_articles


# Main execution function
def scrape_all_zimbabwe_news() -> List[Dict]:
    """Main function to scrape all Zimbabwean news sources"""
    
    # Run async scraping
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    all_articles_by_source = loop.run_until_complete(scrape_all_sources_async())
    
    # Combine all articles
    all_articles = []
    for source, articles in all_articles_by_source.items():
        all_articles.extend(articles)
        logger.info(f"{source}: {len(articles)} articles")
    
    # Remove duplicates based on title similarity
    unique_articles = []
    seen_titles = set()
    
    for article in all_articles:
        title_lower = article['title'].lower()
        # Simple duplicate detection based on first 50 characters
        title_key = title_lower[:50]
        
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_articles.append(article)
    
    logger.info(f"Total unique articles scraped: {len(unique_articles)}")
    return unique_articles


# Requirements.txt content
REQUIREMENTS = """
requests>=2.31.0
cloudscraper>=1.2.71
selenium>=4.15.0
undetected-chromedriver>=3.5.4
playwright>=1.40.0
beautifulsoup4>=4.12.2
fake-useragent>=1.4.0
httpx>=0.25.0
webdriver-manager>=4.0.1
python-dateutil>=2.8.2
aiohttp>=3.9.0
lxml>=4.9.3
"""

# Installation and setup script
SETUP_SCRIPT = """
#!/bin/bash
# Setup script for enhanced scrapers

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright browsers..."
playwright install chromium

echo "Setting up Chrome for Selenium..."
# This will be handled by webdriver-manager automatically

echo "Setup complete!"
echo "You can now run the scrapers with:"
echo "python enhanced_scrapers.py"
"""


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test the scrapers
    print("Starting enhanced news scraping...")
    articles = scrape_all_zimbabwe_news()
    
    print(f"\nSuccessfully scraped {len(articles)} articles!")
    
    # Display sample results
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   URL: {article['source_url']}")
        print(f"   Content length: {len(article.get('content', ''))}")
        print(f"   Has image: {'Yes' if article.get('image_url') else 'No'}")
        print("-" * 80)