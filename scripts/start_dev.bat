@echo off
REM Start Development Server for News Aggregator (Windows Batch)
REM This is a simpler alternative if PowerShell gives issues

cd /d "%~dp0\.."

echo.
echo 🚀 Starting News Aggregator Development Server...
echo.

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check and copy .env file
if not exist ".env" (
    echo ⚙️  Creating .env from template...
    if exist ".env.development" (
        copy ".env.development" ".env" >nul
    )
)

REM Initialize database if needed
if not exist "news_aggregator.db" (
    echo 🗄️  Initializing database...
    python scripts\init_db.py
)

REM Start server
echo.
echo ✨ Starting uvicorn server on http://localhost:8000
echo 📖 API Documentation: http://localhost:8000/docs
echo 📘 Alternative Docs: http://localhost:8000/redoc
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause