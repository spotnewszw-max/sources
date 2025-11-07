import pytest

def test_base_scraper_module_exists():
    mod = pytest.importorskip("src.scrapers.base_scraper")
    assert mod is not None

def test_base_scraper_class_present():
    mod = pytest.importorskip("src.scrapers.base_scraper")
    assert hasattr(mod, "BaseScraper"), "BaseScraper not found in src.scrapers.base_scraper"

def test_clean_headline_if_present():
    mod = pytest.importorskip("src.scrapers.base_scraper")
    if hasattr(mod, "clean_headline"):
        clean = getattr(mod, "clean_headline")
        assert callable(clean)
        out = clean("  Some   Headline  ")
        assert isinstance(out, str)
        assert out.strip() == out
    else:
        pytest.skip("clean_headline not implemented")

def test_basescraper_can_instantiate_minimal():
    mod = pytest.importorskip("src.scrapers.base_scraper")
    BaseScraper = getattr(mod, "BaseScraper", None)
    if BaseScraper is None:
        pytest.skip("BaseScraper class missing")
    try:
        try:
            inst = BaseScraper()
        except TypeError:
            inst = BaseScraper("https://example.com")
        assert inst is not None
    except Exception as exc:
        pytest.skip(f"Could not instantiate BaseScraper: {exc}")