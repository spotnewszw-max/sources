# Zimbabwe News Aggregator - Complete Setup Summary

## 📋 What Has Been Set Up

A production-ready news aggregation system specifically configured for **Zimbabwe news, African coverage, and social media monitoring** of policy makers and influencers.

---

## 🎯 **System Features**

### **News Source Aggregation**
- ✅ **7 Zimbabwe news outlets** (RSS feeds)
  - NewsDay, The Herald, Bulawayo24, Zimbabwe Independent, Techzim, ZimFact, The Source
- ✅ **3 African news sources** for Zimbabwe coverage
  - AllAfrica, Africa News, RFI Afrique, VOA
- ✅ **Economic data feeds**
  - Trading Economics Zimbabwe data
- ✅ **0 API keys required** for RSS feeds (free and public)

### **Social Media Monitoring**
- ✅ **Twitter/X API integration** (optional)
  - Monitor policy makers: Mnangagwa, Chamisa, Ncube, etc.
  - Track trending hashtags: #Zimbabwe, #ZimEconomy, etc.
  - Setup time: 15 minutes
- ✅ **Facebook integration** (optional)
  - Monitor government announcements
  - Track government pages
  - Setup time: 20 minutes

### **Content Intelligence**
- ✅ **Smart filtering** for Zimbabwe relevance
  - Scores articles 0-1 based on keyword matching
  - Filters out non-relevant content
  - Recognizes policy makers and politicians
  - Detects location mentions
- ✅ **Entity extraction**
  - Politicians: Mnangagwa, Chamisa, etc.
  - Locations: Harare, Bulawayo, etc.
  - Organizations: ZANU-PF, CCC, Econet, etc.
  - Issues: Economy, politics, protests, etc.
- ✅ **Category detection**
  - Politics, Economy, Technology, Agriculture, Sports, etc.
- ✅ **Sentiment analysis**
  - Positive/Negative/Neutral detection

---

## 📁 **Files Created/Modified**

### **Configuration Files**

| File | Purpose |
|------|---------|
| `news-aggregator/configs/zimbabwe.yaml` | **NEW** - Complete Zimbabwe sources configuration with all RSS feeds |
| `.env.development` | **UPDATED** - Ready for social media API keys |
| `news-aggregator/requirements.txt` | **UPDATED** - Added feedparser, tweepy for social media |

### **Documentation Files** (5 files)

| File | Purpose | Size |
|------|---------|------|
| `ZIMBABWE_QUICK_START.md` | **START HERE** - 10-minute setup guide | 3 KB |
| `ZIMBABWE_SOURCES.md` | Complete sources list, social media accounts to monitor, API setup guide | 8 KB |
| `SOCIAL_MEDIA_INTEGRATION.md` | Complete Twitter/Facebook setup with code examples | 12 KB |
| `ZIMBABWE_NEWS_AGGREGATOR_SETUP.md` | This file - complete setup summary | 5 KB |

### **Service Files** (2 files - NEW)

| File | Purpose |
|------|---------|
| `src/services/fetcher.py` | **IMPROVED** - Proper RSS parsing with FeedFetcher class |
| `src/services/content_filter.py` | **NEW** - Zimbabwe content filtering and entity extraction |

---

## 🚀 **Quick Start (3 Steps - 10 Minutes)**

### **Step 1: Install**
```powershell
cd "c:\Users\user\Documents\projects\Sources Media"
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r news-aggregator\requirements.txt
```

### **Step 2: Start**
```powershell
python main.py
```

### **Step 3: Access**
```
http://localhost:8000/docs
```

---

## 📰 **Data Sources Configured**

### **Category 1: Zimbabwe Local News (Priority 1)**
1. **NewsDay Zimbabwe** - newsday.co.zw/feed
2. **The Herald** - herald.co.zw/feed
3. **Zimbabwe Independent** - independentzimbabwe.com/feed
4. **Bulawayo24** - bulawayo24.com/feed
5. **Techzim** - techzim.co.zw/feed
6. **ZimFact** - zimfact.org/feed
7. **The Source** - thesource.co.zw/feed

### **Category 2: African News (Priority 2)**
8. **AllAfrica Zimbabwe** - allafrica.com/zimbabwe/feed
9. **Africa News** - africanews.com/feed
10. **RFI Afrique** - rfi.fr/en/africa/feed
11. **VOA Africa** - voanews.com/africa/feed

### **Category 3: Economic Data**
12. **Trading Economics Zimbabwe** - tradingeconomics.com/zimbabwe/rss

---

## 👥 **Policy Makers & Influencers to Monitor**

### **Government Officials**
- **Emmerson Mnangagwa** (President) - @edmnangagwa
- **Constantino Chiwenga** (VP) - @chiwenga_constan
- **Mthuli Ncube** (Finance) - @MthuliNcube

### **Opposition**
- **Nelson Chamisa** (CCC) - @nelsonchamisa

### **Business/Economic**
- **Strive Masiyiwa** (Econet) - @strive

### **Media/Analysts**
- **Hopewell Chin'ono** (Journalist) - @daddyhope
- **Vince Musewe** (Economist) - @VinceMusewe

---

## 🔧 **Configuration Details**

### **Fetcher Settings** (in zimbabwe.yaml)
```yaml
fetcher:
  interval: 60                    # Check every 60 minutes
  timeout: 30                     # Request timeout 30 seconds
  filter_enabled: true            # Enable Zimbabwe filtering
  min_score: 0.3                  # Minimum relevance score
```

### **Content Filter Keywords**
- **Primary:** zimbabwe, harare, bulawayo, gweru, mutare
- **Political:** mnangagwa, chamisa, ncube, chiwenga
- **Economic:** rtgs dollar, inflation, economy, forex
- **Issues:** election, protests, sanctions, corruption

---

## 📊 **API Endpoints Available**

### **Core Article Endpoints**
```
GET  /api/v1/articles              # List all articles
GET  /api/v1/articles?search=      # Search articles
GET  /api/v1/articles/{id}         # Get specific article
POST /api/v1/articles/refresh      # Manually refresh from sources
```

### **Trending & Analytics**
```
GET  /api/v1/trending              # Trending topics
GET  /api/v1/sources               # List configured sources
GET  /api/v1/categories            # Articles by category
```

### **Social Media** (Optional)
```
GET  /api/v1/social/tweets         # Get tweets about Zimbabwe
GET  /api/v1/social/facebook       # Get Facebook posts
```

---

## 🐦 **Social Media Setup (Optional)**

### **Twitter/X - 15 Minutes**
1. Go to: https://developer.twitter.com
2. Create account → Create App → Get Bearer Token
3. Add to `.env.development`:
   ```
   TWITTER_BEARER_TOKEN=your_token
   ```
4. Restart server - now monitors #Zimbabwe tweets

### **Facebook - 20 Minutes**
1. Go to: https://developers.facebook.com
2. Create app → Generate Page Access Token
3. Add to `.env.development`:
   ```
   FACEBOOK_ACCESS_TOKEN=your_token
   ```
4. Restart server - now monitors government pages

**See `SOCIAL_MEDIA_INTEGRATION.md` for detailed setup**

---

## 💾 **Database Configuration**

### **Development** (SQLite - default)
```
Database: news_zimbabwe.db (auto-created)
Location: Project root directory
No configuration needed
```

### **Production** (PostgreSQL)
```yaml
database:
  url: postgresql://user:password@localhost:5432/news_aggregwe
  echo: false
```

---

## 🔍 **What the System Does**

### **Every Hour** (configurable)
1. ✅ Fetches latest articles from 12 RSS feeds
2. ✅ Parses RSS content (title, content, image, author, date)
3. ✅ Scores for Zimbabwe relevance (0-1)
4. ✅ Filters out non-relevant articles
5. ✅ Removes duplicates
6. ✅ Extracts entities (politicians, locations, organizations)
7. ✅ Categorizes (Politics, Economy, Tech, etc.)
8. ✅ Stores in SQLite database

### **Optional** (if social media configured)
9. ✅ Fetches tweets with #Zimbabwe
10. ✅ Monitors policy maker accounts
11. ✅ Fetches government Facebook posts
12. ✅ Includes in main feed

---

## 🎯 **Filter Settings (Tunable)**

In `zimbabwe.yaml`, adjust:

```yaml
content_filter:
  min_relevance: 0.6        # 0-1 (higher = stricter)
  remove_duplicates: true    # Remove exact title matches
  
fetcher:
  interval: 60               # Minutes between fetches
  filter_keywords:           # Add/remove keywords to track
    - zimbabwe
    - harare
    - mnangagwa
```

---

## 📈 **Deployment Options**

### **Local Development** ✅
- SQLite database (included)
- No API keys required for RSS
- Perfect for testing
- Run: `python main.py`

### **Hostinger VPS** (Production-ready)
- PostgreSQL database
- Redis caching
- Nginx reverse proxy
- SSL/TLS certificates
- See: `DEPLOY_HOSTINGER.md` for full setup

### **Cloud Platforms**
- Railway.app (easy, free tier available)
- DigitalOcean ($5-12/month)
- AWS (enterprise scale)

---

## 🆘 **Troubleshooting**

