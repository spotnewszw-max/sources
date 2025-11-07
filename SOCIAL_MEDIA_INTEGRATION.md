# Social Media Integration Guide

## Overview

Monitor policy makers, decision influencers, and trending topics on Twitter/X and Facebook to capture what key figures are saying about Zimbabwe.

---

## 🐦 Twitter/X Integration

### Why Twitter for Zimbabwe News?

- **Breaking News:** Most journalists post breaking news to Twitter first
- **Policy Makers:** Government officials announce decisions on Twitter
- **Real-time Trending:** See what's trending in Zimbabwe NOW
- **Direct Quotes:** Get unfiltered statements from leaders
- **Retweets & Engagement:** See public reaction to issues

### Setup Instructions (15 minutes)

#### Step 1: Create Twitter Developer Account

1. Go to https://developer.twitter.com
2. Click "Sign up" → Create account or use existing Twitter account
3. Fill out developer application:
   - **Intended use:** News aggregation
   - **Organization:** Your organization name
   - **Use case:** "Building a news aggregator focused on Zimbabwe"
4. Agree to terms and verify email
5. Wait for approval (usually instant, sometimes 24 hours)

#### Step 2: Create an App (Project)

1. Go to Dashboard → "Create an App"
2. Choose "Development" environment
3. Give app a name: e.g., "Zimbabwe News Aggregator"
4. You'll get:
   - **API Key** (keep secret)
   - **API Secret** (keep secret)
   - **Bearer Token** (for authentication)

#### Step 3: Add to Environment

Update `.env.development`:

```bash
# Twitter API (Get from https://developer.twitter.com)
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Optional: Tweet collection parameters
TWITTER_QUERY=#Zimbabwe
TWITTER_LANGUAGES=en,zu
TWITTER_MAX_RESULTS=100
```

#### Step 4: Use in Code

```python
from src.services.social_media import TwitterMonitor

monitor = TwitterMonitor(
    bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
)

# Search for tweets about Zimbabwe
tweets = monitor.search_tweets(
    query='#Zimbabwe',
    max_results=100
)

# Get tweets from specific accounts
tweets = monitor.get_user_tweets(
    username='edmnangagwa',
    max_results=50
)

# Track trending topics
trends = monitor.get_trending(
    woeid=12055743  # Zimbabwe WOEID
)
```

### Key Accounts to Monitor

```python
ACCOUNTS_TO_MONITOR = [
    # Government
    'edmnangagwa',          # President
    'MthuliNcube',          # Finance Minister
    
    # Opposition
    'nelsonchamisa',        # CCC Leader
    
    # Business
    'strive',               # Strive Masiyiwa / Econet
    
    # Media/Journalists
    'daddyhope',            # Hopewell Chin'ono
    'VinceMusewe',          # Economist
    
    # News Outlets
    'newsdayzimbabwe',
    'herald_zim',
]
```

### Search Queries

```python
SEARCH_QUERIES = [
    '#Zimbabwe',
    '#ZimEconomy',
    '#Harare',
    '#ZimPolitics',
    'Emmerson Mnangagwa',
    'Nelson Chamisa',
    'Zimbabwe economy',
    'RTGS dollar',
]
```

---

## 📘 Facebook Integration

### Why Facebook for Zimbabwe?

- **Official Announcements:** Government and news outlets post there
- **Wider Audience:** Captures posts not on Twitter
- **Page Comments:** See public engagement
- **Video Content:** Facebook videos from press conferences, statements

### Setup Instructions (20 minutes)

#### Step 1: Create Facebook Developer Account

1. Go to https://developers.facebook.com
2. Click "Get Started"
3. Create account (use your email)
4. Verify email
5. Create a new App:
   - Type: "Business"
   - Name: "Zimbabwe News Aggregator"
   - Purpose: "Analytics"

#### Step 2: Generate Access Token

