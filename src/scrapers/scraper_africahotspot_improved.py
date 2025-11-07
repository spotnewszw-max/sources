from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Africa Hotspot scraper (improved version)
"""

import requests
from bs4 import BeautifulSoup
import cloudscraper
import time
import random

def scrape_africahotspot_improved(max_articles=10):
    """Scrape Africa Hotspot with CloudScraper"""
    articles = []
    
    try:
        # Use cloudscraper to bypass anti-bot
        scraper = cloudscraper.create_scraper()
        
        url = "https://africahotspot.co.zw/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        time.sleep(random.uniform(1, 2))
        response = scraper.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Generic article extraction
        article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and any(cls in str(x).lower() for cls in ['post', 'entry', 'item', 'article']))
        
        for element in article_elements[:max_articles]:
            try:
                title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                title = title_elem.get_text(strip=True) if title_elem else None
                
                if not title or len(title) < 3:
                    continue
                
                link_elem = element.find('a', href=True)
                article_url = link_elem['href'] if link_elem else None
                
                if not article_url:
                    continue
                
                articles.append({
                    "title": title,
                    "url": article_url,
                    "content": title,
                    "source": "Africa Hotspot"
                })
            except:
                continue
        
        return articles
    except Exception as e:
        return articles

if __name__ == "__main__":
    articles = scrape_africahotspot_improved(max_articles=5)
    print(f"Found {len(articles)} articles")