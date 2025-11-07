from functools import wraps
from src.utils.cache import cache
from datetime import datetime
import hashlib
import json
from typing import Any, Callable
from datetime import datetime

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a stable cache key for scraper results"""
    # Create a stable representation of args and kwargs
    key_dict = {
        "args": args,
        "kwargs": kwargs,
        "date": datetime.now().strftime("%Y-%m-%d"),  # Daily cache key
    }

    # Use json.dumps with a safe default to handle non-serializable objects (e.g. scraper self)
    key_json = json.dumps(key_dict, sort_keys=True, default=lambda o: repr(o))
    key_hash = hashlib.md5(key_json.encode()).hexdigest()[:12]

    return f"scraper:{prefix}:{key_hash}"

def cache_scraper(prefix: str, expire_seconds: int = 3600):
    """Cache decorator for scraper functions"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result

            # Execute scraper if not cached
            result = await func(*args, **kwargs)

            # Cache the result
            cache.set(cache_key, result, expire_seconds)

            return result
        return wrapper
    return decorator

def invalidate_scraper_cache(prefix: str = None):
    """Invalidate all scraper cache entries or those matching prefix"""
    pattern = f"scraper:{prefix}:*" if prefix else "scraper:*"
    cache.invalidate(pattern)