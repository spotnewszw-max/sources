from .base_scraper import BaseScraper
#!/usr/bin/env python3
"""
Veritas Zimbabwe scraper
"""

import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_veritaszim(max_articles=10):
    """Scrape Veritas Zimbabwe"""
    articles = []
    urls = [
        "https://www.veritaszim.net/",
        "https://veritaszim.net/",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in urls:
        try:
            time.sleep(random.uniform(1, 2))
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try primary selector first
            latest_posts_block = soup.find("section", id="block-views-latest-posts-block")
            if latest_posts_block:
                for row in latest_posts_block.select(".views-row"):
                    try:
                        link = row.select_one(".views-field-title a")
                        if link:
                            title = link.get_text(strip=True)
                            href = link.get("href")
                            if title and href:
                                article_url = href if href.startswith('http') else ("https://www.veritaszim.net" + href)
                                articles.append({
                                    "title": title,
                                    "url": article_url,
                                    "content": title,
                                    "source": "Veritas Zimbabwe"
                                })
                                if len(articles) >= max_articles:
                                    return articles
                    except:
                        continue
            
            # Fallback to generic extraction if primary selector fails
            if not articles:
                article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and 'post' in str(x).lower())
                for element in article_elements[:max_articles]:
                    try:
                        title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                        title = title_elem.get_text(strip=True) if title_elem else None
                        if not title:
                            continue
                        
                        link_elem = element.find('a', href=True)
                        article_url = link_elem['href'] if link_elem else None
                        if not article_url:
                            continue
                        
                        if not article_url.startswith('http'):
                            article_url = url.rstrip('/') + '/' + article_url.lstrip('/')
                        
                        articles.append({
                            "title": title,
                            "url": article_url,
                            "content": title,
                            "source": "Veritas Zimbabwe"
                        })
                    except:
                        continue
            
            if articles:
                break
        except Exception as e:
            continue
    
    return articles

if __name__ == "__main__":
    articles = scrape_veritaszim(max_articles=5)
    print(f"Found {len(articles)} articles")
    for article in articles:
        print(f"  - {article['title'][:60]}")