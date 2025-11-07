"""
Main entry point for the News Aggregator application
This allows running: uvicorn main:app --reload
"""
import os
import sys
from pathlib import Path

# Ensure we can import from news-aggregator/src
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "news-aggregator"))

# Set default database if not configured
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///./news_aggregator.db"

# Import and return the app
from news_aggregator.src.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)