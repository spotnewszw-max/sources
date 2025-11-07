# enhanced_scrapers_fixed.py
"""
Fixed version of enhanced scrapers with improved link extraction
"""

# Import all the original enhanced scraper code
import sys
import os

# Add the original enhanced_scrapers code here or import it
try:
    from enhanced_scrapers import *
except ImportError:
    print("❌ Please ensure enhanced_scrapers.py is in the same directory")
    sys.exit(1)

# Import our fixes
from scraper_fixes import fix_newsday_link_extraction, fix_newshawks_link_extraction, fix_image_extraction

# Override the problematic function
def _extract_article_links_enhanced_fixed(soup: BeautifulSoup, base_url: str, domain: str) -> List[Dict]:
    """Fixed article link extraction with site-specific strategies"""
    
    print(f"🔧 Using FIXED link extraction for {domain}")
    
    if 'newsday.co.zw' in domain:
        return fix_newsday_link_extraction(soup, base_url)
    elif 'thenewshawks.com' in domain:
        return fix_newshawks_link_extraction(soup, base_url)
    else:
        # Use original method for other sites
        return _extract_article_links_enhanced(soup, base_url, domain)


def _extract_featured_image_enhanced_fixed(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Fixed image extraction"""
    return fix_image_extraction(soup, base_url)


# Fixed scrapers
def scrape_newsday_fixed() -> List[Dict]:
    """Fixed NewsDay scraper"""
    scraper = EnhancedScraper()
    articles = []
    
    listing_urls = [
        "https://newsday.co.zw/local-news/",
        "https://www.newsday.co.zw/local-news/",
        "https://newsday.co.zw/news/",
        "https://www.newsday.co.zw/news/",
        "https://newsday.co.zw/",
        "https://www.newsday.co.zw/",
    ]
    
    processed_links = set()
    
    try:
        for base_url in listing_urls:
            try:
                logger.info(f"🔧 FIXED: Scraping NewsDay listing: {base_url}")
                content = scraper.get_content(base_url)
                if not content:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Use FIXED link extraction
                article_links = _extract_article_links_enhanced_fixed(soup, base_url, 'newsday.co.zw')
                
                if not article_links:
                    logger.warning(f"No articles found on {base_url}")
                    continue
                
                for link_data in article_links:
                    if len(articles) >= 15:
                        break
                        
                    url = link_data['url']
                    title = link_data['title']
                    
                    if url in processed_links:
                        continue
                    processed_links.add(url)
                    
                    # Get full article content
                    article_content = scraper.get_content(url)
                    if not article_content:
                        logger.warning(f"Failed to get content for: {title[:50]}...")
                        continue
                    
                    article_soup = BeautifulSoup(article_content, 'html.parser')
                    
                    # Enhanced content extraction with fixed image extraction
                    content_data = _extract_article_content_enhanced(article_soup, url, 'NewsDay')
                    
                    # Use fixed image extraction
                    if not content_data.get('image_url'):
                        content_data['image_url'] = _extract_featured_image_enhanced_fixed(article_soup, url)
                    
                    if content_data and content_data['content']:
                        article = {
                            'title': title,
                            'content': content_data['content'],
                            'source': 'NewsDay',
                            'source_url': url,
                            'link': url
                        }
                        
                        if content_data.get('image_url'):
                            article['image_url'] = content_data['image_url']
                        
                        if content_data.get('published'):
                            article.setdefault('meta', {})
                            article['meta']['published'] = content_data['published']
                        
                        articles.append(article)
                        logger.info(f"✅ Successfully scraped: {title[:50]}...")
                    
                    # Rate limiting
                    time.sleep(random.uniform(2, 5))
                
                # Break if we got articles from this URL
                if articles:
                    break
                
            except Exception as e:
                logger.warning(f"Error processing {base_url}: {e}")
                continue
                
    finally:
        scraper.close()
    
    logger.info(f"🔧 FIXED NewsDay: Successfully scraped {len(articles)} articles")
    return articles


def scrape_newshawks_fixed() -> List[Dict]:
    """Fixed NewsHawks scraper"""
    scraper = EnhancedScraper()
    articles = []
    
    listing_urls = [
        "https://thenewshawks.com/",
        "https://www.thenewshawks.com/",
        "https://thenewshawks.com/category/news/",
        "https://www.thenewshawks.com/category/news/",
        "https://thenewshawks.com/category/business/",
        "https://thenewshawks.com/category/politics/",
    ]
    
    processed_links = set()
    
    try:
        for base_url in listing_urls:
            try:
                logger.info(f"🔧 FIXED: Scraping NewsHawks listing: {base_url}")
                content = scraper.get_content(base_url)
                if not content:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Use FIXED link extraction
                article_links = _extract_article_links_enhanced_fixed(soup, base_url, 'thenewshawks.com')
                
                if not article_links:
                    logger.warning(f"No articles found on {base_url}")
                    continue
                
                for link_data in article_links:
                    if len(articles) >= 15:
                        break
                        
                    url = link_data['url']
                    title = link_data['title']
                    
                    if url in processed_links:
                        continue
                    processed_links.add(url)
                    
                    # Get full article content
                    article_content = scraper.get_content(url)
                    if not article_content:
                        logger.warning(f"Failed to get content for: {title[:50]}...")
                        continue
                    
                    article_soup = BeautifulSoup(article_content, 'html.parser')
                    
                    # Enhanced content extraction with fixed image extraction
                    content_data = _extract_article_content_enhanced(article_soup, url, 'The NewsHawks')
                    
                    # Use fixed image extraction
                    if not content_data.get('image_url'):
                        content_data['image_url'] = _extract_featured_image_enhanced_fixed(article_soup, url)
                    
                    if content_data and content_data['content']:
                        article = {
                            'title': title,
                            'content': content_data['content'],
                            'source': 'The NewsHawks',
                            'source_url': url,
                            'link': url
                        }
                        
                        if content_data.get('image_url'):
                            article['image_url'] = content_data['image_url']
                        
                        if content_data.get('published'):
                            article.setdefault('meta', {})
                            article['meta']['published'] = content_data['published']
                        
                        articles.append(article)
                        logger.info(f"✅ Successfully scraped: {title[:50]}...")
                    
                    # Rate limiting
                    time.sleep(random.uniform(2, 5))
                
                # Break if we got articles from this URL
                if articles:
                    break
                
            except Exception as e:
                logger.warning(f"Error processing {base_url}: {e}")
                continue
                
    finally:
        scraper.close()
    
    logger.info(f"🔧 FIXED NewsHawks: Successfully scraped {len(articles)} articles")
    return articles


# Fixed main scraping function
def scrape_all_zimbabwe_news_fixed() -> List[Dict]:
    """Fixed main function to scrape all Zimbabwean news sources"""
    
    print("🚀 Starting FIXED enhanced news scraping...")
    
    # Use fixed scrapers
    all_articles = []
    
    # Scrape each source
    try:
        newsday_articles = scrape_newsday_fixed()
        all_articles.extend(newsday_articles)
        logger.info(f"NewsDay: {len(newsday_articles)} articles")
    except Exception as e:
        logger.error(f"NewsDay failed: {e}")
    
    try:
        newshawks_articles = scrape_newshawks_fixed()
        all_articles.extend(newshawks_articles)
        logger.info(f"NewsHawks: {len(newshawks_articles)} articles")
    except Exception as e:
        logger.error(f"NewsHawks failed: {e}")
    
    try:
        newzimbabwe_articles = scrape_newzimbabwe_enhanced()
        all_articles.extend(newzimbabwe_articles)
        logger.info(f"NewZimbabwe: {len(newzimbabwe_articles)} articles")
    except Exception as e:
        logger.error(f"NewZimbabwe failed: {e}")
    
    # Remove duplicates based on title similarity
    unique_articles = []
    seen_titles = set()
    
    for article in all_articles:
        title_lower = article['title'].lower()
        title_key = title_lower[:50]
        
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_articles.append(article)
    
    logger.info(f"🎯 Total unique articles scraped: {len(unique_articles)}")
    return unique_articles


# Quick test function for the fixes
def test_fixes():
    """Quick test of the fixed scrapers"""
    print("🧪 Testing fixed scrapers...")
    
    # Test NewsDay
    print("\n1. Testing NewsDay fix...")
    try:
        newsday_articles = scrape_newsday_fixed()
        print(f"   ✅ NewsDay: {len(newsday_articles)} articles")
        if newsday_articles:
            print(f"   Sample: {newsday_articles[0]['title'][:60]}...")
    except Exception as e:
        print(f"   ❌ NewsDay failed: {e}")
    
    # Test NewsHawks
    print("\n2. Testing NewsHawks fix...")
    try:
        newshawks_articles = scrape_newshawks_fixed()
        print(f"   ✅ NewsHawks: {len(newshawks_articles)} articles")
        if newshawks_articles:
            print(f"   Sample: {newshawks_articles[0]['title'][:60]}...")
    except Exception as e:
        print(f"   ❌ NewsHawks failed: {e}")
    
    print("\n✅ Fix testing complete!")


if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run the fixed scrapers
    articles = scrape_all_zimbabwe_news_fixed()
    
    print(f"\n🎉 Successfully scraped {len(articles)} articles with FIXES!")
    
    # Display sample results
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   URL: {article['source_url']}")
        print(f"   Content length: {len(article.get('content', ''))}")
        print(f"   Has image: {'Yes' if article.get('image_url') else 'No'}")
        if article.get('image_url'):
            print(f"   Image URL: {article['image_url'][:80]}...")
        print("-" * 80)
