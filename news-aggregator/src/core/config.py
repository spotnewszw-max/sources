import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = os.getenv("APP_NAME", "News Aggregator")
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "t")
    
    # Database - defaults to SQLite for development
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        database_url = "sqlite:///./news_aggregator.db"
    DATABASE_URL = database_url
    
    # Redis & Celery
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # API Keys (optional for development)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    
    # Other settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Processing settings
    SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")
    ENABLE_MEDIA_PROCESSING = os.getenv("ENABLE_MEDIA_PROCESSING", "true").lower() in ("true", "1", "t")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")