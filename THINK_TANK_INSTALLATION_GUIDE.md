# 🧠 Think Tank System - Complete Installation & Integration Guide

## Overview

This guide explains how the Think Tank System integrates with your existing Zimbabwe news aggregator and walks through installation and setup.

---

## 📋 What's Been Added

### Code Files (3 new)

```
news-aggregator/src/services/
├── screenshot_capture.py      (NEW - 400 lines) Social media capture
├── think_tank.py              (NEW - 700 lines) Analysis & generation
└── content_filter.py          (EXISTING - Enhanced with entity extraction)

news-aggregator/src/api/
├── think_tank.py              (NEW - 400 lines) API endpoints

news-aggregator/src/db/
├── models.py                  (UPDATED - 6 new tables)

news-aggregator/configs/
├── zimbabwe.yaml              (UPDATED - Think tank configuration added)
```

### Documentation Files (4 new)

```
├── THINK_TANK_SYSTEM.md                  (Complete reference - 15 KB)
├── THINK_TANK_QUICK_START.md            (15-minute setup - 6 KB)
├── THINK_TANK_FEATURES_SUMMARY.md       (Feature overview - 8 KB)
├── THINK_TANK_INSTALLATION_GUIDE.md     (This file - 10 KB)
```

### Dependencies Added

```
selenium==4.14.0              # Browser automation for screenshots
webdriver-manager==4.0.1      # Chrome driver management
pytesseract==0.3.10          # OCR text extraction
Pillow==10.1.0               # Image processing
imageio==2.33.1              # Video/image handling
httpx==0.25.2                # Async HTTP client
aiohttp==3.9.1               # Async HTTP requests
```

---

## 🎯 Architecture Integration

### System Flow

```
Existing Components                   New Think Tank Components
─────────────────────                 ──────────────────────

RSS Feed Fetcher ──────┐
                       │
Social Media            ├──→ Content Analyzer ──→ Trend Detection
(Twitter/Facebook)      │         │
                        │         └──→ Entity Extraction
Articles Database ──────┘                │
                                         ├──→ Prediction Engine
                                         │
                                         └──→ Article Generator
                                                    │
                                                    ├─ Historical Analysis
                                                    ├─ Present Analysis
                                                    └─ Future Prediction
                                                         │
                                                         ↓
                                                  Publication Queue
                                                         │
                                              ┌──────────┼──────────┐
                                              ↓          ↓          ↓
                                         Auto-Publish  Flag Review  Reject
                                              │          │          │
                                              ↓          ↓          ↓
                                         Generated Articles Database
```

### Data Flow

```
Step 1: CAPTURE
  └─ Social media posts → Screenshots → OCR extraction

Step 2: STORE
  └─ Posts stored in: social_media_posts table
  └─ Screenshots stored in: screenshots/ folder

Step 3: ANALYZE
  └─ Extract entities (politicians, topics, organizations)
  └─ Detect sentiment (positive/negative/neutral)
  └─ Identify trends
  └─ Make predictions

Step 4: GENERATE
  └─ Create historical analysis (using all data)
  └─ Create present analysis (using 7-day window)
  └─ Create future predictions (90-day forecast)

Step 5: REVIEW
  └─ Score confidence (0-1)
  └─ Check thresholds
  ├─ HIGH (>0.80) → AUTO-PUBLISH
  ├─ MEDIUM (0.65-0.80) → FLAG FOR REVIEW
  └─ LOW (<0.65) → REQUIRE REVIEW

Step 6: PUBLISH
  └─ High-confidence → Published immediately
  └─ Flagged → Review queue
  └─ Low-confidence → Waiting for approval

Step 7: TRACK
  └─ Monitor engagement
  └─ Track prediction accuracy
  └─ Update metrics
```

---

## 💾 Database Schema Changes

### New Tables

