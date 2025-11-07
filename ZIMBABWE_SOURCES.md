# Zimbabwe News Aggregator - Data Sources Configuration

## 📍 Overview
This document lists all configured news sources for the Zimbabwe-focused news aggregator, including:
- Local Zimbabwe news outlets
- African news sources covering Zimbabwe
- International sources with Zimbabwe coverage
- Social media influencers & policy makers to monitor

---

## 🇿🇼 **Zimbabwe News Sources**

### **Major News Outlets (RSS Available)**

| Source | URL | Focus | Type |
|--------|-----|-------|------|
| **NewsDay Zimbabwe** | https://www.newsday.co.zw/feed | Local news, politics | RSS |
| **The Herald** | https://www.herald.co.zw/feed | National news, government | RSS |
| **Zimbabwe Independent** | https://www.independentzimbabwe.com/feed | Investigative journalism | RSS |
| **Bulawayo24** | https://bulawayo24.com/feed | Local + national | RSS |
| **Techzim** | https://www.techzim.co.zw/feed | Technology, business | RSS |
| **ZimFact** | https://zimfact.org/feed | Fact-checking | RSS |
| **The Source** | https://thesource.co.zw/feed | Business, economics | RSS |

### **African News (Zimbabwe Coverage)**

| Source | URL | Focus | Type |
|--------|-----|-------|------|
| **AllAfrica - Zimbabwe** | https://allafrica.com/zimbabwe/feed | Continental perspective | RSS |
| **Africa News - Zimbabwe** | https://www.africanews.com/feed | African news | RSS |
| **VOA Africa** | https://www.voanews.com/africa/feed | International coverage | RSS |

### **Economic & Business News**

| Source | URL | Focus | Type |
|--------|-----|-------|------|
| **Trading Economics - Zimbabwe** | https://tradingeconomics.com/zimbabwe/rss | Economic data | RSS |
| **RFI Afrique** | https://www.rfi.fr/en/africa/feed | French African news | RSS |

---

## 👥 **Policy Makers & Influencers (Social Media)**

### **Government Officials**

- **Emmerson Mnangagwa** (President) - @edmnangagwa (Twitter), emmerson-mnangagwa (Facebook)
- **Constantino Chiwenga** (VP) - @chiwenga_constan (Twitter)
- **Finance Minister Mthuli Ncube** - @MthuliNcube (Twitter)
- **Ziyambi Ziyambi** (Justice Minister)
- **Nduduzo Ndlela** (Local Government)

### **Opposition Leaders**

- **Advocate Nelson Chamisa** (CCC) - @nelsonchamisa (Twitter)
- **Amos Cumming** (MDC Officials)

### **Business & Economic Influencers**

- **Strive Masiyiwa** (Econet/Founder) - @strive (Twitter)
- **Takunda Chirara** (Business Analyst)
- **Prosper Chatsi Nyatsanga** (Economist)

### **Media & Journalists**

- **Hopewell Chin'ono** - @daddyhope (Twitter) - Investigative journalist
- **Blessing-Miles Tendi** - Academic/commentator
- **Vince Musewe** - @VinceMusewe (Twitter) - Economist

---

## 🔗 **Social Media APIs to Configure**

### **Twitter/X API**
- **Purpose:** Track policy makers, trending topics, breaking news
- **Endpoint:** Search tweets about Zimbabwe, track hashtags: #Zimbabwe, #Harare, #ZimEconomics
- **Authentication:** Bearer Token (requires Twitter Developer account)
- **Rate Limit:** 450 requests/15min (free tier)
- **Status:** ⏳ To be configured (see section below)

### **Facebook API**
- **Purpose:** Monitor government pages, news outlets official pages
- **Official Pages:** Zimbabwe Government, NewsDay, The Herald, etc.
- **Authentication:** Access Token (requires Facebook Developer account)
- **Status:** ⏳ To be configured (see section below)

---

## 🔐 **How to Get API Credentials**

### **Twitter API Setup (15 minutes)**
1. Go to https://developer.twitter.com
2. Sign in with Twitter account
3. Create a new App (Project)
4. Generate API Keys:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Bearer Token (for v2 API)
5. Add credentials to `.env.development`:
```
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
```

### **Facebook API Setup (20 minutes)**
1. Go to https://developers.facebook.com
2. Create app (if not already done)
3. Add "Instagram Graph API" product
4. Generate Page Access Token
5. Add to `.env.development`:
```
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_IDS=page_id_1,page_id_2,page_id_3
```

---

## 📊 **RSS Feed Testing**

Test RSS feeds are working with:
```bash
# Linux/Mac
curl https://www.newsday.co.zw/feed

# Windows PowerShell
Invoke-WebRequest -Uri "https://www.newsday.co.zw/feed" -UseBasicParsing | Select-Object Content
```

---

## 📝 **Configuration in YAML**

See `configs/zimbabwe.yaml` for complete configuration with all sources listed above.

To use:
```bash
# Development
export CONFIG_FILE=configs/zimbabwe.yaml

# Or in .env.development
CONFIG_FILE=configs/zimbabwe.yaml
```

---

## 🔍 **Trending Topics to Monitor**

### **Key Hashtags**
- `#Zimbabwe`
- `#ZimEconomy` or `#ZimEconomics`
- `#Harare`
- `#ZimPolitics`
- `#ZimTech`
- `#ZimBusiness`

### **Key Search Terms**
- "Zimbabwe economy"
- "RTGS dollar"
- "Zimbabwe politics"
- "Emmerson Mnangagwa"
- "Strive Masiyiwa"
- "Nelson Chamisa"

---

## 📈 **Next Steps**

1. ✅ **Immediate:** Start with RSS sources (no API key needed)
2. ⏳ **Week 2:** Add Twitter API integration
3. ⏳ **Week 3:** Add Facebook integration
4. ⏳ **Week 4:** Add custom web scrapers for sites without RSS

---

## 📌 **Notes**

- All RSS URLs are public and don't require authentication
- Some sites may have CORS issues - our fetcher handles this
- Update sources list as new outlets launch RSS feeds
- Social media APIs require paid tier for production volume
- Consider rate limiting to avoid API bans

---

## 🆘 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| RSS feed not working | Check URL in browser first, some sites may be down |
| XML parsing error | Ensure valid RSS URL (many sites have multiple feed types) |
| Social media API rejected | Verify credentials in `.env.development` |
| CORS error on frontend | Backend fetcher handles this internally |

---

**Last Updated:** 2024
**Maintained By:** News Aggregator Team