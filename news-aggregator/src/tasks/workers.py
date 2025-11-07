from celery import Celery
from src.core.config import settings

celery_app = Celery(
    'news_aggregator',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task
def fetch_articles():
    from src.services.fetcher import fetch_articles_from_sources
    fetch_articles_from_sources.delay()

@celery_app.task
def parse_article(article_id):
    from src.services.parser import parse_article
    parse_article(article_id)

@celery_app.task
def summarize_article(article_id):
    from src.services.summarizer import summarize_article
    summarize_article(article_id)