# Content Aggregation & Web Scraping Guide

## Overview

The Think Tank system now aggregates content from **three complementary sources**:

1. **RSS Feeds** (12 sources) - Traditional news feeds from Zimbabwe & African publishers
2. **Web Scraping** (9 sites) - Direct scraping from news websites for fresh content
3. **Social Media** (6 influencers) - Captures posts from politicians, journalists, economists

All three sources feed into a unified analysis engine that identifies trends, makes predictions, and generates articles.

---

## Architecture

### Content Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   CONTENT SOURCES                           │
├──────────────────┬──────────────────┬──────────────────────┤
│   RSS Feeds      │   Web Scraping   │  Social Media Posts  │
│  (12 sources)    │   (9 sites)      │   (6 influencers)    │
├──────────────────┴──────────────────┴──────────────────────┤
│              Normalization Layer                            │
│  • Unified data structure                                   │
│  • Timestamp standardization                                │
│  • Entity extraction                                        │
├─────────────────────────────────────────────────────────────┤
│           Duplicate Detection & Deduplication               │
│  • Title similarity matching (75%+ threshold)               │
│  • Content comparison                                       │
│  • Cross-source correlation                                 │
├─────────────────────────────────────────────────────────────┤
│         Unified Content Analysis Engine                     │
│  • Combined trend analysis                                  │
│  • Sentiment analysis across sources                        │
│  • Entity & keyword extraction                              │
│  • Source weighting (social=1.2x, scraped=1.1x, rss=1.0x) │
├─────────────────────────────────────────────────────────────┤
│        Think Tank Article Generation                        │
│  • Historical Analysis (unlimited historical data)          │
│  • Present Analysis (last 7 days across all sources)       │
│  • Future Prediction (90-day forecast)                      │
├─────────────────────────────────────────────────────────────┤
│          Publication & Distribution                         │
│  • Confidence scoring                                       │
│  • Auto-publish (≥80% confidence)                          │
│  • Flag for review (65-80% confidence)                      │
│  • Manual approval (<65% confidence)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Web Scraper Configuration

### Pre-Configured Sites

The system comes with 9 pre-configured scraper targets:

#### Zimbabwe Local News (High Priority - Every 60 minutes)
```yaml
herald       → The Herald Zimbabwe
newsday      → NewsDay Zimbabwe
bulawayo24   → Bulawayo24
zimbabwean   → The Zimbabwean
```

#### African Regional News (Medium Priority - Every 2 hours)
```yaml
allafrica    → AllAfrica Zimbabwe section
mg           → Mail & Guardian Africa
```

#### International Coverage (Low Priority - Every 3 hours)
```yaml
bbc_africa   → BBC Africa section
reuters      → Reuters Africa
aljazeera    → Al Jazeera Africa
```

### Adding Custom Sites

To add a new scraper target:

1. **Edit `zimbabwe.yaml`:**
```yaml
think_tank:
  web_scraper:
    sites:
      zimbabwe_local:
        sites_to_scrape:
          - herald           # Existing
          - newsday          # Existing
          - mynewsite        # ADD THIS
```

2. **Define the configuration in `web_scraper.py`:**
```python
DEFAULT_CONFIGS = {
    # ... existing configs ...
    "mynewsite": {
        "site_name": "My News Site",
        "site_url": "https://mynewsite.com",
        "source_category": "zimbabwe_local",
        "scraper_type": "beautifulsoup",
        "article_selector": "article.post, div.news-item",
        "title_selector": "h2.title",
        "content_selector": "div.content",
        "author_selector": "span.author",
        "date_selector": "time.published",
        "image_selector": "img.featured",
        "scrape_interval_minutes": 60,
    }
}
```

---

## Duplicate Detection

### How It Works

The system automatically detects duplicates and similar articles:

| Type | Similarity | Description |
|------|-----------|-------------|
| **exact** | >95% | Identical articles from multiple sources |
| **near_duplicate** | 75-95% | Same story with slight variations |
| **same_story_different_angle** | 65-75% | Different perspectives on same event |
| **same_topic** | <65% | Articles on same topic, different stories |

### Database Tracking

All duplicates are tracked in `content_duplicates` table:
```
canonical_article_id  → Original/primary article
related_article_id    → Related/duplicate article
title_similarity      → 0-1 score
content_similarity    → 0-1 score
duplicate_type        → Classification
```

### Handling Duplicates

When duplicates are detected:

1. **Keep all versions** - Each source's version is retained
2. **Mark relationships** - Link canonical to duplicates
3. **Track in analysis** - Use for ranking source reliability
4. **Include in reports** - Show coverage breadth across sources

---

## Unified Content Analysis

### Combining All Sources

The `UnifiedContentAnalyzer` normalizes content from all sources:

```python
# Collect from all sources
all_articles = analyzer.collect_all_articles(
    rss_articles=rss_data,
    scraped_articles=scraped_data,
    social_posts=twitter_posts,
    topic="economy",
    days_back=30
)

# Get unified trends
trends = analyzer.analyze_unified_trends(all_articles)
# Returns: top keywords, sentiment, politicians mentioned, source breakdown, etc.
```

