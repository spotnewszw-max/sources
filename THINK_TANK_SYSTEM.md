# 🧠 Think Tank System - Complete Setup & Usage Guide

## Overview

The **Think Tank System** transforms your news aggregator into an intelligent analysis platform that:

✅ **Captures** social media posts from politicians, journalists, and influencers  
✅ **Extracts** text and images from screenshots using OCR  
✅ **Analyzes** trends, patterns, and events across 100% of your collected data  
✅ **Generates** three types of original articles:
  - **Historical Analysis** - Rewrite history with full context
  - **Present Analysis** - Current situation with stakeholder positions
  - **Future Predictions** - Forecast outcomes based on trends  
✅ **Publishes** with automatic review flagging for uncertain articles  

---

## 🎯 System Architecture

```
Social Media Influencers
    ↓
Screenshot Capture (Auto every 30 min)
    ↓
OCR Text Extraction + Image Storage
    ↓
Content Analysis Engine
    │
    ├→ Trend Detection
    ├→ Entity Extraction (Politicians, Organizations, Topics)
    ├→ Sentiment Analysis
    └→ Pattern Recognition
    ↓
Think Tank Analysis
    │
    ├→ Historical Context Builder
    ├→ Present Situation Analyzer
    └→ Future Prediction Engine
    ↓
Article Generator (Hybrid: Template + LLM)
    ↓
Publication Queue
    │
    ├→ Auto-publish (High confidence)
    └→ Flag for Review (Uncertain/Controversial)
    ↓
Published Articles Database
```

---

## 🚀 Quick Start (20 Minutes)

### Step 1: Install Additional Dependencies

```powershell
cd "c:\Users\user\Documents\projects\Sources Media"

# Install screenshot and OCR dependencies
pip install selenium pytesseract pillow

# Download Tesseract OCR (required for text extraction)
# Option A: Chocolatey (if installed)
choco install tesseract

# Option B: Download from GitHub
# https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR
```

### Step 2: Configure Influencers to Monitor

Edit `news-aggregator/configs/zimbabwe.yaml` and add:

```yaml
social_media:
  # Enable social media capture
  enabled: true
  
  # Screenshot capture interval in minutes
  capture_interval: 30
  
  influencers:
    twitter:
      - "edmnangagwa"        # President Emmerson Mnangagwa
      - "nelsonchamisa"      # Opposition Leader Nelson Chamisa
      - "MthuliNcube"        # Finance Minister Mthuli Ncube
      - "strive"             # Strive Masiyiwa (Entrepreneur)
      - "daddyhope"          # Hopewell Chin'ono (Journalist)
      - "VinceMusewe"        # Vince Musewe (Economist)
    
    facebook:
      - "GovernmentZW"       # Government of Zimbabwe
      - "ZimbabweIndependent"
      - "NewsDay.co.zw"
    
    instagram:
      - "emmersonmn"
```

### Step 3: Start the Think Tank System

```powershell
# In your project directory
python main.py

# The system will:
# 1. Start capturing social media posts every 30 minutes
# 2. Extract text from screenshots using OCR
# 3. Analyze content automatically
# 4. Generate articles based on trends
```

### Step 4: Access the Dashboard

Open your browser and go to:
```
http://localhost:8000/docs
```

Navigate to `/api/think-tank` endpoints to:
- View captured posts
- Analyze trends
- Generate articles
- View publication queue

---

## 📸 Screenshot Capture System

### How It Works

1. **Automatic Capture** - Every 30 minutes (configurable)
2. **OCR Processing** - Extract text from images
3. **Media Storage** - Save images locally
4. **Engagement Metrics** - Track likes, retweets, shares
5. **Context Preservation** - Store full post context

### Captured Data

Each captured post includes:

```json
{
  "id": "post_uuid",
  "platform": "twitter",
  "author_username": "edmnangagwa",
  "text": "Full post text",
  "screenshot_path": "screenshots/twitter_edmnangagwa_0_timestamp.png",
  "extracted_text": "OCR'd text from image",
  "media_urls": ["https://...image1.jpg", "https://...image2.jpg"],
  "posted_date": "2024-01-15T10:30:00Z",
  "captured_date": "2024-01-15T10:35:00Z",
  "sentiment": "positive",
  "engagement_metrics": {
    "likes": 5432,
    "retweets": 1200,
    "replies": 342
  },
  "mentioned_politicians": ["Emmerson Mnangagwa"],
  "mentioned_topics": ["Politics", "Economy"]
}
```

### API: Capture Social Media Posts

```bash
POST /api/think-tank/capture-social-media
Query Parameters:
  - platforms: ["twitter", "facebook", "instagram"]
  - run_background: boolean (default: true)

Response:
{
  "message": "Social media posts captured",
  "total_posts": 15,
  "breakdown": {
    "twitter": 8,
    "facebook": 5,
    "instagram": 2
  }
}
```

### Configuration Options

```yaml
social_media:
  # Capture settings
  capture_interval: 30              # Minutes between captures
  max_posts_per_influencer: 10      # Posts to capture per check
  
  # Storage
  storage_path: "screenshots"
  download_media: true              # Download images locally
  
  # OCR settings
  ocr_enabled: true
  ocr_language: "eng"               # Language for text extraction
  
  # Analysis
  extract_entities: true
  analyze_sentiment: true
  extract_engagement: true
```

---

## 🧠 Think Tank Analysis Engine

### What It Analyzes

#### 1. **Trend Detection**
```python
{
  "period": "30 days",
  "top_topics": [
    {"topic": "Politics", "mentions": 245, "sentiment": "mixed"},
    {"topic": "Economy", "mentions": 189, "sentiment": "negative"},
    {"topic": "Technology", "mentions": 87, "sentiment": "positive"}
  ],
  "top_politicians": [
    {"name": "Emmerson Mnangagwa", "mentions": 156, "sentiment": "neutral"},
    {"name": "Nelson Chamisa", "mentions": 134, "sentiment": "mixed"}
  ]
}
```

#### 2. **Entity Extraction**
Automatically identifies:
- **Politicians** (Mnangagwa, Chamisa, Ncube, etc.)
- **Organizations** (ZANU-PF, CCC, Econet, RBZ, etc.)
- **Locations** (Harare, Bulawayo, Victoria Falls, etc.)
- **Topics** (Politics, Economy, Health, Agriculture, etc.)

#### 3. **Sentiment Analysis**
```python
{
  "positive": 0.35,    # 35% of content
  "negative": 0.42,    # 42% of content
  "neutral": 0.23      # 23% of content
}
```

#### 4. **Pattern Recognition**
Identifies recurring patterns:
- Political cycles
- Economic trends
- Policy announcements
- Crisis periods
- Seasonal variations

### API: Get Trends

```bash
GET /api/think-tank/trends
Query Parameters:
  - window_days: 30 (1-365)
  - limit: 10 (1-50)

Response:
{
  "window_days": 30,
  "top_topics": [
    {"topic": "Politics", "count": 245},
    {"topic": "Economy", "count": 189}
  ],
  "top_politicians": [...],
  "sentiment_distribution": {...},
  "analysis_date": "2024-01-15T10:30:00Z"
}
```

### API: Analyze Specific Topic

```bash
POST /api/think-tank/analyze-topic
Query Parameters:
  - topic: "Zimbabwe Economy"
  - days_window: 30

Response:
{
  "topic": "Zimbabwe Economy",
  "patterns": {...},
  "trends": {...},
  "entities": {
    "politicians": ["Mthuli Ncube", "Emmerson Mnangagwa"],
    "organizations": ["RBZ", "Stock Exchange"]
  },
  "analysis_date": "2024-01-15T10:30:00Z"
}
```

---

## 📝 Article Generation System

### Three Types of Articles

#### 1. **Historical Analysis** (`/historical`)

