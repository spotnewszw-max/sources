from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
EarGround scraper (standardized)
- RSS-first via BaseScraper
- Simple homepage fallback using common selectors
- Standard output keys
"""
import logging
import requests
import urllib3
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.scrapers.base_scraper import BaseScraper
from src.scrapers.base_scraper import validate_article_quality

# Disable SSL warnings for this specific scraper
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class EarGroundScraper(BaseScraper):
    def __init__(self, max_articles: int = 10):
        # Use www subdomain first as earground.com doesn't resolve properly
        super().__init__(
            "EarGround",
            [
                "https://www.earground.com/",
                "https://earground.com/",
                "http://www.earground.com/",
                "http://earground.com/",
            ],
            max_articles=max_articles,
        )
        # Create a custom session with SSL verification disabled
        self.custom_session = requests.Session()
        self.custom_session.verify = False
        self.custom_session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def scrape_webpage(self) -> List[Dict]:
        results: List[Dict] = []
        base = self.base_urls[0]
        try:
            # Use custom session with SSL verification disabled
            resp = self.custom_session.get(base, timeout=20, verify=False)
            if resp.status_code != 200:
                return []
            soup = BeautifulSoup(resp.content, "html.parser")

            selectors = [
                ".elementor-post__title a",
                "h2.entry-title a",
                "article h2 a",
                "h6 a",  # EarGround uses h6 for article titles
            ]
            links = []
            for sel in selectors:
                links = soup.select(sel)
                if links:
                    logger.info(f"EarGround: Found {len(links)} links with selector '{sel}'")
                    break

            seen = set()
            for a in links:
                if len(results) >= self.max_articles:
                    break
                href = (a.get("href", "") or "").strip()
                title = (a.get_text(strip=True) or "").strip()
                if not href or not title or len(title) < 8:
                    continue
                href = urljoin(base, href)
                if href in seen:
                    continue
                seen.add(href)

                article = self._fetch_full_article_custom(href, title)
                if article and validate_article_quality(article):
                    results.append(article)
        except Exception as e:
            logger.warning("EarGround webpage scrape failed: %s", e)
        return results
    
    def _fetch_full_article_custom(self, url: str, title: str) -> Dict:
        """Fetch article with custom SSL-disabled session"""
        try:
            from utils.scraper_enhanced import extract_article_content
            resp = self.custom_session.get(url, timeout=20, verify=False)
            if resp.status_code != 200:
                return {}
            
            soup = BeautifulSoup(resp.content, "html.parser")
            content_html = extract_article_content(soup, url)
            
            if not content_html or len(content_html) < 100:
                return {}
            
            # Try to extract featured image
            image_url = None
            try:
                # Look for common image patterns
                img_selectors = [
                    'meta[property="og:image"]',
                    'meta[name="twitter:image"]',
                    '.featured-image img',
                    'article img',
                    '.post-thumbnail img'
                ]
                for selector in img_selectors:
                    img_tag = soup.select_one(selector)
                    if img_tag:
                        if img_tag.name == 'meta':
                            image_url = img_tag.get('content')
                        else:
                            image_url = img_tag.get('src')
                        if image_url:
                            break
            except Exception:
                pass
            
            return {
                "title": title,
                "content": content_html,
                "source_url": url,
                "source": "EarGround",
                "image_url": image_url
            }
        except Exception as e:
            logger.warning(f"Failed to fetch EarGround article {url}: {e}")
            return {}


def scrape_earground(max_articles: int = 10) -> List[Dict]:
    return EarGroundScraper(max_articles=max_articles).scrape()




def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_earground(max_articles=max_articles)
    
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
    # Simple CLI smoke test for quick validation
    import argparse, json, sys, logging

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Smoke test for EarGround scraper")
    parser.add_argument("-n", "--num", type=int, default=3, help="Number of articles to fetch")
    args = parser.parse_args()

    try:
        items = scrape_earground(args.num)
        # Print count and a single sample to avoid overly large stdout
        print(json.dumps({"count": len(items), "sample": items[:1]}, ensure_ascii=False, indent=2))
        sys.exit(0)
    except Exception:
        logging.exception("EarGround smoke test failed")
        sys.exit(1)
