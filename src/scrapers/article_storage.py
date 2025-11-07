import json
import os
from datetime import datetime
from typing import List, Dict
import hashlib
import sqlite3

class ArticleStorage:
    """Store scraped articles without posting to WordPress"""
    
    def __init__(self, storage_type='json', db_path='articles.db', json_path='articles.json'):
        self.storage_type = storage_type
        self.db_path = db_path
        self.json_path = json_path
        
        if storage_type == 'sqlite':
            self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                url TEXT,
                image_url TEXT,
                category TEXT,
                tags TEXT,
                scraped_date TEXT,
                content_hash TEXT UNIQUE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_article(self, article: Dict) -> bool:
        """Store a single article"""
        # Create content hash to avoid duplicates
        content_hash = hashlib.md5(
            (article.get('title', '') + article.get('content', '')).encode()
        ).hexdigest()
        
        article['content_hash'] = content_hash
        article['scraped_date'] = datetime.now().isoformat()
        
        if self.storage_type == 'json':
            return self._store_to_json(article)
        elif self.storage_type == 'sqlite':
            return self._store_to_sqlite(article)
        else:
            print(f"Unsupported storage type: {self.storage_type}")
            return False
    
    def _store_to_json(self, article: Dict) -> bool:
        """Store article to JSON file"""
        try:
            # Load existing articles
            articles = []
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
            
            # Check for duplicates
            existing_hashes = {a.get('content_hash') for a in articles}
            if article['content_hash'] in existing_hashes:
                print(f"Duplicate article skipped: {article.get('title', 'Unknown')}")
                return False
            
            # Add new article
            articles.append(article)
            
            # Save back to file
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Stored to JSON: {article.get('title', 'Unknown')}")
            return True
            
        except Exception as e:
            print(f"Error storing to JSON: {e}")
            return False
    
    def _store_to_sqlite(self, article: Dict) -> bool:
        """Store article to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert tags list to string
            tags_str = json.dumps(article.get('tags', [])) if article.get('tags') else ''
            
            cursor.execute('''
                INSERT OR IGNORE INTO articles 
                (title, content, source, url, image_url, category, tags, scraped_date, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.get('title', ''),
                article.get('content', ''),
                article.get('source', ''),
                article.get('url', ''),
                article.get('image_url', ''),
                article.get('category', ''),
                tags_str,
                article['scraped_date'],
                article['content_hash']
            ))
            
            if cursor.rowcount > 0:
                print(f"✓ Stored to DB: {article.get('title', 'Unknown')}")
                success = True
            else:
                print(f"Duplicate article skipped: {article.get('title', 'Unknown')}")
                success = False
            
            conn.commit()
            conn.close()
            return success
            
        except Exception as e:
            print(f"Error storing to database: {e}")
            return False
    
    def get_stored_articles(self, limit: int = None) -> List[Dict]:
        """Retrieve stored articles"""
        if self.storage_type == 'json':
            return self._get_from_json(limit)
        elif self.storage_type == 'sqlite':
            return self._get_from_sqlite(limit)
        else:
            return []
    
    def _get_from_json(self, limit: int = None) -> List[Dict]:
        """Get articles from JSON file"""
        try:
            if not os.path.exists(self.json_path):
                return []
            
            with open(self.json_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            if limit:
                return articles[-limit:]  # Get most recent
            return articles
            
        except Exception as e:
            print(f"Error reading from JSON: {e}")
            return []
    
    def _get_from_sqlite(self, limit: int = None) -> List[Dict]:
        """Get articles from SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM articles ORDER BY scraped_date DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Convert to dictionaries
            columns = [desc[0] for desc in cursor.description]
            articles = []
            for row in rows:
                article = dict(zip(columns, row))
                # Convert tags back to list
                if article.get('tags'):
                    try:
                        article['tags'] = json.loads(article['tags'])
                    except:
                        article['tags'] = []
                articles.append(article)
            
            conn.close()
            return articles
            
        except Exception as e:
            print(f"Error reading from database: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        articles = self.get_stored_articles()
        
        if not articles:
            return {"total": 0, "sources": {}, "latest": None}
        
        # Count by source
        sources = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total": len(articles),
            "sources": sources,
            "latest": articles[0].get('scraped_date') if articles else None
        }


# Usage example for scrape-only mode
def scrape_and_store_only(scrapers, storage_type='json'):
    """
    Example function to scrape articles and store them without posting
    
    Args:
        scrapers: List of scraper instances
        storage_type: 'json' or 'sqlite'
    """
    storage = ArticleStorage(storage_type=storage_type)
    
    total_stored = 0
    
    for scraper in scrapers:
        print(f"\n🔍 Scraping {scraper.name}...")
        
        try:
            articles = scraper.scrape()  # Assuming each scraper has a scrape() method
            
            for article in articles:
                if storage.store_article(article):
                    total_stored += 1
                    
        except Exception as e:
            print(f"Error scraping {scraper.name}: {e}")
            continue
    
    # Print summary
    stats = storage.get_stats()
    print(f"\n📊 Scraping Summary:")
    print(f"Total articles stored: {total_stored}")
    print(f"Total in storage: {stats['total']}")
    print(f"Sources: {stats['sources']}")
    
    return stats

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Article Storage System')
    parser.add_argument('--storage', choices=['json', 'sqlite'], default='json',
                       help='Storage type (default: json)')
    parser.add_argument('--stats', action='store_true',
                       help='Show storage statistics')
    parser.add_argument('--list', type=int, metavar='N',
                       help='List last N articles')
    
    args = parser.parse_args()
    
    storage = ArticleStorage(storage_type=args.storage)
    
    if args.stats:
        stats = storage.get_stats()
        print(f"Storage Statistics:")
        print(f"Total articles: {stats['total']}")
        print(f"Sources: {json.dumps(stats['sources'], indent=2)}")
        print(f"Latest: {stats['latest']}")
    
    if args.list:
        articles = storage.get_stored_articles(args.list)
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.get('title', 'No title')}")
            print(f"   Source: {article.get('source', 'Unknown')}")
            print(f"   Date: {article.get('scraped_date', 'Unknown')}")
            print(f"   URL: {article.get('url', 'No URL')}")
