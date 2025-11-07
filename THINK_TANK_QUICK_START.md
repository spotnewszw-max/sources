# 🧠 Think Tank System - Quick Start (15 Minutes)

## What You'll Have After This

✅ Social media posts captured from 7 Zimbabwe influencers  
✅ OCR text extraction from screenshots  
✅ Automatic article generation (historical, present, future)  
✅ Publication queue with smart flagging  
✅ Trend analysis dashboard  

---

## 🚀 Setup (5 Minutes)

### 1. Install Dependencies

```powershell
cd "c:\Users\user\Documents\projects\Sources Media"

# Install screenshot & OCR tools
pip install selenium pytesseract pillow

# Download Tesseract OCR (for text extraction)
choco install tesseract

# If Tesseract install fails, download from:
# https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. Configure Influencers

Open `news-aggregator/configs/zimbabwe.yaml` and add this at the end:

```yaml
think_tank:
  enabled: true
  article_generation:
    auto_publish: true
    confidence_threshold: 0.65

social_media:
  enabled: true
  capture_interval: 30
  
  influencers:
    twitter:
      - "edmnangagwa"      # President
      - "nelsonchamisa"    # Opposition Leader
      - "MthuliNcube"      # Finance Minister
      - "strive"           # Entrepreneur
      - "daddyhope"        # Journalist
      - "VinceMusewe"      # Economist
    
    facebook:
      - "GovernmentZW"
```

### 3. Start the System

```powershell
python main.py

# System will start capturing posts in background
# Check every 30 minutes
```

---

## 📊 Using the System (10 Minutes)

### Access Dashboard

Open: `http://localhost:8000/docs`

### 1. Capture Social Media Posts

```bash
POST /api/think-tank/capture-social-media

# Response: "Captured 15 posts from influencers"
```

**What it captures:**
- Posts from all configured influencers
- Screenshots of each post
- OCR extracted text from images
- Engagement metrics (likes, retweets)
- Sentiment (positive/negative/neutral)

### 2. View Captured Posts

```bash
GET /api/think-tank/social-media-posts

# Returns: All captured posts with full details
```

### 3. Generate Articles

```bash
POST /api/think-tank/generate-article

Body:
{
  "topic": "Zimbabwe Elections 2025",
  "article_type": "future",
  "days_window": 90
}

# Response: "Article generation started"
```

**Three article types:**

1. **Historical** - "How did we get here?"
   - Rewrite history with full context
   - Timeline of events
   - Key turning points
   - Evolution of the issue

2. **Present** - "What's happening now?"
   - Current situation analysis
   - Who's involved (stakeholders)
   - Current challenges
   - Recent developments
   - Sentiment analysis

3. **Future** - "What will happen?"
   - Predictions based on trends
   - Possible scenarios
   - Risk analysis
   - Opportunities
   - Recommendations

### 4. View Generated Articles

```bash
GET /api/think-tank/generated-articles

# Returns list of all generated articles
```

### 5. Check Publication Queue

```bash
GET /api/think-tank/publication-queue

# Returns articles flagged for review
```

**Confidence levels:**
- ✅ **HIGH (>80%)** → Auto-published
- ⚠️ **MEDIUM (65-80%)** → Flagged for optional review
- ❌ **LOW (<65%)** → Requires human review

### 6. Approve/Reject Articles

```bash
# Approve for publishing
POST /api/think-tank/publication-queue/{article_id}/approve

# Reject for revision
POST /api/think-tank/publication-queue/{article_id}/reject
Body: { "reason": "Needs more data" }
```

### 7. View Trends

```bash
GET /api/think-tank/trends?window_days=30

# Returns:
# - Top topics (Politics, Economy, etc.)
# - Top politicians mentioned
# - Sentiment distribution
# - Trending keywords
```

### 8. Get Dashboard Summary

```bash
GET /api/think-tank/dashboard/summary

# Returns overview of all activity
```

---

## 📸 What Gets Captured

### From Social Media Posts

```json
{
  "platform": "twitter",
  "author": "edmnangagwa",
  "text": "Zimbabwe's economy shows signs of recovery...",
  "screenshot": "screenshots/twitter_edmnangagwa_0.png",
  "extracted_text": "[OCR'd text from image]",
  "sentiment": "positive",
  "engagement": {
    "likes": 5432,
    "retweets": 1200,
    "replies": 342
  },
  "topics": ["Politics", "Economy"],
  "mentioned_politicians": ["Emmerson Mnangagwa"]
}
```

