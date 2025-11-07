import re
from pathlib import Path

SCRAPERS_DIR = Path(__file__).resolve().parent.parent / "src" / "scrapers"
PAT_CLASS = re.compile(r"^class\s+([A-Za-z0-9_]+)\s*(\([^\)]*\))?\s*:")

def ensure_base_import_and_inheritance(path: Path):
    text = path.read_text(encoding="utf-8")
    changed = False

    # Ensure import of BaseScraper
    if "from .base_scraper import BaseScraper" not in text:
        text = "from .base_scraper import BaseScraper\n" + text
        changed = True

    lines = text.splitlines()
    new_lines = []
    for line in lines:
        m = PAT_CLASS.match(line)
        if m:
            cls_name, paren = m.groups()
            if cls_name.endswith("Scraper"):
                # If no inheritance or doesn't include BaseScraper, add it
                if not paren or "BaseScraper" not in paren:
                    new_line = f"class {cls_name}(BaseScraper):"
                    new_lines.append(new_line)
                    changed = True
                    continue
        new_lines.append(line)

    if changed:
        path.write_text("\n".join(new_lines), encoding="utf-8")
        print(f"Patched: {path.name}")
    else:
        print(f"No changes: {path.name}")

def main():
    if not SCRAPERS_DIR.exists():
        print("Scrapers directory not found:", SCRAPERS_DIR)
        return
    for p in SCRAPERS_DIR.glob("scraper_*.py"):
        ensure_base_import_and_inheritance(p)

if __name__ == "__main__":
    main()