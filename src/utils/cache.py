from redis import Redis, ConnectionError, TimeoutError
from functools import wraps, lru_cache
import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional
from threading import Lock
import logging
import fnmatch
from dataclasses import dataclass, field
from collections import Counter
from time import time

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Cache statistics tracker"""
    hits: int = 0
    misses: int = 0
    keys_count: int = 0
    operations: Counter = field(default_factory=Counter)
    last_cleanup: float = field(default_factory=time)
    
    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": f"{self.hit_ratio:.2%}",
            "keys_count": self.keys_count,
            "operations": dict(self.operations),
            "last_cleanup": datetime.fromtimestamp(self.last_cleanup).isoformat()
        }

class LocalCache:
    """Simple thread-safe in-memory cache with monitoring"""
    def __init__(self):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._lock = Lock()
        self.stats = CacheStats()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self.stats.operations['get'] += 1
            if key not in self._cache:
                self.stats.misses += 1
                return None
            
            value, expiry = self._cache[key]
            if datetime.now() > expiry:
                del self._cache[key]
                self.stats.misses += 1
                return None
            
            self.stats.hits += 1
            return value

    def set(self, key: str, value: Any, expire_seconds: int):
        with self._lock:
            self.stats.operations['set'] += 1
            expiry = datetime.now() + timedelta(seconds=expire_seconds)
            self._cache[key] = (value, expiry)
            self.stats.keys_count = len(self._cache)

    def invalidate(self, pattern: str):
        with self._lock:
            self.stats.operations['invalidate'] += 1
            fnmatch_pattern = pattern.replace('*', '*')
            keys_to_delete = [
                k for k in list(self._cache.keys())
                if fnmatch.fnmatch(k, fnmatch_pattern)
            ]
            for key in keys_to_delete:
                del self._cache[key]
            
            if keys_to_delete:
                self.stats.keys_count = len(self._cache)
                logger.info(f"Invalidated {len(keys_to_delete)} keys matching '{pattern}'")
            return len(keys_to_delete)

    def get_stats(self) -> Dict[str, Any]:
        """Get current cache statistics"""
        with self._lock:
            return self.stats.to_dict()

    def cleanup(self, max_age: int = 3600) -> int:
        """Remove expired entries"""
        with self._lock:
            self.stats.operations['cleanup'] += 1
            now = datetime.now()
            expired = [
                k for k, v in self._cache.items()
                if now > v[1]
            ]
            for key in expired:
                del self._cache[key]
            
            self.stats.keys_count = len(self._cache)
            self.stats.last_cleanup = time()
            return len(expired)

class CacheManager:
    """Cache manager with Redis and local fallback"""
    def __init__(self, use_redis: bool = True):
        self.redis_client = None
        self.local_cache = LocalCache()
        self.use_redis = use_redis
        if use_redis:
            self._try_connect()

    def _try_connect(self):
        """Attempt Redis connection with shorter timeout"""
        try:
            self.redis_client = Redis(
                host='localhost',
                port=6379,
                socket_timeout=1,
                socket_connect_timeout=1,
                retry_on_timeout=False
            )
            self.redis_client.ping()
            logger.info("✅ Connected to Redis successfully")
        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            logger.info("🔄 Falling back to local cache")
            self.redis_client = None

    def get(self, key: str) -> Any:
        # Try Redis if available
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
            except Exception as e:
                logger.debug(f"Redis get failed: {e}")

        # Fallback to local cache
        return self.local_cache.get(key)

    def set(self, key: str, value: Any, expire_seconds: int):
        # Try Redis if available
        if self.redis_client:
            try:
                pickled_value = pickle.dumps(value)
                self.redis_client.setex(key, expire_seconds, pickled_value)
                return
            except Exception as e:
                logger.debug(f"Redis set failed: {e}")

        # Fallback to local cache
        self.local_cache.set(key, value, expire_seconds)

    def invalidate(self, pattern: str):
        # Try Redis if available
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Invalidated {len(keys)} Redis cache keys")
                return
            except Exception as e:
                logger.debug(f"Redis invalidation failed: {e}")

        # Fallback to local cache
        self.local_cache.invalidate(pattern)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.local_cache.get_stats()
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats["redis"] = {
                    "connected": True,
                    "used_memory": info["used_memory_human"],
                    "connected_clients": info["connected_clients"],
                    "uptime": info["uptime_in_seconds"]
                }
            except Exception as e:
                stats["redis"] = {"connected": False, "error": str(e)}
        return stats

    def cleanup(self) -> int:
        """Run cache cleanup"""
        count = self.local_cache.cleanup()
        logger.info(f"Cleaned up {count} expired cache entries")
        return count

# Initialize cache singleton with Redis disabled for now
cache = CacheManager(use_redis=False)

def cache_response(expire_seconds: int = 300, cleanup_threshold: int = 1000):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Run cleanup if too many keys
            if cache.local_cache.stats.keys_count > cleanup_threshold:
                cache.cleanup()
                
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args))}-{hash(str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                return pickle.loads(cached_result)
            
            # Execute function if not cached
            result = await func(*args, **kwargs)
            
            # Cache the result
            cache.set(
                cache_key,
                pickle.dumps(result),
                expire_seconds
            )
            
            return result
        return wrapper
    return decorator