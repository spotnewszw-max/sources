# Zimbabwe News Aggregator - Quick Start Guide

**Get your Zimbabwe-focused news aggregator running in 10 minutes!** 🇿🇼

---

## ⚡ **30-Second Overview**

Your news aggregator is pre-configured with:
- ✅ **7 Zimbabwe local news sources** (RSS feeds, no API key needed)
- ✅ **3 African news outlets** covering Zimbabwe
- ✅ **Economic data feeds** for Zimbabwe
- ✅ **Smart filtering** for Zimbabwe-relevant content
- ✅ **Social media support** (Twitter/Facebook) - optional

---

## 🚀 **Start in 3 Steps**

### **Step 1: Install Dependencies (2 minutes)**

```powershell
# Windows PowerShell
Set-Location "c:\Users\user\Documents\projects\Sources Media"
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r news-aggregator\requirements.txt
```

### **Step 2: Start the Server (1 minute)**

```powershell
python main.py
```

**Output should show:**
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### **Step 3: Access the API (< 1 minute)**

Open in browser:
```
http://localhost:8000/docs
```

You'll see the interactive API dashboard.

---

## 📰 **What's Included**

### **News Sources (7 Zimbabwe outlets)**

| Source | URL | Type |
|--------|-----|------|
| NewsDay Zimbabwe | newsday.co.zw | Local news |
| The Herald | herald.co.zw | Government news |
| Zimbabwe Independent | independentzimbabwe.com | Investigative |
| Bulawayo24 | bulawayo24.com | Local |
| Techzim | techzim.co.zw | Technology |
| ZimFact | zimfact.org | Fact-checking |
| The Source | thesource.co.zw | Business |

**Plus:** 3 African news sources covering Zimbabwe

### **Content Filtering**

Automatically filters content for Zimbabwe relevance:
- Looks for keywords: Zimbabwe, Harare, economy, Mnangagwa, etc.
- Scores relevance (0-1)
- Removes duplicates
- Removes non-relevant content

---

## 🐦 **Add Social Media (Optional - 15 minutes)**

### **Option 1: Twitter/X (Recommended)**

This lets you monitor what policy makers are saying in real-time.

1. **Get API Key** (5 min)
   - Go to: https://developer.twitter.com
   - Click "Create App"
   - Get your Bearer Token

2. **Add to .env.development**
   ```
   TWITTER_BEARER_TOKEN=your_token_here
   ```

3. **Done!** The aggregator will now also collect tweets with #Zimbabwe

### **Option 2: Facebook (Optional)**

1. **Get Access Token** (10 min)
   - Go to: https://developers.facebook.com
   - Create app, generate Page Access Token

2. **Add to .env.development**
   ```
   FACEBOOK_ACCESS_TOKEN=your_token_here
   ```

**See full guide:** `SOCIAL_MEDIA_INTEGRATION.md`

---

## 🔍 **Test the Aggregator**

### **Fetch Articles from RSS**

```powershell
# PowerShell
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/articles" -UseBasicParsing
$response.Content | ConvertFrom-Json | Select-Object -First 5
```

### **Search for Zimbabwe News**

```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/articles?search=zimbabwe" -UseBasicParsing
$response.Content | ConvertFrom-Json
```

### **Get Trending Topics**

```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/trending" -UseBasicParsing
$response.Content | ConvertFrom-Json
```

---

## 📁 **Configuration Files**

All Zimbabwe sources are configured in:
```
news-aggregator/configs/zimbabwe.yaml
```

To change sources:
1. Edit `zimbabwe.yaml`
2. Add/remove sources under `fetcher.sources`
3. Set `CONFIG_FILE=configs/zimbabwe.yaml` in `.env.development`
4. Restart server

---

## 📊 **Monitor Key Figures**

Create alerts for statements from:

- **Government**
  - President: Emmerson Mnangagwa (@edmnangagwa)
  - Finance Minister: Mthuli Ncube (@MthuliNcube)
  
- **Opposition**
  - Nelson Chamisa (@nelsonchamisa)

- **Business**
  - Strive Masiyiwa (@strive)

- **Journalists**
  - Hopewell Chin'ono (@daddyhope)

---

## 🎯 **Common Tasks**

### **Enable/Disable Sources**

In `zimbabwe.yaml`:
```yaml
fetcher:
  sources:
    - name: NewsDay Zimbabwe
      enabled: true          # Change to false to disable
```

### **Change Update Frequency**

In `zimbabwe.yaml`:
```yaml
fetcher:
  interval: 60              # Check every 60 minutes
```

### **Adjust Filter Sensitivity**

In `zimbabwe.yaml`:
```yaml
content_filter:
  min_relevance: 0.6        # 0-1 (higher = stricter filtering)
```

---

## 🆘 **Troubleshooting**

### **"No articles found"**
- Check your internet connection
- Test RSS feeds in browser first
- Check logs: `tail -f logs/zimbabwe.log`

### **"Connection refused"**
- Make sure server is running: `python main.py`
- Check port 8000 is not in use

### **"Social media not working"**
- Verify API token in `.env.development`
- Check token hasn't expired
- See `SOCIAL_MEDIA_INTEGRATION.md` for details

### **Database error**
- Delete `news_zimbabwe.db` and restart (will recreate)
- Check disk space
- Run: `python scripts/init_db.py`

---

## 📈 **Next Steps**

### **Immediate**
- ✅ Start the server and explore the API
- ✅ Review collected articles
- ✅ Check filtering is working correctly

### **Today**
- 🔧 Customize sources for your specific needs
- 🐦 (Optional) Set up Twitter API

### **This Week**
- 📊 Build a dashboard to display articles
- 🔔 Set up alerts for trending topics
- 💾 Configure production database (PostgreSQL)

### **Later**
- 📱 Add more social media platforms
- 🎯 Build ML models to categorize articles
- 📧 Set up email alerts for key topics

---

## 📚 **Full Documentation**

| Document | Purpose |
|----------|---------|
| **ZIMBABWE_SOURCES.md** | Complete list of all sources |
| **SOCIAL_MEDIA_INTEGRATION.md** | Twitter/Facebook setup |
| **SETUP_DEVELOPMENT.md** | Detailed development setup |
| **configs/zimbabwe.yaml** | Source configuration |

---

## 💡 **Tips**

1. **Test RSS feeds in browser first**
   - Go to https://newsday.co.zw/feed
   - If it works in browser, it'll work in aggregator

2. **Start without social media**
   - Get RSS working first
   - Add Twitter/Facebook later

3. **Monitor disk space**
   - Database grows over time
   - Run cleanup: `python scripts/cleanup_old_articles.py`

4. **Set up backup**
   - Copy `news_zimbabwe.db` regularly
   - Store in cloud storage

---

## 🎉 **You're All Set!**

Your Zimbabwe news aggregator is ready to:
- ✅ Fetch local Zimbabwe news automatically
- ✅ Monitor policy makers (Twitter/Facebook)
- ✅ Filter for relevance
- ✅ Track trending topics
- ✅ Power your news dashboard

**Now go build something amazing!** 🚀

---

**Questions?** Check `ZIMBABWE_SOURCES.md` or `SOCIAL_MEDIA_INTEGRATION.md`

**Having issues?** See the Troubleshooting section above, or check logs in `logs/zimbabwe.log`