# ✅ Setup Checklist

Use this to verify your setup step-by-step.

## Phase 1: Prerequisites ✓

- [ ] **Python 3.9+** installed
  ```powershell
  python --version
  ```
  Should show: `Python 3.x.x` (3.9 or higher)

- [ ] **Git** installed (optional)
  ```powershell
  git --version
  ```

- [ ] Project directory exists
  ```powershell
  ls "c:\Users\user\Documents\projects\Sources Media"
  ```
  Should show folders: `news-aggregator`, `venv`, `scripts`, etc.

---

## Phase 2: Virtual Environment ✓

- [ ] Virtual environment already created
  ```powershell
  ls "c:\Users\user\Documents\projects\Sources Media\venv"
  ```
  Should show: `Scripts`, `Lib`, `Include` folders

- [ ] Activate virtual environment
  ```powershell
  Set-Location "c:\Users\user\Documents\projects\Sources Media"
  .\venv\Scripts\Activate.ps1
  ```
  Should show: `(venv)` prefix in terminal

- [ ] Python points to venv
  ```powershell
  (venv) python -c "import sys; print(sys.executable)"
  ```
  Should show path containing `\venv\Scripts\`

---

## Phase 3: Dependencies ✓

- [ ] **Upgrade pip**
  ```powershell
  (venv) python -m pip install --upgrade pip
  ```

- [ ] **Install main dependencies**
  ```powershell
  (venv) pip install -r requirements.txt
  ```
  Should take 10-15 minutes. Watch for errors.

- [ ] **Verify key packages**
  ```powershell
  (venv) python -c "import fastapi; import sqlalchemy; import openai; print('✅ All imports OK')"
  ```

- [ ] **Download Spacy model**
  ```powershell
  (venv) python -m spacy download en_core_web_sm
  ```
  Should show: Downloaded model successfully

---

## Phase 4: Configuration ✓

- [ ] **Copy environment template**
  ```powershell
  Copy-Item ".\.env.development" ".\.env" -Force
  ```

- [ ] **Verify .env file exists**
  ```powershell
  ls .\.env
  ```

- [ ] **(Optional) Add API keys to .env**
  Edit `.env` and add if you have them:
  ```
  OPENAI_API_KEY=sk-...
  ANTHROPIC_API_KEY=sk-...
  NEWS_API_KEY=...
  ```

---

## Phase 5: Database Setup ✓

- [ ] **Verify __init__.py files created**
  ```powershell
  ls "news-aggregator\src\core\__init__.py"
  ls "news-aggregator\src\services\__init__.py"
  ```
  Both should exist

- [ ] **Initialize database**
  ```powershell
  (venv) python scripts/init_db.py
  ```
  Should show: `✅ Database tables created successfully!`

- [ ] **Verify database file**
  ```powershell
  ls .\news_aggregator.db
  ```
  Should exist and have content

---

## Phase 6: Start Application ✓

Choose one method to start:

### Method 1: PowerShell Script (Recommended)
```powershell
powershell -ExecutionPolicy Bypass -File "scripts/start_dev.ps1"
```

### Method 2: Batch File
```powershell
cmd /c scripts\start_dev.bat
```

### Method 3: Manual
```powershell
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

✓ Look for these signs of success:
- `Uvicorn running on http://127.0.0.1:8000`
- No error messages in red
- Terminal doesn't hang

---

## Phase 7: Verification ✓

- [ ] **API is responsive**
  Open http://localhost:8000/docs
  Should see: Interactive API documentation

- [ ] **Root endpoint works**
  http://localhost:8000/
  Should see: `{"message": "Welcome to the News Aggregator API"}`

- [ ] **Database connected**
  In API docs, try GET /feeds
  Should return: `[]` (empty array, not an error)

- [ ] **Documentation available**
  - http://localhost:8000/docs (Swagger UI)
  - http://localhost:8000/redoc (ReDoc)

---

## Phase 8: Advanced Features (Optional) ✓

### Media Processing Setup

- [ ] **Install Tesseract OCR** (for image text extraction)
  - Download: https://github.com/UB-Mannheim/tesseract/wiki
  - Run installer
  - Add to .env: `TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe`
  - Verify: `tesseract --version`

- [ ] **Install FFmpeg** (for video/audio)
  ```powershell
  choco install ffmpeg
  ```
  Or download from: https://ffmpeg.org/download.html
  Verify: `ffmpeg -version`

### Background Tasks Setup (Optional)

- [ ] **Install Redis** (for Celery task queue)
  - Windows: https://github.com/microsoftarchive/redis/releases
  - Or use WSL: `wsl apt install redis-server`

- [ ] **Start Redis**
  ```powershell
  redis-server
  ```
  Should show: `Ready to accept connections`

- [ ] **Start Celery worker** (in new terminal)
  ```powershell
  (venv) celery -A news_aggregator.src.tasks.celery_app worker --loglevel=info
  ```

---

## 🎉 Success Criteria

You're ready when:
- [x] Virtual environment activates without errors
- [x] All packages install successfully
- [x] Database initializes
- [x] Server starts on port 8000
- [x] API documentation loads in browser
- [x] GET /feeds returns empty array (not error)

---

## 🆘 Issues?

### Problem: `ModuleNotFoundError`
**Solution:** 
```powershell
# Ensure venv is activated (see (venv) prefix)
.\venv\Scripts\Activate.ps1
```

### Problem: `Port 8000 in use`
**Solution:**
```powershell
# Use different port
uvicorn main:app --reload --port 8001
```

### Problem: `Database locked`
**Solution:**
```powershell
Remove-Item "news_aggregator.db" -Force
python scripts/init_db.py
```

### Problem: `Import errors with news_aggregator`
**Solution:**
```powershell
# Verify __init__.py files exist in all subdirs
Get-ChildItem -Recurse -Filter "__init__.py"
```

---

## 📚 Next Steps After Setup

1. ✅ **Read the code** - Explore `news-aggregator/src/`
2. ✅ **Try API endpoints** - Use http://localhost:8000/docs
3. ✅ **Add test data** - Create feeds and articles via API
4. ✅ **Review SETUP_DEVELOPMENT.md** - For full documentation
5. ✅ **Build frontend** - React app to interact with API
6. ✅ **Deploy** - Move to production setup

---

**Questions?** Check the error messages in your terminal, or review the SETUP_DEVELOPMENT.md file.

**Ready?** Let's go! 🚀