import pytest
from src.services.fetcher import fetch_articles

def test_fetch_articles_valid_source():
    source = "https://valid-news-source.com/rss"
    articles = fetch_articles(source)
    assert isinstance(articles, list)
    assert len(articles) > 0

def test_fetch_articles_invalid_source():
    source = "https://invalid-news-source.com/rss"
    articles = fetch_articles(source)
    assert articles == []

def test_fetch_articles_empty_source():
    source = ""
    articles = fetch_articles(source)
    assert articles == []