### Generated Articles Include

Each article contains:
- ✅ Full analysis text
- ✅ Multiple sections (overview, analysis, recommendations)
- ✅ Confidence score
- ✅ Supporting data and analysis
- ✅ Links to source materials
- ✅ Publication status and review notes

---

## 🎯 Example Workflow

```
1. 09:00 - Capture posts from influencers
   └─ 15 posts captured, OCR extracted

2. 09:15 - Analyze trends
   └─ Top topics: Politics (245 mentions), Economy (189 mentions)

3. 09:30 - Generate articles
   └─ Historical: "Zimbabwe Economic Crisis Timeline"
   └─ Present: "Current Economy Situation Jan 2024"
   └─ Future: "Economy Forecast Next 90 Days"

4. 09:45 - Review & publish
   └─ High confidence (85%) → Auto-publish
   └─ Medium confidence (68%) → Flag for review
   └─ Low confidence (42%) → Require human review

5. 10:00 - Dashboard shows results
   └─ 3 new articles
   └─ 12 pending review
   └─ 2 published today
```

---

## 🔄 Automated Workflow

```
Every 30 minutes:
  ✓ Capture new posts from influencers
  ✓ Extract text with OCR
  ✓ Analyze sentiment & topics
  ✓ Update trends

Every day (at midnight):
  ✓ Generate historical analysis (if new major event)
  ✓ Generate present analysis
  ✓ Generate future predictions
  ✓ Flag uncertain articles for review
  ✓ Auto-publish high confidence articles

Every week:
  ✓ Validate past predictions
  ✓ Calculate accuracy metrics
  ✓ Generate weekly summary report
```

---

## 📱 Key Features

| Feature | What It Does |
|---------|-------------|
| **Screenshot Capture** | Auto-saves posts from influencers every 30 min |
| **OCR Text Extraction** | Extracts text from images for analysis |
| **Sentiment Analysis** | Detects if posts are positive/negative |
| **Entity Recognition** | Identifies politicians, organizations, topics |
| **Trend Detection** | Finds what topics are trending |
| **Article Generation** | Creates 3 types of analysis articles |
| **Confidence Scoring** | Rates how sure predictions are |
| **Publication Queue** | Review workflow before publishing |
| **Prediction Tracking** | Measures accuracy over time |
| **Dashboard** | See everything in one place |

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Tesseract not found" | `choco install tesseract` |
| "Chrome not found" | Install Google Chrome |
| "Posts not capturing" | Check influencer usernames in config |
| "No articles generated" | Wait 30 min for posts, then check for errors |
| "Low confidence scores" | System is being conservative - that's good! |

---

## 📈 What Changes Next?

**Hourly (every 30 min):**
- New social media posts captured
- Sentiment updated
- Articles may regenerate if trends change

**Daily:**
- New analysis articles auto-generated
- Publication queue updated
- Dashboard metrics refreshed

**Weekly:**
- Prediction accuracy calculated
- System learning improved
- Summary report generated

---

## 🎉 Success Indicators

After 1 hour, you should see:
- ✅ Posts captured in `screenshots/` folder
- ✅ Extracted text in database
- ✅ First generated articles appearing
- ✅ Dashboard showing activity

After 1 day, you should see:
- ✅ Multiple articles generated
- ✅ Publication queue with articles
- ✅ Clear trends identified
- ✅ Prediction data appearing

After 1 week, you should see:
- ✅ Accurate trend predictions
- ✅ Growing database of articles
- ✅ Prediction accuracy metrics
- ✅ Pattern recognition working

---

## 🚀 Next Steps

1. **Let it run for 24 hours** - More data = better analysis
2. **Review generated articles** - Check publication queue
3. **Tweak influencer list** - Add/remove accounts as needed
4. **Customize templates** - Adjust article generation
5. **Monitor accuracy** - Track prediction results

---

## 📚 Full Documentation

For detailed information, see: `THINK_TANK_SYSTEM.md`

Contains:
- Complete API reference
- Configuration options
- Advanced usage
- Custom analysis
- Data storage details

---

## ✨ Your Think Tank is Ready!

The system is now:
- ✅ Capturing posts automatically
- ✅ Extracting text with OCR
- ✅ Analyzing trends
- ✅ Generating articles
- ✅ Publishing with smart review

**All happening automatically in the background!** 🚀

Access it anytime at: `http://localhost:8000/docs`

---

**Questions?** Check `THINK_TANK_SYSTEM.md` for full documentation.