1. In app settings → "Basic" → Copy App ID and App Secret
2. Go to Graph API Explorer (https://developers.facebook.com/tools/explorer)
3. Select your app from dropdown
4. Click "Generate Access Token"
5. Select permissions:
   - `public_content`
   - `pages_read_engagement`
   - `pages_read_user_content`
6. Copy the token

#### Step 3: Get Page IDs

Find Facebook page IDs for news outlets:

```bash
# Using curl
curl -G \
  -d "access_token=YOUR_ACCESS_TOKEN" \
  https://graph.facebook.com/zimbabwegovernment

# Returns: "id": "123456789"
```

#### Step 4: Add to Environment

```bash
# Facebook API
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_IDS=zimbabwegovernment,newsdayzimbabwe,herald.co.zw,bulawayo24
FACEBOOK_FIELDS=id,message,created_time,permalink_url,shares,comments,likes
```

#### Step 5: Use in Code

```python
from src.services.social_media import FacebookMonitor

monitor = FacebookMonitor(
    access_token=os.getenv('FACEBOOK_ACCESS_TOKEN')
)

# Get posts from a page
posts = monitor.get_page_posts(
    page_id='zimbabwegovernment',
    limit=50
)

# Get comments on a post
comments = monitor.get_post_comments(
    post_id='123456789_987654321'
)

# Get engagement metrics
engagement = monitor.get_engagement(
    page_id='zimbabwegovernment'
)
```

### Official Pages to Monitor

```python
PAGES_TO_MONITOR = {
    'zimbabwegovernment': 'Government of Zimbabwe',
    'newsdayzimbabwe': 'NewsDay Zimbabwe',
    'herald.co.zw': 'The Herald',
    'bulawayo24': 'Bulawayo24',
    'econet.co.zw': 'Econet Zimbabwe',
}
```

---

## 🤖 Implementation Code Structure

### Create Social Media Service

File: `src/services/social_media.py`

```python
"""Social media monitoring for Zimbabwe news aggregator"""

import tweepy
import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TwitterMonitor:
    """Monitor Twitter for Zimbabwe news and policy maker statements"""
    
    def __init__(self, bearer_token: str):
        self.client = tweepy.Client(bearer_token=bearer_token)
    
    def search_tweets(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search for tweets matching query"""
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['author_id', 'created_at', 'public_metrics'],
                expansions=['author_id'],
                user_fields=['username', 'name', 'public_metrics']
            )
            
            results = []
            if tweets.data:
                users = {user.id: user for user in tweets.includes['users']}
                
                for tweet in tweets.data:
                    user = users.get(tweet.author_id)
                    results.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'author': user.username,
                        'author_name': user.name,
                        'created_at': tweet.created_at,
                        'likes': tweet.public_metrics['like_count'],
                        'retweets': tweet.public_metrics['retweet_count'],
                        'replies': tweet.public_metrics['reply_count'],
                        'url': f"https://twitter.com/{user.username}/status/{tweet.id}",
                        'source': 'twitter',
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching Twitter: {str(e)}")
            return []
    
    def get_user_tweets(self, username: str, max_results: int = 50) -> List[Dict]:
        """Get recent tweets from a specific user"""
        try:
            user = self.client.get_user(username=username)
            
            tweets = self.client.get_users_tweets(
                id=user.data.id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            results = []
            if tweets.data:
                for tweet in tweets.data:
                    results.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'author': username,
                        'created_at': tweet.created_at,
                        'likes': tweet.public_metrics['like_count'],
                        'retweets': tweet.public_metrics['retweet_count'],
                        'url': f"https://twitter.com/{username}/status/{tweet.id}",
                        'source': 'twitter',
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting tweets from {username}: {str(e)}")
            return []


class FacebookMonitor:
    """Monitor Facebook for Zimbabwe news and policy maker statements"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.graph_url = "https://graph.facebook.com/v18.0"
    
    def get_page_posts(self, page_id: str, limit: int = 50) -> List[Dict]:
        """Get posts from a Facebook page"""
        try:
            url = f"{self.graph_url}/{page_id}/posts"
            params = {
                'access_token': self.access_token,
                'fields': 'id,message,story,created_time,type,link,permalink_url,shares,comments.summary(total_count).limit(0),likes.summary(total_count).limit(0)',
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            results = []
            for post in response.json().get('data', []):
                results.append({
                    'id': post.get('id'),
                    'text': post.get('message') or post.get('story'),
                    'created_at': post.get('created_time'),
                    'url': post.get('permalink_url'),
                    'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                    'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                    'shares': post.get('shares', {}).get('count', 0),
                    'source': 'facebook',
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting Facebook posts: {str(e)}")
            return []
```

---

## 🔗 Integration with News Aggregator

### Update Fetcher to Include Social Media

In `configs/zimbabwe.yaml`:

```yaml
social_media:
  twitter:
    enabled: true
    bearer_token: ${TWITTER_BEARER_TOKEN}
    search_queries:
      - "#Zimbabwe"
      - "#ZimEconomy"
    accounts:
      - edmnangagwa
      - nelsonchamisa
      - strive
  
  facebook:
    enabled: true
    access_token: ${FACEBOOK_ACCESS_TOKEN}
    pages:
      - zimbabwegovernment
      - newsdayzimbabwe
```

### Update Main Fetch Job

In `src/tasks/workers.py`:

```python
@shared_task
def fetch_all_news():
    """Fetch news from RSS and social media"""
    from src.services.fetcher import fetch_articles_from_sources
    from src.services.social_media import TwitterMonitor, FacebookMonitor
    from src.services.content_filter import ZimbabweContentFilter
    
    all_articles = []
    
    # Fetch RSS feeds
    rss_articles = fetch_articles_from_sources(CONFIG.fetcher.sources)
    all_articles.extend(rss_articles)
    
    # Fetch Twitter
    if CONFIG.social_media.twitter.enabled:
        twitter = TwitterMonitor(CONFIG.social_media.twitter.bearer_token)
        for query in CONFIG.social_media.twitter.search_queries:
            tweets = twitter.search_tweets(query)
            # Convert tweets to article format
            all_articles.extend(tweets)
    
    # Filter for Zimbabwe relevance
    filter = ZimbabweContentFilter()
    filtered = filter.filter_articles(all_articles)
    
    # Store in database
    # ... save to DB
```

---

## 📊 Monitoring Dashboard

Display social media content alongside news:

```python
@app.get('/api/v1/trending')
async def get_trending():
    """Get trending topics from Twitter and Facebook"""
    twitter = TwitterMonitor(os.getenv('TWITTER_BEARER_TOKEN'))
    
    return {
        'twitter': twitter.search_tweets('#Zimbabwe', max_results=10),
        'policy_makers': get_latest_from_accounts(['edmnangagwa', 'nelsonchamisa']),
        'news': get_latest_articles(limit=10)
    }
```

---

## ✅ Rate Limits

### Twitter API

- **Free Tier:** 450 requests/15 minutes
- **Pricing:** $100-2,000/month for higher limits
- **Recommendation:** Cache results, fetch every 1-2 hours

### Facebook API

- **Free Tier:** Rate limited but generous
- **Recommendation:** 1 request per second max

---

## 🔒 Security Best Practices

1. **Never commit API keys to git**
   ```bash
   # Add to .gitignore
   .env
   .env.development
   .env.production
   ```

2. **Use environment variables**
   ```python
   TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
   ```

3. **Rotate tokens regularly**
   - Set a reminder to rotate quarterly

4. **Use separate credentials for dev/prod**
   - Development: Lower volume limits
   - Production: Higher volume, separate tokens

---

## 🆘 Troubleshooting

### "Invalid Bearer Token"
- Check token has not expired
- Regenerate token from developer dashboard
- Ensure no extra spaces/quotes

### "Access Denied"
- Verify permissions in app settings
- Check page IDs are correct
- Ensure token has not been revoked

### "Rate Limited"
- Implement exponential backoff retry
- Cache results longer
- Upgrade API tier

### "No Results"
- Check query syntax is correct
- Verify accounts/pages exist
- Try in Twitter/Facebook directly first

---

## 📝 Next Steps

1. **Immediate:** Set up Twitter API (can start searching for #Zimbabwe content today)
2. **This week:** Add Twitter integration to aggregator
3. **Next week:** Set up Facebook API
4. **Later:** Add TikTok, Instagram, LinkedIn if needed

---

## 📚 Resources

- [Twitter API Docs](https://developer.twitter.com/en/docs/twitter-api)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Tweepy Python Library](https://docs.tweepy.org)
- [Rate Limiting Guide](https://developer.twitter.com/en/docs/projects/overview)

---

**Start with Twitter API - it's simpler and more useful for news aggregation! 🚀**