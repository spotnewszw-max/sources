# ⚡ Quick Start - News Aggregator

## 🎯 Get Running in 3 Minutes

### Step 1: Activate Environment & Install (First time only)

```powershell
# Open PowerShell, navigate to project root
cd "c:\Users\user\Documents\projects\Sources Media"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (takes ~10 min first time)
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Run the Server

**Easiest - Use Start Script:**
```powershell
powershell -ExecutionPolicy Bypass -File "scripts/start_dev.ps1"
```

**Or Manually:**
```powershell
# Activate venv first
.\venv\Scripts\Activate.ps1

# Create .env if it doesn't exist
Copy-Item ".env.development" ".env" -Force -ErrorAction SilentlyContinue

# Start server
uvicorn main:app --reload
```

### Step 3: Test It! 🎉

Open browser:
- **http://localhost:8000/docs** ← Interactive API explorer
- **http://localhost:8000/redoc** ← API documentation
- **http://localhost:8000/** ← Hello endpoint

---

## 📝 First Test

In the /docs interface (http://localhost:8000/docs):

1. Click **Try it out** on any endpoint
2. Execute and see the response
3. Try creating a feed or article

---

## 🆘 Troubleshooting

### "ModuleNotFoundError" or "Cannot find module"
```powershell
# Make sure venv is activated (should see (venv) in terminal)
.\venv\Scripts\Activate.ps1

# If still issues, update pip
python -m pip install --upgrade pip
```

### "Port 8000 already in use"
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (replace PID)
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --reload --port 8001
```

### "Database error"
```powershell
# Delete old database and reinitialize
Remove-Item "news_aggregator.db" -Force -ErrorAction SilentlyContinue
python scripts/init_db.py
```

### "Spacy model not found"
```powershell
python -m spacy download en_core_web_sm
```

---

## 📚 Next Steps

After confirming it works:

1. ✅ Read `SETUP_DEVELOPMENT.md` for full setup guide
2. ⏭️ Add optional features (see below)
3. ⏭️ Check API endpoints at `/docs`
4. ⏭️ Build your frontend

---

## 🎁 Optional Features

### Enable Image Processing (OCR)
1. Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Update `.env`:
   ```
   TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
   ```

### Enable Video/Audio Processing
1. Install FFmpeg: `choco install ffmpeg`
2. Verify: `ffmpeg -version`

### Enable Background Tasks (Celery)
1. Install & start Redis
2. Open new terminal and run:
   ```powershell
   celery -A news_aggregator.src.tasks.celery_app worker --loglevel=info
   ```

---

## 📦 Project Structure

```
Sources Media/
├── news-aggregator/          # Main application
│   └── src/
│       ├── app.py            # FastAPI app entry point
│       ├── api/              # API routes
│       ├── db/               # Database models
│       ├── services/         # Business logic
│       └── ...
├── main.py                   # Root entry point for uvicorn
├── scripts/
│   ├── start_dev.ps1        # Start dev server (PowerShell)
│   ├── start_dev.bat        # Start dev server (Batch)
│   └── init_db.py           # Initialize database
├── .env.development         # Dev configuration template
└── requirements.txt         # Python dependencies
```

---

## 🚀 You're Ready!

The system is now running. Check:
- Terminal shows "Application startup complete"
- No error messages
- http://localhost:8000/docs is accessible

Happy coding! 🎉