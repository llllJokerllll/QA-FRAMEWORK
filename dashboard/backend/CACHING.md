# Redis Caching System

This document describes the Redis caching system implemented in the QA-FRAMEWORK Dashboard.

## Overview

The caching system uses Redis as a distributed cache to improve performance by storing frequently accessed data. It supports both synchronous and asynchronous operations, TTL-based expiration, and automatic cache invalidation.

## Architecture

### Components

1. **Cache Manager** (`backend/core/cache.py`)
   - Singleton pattern for managing Redis connections
   - Connection pooling for optimal performance
   - Async and sync operation support
   - Cache invalidation strategies

2. **Service Layer Integration**
   - Automatic caching in service methods
   - Cache invalidation on data mutations
   - Graceful degradation on cache failures

## Configuration

### Environment Variables

The cache system uses the following environment variables (already configured in `config.py`):

```python
REDIS_HOST=localhost      # Redis server hostname
REDIS_PORT=6379          # Redis server port
REDIS_PASSWORD=None      # Redis password (optional)
```

### Docker Compose

Redis is already configured in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  restart: always
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

### TTL Configuration

Default TTL values (in seconds):

```python
SHORT_TTL = 60      # 1 minute - for rapidly changing data (executions)
MEDIUM_TTL = 600    # 10 minutes - for semi-static data (suites, cases)
LONG_TTL = 3600     # 1 hour - for rarely changing data
EXTENDED_TTL = 86400 # 24 hours - for reference data
```

## Usage

### Basic Cache Operations

```python
from core.cache import cache_manager, CacheManager

# Async operations
await cache_manager.async_set("key", value, ttl=300)
value = await cache_manager.async_get("key")
await cache_manager.async_delete("key")

# Sync operations
cache_manager.sync_set("key", value, ttl=300)
value = cache_manager.sync_get("key")
cache_manager.sync_delete("key")
```

### Convenience Functions

```python
from core.cache import cache_get, cache_set, cache_delete, cache_delete_pattern

# Quick async operations
await cache_set("my_key", my_data, ttl=600)
data = await cache_get("my_key")
await cache_delete("my_key")
await cache_delete_pattern("prefix:*")
```

### Cache Decorator

```python
from core.cache import cached

@cached(ttl=300, key_prefix="my_data")
async def get_expensive_data(param1, param2):
    # This will be cached
    return await fetch_from_database(param1, param2)
```

## Cache Key Patterns

The system uses consistent key prefixes for different entities:

```python
# Test Suites
suite:{id}                    # Individual suite
suites:list:skip:{n}:limit:{m} # Suite list

# Test Cases
case:{id}                     # Individual case
cases:list:suite:{id}:skip:{n}:limit:{m}  # Cases by suite
cases:list:skip:{n}:limit:{m} # All cases

# Executions
execution:{id}                # Individual execution
executions:list:suite:{id}:status:{s}:skip:{n}:limit:{m}

# Dashboard
dashboard:stats               # Statistics
dashboard:trends:days:{n}     # Trends data
dashboard:recent:limit:{n}    # Recent executions
dashboard:test_types_distribution
dashboard:performance_metrics
```

## Cache Invalidation Patterns

### Automatic Invalidation

Cache invalidation happens automatically on data mutations:

```python
# In services, cache is invalidated after mutations
async def update_suite_service(suite_id, suite_update, db):
    # ... update logic ...
    await db.commit()
    
    # Invalidate suite cache
    await cache_manager.invalidate_suite_cache(suite_id)
```

### Manual Invalidation

```python
# Invalidate specific entity caches
await cache_manager.invalidate_suite_cache(suite_id=1)
await cache_manager.invalidate_case_cache(case_id=1, suite_id=1)
await cache_manager.invalidate_execution_cache(execution_id=1)

# Invalidate dashboard cache
await cache_manager.invalidate_dashboard_cache()

# Invalidate all cache (use with caution!)
await cache_manager.invalidate_all_cache()
```

### Pattern-based Invalidation

```python
# Delete all keys matching a pattern
await cache_manager.async_delete_pattern("suites:*")
```

