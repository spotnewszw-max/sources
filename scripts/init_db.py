#!/usr/bin/env python
"""
Initialize the database schema for development
Run from project root: python scripts/init_db.py
"""
import sys
import os
from pathlib import Path

# Get absolute path to project root
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Ensure we're running from project root
os.chdir(project_root)

from src.database.base import Base, engine
from src.models.article import Article  # Import models to register them

def init_db():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully!")
        print(f"Database file created at: {project_root / 'news_aggregator.db'}")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Project root: {project_root}")

if __name__ == "__main__":
    init_db()