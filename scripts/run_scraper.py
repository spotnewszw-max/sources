import sys
import asyncio
from src.scrapers.manager import scraper_manager

async def main(name: str):
    try:
        ScraperClass = scraper_manager.get_scraper(name)
    except KeyError:
        print("Available scrapers:", scraper_manager.list_scrapers())
        raise SystemExit(1)

    async with ScraperClass() as scraper:
        headlines = await scraper.fetch_headlines()
        for h in headlines[:10]:
            print(h.get("title") or h.get("url"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_scraper.py <scraper_name>")
        print("Available:", scraper_manager.list_scrapers())
        raise SystemExit(1)
    asyncio.run(main(sys.argv[1]))