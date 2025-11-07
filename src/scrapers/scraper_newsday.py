from .base_scraper import BaseScraper
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import time
import random

# Use shared crawler and helpers
from src.scrapers.base_scraper import (
    crawler, logger,
    extract_content_paragraphs, extract_published_date, extract_featured_image,
    render_paragraphs_html, build_source_attribution, extract_article_metadata
)
# Import image extraction utilities
from src.utils.image_utils import extract_all_images_from_content, extract_featured_image as extract_featured_img

def clean_article_html(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove bylines, share buttons, ads, and other non-article elements."""
    selectors = [
        ".byline", ".author", ".posted-by", ".post-meta", ".entry-meta",
        ".share", ".social", ".td-post-sharing", ".td_block_social_counter",
        ".td-post-author-name", ".td-author-by", ".td-post-date", ".td-post-views",
        ".td-post-comments", ".td-post-source-tags", ".td_block_related_posts",
        ".related-posts", ".advertisement", ".ad", ".adsbygoogle", ".promo", ".wp-block-button",
        "#jp-post-flair", "#sharing", "#share-buttons", "#social-share", "#author-info"
    ]
    for sel in selectors:
        for tag in soup.select(sel):
            tag.decompose()
    return soup

def scrape_newsday(max_articles=10) -> List[Dict]:
    """Scrape NewsDay (newsday.co.zw) for latest articles with robust fallbacks."""
    articles = []
    start_urls = [
        "https://www.newsday.co.zw/category/16/local-news",
        "https://www.newsday.co.zw/category/10/news",
        "https://www.newsday.co.zw/category/4/business",
        "https://www.newsday.co.zw/category/5/sport",
        "https://www.newsday.co.zw/category/8/life-amp-style",
        "https://www.newsday.co.zw/category/9/opinion-analysis",
        "https://www.newsday.co.zw/",
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    seen = set()

    logger.info("Scraping NewsDay with multiple fallbacks")

    try:
        for url in start_urls:
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                link_selectors = [
                    "a.text-dark[href*='/article/']",
                    "a.text-dark[href*='/local-news/article/']",
                    "a.text-dark[href*='/business/article/']",
                    "a.text-dark[href*='/sport/article/']",
                    "a.text-dark[href*='/life-amp-style/article/']",
                    "a.text-dark[href*='/opinion-analysis/article/']",
                    "a.text-dark[href*='/letters/article/']",
                    "a.text-dark[href*='/editorials/article/']",
                    "a.text-dark[href*='/uncategorized/article/']",
                    "h3 a[href*='/article/']",
                    "h2 a[href*='/article/']",
                ]
                link_elems = []
                for sel in link_selectors:
                    elems = soup.select(sel)
                    if elems:
                        link_elems.extend(elems)
                for a in link_elems:
                    if len(articles) >= max_articles:
                        break
                    href = a.get("href")
                    if not href or href in seen:
                        continue
                    seen.add(href)
                    title = a.get_text(strip=True)
                    if not title or len(title) < 8:
                        continue
                    article_url = urljoin(url, href)
                    time.sleep(random.uniform(0.5, 1.2))
                    ar = requests.get(article_url, headers=headers, timeout=15)
                    if ar.status_code != 200 or not ar.text:
                        continue
                    art_soup = BeautifulSoup(ar.text, "html.parser")
                    
                    all_images = extract_all_images_from_content(art_soup, article_url, min_width=150, min_height=100)
                    logger.info(f"Extracted {len(all_images)} images from {article_url}")
                    
                    art_soup = clean_article_html(art_soup)
                    
                    content_div = art_soup.find("div", class_="article-content") or \
                                  art_soup.find("div", class_="entry-content") or \
                                  art_soup.find("div", class_="contents") or \
                                  art_soup.find("div", class_="card-body") or \
                                  art_soup.find("section", class_="section-phase") or \
                                  art_soup.find("div", class_="post-content") or \
                                  art_soup.find("article")
                    
                    if content_div:
                        paragraphs = [p.get_text(strip=True) for p in content_div.find_all("p") if len(p.get_text(strip=True)) > 20]
                    else:
                        paragraphs = [p.get_text(strip=True) for p in art_soup.find_all("p") if len(p.get_text(strip=True)) > 20]
                    
                    if not paragraphs:
                        logger.warning(f"No paragraphs found in {article_url}, skipping")
                        continue
                    
                    body_html = ""
                    images_inserted = 0
                    
                    for i, para in enumerate(paragraphs[:15]):
                        body_html += f"<p>{para}</p>\n\n"
                        
                        if i % 2 == 0 and images_inserted < len(all_images):
                            img_info = all_images[images_inserted]
                            img_html = f'<figure class="wp-block-image size-large">'
                            img_html += f'<img src="{img_info["url"]}" alt="{img_info.get("alt", "")}"'
                            if img_info.get('width'):
                                img_html += f' width="{img_info["width"]}"'
                            if img_info.get('height'):
                                img_html += f' height="{img_info["height"]}"'
                            img_html += ' />'
                            if img_info.get('caption'):
                                img_html += f'<figcaption>{img_info["caption"]}</figcaption>'
                            img_html += '</figure>\n\n'
                            body_html += img_html
                            images_inserted += 1
                    
                    featured_image_url = all_images[0]['url'] if all_images else None
                    if not featured_image_url:
                        img = art_soup.find("img", {"class": "img-fluid"}) or art_soup.find("img", {"class": "style-image"})
                        featured_image_url = img.get("data-src") or img.get("src") if img else None
                    
                    articles.append({
                        "title": title,
                        "content": body_html.strip(),
                        "source_url": article_url,
                        "source": "NewsDay",
                        "image_url": featured_image_url,
                        "images": all_images
                    })
                    if len(articles) >= max_articles:
                        break
                if len(articles) >= max_articles:
                    break
            except Exception as e:
                logger.warning(f"Error processing listing {url}: {e}")
                continue

        logger.info(f"Total NewsDay articles scraped: {len(articles)}")
        return articles

    except Exception as e:
        logger.error(f"NewsDay scraping error: {e}")
        return []


def scrape_webpage(url: str = None, max_articles: int = 10) -> List[Dict]:
    """Wrapper function for compatibility with testing framework"""
    return scrape_newsday(max_articles=max_articles)




def scrape_webpage(url: str = None, max_articles: int = 10):
    """Wrapper function for compatibility with testing framework"""
    from typing import List, Dict
    articles = scrape_newsday(max_articles=max_articles)
    
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
    items = scrape_newsday(8)
    print(f"Found {len(items)} NewsDay articles")
    for i, it in enumerate(items, 1):
        print(i, it["title"][:90])
        print("URL:", it.get("url"))
        print("Image:", it.get("image_url"))
