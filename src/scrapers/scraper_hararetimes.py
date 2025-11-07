from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Harare Times News Scraper
Scrapes articles from https://hararetimes.news/

Features:
- Efficient article discovery with custom selectors
- Optimized image extraction using meta tags
- Performance tracking and logging
"""

import logging
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.scrapers.base_scraper import BaseScraper
from src.utils.image_utils import OptimizedImageExtractor

logger = logging.getLogger(__name__)


class HarareTimesScraper(BaseScraper):
    def __init__(self, max_articles: int = 10):
        super().__init__(
            "Harare Times",
            [
                "https://hararetimes.news/",
                "https://hararetimes.news/category/news/",
                "https://hararetimes.news/category/politics/",
                "https://hararetimes.news/category/business/",
            ],
            max_articles=max_articles,
        )
        # Initialize optimized image extractor with connection pooling
        self.image_extractor = OptimizedImageExtractor(timeout=20)

    def _fetch_full_article(self, url: str, title: str) -> dict:
        """Override to add image extraction for Harare Times"""
        article = super()._fetch_full_article(url, title)
        if article:
            # Add featured image
            logger.debug(f"_fetch_full_article: Adding image for {url}")
            article = self._add_featured_image(article, url)
            logger.debug(f"_fetch_full_article: After image add, has image_url: {'image_url' in article}")
        return article

    def _is_valid_article_url(self, url: str) -> bool:
        """Check if URL is a valid article URL"""
        L = (url or "").lower()
        if not "hararetimes.news" in L:
            return False
        
        # Exclude obvious non-articles
        skip = [
            "/category/",
            "/tag/",
            "/author/",
            "/page/",
            "/contact",
            "/about",
            "/wp-login",
            "/wp-admin",
            "/?s=",
            "/search",
        ]
        if any(p in L for p in skip):
            return False
        
        # Accept article URLs (they typically have year/month pattern or are deep paths)
        if "/20" in L:  # Year pattern (2024, 2025, etc.)
            return True
        
        # Accept URLs with sufficient depth (article permalinks)
        path_parts = L.strip("/").split("/")
        if len(path_parts) >= 2:  # Domain + at least one path segment
            return True
        
        return False

    def scrape_webpage(self) -> List[Dict]:
        """Custom scraping implementation for Harare Times"""
        articles: List[Dict] = []
        try:
            for base in self.base_urls:
                if len(articles) >= self.max_articles:
                    break
                
                # Try rendered first for better JS content, fallback to non-render
                html = self.fetcher.get_html(base, render=True, timeout=20) or self.fetcher.get_html(
                    base, render=False, timeout=25
                )
                if not html:
                    continue
                
                soup = BeautifulSoup(html, "html.parser")

                # Harare Times uses various selectors for article links
                link_selectors = [
                    "h2.entry-title a",
                    "h3.entry-title a",
                    ".entry-title a",
                    "article h2 a",
                    "article h3 a",
                    ".post-title a",
                    ".jeg_post_title a",
                    ".wp-block-post-title a",
                    "a[href*='/20']",  # Year in URL
                ]
                
                link_elems = []
                for sel in link_selectors:
                    try:
                        elems = soup.select(sel)
                        if elems:
                            link_elems.extend(elems)
                            logger.info(f"Selector '{sel}' -> {len(elems)} elements")
                    except Exception:
                        continue

                if not link_elems:
                    # Fallback: all anchors
                    link_elems = soup.find_all("a", href=True)

                seen = set()
                for a in link_elems:
                    if len(articles) >= self.max_articles:
                        break
                    
                    href = (a.get("href", "") or "").strip()
                    if not href:
                        continue
                    
                    url = urljoin(base, href)
                    if url in seen:
                        continue
                    seen.add(url)

                    title = (a.get_text(strip=True) or "").strip()
                    if not title or len(title) < 10:
                        continue

                    if not self._is_valid_article_url(url):
                        continue

                    art = self._fetch_full_article(url, title)
                    if art:
                        articles.append(art)

            return articles
        except Exception as e:
            logger.warning(f"Harare Times custom scrape failed: {e}")
            return articles

    def _add_featured_image(self, article: Dict, url: str) -> Dict:
        """Extract featured image using optimized extractor with connection pooling"""
        try:
            # Try meta tags first (fastest and most reliable)
            img_url = self.image_extractor.extract_image(url, priority='meta')
            
            if not img_url:
                # Fallback to featured images
                img_url = self.image_extractor.extract_image(url, priority='featured')
            
            if not img_url:
                # Final fallback to content images
                img_url = self.image_extractor.extract_image(url, priority='content')
            
            if img_url:
                article['image_url'] = img_url
                logger.debug(f"✓ Image extracted: {img_url[:80]}")
            else:
                logger.debug(f"No image found for: {url}")
                
        except Exception as e:
            logger.debug(f"Image extraction error for {url}: {e}")
        
        return article

    def _is_valid_image_url(self, url: str) -> bool:
        """Check if image URL is valid and not a placeholder"""
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Skip data URIs and placeholders
        if url_lower.startswith('data:'):
            return False
        
        # Skip logos and common placeholders
        bad_keywords = ['logo', 'placeholder', 'default', 'avatar', 'favicon', 'sprite', 'icon']
        if any(keyword in url_lower for keyword in bad_keywords):
            return False
        
        # Accept common image extensions
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
        return url_lower.endswith(valid_extensions)


def scrape_hararetimes(max_articles: int = 10) -> List[Dict]:
    """Main entry point for Harare Times scraper"""
    return HarareTimesScraper(max_articles=max_articles).scrape()


def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    return scrape_hararetimes(max_articles=max_articles)