### Source Weighting

Different sources contribute differently to analysis:

| Source | Weight | Rationale |
|--------|--------|-----------|
| Social Posts | 1.2× | High engagement indicates importance; influencer reach matters |
| Scraped News | 1.1× | Fresh content; reflects current reporting |
| RSS Feeds | 1.0× | Baseline; established, traditional sources |

### Analysis Output

```python
trends = {
    'top_keywords': [('economy', 45), ('inflation', 38), ('currency', 32)],
    'sentiment_distribution': {'positive': 12, 'negative': 28, 'neutral': 15},
    'weighted_sentiment': {'positive': 14.4, 'negative': 33.6, 'neutral': 15.0},
    'source_distribution': {'social_media': 12, 'rss': 28, 'scraped': 15},
    'top_politicians': [('Mnangagwa', 31), ('Chamisa', 24), ('Ncube', 19)],
    'total_articles': 55,
    'date_range': {
        'earliest': '2024-01-15',
        'latest': '2024-02-15'
    }
}
```

---

## Database Schema

### New Tables

#### `scraped_articles`
Stores articles scraped from websites (not RSS)

```sql
id                    -- Unique identifier
title, content        -- Article text
url                   -- Source URL
source_site           -- e.g., "herald.co.zw"
source_category       -- zimbabwe_local, regional_african, international
author, published_date
sentiment, relevance_score
mentioned_politicians, mentioned_organizations
is_duplicate          -- Marks as duplicate of another article
duplicate_of_id       -- Reference to original article
duplicate_sources     -- List of other URLs with same content
extraction_confidence -- 0-1 confidence in scraper accuracy
```

#### `content_duplicates`
Tracks relationships between duplicate/similar articles

```sql
id
canonical_article_id, canonical_source
related_article_id, related_source
title_similarity, content_similarity
duplicate_type        -- exact, near_duplicate, same_story, etc.
detected_date
manual_review, is_verified
```

#### `web_scraper_configs`
Configuration for scraper targets (managed via YAML)

```sql
site_name             -- e.g., "The Herald"
site_url              -- https://herald.co.zw
source_category       -- zimbabwe_local, regional_african, international
scraper_type          -- beautifulsoup, xpath, css
article_selector      -- CSS selector for articles
title_selector, content_selector, etc.
is_active             -- Enable/disable scraper
scrape_interval_minutes
last_scrape_date, last_scrape_status
total_articles_scraped, avg_relevance_score
```

### Relationships

```
Generated Articles
    ├── Links to RSS articles via generated_article_sources
    ├── Links to scraped articles via generated_article_sources_scraped
    └── Links to social posts via generated_article_sources_social

Content Duplicates
    ├── Maps canonical → related articles
    └── Tracks across all three sources (RSS, scraped, social)

Scraped Articles
    ├── Marked as duplicate of other content
    └── Tracked in publication queue
```

---

## Configuration Details

### Web Scraper Settings

```yaml
think_tank:
  web_scraper:
    # Master enable/disable
    enabled: true
    
    # Global scrape interval (minutes)
    scrape_interval: 120
    
    # Max articles per site
    max_articles_per_site: 50
    
    # Duplicate detection threshold
    similarity_threshold: 0.75
    
    # Analysis settings
    analyze_content: true
    extract_entities: true
    analyze_sentiment: true
    min_relevance_score: 0.5
    
    # Content filters
    min_content_length: 200
    exclude_keywords:
      - sponsored
      - advertisement
```

### Unified Analysis Settings

```yaml
unified_analysis:
  enabled: true
  
  # Combine these sources
  sources_to_combine:
    - rss_feeds
    - scraped_articles
    - social_posts
  
  # Generate cross-source insights
  generate_cross_source_insights: true
  
  # Source importance weighting
  source_weights:
    social_posts: 1.2
    rss_feeds: 1.0
    scraped_articles: 1.1
```

---

## API Endpoints

### Scraper Management

```
GET  /api/v1/scrapers/config          List all scraper configs
POST /api/v1/scrapers/config          Add new scraper
PUT  /api/v1/scrapers/config/{id}     Update scraper config
DELETE /api/v1/scrapers/config/{id}   Disable scraper

GET  /api/v1/scrapers/status          Check scraper status
POST /api/v1/scrapers/run             Trigger scraping now
```

### Duplicate Detection

```
GET  /api/v1/duplicates               List duplicate groups
GET  /api/v1/duplicates/{id}          Details on specific duplicate
POST /api/v1/duplicates/resolve       Mark as resolved
```

### Unified Analysis

```
GET  /api/v1/unified/articles         Get all articles from all sources
GET  /api/v1/unified/trends           Trend analysis across sources
GET  /api/v1/unified/report           Generate comprehensive report
GET  /api/v1/unified/by-source        Articles grouped by source type
```

---

## Article Generation with Multiple Sources

### Historical Analysis (Example)

When generating a historical article on "Zimbabwe Economy":

