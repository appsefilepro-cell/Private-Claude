"""
Rate Limiting and DDoS Protection System
FIX: Lack of Rate Limiting and DDoS Protection
"""

import time
from typing import Optional, Dict, Callable
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta

import redis
from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import get_settings
from logging_system import logging_system, AuditEventType


class RateLimitConfig:
    """Rate limit configuration for different endpoints"""

    # Global limits
    GLOBAL = "100/minute"

    # Authentication limits
    LOGIN = "5/minute"
    API_KEY_AUTH = "100/minute"

    # Trading limits
    TRADE_EXECUTION = "10/minute"
    MARKET_DATA = "60/minute"

    # Email limits
    EMAIL_SEND = "10/minute;50/hour"

    # API limits
    API_READ = "100/minute"
    API_WRITE = "20/minute"

    # Kraken API limits (to avoid IP bans)
    KRAKEN_PUBLIC = "1/second;15/minute"
    KRAKEN_PRIVATE = "1/second;15/minute"


class AdvancedRateLimiter:
    """
    Advanced rate limiter with Redis backend for distributed rate limiting
    """

    def __init__(self):
        self.settings = get_settings()
        self._setup_redis()
        self._memory_storage: Dict[str, Dict] = defaultdict(dict)
        self._use_redis = self.redis_client is not None

    def _setup_redis(self):
        """Set up Redis connection for distributed rate limiting"""
        try:
            self.redis_client = redis.from_url(
                self.settings.rate_limit_storage,
                password=self.settings.redis_password,
                decode_responses=True,
            )
            # Test connection
            self.redis_client.ping()
            logging_system.info("Redis connected for rate limiting")

        except Exception as e:
            logging_system.warning(
                f"Redis connection failed, using in-memory rate limiting: {e}"
            )
            self.redis_client = None

    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate rate limit key"""
        return f"ratelimit:{identifier}:{endpoint}"

    def _check_limit_redis(
        self,
        key: str,
        limit: int,
        window: int,
    ) -> bool:
        """Check rate limit using Redis"""
        try:
            current = int(time.time())
            window_start = current - window

            # Use Redis sorted set for sliding window
            pipe = self.redis_client.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Add current request
            pipe.zadd(key, {str(current): current})

            # Count requests in window
            pipe.zcount(key, window_start, current)

            # Set expiration
            pipe.expire(key, window + 1)

            results = pipe.execute()
            count = results[2]

            return count <= limit

        except Exception as e:
            logging_system.error(f"Redis rate limit check failed: {e}")
            # Fallback to allow request if Redis fails
            return True

    def _check_limit_memory(
        self,
        key: str,
        limit: int,
        window: int,
    ) -> bool:
        """Check rate limit using in-memory storage"""
        current = time.time()
        window_start = current - window

        if key not in self._memory_storage:
            self._memory_storage[key] = {"requests": [], "count": 0}

        storage = self._memory_storage[key]

        # Remove old requests
        storage["requests"] = [
            req_time for req_time in storage["requests"]
            if req_time > window_start
        ]

        # Add current request
        storage["requests"].append(current)
        storage["count"] = len(storage["requests"])

        return storage["count"] <= limit

    def check_limit(
        self,
        identifier: str,
        endpoint: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        """
        Check if request is within rate limit

        Args:
            identifier: User ID, IP address, or API key
            endpoint: Endpoint being accessed
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if within limit, False if exceeded
        """
        key = self._get_key(identifier, endpoint)

        if self._use_redis:
            return self._check_limit_redis(key, limit, window_seconds)
        else:
            return self._check_limit_memory(key, limit, window_seconds)

    def parse_limit_string(self, limit_str: str) -> list:
        """
        Parse limit string like "10/minute;50/hour"

        Returns list of (limit, window_seconds) tuples
        """
        limits = []

        for part in limit_str.split(";"):
            count, period = part.split("/")
            count = int(count.strip())

            period = period.strip().lower()
            if period == "second":
                window = 1
            elif period == "minute":
                window = 60
            elif period == "hour":
                window = 3600
            elif period == "day":
                window = 86400
            else:
                raise ValueError(f"Invalid period: {period}")

            limits.append((count, window))

        return limits

    def check_limits(
        self,
        identifier: str,
        endpoint: str,
        limit_str: str,
    ) -> bool:
        """Check multiple rate limits"""
        limits = self.parse_limit_string(limit_str)

        for limit, window in limits:
            if not self.check_limit(identifier, endpoint, limit, window):
                return False

        return True


# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()


# SlowAPI limiter for FastAPI integration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[RateLimitConfig.GLOBAL],
    storage_uri=get_settings().rate_limit_storage,
)


def rate_limit(limit_str: str):
    """
    Decorator for rate limiting routes

    Usage:
        @rate_limit("10/minute")
        async def my_endpoint():
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request: Optional[Request] = kwargs.get("request")

            if request:
                # Use IP address as identifier
                identifier = request.client.host

                # Check rate limit
                if not rate_limiter.check_limits(
                    identifier,
                    request.url.path,
                    limit_str,
                ):
                    # Log rate limit exceeded
                    logging_system.audit_security_event(
                        event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
                        ip_address=identifier,
                        details={
                            "endpoint": request.url.path,
                            "limit": limit_str,
                        },
                    )

                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later.",
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class KrakenRateLimiter:
    """
    Specialized rate limiter for Kraken API to prevent IP bans

    Kraken has strict rate limits:
    - Public endpoints: 1 per second
    - Private endpoints: Variable based on tier
    """

    def __init__(self):
        self.settings = get_settings()
        self._public_last_call = 0.0
        self._private_last_call = 0.0
        self._private_counter = 0
        self._counter_decay_time = time.time()

    def wait_for_public_endpoint(self):
        """Wait if necessary before calling public endpoint"""
        if not self.settings.kraken_rate_limit_enabled:
            return

        now = time.time()
        time_since_last = now - self._public_last_call

        # Ensure at least 1 second between calls
        if time_since_last < 1.0:
            sleep_time = 1.0 - time_since_last
            logging_system.debug(f"Kraken rate limit: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self._public_last_call = time.time()

    def wait_for_private_endpoint(self):
        """Wait if necessary before calling private endpoint"""
        if not self.settings.kraken_rate_limit_enabled:
            return

        now = time.time()

        # Decay counter (Kraken uses a counter that decays over time)
        time_since_decay = now - self._counter_decay_time
        decay_amount = int(time_since_decay / 3)  # Decay every 3 seconds

        if decay_amount > 0:
            self._private_counter = max(0, self._private_counter - decay_amount)
            self._counter_decay_time = now

        # Check if we need to wait
        max_counter = self.settings.kraken_max_requests_per_minute
        if self._private_counter >= max_counter:
            sleep_time = 3.0  # Wait for decay
            logging_system.debug(f"Kraken rate limit: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
            self._private_counter = 0
            self._counter_decay_time = time.time()

        # Ensure at least 1 second between calls
        time_since_last = now - self._private_last_call
        if time_since_last < 1.0:
            sleep_time = 1.0 - time_since_last
            time.sleep(sleep_time)

        self._private_counter += 1
        self._private_last_call = time.time()

    def reset(self):
        """Reset rate limiter counters"""
        self._public_last_call = 0.0
        self._private_last_call = 0.0
        self._private_counter = 0
        self._counter_decay_time = time.time()


# Global Kraken rate limiter
kraken_rate_limiter = KrakenRateLimiter()


class EmailRateLimiter:
    """
    Rate limiter for email sending to prevent spam and resource exhaustion
    """

    def __init__(self):
        self.settings = get_settings()
        self._hourly_counts: Dict[str, list] = defaultdict(list)

    def can_send_email(self, sender: str) -> bool:
        """Check if sender can send an email"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)

        # Clean old entries
        self._hourly_counts[sender] = [
            timestamp for timestamp in self._hourly_counts[sender]
            if timestamp > hour_ago
        ]

        # Check limit
        if len(self._hourly_counts[sender]) >= self.settings.email_rate_limit_per_hour:
            logging_system.audit_security_event(
                event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
                ip_address="system",
                details={
                    "service": "email",
                    "sender": sender,
                    "limit": self.settings.email_rate_limit_per_hour,
                },
                user=sender,
            )
            return False

        # Record this send
        self._hourly_counts[sender].append(now)
        return True


# Global email rate limiter
email_rate_limiter = EmailRateLimiter()