**Purpose:** Rewrite history with full context, understanding how past events shaped present

**Example:**
```
Title: "Historical Analysis: Zimbabwe's Economic Crisis (Past 10 Years)"

Sections:
- Background: Context and origins
- Timeline: Key events chronologically
- Key Events: Most significant moments
- Evolution: How the crisis evolved
- Contributing Factors: Root causes
- Lessons Learned: What we can learn
```

**Data Used:**
- All available historical articles (no time limit)
- Social media posts from past
- Policy changes and announcements
- Economic indicators over time

#### 2. **Present Analysis** (`/present`)

**Purpose:** Understand current situation with all stakeholder positions

**Example:**
```
Title: "Current Situation: Zimbabwe Economy Crisis - January 2024"

Sections:
- Overview: Current state as of today
- Key Stakeholders: Who's involved
- Current Challenges: What's happening now
- Recent Developments: Last 7 days
- Sentiment Analysis: How people feel
- Policy Responses: Government actions
- Expert Opinions: Analysis and views
```

**Data Used:**
- Articles from last 7 days (configurable)
- Recent social media posts from influencers
- Current policy statements
- Real-time economic data

#### 3. **Future Prediction** (`/future`)

**Purpose:** Forecast what will happen based on trends and patterns

**Example:**
```
Title: "Outlook: Zimbabwe Economy - Next 90 Days Forecast"

Sections:
- Executive Summary: What will likely happen
- Predicted Scenarios: 3-5 possible outcomes
- Risk Analysis: What could go wrong
- Opportunities: What could go right
- Confidence Level: How sure we are
- Recommendations: What should be done
```

**Data Used:**
- Historical trends (all available data)
- Current trajectory
- Political cycle patterns
- Economic indicators
- Policy direction

### Confidence Levels

Articles are auto-flagged based on confidence:

```python
{
  "confidence": 0.85,  # 85% confidence
  "auto_publish": true # Publishes automatically
}

{
  "confidence": 0.65,  # 65% confidence
  "auto_publish": false,
  "flag_for_review": true,
  "review_reason": "Moderate uncertainty - contains conflicting signals"
}

{
  "confidence": 0.45,  # 45% confidence
  "auto_publish": false,
  "flag_for_review": true,
  "review_reason": "LOW CONFIDENCE - Requires human review before publication"
}
```

### API: Generate Article

```bash
POST /api/think-tank/generate-article
Body:
{
  "topic": "Zimbabwe Elections 2025",
  "article_type": "future",  # historical, present, or future
  "days_window": 90          # Optional time window
}

Response:
{
  "message": "Article generation started",
  "topic": "Zimbabwe Elections 2025",
  "article_type": "future",
  "status": "generating",
  "submitted_date": "2024-01-15T10:30:00Z"
}

# Check status
GET /api/think-tank/generated-articles
Response:
[
  {
    "id": "article_uuid",
    "article_type": "future",
    "title": "Outlook: Zimbabwe Elections 2025 - Next 90 Days",
    "topic": "Zimbabwe Elections 2025",
    "status": "flagged_for_review",  # or "published"
    "confidence_score": 0.68,
    "generated_date": "2024-01-15T10:35:00Z",
    "published_date": null
  }
]

# Get full article
GET /api/think-tank/generated-articles/{article_id}
Response:
{
  "id": "article_uuid",
  "article_type": "future",
  "title": "Outlook: Zimbabwe Elections 2025",
  "content": "Full article text with all sections...",
  "sections": {
    "executive_summary": "...",
    "predicted_scenarios": "...",
    "risk_analysis": "...",
    "opportunities": "...",
    "recommendations": "..."
  },
  "analysis_data": {
    "confidence": 0.68,
    "risk_factors": ["Political polarization", "Economic uncertainty"],
    "opportunity_factors": ["Voter engagement", "International support"],
    "trends": {...}
  }
}
```

---

## 🎯 Prediction Tracking & Validation

### How Predictions Work

