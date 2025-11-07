# Web Scraper & Unified Analysis - Quick Reference

## 🚀 5-Minute Start

### Step 1: Verify Dependencies
```bash
python -c "import bs4, aiohttp; print('✅ Ready')"
```

### Step 2: Create Tables
```bash
python -c "from src.db.models import Base, ScrapedArticle, ContentDuplicate, WebScraperConfig; Base.metadata.create_all()"
```

### Step 3: Run System
```bash
python main.py
```

### Step 4: Trigger Scraper
```bash
curl -X POST http://localhost:8000/api/v1/scrapers/run
```

### Step 5: View Results
```bash
curl http://localhost:8000/api/v1/unified/articles | head -20
```

**Done!** You're now scraping 9 news sites.

---

## 📡 What's Being Scraped (Pre-Configured)

```
Zimbabwe Local (Every 1 hour)
├─ Herald              (herald.co.zw)
├─ NewsDay             (newsday.co.zw)
├─ Bulawayo24          (bulawayo24.com)
└─ Zimbabwean          (thezimbabwean.co.uk)

African Regional (Every 2 hours)
├─ AllAfrica           (allafrica.com/zimbabwe)
└─ Mail & Guardian     (mg.co.za/africa)

International (Every 3 hours)
├─ BBC Africa          (bbc.com/news/world/africa)
├─ Reuters             (reuters.com/world/africa)
└─ Al Jazeera          (aljazeera.com/news)

Social Media (Every 30 minutes)
└─ 6 Influencers on Twitter, Facebook, Instagram
```

---

## 🔧 Common Configuration Changes

### Change Scrape Interval

```yaml
# zimbabwe.yaml
think_tank:
  web_scraper:
    scrape_interval: 60  # Minutes between scrapes
```

### Enable Only Specific Categories

```yaml
think_tank:
  web_scraper:
    sites:
      zimbabwe_local:
        enabled: true
      regional_african:
        enabled: false  # Skip this
      international:
        enabled: false  # Skip this
```

### Stricter Duplicate Detection

```yaml
think_tank:
  web_scraper:
    duplicate_detection:
      similarity_threshold: 0.85  # More strict
```

### Skip Low-Relevance Articles

```yaml
think_tank:
  web_scraper:
    min_relevance_score: 0.7  # Only keep 70%+ relevant
```

---

## 📊 API Endpoints - Cheat Sheet

### Scraper Control
```bash
# See scraper status
curl http://localhost:8000/api/v1/scrapers/status

# Run scrapers now
curl -X POST http://localhost:8000/api/v1/scrapers/run

# Get scraper configs
curl http://localhost:8000/api/v1/scrapers/config
```

### View Content
```bash
# All articles (unified)
curl http://localhost:8000/api/v1/unified/articles

# By source type
curl "http://localhost:8000/api/v1/unified/articles?source=scraped"
curl "http://localhost:8000/api/v1/unified/articles?source=social"

# By date
curl "http://localhost:8000/api/v1/unified/articles?days=7"

# Search
curl "http://localhost:8000/api/v1/unified/articles?search=economy"
```

### Duplicates
```bash
# List duplicates
curl http://localhost:8000/api/v1/duplicates

# Get details
curl http://localhost:8000/api/v1/duplicates/canonical/{id}

# Mark resolved
curl -X POST http://localhost:8000/api/v1/duplicates/resolve
```

### Analysis
```bash
# Trends
curl http://localhost:8000/api/v1/unified/trends

# Comprehensive report
curl http://localhost:8000/api/v1/unified/report

# By topic
curl "http://localhost:8000/api/v1/unified/trends?topic=economy"

# By politician
curl "http://localhost:8000/api/v1/unified/articles?politician=mnangagwa"
```

---

## 🎯 Common Tasks

### Get Latest News (All Sources)
```bash
curl "http://localhost:8000/api/v1/unified/articles?days=1" | jq '.[] | {title, source_type, published_date}'
```

### Find Economy Articles
```bash
curl "http://localhost:8000/api/v1/unified/articles?search=economy" | jq '.[] | {title, source}'
```

### See What's Trending
```bash
curl http://localhost:8000/api/v1/unified/trends | jq '.top_keywords'
```

### Check Article Duplicates
```bash
curl http://localhost:8000/api/v1/duplicates | jq '.[] | {canonical_id, related_id, similarity: .title_similarity}'
```

### Social Media with High Engagement
```bash
curl "http://localhost:8000/api/v1/unified/articles?source=social&min_engagement=100"
```

### Generate Comprehensive Report
```bash
curl http://localhost:8000/api/v1/unified/report > report.txt && cat report.txt
```

---

## 🔍 Troubleshooting Quick Fixes

### "No scraped articles found"
```yaml
# Solution: Check interval
think_tank:
  web_scraper:
    scrape_interval: 60  # Was 120, now every hour

# Then wait 1+ hours or manually trigger:
curl -X POST http://localhost:8000/api/v1/scrapers/run
```

### "Too many duplicates"
```yaml
# Solution: Increase threshold
think_tank:
  web_scraper:
    duplicate_detection:
      similarity_threshold: 0.85  # Was 0.75
```

### "Articles disappear"
```yaml
# Solution: Check relevance threshold
think_tank:
  web_scraper:
    min_relevance_score: 0.3  # Was 0.5, now more permissive
```

### "Scraper too slow"
```yaml
# Solution 1: Reduce max articles
think_tank:
  web_scraper:
    max_articles_per_site: 20  # Was 50

# Solution 2: Skip international
think_tank:
  web_scraper:
    sites:
      international:
        enabled: false
```

---

## 📋 Database Queries

### See Scraped Articles
```sql
SELECT title, source_site, published_date FROM scraped_articles LIMIT 10;
```

