import requests
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from utils.enhanced_session import EnhancedSessionManager

logger = logging.getLogger(__name__)

class Chat263Scraper(BaseScraper):
    def __init__(self, max_articles=10):
        # Use www subdomain first as 263chat.com doesn't resolve properly
        base_urls = [
            "https://www.263chat.com/",
            "https://www.263chat.com/category/news/",
            "https://263chat.com/",
            "https://263chat.com/category/news/"
        ]
        super().__init__("263Chat", base_urls, max_articles)
    
    def _fetch_full_article(self, url: str, title: str):
        """Override to add image extraction for 263Chat"""
        article = super()._fetch_full_article(url, title)
        if article:
            # Add featured image for RSS-discovered articles
            article = self._add_featured_image(article, url)
        return article
    
    def scrape_webpage(self):
        """Custom 263Chat webpage scraping logic"""
        articles = []
        
        for base_url in self.base_urls:
            try:
                response = self.session.get(base_url, timeout=15)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 263Chat uses section.eltd-post-item containers with h6 titles
                # Updated to match current site structure
                containers = soup.select('section.eltd-post-item')
                
                if containers:
                    for container in containers[:self.max_articles * 2]:
                        if len(articles) >= self.max_articles:
                            break
                        
                        try:
                            # Extract title from h6
                            title_elem = container.select_one('h6 a')
                            if not title_elem:
                                continue
                            
                            url = urljoin(base_url, title_elem.get('href', ''))
                            title = title_elem.get_text(strip=True)
                            
                            if not self._is_valid_263chat_url(url) or len(title) < 10:
                                continue
                            
                            # Extract image from container (lazyload placeholders)
                            img_url = self._extract_image_from_container(container, url)
                            
                            # Fetch full article content
                            article = self._fetch_full_article(url, title)
                            if article:
                                if img_url:
                                    article['image_url'] = img_url
                                else:
                                    # Fallback: try to extract from article page
                                    article = self._add_featured_image(article, url)
                                articles.append(article)
                            
                            self.rate_limiter.wait()
                        except Exception as e:
                            logger.debug(f"Error processing article: {e}")
                            continue
                else:
                    # Fallback to older selectors
                    article_selectors = [
                        "h6 a",
                        ".jeg_post_title a",
                        ".entry-title a",
                        "article h2 a",
                        "h3 a",
                        ".post h2 a"
                    ]
                    
                    for selector in article_selectors:
                        links = soup.select(selector)
                        if len(links) >= 3:
                            for link in links[:self.max_articles * 2]:
                                if len(articles) >= self.max_articles:
                                    break
                                
                                url = urljoin(base_url, link.get('href', ''))
                                title = link.get_text(strip=True)
                                
                                if self._is_valid_263chat_url(url) and len(title) > 10:
                                    article = self._fetch_full_article(url, title)
                                    if article:
                                        article = self._add_featured_image(article, url)
                                        articles.append(article)
                                
                                self.rate_limiter.wait()
                            break
                
                if articles:
                    break
                    
            except Exception as e:
                logger.warning(f"263Chat webpage scraping failed for {base_url}: {e}")
                continue
        
        return articles
    
    def _is_valid_263chat_url(self, url):
        if not url or '263chat.com' not in url:
            return False
        
        url_lower = url.lower()
        return not any(x in url_lower for x in ['/category/', '/tag/', '/author/', '/about', '/contact'])
    
    def _extract_image_from_container(self, container, article_url):
        """Extract image URL from article list container (with lazyload handling)"""
        try:
            # 263Chat uses lazyload with data-src
            img = container.select_one('img.lazyload')
            if img:
                # Try data-src first (actual image), then src (placeholder)
                img_url = img.get('data-src') or img.get('src')
                if img_url and not img_url.startswith('data:'):
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = urljoin(article_url, img_url)
                    return img_url
            
            # Fallback to any img in container
            img = container.select_one('img')
            if img:
                img_url = img.get('data-src') or img.get('src')
                if img_url and not img_url.startswith('data:'):
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = urljoin(article_url, img_url)
                    return img_url
        except:
            pass
        
        return None
    
    def _add_featured_image(self, article, url):
        """Extract featured image for 263Chat articles"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for featured images (in order of preference)
            image_selectors = [
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
                '.jeg_featured_image img',
                '.wp-post-image',
                'img[class*="featured"]',
                '.entry-image img',
                'article img:first-of-type',
                '.post-thumbnail img',
                'figure img:first-of-type',
                'article img'
            ]
            
            for selector in image_selectors:
                if selector.startswith('meta'):
                    # Handle meta tags
                    tag = soup.select_one(selector)
                    if tag:
                        img_url = tag.get('content')
                        if img_url:
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            elif img_url.startswith('/'):
                                img_url = urljoin(url, img_url)
                            if self._is_valid_image_url(img_url):
                                article['image_url'] = img_url
                                return article
                else:
                    # Handle img tags
                    img = soup.select_one(selector)
                    if img:
                        img_url = img.get('src') or img.get('data-src')
                        if img_url and not img_url.startswith('data:'):
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            elif img_url.startswith('/'):
                                img_url = urljoin(url, img_url)
                            
                            if self._is_valid_image_url(img_url):
                                article['image_url'] = img_url
                                return article
        except:
            pass
        
        return article
    
    def _is_valid_image_url(self, url):
        """Check if image URL is valid and not a placeholder"""
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Skip data URIs and placeholders
        if url_lower.startswith('data:'):
            return False
        
        # Skip logos and common placeholders
        bad_keywords = ['logo', 'placeholder', 'default', 'avatar', 'favicon', 'sprite']
        if any(keyword in url_lower for keyword in bad_keywords):
            return False
        
        # Accept common image extensions
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
        return url_lower.endswith(valid_extensions)

def scrape_263chat(max_articles=10):
    """Main function to maintain compatibility"""
    scraper = Chat263Scraper(max_articles)
    return scraper.scrape()



def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_263chat(max_articles=max_articles)
    
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
    articles = scrape_263chat(5)
    print(f"Found {len(articles)} 263Chat articles")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title'][:60]}...")
        print(f"   Image: {article.get('image_url', 'None')}")