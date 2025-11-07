import asyncio
import pytest
from pathlib import Path
from src.scrapers.scraper_263chat import Chat263Scraper

SAMPLE_HTML = """
<html>
  <body>
    <article>
      <h2><a href="https://263chat.com/news/1">Test Headline</a></h2>
      <div class="excerpt"><p>Short excerpt</p></div>
      <img src="https://example.com/thumb.jpg" alt="thumb">
    </article>
  </body>
</html>
"""

@pytest.mark.asyncio
async def test_263chat_headlines(monkeypatch):
    async def fake_fetch(self, url, timeout=10):
        return SAMPLE_HTML

    monkeypatch.setattr(Chat263Scraper, "_fetch_page", fake_fetch)

    async with Chat263Scraper() as scraper:
        headlines = await scraper.fetch_headlines()
        assert isinstance(headlines, list)
        assert len(headlines) == 1
        assert "Test Headline" in headlines[0]["title"] or "Test Headline" == headlines[0]["title"]

@pytest.mark.asyncio
async def test_263chat_article(monkeypatch):
    async def fake_fetch(self, url, timeout=10):
        # return a fuller article HTML
        return """
        <html>
          <head><title>Article Page</title></head>
          <body>
            <article>
              <h1>Article Title</h1>
              <div class="content"><p>Full content here</p></div>
              <img src="img.jpg" alt="i">
            </article>
            <meta name="description" content="meta desc">
          </body>
        </html>
        """

    monkeypatch.setattr(Chat263Scraper, "_fetch_page", fake_fetch)

    async with Chat263Scraper() as scraper:
        article = await scraper.fetch_article("https://263chat.com/news/1")
        assert article is not None
        assert "Article Title" in article.get("title", "") or article.get("content", "")