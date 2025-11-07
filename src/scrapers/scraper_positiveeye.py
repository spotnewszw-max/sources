from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Positive Eye News scraper
"""

import requests
from bs4 import BeautifulSoup

def scrape_positiveeye(max_articles=10):
    """Scrape Positive Eye News"""
    articles = []
    url = "http://positiveeyenews.co.zw"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Try multiple selectors
        article_links = soup.select("h2.entry-title a") or soup.select("h3.entry-title a") or soup.select("a.entry-link")
        
        for link_elem in article_links[:max_articles]:
            try:
                link = link_elem.get("href")
                if not link:
                    continue
                
                title = link_elem.get_text(strip=True)
                if not title:
                    continue
                
                articles.append({
                    "title": title,
                    "url": link,
                    "content": title,
                    "source": "Positive Eye News"
                })
            except Exception as e:
                continue
        
        return articles
    except Exception as e:
        return articles

if __name__ == "__main__":
    articles = scrape_positiveeye(max_articles=5)
    print(f"Found {len(articles)} articles")
    for article in articles:
        print(f"  - {article['title'][:60]}")