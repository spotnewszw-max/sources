from pathlib import Path
from typing import Any
import logging
import time
import asyncio

# Add project root to Python path for standalone runs (if needed)
import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.utils.cache import cache
from src.scrapers.cache_utils import generate_cache_key, invalidate_scraper_cache
from src.scrapers.html_utils import HTMLParser
from src.scrapers.newziana_scraper import NewzianaScraper

logging.basicConfig(level=logging.INFO)

def assert_test(name: str, condition: bool, actual: Any = None, expected: Any = None):
    status = "✅" if condition else "❌"
    result = f"{status} {name}"
    if not condition and actual is not None:
        result += f"\n   Expected: {expected}\n   Got     : {actual}"
    print(result)
    assert condition, f"{name} failed: expected {expected} got {actual}"

# --- Tests converted to use plain asserts ---

async def test_scraper_cache():
    print("\n5️⃣ Testing scraper cache:")

    # Test cache key generation stability
    key1 = generate_cache_key("test", "arg1", kwarg1="value1")
    key2 = generate_cache_key("test", "arg1", kwarg1="value1")
    assert_test("Cache key stability", key1 == key2, key1, key2)

    # Test scraper cache invalidation
    cache.set(key1, "test_value", 60)
    invalidate_scraper_cache("test")
    result = cache.get(key1)
    assert_test("Scraper cache invalidation", result is None, result, None)

async def test_html_parser():
    print("\n6️⃣ Testing HTML parser:")

    html = """
    <html>
        <head>
            <title>Test Article</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <article>
                <h1>Article Title</h1>
                <div class="content">
                    <p>Test content</p>
                    <img src="test.jpg" alt="Test image">
                    <a href="https://example.com">Test link</a>
                </div>
            </article>
        </body>
    </html>
    """

    parser = HTMLParser()
    soup = parser.parse(html)

    metadata = parser.extract_metadata(soup)
    assert_test("Metadata extraction", metadata["title"] == "Test Article", metadata["title"], "Test Article")

    article = parser.extract_article_content(soup)
    assert_test("Article content extraction", article["title"] == "Article Title" and len(article["images"]) == 1, article, "Expected article with title and image")

async def test_newziana_scraper(monkeypatch):
    print("\n7️⃣ Testing Newziana scraper:")

    async def fake_fetch(self, url, timeout=10):
        # minimal headlines page
        return """
        <html>
          <body>
            <article class="entry">
              <h2 class="entry-title"><a href="https://newziana.co.zw/news/1">NZ Headline</a></h2>
              <div class="entry-content"><p>Excerpt</p></div>
              <img src="thumb.jpg"/>
            </article>
          </body>
        </html>
        """

    monkeypatch.setattr(NewzianaScraper, "_fetch_page", fake_fetch)

    async with NewzianaScraper() as scraper:
        headlines = await scraper.fetch_headlines()
        assert_test("Fetch headlines", len(headlines) > 0, len(headlines), ">0")

        if headlines:
            # Fake full article fetch
            async def fake_article(self, url, timeout=10):
                return """
                <html><head><title>Article</title></head>
                <body><article><h1>Article Title</h1><div class="content"><p>Full content</p></div></article></body></html>
                """
            monkeypatch.setattr(NewzianaScraper, "_fetch_page", fake_article)
            article = await scraper.fetch_article(headlines[0]["url"])
            assert_test("Fetch article", article is not None and ("content" in article or article.get("title")), article, "article dict")

# expose sync wrappers so pytest can discover as async tests via pytest-asyncio
import pytest

@pytest.mark.asyncio
async def run_test_scraper_cache():
    await test_scraper_cache()

@pytest.mark.asyncio
async def run_test_html_parser():
    await test_html_parser()

@pytest.mark.asyncio
async def run_test_newziana_scraper(monkeypatch):
    await test_newziana_scraper(monkeypatch)