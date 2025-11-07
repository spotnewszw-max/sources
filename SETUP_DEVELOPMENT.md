# 🚀 Development Setup Guide - News Aggregator

## Prerequisites

### Required
- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/)

### Optional (for advanced features)
- **Tesseract OCR** - For image text extraction
  - Download: https://github.com/UB-Mannheim/tesseract/wiki
  - After install, update `TESSERACT_CMD` in `.env`
  
- **FFmpeg** - For video/audio processing
  - Download: https://ffmpeg.org/download.html
  - Windows: Use chocolatey: `choco install ffmpeg`
  
- **Redis** - For background task queue (optional)
  - Windows: https://github.com/microsoftarchive/redis/releases
  - Or use Windows Subsystem for Linux (WSL)

---

## Step 1: Verify Prerequisites

```powershell
# Check Python version (should be 3.9+)
python --version

# Check Git
git --version
```

---

## Step 2: Clone & Navigate

```powershell
cd "c:\Users\user\Documents\projects\Sources Media"
```

---

## Step 3: Create & Activate Virtual Environment

The venv already exists, just activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` prefix in your terminal.

---

## Step 4: Install Dependencies

**Option A: Quick Install (Recommended for first run)**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**Option B: Minimal Install (Core features only)**
```powershell
pip install fastapi uvicorn sqlalchemy aiohttp beautifulsoup4 feedparser
pip install python-dotenv pydantic python-multipart
pip install openai transformers spacy
python -m spacy download en_core_web_sm
```

> ⚠️ Installation takes 10-15 minutes due to PyTorch and other large libraries.

---

## Step 5: Configure Environment

Copy development config:
```powershell
Copy-Item ".\.env.development" ".\.env" -Force
```

Edit `.env` file with your settings (or use defaults):
```
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///./news_aggregator.db
OPENAI_API_KEY=your_key_here (optional)
```

---

## Step 6: Initialize Database

```powershell
python scripts/init_db.py
```

You should see:
```
✅ Database tables created successfully!
```

---

## Step 7: Run the Application

### Option A: Using PowerShell Script (Easiest)
```powershell
powershell -ExecutionPolicy Bypass -File "scripts/start_dev.ps1"
```

### Option B: Manual Start
```powershell
# Terminal 1 - Activate venv
.\venv\Scripts\Activate.ps1

# Start server
uvicorn news_aggregator.src.app:app --reload --host 0.0.0.0 --port 8000
```

---

## Step 8: Access the Application

🎉 **The app is running!**

- **API Base:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc (ReDoc)

---

## 📝 First API Test

Open http://localhost:8000/docs and try:

1. **GET /** - Test root endpoint
2. **GET /feeds** - List all feeds (empty initially)
3. **POST /feeds** - Create a test feed

---

## 🔧 Additional Setup (Optional)

### Install Media Processing Tools

For OCR, Video, Audio processing:

```powershell
# Tesseract OCR (Windows)
# Download: https://github.com/UB-Mannheim/tesseract/wiki
# Then update TESSERACT_CMD in .env

# FFmpeg
choco install ffmpeg

# Verify installations
tesseract --version
ffmpeg -version
```

### Enable Background Tasks (Celery)

If you have Redis installed:

```powershell
# Terminal 2 - Start Celery worker
celery -A news_aggregator.src.tasks.celery_app worker --loglevel=info
```

Without Redis, tasks run synchronously (slower but works).

---

## 📦 Available Endpoints

### Feeds
- `GET /feeds` - List all feeds
- `POST /feeds` - Create new feed
- `GET /feeds/{id}` - Get feed details
- `DELETE /feeds/{id}` - Delete feed

### Articles
- `GET /articles` - List articles
- `POST /articles` - Create article
- `GET /articles/{id}` - Get article
- `PUT /articles/{id}` - Update article
- `DELETE /articles/{id}` - Delete article

### Advanced Features
- `POST /process-image` - OCR image processing
- `POST /process-audio` - Audio transcription
- `POST /process-video` - Video processing
- `POST /generate-article` - AI article generation
- `POST /analyze-style` - Writing style analysis

---

## 🐛 Troubleshooting

### Virtual Environment not activating?
```powershell
# Try alternative activation
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### Database locked error?
```powershell
# Delete and reinitialize
Remove-Item "news_aggregator.db" -Force
python scripts/init_db.py
```

### Import errors?
```powershell
# Verify PYTHONPATH
python -c "import sys; print(sys.path)"

# Reinstall the package
pip install -e .
```

### Dependencies installation fails?
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Try installing one by one
pip install fastapi
pip install uvicorn
# ... etc
```

### Tesseract not found?
```powershell
# Update .env with correct path:
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
```

---

## 🎯 Next Steps

1. ✅ App is running
2. ⏭️ [Optional] Add API keys (OpenAI, Anthropic, NewsAPI)
3. ⏭️ [Optional] Setup media processing (Tesseract, FFmpeg)
4. ⏭️ [Optional] Configure Redis for background tasks
5. ⏭️ Build frontend interface
6. ⏭️ Deploy to production

---

## 📚 Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org
- **Celery Docs:** https://docs.celeryproject.io
- **OpenAI Docs:** https://platform.openai.com/docs
- **Spacy Models:** https://spacy.io/models

---

**Questions?** Check logs in the terminal or create an issue! 🚀