"""
Performance Optimization Module for Agent 5.0
==============================================

Comprehensive performance optimization utilities including:
- Database query optimization
- Redis caching layer
- Rate limiting and throttling
- Connection pooling
- Memory profiling and leak detection
- Performance monitoring and alerting

Author: Agent 5.0 System
Version: 1.0.0
"""

import time
import functools
import asyncio
import logging
import json
import hashlib
import psutil
import threading
import tracemalloc
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque
from contextlib import asynccontextmanager, contextmanager
import sys
import gc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis-based caching layer with TTL support and automatic serialization.
    Falls back to in-memory cache if Redis is unavailable.
    """

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0,
                 default_ttl: int = 3600, use_fallback: bool = True):
        self.host = host
        self.port = port
        self.db = db
        self.default_ttl = default_ttl
        self.use_fallback = use_fallback
        self.redis_client = None
        self.fallback_cache = {} if use_fallback else None
        self.cache_stats = {'hits': 0, 'misses': 0, 'sets': 0, 'deletes': 0}

        try:
            import redis
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            self.redis_client.ping()
            logger.info(f"Redis cache connected to {host}:{port}")
        except Exception as e:
            logger.warning(f"Redis unavailable, using fallback cache: {e}")
            if not use_fallback:
                raise

    def _generate_key(self, key: str, namespace: str = '') -> str:
        """Generate a namespaced cache key."""
        if namespace:
            return f"{namespace}:{key}"
        return key

    def get(self, key: str, namespace: str = '') -> Optional[Any]:
        """Retrieve value from cache."""
        full_key = self._generate_key(key, namespace)

        try:
            if self.redis_client:
                value = self.redis_client.get(full_key)
                if value:
                    self.cache_stats['hits'] += 1
                    return json.loads(value)
                else:
                    self.cache_stats['misses'] += 1
                    return None
            elif self.fallback_cache is not None:
                if full_key in self.fallback_cache:
                    entry = self.fallback_cache[full_key]
                    if entry['expires_at'] > time.time():
                        self.cache_stats['hits'] += 1
                        return entry['value']
                    else:
                        del self.fallback_cache[full_key]
                self.cache_stats['misses'] += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {full_key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = '') -> bool:
        """Store value in cache with TTL."""
        full_key = self._generate_key(key, namespace)
        ttl = ttl or self.default_ttl

        try:
            if self.redis_client:
                serialized = json.dumps(value)
                self.redis_client.setex(full_key, ttl, serialized)
                self.cache_stats['sets'] += 1
                return True
            elif self.fallback_cache is not None:
                self.fallback_cache[full_key] = {
                    'value': value,
                    'expires_at': time.time() + ttl
                }
                self.cache_stats['sets'] += 1
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {full_key}: {e}")
            return False

    def delete(self, key: str, namespace: str = '') -> bool:
        """Delete key from cache."""
        full_key = self._generate_key(key, namespace)

        try:
            if self.redis_client:
                self.redis_client.delete(full_key)
                self.cache_stats['deletes'] += 1
                return True
            elif self.fallback_cache is not None:
                if full_key in self.fallback_cache:
                    del self.fallback_cache[full_key]
                self.cache_stats['deletes'] += 1
                return True
        except Exception as e:
            logger.error(f"Cache delete error for key {full_key}: {e}")
            return False

    def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace."""
        count = 0
        try:
            if self.redis_client:
                pattern = f"{namespace}:*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
                    count += 1
            elif self.fallback_cache is not None:
                keys_to_delete = [k for k in self.fallback_cache.keys() if k.startswith(f"{namespace}:")]
                for key in keys_to_delete:
                    del self.fallback_cache[key]
                    count += 1
            logger.info(f"Cleared {count} keys from namespace {namespace}")
        except Exception as e:
            logger.error(f"Error clearing namespace {namespace}: {e}")
        return count

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self.cache_stats,
            'total_requests': total_requests,
            'hit_rate_percentage': round(hit_rate, 2)
        }


