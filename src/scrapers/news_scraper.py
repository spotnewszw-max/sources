import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from .cache_utils import cache_scraper
from typing import List, Dict

class NewsScraper:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @cache_scraper(prefix="news", expire_seconds=1800)  # 30 minutes cache
    async def fetch_headlines(self, url: str) -> List[Dict[str, str]]:
        """Fetch news headlines with caching"""
        async with self.session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            
            headlines = []
            for article in soup.find_all('article'):
                headline = {
                    'title': article.find('h2').text.strip(),
                    'url': article.find('a')['href'],
                    'timestamp': datetime.now().isoformat()
                }
                headlines.append(headline)
            
            return headlines