"""
Web Scraper Service
Scrapes news articles from various news websites with duplicate detection
"""

import logging
import asyncio
import aiohttp
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
import difflib
from collections import defaultdict

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrapes news articles from websites"""
    
    # Pre-configured scraper configurations for popular Zimbabwe news sites
    DEFAULT_CONFIGS = {
        # ===== ZIMBABWE LOCAL NEWS =====
        "herald": {
            "site_name": "The Herald Zimbabwe",
            "site_url": "https://www.herald.co.zw",
            "source_category": "zimbabwe_local",
            "scraper_type": "beautifulsoup",
            "article_selector": "article.post, div.post-item, article.entry",
            "title_selector": "h2.post-title, h2.entry-title, a.post-link",
            "content_selector": "div.post-content, div.entry-content, p.post-excerpt",
            "author_selector": "span.author, span.post-author",
            "date_selector": "time.post-date, span.published, time.entry-date",
            "image_selector": "img.post-image, img.featured-image",
            "scrape_interval_minutes": 60,
        },
        "newsday": {
            "site_name": "NewsDay Zimbabwe",
            "site_url": "https://www.newsday.co.zw",
            "source_category": "zimbabwe_local",
            "scraper_type": "beautifulsoup",
            "article_selector": "article, div.news-item",
            "title_selector": "h2, h3.news-title",
            "content_selector": "div.news-content, p.summary",
            "author_selector": "span.author",
            "date_selector": "time, span.date",
            "image_selector": "img.news-image, img.featured",
            "scrape_interval_minutes": 60,
        },
        "bulawayo24": {
            "site_name": "Bulawayo24",
            "site_url": "https://bulawayo24.com",
            "source_category": "zimbabwe_local",
            "scraper_type": "beautifulsoup",
            "article_selector": "div.article, article.post",
            "title_selector": "h2.article-title, h2.post-title",
            "content_selector": "div.article-body, div.post-content",
            "author_selector": "span.author",
            "date_selector": "time.article-date, span.published",
            "image_selector": "img.article-image",
            "scrape_interval_minutes": 60,
        },
        "zimbabwean": {
            "site_name": "The Zimbabwean",
            "site_url": "https://www.thezimbabwean.co.uk",
            "source_category": "zimbabwe_local",
            "scraper_type": "beautifulsoup",
            "article_selector": "article.post, div.post-item",
            "title_selector": "h2.entry-title, h1.post-title",
            "content_selector": "div.entry-content, div.post-body",
            "author_selector": "span.author-name",
            "date_selector": "span.published-date",
            "image_selector": "img.entry-image",
            "scrape_interval_minutes": 120,
        },
        # ===== AFRICAN REGIONAL NEWS =====
        "allafrica": {
            "site_name": "AllAfrica Zimbabwe",
            "site_url": "https://allafrica.com/zimbabwe",
            "source_category": "regional_african",
            "scraper_type": "beautifulsoup",
            "article_selector": "div.story-item, article.story",
            "title_selector": "h2.story-title, a.story-link",
            "content_selector": "p.story-excerpt, div.story-summary",
            "author_selector": "span.source",
            "date_selector": "span.story-date, time",
            "image_selector": "img.story-image",
            "scrape_interval_minutes": 120,
        },
        "mg": {
            "site_name": "Mail & Guardian Africa",
            "site_url": "https://mg.co.za/category/africa",
            "source_category": "regional_african",
            "scraper_type": "beautifulsoup",
            "article_selector": "article.article-card, div.article-item",
            "title_selector": "h2.article-title, a.article-link",
            "content_selector": "p.article-excerpt, div.article-summary",
            "date_selector": "time.publish-date",
            "image_selector": "img.article-image",
            "scrape_interval_minutes": 180,
        },
        # ===== INTERNATIONAL NEWS (Zimbabwe coverage) =====
        "bbc_africa": {
            "site_name": "BBC Africa",
            "site_url": "https://www.bbc.com/news/world/africa",
            "source_category": "international",
            "scraper_type": "beautifulsoup",
            "article_selector": "a[data-testid='internal-link']",
            "title_selector": "h2, h3",
            "content_selector": "p",
            "date_selector": "time",
            "scrape_interval_minutes": 180,
        },
        "reuters": {
            "site_name": "Reuters Africa",
            "site_url": "https://www.reuters.com/world/africa",
            "source_category": "international",
            "scraper_type": "beautifulsoup",
            "article_selector": "div[data-testid='Link']",
            "title_selector": "h3",
            "date_selector": "time",
            "scrape_interval_minutes": 180,
        },
        "aljazeera": {
            "site_name": "Al Jazeera Africa",
            "site_url": "https://www.aljazeera.com/news",
            "source_category": "international",
            "scraper_type": "beautifulsoup",
            "article_selector": "article, div.article-item",
            "title_selector": "h2, h3",
            "date_selector": "time",
            "scrape_interval_minutes": 180,
        },
    }
    
    def __init__(self):
        self.beautifulsoup_available = BEAUTIFULSOUP_AVAILABLE
        self.selenium_available = SELENIUM_AVAILABLE
        
        if not BEAUTIFULSOUP_AVAILABLE:
            logger.warning("BeautifulSoup not available. Install: pip install beautifulsoup4")
    
    async def scrape_website(self, config: Dict, max_articles: int = 50) -> List[Dict]:
        """
        Scrape articles from a website
        
        Args:
            config: Configuration dict with scraper settings
            max_articles: Maximum articles to scrape
            
        Returns:
            List of scraped articles with metadata
        """
        if not BEAUTIFULSOUP_AVAILABLE:
            logger.error("BeautifulSoup not installed")
            return []
        
        articles = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config['site_url'], timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        articles = self._parse_articles(soup, config, max_articles)
                        logger.info(f"Scraped {len(articles)} articles from {config['site_name']}")
        except Exception as e:
            logger.error(f"Error scraping {config['site_name']}: {e}")
        
        return articles
    
    def _parse_articles(self, soup: 'BeautifulSoup', config: Dict, max_articles: int) -> List[Dict]:
        """Parse articles from soup"""
        articles = []
        
        try:
            # Find all article containers
            article_elements = soup.select(config['article_selector'])[:max_articles]
            
            for element in article_elements:
                article_data = self._extract_article_data(element, config)
                if article_data and article_data.get('title') and article_data.get('url'):
                    articles.append(article_data)
            
        except Exception as e:
            logger.error(f"Error parsing articles: {e}")
        
        return articles
    
    def _extract_article_data(self, element, config: Dict) -> Optional[Dict]:
        """Extract article data from HTML element"""
        try:
            article = {}
            
            # Title
            title_elem = element.select_one(config.get('title_selector', 'h2'))
            article['title'] = title_elem.get_text(strip=True) if title_elem else None
            
            # Content/excerpt
            content_elem = element.select_one(config.get('content_selector', 'p'))
            article['content'] = content_elem.get_text(strip=True) if content_elem else None
            
            # URL
            link_elem = element.find('a', href=True)
            if link_elem:
                article['url'] = link_elem['href']
                # Make absolute URL
                if not article['url'].startswith('http'):
                    base_url = config['site_url']
                    article['url'] = urljoin(base_url, article['url'])
            
            # Author
            author_elem = element.select_one(config.get('author_selector', 'span.author'))
            article['author'] = author_elem.get_text(strip=True) if author_elem else None
            
            # Date
            date_elem = element.select_one(config.get('date_selector', 'time'))
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                article['published_date'] = date_str
            
            # Image
            image_elem = element.select_one(config.get('image_selector', 'img'))
            if image_elem:
                img_url = image_elem.get('src') or image_elem.get('data-src')
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = urljoin(config['site_url'], img_url)
                    article['image_url'] = img_url
            
            # Add metadata
            article['source_site'] = config['site_name']
            article['source_category'] = config['source_category']
            article['scraper_method'] = config.get('scraper_type', 'beautifulsoup')
            article['extraction_confidence'] = 0.85
            article['scraped_date'] = datetime.utcnow().isoformat()
            
            return article if article.get('title') else None
            
        except Exception as e:
            logger.debug(f"Error extracting article data: {e}")
            return None
    
    async def scrape_all_configured(self, db_config_list: List[Dict], max_articles: int = 50) -> List[Dict]:
        """
        Scrape multiple websites concurrently
        
        Args:
            db_config_list: List of scraper configurations from database
            max_articles: Max articles per site
            
        Returns:
            List of all scraped articles
        """
        tasks = []
        for config in db_config_list:
            if config.get('is_active', True):
                tasks.append(self.scrape_website(config, max_articles))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
        
        return all_articles


class DuplicateDetector:
    """Detects duplicate and similar content across sources"""
    
    def __init__(self, similarity_threshold: float = 0.75):
        self.similarity_threshold = similarity_threshold
    
    def detect_duplicates(self, articles: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Detect duplicates within article list
        
        Args:
            articles: List of articles (from all sources)
            
        Returns:
            Tuple of (unique_articles, duplicate_records)
        """
        unique_articles = []
        duplicates = []
        seen_titles = {}
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            
            # Check against previously seen titles
            is_duplicate = False
            for seen_title, original_idx in seen_titles.items():
                similarity = self._calculate_similarity(title, seen_title)
                
                if similarity >= self.similarity_threshold:
                    # This is a duplicate
                    duplicate_record = {
                        'canonical_idx': original_idx,
                        'duplicate_idx': len(unique_articles),
                        'title_similarity': similarity,
                        'type': 'exact' if similarity > 0.95 else 'near_duplicate'
                    }
                    duplicates.append(duplicate_record)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles[title] = len(unique_articles)
                unique_articles.append(article)
        
        return unique_articles, duplicates
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)"""
        if not text1 or not text2:
            return 0.0
        
        # Use SequenceMatcher for quick similarity check
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        return similarity
    
    def find_duplicate_sources(self, article: Dict, existing_articles: List[Dict]) -> List[str]:
        """
        Find other sources with same/similar content
        
        Args:
            article: Article to check
            existing_articles: List of existing articles in database
            
        Returns:
            List of URLs with duplicate/similar content
        """
        article_title = article.get('title', '').lower().strip()
        article_content = article.get('content', '').lower().strip()
        
        duplicates = []
        
        for existing in existing_articles:
            existing_title = existing.get('title', '').lower().strip()
            existing_content = existing.get('content', '').lower().strip()
            
            # Check title similarity
            title_sim = self._calculate_similarity(article_title, existing_title)
            
            # Check content similarity (first 200 chars)
            content_sim = 0
            if article_content and existing_content:
                content_sim = self._calculate_similarity(
                    article_content[:200], 
                    existing_content[:200]
                )
            
            # If high similarity on both, it's a duplicate
            if (title_sim >= 0.85 or content_sim >= 0.80):
                duplicates.append(existing.get('url'))
        
        return duplicates


class ContentAnalyzerForScraped:
    """Analyzes scraped articles for relevance, entities, and sentiment"""
    
    ZIMBABWE_KEYWORDS = {
        "Politics": [
            "parliament", "minister", "government", "election", "opposition", 
            "zanu-pf", "mdc", "political", "legislation", "parliament"
        ],
        "Economy": [
            "inflation", "economy", "currency", "dollar", "rtgs", "bond", 
            "economic", "business", "market", "trade", "investment"
        ],
        "Agriculture": [
            "farming", "agriculture", "crops", "harvest", "drought", "land", 
            "farmer", "rural", "commercial farming"
        ],
        "Health": [
            "health", "disease", "medical", "hospital", "doctor", "covid", 
            "pandemic", "healthcare", "patient"
        ],
        "Education": [
            "education", "school", "university", "student", "exam", "teacher", 
            "learning", "academic"
        ],
    }
    
    SENTIMENT_POSITIVE = ["good", "better", "growth", "success", "positive", "improvement", "gain"]
    SENTIMENT_NEGATIVE = ["bad", "worse", "decline", "fail", "negative", "crisis", "loss", "problem"]
    
    def calculate_relevance(self, article: Dict) -> float:
        """Calculate Zimbabwe relevance score (0-1)"""
        score = 0.0
        max_score = 0.0
        
        title = (article.get('title') or '').lower()
        content = (article.get('content') or '').lower()
        combined = title + ' ' + content
        
        # Check for Zimbabwe mentions
        if any(kw in combined for kw in ['zimbabwe', 'zim', 'harare', 'bulawayo', 'zvimba']):
            score += 0.4
            max_score += 0.4
        
        # Check for key political figures
        politicians = ['mnangagwa', 'chamisa', 'ncube', 'chiwenga', 'masiyiwa', 'musewe']
        if any(pol in combined for pol in politicians):
            score += 0.3
            max_score += 0.3
        
        # Check for key topics
        for category, keywords in self.ZIMBABWE_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                score += 0.2
                max_score += 0.2
                break
        
        max_score = max(max_score, 0.1)  # Avoid division issues
        relevance = min(score / max_score, 1.0) if max_score > 0 else 0.0
        
        return relevance
    
    def extract_category(self, article: Dict) -> str:
        """Extract primary category"""
        combined = (article.get('title') or '') + ' ' + (article.get('content') or '')
        combined_lower = combined.lower()
        
        for category, keywords in self.ZIMBABWE_KEYWORDS.items():
            if any(kw in combined_lower for kw in keywords):
                return category
        
        return "General"
    
    def analyze_sentiment(self, article: Dict) -> str:
        """Simple sentiment analysis"""
        combined = (article.get('title') or '') + ' ' + (article.get('content') or '')
        combined_lower = combined.lower()
        
        positive_count = sum(1 for word in self.SENTIMENT_POSITIVE if word in combined_lower)
        negative_count = sum(1 for word in self.SENTIMENT_NEGATIVE if word in combined_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"


async def main():
    """Test scraper"""
    scraper = WebScraper()
    
    # Test with herald config
    config = WebScraper.DEFAULT_CONFIGS['herald']
    articles = await scraper.scrape_website(config, max_articles=5)
    
    print(f"Found {len(articles)} articles:")
    for article in articles:
        print(f"  - {article['title']}")
    
    # Test duplicate detection
    detector = DuplicateDetector()
    unique, dups = detector.detect_duplicates(articles)
    print(f"\nUnique: {len(unique)}, Duplicates: {len(dups)}")


if __name__ == "__main__":
    asyncio.run(main())