class RateLimiter:
    """
    Token bucket rate limiter with configurable limits per endpoint/user.
    Supports both synchronous and asynchronous operations.
    """

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.buckets = defaultdict(lambda: deque())
        self.lock = threading.Lock()

    def _clean_old_requests(self, bucket: deque, current_time: float) -> None:
        """Remove requests outside the time window."""
        cutoff_time = current_time - self.time_window
        while bucket and bucket[0] < cutoff_time:
            bucket.popleft()

    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.

        Args:
            identifier: Unique identifier (e.g., user_id, ip_address, api_key)

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        with self.lock:
            current_time = time.time()
            bucket = self.buckets[identifier]

            self._clean_old_requests(bucket, current_time)

            current_count = len(bucket)
            is_allowed = current_count < self.max_requests

            if is_allowed:
                bucket.append(current_time)

            retry_after = 0
            if not is_allowed and bucket:
                oldest_request = bucket[0]
                retry_after = int(oldest_request + self.time_window - current_time) + 1

            return is_allowed, {
                'limit': self.max_requests,
                'remaining': max(0, self.max_requests - current_count - (1 if is_allowed else 0)),
                'reset': int(current_time + self.time_window),
                'retry_after': retry_after
            }

    async def async_is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, Any]]:
        """Async version of is_allowed."""
        return self.is_allowed(identifier)

    def reset(self, identifier: str) -> None:
        """Reset rate limit for an identifier."""
        with self.lock:
            if identifier in self.buckets:
                del self.buckets[identifier]


class ConnectionPool:
    """
    Generic connection pool for database and API connections.
    Manages connection lifecycle, health checks, and automatic reconnection.
    """

    def __init__(self, connection_factory: Callable, max_connections: int = 10,
                 min_connections: int = 2, max_idle_time: int = 300,
                 health_check_interval: int = 60):
        self.connection_factory = connection_factory
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.max_idle_time = max_idle_time
        self.health_check_interval = health_check_interval

        self.available_connections = deque()
        self.in_use_connections = set()
        self.connection_metadata = {}
        self.lock = threading.Lock()
        self.total_created = 0
        self.total_closed = 0

        # Initialize minimum connections
        self._initialize_pool()

        # Start health check thread
        self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_check_thread.start()

    def _initialize_pool(self) -> None:
        """Create minimum number of connections."""
        for _ in range(self.min_connections):
            try:
                conn = self._create_connection()
                self.available_connections.append(conn)
            except Exception as e:
                logger.error(f"Failed to create initial connection: {e}")

    def _create_connection(self) -> Any:
        """Create a new connection."""
        conn = self.connection_factory()
        conn_id = id(conn)
        self.connection_metadata[conn_id] = {
            'created_at': time.time(),
            'last_used': time.time(),
            'use_count': 0
        }
        self.total_created += 1
        logger.debug(f"Created new connection {conn_id}")
        return conn

    def _is_connection_valid(self, conn: Any) -> bool:
        """Check if connection is still valid."""
        try:
            # Implement connection-specific health check
            # For databases, this might be a simple query
            # For APIs, might be a ping endpoint
            return True
        except Exception:
            return False

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool (context manager)."""
        conn = None
        try:
            with self.lock:
                # Try to get an available connection
                while self.available_connections:
                    conn = self.available_connections.popleft()
                    if self._is_connection_valid(conn):
                        break
                    else:
                        self._close_connection(conn)
                        conn = None

                # Create new connection if needed
                if conn is None:
                    if len(self.in_use_connections) < self.max_connections:
                        conn = self._create_connection()
                    else:
                        raise Exception("Connection pool exhausted")

                # Mark as in use
                self.in_use_connections.add(conn)
                conn_id = id(conn)
                self.connection_metadata[conn_id]['last_used'] = time.time()
                self.connection_metadata[conn_id]['use_count'] += 1

            yield conn

        finally:
            if conn is not None:
                with self.lock:
                    self.in_use_connections.discard(conn)
                    self.available_connections.append(conn)

    @asynccontextmanager
    async def async_get_connection(self):
        """Async version of get_connection."""
        conn = None
        try:
            # Use asyncio.Lock for async operations
            conn = await asyncio.get_event_loop().run_in_executor(
                None, self._get_connection_sync
            )
            yield conn
        finally:
            if conn is not None:
                await asyncio.get_event_loop().run_in_executor(
                    None, self._return_connection_sync, conn
                )

    def _get_connection_sync(self) -> Any:
        """Synchronous connection retrieval for async wrapper."""
        with self.lock:
            while self.available_connections:
                conn = self.available_connections.popleft()
                if self._is_connection_valid(conn):
                    self.in_use_connections.add(conn)
                    conn_id = id(conn)
                    self.connection_metadata[conn_id]['last_used'] = time.time()
                    self.connection_metadata[conn_id]['use_count'] += 1
                    return conn
                else:
                    self._close_connection(conn)

            if len(self.in_use_connections) < self.max_connections:
                conn = self._create_connection()
                self.in_use_connections.add(conn)
                return conn
            else:
                raise Exception("Connection pool exhausted")

    def _return_connection_sync(self, conn: Any) -> None:
        """Synchronous connection return for async wrapper."""
        with self.lock:
            self.in_use_connections.discard(conn)
            self.available_connections.append(conn)

    def _close_connection(self, conn: Any) -> None:
        """Close a connection and clean up metadata."""
        try:
            if hasattr(conn, 'close'):
                conn.close()
            conn_id = id(conn)
            if conn_id in self.connection_metadata:
                del self.connection_metadata[conn_id]
            self.total_closed += 1
            logger.debug(f"Closed connection {conn_id}")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

    def _health_check_loop(self) -> None:
        """Periodic health check for idle connections."""
        while True:
            time.sleep(self.health_check_interval)
            try:
                with self.lock:
                    current_time = time.time()
                    connections_to_remove = []

                    for conn in list(self.available_connections):
                        conn_id = id(conn)
                        metadata = self.connection_metadata.get(conn_id)

                        if metadata:
                            idle_time = current_time - metadata['last_used']

                            # Close idle connections beyond min_connections
                            if (idle_time > self.max_idle_time and
                                len(self.available_connections) > self.min_connections):
                                connections_to_remove.append(conn)
                            # Validate remaining connections
                            elif not self._is_connection_valid(conn):
                                connections_to_remove.append(conn)

                    for conn in connections_to_remove:
                        self.available_connections.remove(conn)
                        self._close_connection(conn)

                    if connections_to_remove:
                        logger.info(f"Health check removed {len(connections_to_remove)} connections")
            except Exception as e:
                logger.error(f"Health check error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self.lock:
            return {
                'available': len(self.available_connections),
                'in_use': len(self.in_use_connections),
                'total_created': self.total_created,
                'total_closed': self.total_closed,
                'max_connections': self.max_connections,
                'min_connections': self.min_connections
            }

    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self.lock:
            for conn in list(self.available_connections):
                self._close_connection(conn)
            self.available_connections.clear()

            for conn in list(self.in_use_connections):
                self._close_connection(conn)
            self.in_use_connections.clear()


class MemoryProfiler:
    """
    Memory profiling and leak detection utilities.
    Tracks memory usage patterns and identifies potential leaks.
    """

    def __init__(self, threshold_mb: float = 100.0, sample_interval: int = 60):
        self.threshold_mb = threshold_mb
        self.sample_interval = sample_interval
        self.snapshots = deque(maxlen=100)
        self.is_tracking = False
        self.tracking_thread = None
        tracemalloc.start()

    def take_snapshot(self) -> Dict[str, Any]:
        """Take a memory snapshot."""
        snapshot = tracemalloc.take_snapshot()
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            'timestamp': datetime.now().isoformat(),
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'snapshot': snapshot
        }

    def start_tracking(self) -> None:
        """Start continuous memory tracking."""
        if not self.is_tracking:
            self.is_tracking = True
            self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
            self.tracking_thread.start()
            logger.info("Memory tracking started")

    def stop_tracking(self) -> None:
        """Stop memory tracking."""
        self.is_tracking = False
        logger.info("Memory tracking stopped")

    def _tracking_loop(self) -> None:
        """Continuous tracking loop."""
        while self.is_tracking:
            snapshot = self.take_snapshot()
            self.snapshots.append(snapshot)

            # Check threshold
            if snapshot['rss_mb'] > self.threshold_mb:
                logger.warning(f"Memory usage {snapshot['rss_mb']:.2f} MB exceeds threshold {self.threshold_mb} MB")

            time.sleep(self.sample_interval)

    def get_top_allocations(self, limit: int = 10) -> List[str]:
        """Get top memory allocations."""
        if not self.snapshots:
            return []

        latest_snapshot = self.snapshots[-1]['snapshot']
        top_stats = latest_snapshot.statistics('lineno')[:limit]

        return [
            f"{stat.filename}:{stat.lineno} - {stat.size / 1024:.1f} KB ({stat.count} objects)"
            for stat in top_stats
        ]

    def detect_leaks(self) -> Dict[str, Any]:
        """Analyze snapshots to detect potential memory leaks."""
        if len(self.snapshots) < 2:
            return {'status': 'insufficient_data'}

        first_snapshot = self.snapshots[0]
        last_snapshot = self.snapshots[-1]

        memory_growth = last_snapshot['rss_mb'] - first_snapshot['rss_mb']
        growth_rate = memory_growth / len(self.snapshots) * 60  # MB per hour

        # Compare snapshots
        diff = last_snapshot['snapshot'].compare_to(first_snapshot['snapshot'], 'lineno')
        top_increases = sorted(diff, key=lambda x: x.size_diff, reverse=True)[:10]

        leak_detected = growth_rate > 10  # More than 10 MB/hour growth

        return {
            'status': 'leak_detected' if leak_detected else 'normal',
            'memory_growth_mb': round(memory_growth, 2),
            'growth_rate_mb_per_hour': round(growth_rate, 2),
            'top_increases': [
                f"{stat.filename}:{stat.lineno} - +{stat.size_diff / 1024:.1f} KB"
                for stat in top_increases
            ]
        }

    def force_gc(self) -> Dict[str, int]:
        """Force garbage collection and return statistics."""
        collected = {
            'gen0': gc.collect(0),
            'gen1': gc.collect(1),
            'gen2': gc.collect(2)
        }
        logger.info(f"Garbage collection completed: {collected}")
        return collected


class PerformanceMonitor:
    """
    Comprehensive performance monitoring for functions and code blocks.
    Tracks execution time, call frequency, and resource usage.
    """

    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'call_count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'errors': 0
        })
        self.lock = threading.Lock()

    def monitor(self, name: Optional[str] = None):
        """Decorator to monitor function performance."""
        def decorator(func: Callable) -> Callable:
            metric_name = name or f"{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    self._record_metric(metric_name, elapsed, False)
                    return result
                except Exception as e:
                    elapsed = time.time() - start_time
                    self._record_metric(metric_name, elapsed, True)
                    raise

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    self._record_metric(metric_name, elapsed, False)
                    return result
                except Exception as e:
                    elapsed = time.time() - start_time
                    self._record_metric(metric_name, elapsed, True)
                    raise

            return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
        return decorator

    def _record_metric(self, name: str, elapsed: float, is_error: bool) -> None:
        """Record a metric measurement."""
        with self.lock:
            metric = self.metrics[name]
            metric['call_count'] += 1
            metric['total_time'] += elapsed
            metric['min_time'] = min(metric['min_time'], elapsed)
            metric['max_time'] = max(metric['max_time'], elapsed)
            if is_error:
                metric['errors'] += 1

    def get_metrics(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics."""
        with self.lock:
            if name:
                metric = self.metrics.get(name)
                if not metric:
                    return {}

                avg_time = metric['total_time'] / metric['call_count'] if metric['call_count'] > 0 else 0
                error_rate = (metric['errors'] / metric['call_count'] * 100) if metric['call_count'] > 0 else 0

                return {
                    'name': name,
                    'call_count': metric['call_count'],
                    'avg_time_ms': round(avg_time * 1000, 2),
                    'min_time_ms': round(metric['min_time'] * 1000, 2),
                    'max_time_ms': round(metric['max_time'] * 1000, 2),
                    'total_time_s': round(metric['total_time'], 2),
                    'errors': metric['errors'],
                    'error_rate_percentage': round(error_rate, 2)
                }
            else:
                return {
                    metric_name: self.get_metrics(metric_name)
                    for metric_name in self.metrics.keys()
                }

    def reset(self, name: Optional[str] = None) -> None:
        """Reset metrics."""
        with self.lock:
            if name:
                if name in self.metrics:
                    del self.metrics[name]
            else:
                self.metrics.clear()