The system makes predictions and tracks accuracy over time:

```json
{
  "id": "prediction_uuid",
  "topic": "Zimbabwe Inflation Rate Q1 2024",
  "prediction_text": "Inflation will stabilize between 25-35% by end of Q1",
  "made_date": "2024-01-01T00:00:00Z",
  "forecast_date": "2024-04-01T00:00:00Z",
  "forecast_days": 90,
  "confidence_level": 0.72,
  "supporting_factors": [
    "Recent currency stabilization",
    "Central bank policy consistency"
  ],
  "risk_factors": [
    "External economic shocks",
    "Political instability"
  ],
  "status": "pending"
}
```

### Validation Flow

```
Prediction Made (Confidence: 0.72)
    ↓
90 Days Pass
    ↓
Record Actual Outcome
    ↓
Calculate Accuracy (e.g., 85% accurate)
    ↓
Update Confidence Metrics
    ↓
Use for Training Future Predictions
```

### API: Track Predictions

```bash
# Get all predictions
GET /api/think-tank/predictions
Query: ?topic=Zimbabwe+Economy&limit=50

# Get predictions for a topic
GET /api/think-tank/predictions?topic=Zimbabwe+Elections

# Validate a prediction
POST /api/think-tank/predictions/{prediction_id}/validate
Body:
{
  "actual_outcome": "Elections held successfully with high turnout",
  "accuracy_score": 0.85
}

Response:
{
  "prediction_id": "prediction_uuid",
  "accuracy_score": 0.85,
  "validation_status": "validated",
  "validation_date": "2024-04-01T00:00:00Z"
}
```

### Accuracy Metrics

The system automatically calculates:

```python
{
  "total_predictions": 127,
  "successful": 98,          # accuracy >= 0.75
  "partially_correct": 19,   # accuracy 0.50-0.75
  "failed": 10,              # accuracy < 0.50
  "average_accuracy": 0.78,
  "accuracy_by_category": {
    "politics": 0.82,
    "economy": 0.75,
    "social": 0.71,
    "technology": 0.88
  }
}
```

---

## 📊 Publication Queue & Review Process

### Automatic Flagging

Articles are automatically flagged if:

1. **Confidence < 0.65** - Uncertain predictions
2. **Conflicting Signals** - Mixed sentiment/trends
3. **Controversial Topics** - Politics, sensitive issues
4. **Predictions > 60 days** - Long-term forecasts
5. **New Topics** - First analysis of a topic

### Review Workflow

```
Generated Article
    ↓
Confidence Check
    ├→ HIGH (>0.80) → AUTO-PUBLISH
    ├→ MEDIUM (0.65-0.80) → FLAG FOR OPTIONAL REVIEW
    └→ LOW (<0.65) → REQUIRE REVIEW
    ↓
Publication Queue
    ├→ Pending Review
    ├→ Approved (by editor/manager)
    ├→ Rejected (needs revision)
    └→ Published
```

### API: Manage Publication Queue

```bash
# Get pending articles
GET /api/think-tank/publication-queue
Query: ?status=pending&limit=50

Response:
{
  "queue_items": [
    {
      "id": "queue_uuid",
      "article_id": "article_uuid",
      "article_title": "Outlook: Zimbabwe Elections 2025",
      "status": "pending",
      "reason_flagged": "Confidence 0.68 - Moderate uncertainty",
      "uncertainty_level": "medium",
      "submitted_date": "2024-01-15T10:35:00Z"
    }
  ],
  "count": 12
}

# Approve article
POST /api/think-tank/publication-queue/{article_id}/approve
Body:
{
  "scheduled_publish_date": "2024-01-16T09:00:00Z"
}

# Reject article
POST /api/think-tank/publication-queue/{article_id}/reject
Body:
{
  "reason": "Predictions need more data - wait 7 more days"
}
```

---

## 📈 Dashboard & Analytics

### Dashboard Summary