### Count by Source
```sql
SELECT source_site, COUNT(*) as count FROM scraped_articles GROUP BY source_site;
```

### Find Duplicates
```sql
SELECT * FROM content_duplicates WHERE duplicate_type = 'exact';
```

### Articles with High Engagement (Social)
```sql
SELECT author_username, text, engagement_metrics 
FROM social_media_posts 
WHERE (engagement_metrics->>'likes')::int > 100;
```

### Latest from Each Source
```sql
SELECT DISTINCT source_site, MAX(published_date) 
FROM scraped_articles 
GROUP BY source_site;
```

---

## 🚀 Add Custom News Site (30 seconds)

### 1. Add to config
```yaml
think_tank:
  web_scraper:
    sites:
      zimbabwe_local:
        sites_to_scrape:
          - herald
          - newsday
          - mynewsite  # ← ADD HERE
```

### 2. Add extractor config
```python
# In src/services/web_scraper.py

DEFAULT_CONFIGS = {
    # ... existing ...
    "mynewsite": {
        "site_name": "My News Site",
        "site_url": "https://mynewsite.com",
        "source_category": "zimbabwe_local",
        "article_selector": "article, div.post",
        "title_selector": "h2",
        "content_selector": "div.content",
        "author_selector": "span.author",
        "date_selector": "time",
        "image_selector": "img",
        "scrape_interval_minutes": 60,
    }
}
```

### 3. Done! 
Next scrape will include your site.

---

## 📊 Data Structure

### Unified Article Object
```json
{
  "id": "uuid",
  "source_type": "rss|scraped|social_media",
  "title": "Article title",
  "content": "Article content",
  "url": "https://...",
  "source": "source name",
  "published_date": "2024-02-15T10:30:00",
  "sentiment": "positive|negative|neutral",
  "relevance_score": 0.85,
  "entities": {
    "politicians": ["Mnangagwa", "Chamisa"],
    "organizations": ["Government", "Opposition"],
    "locations": ["Harare", "Zimbabwe"]
  },
  "keywords": ["election", "politics"],
  "engagement": {
    "likes": 150,
    "retweets": 45,
    "comments": 23
  }
}
```

### Duplicate Record
```json
{
  "canonical_article_id": "uuid1",
  "related_article_id": "uuid2",
  "title_similarity": 0.92,
  "content_similarity": 0.88,
  "duplicate_type": "near_duplicate",
  "detected_date": "2024-02-15T10:30:00"
}
```

---

## ⏱️ Processing Timeline

```
10:00 AM
├─ RSS Feeds checked   → ~50 articles
├─ Social Media checked → ~12 posts
├─ Web Scrapers run    → ~45 articles
└─ Duplicates detected → 15 duplicates

10:15 AM - Articles normalized & analyzed
10:25 AM - Trends calculated & stored
10:30 AM - Articles available via API
```

---

## 🎯 Monitoring Commands

### Check System Health
```bash
# See what's in database
curl http://localhost:8000/api/v1/unified/articles | jq '.[] | .source_type' | sort | uniq -c

# See latest scrape time
curl http://localhost:8000/api/v1/scrapers/status | jq '.[] | {site: .site_name, last_scrape: .last_scrape_date}'
```

### Monitor Performance
```bash
# Count articles per source type
curl http://localhost:8000/api/v1/unified/trends | jq '.source_distribution'

# See sentiment breakdown
curl http://localhost:8000/api/v1/unified/trends | jq '.sentiment_distribution'
```

---

## 📚 Documentation Links

- **Complete Guide:** `CONTENT_AGGREGATION_GUIDE.md`
- **Architecture:** `ENHANCED_THINK_TANK_DELIVERY.md`
- **Features:** `COMPLETE_SYSTEM_FEATURES.md`
- **Think Tank:** `THINK_TANK_SYSTEM.md`
- **Quick Start:** `THINK_TANK_QUICK_START.md`
- **Config:** `zimbabwe.yaml`

---

## 💡 Pro Tips

### Tip 1: Warm Start
On first run, manually trigger scraper:
```bash
curl -X POST http://localhost:8000/api/v1/scrapers/run
```
Wait a few seconds to see results instead of waiting for auto-schedule.

### Tip 2: Monitor Duplicates
High duplicates = threshold too low. Adjust:
```bash
# In logs or dashboard, if seeing >20% duplicates:
# Increase threshold from 0.75 to 0.85
```

### Tip 3: Relevance Tuning
Too many irrelevant articles? Increase:
```yaml
min_relevance_score: 0.7  # More strict
```

### Tip 4: Peak Times
Deploy during low-traffic times:
- Scraping: Every 1-3 hours (not always)
- Analysis: Once daily (midnight)
- Articles: On-demand via API

### Tip 5: Duplicate Investigation
Find why articles are duplicated:
```bash
curl http://localhost:8000/api/v1/duplicates/{id} | jq '.[] | {canonical: .canonical_article_id, related: .related_article_id, titles: [.title1, .title2]}'
```

---

## ✅ Verification Checklist

- [ ] Scrapers configured in `zimbabwe.yaml`
- [ ] Database tables created (`Base.metadata.create_all()`)
- [ ] System started (`python main.py`)
- [ ] Scraper triggered (`curl -X POST .../scrapers/run`)
- [ ] Articles retrieved (`curl .../unified/articles`)
- [ ] Duplicates detected (`curl .../duplicates`)
- [ ] Trends analyzed (`curl .../unified/trends`)
- [ ] Report generated (`curl .../unified/report`)

---

**Everything you need to run the content aggregation system!** 🚀

For detailed information, see `CONTENT_AGGREGATION_GUIDE.md`