```sql
-- Social media posts with OCR extraction
CREATE TABLE social_media_posts (
  id VARCHAR PRIMARY KEY,
  platform VARCHAR,          -- twitter, facebook, instagram
  author_username VARCHAR,
  text TEXT,
  extracted_text TEXT,       -- OCR'd text from screenshots
  screenshot_path VARCHAR,   -- Local file path
  media_urls JSON,
  sentiment VARCHAR,         -- positive, negative, neutral
  captured_date DATETIME,
  ...
);

-- Generated articles from think tank
CREATE TABLE generated_articles (
  id VARCHAR PRIMARY KEY,
  article_type VARCHAR,      -- historical, present, future
  title VARCHAR,
  content TEXT,
  topic VARCHAR,
  status VARCHAR,            -- draft, flagged, published
  confidence_score FLOAT,    -- 0-1
  sections JSON,             -- Article sections
  analysis_data JSON,        -- Trends, predictions, etc.
  generated_date DATETIME,
  published_date DATETIME,
  ...
);

-- Identified trends
CREATE TABLE analysis_trends (
  id VARCHAR PRIMARY KEY,
  trend_name VARCHAR,
  category VARCHAR,
  mention_count INTEGER,
  sentiment_breakdown JSON,
  trend_strength FLOAT,      -- 0-1
  predicted_trajectory VARCHAR,
  confidence FLOAT,
  ...
);

-- Made predictions
CREATE TABLE predictions (
  id VARCHAR PRIMARY KEY,
  topic VARCHAR,
  prediction_text TEXT,
  made_date DATETIME,
  forecast_date DATETIME,    -- When prediction is for
  confidence_level FLOAT,    -- 0-1
  actual_outcome TEXT,       -- After forecast date
  outcome_accuracy FLOAT,    -- 0-1
  validation_status VARCHAR,
  ...
);

-- Publication workflow
CREATE TABLE publication_queue (
  id VARCHAR PRIMARY KEY,
  generated_article_id VARCHAR,
  status VARCHAR,            -- pending, approved, published
  review_date DATETIME,
  reviewed_by VARCHAR,
  ...
);

-- Monitored sources
CREATE TABLE content_sources (
  id VARCHAR PRIMARY KEY,
  source_type VARCHAR,       -- rss, twitter, facebook
  name VARCHAR,
  username VARCHAR,
  category VARCHAR,
  ...
);
```

---

## 🚀 Installation Steps

### Step 1: Install Python Dependencies (5 minutes)

```powershell
cd "c:\Users\user\Documents\projects\Sources Media"

# Upgrade pip first
python -m pip install --upgrade pip

# Install new dependencies
pip install selenium==4.14.0
pip install webdriver-manager==4.0.1
pip install pytesseract==0.3.10
pip install Pillow==10.1.0
pip install imageio==2.33.1
pip install httpx==0.25.2
pip install aiohttp==3.9.1

# Or install all at once
pip install -r requirements.txt
```

### Step 2: Install OCR Engine (5 minutes)

**Option A: Using Chocolatey (recommended if installed)**

```powershell
# Must run as Administrator
choco install tesseract
```

**Option B: Manual Download**

1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Download: `tesseract-ocr-w64-setup-v5.x.x.exe` (newest version)
3. Run installer
4. Install to default: `C:\Program Files\Tesseract-OCR`
5. Add to system PATH (usually done automatically)

**Verify Installation:**

```powershell
# Should return version info
tesseract --version

# Should find Tesseract location
where tesseract
```

### Step 3: Update Configuration (5 minutes)

**Already Done!** The file `news-aggregator/configs/zimbabwe.yaml` has been updated with:

- ✅ Think tank system enabled
- ✅ Social media capture configured
- ✅ 6 influencers configured
- ✅ All analysis settings optimized
- ✅ Publication workflow setup

**Verify configuration is loaded:**

```python
import yaml
with open("news-aggregator/configs/zimbabwe.yaml") as f:
    config = yaml.safe_load(f)
    print(config["think_tank"]["enabled"])  # Should print: True
```

### Step 4: Create Database Tables (2 minutes)

