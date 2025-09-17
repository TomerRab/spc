import time
import hashlib
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 900):  # 15 minutes default
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, token: str, query: str) -> str:
        """Generate cache key from token and query."""
        # Hash token for security, keep query readable
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        return f"groups_{token_hash}_{query.lower()}"
    
    def get(self, token: str, query: str) -> Optional[Any]:
        """Get cached value if not expired."""
        key = self._generate_key(token, query)
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.default_ttl:
                logger.info(f"Cache hit for query: {query}")
                return value
            else:
                # Remove expired entry
                del self.cache[key]
                logger.info(f"Cache expired for query: {query}")
        
        return None
    
    def set(self, token: str, query: str, value: Any) -> None:
        """Set cache value with current timestamp."""
        key = self._generate_key(token, query)
        self.cache[key] = (value, time.time())
        logger.info(f"Cached result for query: {query} (cache size: {len(self.cache)})")
    
    def clear_expired(self) -> int:
        """Clear all expired entries and return count of removed items."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.default_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


# Global cache instance
groups_cache = SimpleCache(default_ttl=900)  # 15 minutes