import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, Type, List

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)
SCRAPERS_DIR = Path(__file__).parent

class ScraperManager:
    """Load and register all Scraper classes found under src.scrapers"""
    def __init__(self):
        self.scrapers: Dict[str, Type[BaseScraper]] = {}
        self._load_scrapers()

    def _load_scrapers(self):
        # find python files
        for path in SCRAPERS_DIR.glob("scraper_*.py"):
            module_name = f"src.scrapers.{path.stem}"
            try:
                module = importlib.import_module(module_name)
            except Exception as e:
                logger.warning("Failed to import %s: %s", module_name, e)
                continue

            for name, obj in inspect.getmembers(module, inspect.isclass):
                # ensure class is defined in that module and is a Scraper subclass
                if obj.__module__ == module_name and name.endswith("Scraper"):
                    try:
                        if issubclass(obj, BaseScraper):
                            key = name.replace("Scraper", "").lower()
                            self.scrapers[key] = obj
                            logger.info("Registered scraper: %s -> %s.%s", key, module_name, name)
                        else:
                            logger.debug("Found scraper-like class not subclassing BaseScraper: %s.%s", module_name, name)
                    except Exception as e:
                        logger.debug("Skipping class %s in %s: %s", name, module_name, e)

    def get_scraper(self, name: str) -> Type[BaseScraper]:
        key = name.lower()
        if key not in self.scrapers:
            raise KeyError(f"Scraper '{name}' not found")
        return self.scrapers[key]

    def list_scrapers(self) -> List[str]:
        return sorted(self.scrapers.keys())

# singleton
scraper_manager = ScraperManager()