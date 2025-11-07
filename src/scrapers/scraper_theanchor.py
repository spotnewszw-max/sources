from .base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup

def scrape_theanchor(max_articles=10):
    articles = []
    url = "https://www.theanchor.co.zw/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        selectors = "h2.entry-title a, .entry-title a, article h2 a, .jeg_post_title a"
        for a in soup.select(selectors)[:max_articles * 3]:
            link = a.get("href")
            title = a.get_text(strip=True)
            if not link or not title or len(title) < 8:
                continue
            try:
                article_resp = requests.get(link, headers=headers, timeout=20)
                article_resp.raise_for_status()
                article_soup = BeautifulSoup(article_resp.text, "html.parser")
                body = (
                    article_soup.select_one("div.td-post-content") or
                    article_soup.select_one(".entry-content, .post-content, .article-content, .single-content")
                )
                html = str(body) if body else ""
                if not html:
                    parts = [p.get_text(strip=True) for p in article_soup.find_all('p') if len(p.get_text(strip=True)) > 40]
                    html = "\n\n".join(f"<p>{t}</p>" for t in parts[:12])
                if not html:
                    continue
                articles.append({
                    "title": title,
                    "url": link,
                    "html": html,
                    "image_url": None
                })
                if len(articles) >= max_articles:
                    break
            except Exception:
                continue
    except Exception:
        pass
    return articles

def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_theanchor(max_articles=max_articles)
    
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