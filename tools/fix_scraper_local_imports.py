from pathlib import Path
import re
import logging
import argparse
import json
import shutil
from typing import Dict, List, Tuple, Callable

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

SCRAPERS_DIR = Path(__file__).resolve().parent.parent / "src" / "scrapers"
TRACKING_FILE = Path(__file__).parent / ".modified_files.json"

REPLACEMENTS: List[Tuple[str, str]] = [
    (r"(?m)^\s*from\s+src\.utils\.base_scraper\s+import", "from src.scrapers.base_scraper import"),
    (r"(?m)^\s*from\s+src\.utils\.scraper_enhanced\s+import", "from src.scrapers.base_scraper import"),
    (r"(?m)^\s*from\s+src\.utils\.scraper\s+import", "from src.scrapers.base_scraper import"),
    (r"(?m)^\s*from\s+src\.utils\.crawler\s+import", "from src.scrapers.base_scraper import"),
    (r"(?m)^\s*from\s+src\.utils\.image_extraction_optimizer\s+import", "from src.utils.image_utils import"),
    (r"(?m)^\s*from\s+src\.utils\.image_extractor\s+import", "from src.utils.image_utils import"),
    (r"(?m)^\s*from\s+src\.utils\.ssl_fix\s+import", "from src.utils.ssl_utils import"),
    (r"(?m)^\s*from\s+src\.utils\.smart_tools\s+import", "from src.utils.smart_utils import"),
]

def load_modified_files() -> set:
    if TRACKING_FILE.exists():
        try:
            return set(json.loads(TRACKING_FILE.read_text()))
        except Exception as e:
            logger.warning(f"Error loading tracking file: {e}")
    return set()

def save_modified_files(files: set):
    try:
        TRACKING_FILE.write_text(json.dumps(list(files)))
    except Exception as e:
        logger.warning(f"Error saving tracking file: {e}")

def preview_changes(path: Path) -> Dict[int, Tuple[str, str]]:
    changes: Dict[int, Tuple[str, str]] = {}
    try:
        original = path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading {path.name}: {e}")
        return {}
    new = original
    for pattern, repl in REPLACEMENTS:
        new = re.sub(pattern, repl, new)
    if new == original:
        return {}
    orig_lines = original.splitlines()
    new_lines = new.splitlines()
    max_lines = max(len(orig_lines), len(new_lines))
    for i in range(max_lines):
        o = orig_lines[i] if i < len(orig_lines) else ""
        n = new_lines[i] if i < len(new_lines) else ""
        if o != n:
            changes[i + 1] = (o, n)
    return changes

def make_backup(path: Path, index: int = 0) -> Path:
    if index == 0:
        backup_path = path.with_suffix(path.suffix + '.bak')
    else:
        backup_path = path.with_suffix(f"{path.suffix}.bak.{index}")
    if backup_path.exists():
        return make_backup(path, index + 1)
    return backup_path

def fix_file(path: Path, dry_run: bool = False) -> bool:
    try:
        changes = preview_changes(path)
        if not changes:
            return False
        if dry_run:
            logger.info(f"\nPreview changes for {path.name}:")
            for line_num, (old, new) in sorted(changes.items()):
                logger.info(f"Line {line_num}:")
                logger.info(f"  - {old}")
                logger.info(f"  + {new}\n")
            return True
        original = path.read_text(encoding="utf-8")
        new = original
        for pattern, repl in REPLACEMENTS:
            new = re.sub(pattern, repl, new)
        backup_path = make_backup(path)
        shutil.copy2(path, backup_path)
        path.write_text(new, encoding="utf-8")
        logger.info(f"Updated {path.name} (backup at {backup_path.name})")
        modified_files = load_modified_files()
        modified_files.add(path.name)
        save_modified_files(modified_files)
        return True
    except Exception as e:
        logger.error(f"Error updating {path.name}: {e}")
        return False

def restore_file(path: Path) -> bool:
    modified_files = load_modified_files()
    if path.name not in modified_files:
        return False
    backup = path.with_suffix(path.suffix + '.bak')
    if not backup.exists():
        return False
    try:
        shutil.copy2(backup, path)
        backup.unlink()
        modified_files.remove(path.name)
        save_modified_files(modified_files)
        logger.info(f"Restored {path.name}")
        return True
    except Exception as e:
        logger.error(f"Error restoring {path.name}: {e}")
        return False

def cleanup_backups():
    count = 0
    for p in SCRAPERS_DIR.glob("*.bak*"):
        try:
            p.unlink()
            count += 1
        except Exception as e:
            logger.error(f"Error removing {p.name}: {e}")
    if TRACKING_FILE.exists():
        TRACKING_FILE.unlink()
    logger.info(f"Removed {count} backup files")

def main():
    parser = argparse.ArgumentParser(description='Fix imports in scraper files')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--restore', '-r', action='store_true', help='Restore from backup files')
    parser.add_argument('--cleanup', '-c', action='store_true', help='Remove all backup files')
    parser.add_argument('--list', '-l', action='store_true', help='List modified files')
    args = parser.parse_args()
    scraper_files = sorted(SCRAPERS_DIR.glob("scraper_*.py"))
    logger.info(f"Found {len(scraper_files)} scraper files")
    if args.list:
        modified = load_modified_files()
        if modified:
            logger.info("Modified files:")
            for f in sorted(modified):
                logger.info(f"  {f}")
        else:
            logger.info("No files have been modified")
        return
    if args.cleanup:
        cleanup_backups()
        return
    if args.restore:
        restored = 0
        for p in scraper_files:
            if restore_file(p):
                restored += 1
        logger.info(f"Done. Restored {restored} files.")
        return
    changed = 0
    for p in scraper_files:
        if fix_file(p, dry_run=args.dry_run):
            changed += 1
    action = "Would change" if args.dry_run else "Changed"
    logger.info(f"Done. {action} {changed} files.")

if __name__ == "__main__":
    main()