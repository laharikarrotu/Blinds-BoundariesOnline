"""LRU Cache implementation with TTL support."""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
from threading import Lock
import time


class LRUCache:
    """
    Thread-safe LRU Cache with TTL support.
    Uses OrderedDict for O(1) operations.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize LRU Cache.
        
        Args:
            max_size: Maximum number of items
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache.
        O(1) time complexity.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expiry = self._cache[key]
            
            # Check if expired
            if time.time() > expiry:
                del self._cache[key]
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set item in cache.
        O(1) time complexity.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            ttl = ttl or self.default_ttl
            expiry = time.time() + ttl
            
            if key in self._cache:
                # Update existing
                self._cache.move_to_end(key)
            elif len(self._cache) >= self.max_size:
                # Evict least recently used
                self._cache.popitem(last=False)
            
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> bool:
        """
        Delete item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if current_time > expiry
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)


# Global cache instance
cache = LRUCache(max_size=1000, default_ttl=3600)