```bash
GET /api/think-tank/dashboard/summary

Response:
{
  "total_articles_processed": 4523,
  "total_social_posts_captured": 2847,
  "generated_articles_count": 156,
  "pending_review_count": 12,
  "published_count": 144,
  "top_trends": [
    {"topic": "Politics", "mentions": 1245},
    {"topic": "Economy", "mentions": 987}
  ],
  "recent_predictions": [...],
  "accuracy_metrics": {
    "average_prediction_accuracy": 0.78,
    "successful_predictions": 98,
    "failed_predictions": 10
  }
}
```

### Detailed Analytics

```bash
GET /api/think-tank/dashboard/analytics
Query: ?time_period=30d

Response:
{
  "time_period": "30d",
  "metrics": {
    "total_articles": 1234,
    "total_posts": 847,
    "articles_generated": 45,
    "sentiment_trend": [
      {"date": "2024-01-01", "positive": 0.35, "negative": 0.42},
      ...
    ],
    "topic_distribution": {...},
    "politician_mentions": {...},
    "engagement_metrics": {
      "avg_views": 3452,
      "avg_engagement": 0.18
    }
  }
}
```

---

## ⚙️ Configuration Guide

### Complete Config Example

```yaml
think_tank:
  # Enable/disable think tank features
  enabled: true
  
  # Article generation
  article_generation:
    enabled: true
    auto_publish: true
    confidence_threshold: 0.65  # Auto-publish if >= this
    review_required_below: 0.65
  
  # Analysis settings
  analysis:
    # How far back to analyze for patterns
    historical_window_years: 10
    
    # Trend analysis window
    trend_window_days: 30
    
    # Prediction forecast period
    forecast_days: 90
    
    # Minimum articles needed for analysis
    min_articles_for_analysis: 10
  
  # Generation settings
  generation:
    # Which types to auto-generate
    auto_generate_types:
      - historical
      - present
      - future
    
    # Generate on what trigger
    generate_on_new_posts: true
    generate_on_trending_topics: true
    generate_interval_hours: 24
    
    # LLM settings (if using LLM enhancement)
    use_llm_enhancement: true
    llm_model: "gpt-4"  # gpt-3.5-turbo, gpt-4, claude-opus, etc.
    llm_temperature: 0.7

social_media:
  enabled: true
  capture_interval: 30  # minutes
  
  influencers:
    twitter:
      - "edmnangagwa"
      - "nelsonchamisa"
      - "MthuliNcube"
    facebook:
      - "GovernmentZW"
    instagram:
      - "emmersonmn"
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **OCR Not Working**

```
Error: "pytesseract not found"
```

**Solution:**
```powershell
# Reinstall pytesseract
pip install pytesseract

# Make sure Tesseract is installed at:
# C:\Program Files\Tesseract-OCR
```

#### 2. **Screenshots Not Capturing**

```
Error: "Chrome not found" or "Selenium timeout"
```

**Solution:**
```powershell
# Install Chrome
# Download from: https://www.google.com/chrome/

# Reinstall Selenium
pip install --upgrade selenium

# Update ChromeDriver
pip install webdriver-manager
```

#### 3. **LLM API Errors**

```
Error: "OpenAI API key not found"
```

**Solution:**
```powershell
# Add to .env.development
OPENAI_API_KEY=sk-...your-key...

# Or use template-based generation (no API needed)
```

#### 4. **Database Issues**

```
Error: "GeneratedArticle table not found"
```

**Solution:**
```powershell
# Run migrations
python -m alembic upgrade head

