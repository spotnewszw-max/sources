from .base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup
import time
import logging
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import json
from src.scrapers.base_scraper import SmartCrawler
from src.utils.image_utils import extract_all_images_from_content

# Configure logging
logger = logging.getLogger(__name__)

class ZimLiveScraper(BaseScraper):
    """Scraper for ZimLive news website"""
    
    def __init__(self):
        self.base_url = "https://www.zimlive.com"
        # Shared crawler with best-effort robots, retries, rate limiting
        self.crawler = SmartCrawler(obey_robots="best_effort", default_delay=1.0)
        # Keep a session for backward compatibility in methods that still use it
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
    
    def scrape_zimlive(self, max_articles=10):
        """
        Scrape ZimLive articles
        Returns list of articles with title, content, url, and metadata
        """
        articles = []
        
        try:
            logger.info(f"Scraping ZimLive: {self.base_url}")
            # Use shared crawler for politeness, retries, backoff
            soup = self.crawler.get_soup(self.base_url)
            if soup is None:
                raise RuntimeError("Failed to fetch ZimLive homepage")
            
            # Extract articles from homepage
            articles = self._extract_articles_from_homepage(soup, max_articles)
            
            logger.info(f"Total ZimLive articles scraped: {len(articles)}")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping ZimLive: {e}")
            return []
    
    def _extract_articles_from_homepage(self, soup, max_articles):
        """Extract articles from ZimLive homepage"""
        articles = []
        
        # Multiple selectors to try for different page layouts
        article_selectors = [
            'article.post',
            'div.post',
            'div[class*="post"]',
            'div.entry',
            'div[class*="entry"]',
            'div.story',
            'div[class*="story"]',
            'div.news-item',
            'div[class*="news"]',
            '.elementor-post',
            '.post-item',
            '.blog-post'
        ]
        
        article_containers = []
        
        # Try each selector until we find articles
        for selector in article_selectors:
            containers = soup.select(selector)
            if containers and len(containers) >= 3:  # Need at least 3 for a reasonable selection
                article_containers = containers
                logger.info(f"Using selector '{selector}' - found {len(containers)} containers")
                break
        
        # Fallback: look for links that appear to be articles
        if not article_containers:
            logger.warning("No article containers found, trying fallback approach")
            all_links = soup.find_all('a', href=True)
            potential_articles = []
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Check if this looks like an article link
                if (self._is_likely_article_link(href) and 
                    text and len(text) > 20 and len(text) < 200):
                    potential_articles.append(link)
            
            article_containers = potential_articles[:max_articles]
        
        # Process each container
        for i, container in enumerate(article_containers[:max_articles]):
            try:
                article_data = self._extract_article_data(container)
                if article_data:
                    articles.append(article_data)
                    logger.info(f"Extracted: {article_data['title'][:60]}...")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"Error processing article container {i}: {e}")
                continue
        
        return articles
    
    def _extract_article_data(self, container):
        """Extract article data from a container element"""
        try:
            # Extract link
            if container.name == 'a':
                link_element = container
                link = container.get('href', '')
            else:
                link_element = container.find('a', href=True)
                if not link_element:
                    return None
                link = link_element.get('href', '')
            
            if not link:
                return None
            
            # Make URL absolute
            if link.startswith('/'):
                link = self.base_url + link
            elif not link.startswith('http'):
                link = urljoin(self.base_url, link)
            
            # Skip non-article links
            if not self._is_likely_article_link(link):
                return None
            
            # Extract title
            title = self._extract_title(container, link_element)
            if not title or len(title) < 10:
                return None
            
            # Clean title
            title = self._clean_title(title)
            
            # Extract excerpt/summary if available
            excerpt = self._extract_excerpt(container)
            
            # Get full article content with images
            content_data = self._get_full_article_content(link)
            if not content_data:
                logger.warning(f"Failed to get content for: {title[:50]}...")
                return None
            
            content = content_data.get('content', '')
            all_images = content_data.get('images', [])
            
            if not content or len(content) < 100:
                logger.warning(f"Insufficient content for: {title[:50]}...")
                return None
            
            # Extract publish date if available
            pub_date = self._extract_publish_date(container)
            
            # Set featured image to first extracted image, fallback to container image
            featured_image = None
            if all_images:
                featured_image = all_images[0]['url']
            else:
                featured_image = self._extract_image_url(container)
            
            return {
                'title': title,
                'content': content,
                'source_url': link,
                'source': 'ZimLive',
                'image_url': featured_image,
                'images': all_images,  # Store all images for reference
                'excerpt': excerpt,
                'published_date': pub_date or datetime.now().isoformat(),
                'section': 'Zimbabwe News'
            }
            
        except Exception as e:
            logger.error(f"Error extracting article data: {e}")
            return None
    
    def _extract_title(self, container, link_element):
        """Extract title from various possible locations"""
        title_selectors = [
            'h1',
            'h2', 
            'h3',
            'h4',
            '.post-title',
            '.entry-title',
            '.article-title',
            '.title',
            '[class*="title"]',
            '.headline',
            '[class*="headline"]'
        ]
        
        # Try structured selectors first
        for selector in title_selectors:
            element = container.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 10 and len(title) < 300:
                    return title
        
        # Fallback to link text
        title = link_element.get_text(strip=True)
        if title and len(title) > 10 and len(title) < 300:
            return title
        
        # Try title attribute
        title = link_element.get('title', '').strip()
        if title and len(title) > 10:
            return title
        
        return None
    
    def _extract_image_url(self, container):
        """Extract featured image URL"""
        try:
            # Try different image selectors
            img_selectors = [
                'img',
                '.post-thumbnail img',
                '.featured-image img',
                '.entry-image img',
                'img[class*="featured"]',
                'img[class*="thumb"]'
            ]
            
            for selector in img_selectors:
                img = container.select_one(selector)
                if img:
                    # Try different attributes
                    for attr in ['src', 'data-src', 'data-lazy-src']:
                        img_url = img.get(attr)
                        if img_url:
                            # Make URL absolute
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            elif img_url.startswith('/'):
                                img_url = self.base_url + img_url
                            elif not img_url.startswith('http'):
                                img_url = urljoin(self.base_url, img_url)
                            
                            # Skip placeholder images
                            if ('placeholder' not in img_url.lower() and 
                                'default' not in img_url.lower() and
                                img_url.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))):
                                return img_url
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting image: {e}")
            return None
    
    def _extract_excerpt(self, container):
        """Extract article excerpt/summary"""
        try:
            excerpt_selectors = [
                '.post-excerpt',
                '.entry-summary',
                '.excerpt',
                'p.summary',
                '.description',
                'p:first-of-type'
            ]
            
            for selector in excerpt_selectors:
                element = container.select_one(selector)
                if element:
                    excerpt = element.get_text(strip=True)
                    if excerpt and 50 < len(excerpt) < 300:
                        return excerpt
            
            # Fallback: try to find any paragraph
            paragraphs = container.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and 50 < len(text) < 300:
                    return text
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting excerpt: {e}")
            return None
    
    def _extract_publish_date(self, container):
        """Extract publish date if available"""
        try:
            date_selectors = [
                'time',
                '.post-date',
                '.entry-date', 
                '.published',
                '.date',
                '[class*="date"]',
                '[datetime]'
            ]
            
            for selector in date_selectors:
                element = container.select_one(selector)
                if element:
                    # Try datetime attribute first
                    datetime_attr = element.get('datetime')
                    if datetime_attr:
                        return datetime_attr
                    
                    # Try to parse text content
                    date_text = element.get_text(strip=True)
                    if date_text:
                        # Simple date parsing (you might want to enhance this)
                        try:
                            if 'ago' in date_text.lower():
                                # Handle relative dates like "2 hours ago"
                                return self._parse_relative_date(date_text)
                            else:
                                # Try to parse absolute dates
                                return self._parse_absolute_date(date_text)
                        except:
                            continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting publish date: {e}")
            return None
    
    def _parse_relative_date(self, date_text):
        """Parse relative dates like '2 hours ago'"""
        try:
            import re
            from datetime import timedelta
            
            now = datetime.now()
            
            # Extract number and unit
            match = re.search(r'(\d+)\s*(hour|hr|minute|min|day|week|month)s?\s*ago', date_text.lower())
            if match:
                number = int(match.group(1))
                unit = match.group(2)
                
                if unit in ['hour', 'hr']:
                    return (now - timedelta(hours=number)).isoformat()
                elif unit in ['minute', 'min']:
                    return (now - timedelta(minutes=number)).isoformat()
                elif unit == 'day':
                    return (now - timedelta(days=number)).isoformat()
                elif unit == 'week':
                    return (now - timedelta(weeks=number)).isoformat()
                elif unit == 'month':
                    return (now - timedelta(days=number * 30)).isoformat()
            
            return now.isoformat()
            
        except Exception:
            return datetime.now().isoformat()
    
    def _parse_absolute_date(self, date_text):
        """Parse absolute dates"""
        try:
            from dateutil import parser
            parsed_date = parser.parse(date_text)
            return parsed_date.isoformat()
        except:
            return datetime.now().isoformat()
    
    def _clean_title(self, title):
        """Clean and normalize title"""
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Remove common unwanted patterns
        title = re.sub(r'^Read more:?\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^Continue reading:?\s*', '', title, flags=re.IGNORECASE)
        
        # Remove trailing dots or dashes
        title = title.rstrip('.-')
        
        return title
    
    def _is_likely_article_link(self, url):
        """Check if URL is likely an article"""
        if not url:
            return False
        
        # Must be from the same domain or relative
        parsed = urlparse(url)
        if parsed.netloc and 'zimlive.com' not in parsed.netloc:
            return False
        
        # Skip certain patterns
        skip_patterns = [
            '/category/',
            '/tag/',
            '/author/',
            '/page/',
            '/search/',
            '/feed/',
            '/rss/',
            '/wp-',
            '/admin/',
            'javascript:',
            'mailto:',
            '#',
            '/contact',
            '/about',
            '/privacy',
            '/terms'
        ]
        
        url_lower = url.lower()
        for pattern in skip_patterns:
            if pattern in url_lower:
                return False
        
        # Must have some path (not just domain)
        if parsed.path in ['/', '']:
            return False
        
        return True
    
    def _get_full_article_content(self, url):
        """Get full article content from article page with all images embedded"""
        try:
            logger.debug(f"Fetching content from: {url}")
            # Fetch with crawler to get retries/backoff and optional render later
            soup = self.crawler.get_soup(url)
            if soup is None:
                return None
            
            # Article content selectors to try
            content_selectors = [
                '.post-content',
                '.entry-content', 
                '.article-content',
                '.content',
                'div[class*="content"]',
                '.post-body',
                '.entry-body',
                'article .text',
                '[class*="post-text"]',
                '.elementor-widget-theme-post-content',
                'div[id*="content"]'
            ]
            
            content_container = None
            
            # Try structured content selectors
            for selector in content_selectors:
                container = soup.select_one(selector)
                if container:
                    content_container = container
                    logger.debug(f"Found content using selector: {selector}")
                    break
            
            # Fallback: try to find article tag
            if not content_container:
                content_container = soup.find('article')
            
            if not content_container:
                logger.warning(f"No content container found for {url}")
                return None
            
            # Extract ALL images from the article BEFORE cleaning
            # Pass BeautifulSoup object, not string representation
            all_images = extract_all_images_from_content(
                content_container,
                base_url=self.base_url,
                min_width=150,
                min_height=100
            )
            
            logger.info(f"Extracted {len(all_images)} images from ZimLive article")
            
            # Now clean the content
            for element in content_container.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header', 'form']):
                element.decompose()
            
            # Remove ads and social sharing
            for element in content_container.find_all(attrs={'class': re.compile(r'(ad|advertisement|social|share|related)', re.I)}):
                element.decompose()
            
            # Get all paragraphs
            paragraphs = content_container.find_all('p', recursive=True)
            
            # Filter out unwanted paragraphs
            valid_paragraphs = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 30 and not self._is_unwanted_content(text):
                    valid_paragraphs.append(p)
            
            if not valid_paragraphs:
                logger.warning(f"No valid paragraphs found for {url}")
                return None
            
            # Build HTML content with images strategically placed
            content_html = []
            image_index = 0
            
            for i, paragraph in enumerate(valid_paragraphs[:15]):  # Limit to 15 paragraphs
                # Add paragraph
                content_html.append(str(paragraph))
                
                # Insert images after every 2nd paragraph
                if i > 0 and i % 2 == 0 and image_index < len(all_images):
                    img_data = all_images[image_index]
                    
                    # Create WordPress-style image block
                    img_html = f'<figure class="wp-block-image size-large">'
                    img_html += f'<img src="{img_data["url"]}" alt="{img_data.get("alt", "")}"'
                    
                    if img_data.get('width'):
                        img_html += f' width="{img_data["width"]}"'
                    if img_data.get('height'):
                        img_html += f' height="{img_data["height"]}"'
                    
                    img_html += ' />'
                    
                    if img_data.get('caption'):
                        img_html += f'<figcaption>{img_data["caption"]}</figcaption>'
                    
                    img_html += '</figure>'
                    
                    content_html.append(img_html)
                    image_index += 1
            
            # Join all content
            final_content = '\n'.join(content_html)
            
            # Add source attribution
            final_content += f'\n<p><em>Source: ZimLive - <a href="{url}">{url}</a></em></p>'
            
            if len(final_content) < 200:
                return None
            
            return {
                'content': final_content,
                'images': all_images
            }
            
        except Exception as e:
            logger.error(f"Error getting article content from {url}: {e}")
            return None
    
    def _is_unwanted_content(self, text):
        """Check if text content should be skipped"""
        unwanted_patterns = [
            'subscribe',
            'newsletter',
            'follow us',
            'share this',
            'related articles',
            'read more',
            'continue reading',
            'advertisement',
            'sponsored',
            'cookie',
            'privacy policy',
            'terms of service',
            'all rights reserved',
            'copyright',
            '© 20',
            'leave a comment',
            'post a comment'
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in unwanted_patterns)
    
    def _clean_content(self, content):
        """Clean article content"""
        # Remove extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common unwanted patterns
        content = re.sub(r'Image:.*?\n', '', content)
        content = re.sub(r'Photo:.*?\n', '', content)
        content = re.sub(r'Getty Images.*?\n', '', content)
        
        return content.strip()

# Test function
def test_zimlive_scraper():
    """Test the ZimLive scraper"""
    logging.basicConfig(level=logging.INFO)
    
    scraper = ZimLiveScraper()
    articles = scraper.scrape_zimlive(max_articles=5)
    
    print(f"\nScraped {len(articles)} articles from ZimLive:")
    print("=" * 80)
    
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Content length: {len(article['content'])} characters")
        print(f"Image: {article['image_url'] or 'None'}")
        print(f"Published: {article['published_date']}")
        print(f"Content preview: {article['content'][:200]}...")
        print("-" * 80)

# Wrapper function for compatibility
def scrape_zimlive(max_articles=10):
    """Wrapper function for ZimLive scraper"""
    scraper = ZimLiveScraper()
    return scraper.scrape_zimlive(max_articles)

def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_zimlive(max_articles=max_articles)
    
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
    test_zimlive_scraper()
