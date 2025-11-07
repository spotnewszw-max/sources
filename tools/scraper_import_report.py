import importlib
import traceback
from pathlib import Path
from collections import defaultdict

SCRAPERS_DIR = Path(__file__).resolve().parent.parent / "src" / "scrapers"

def try_import(module_name: str):
    try:
        importlib.import_module(module_name)
        return None
    except Exception as e:
        tb = traceback.format_exc()
        return tb

def analyze():
    failures = {}
    for p in sorted(SCRAPERS_DIR.glob("scraper_*.py")):
        module_name = f"src.scrapers.{p.stem}"
        tb = try_import(module_name)
        if tb:
            # Extract first ImportError / ModuleNotFoundError line
            failures[module_name] = tb.splitlines()[:12]
    return failures

def print_report(failures):
    if not failures:
        print("All scraper modules imported successfully.")
        return
    print("Import failures for scrapers:\n")
    missing_packages = defaultdict(set)
    for module, tb_lines in failures.items():
        print(f"--- {module} ---")
        for line in tb_lines:
            print(line)
            if "ModuleNotFoundError" in line or "ImportError" in line:
                # very rough extraction of missing name
                parts = line.split("No module named")
                if len(parts) > 1:
                    name = parts[1].strip().strip(" '\"")
                    missing_packages[name].add(module)
        print()
    if missing_packages:
        print("Top-level missing packages/modules (aggregated):")
        for pkg, mods in missing_packages.items():
            print(f"  {pkg}  -> referenced by {len(mods)} scrapers")
    else:
        print("No clear top-level missing package names found; inspect the individual tracebacks above.")

if __name__ == "__main__":
    failures = analyze()
    print_report(failures)