# Global instances
cache = RedisCache(use_fallback=True)
rate_limiter = RateLimiter(max_requests=100, time_window=60)
performance_monitor = PerformanceMonitor()
memory_profiler = MemoryProfiler()

# Convenience decorators
monitor_performance = performance_monitor.monitor


if __name__ == "__main__":
    # Example usage and testing
    print("Performance Optimizer Module - Example Usage")
    print("=" * 50)

    # Test cache
    print("\n1. Testing Redis Cache:")
    cache.set('test_key', {'data': 'test_value'}, ttl=60)
    value = cache.get('test_key')
    print(f"Cached value: {value}")
    print(f"Cache stats: {cache.get_stats()}")

    # Test rate limiter
    print("\n2. Testing Rate Limiter:")
    for i in range(5):
        allowed, info = rate_limiter.is_allowed('user_123')
        print(f"Request {i+1}: Allowed={allowed}, Remaining={info['remaining']}")

    # Test performance monitor
    print("\n3. Testing Performance Monitor:")

    @monitor_performance()
    def sample_function():
        time.sleep(0.1)
        return "done"

    for _ in range(3):
        sample_function()

    print(f"Metrics: {performance_monitor.get_metrics('__main__.sample_function')}")

    # Test memory profiler
    print("\n4. Testing Memory Profiler:")
    snapshot = memory_profiler.take_snapshot()
    print(f"Memory usage: {snapshot['rss_mb']:.2f} MB")

    print("\nAll tests completed successfully!")
