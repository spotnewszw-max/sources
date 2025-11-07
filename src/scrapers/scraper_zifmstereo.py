from .base_scraper import BaseScraper
import requests
#!/usr/bin/env python3
"""
ZIFM Stereo scraper (standardized)
- RSS-first via BaseScraper
- Generic and simple homepage fallback
- Standard output keys: title, content, source_url, source, image_url (optional)
"""
import logging
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.scrapers.base_scraper import BaseScraper
from src.scrapers.base_scraper import validate_article_quality

logger = logging.getLogger(__name__)


class ZIFMStereoScraper(BaseScraper):
    def __init__(self, max_articles: int = 10):
        super().__init__("ZIFM Stereo", [
            "https://zifmstereo.co.zw/",
        ], max_articles=max_articles)

    def scrape_webpage(self) -> List[Dict]:
        results: List[Dict] = []
        base = self.base_urls[0]
        try:
            resp = self.session.get(base, timeout=20)
            if getattr(resp, "status_code", 0) != 200:
                return []
            soup = BeautifulSoup(getattr(resp, "content", b""), "html.parser")

            selectors = [
                ".elementor-post__title a",
                "h2.entry-title a",
                "article h2 a",
            ]
            links = []
            for sel in selectors:
                links = soup.select(sel)
                if links:
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

                article = self._fetch_full_article(href, title)
                if article and validate_article_quality(article):
                    results.append(article)
        except Exception as e:
            logger.warning("ZIFM webpage scrape failed: %s", e)
        return results


def scrape_zifmstereo(max_articles: int = 10) -> List[Dict]:
    return ZIFMStereoScraper(max_articles=max_articles).scrape()




def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_zifmstereo(max_articles=max_articles)
    
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
    parser = argparse.ArgumentParser(description="Smoke test for ZIFM Stereo scraper")
    parser.add_argument("-n", "--num", type=int, default=3, help="Number of articles to fetch")
    args = parser.parse_args()

    try:
        items = scrape_zifmstereo(args.num)
        # Print count and a single sample to avoid overly large stdout
        print(json.dumps({"count": len(items), "sample": items[:1]}, ensure_ascii=False, indent=2))
        sys.exit(0)
    except Exception:
        logging.exception("ZIFM smoke test failed")
        sys.exit(1)
