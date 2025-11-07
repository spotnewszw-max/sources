from .base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup

def scrape_openparly():
    url = "https://openparly.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    # Scrape from the LATEST NEWS carousel
    for post in soup.select('.block-list-small-2 .p-wrap'):
        title_tag = post.select_one('.entry-title a')
        img_tag = post.select_one('.p-featured img')
        date_tag = post.select_one('.meta-date time')
        if title_tag:
            articles.append({
                "title": title_tag.get_text(strip=True),
                "url": title_tag.get("href"),
                "image": img_tag.get("src") if img_tag else None,
                "date": date_tag.get_text(strip=True) if date_tag else None
            })

    # Scrape from TRENDING section
    for post in soup.select('.block-list-small-1 .p-wrap'):
        title_tag = post.select_one('.entry-title a')
        date_tag = post.select_one('.meta-date time')
        if title_tag:
            articles.append({
                "title": title_tag.get_text(strip=True),
                "url": title_tag.get("href"),
                "image": None,
                "date": date_tag.get_text(strip=True) if date_tag else None
            })

    # Scrape from More News grid
    for post in soup.select('.block-grid-small-1 .p-wrap'):
        title_tag = post.select_one('.entry-title a')
        img_tag = post.select_one('.p-featured img')
        if title_tag:
            articles.append({
                "title": title_tag.get_text(strip=True),
                "url": title_tag.get("href"),
                "image": img_tag.get("src") if img_tag else None,
                "date": None
            })

    return articles

def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_openparly(max_articles=max_articles)
    
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


if __name__ == "__main__":
    for article in scrape_openparly():
        print(article)