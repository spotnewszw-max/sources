from .base_scraper import BaseScraper
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Chat263Scraper(BaseScraper):
    """Scraper for 263Chat news website"""

    BASE_URL = "https://263chat.com"

    async def fetch_headlines(self) -> List[Dict[str, str]]:
        html = await self._fetch_page(self.BASE_URL)
        if not html:
            return []

        soup = self.parser.parse(html)
        articles = []

        for article in soup.find_all("article"):
            try:
                title_el = article.find(["h2", "h3", "h1"])
                link_el = article.find("a", href=True)
                excerpt_el = article.find(class_=["excerpt", "entry-summary", "post-excerpt"])
                thumbnail = ""
                img = article.find("img")
                if img:
                    thumbnail = img.get("src", "")

                headline = {
                    **self._get_base_article_data(),
                    "title": self.parser.extract_text(title_el),
                    "url": link_el.get("href") if link_el else "",
                    "excerpt": self.parser.extract_text(excerpt_el),
                    "thumbnail": thumbnail
                }
                articles.append(headline)
            except Exception as e:
                logger.debug(f"Error parsing headline entry: {e}")
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
            "url": url
        }