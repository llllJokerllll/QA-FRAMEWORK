"""
Cache Statistics Tracker

Tracks cache performance metrics for monitoring and optimization.

Metrics tracked:
- Hit rate
- Hit/miss latency
- Memory usage
- Cache size
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class CacheStats:
    """
    Track cache statistics and performance metrics.

    Provides methods to record and query cache performance.
    """

    def __init__(self):
        """Initialize statistics tracker."""
        self.hits = 0
        self.misses = 0
        self.hit_times = []  # List of hit times in ms
        self.miss_times = []  # List of miss times in ms
        self.errors = 0
        self.start_time = datetime.now()

        # Track per-key metrics
        self.key_metrics = defaultdict(lambda: {
            "hits": 0,
            "misses": 0,
            "last_hit": None,
            "total_hit_time": 0.0,
            "total_miss_time": 0.0
        })

        self._initialized = True

    def record_hit(
        self,
        key: str,
        duration_ms: Optional[float] = None
    ):
        """
        Record a cache hit.

        Args:
            key: Cache key
            duration_ms: Time taken to retrieve (optional)
        """
        self.hits += 1

        if key in self.key_metrics:
            self.key_metrics[key]["hits"] += 1
            self.key_metrics[key]["last_hit"] = datetime.now()

        if duration_ms is not None:
            self.hit_times.append(duration_ms)

            if key in self.key_metrics:
                self.key_metrics[key]["total_hit_time"] += duration_ms

    def record_miss(
        self,
        key: str,
        duration_ms: Optional[float] = None
    ):
        """
        Record a cache miss.

        Args:
            key: Cache key
            duration_ms: Time taken to execute (optional)
        """
        self.misses += 1

        if key in self.key_metrics:
            self.key_metrics[key]["misses"] += 1

        if duration_ms is not None:
            self.miss_times.append(duration_ms)

            if key in self.key_metrics:
                self.key_metrics[key]["total_miss_time"] += duration_ms

    def record_error(self):
        """Record a cache error."""
        self.errors += 1

    def get_hit_rate(self) -> float:
        """
        Calculate hit rate as percentage.

        Returns:
            Hit rate (0-100) or 0 if no operations
        """
        total = self.hits + self.misses

        if total == 0:
            return 0.0

        return (self.hits / total) * 100

    def get_average_hit_time(self) -> float:
        """
        Get average hit time in ms.

        Returns:
            Average hit time in milliseconds
        """
        if not self.hit_times:
            return 0.0

        return sum(self.hit_times) / len(self.hit_times)

    def get_average_miss_time(self) -> float:
        """
        Get average miss time in ms.

        Returns:
            Average miss time in milliseconds
        """
        if not self.miss_times:
            return 0.0

        return sum(self.miss_times) / len(self.miss_times)

    def get_total_requests(self) -> int:
        """Get total number of requests (hits + misses)."""
        return self.hits + self.misses

    def get_memory_usage(self, test_cache) -> int:
        """
        Get memory usage in bytes.

        Args:
            test_cache: TestCache instance

        Returns:
            Memory usage in bytes
        """
        try:
            return test_cache.get_memory_usage()
        except Exception:
            # Fallback to manual calculation
            return sum(len(str(test_cache.get(k))) if test_cache.get(k) else 0
                      for k in test_cache.get_all_keys())

    def get_cache_size(self, test_cache) -> int:
        """
        Get cache size (number of entries).

        Args:
            test_cache: TestCache instance

        Returns:
            Number of cache entries
        """
        try:
            return test_cache.get_cache_size()
        except Exception:
            # Fallback to manual calculation
            return len(test_cache.get_all_keys())

    def get_most_hit_keys(self, top_n: int = 5) -> list[Dict[str, Any]]:
        """
        Get the most hit cache keys.

        Args:
            top_n: Number of top keys to return

        Returns:
            List of top keys with metrics
        """
        sorted_keys = sorted(
            self.key_metrics.items(),
            key=lambda x: x[1]["hits"],
            reverse=True
        )

        return [
            {
                "key": key,
                "hits": metrics["hits"],
                "misses": metrics["misses"],
                "hit_rate": (metrics["hits"] / (metrics["hits"] + metrics["misses"]) * 100
                           if (metrics["hits"] + metrics["misses"]) > 0 else 0),
                "avg_hit_time": (metrics["total_hit_time"] / metrics["hits"]
                               if metrics["hits"] > 0 else 0),
                "last_hit": metrics["last_hit"].isoformat() if metrics["last_hit"] else None
            }
            for key, metrics in sorted_keys[:top_n]
        ]

    def get_most_important_keys(self, test_cache) -> list[Dict[str, Any]]:
        """
        Get most important keys based on usage patterns.

        Args:
            test_cache: TestCache instance

        Returns:
            List of important keys with metrics
        """
        return self.get_most_hit_keys(top_n=5)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics.

        Returns:
            Dictionary with all statistics
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "hit_rate_fraction": hit_rate / 100 if total > 0 else 0,
            "average_hit_time_ms": round(self.get_average_hit_time(), 2),
            "average_miss_time_ms": round(self.get_average_miss_time(), 2),
            "cache_size": self.get_cache_size(test_cache),
            "memory_usage_bytes": self.get_memory_usage(test_cache),
            "uptime_seconds": round((datetime.now() - self.start_time).total_seconds(), 2),
            "key_metrics": {
                key: {
                    "hits": m["hits"],
                    "misses": m["misses"],
                    "hit_rate": round((m["hits"] / (m["hits"] + m["misses"]) * 100)
                                    if (m["hits"] + m["misses"]) > 0 else 0, 2)
                }
                for key, m in self.key_metrics.items()
            }
        }

    def reset(self):
        """Reset all statistics."""
        self.hits = 0
        self.misses = 0
        self.hit_times = []
        self.miss_times = []
        self.errors = 0
        self.key_metrics = defaultdict(lambda: {
            "hits": 0,
            "misses": 0,
            "last_hit": None,
            "total_hit_time": 0.0,
            "total_miss_time": 0.0
        })
        self.start_time = datetime.now()

    def log_stats(self):
        """Log statistics to logger."""
        stats = self.get_stats()
        logger.info(
            f"Cache stats: "
            f"hits={stats['hits']}, misses={stats['misses']}, "
            f"hit_rate={stats['hit_rate_percent']:.1f}%, "
            f"avg_hit_time={stats['average_hit_time_ms']:.2f}ms, "
            f"cache_size={stats['cache_size']}, "
            f"memory={self.format_bytes(stats['memory_usage_bytes'])}"
        )

    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """
        Format bytes to human-readable string.

        Args:
            bytes_value: Number of bytes

        Returns:
            Formatted string (e.g., "1.5 KB", "2.3 MB")
        """
        if bytes_value == 0:
            return "0 Bytes"

        units = ["Bytes", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(bytes_value)

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"

    def get_performance_summary(self) -> str:
        """
        Get human-readable performance summary.

        Returns:
            Formatted string with performance summary
        """
        stats = self.get_stats()

        lines = [
            "=" * 60,
            "CACHE PERFORMANCE SUMMARY",
            "=" * 60,
            f"Total Requests:     {stats['total_requests']}",
            f"Cache Hits:         {stats['hits']}",
            f"Cache Misses:       {stats['misses']}",
            f"Errors:             {stats['errors']}",
            f"Hit Rate:           {stats['hit_rate_percent']:.1f}%",
            f"Average Hit Time:   {stats['average_hit_time_ms']:.2f} ms",
            f"Average Miss Time:  {stats['average_miss_time_ms']:.2f} ms",
            f"Cache Size:         {stats['cache_size']} entries",
            f"Memory Usage:       {self.format_bytes(stats['memory_usage_bytes'])}",
            f"Uptime:             {stats['uptime_seconds']:.0f} seconds",
            "=" * 60
        ]

        if self.key_metrics:
            lines.append("\nTop Cache Keys:")
            top_keys = self.get_most_hit_keys(top_n=3)

            for i, key_data in enumerate(top_keys, 1):
                lines.append(
                    f"{i}. {key_data['key']}: "
                    f"{key_data['hits']} hits, "
                    f"{key_data['hit_rate']:.1f}% hit rate"
                )

            lines.append("=" * 60)

        return "\n".join(lines)
