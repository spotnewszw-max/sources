import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timezone
import logging

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class NewzianaScraper(BaseScraper):
    """Scraper for Newziana news website"""

    BASE_URL = "https://newziana.co.zw"

    def _get_base_article_data(self) -> Dict[str, str]:
        return {
            "source": self.source_name,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "title": "",
            "content": "",
            "url": "",
            "author": "",
            "published_date": "",
            "images": [],
            "links": []
        }

    async def fetch_headlines(self, category: str = "") -> List[Dict[str, str]]:
        url = f"{self.BASE_URL}/{category}" if category else self.BASE_URL
        html = await self._fetch_page(url)
        if not html:
            return []

        soup = self.parser.parse(html)
        articles = []

        for article in soup.find_all("article"):
            try:
                title_el = article.find(["h1", "h2", "h3"])
                link_el = article.find("a", href=True)
                excerpt_el = article.find(class_=["entry-content", "content", "excerpt"])
                img = article.find("img")
                thumbnail = img.get("src", "") if img else ""

                headline = {
                    **self._get_base_article_data(),
                    "title": self.parser.extract_text(title_el),
                    "url": link_el.get("href") if link_el else "",
                    "excerpt": self.parser.extract_text(excerpt_el),
                    "thumbnail": thumbnail,
                }
                articles.append(headline)
            except Exception as e:
                logger.debug(f"Error parsing Newziana headline: {e}")
                continue

        return articles

    async def fetch_article(self, url: str) -> Optional[Dict[str, str]]:
        html = await self._fetch_page(url)
        if not html:
            return None

        soup = self.parser.parse(html)
        article_data = self.parser.extract_article_content(soup)
        metadata = self.parser.extract_metadata(soup)

        return {
            **self._get_base_article_data(),
            **article_data,
            **metadata,
            "url": url,
        }