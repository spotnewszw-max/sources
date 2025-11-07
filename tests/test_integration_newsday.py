from pathlib import Path
import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "newsday" / "sample_article.html"

def test_newsday_extract_from_fixture():
    """Integration test: ensure scraper_newsday can extract content from fixture."""
    mod = pytest.importorskip("src.scrapers.scraper_newsday")
    html = FIXTURE.read_text(encoding="utf-8")
    if hasattr(mod, "extract_article_content"):
        out = mod.extract_article_content(html)
        assert out is not None
    elif hasattr(mod, "parse_article"):
        out = mod.parse_article(html)
        assert out is not None
    else:
        pytest.skip("No extract function found in scraper_newsday")