```python
# Run Python script to create tables
from news_aggregator.src.db.models import Base, engine
Base.metadata.create_all(engine)

# Or using Alembic (if migrations exist)
alembic upgrade head
```

### Step 5: Verify Installation (5 minutes)

```powershell
# Start the application
python main.py

# You should see:
# - FastAPI starting on http://localhost:8000
# - All routes loaded
# - Think tank system initialized
# - Social media monitor started
```

**Check endpoints:**

```bash
# In another terminal
curl http://localhost:8000/docs

# Should see:
# - /api/think-tank/capture-social-media
# - /api/think-tank/generate-article
# - /api/think-tank/dashboard/summary
# - ... (20+ new endpoints)
```

---

## ⚙️ Configuration Details

### Think Tank System Configuration

All settings are in: `news-aggregator/configs/zimbabwe.yaml`

```yaml
think_tank:
  enabled: true                          # Enable/disable entire system
  
  article_generation:
    auto_publish: true                   # Auto-publish high confidence
    confidence_threshold: 0.65           # Auto-publish if >= this
    
  analysis:
    historical_window_years: 0           # 0 = unlimited
    trend_window_days: 30
    forecast_days: 90
    
  social_media_capture:
    capture_interval: 30                 # Minutes between captures
    ocr_enabled: true
    
  publication:
    auto_publish_high_confidence: true
    high_confidence_threshold: 0.80
```

### Influencers to Monitor

Already configured in `zimbabwe.yaml`:

```yaml
influencers:
  twitter:
    - edmnangagwa        # President
    - nelsonchamisa      # Opposition
    - MthuliNcube        # Finance Minister
    - strive             # Entrepreneur
    - daddyhope          # Journalist
    - VinceMusewe        # Economist
```

**To add more influencers:**

```yaml
influencers:
  twitter:
    - existing_username
    - new_username       # Add here
```

---

## 🔧 Optional: LLM Enhancement

The system works perfectly with **template-based article generation** (no API keys needed).

**To use OpenAI/Claude for enhanced articles:**

1. Get API key from:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

2. Add to `.env.development`:
   ```
   OPENAI_API_KEY=sk-...your-key...
   # OR
   ANTHROPIC_API_KEY=sk-ant-...your-key...
   ```

3. Update configuration:
   ```yaml
   article_generation:
     use_llm_enhancement: true
     llm_model: "gpt-4"  # or claude-opus
   ```

---

## 📊 First Run

### What Happens When You Start

```
Time 0:00 - python main.py
  └─ Load configuration
  └─ Initialize database
  └─ Create tables (if needed)
  └─ Start FastAPI server

Time 0:10 - Social Media Capture Starts
  └─ Connect to Twitter/Facebook
  └─ Load influencer profiles
  └─ Capture posts
  └─ Run OCR extraction

Time 0:20 - Posts Stored
  └─ social_media_posts table updated
  └─ Screenshots saved to disk
  └─ Extracted text indexed

Time 0:30 - Analysis Begins
  └─ Detect trends
  └─ Extract entities
  └─ Analyze sentiment
  └─ Update metrics

Time 1:00 - Next Capture Cycle
  └─ (Repeats every 30 minutes)

Time 24:00 - Article Generation
  └─ Generate historical analysis
  └─ Generate present analysis
  └─ Generate future predictions
  └─ Evaluate confidence
  └─ Publish or flag for review
```

### Check Dashboard After Setup

```bash
# Open in browser
http://localhost:8000/docs

# Navigate to think-tank endpoints
# Click: /api/think-tank/dashboard/summary

# Expected response:
{
  "total_posts_captured": 0,      # Will grow
  "total_articles_processed": 0,
  "generated_articles_count": 0,
  "pending_review": 0,
  "published": 0
}
```

---

## 📁 File Locations & Storage

### Screenshots Storage

```
project_root/
└── screenshots/
    ├── twitter_edmnangagwa_0_1705334200.png
    ├── twitter_edmnangagwa_1_1705334205.png
    ├── facebook_GovernmentZW_0_1705334210.png
    └── ... (grows over time)
```

