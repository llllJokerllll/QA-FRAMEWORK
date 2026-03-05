"""
Test Cache Implementation

Provides efficient caching for test results using Redis as backend.

Features:
- Fast key-value storage
- TTL support
- Pattern-based key matching
- Suite/test based cache invalidation
- Performance metrics
"""

import logging
import re
from typing import Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TestCache:
    """
    Cache implementation for test results.

    Uses Redis for distributed caching with support for:
    - Key-value storage with TTL
    - Pattern-based key matching
    - Suite/test based invalidation
    - Performance tracking
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize test cache.

        Args:
            redis_url: Redis connection URL (defaults to env var)
        """
        try:
            import redis
        except ImportError:
            raise ImportError("Redis is required. Install with: pip install redis")

        self.redis = redis.from_url(
            redis_url or "redis://localhost:6379/0",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        self._ping()

    def _ping(self):
        """Test Redis connection."""
        try:
            self.redis.ping()
            logger.info("Test cache: Redis connection established")
        except Exception as e:
            logger.error(f"Test cache: Redis connection failed: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = self.redis.get(key)

            if value is None:
                return None

            # Try to parse JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except Exception as e:
            logger.error(f"Test cache: Failed to get key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to store (will be JSON encoded)
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert value to JSON
            value_str = json.dumps(value, default=str)

            # Store with TTL
            self.redis.setex(key, ttl, value_str)

            return True

        except Exception as e:
            logger.error(f"Test cache: Failed to set key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis.delete(key)
            return True

        except Exception as e:
            logger.error(f"Test cache: Failed to delete key {key}: {e}")
            return False

    def clear_all(self):
        """Delete all keys from cache."""
        try:
            self.redis.flushdb()
            logger.warning("Test cache: All keys cleared")
        except Exception as e:
            logger.error(f"Test cache: Failed to clear cache: {e}")

    def get_keys_by_suite(self, test_suite_id: int) -> List[str]:
        """
        Get all cache keys for a specific test suite.

        Args:
            test_suite_id: Test suite ID

        Returns:
            List of cache keys
        """
        pattern = f"test_suite_{test_suite_id}_*"
        return self._get_keys_by_pattern(pattern)

    def get_keys_by_test(self, test_id: int) -> List[str]:
        """
        Get all cache keys for a specific test.

        Args:
            test_id: Test ID

        Returns:
            List of cache keys
        """
        pattern = f"*test_{test_id}"
        return self._get_keys_by_pattern(pattern)

    def get_keys_matching(self, pattern: str) -> List[str]:
        """
        Get all cache keys matching a pattern.

        Args:
            pattern: Redis key pattern (supports regex)

        Returns:
            List of matching cache keys
        """
        return self._get_keys_by_pattern(pattern)

    def _get_keys_by_pattern(self, pattern: str) -> List[str]:
        """
        Get keys matching a pattern (helper method).

        Args:
            pattern: Redis key pattern

        Returns:
            List of matching keys
        """
        try:
            keys = self.redis.keys(pattern)
            return [k.decode() if isinstance(k, bytes) else k for k in keys]
        except Exception as e:
            logger.error(f"Test cache: Failed to get keys for pattern {pattern}: {e}")
            return []

    def get_keys_by_prefix(self, prefix: str) -> List[str]:
        """
        Get all cache keys starting with a prefix.

        Args:
            prefix: Key prefix

        Returns:
            List of matching keys
        """
        pattern = f"{prefix}*"
        return self._get_keys_by_pattern(pattern)

    def get_key_age(self, key: str) -> Optional[float]:
        """
        Get age of cache entry in seconds.

        Args:
            key: Cache key

        Returns:
            Age in seconds or None if not found
        """
        try:
            ttl = self.redis.ttl(key)
            if ttl == -1:  # Key exists but has no expiry
                return None
            return ttl
        except Exception as e:
            logger.error(f"Test cache: Failed to get age for key {key}: {e}")
            return None

    def get_key_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a cache key.

        Args:
            key: Cache key

        Returns:
            Dictionary with key info or None if not found
        """
        try:
            ttl = self.redis.ttl(key)
            info = {
                "exists": ttl != -2,  # -2 means key doesn't exist
                "ttl": ttl if ttl != -1 else None,  # -1 means no expiry
            }

            if info["exists"]:
                info["value_type"] = self.redis.type(key)

            return info
        except Exception as e:
            logger.error(f"Test cache: Failed to get info for key {key}: {e}")
            return None

    def get_cache_size(self) -> int:
        """
        Get total number of cache entries.

        Returns:
            Number of entries
        """
        try:
            return len(self.redis.dbsize())
        except Exception as e:
            logger.error(f"Test cache: Failed to get cache size: {e}")
            return 0

    def get_memory_usage(self) -> int:
        """
        Get memory usage in bytes.

        Returns:
            Memory usage in bytes
        """
        try:
            info = self.redis.info("memory")
            return info.get("used_memory", 0)
        except Exception as e:
            logger.error(f"Test cache: Failed to get memory usage: {e}")
            return 0

    def get_all_keys(self) -> List[str]:
        """
        Get all cache keys.

        Returns:
            List of all keys
        """
        try:
            keys = self.redis.keys("*")
            return [k.decode() if isinstance(k, bytes) else k for k in keys]
        except Exception as e:
            logger.error(f"Test cache: Failed to get all keys: {e}")
            return []

    def get_tiered_stats(self) -> Dict[str, Any]:
        """
        Get tiered statistics about cache.

        Returns:
            Dictionary with statistics by prefix
        """
        try:
            stats = {}

            prefixes = [
                "test_suite_",
                "execution_",
                "execution_result_"
            ]

            for prefix in prefixes:
                pattern = f"{prefix}*"
                keys = self.redis.keys(pattern)
                stats[prefix] = {
                    "count": len(keys),
                    "memory_bytes": sum(len(self.redis.get(k)) if self.redis.get(k) else 0
                                       for k in keys) if keys else 0
                }

            return stats

        except Exception as e:
            logger.error(f"Test cache: Failed to get tiered stats: {e}")
            return {}

    def cleanup_expired(self) -> int:
        """
        Remove all expired keys.

        Returns:
            Number of keys removed
        """
        try:
            # This is handled by Redis's automatic expiration
            # We can't force-expire all keys without some logic
            # So we return 0 and let Redis handle it naturally
            logger.info("Test cache: Redis handles automatic expiration")
            return 0
        except Exception as e:
            logger.error(f"Test cache: Failed to cleanup expired keys: {e}")
            return 0


# Standalone fallback if Redis not available
class InMemoryCache:
    """
    In-memory fallback cache for development/testing.

    WARNING: NOT suitable for production use.
    """

    def __init__(self):
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str):
        """Get value from cache."""
        if key in self._cache:
            # Check if expired
            if key in self._timestamps:
                if (datetime.now() - self._timestamps[key]).total_seconds() > 3600:
                    del self._cache[key]
                    del self._timestamps[key]
                    return None
            return self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache."""
        self._cache[key] = value
        self._timestamps[key] = datetime.now()

    def delete(self, key: str):
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]

    def clear_all(self):
        """Clear all cache."""
        self._cache = {}
        self._timestamps = {}

    def get_keys_by_suite(self, test_suite_id: int) -> List[str]:
        """Get all keys for a suite."""
        return [k for k in self._cache.keys() if f"test_suite_{test_suite_id}" in k]

    def get_keys_by_test(self, test_id: int) -> List[str]:
        """Get all keys for a test."""
        return [k for k in self._cache.keys() if f"test_{test_id}" in k]

    def get_keys_matching(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        regex = re.compile(pattern.replace("*", ".*"))
        return [k for k in self._cache.keys() if regex.search(k)]

    def get_keys_by_prefix(self, prefix: str) -> List[str]:
        """Get keys by prefix."""
        return [k for k in self._cache.keys() if k.startswith(prefix)]

    def get_cache_size(self) -> int:
        """Get number of cache entries."""
        return len(self._cache)

    def get_memory_usage(self) -> int:
        """Get memory usage in bytes."""
        return sum(len(str(v)) for v in self._cache.values())

    def get_all_keys(self) -> List[str]:
        """Get all keys."""
        return list(self._cache.keys())

    def get_tiered_stats(self) -> Dict[str, Any]:
        """Get tiered statistics."""
        return {}

    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        now = datetime.now()
        expired = [
            k for k, t in self._timestamps.items()
            if (now - t).total_seconds() > 3600
        ]

        for key in expired:
            if key in self._cache:
                del self._cache[key]
            if key in self._timestamps:
                del self._timestamps[key]

        return len(expired)
