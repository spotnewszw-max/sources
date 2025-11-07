from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from .html_utils import HTMLParser
from .cache_utils import cache_scraper
import aiohttp
import logging
from . import monitor
import asyncio

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.parser = HTMLParser()
        self.source_name = self.__class__.__name__.replace("Scraper", "").lower()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None

    async def _fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            async with self.session.get(url, timeout=timeout) as resp:
                resp.raise_for_status()
                return await resp.text()
        except Exception as e:
            logger.debug(f"[{self.source_name}] fetch error {url}: {e}")
            return None

    def _get_base_article_data(self) -> Dict[str, str]:
        return {
            "source": self.source_name,
            "scraped_at": datetime.utcnow().isoformat(),
            "title": "",
            "content": "",
            "url": "",
            "author": "",
            "published_date": "",
            "images": [],
            "links": []
        }

    # Helper decorator for instrumentation around async methods
    @staticmethod
    def instrument(op: str):
        def decorator(func):
            async def wrapper(self, *args, **kwargs):
                labels = {"scraper": getattr(self, "source_name", "unknown"), "op": op}
                with monitor.SCRAPER_LATENCY.labels(**labels).time():
                    monitor.SCRAPER_REQUESTS.labels(**labels).inc()
                    try:
                        return await func(self, *args, **kwargs)
                    except Exception as e:
                        monitor.SCRAPER_ERRORS.labels(**labels).inc()
                        logger.exception(f"[{labels['scraper']}] error in {op}: {e}")
                        raise
            return wrapper
        return decorator

    # Subclasses must implement these; caching done at subclass level via cache_scraper
    @abstractmethod
    async def fetch_headlines(self) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    async def fetch_article(self, url: str) -> Optional[Dict[str, str]]:
        pass