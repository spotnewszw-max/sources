import logging
import time
import json
import os
from datetime import datetime
from typing import List, Dict
import schedule
import argparse
import hashlib

from scrapers.scraper_herald import scrape_herald
from scrapers.scraper_newzimbabwe import scrape_newzimbabwe
from scrapers.scraper_newsday import scrape_newsday
from scrapers.scraper_newsday_com import scrape_newsday_com
from scrapers.scraper_herald_com import scrape_herald_com
from scrapers.scraper_bbc import scrape_bbc
from poster import WordPressPoster, test_wordpress_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ArticleStorage:
    """Simple JSON storage for scraped articles"""
    
    def __init__(self, storage_file='scraped_articles.json'):
        self.storage_file = storage_file
        self.articles = self.load_articles()
    
    def load_articles(self):
        """Load existing articles from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading articles: {e}")
                return []
        return []
    
    def save_articles(self):
        """Save articles to file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.articles, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving articles: {e}")
            return False
    
    def add_article(self, article):
        """Add article if not duplicate"""
        # Create hash for duplicate detection
        content_hash = hashlib.md5(
            (article.get('title', '') + article.get('content', '')).encode()
        ).hexdigest()
        
        # Check for duplicates
        for existing in self.articles:
            if existing.get('content_hash') == content_hash:
                logger.info(f"Duplicate article skipped: {article.get('title', 'No title')[:50]}")
                return False
        
        # Add metadata
        article['content_hash'] = content_hash
        article['scraped_date'] = datetime.now().isoformat()
        
        self.articles.append(article)
        logger.info(f"Stored article: {article.get('title', 'No title')[:50]}")
        return True
    
    def get_stats(self):
        """Get storage statistics"""
        sources = {}
        for article in self.articles:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'total': len(self.articles),
            'sources': sources,
            'latest': self.articles[-1].get('scraped_date') if self.articles else None
        }