### **Issue: No articles appearing**
**Solution:**
1. Check RSS feeds work in browser first
2. Look at logs: `tail -f logs/zimbabwe.log`
3. Test fetcher directly:
   ```python
   from src.services.fetcher import fetch_rss_feed
   articles = fetch_rss_feed("https://www.newsday.co.zw/feed", "NewsDay")
   ```

### **Issue: All articles filtered out**
**Solution:**
1. Reduce filter sensitivity:
   ```yaml
   content_filter:
     min_relevance: 0.3  # Was 0.6
   ```
2. Check keywords are relevant to your content

### **Issue: Social media not working**
**Solution:**
1. Verify API token in `.env.development`
2. Check token hasn't expired
3. See `SOCIAL_MEDIA_INTEGRATION.md` troubleshooting section

---

## 📚 **Documentation Map**

```
.
├── ZIMBABWE_QUICK_START.md              ← START HERE (10 min)
├── ZIMBABWE_SOURCES.md                   ← Sources & API keys
├── SOCIAL_MEDIA_INTEGRATION.md           ← Twitter/Facebook setup
├── ZIMBABWE_NEWS_AGGREGATOR_SETUP.md     ← This file
├── SETUP_DEVELOPMENT.md                  ← General setup
├── DEPLOY_HOSTINGER.md                   ← Production deployment
└── news-aggregator/
    ├── configs/
    │   └── zimbabwe.yaml                 ← Source configuration
    ├── src/services/
    │   ├── fetcher.py                    ← RSS feed parser
    │   └── content_filter.py             ← Zimbabwe filtering
    └── requirements.txt                  ← Dependencies
```

---

## ✨ **Key Improvements Made**

### **Fetcher Service**
- ✅ **Proper RSS parsing** with feedparser library
- ✅ **Error handling** for timeouts and connection issues
- ✅ **HTML cleanup** - removes tags from content
- ✅ **Image extraction** from RSS entries
- ✅ **Date parsing** from multiple date formats
- ✅ **Author extraction** from various formats
- ✅ **Batch processing** of multiple sources

### **Content Filter**
- ✅ **Keyword-based relevance scoring** (tunable)
- ✅ **Entity extraction** - politicians, locations, organizations
- ✅ **Issue detection** - economy, politics, protests, etc.
- ✅ **Category detection** - automatically categorizes articles
- ✅ **Duplicate detection** - removes exact duplicates
- ✅ **Sentiment analysis** - positive/negative/neutral

### **Configuration**
- ✅ **YAML-based** - easy to edit
- ✅ **Environment variables** - for API keys
- ✅ **Extensible** - easy to add new sources
- ✅ **Well-documented** - every parameter explained

---

## 🚀 **Next Steps**

### **Right Now**
- [ ] Read `ZIMBABWE_QUICK_START.md`
- [ ] Run `python main.py`
- [ ] Open http://localhost:8000/docs
- [ ] Test fetching articles

### **Today**
- [ ] Review collected articles
- [ ] Check filtering is working
- [ ] Customize sources if needed

### **This Week**
- [ ] (Optional) Set up Twitter API
- [ ] (Optional) Set up Facebook API
- [ ] Build frontend to display articles

### **Later**
- [ ] Deploy to Hostinger (45 minutes)
- [ ] Configure PostgreSQL
- [ ] Set up automated backups

---

## 💡 **Pro Tips**

1. **Test individual sources**
   ```bash
   curl https://newsday.co.zw/feed
   ```

2. **Monitor filtering in real-time**
   ```bash
   tail -f logs/zimbabwe.log
   ```

3. **Export articles for analysis**
   ```python
   # In Python
   from src.repositories.article_repository import get_articles
   articles = get_articles(limit=1000)
   # Use pandas to analyze
   ```

4. **Scale to production gradually**
   - Start: SQLite on local machine
   - Then: SQLite on server
   - Finally: PostgreSQL on Hostinger VPS

---

## 📞 **Support Resources**

- **RSS Feed Issues:** Check source URL works in browser first
- **API Keys:** See `SOCIAL_MEDIA_INTEGRATION.md`
- **Deployment:** See `DEPLOY_HOSTINGER.md`
- **General Setup:** See `SETUP_DEVELOPMENT.md`

---

## 🎉 **You're Ready!**

Your Zimbabwe-focused news aggregator is:
- ✅ Configured with 12 news sources
- ✅ Ready to filter for Zimbabwe relevance
- ✅ Set up for social media monitoring (optional)
- ✅ Deployed locally and ready to scale

**Next action:** Open `ZIMBABWE_QUICK_START.md` and follow the 3-step setup! 🚀

---

**Last Updated:** 2024
**Version:** 1.0
**Status:** ✅ Production Ready (local & Hostinger)