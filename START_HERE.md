# 🎯 START HERE - News Aggregator Setup

## 👋 Welcome!

You have a complete, production-ready news aggregator system. This guide will get you running **in under 5 minutes**.

---

## 🚀 Quick Start (Choose ONE)

### Option 1: PowerShell Script (Easiest) ✨
```powershell
cd "c:\Users\user\Documents\projects\Sources Media"
powershell -ExecutionPolicy Bypass -File "scripts/start_dev.ps1"
```

### Option 2: Batch File
```powershell
cd "c:\Users\user\Documents\projects\Sources Media"
cmd /c scripts\start_dev.bat
```

### Option 3: Manual Setup
```powershell
cd "c:\Users\user\Documents\projects\Sources Media"
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python scripts/init_db.py
uvicorn main:app --reload
```

---

## ✅ Verify It's Working

Once started, you should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

Then open: **http://localhost:8000/docs**

You should see the interactive API documentation with all available endpoints.

---

## 📚 Documentation Files

Explore these files for more details:

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | 3-minute quick reference |
| **SETUP_DEVELOPMENT.md** | Complete setup guide with all options |
| **SETUP_CHECKLIST.md** | Step-by-step verification checklist |
| **.env.development** | Default development configuration |

---

## 🎁 What You Have

### Core Features ✅
- Multi-source news collection (RSS, APIs, web scraping)
- SQLite database (development)
- RESTful FastAPI backend
- Interactive API documentation

### Advanced Features ✅
- **Image Processing** - OCR with Tesseract (optional)
- **Audio Processing** - Transcription with Whisper (optional)
- **Video Processing** - Video analysis (optional)
- **Document Processing** - PDF, DOCX, etc. (optional)
- **AI Integration** - OpenAI/Anthropic (optional)
- **Writing Style Mimicking** - Analyze and apply user style
- **Archive Research** - Historical data analysis
- **Background Tasks** - Celery + Redis (optional)

---

## 🔑 Configuration

Default environment (`.env`):
- Database: SQLite (auto-created)
- Debug: True (shows detailed errors)
- API Keys: Optional (can work without them)
- Media Tools: Optional (Tesseract, FFmpeg, etc.)

To add features, edit `.env`:
```
# Optional - Add your API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
NEWS_API_KEY=...

# Optional - Enable media processing
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
```

---

## 🛠️ Troubleshooting

### Issue: Port 8000 in use
```powershell
uvicorn main:app --reload --port 8001
```

### Issue: Module not found
```powershell
# Ensure venv is activated
.\venv\Scripts\Activate.ps1
```

### Issue: Database errors
```powershell
# Reinitialize
Remove-Item "news_aggregator.db" -Force
python scripts/init_db.py
```

### Issue: Dependency errors
```powershell
# Reinstall
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📖 API Endpoints

Once running, visit **http://localhost:8000/docs** to interact with:

### Feed Management
- `GET /feeds` - List feeds
- `POST /feeds` - Create feed
- `GET /feeds/{id}` - Get feed details
- `DELETE /feeds/{id}` - Delete feed

### Article Management
- `GET /articles` - List articles
- `POST /articles` - Create article
- `GET /articles/{id}` - Get article
- `PUT /articles/{id}` - Update article
- `DELETE /articles/{id}` - Delete article

### Advanced Features
- `POST /process-image` - OCR (image → text)
- `POST /process-audio` - Transcription (audio → text)
- `POST /process-video` - Video analysis
- `POST /generate-article` - AI writing
- `POST /analyze-style` - Writing analysis

---

## 🚀 Next Steps

### Phase 1: Verify (Now)
- [x] Run one of the quick start commands
- [x] Open http://localhost:8000/docs
- [x] Try a simple API call

### Phase 2: Explore (Next)
- [ ] Read through the API endpoints
- [ ] Test creating feeds and articles
- [ ] Review the database schema
- [ ] Check out the source code in `news-aggregator/src/`

### Phase 3: Customize (Optional)
- [ ] Add API keys for AI features
- [ ] Install media processing tools
- [ ] Configure Redis for background tasks
- [ ] Build a custom frontend

### Phase 4: Production (Later)
- [ ] Switch to PostgreSQL database
- [ ] Deploy to server/cloud
- [ ] Set up monitoring
- [ ] Configure nginx/reverse proxy
- [ ] SSL certificates

---

## 📞 Project Structure

```
Sources Media/
├── news-aggregator/              # Main application
│   ├── src/
│   │   ├── app.py               # FastAPI entry point
│   │   ├── api/routers/         # API endpoints
│   │   ├── db/                  # Database models
│   │   ├── services/            # Business logic
│   │   ├── core/config.py       # Configuration
│   │   ├── tasks/               # Background tasks
│   │   └── ...
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── scripts/
│   ├── start_dev.ps1            # Start server (PowerShell)
│   ├── start_dev.bat            # Start server (Batch)
│   └── init_db.py               # Initialize database
│
├── main.py                       # Root entry point
├── requirements.txt             # All dependencies
├── .env                        # Actual config (git ignored)
├── .env.development            # Template config
│
├── SETUP_DEVELOPMENT.md        # Full setup guide
├── QUICKSTART.md               # Quick reference
├── SETUP_CHECKLIST.md          # Verification steps
└── START_HERE.md              # This file

```

---

## ⚡ One Command To Rule Them All

```powershell
# Copy this entire command and paste it:
cd "c:\Users\user\Documents\projects\Sources Media"; 
powershell -ExecutionPolicy Bypass -File "scripts/start_dev.ps1"
```

This will:
1. ✅ Navigate to project
2. ✅ Activate virtual environment
3. ✅ Load configuration
4. ✅ Initialize database (if needed)
5. ✅ Start the server

Then open: **http://localhost:8000/docs**

---

## 🎉 You're All Set!

The system is ready to use. Start with the quick start command above, then explore the API documentation.

**Questions?** Check the other documentation files or examine the error messages in your terminal.

**Ready?** 

```powershell
cd "c:\Users\user\Documents\projects\Sources Media"
powershell -ExecutionPolicy Bypass -File "scripts/start_dev.ps1"
```

Let's go! 🚀