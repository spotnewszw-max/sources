import pytest
from src.parsers.parser import parse_article

def test_parse_article_valid():
    html_content = "<html><body><h1>Test Article</h1><p>This is a test article.</p></body></html>"
    expected_output = {
        "title": "Test Article",
        "content": "This is a test article."
    }
    assert parse_article(html_content) == expected_output

def test_parse_article_invalid():
    html_content = "<html><body></body></html>"
    expected_output = {
        "title": None,
        "content": None
    }
    assert parse_article(html_content) == expected_output

def test_parse_article_empty():
    html_content = ""
    expected_output = {
        "title": None,
        "content": None
    }
    assert parse_article(html_content) == expected_output