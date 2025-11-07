from .base_scraper import BaseScraper
import requests
import cloudscraper
from bs4 import BeautifulSoup
from typing import List, Dict

def scrape_africahotspot(max_articles=10):
    articles = []
    url = "https://africahotspot.co.zw"
    
    # Use cloudscraper instead of requests for better anti-bot bypass
    try:
        scraper = cloudscraper.create_scraper()
        scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        resp = scraper.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        candidates = soup.select("h2.entry-title a, .entry-title a, article h2 a, .jeg_post_title a")
        for a in candidates[:max_articles * 3]:
            link = a.get("href")
            title = a.get_text(strip=True)
            if not link or not title or len(title) < 8:
                continue
            try:
                article_resp = scraper.get(link, timeout=15)
                article_resp.raise_for_status()
                article_soup = BeautifulSoup(article_resp.text, "html.parser")
                body = (
                    article_soup.select_one("div.td-post-content") or
                    article_soup.select_one(".entry-content, .post-content, .article-content, .single-content")
                )
                # Standardize keys to integrate with bot: title, content/html+url
                html = str(body) if body else ""
                if not html:
                    # Fallback: combine paragraphs
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

def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    return scrape_africahotspot(max_articles=max_articles)

def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_africahotspot(max_articles=max_articles)
    
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