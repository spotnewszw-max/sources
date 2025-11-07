from .base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup

def scrape_stateofthenation(max_articles=10):
    articles = []
    url = "http://stateofthenation.co.zw"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.select("h2.entry-title a")[:max_articles]:
            link = a.get("href")
            title = a.get_text(strip=True)
            try:
                article_resp = requests.get(link, headers=headers, timeout=10)
                article_resp.raise_for_status()
                article_soup = BeautifulSoup(article_resp.text, "html.parser")
                body = article_soup.select_one("div.td-post-content")
                articles.append({
                    "title": title,
                    "url": link,
                    "html": str(body) if body else "",
                    "image_url": None
                })
            except Exception as e:
                print(f"Failed to fetch article: {link} ({e})")
    except Exception as e:
        print(f"Failed to fetch main page: {url} ({e})")
    return articles

def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_stateofthenation(max_articles=max_articles)
    
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