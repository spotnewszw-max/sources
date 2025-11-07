"""
Content filtering and relevance scoring for Zimbabwe news aggregator
"""

import re
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class ZimbabweContentFilter:
    """Filters and scores articles for relevance to Zimbabwe"""
    
    # Zimbabwe-specific keywords and their weights
    ZIMBABWE_KEYWORDS = {
        # Geographic - Primary (weight: 1.0)
        'zimbabwe': 1.0,
        'harare': 1.0,
        'bulawayo': 1.0,
        'gweru': 1.0,
        'mutare': 1.0,
        'victoria falls': 0.9,
        'zim': 0.8,
        
        # Political figures
        'mnangagwa': 1.0,
        'emmerson': 0.8,
        'chamisa': 1.0,
        'nelson chamisa': 1.0,
        'mthuli ncube': 0.9,
        'chiwenga': 0.9,
        'constantino chiwenga': 1.0,
        
        # Government/Political parties
        'zanu-pf': 1.0,
        'ccc': 1.0,
        'mdca': 0.9,
        'parliament': 0.7,
        'government': 0.5,  # Lower weight - could refer to any government
        
        # Economic terms
        'rtgs dollar': 1.0,
        'zimbabwean dollar': 0.9,
        'zwd': 0.8,
        'bond notes': 0.9,
        'foreign currency': 0.7,
        'inflation': 0.6,
        'economy': 0.5,
        
        # Companies/Institutions
        'econet': 0.8,
        'strive masiyiwa': 0.8,
        'reserve bank': 0.7,
        'cbz': 0.7,
        'fbc': 0.7,
        
        # Social/Issues
        'election': 0.7,
        'protests': 0.7,
        'crisis': 0.6,
        'reform': 0.6,
        'sanctions': 0.7,
        
        # Other
        'africa': 0.3,  # Low weight - common term
    }
    
    # Negative keywords (reduce score if present)
    NEGATIVE_KEYWORDS = {
        'nigeria': -0.3,
        'egypt': -0.3,
        'south africa': -0.2,
        'kenya': -0.2,
        'uganda': -0.2,
    }
    
    def __init__(self, min_score: float = 0.3, min_keywords: int = 1):
        """
        Initialize filter
        
        Args:
            min_score: Minimum relevance score (0-1) to include article
            min_keywords: Minimum number of matched keywords
        """
        self.min_score = min_score
        self.min_keywords = min_keywords
    
    def calculate_relevance_score(self, article: Dict) -> float:
        """
        Calculate relevance score for an article (0-1)
        
        Args:
            article: Article dictionary with title, content, summary
            
        Returns:
            Float score between 0 and 1
        """
        text = self._prepare_text(article)
        
        if not text:
            return 0.0
        
        score = 0.0
        matched_keywords = []
        
        # Check for positive keywords
        for keyword, weight in self.ZIMBABWE_KEYWORDS.items():
            if keyword.lower() in text:
                score += weight
                matched_keywords.append((keyword, weight))
        
        # Check for negative keywords
        for keyword, weight in self.NEGATIVE_KEYWORDS.items():
            if keyword.lower() in text:
                score += weight  # weight is negative
        
        # Normalize score (roughly)
        # Max possible score is sum of all weights, but normalize to 0-1
        max_weight = sum(w for w in self.ZIMBABWE_KEYWORDS.values() if w > 0)
        if max_weight > 0:
            score = min(score / (max_weight / 5), 1.0)  # Divide by max_weight/5 for reasonable scaling
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        logger.debug(f"Article score: {score:.2f}, Keywords: {len(matched_keywords)}")
        
        return score
    
    def _prepare_text(self, article: Dict) -> str:
        """Prepare article text for analysis"""
        parts = []
        
        if article.get('title'):
            parts.append(article['title'].lower())
        
        if article.get('content'):
            parts.append(article['content'].lower()[:1000])  # First 1000 chars
        elif article.get('summary'):
            parts.append(article['summary'].lower())
        
        return ' '.join(parts)
    
    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter articles and add relevance scores
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Filtered list with scores, sorted by relevance
        """
        scored_articles = []
        
        for article in articles:
            score = self.calculate_relevance_score(article)
            
            if score >= self.min_score:
                article['relevance_score'] = score
                scored_articles.append(article)
            else:
                logger.debug(f"Filtered out article (score {score:.2f}): {article.get('title', 'Unknown')[:50]}")
        
        # Sort by relevance score (highest first)
        scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"Filtered {len(scored_articles)}/{len(articles)} articles (kept {len(scored_articles)})")
        
        return scored_articles
    
    def extract_entities(self, article: Dict) -> Dict:
        """
        Extract named entities and metadata from article
        
        Args:
            article: Article dictionary
            
        Returns:
            Dictionary with extracted entities
        """
        text = self._prepare_text(article)
        
        entities = {
            'politicians': self._extract_politicians(text),
            'locations': self._extract_locations(text),
            'organizations': self._extract_organizations(text),
            'issues': self._extract_issues(text),
        }
        
        return entities
    
    def _extract_politicians(self, text: str) -> List[str]:
        """Extract mentions of Zimbabwe political figures"""
        politicians = {
            'emmerson mnangagwa': ['emmerson', 'mnangagwa', 'ed'],
            'nelson chamisa': ['chamisa', 'nelson'],
            'mthuli ncube': ['ncube', 'mthuli'],
            'constantino chiwenga': ['chiwenga', 'constantino'],
            'strive masiyiwa': ['masiyiwa', 'strive'],
            'hopewell chin\'ono': ['chin\'ono', 'hopewell'],
        }
        
        found = []
        for name, keywords in politicians.items():
            for keyword in keywords:
                if keyword in text:
                    if name not in found:
                        found.append(name)
                    break
        
        return found
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extract geographic locations"""
        locations = ['harare', 'bulawayo', 'gweru', 'mutare', 'victoria falls', 'zimbabwe']
        return [loc for loc in locations if loc in text]
    
    def _extract_organizations(self, text: str) -> List[str]:
        """Extract organization names"""
        organizations = [
            'zanu-pf', 'ccc', 'mdca',
            'econet', 'reserve bank', 'cbz', 'fbc',
            'herald', 'newsday', 'zimfact'
        ]
        return [org for org in organizations if org in text]
    
    def _extract_issues(self, text: str) -> List[str]:
        """Extract key issues/topics"""
        issues = {
            'economy': ['inflation', 'economy', 'rtgs', 'dollar', 'forex', 'recession'],
            'politics': ['election', 'government', 'politics', 'parliament', 'minister'],
            'protests': ['protest', 'demonstration', 'strike', 'violence', 'unrest'],
            'sanctions': ['sanctions', 'embargo', 'international'],
            'corruption': ['corruption', 'fraud', 'scandal', 'arrest'],
        }
        
        found = []
        for category, keywords in issues.items():
            for keyword in keywords:
                if keyword in text:
                    if category not in found:
                        found.append(category)
                    break
        
        return found
    
    def categorize_article(self, article: Dict) -> str:
        """
        Categorize article into news type
        
        Args:
            article: Article dictionary
            
        Returns:
            Category string
        """
        text = self._prepare_text(article)
        
        categories = {
            'politics': ['election', 'government', 'parliament', 'mnangagwa', 'chamisa', 'minister'],
            'economy': ['economy', 'inflation', 'rtgs', 'dollar', 'business', 'stock', 'trade'],
            'technology': ['tech', 'software', 'internet', 'digital', 'innovation'],
            'agriculture': ['farmer', 'crop', 'agriculture', 'tobacco', 'farming'],
            'sports': ['sport', 'football', 'soccer', 'cricket', 'zimbabwe warriors'],
            'health': ['health', 'doctor', 'hospital', 'covid', 'disease'],
            'education': ['school', 'university', 'education', 'student'],
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(text.count(keyword) for keyword in keywords)
            scores[category] = score
        
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'general'


class ContentAnalyzer:
    """Analyzes content for insights and trends"""
    
    @staticmethod
    def detect_sentiment(text: str) -> str:
        """
        Simple sentiment detection (positive/negative/neutral)
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment label
        """
        positive_words = ['good', 'great', 'excellent', 'growth', 'success', 'improve']
        negative_words = ['bad', 'crisis', 'decline', 'loss', 'fail', 'problem', 'issue']
        
        text_lower = text.lower()
        
        pos_count = sum(text_lower.count(word) for word in positive_words)
        neg_count = sum(text_lower.count(word) for word in negative_words)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect language of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (en, zu, sn, etc.)
        """
        # Simple heuristic - check for Zulu and Shona words
        shona_words = ['muno', 'chirwere', 'kubva', 'asi', 'zviri']
        zulu_words = ['umuntu', 'ikhaya', 'ukusikela', 'isizulu']
        
        text_lower = text.lower()
        
        shona_count = sum(text_lower.count(word) for word in shona_words)
        zulu_count = sum(text_lower.count(word) for word in zulu_words)
        
        if shona_count > zulu_count and shona_count > 0:
            return 'sn'  # Shona
        elif zulu_count > 0:
            return 'zu'  # Zulu
        else:
            return 'en'  # English (default)
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#\w+', text)
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract @mentions from text"""
        return re.findall(r'@\w+', text)