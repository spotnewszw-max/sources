from .base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup

def scrape_businessweekly():
    url = "https://www.zimpapers.co.zw/business-weekly/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    for item in soup.select("h3.entry-title a"):
        title = item.get_text(strip=True)
        link = item.get("href")
        articles.append({
            "title": title,
            "url": link,
            "content": f"<p>{title}</p><p>Read more: <a href='{link}'>{link}</a></p>"
        })
    return articles


def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_businessweekly(max_articles=max_articles)
    
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