# Or create tables manually
python -c "from src.db.models import Base; Base.metadata.create_all(engine)"
```

---

## 📊 Data Storage

### Article Storage

**Original Articles** (from RSS feeds):
- Stored in: `articles` table
- Includes: Title, content, URL, source, published date
- Extraction: Politicians, organizations, topics

**Social Media Posts** (from influencers):
- Stored in: `social_media_posts` table
- Includes: Platform, text, screenshot path, extracted text (OCR)
- Media: Original images + locally cached copies

**Generated Articles** (think tank output):
- Stored in: `generated_articles` table
- Includes: Full content, sections, analysis data, confidence score
- Status: Draft, flagged, published

### Screenshots & Images

Default storage location: `screenshots/`

```
screenshots/
├── twitter_edmnangagwa_0_1705334200.png
├── twitter_nelsonchamisa_1_1705334205.png
├── facebook_GovernmentZW_0_1705334210.png
└── ...
```

---

## 🚀 Advanced Usage

### Custom Analysis

```python
from src.services.think_tank import ContentAnalyzer, PredictionEngine

analyzer = ContentAnalyzer()
articles = [...]  # Your articles

# Detect trends
trends = analyzer.identify_trends(articles, window_days=30)

# Extract entities from specific text
entities = analyzer.extract_entities("Mnangagwa discusses economic reforms...")

# Run prediction engine
predictor = PredictionEngine()
forecast = predictor.forecast_trends(articles, forecast_days=90)
```

### Batch Generation

```python
from src.services.think_tank import ArticleGenerator

generator = ArticleGenerator()

topics = ["Zimbabwe Elections", "Economic Crisis", "Education"]

for topic in topics:
    # Generate all three types
    historical = await generator.generate_historical_analysis(topic, articles)
    present = await generator.generate_present_analysis(topic, articles)
    future = await generator.generate_future_prediction(topic, articles)
```

### Custom Filtering

```yaml
# In zimbabwe.yaml
content_filter:
  # Only generate articles for these topics
  topics_to_monitor:
    - Politics
    - Economy
    - Agriculture
  
  # Exclude these keywords
  exclude_keywords:
    - spam
    - advertisement
  
  # Minimum sources needed
  min_sources: 3
```

---

## 📚 API Reference Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/think-tank/capture-social-media` | POST | Capture posts from influencers |
| `/api/think-tank/social-media-posts` | GET | Get captured posts |
| `/api/think-tank/trends` | GET | Get identified trends |
| `/api/think-tank/analyze-topic` | POST | Analyze specific topic |
| `/api/think-tank/generate-article` | POST | Generate analysis article |
| `/api/think-tank/generated-articles` | GET | Get generated articles |
| `/api/think-tank/generated-articles/{id}` | GET | Get article details |
| `/api/think-tank/predictions` | GET | Get predictions |
| `/api/think-tank/predictions/{id}/validate` | POST | Validate prediction |
| `/api/think-tank/publication-queue` | GET | Get approval queue |
| `/api/think-tank/publication-queue/{id}/approve` | POST | Approve article |
| `/api/think-tank/publication-queue/{id}/reject` | POST | Reject article |
| `/api/think-tank/dashboard/summary` | GET | Dashboard summary |
| `/api/think-tank/dashboard/analytics` | GET | Detailed analytics |

---

## 📞 Support & Customization

Need to:
- Add more influencers? → Edit `zimbabwe.yaml`
- Change article templates? → Edit `think_tank.py` section generator methods
- Adjust confidence thresholds? → Edit `ArticleGenerator` class
- Add new analysis types? → Extend `ContentAnalyzer` class

---

## ✨ What You Now Have

✅ **Complete Think Tank System** - Analyzes all news and social media  
✅ **Screenshot Capture** - Automatic capture every 30 minutes  
✅ **OCR Text Extraction** - Convert images to searchable text  
✅ **Trend Analysis** - Identify patterns across all data  
✅ **Article Generation** - Historical, present, and future  
✅ **Publication Queue** - Review workflow with auto-flagging  
✅ **Prediction Tracking** - Validate accuracy over time  
✅ **Dashboard & Analytics** - Complete visibility  

---

**Your Zimbabwe think tank is ready! 🇿🇼🧠**

Start with:
1. Configure influencers in `zimbabwe.yaml`
2. Run `python main.py`
3. Wait 30 minutes for first posts to be captured
4. Check dashboard at `http://localhost:8000/docs`