import time
import hashlib
import threading
from typing import Dict, Any, Optional, Tuple
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class LRUCache:
    """Thread-safe LRU cache with TTL support and size limits."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 900):  # 15 minutes default
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, token: str, query: str) -> str:
        """Generate cache key from token and query."""
        # Use full SHA-256 hash to prevent collisions (64 hex chars = 256 bits)
        # Combining token + query ensures unique keys per user per search
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        query_normalized = query.lower().strip()
        return f"groups_{token_hash}_{query_normalized}"
    
    def get(self, token: str, query: str) -> Optional[Any]:
        """Get cached value if not expired."""
        key = self._generate_key(token, query)
        
        with self._lock:
            if key not in self.cache:
                self._misses += 1
                return None
            
            return self._process_cached_entry(key, query)

    def _process_cached_entry(self, key: str, query: str) -> Optional[Any]:
        """Process cached entry and return value if not expired."""
        value, timestamp = self.cache[key]
        current_time = time.time()
        
        if current_time - timestamp < self.default_ttl:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self._hits += 1
            logger.debug(f"Cache hit for query: {query}")
            return value
        else:
            # Remove expired entry
            del self.cache[key]
            self._misses += 1
            logger.debug(f"Cache expired for query: {query}")
            return None
    
    def set(self, token: str, query: str, value: Any) -> None:
        """Set cache value with current timestamp."""
        key = self._generate_key(token, query)
        
        with self._lock:
            # Remove oldest entries if cache is full
            while len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                logger.debug(f"Evicted oldest cache entry: {oldest_key}")
            
            self.cache[key] = (value, time.time())
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            logger.debug(f"Cached result for query: {query} (cache size: {len(self.cache)})")
    
    def clear_expired(self) -> int:
        """Clear all expired entries and return count of removed items."""
        with self._lock:
            current_time = time.time()
            expired_keys = self._find_expired_keys(current_time)
            self._remove_expired_keys(expired_keys)
            self._log_cleanup_results(expired_keys)
            return len(expired_keys)

    def _find_expired_keys(self, current_time: float) -> list:
        """Find all expired cache keys."""
        return [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.default_ttl
        ]

    def _remove_expired_keys(self, expired_keys: list) -> None:
        """Remove expired keys from cache."""
        for key in expired_keys:
            del self.cache[key]

    def _log_cleanup_results(self, expired_keys: list) -> None:
        """Log cache cleanup results."""
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self.cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self.cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': f'{hit_rate:.1f}%',
                'ttl': self.default_ttl
            }
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Estimate memory usage of cache."""
        import sys
        
        with self._lock:
            total_size = 0
            for key, (value, timestamp) in self.cache.items():
                total_size += sys.getsizeof(key)
                total_size += sys.getsizeof(value) 
                total_size += sys.getsizeof(timestamp)
            
            return {
                'entries': len(self.cache),
                'estimated_bytes': total_size,
                'estimated_mb': total_size / 1024 / 1024
            }


class CacheManager:
    """Manages multiple cache instances."""

    def __init__(self):
        from app.core.config import settings

        self.caches = {
            'groups': LRUCache(max_size=settings.cache_max_size_groups, default_ttl=settings.cache_ttl_groups),
            'projects': LRUCache(max_size=settings.cache_max_size_projects, default_ttl=settings.cache_ttl_projects),
            'templates': LRUCache(max_size=settings.cache_max_size_templates, default_ttl=settings.cache_ttl_templates),
        }
    
    def get_cache(self, cache_name: str) -> LRUCache:
        """Get cache instance by name."""
        return self.caches.get(cache_name)
    
    def cleanup_all(self) -> Dict[str, int]:
        """Cleanup expired entries in all caches."""
        results = {}
        for name, cache in self.caches.items():
            results[name] = cache.clear_expired()
        return results
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        return {name: cache.stats() for name, cache in self.caches.items()}
    
    def clear_all(self) -> None:
        """Clear all caches."""
        for cache in self.caches.values():
            cache.clear()
        logger.info("All caches cleared")


# Global cache instances
cache_manager = CacheManager()
groups_cache = cache_manager.get_cache('groups')
projects_cache = cache_manager.get_cache('projects')
templates_cache = cache_manager.get_cache('templates')