### Logs

```
project_root/
└── logs/
    └── zimbabwe.log
```

### Database

```
project_root/
└── news_zimbabwe.db           # SQLite database (created automatically)
```

### Configuration

```
project_root/
└── news-aggregator/configs/
    └── zimbabwe.yaml          # All settings here
```

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'selenium'"

**Solution:**
```powershell
pip install selenium webdriver-manager
```

### Problem: "pytesseract not found"

**Solution:**
```powershell
pip install pytesseract

# Then install Tesseract OCR engine
choco install tesseract
# OR download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Problem: "Chrome not found" or "WebDriver timeout"

**Solution:**
```powershell
# Reinstall webdriver-manager
pip install --upgrade webdriver-manager

# Make sure Chrome is installed
# Download from: https://www.google.com/chrome/
```

### Problem: "Database table not found"

**Solution:**
```python
# Create tables
from news_aggregator.src.db.models import Base
Base.metadata.create_all(engine)
```

### Problem: "No posts being captured"

**Check:**
1. Is think tank enabled?
   ```yaml
   think_tank:
     enabled: true
   ```

2. Check if influencer usernames are correct in config

3. Check logs:
   ```bash
   tail -f logs/zimbabwe.log
   ```

4. Test capture manually:
   ```bash
   curl -X POST http://localhost:8000/api/think-tank/capture-social-media
   ```

### Problem: "Low confidence scores"

This is **normal and good!** The system is being conservative. As it collects more data (1-2 weeks), confidence will improve.

---

## 📚 Next Steps

### 1. **Let it Run for 24 Hours**
- More data = better analysis
- First articles will be generated
- Trends will start appearing

### 2. **Review Generated Articles**
```bash
GET http://localhost:8000/api/think-tank/generated-articles
```

### 3. **Monitor Publication Queue**
```bash
GET http://localhost:8000/api/think-tank/publication-queue
```

### 4. **Check Dashboard**
```bash
GET http://localhost:8000/api/think-tank/dashboard/summary
```

### 5. **After 7 Days**
- Review prediction accuracy
- Adjust confidence thresholds if needed
- Add/remove influencers as needed
- Fine-tune article generation

---

## 🎯 Success Checklist

- [ ] Python dependencies installed
- [ ] Tesseract OCR installed and verified
- [ ] Configuration file updated
- [ ] Database tables created
- [ ] Application starts without errors
- [ ] Dashboard accessible at http://localhost:8000/docs
- [ ] Think tank endpoints visible in Swagger UI
- [ ] First social media posts captured
- [ ] First articles being generated
- [ ] Publication queue working

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start system | `python main.py` |
| Install deps | `pip install -r requirements.txt` |
| Create DB | `python -c "from src.db.models import Base; Base.metadata.create_all()"` |
| View logs | `tail -f logs/zimbabwe.log` |
| Access API | `http://localhost:8000/docs` |
| Check config | `cat news-aggregator/configs/zimbabwe.yaml` |
| View screenshots | `ls -la screenshots/` |

---

## 🎉 You're All Set!

Your Think Tank System is ready to:
- ✅ Capture social media posts automatically
- ✅ Extract text from images with OCR
- ✅ Analyze trends and patterns
- ✅ Generate original analysis articles
- ✅ Track prediction accuracy
- ✅ Publish intelligently with review queue

**All running in the background!** 🚀

---

## 📖 Documentation Reference

| Document | Purpose |
|----------|---------|
| `THINK_TANK_QUICK_START.md` | 15-minute setup |
| `THINK_TANK_SYSTEM.md` | Complete reference |
| `THINK_TANK_FEATURES_SUMMARY.md` | Feature overview |
| `THINK_TANK_INSTALLATION_GUIDE.md` | This file |

---

**Ready to build your Zimbabwe think tank? Let's go!** 🇿🇼🧠