**Data Collection:**
- ✅ All RSS articles mentioning economy (12+ sources, unlimited history)
- ✅ All scraped articles from Herald, Newsday, etc. (last 6 months)
- ✅ All influencer social posts about economy (unlimited history)
- ✅ Apply duplicate deduplication
- ✅ Combine 100+ related articles

**Analysis:**
- Identify economic cycles and patterns
- Track sentiment evolution over time
- Extract key events and milestones
- Identify influential figures and organizations

**Output:**
- Comprehensive historical context
- Timeline of major events
- Evolution of sentiment
- Key stakeholders and their positions

### Present Analysis (Example)

**Data Collection:**
- ✅ RSS feeds (last 7 days)
- ✅ Scraped news (last 7 days, freshest content)
- ✅ Social media posts (last 7 days, highest engagement)

**Analysis:**
- Current situation overview
- Multiple perspectives from different sources
- Sentiment snapshot (weighted by engagement)
- Current stakeholder positions

**Output:**
- Situation summary
- All viewpoints represented
- Public sentiment
- Key developments

### Future Prediction (Example)

**Data Collection:**
- ✅ All historical data (unlimited)
- ✅ Current trends (last 30 days)
- ✅ Recent social media signals
- ✅ Breaking news (fresh scraped articles)

**Analysis:**
- Identify trend patterns
- Consider all source signals
- Calculate prediction confidence
- Model multiple scenarios

**Output:**
- Most likely outcome
- Alternative scenarios
- Risk factors
- Confidence level

---

## Workflow Example

### Complete Content Analysis Cycle (Every 2 hours)

**Step 1: Content Collection (15 min)**
```
Time: 08:00
├─ RSS feeds fetch       → 50 new articles
├─ Web scrapers run      → 45 new articles
└─ Social media capture  → 12 new posts
    Total new content: 107 items
```

**Step 2: Normalization (5 min)**
```
├─ Standardize timestamps
├─ Extract entities (politicians, organizations, topics)
├─ Analyze sentiment
├─ Calculate relevance scores
└─ Status: 107 items normalized
```

**Step 3: Deduplication (10 min)**
```
├─ Compare titles across sources
├─ Similarity analysis (>75% = duplicate)
├─ Mark related content
└─ Result: 95 unique + 12 duplicates identified
```

**Step 4: Unified Analysis (10 min)**
```
├─ Top keywords across all sources
├─ Sentiment distribution (weighted by engagement)
├─ Politicians mentioned frequency
├─ Source contribution breakdown
└─ Generate comprehensive trend report
```

**Step 5: Article Generation (20 min, if scheduled)**
```
└─ Only if it's article generation time (daily 00:00)
    ├─ Historical analysis
    ├─ Present analysis
    └─ Future prediction
```

**Step 6: Publication (5 min, if high confidence)**
```
└─ Auto-publish articles ≥80% confidence
└─ Flag for review 65-80% confidence
└─ Mark for approval <65% confidence
```

Total cycle: ~60-75 minutes

---

## Performance Tips

### For Production Deployment

1. **Parallel Scraping**
   - Scrape multiple sites concurrently
   - Separate threads for different priorities
   - Can handle 10+ simultaneous scrapes

2. **Caching**
   - Cache article HTML for 5 minutes
   - Avoid re-scraping same content
   - Reduces bandwidth and load

3. **Database Optimization**
   - Index on `scraped_articles.source_site`
   - Index on `content_duplicates.detected_date`
   - Regular vacuum/analyze

4. **Selective Scraping**
   - Reduce `scrape_interval` for important sites
   - Increase for low-priority sources
   - Skip inactive sites

---

## Troubleshooting

### Scraper Not Running

**Check:**
```yaml
think_tank:
  web_scraper:
    enabled: true  # Must be true
```

**Verify:**
```bash
curl http://localhost:8000/api/v1/scrapers/status
```

### Low Article Count

**Causes:**
1. Scrape interval too long (120+ min = slower)
2. Min relevance score too high (0.5-0.7 recommended)
3. Sites returning errors

**Solution:**
- Reduce `scrape_interval` to 60 min
- Lower `min_relevance_score` to 0.4
- Check scraper logs

### Duplicate False Positives

**Adjust threshold:**
```yaml
duplicate_detection:
  similarity_threshold: 0.80  # Increase from 0.75
```

---

## Next Steps

1. ✅ **System Review** - Check all scrapers working
   ```bash
   curl http://localhost:8000/api/v1/scrapers/status
   ```

2. ✅ **Run First Scrape** - Manually trigger
   ```bash
   curl -X POST http://localhost:8000/api/v1/scrapers/run
   ```

3. ✅ **View Results** - See scraped articles
   ```bash
   curl http://localhost:8000/api/v1/unified/articles
   ```

4. ✅ **Generate Reports** - Create unified analysis
   ```bash
   curl http://localhost:8000/api/v1/unified/report
   ```

5. ✅ **Configure Custom Sites** - Add more sources as needed

---

## See Also

- `THINK_TANK_SYSTEM.md` - Complete Think Tank reference
- `THINK_TANK_QUICK_START.md` - 15-minute setup guide
- `zimbabwe.yaml` - Full configuration reference