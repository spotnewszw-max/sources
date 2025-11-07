"""
Unified Analyzer
Consolidates analysis across all content sources:
- RSS feed articles (traditional)
- Scraped news articles (websites)
- Social media posts (influencers)
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger(__name__)


class UnifiedContentAnalyzer:
    """Analyzes content from all sources (RSS, scraped, social media) together"""
    
    def __init__(self):
        pass
    
    def collect_all_articles(self, 
                            rss_articles: List[Dict] = None,
                            scraped_articles: List[Dict] = None,
                            social_posts: List[Dict] = None,
                            topic: str = None,
                            days_back: int = 30) -> List[Dict]:
        """
        Collect and normalize articles from all sources
        
        Args:
            rss_articles: Articles from RSS feeds
            scraped_articles: Articles scraped from websites
            social_posts: Posts from social media
            topic: Optional topic filter
            days_back: Number of days to look back
            
        Returns:
            Unified list of articles with normalized structure
        """
        all_articles = []
        
        # Collect RSS articles
        if rss_articles:
            all_articles.extend([
                self._normalize_rss_article(a, topic, days_back) 
                for a in rss_articles
            ])
        
        # Collect scraped articles
        if scraped_articles:
            all_articles.extend([
                self._normalize_scraped_article(a, topic, days_back)
                for a in scraped_articles
            ])
        
        # Collect social media posts
        if social_posts:
            all_articles.extend([
                self._normalize_social_post(p, topic, days_back)
                for p in social_posts
            ])
        
        # Filter by topic if specified
        if topic:
            all_articles = [a for a in all_articles if a is not None]
        
        # Sort by date (newest first)
        all_articles.sort(
            key=lambda x: x.get('published_date', datetime.now()),
            reverse=True
        )
        
        logger.info(
            f"Collected {len(all_articles)} articles: "
            f"RSS={len(rss_articles or [])}, "
            f"Scraped={len(scraped_articles or [])}, "
            f"Social={len(social_posts or [])}"
        )
        
        return all_articles
    
    def _normalize_rss_article(self, article: Dict, topic: str = None, days_back: int = 30) -> Optional[Dict]:
        """Normalize RSS article to unified format"""
        try:
            # Check date
            if days_back:
                pub_date = article.get('published_date') or article.get('fetched_date')
                if pub_date and isinstance(pub_date, str):
                    # Skip if we can't parse date
                    pass
            
            normalized = {
                'id': article.get('id'),
                'source_type': 'rss',
                'title': article.get('title'),
                'content': article.get('content'),
                'url': article.get('url'),
                'source': article.get('source'),
                'author': article.get('author'),
                'published_date': article.get('published_date') or article.get('fetched_date'),
                'sentiment': article.get('sentiment'),
                'relevance_score': article.get('relevance_score', 0.5),
                'entities': {
                    'politicians': article.get('mentioned_politicians', []),
                    'organizations': article.get('mentioned_organizations', []),
                    'locations': article.get('mentioned_locations', []),
                },
                'keywords': article.get('keywords', []),
                'engagement': None,  # RSS doesn't have engagement
            }
            
            return normalized
            
        except Exception as e:
            logger.debug(f"Error normalizing RSS article: {e}")
            return None
    
    def _normalize_scraped_article(self, article: Dict, topic: str = None, days_back: int = 30) -> Optional[Dict]:
        """Normalize scraped article to unified format"""
        try:
            normalized = {
                'id': article.get('id'),
                'source_type': 'scraped',
                'title': article.get('title'),
                'content': article.get('content'),
                'url': article.get('url'),
                'source': article.get('source_site'),
                'author': article.get('author'),
                'published_date': article.get('published_date') or article.get('scraped_date'),
                'sentiment': article.get('sentiment'),
                'relevance_score': article.get('relevance_score', 0.5),
                'entities': {
                    'politicians': article.get('mentioned_politicians', []),
                    'organizations': article.get('mentioned_organizations', []),
                    'locations': article.get('mentioned_locations', []),
                },
                'keywords': article.get('keywords', []),
                'engagement': None,  # Scraped articles don't have engagement
                'category': article.get('source_category'),
                'extraction_confidence': article.get('extraction_confidence', 0.85),
            }
            
            return normalized
            
        except Exception as e:
            logger.debug(f"Error normalizing scraped article: {e}")
            return None
    
    def _normalize_social_post(self, post: Dict, topic: str = None, days_back: int = 30) -> Optional[Dict]:
        """Normalize social media post to unified format"""
        try:
            normalized = {
                'id': post.get('id'),
                'source_type': 'social_media',
                'title': f"Post by {post.get('author_username', 'Unknown')}",
                'content': post.get('text') or post.get('extracted_text'),
                'url': post.get('platform_post_id'),  # Using post ID as URL
                'source': f"{post.get('platform', 'social').upper()}/{post.get('author_username')}",
                'author': post.get('author_name') or post.get('author_username'),
                'published_date': post.get('posted_date') or post.get('captured_date'),
                'sentiment': post.get('sentiment'),
                'relevance_score': 1.0,  # Social posts are pre-filtered
                'entities': {
                    'politicians': post.get('mentioned_politicians', []),
                    'organizations': post.get('mentioned_topics', []),  # Note: topics in social
                    'locations': [],
                },
                'keywords': post.get('mentioned_topics', []),
                'engagement': post.get('engagement_metrics'),
                'platform': post.get('platform'),
                'follower_count': post.get('author_follower_count'),
            }
            
            return normalized
            
        except Exception as e:
            logger.debug(f"Error normalizing social post: {e}")
            return None
    
    def analyze_unified_trends(self, articles: List[Dict]) -> Dict:
        """
        Analyze trends across all sources
        
        Returns comprehensive trend analysis combining:
        - Topic frequencies
        - Sentiment across sources
        - Entity mentions
        - Source distribution
        """
        if not articles:
            return {}
        
        # Extract all keywords
        all_keywords = []
        for article in articles:
            all_keywords.extend(article.get('keywords', []))
        
        keyword_freq = Counter(all_keywords)
        
        # Analyze sentiment
        sentiment_counts = Counter([a.get('sentiment', 'neutral') for a in articles])
        
        # Source distribution
        source_dist = Counter([a.get('source_type') for a in articles])
        
        # Entity mentions
        all_politicians = []
        for article in articles:
            all_politicians.extend(article.get('entities', {}).get('politicians', []))
        
        politician_freq = Counter(all_politicians)
        
        # Engagement-weighted sentiment (social media engagement matters more)
        weighted_sentiment = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for article in articles:
            sentiment = article.get('sentiment', 'neutral')
            weight = 1.0
            
            # Social posts with high engagement weighted more heavily
            if article.get('source_type') == 'social_media':
                engagement = article.get('engagement', {})
                if engagement:
                    total_engagement = (
                        engagement.get('likes', 0) + 
                        engagement.get('retweets', 0) + 
                        engagement.get('comments', 0)
                    )
                    weight = 1 + (total_engagement / 100)  # Normalize
            
            if sentiment in weighted_sentiment:
                weighted_sentiment[sentiment] += weight
        
        return {
            'top_keywords': keyword_freq.most_common(20),
            'sentiment_distribution': dict(sentiment_counts),
            'weighted_sentiment': weighted_sentiment,
            'source_distribution': dict(source_dist),
            'top_politicians': politician_freq.most_common(10),
            'total_articles': len(articles),
            'date_range': {
                'earliest': min(a.get('published_date') for a in articles if a.get('published_date')),
                'latest': max(a.get('published_date') for a in articles if a.get('published_date')),
            }
        }
    
    def get_articles_by_source_type(self, articles: List[Dict], source_type: str) -> List[Dict]:
        """Get articles filtered by source type"""
        return [a for a in articles if a.get('source_type') == source_type]
    
    def get_high_engagement_articles(self, articles: List[Dict], min_engagement: int = 100) -> List[Dict]:
        """Get social media posts with high engagement"""
        high_engagement = []
        for article in articles:
            if article.get('source_type') == 'social_media':
                engagement = article.get('engagement', {})
                total = (
                    engagement.get('likes', 0) + 
                    engagement.get('retweets', 0) + 
                    engagement.get('comments', 0)
                )
                if total >= min_engagement:
                    high_engagement.append(article)
        
        return sorted(
            high_engagement,
            key=lambda x: (
                x.get('engagement', {}).get('likes', 0) + 
                x.get('engagement', {}).get('retweets', 0) + 
                x.get('engagement', {}).get('comments', 0)
            ),
            reverse=True
        )
    
    def get_articles_by_politician(self, articles: List[Dict], politician: str) -> List[Dict]:
        """Get all articles mentioning a specific politician"""
        relevant = []
        politician_lower = politician.lower()
        
        for article in articles:
            # Check entities
            politicians = article.get('entities', {}).get('politicians', [])
            if any(politician_lower in p.lower() for p in politicians):
                relevant.append(article)
            # Also check content
            elif politician_lower in (article.get('content', '') or '').lower():
                relevant.append(article)
        
        return relevant
    
    def group_articles_by_date(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Group articles by date"""
        grouped = {}
        
        for article in articles:
            date = article.get('published_date')
            if date:
                # Convert to string date if datetime
                if hasattr(date, 'date'):
                    date_str = str(date.date())
                else:
                    date_str = str(date)[:10]  # Get YYYY-MM-DD part
                
                if date_str not in grouped:
                    grouped[date_str] = []
                grouped[date_str].append(article)
        
        return grouped
    
    def generate_summary_report(self, articles: List[Dict]) -> str:
        """Generate a text summary report of all content"""
        trends = self.analyze_unified_trends(articles)
        
        report = f"""
UNIFIED CONTENT ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW
--------
Total Articles Analyzed: {trends.get('total_articles', 0)}
Sources: {', '.join(trends.get('source_distribution', {}).keys())}

SOURCE BREAKDOWN
{self._format_source_breakdown(trends.get('source_distribution', {}))}

TOP KEYWORDS
{self._format_list(trends.get('top_keywords', [])[:10])}

SENTIMENT ANALYSIS
{self._format_sentiment(trends.get('sentiment_distribution', {}))}

TOP POLITICIANS MENTIONED
{self._format_list(trends.get('top_politicians', [])[:10])}

TIME PERIOD
From {trends.get('date_range', {}).get('earliest')}
To {trends.get('date_range', {}).get('latest')}
        """.strip()
        
        return report
    
    def _format_source_breakdown(self, source_dist: Dict) -> str:
        """Format source breakdown for report"""
        lines = []
        for source, count in source_dist.items():
            lines.append(f"  {source}: {count} articles")
        return "\n".join(lines) if lines else "  No data"
    
    def _format_list(self, items: List[Tuple]) -> str:
        """Format a list of (item, count) tuples"""
        lines = []
        for item, count in items:
            lines.append(f"  {item}: {count} mentions")
        return "\n".join(lines) if lines else "  No data"
    
    def _format_sentiment(self, sentiment: Dict) -> str:
        """Format sentiment data for report"""
        total = sum(sentiment.values()) or 1
        lines = []
        for sent, count in sentiment.items():
            percentage = (count / total) * 100
            lines.append(f"  {sent.capitalize()}: {count} ({percentage:.1f}%)")
        return "\n".join(lines) if lines else "  No data"