## Best Practices

### 1. Cache Key Generation

Always use the built-in key generation methods:

```python
# Good - uses consistent naming
cache_key = cache_manager.get_suite_key(suite_id)

# Avoid - manual key construction
cache_key = f"suite:{suite_id}"
```

### 2. TTL Selection

Choose appropriate TTL values based on data volatility:

- **SHORT_TTL (1 min)**: Execution results, recent data
- **MEDIUM_TTL (10 min)**: Suite/case lists, test configurations
- **LONG_TTL (1 hour)**: User profiles, reference data
- **EXTENDED_TTL (24 hours)**: Static configuration

### 3. Error Handling

Cache operations are designed to fail gracefully:

```python
# This will not raise an exception if cache fails
cached_value = await cache_manager.async_get(key)
if cached_value is None:
    # Fetch from database
    value = await fetch_from_db()
    # Try to cache (will not fail if Redis is down)
    await cache_manager.async_set(key, value)
```

### 4. Cache Invalidation Strategy

Follow these guidelines for cache invalidation:

- **Create**: Invalidate list caches only
- **Update**: Invalidate specific entity + list caches
- **Delete**: Invalidate specific entity + list caches

### 5. Monitoring Cache Performance

Monitor cache effectiveness through logs:

```python
# Cache hit
logger.debug("Cache hit", key=key)

# Cache miss
logger.debug("Cache miss", key=key)

# Cache errors
logger.error("Cache operation failed", error=str(e))
```

## Service Integration Examples

### Test Suite Service

```python
async def get_suite_by_id(suite_id: int, db: AsyncSession):
    cache_key = cache_manager.get_suite_key(suite_id)
    
    # Try cache first
    cached_suite = await cache_manager.async_get(cache_key)
    if cached_suite is not None:
        return cached_suite
    
    # Fetch from database
    suite = await db.fetch_suite(suite_id)
    
    # Cache the result
    await cache_manager.async_set(cache_key, suite, ttl=CacheManager.MEDIUM_TTL)
    
    return suite

async def update_suite_service(suite_id: int, suite_update, db):
    # ... update logic ...
    await db.commit()
    
    # Invalidate cache
    await cache_manager.invalidate_suite_cache(suite_id)
```

### Dashboard Service

```python
async def get_stats_service(db: AsyncSession):
    cache_key = cache_manager.get_dashboard_stats_key()
    
    # Try cache first
    cached_stats = await cache_manager.async_get(cache_key)
    if cached_stats is not None:
        return cached_stats
    
    # Expensive aggregation query
    stats = await calculate_stats(db)
    
    # Cache with short TTL since stats change frequently
    await cache_manager.async_set(cache_key, stats, ttl=CacheManager.SHORT_TTL)
    
    return stats
```

## Troubleshooting

### Cache Not Working

1. Check Redis connection:
   ```bash
   docker-compose ps redis
   redis-cli ping
   ```

2. Verify environment variables:
   ```bash
   echo $REDIS_HOST
   echo $REDIS_PORT
   ```

3. Check application logs for cache errors

### Cache Stale Data

1. Verify TTL settings are appropriate
2. Check if cache invalidation is being triggered
3. Use pattern-based invalidation to clear stale data

### High Memory Usage

1. Review TTL settings - shorter TTL for large objects
2. Implement cache size limits in Redis config
3. Use `cache_manager.async_delete_pattern()` to clear old data

## Redis CLI Commands

Useful commands for debugging:

```bash
# Connect to Redis
redis-cli

# List all keys
KEYS *

# Get key value
GET "suite:1"

# Check TTL
TTL "suite:1"

# Delete key
DEL "suite:1"

# Flush all data (use with caution!)
FLUSHDB

# Monitor operations
MONITOR
```

## Future Enhancements

Potential improvements to consider:

1. **Cache Warming**: Pre-populate cache on startup
2. **Cache Statistics**: Track hit/miss ratios
3. **Multi-tier Caching**: Local LRU cache + Redis
4. **Compression**: Compress large cached objects
5. **Distributed Locks**: For cache stampede protection
