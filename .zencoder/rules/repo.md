---
description: Repository Information Overview
alwaysApply: true
---

# Repository Information Overview

## Repository Summary

The Sources Media project is a comprehensive news aggregation and content analysis system built with Python and FastAPI. It provides REST APIs for fetching, parsing, and analyzing news articles from multiple sources with advanced features including AI-powered content processing, media handling, document analysis, and web scraping capabilities. The system supports both SQLite (development) and PostgreSQL (production) databases, with optional async task processing via Celery and Redis.

## Repository Structure

The repository is organized as a multi-project system with the following main components:

### Main Repository Components
- **news-aggregator**: Core application module with FastAPI backend, database models, API routers, and services
- **Root Application**: Main entry point (main.py) that wraps and runs the news-aggregator
- **Utilities**: Helper modules for storage (storage.py) and database initialization
- **Scripts**: Deployment and development automation scripts
- **Configuration**: Environment configuration files and YAML-based application settings
- **Database**: SQL initialization scripts and migrations

---

## Projects

### News Aggregator (Main Application)
**Configuration File**: requirements.txt, .env.development, configs/default.yaml

#### Language & Runtime
**Language**: Python
**Version**: 3.13.5
**Build System**: pip/setuptools
**Package Manager**: pip
**Framework**: FastAPI 0.104.1, Uvicorn 0.24.0

#### Dependencies
**Web & API**:
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- python-multipart==0.0.6

**Database**:
- sqlalchemy==2.0.23
- psycopg2-binary==2.9.9
- alembic==1.12.1

**Async & HTTP**:
- aiohttp==3.9.1
- aiofiles==23.2.1
- httpx==0.25.2

**Task Queue**:
- celery==5.3.4
- redis==5.0.1

**AI & ML**:
- openai==1.3.7
- anthropic==0.7.1
- transformers==4.35.2
- torch==2.1.1
- spacy==3.7.2

**Media Processing**:
- Pillow==10.1.0
- pytesseract==0.3.10
- openai-whisper==20231117
- moviepy==1.0.3
- pydub==0.25.1

**Document Processing**:
- python-docx==1.1.0
- PyPDF2==3.0.1
- mammoth==1.6.0
- openpyxl==3.1.2

**Web Scraping**:
- beautifulsoup4==4.12.2
- feedparser==6.0.10
- lxml==4.9.3
- selenium==4.14.0

**Utilities**:
- python-dotenv==1.0.0
- pydantic==2.5.2
- pydantic-settings==2.1.0
- apscheduler==3.10.4

**Development & Testing**:
- pytest==7.4.3
- pytest-asyncio==0.21.1

#### Main Files & Entry Points
- **Root Entry Point**: main.py (uvicorn main:app --reload)
- **Application Core**: news-aggregator/src/app.py (FastAPI app initialization)
- **API Routes**: 
  - news-aggregator/src/api/routers/feeds.py
  - news-aggregator/src/api/routers/articles.py
  - news-aggregator/src/api/routers/article_requests.py
- **Services**: 
  - article_request_service.py
  - think_tank.py
  - web_scraper.py
  - unified_analyzer.py
  - content_filter.py
  - fetcher.py
- **Database Models**: news-aggregator/src/db/models.py
- **Database Session**: news-aggregator/src/db/session.py

#### Build & Installation
`ash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\\venv\\Scripts\\Activate.ps1
# Windows Command Prompt:
venv\\Scripts\\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Run application
uvicorn main:app --reload

# Or use startup scripts
powershell -ExecutionPolicy Bypass -File scripts/start_dev.ps1
`

#### Docker
**Dockerfile**: news-aggregator/docker/Dockerfile
**Base Image**: python:3.9-slim
**Working Directory**: /app
**Exposed Port**: 8000
**Container Command**: uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload

**Docker Compose**: news-aggregator/docker/docker-compose.yml
- **Web Service**: FastAPI application on port 8000
- **Database Service**: PostgreSQL 13
- **Volumes**: src code, db_data persistence

#### Configuration
**Development Config**: .env.development
- Environment: development
- Debug: True
- Database: SQLite (sqlite:///./news_aggregator.db)
- Redis: localhost:6379/0
- API Keys: Optional (OpenAI, Anthropic, News API)

**YAML Config**: news-aggregator/configs/default.yaml
- Application metadata and logging
- Database connection settings
- API prefix and documentation URLs
- Celery broker and result backend
- CORS settings

#### Testing
**Framework**: pytest, pytest-asyncio
**Test Location**: news-aggregator/tests/
**Naming Convention**: test_*.py
**Test Files**:
- test_api.py - API endpoint tests
- test_fetcher.py - Data fetching tests
- test_parser.py - Content parsing tests

**Test Configuration**:
- Async test support via pytest-asyncio
- TestClient from fastapi.testclient for API testing

**Run Tests**:
`ash
pytest
pytest news-aggregator/tests/
pytest -v --asyncio-mode=auto
`

#### Database
**Migrations**: Alembic-based (news-aggregator/migrations/)
**Models**: SQLAlchemy ORM models in news-aggregator/src/db/models.py
**Initialization**: scripts/init_db.py

`ash
# Run migrations
sh news-aggregator/scripts/migrate.sh
`

#### API Endpoints
**Base URL**: http://localhost:8000
**API Documentation**: http://localhost:8000/docs (Swagger UI)
**ReDoc**: http://localhost:8000/redoc
**Health Check**: GET /
**Feeds**: /feeds/* (feed management)
**Articles**: /articles/* (article CRUD operations)
**Article Requests**: /article_requests/* (user content requests)
**Think Tank**: API endpoint for advanced analysis features

#### Deployment
**Scripts**:
- scripts/start_dev.bat - Windows batch startup
- scripts/start_dev.ps1 - Windows PowerShell startup
- scripts/deploy_hostinger.sh - Hostinger deployment
- news-aggregator/scripts/run.sh - Shell runtime script
- news-aggregator/scripts/migrate.sh - Database migration script

#### System Requirements
- Python 3.9+
- PostgreSQL 13 (production)
- Redis server (for Celery/async tasks)
- Tesseract OCR (optional, for document OCR)
- FFmpeg (optional, for media processing)

---

## Development Workflow

**Quick Start**:
1. Activate virtual environment
2. Install dependencies: pip install -r requirements.txt
3. Initialize database: python scripts/init_db.py
4. Run development server: uvicorn main:app --reload
5. Access API docs: http://localhost:8000/docs

**For Production**:
1. Set up PostgreSQL database
2. Configure Redis server
3. Deploy using Docker: docker-compose up -d
4. Run migrations: sh scripts/migrate.sh
5. Start application with proper environment variables

---

## Key Features
- Multi-source news collection (RSS, APIs, web scraping)
- AI-powered content analysis and summarization
- Document and media processing (OCR, transcription, video analysis)
- Asynchronous task processing with Celery
- RESTful API with comprehensive documentation
- Database persistence and migration support
- Containerized deployment with Docker