class NewsBot:
    def __init__(self, store_only=False):
        self.store_only = store_only
        self.storage = ArticleStorage() if store_only else None
        self.poster = None if store_only else WordPressPoster()
        
        self.scrapers = {
            'herald': scrape_herald,
            'newzimbabwe': scrape_newzimbabwe, 
            'newsday': scrape_newsday,
            'newsday_com': scrape_newsday_com,
            'herald_com': scrape_herald_com,
            'bbc': scrape_bbc
        }
        
        if store_only:
            logger.info("Bot initialized in STORE-ONLY mode (no WordPress posting)")
        else:
            logger.info("Bot initialized in normal mode (scrape and post)")
        
    def validate_article(self, article: Dict) -> bool:
        """Validate article data before posting/storing"""
        required_fields = ['title', 'content']
        
        for field in required_fields:
            if not article.get(field):
                logger.warning(f"Article missing required field: {field}")
                return False
        
        # Check minimum content length
        if len(article['content']) < 50:
            logger.warning(f"Article content too short: {article['title']}")
            return False
            
        return True
    
    def enhance_article(self, article: Dict, source: str) -> Dict:
        """Enhance article with additional metadata"""
        enhanced = article.copy()
        
        # Add source information
        enhanced['source'] = source  # Always add source
        
        if 'category' not in enhanced:
            enhanced['category'] = self.get_category_from_source(source)
        
        # Add tags based on content analysis
        if 'tags' not in enhanced:
            enhanced['tags'] = self.extract_tags_from_content(article.get('content', ''), source)
        
        # Add excerpt if not present
        if 'excerpt' not in enhanced and 'content' in enhanced:
            # Create excerpt from content (clean HTML first)
            import re
            clean_content = re.sub(r'<[^>]+>', '', enhanced['content'])
            enhanced['excerpt'] = clean_content[:200] + '...' if len(clean_content) > 200 else clean_content
        
        # Add source attribution to content if not already present (only for posting)
        if not self.store_only and f"Source: {source.title()}" not in enhanced['content']:
            enhanced['content'] += f"\n\n<p><em>Source: {source.title()}</em></p>"
        
        return enhanced
    
    def get_category_from_source(self, source: str) -> str:
        """Map source to appropriate category"""
        category_mapping = {
            'herald': 'National News',
            'newzimbabwe': 'Politics',
            'newsday': 'Local News',
            'newsday_com': 'General News',
            'herald_com': 'National News',
            'bbc': 'International News'
        }
        return category_mapping.get(source, 'News')
    
    def extract_tags_from_content(self, content: str, source: str) -> List[str]:
        """Extract relevant tags from content"""
        keywords = []
        content_lower = content.lower()
        
        # Source-specific keywords
        if source == 'bbc':
            # International keywords for BBC content
            international_keywords = [
                'africa', 'southern africa', 'sadc', 'african union', 'world',
                'international', 'global', 'trade', 'diplomacy', 'united nations',
                'brexit', 'europe', 'asia', 'middle east', 'america'
            ]
            keywords.extend([kw.title() for kw in international_keywords if kw in content_lower])
        else:
            # Zimbabwe-specific keywords for local sources
            zimbabwe_keywords = [
                'zimbabwe', 'harare', 'bulawayo', 'zanu-pf', 'mdc', 'parliament',
                'government', 'president', 'minister', 'council', 'economy',
                'election', 'politics', 'development', 'infrastructure', 'mining',
                'agriculture', 'education', 'health'
            ]
            keywords.extend([kw.title() for kw in zimbabwe_keywords if kw in content_lower])
        
        # General news keywords
        general_keywords = [
            'breaking', 'urgent', 'update', 'report', 'statement', 'announcement',
            'crisis', 'emergency', 'meeting', 'conference', 'summit'
        ]
        keywords.extend([kw.title() for kw in general_keywords if kw in content_lower])
        
        # Remove duplicates and limit to 5 tags
        keywords = list(set(keywords))[:5]
        
        return keywords
    
    def scrape_single_source(self, source_name: str) -> List[Dict]:
        """Scrape articles from a single source with better error handling"""
        try:
            logger.info(f"Scraping {source_name}...")
            scraper_func = self.scrapers.get(source_name)
            
            if not scraper_func:
                logger.error(f"No scraper found for: {source_name}")
                return []
            
            articles = scraper_func()
            
            if articles is None:
                articles = []
            
            logger.info(f"Scraped {len(articles)} articles from {source_name}")
            
            # Validate each article
            valid_articles = []
            for article in articles:
                if self.validate_article(article):
                    valid_articles.append(article)
                else:
                    logger.warning(f"Invalid article from {source_name}: {article.get('title', 'No title')[:50]}...")
            
            logger.info(f"Validated {len(valid_articles)} articles from {source_name}")
            return valid_articles
            
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {e}")
            return []
    
    def scrape_all_sources(self) -> Dict[str, List[Dict]]:
        """Scrape articles from all sources"""
        all_articles = {}
        
        for source_name in self.scrapers.keys():
            articles = self.scrape_single_source(source_name)
            if articles:
                all_articles[source_name] = articles
        
        return all_articles
    
    def process_articles(self, articles_by_source: Dict[str, List[Dict]]) -> Dict:
        """Process articles - either store or post based on mode"""
        stats = {
            'total_scraped': 0,
            'total_processed': 0,
            'total_failed': 0,
            'by_source': {}
        }
        
        for source, articles in articles_by_source.items():
            logger.info(f"Processing {len(articles)} articles from {source}")
            
            processed = 0
            failed = 0
            
            for i, article in enumerate(articles, 1):
                stats['total_scraped'] += 1
                
                try:
                    # Validate article
                    if not self.validate_article(article):
                        failed += 1
                        continue
                    
                    # Enhance article
                    enhanced_article = self.enhance_article(article, source)
                    
                    if self.store_only:
                        # Store mode
                        if self.storage.add_article(enhanced_article):
                            processed += 1
                            stats['total_processed'] += 1
                        else:
                            failed += 1
                            stats['total_failed'] += 1
                    else:
                        # Post mode
                        logger.info(f"Posting article {i}/{len(articles)}: {enhanced_article['title'][:50]}...")
                        
                        if self.poster.post_to_wordpress(**enhanced_article):
                            processed += 1
                            stats['total_processed'] += 1
                            logger.info(f"Successfully posted: {enhanced_article['title'][:50]}...")
                        else:
                            failed += 1
                            stats['total_failed'] += 1
                            logger.error(f"Failed to post: {enhanced_article['title'][:50]}...")
                        
                        # Rate limiting for posting
                        time.sleep(3)
                    
                except Exception as e:
                    logger.error(f"Error processing article from {source}: {e}")
                    failed += 1
                    stats['total_failed'] += 1
            
            stats['by_source'][source] = {
                'scraped': len(articles),
                'processed': processed,
                'failed': failed
            }
            
            action = "stored" if self.store_only else "posted"
            logger.info(f"Completed {source}: {processed} {action}, {failed} failed")
        
        # Save articles if in store mode
        if self.store_only:
            self.storage.save_articles()
            logger.info(f"Saved articles to {self.storage.storage_file}")
        
        return stats
    
    def run_full_cycle(self) -> Dict:
        """Run complete scraping cycle"""
        mode_text = "STORE-ONLY" if self.store_only else "SCRAPE & POST"
        
        logger.info("=" * 50)
        logger.info(f"Starting news bot cycle ({mode_text}) at {datetime.now()}")
        logger.info("=" * 50)
        
        # Test WordPress connection only if posting
        if not self.store_only:
            if not self.poster.test_connection():
                logger.error("WordPress connection failed. Aborting cycle.")
                return {'error': 'WordPress connection failed'}
        
        # Scrape all sources
        articles_by_source = self.scrape_all_sources()
        
        if not articles_by_source:
            logger.warning("No articles scraped from any source")
            return {'error': 'No articles scraped'}
        
        # Process articles
        stats = self.process_articles(articles_by_source)
        
        # Log final statistics
        logger.info("=" * 50)
        logger.info(f"CYCLE SUMMARY ({mode_text}):")
        logger.info(f"Total articles scraped: {stats['total_scraped']}")
        
        if self.store_only:
            logger.info(f"Total articles stored: {stats['total_processed']}")
            storage_stats = self.storage.get_stats()
            logger.info(f"Total in storage: {storage_stats['total']}")
        else:
            logger.info(f"Total articles posted: {stats['total_processed']}")
        
        logger.info(f"Total failures: {stats['total_failed']}")
        logger.info("By source:")
        for source, source_stats in stats['by_source'].items():
            action = "stored" if self.store_only else "posted"
            logger.info(f"  {source}: {source_stats['processed']}/{source_stats['scraped']} {action}")
        logger.info("=" * 50)
        
        return stats

def main():
    parser = argparse.ArgumentParser(description='AllZimNews Scraping Bot')
    parser.add_argument('--mode', choices=['once', 'store-only', 'schedule', 'test'], 
                       default='once', help='Run mode')
    parser.add_argument('--source', choices=['herald', 'newzimbabwe', 'newsday', 
                       'newsday_com', 'herald_com', 'bbc'],
                       help='Scrape single source')
    parser.add_argument('--storage-file', default='scraped_articles.json',
                       help='Storage file for store-only mode')
    
    args = parser.parse_args()
    
    # Determine if store-only mode
    store_only = args.mode == 'store-only'
    
    bot = NewsBot(store_only=store_only)
    
    if args.mode == 'test':
        logger.info("Testing scrapers...")
        
        # Test each scraper
        for source_name in bot.scrapers.keys():
            logger.info(f"Testing {source_name} scraper...")
            try:
                articles = bot.scrape_single_source(source_name)
                if articles:
                    logger.info(f"✅ {source_name} scraper working: {len(articles)} articles found")
                    logger.info(f"Sample article: {articles[0]['title'][:50]}...")
                else:
                    logger.warning(f"⚠️ {source_name} scraper returned no articles")
            except Exception as e:
                logger.error(f"❌ {source_name} scraper failed: {e}")
                
        # Test WordPress connection only if not store-only
        if not store_only:
            logger.info("Testing WordPress connection...")
            if test_wordpress_connection():
                logger.info("✅ WordPress connection working!")
            else:
                logger.error("❌ WordPress connection test failed!")
            
    elif args.mode in ['once', 'store-only']:
        if args.source:
            # Scrape single source
            articles = bot.scrape_single_source(args.source)
            if articles:
                articles_by_source = {args.source: articles}
                bot.process_articles(articles_by_source)
        else:
            # Run full cycle
            bot.run_full_cycle()
    
    elif args.mode == 'schedule':
        logger.info("Starting scheduled mode...")
        mode_text = "store-only" if store_only else "scrape and post"
        logger.info(f"Bot will run in {mode_text} mode every 2 hours")
        
        # Schedule the job
        def run_scheduled_job():
            bot.run_full_cycle()
            
        schedule.every(2).hours.do(run_scheduled_job)
        
        # Run once immediately
        run_scheduled_job()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()