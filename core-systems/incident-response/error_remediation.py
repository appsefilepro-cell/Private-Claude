"""
Error Remediation System for Agent 5.0
========================================

Automated error detection, classification, and self-healing capabilities.
Includes retry mechanisms, circuit breakers, and integration with incident management.

Author: Agent 5.0 System
Version: 1.0.0
"""

import time
import asyncio
import logging
import json
import traceback
import hashlib
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import functools
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    UNKNOWN = "unknown"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ErrorClassifier:
    """
    Classifies errors by analyzing exception types, messages, and patterns.
    """

    # Exception type to category mapping
    EXCEPTION_CATEGORIES = {
        'ConnectionError': ErrorCategory.NETWORK,
        'TimeoutError': ErrorCategory.TIMEOUT,
        'requests.exceptions.ConnectionError': ErrorCategory.NETWORK,
        'requests.exceptions.Timeout': ErrorCategory.TIMEOUT,
        'pymongo.errors.ConnectionFailure': ErrorCategory.DATABASE,
        'sqlalchemy.exc.OperationalError': ErrorCategory.DATABASE,
        'AuthenticationError': ErrorCategory.AUTHENTICATION,
        'PermissionError': ErrorCategory.AUTHORIZATION,
        'ValidationError': ErrorCategory.VALIDATION,
        'ValueError': ErrorCategory.VALIDATION,
        'MemoryError': ErrorCategory.RESOURCE,
        'ResourceWarning': ErrorCategory.RESOURCE,
    }

    # Message patterns for classification
    MESSAGE_PATTERNS = {
        ErrorCategory.NETWORK: ['connection', 'network', 'unreachable', 'dns'],
        ErrorCategory.DATABASE: ['database', 'query', 'transaction', 'deadlock'],
        ErrorCategory.API: ['api', 'endpoint', 'rate limit', 'quota'],
        ErrorCategory.TIMEOUT: ['timeout', 'timed out', 'deadline exceeded'],
        ErrorCategory.AUTHENTICATION: ['auth', 'credential', 'token', 'unauthorized'],
        ErrorCategory.AUTHORIZATION: ['permission', 'forbidden', 'access denied'],
        ErrorCategory.RESOURCE: ['memory', 'disk', 'cpu', 'quota exceeded'],
    }

    @classmethod
    def classify_error(cls, exception: Exception) -> Tuple[ErrorCategory, ErrorSeverity]:
        """
        Classify an error based on its type and message.

        Returns:
            Tuple of (category, severity)
        """
        exc_type = type(exception).__name__
        exc_message = str(exception).lower()

        # Try to match by exception type
        category = cls.EXCEPTION_CATEGORIES.get(exc_type, ErrorCategory.UNKNOWN)

        # If unknown, try to match by message patterns
        if category == ErrorCategory.UNKNOWN:
            for cat, patterns in cls.MESSAGE_PATTERNS.items():
                if any(pattern in exc_message for pattern in patterns):
                    category = cat
                    break

        # Determine severity
        severity = cls._determine_severity(category, exception)

        return category, severity

    @classmethod
    def _determine_severity(cls, category: ErrorCategory, exception: Exception) -> ErrorSeverity:
        """Determine error severity based on category and context."""
        # Critical errors
        if category in [ErrorCategory.DATABASE, ErrorCategory.RESOURCE]:
            return ErrorSeverity.CRITICAL

        # High severity errors
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
            return ErrorSeverity.HIGH

        # Medium severity errors
        if category in [ErrorCategory.API, ErrorCategory.TIMEOUT]:
            return ErrorSeverity.MEDIUM

        # Low severity errors
        return ErrorSeverity.LOW

    @classmethod
    def generate_error_signature(cls, exception: Exception) -> str:
        """Generate a unique signature for an error for deduplication."""
        exc_type = type(exception).__name__
        exc_message = str(exception)
        # Create hash from type and normalized message
        signature_data = f"{exc_type}:{exc_message[:100]}"
        return hashlib.md5(signature_data.encode()).hexdigest()


class RetryStrategy:
    """
    Configurable retry strategy with exponential backoff and jitter.
    """

    def __init__(self,
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True,
                 retryable_exceptions: Optional[List[Type[Exception]]] = None):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or [Exception]

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the next retry attempt."""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        if self.jitter:
            # Add random jitter (0-25% of delay)
            delay += random.uniform(0, delay * 0.25)

        return delay

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if the error should be retried."""
        if attempt >= self.max_attempts:
            return False

        # Check if exception type is retryable
        return any(isinstance(exception, exc_type) for exc_type in self.retryable_exceptions)

    def __call__(self, func: Callable) -> Callable:
        """Decorator for automatic retry with exponential backoff."""

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    category, severity = ErrorClassifier.classify_error(e)

                    if not self.should_retry(e, attempt):
                        logger.error(
                            f"Max retries ({self.max_attempts}) reached for {func.__name__}: {e}"
                        )
                        raise

                    delay = self.calculate_delay(attempt)
                    logger.warning(
                        f"Retry {attempt + 1}/{self.max_attempts} for {func.__name__} "
                        f"after {delay:.2f}s. Error: {e} (Category: {category.value})"
                    )
                    time.sleep(delay)

            raise last_exception

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(self.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    category, severity = ErrorClassifier.classify_error(e)

                    if not self.should_retry(e, attempt):
                        logger.error(
                            f"Max retries ({self.max_attempts}) reached for {func.__name__}: {e}"
                        )
                        raise

                    delay = self.calculate_delay(attempt)
                    logger.warning(
                        f"Retry {attempt + 1}/{self.max_attempts} for {func.__name__} "
                        f"after {delay:.2f}s. Error: {e} (Category: {category.value})"
                    )
                    await asyncio.sleep(delay)

            raise last_exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


class CircuitBreaker:
    """
    Circuit breaker pattern implementation to prevent cascading failures.
    """

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: Type[Exception] = Exception,
                 name: Optional[str] = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name or "unnamed"

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._success_count = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    def _record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            self._failure_count = 0
            self._success_count += 1

            if self._state == CircuitState.HALF_OPEN:
                # Successful call in half-open state, close the circuit
                self._state = CircuitState.CLOSED
                logger.info(f"Circuit breaker '{self.name}' closed after successful recovery")

    def _record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                # Failure in half-open state, reopen the circuit
                self._state = CircuitState.OPEN
                logger.warning(f"Circuit breaker '{self.name}' reopened after failed recovery attempt")
            elif self._failure_count >= self.failure_threshold:
                # Threshold reached, open the circuit
                self._state = CircuitState.OPEN
                logger.error(
                    f"Circuit breaker '{self.name}' opened after {self._failure_count} failures"
                )

    def _check_and_update_state(self) -> None:
        """Check if circuit should transition to half-open state."""
        with self._lock:
            if self._state == CircuitState.OPEN and self._last_failure_time:
                if time.time() - self._last_failure_time >= self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit breaker '{self.name}' entering half-open state")

    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker protection."""

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            self._check_and_update_state()

            if self._state == CircuitState.OPEN:
                raise Exception(
                    f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
                )

            try:
                result = func(*args, **kwargs)
                self._record_success()
                return result
            except self.expected_exception as e:
                self._record_failure()
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            self._check_and_update_state()

            if self._state == CircuitState.OPEN:
                raise Exception(
                    f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
                )

            try:
                result = await func(*args, **kwargs)
                self._record_success()
                return result
            except self.expected_exception as e:
                self._record_failure()
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        with self._lock:
            return {
                'name': self.name,
                'state': self._state.value,
                'failure_count': self._failure_count,
                'success_count': self._success_count,
                'last_failure_time': self._last_failure_time,
                'failure_threshold': self.failure_threshold
            }

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            logger.info(f"Circuit breaker '{self.name}' manually reset")


class ErrorAggregator:
    """
    Aggregates and analyzes errors for pattern detection and reporting.
    """

    def __init__(self, window_size: int = 3600):
        self.window_size = window_size
        self.errors = deque()
        self.error_counts = defaultdict(int)
        self.error_signatures = {}
        self._lock = threading.Lock()

    def record_error(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Record an error occurrence.

        Returns:
            Error signature for deduplication
        """
        signature = ErrorClassifier.generate_error_signature(exception)
        category, severity = ErrorClassifier.classify_error(exception)

        error_record = {
            'signature': signature,
            'timestamp': time.time(),
            'exception_type': type(exception).__name__,
            'message': str(exception),
            'category': category.value,
            'severity': severity.value,
            'traceback': traceback.format_exc(),
            'context': context or {}
        }

        with self._lock:
            self.errors.append(error_record)
            self.error_counts[signature] += 1

            if signature not in self.error_signatures:
                self.error_signatures[signature] = {
                    'first_seen': error_record['timestamp'],
                    'last_seen': error_record['timestamp'],
                    'count': 0,
                    'category': category.value,
                    'severity': severity.value,
                    'example': error_record
                }

            self.error_signatures[signature]['last_seen'] = error_record['timestamp']
            self.error_signatures[signature]['count'] += 1

            # Clean old errors outside time window
            self._clean_old_errors()

        return signature

    def _clean_old_errors(self) -> None:
        """Remove errors outside the time window."""
        current_time = time.time()
        cutoff_time = current_time - self.window_size

        while self.errors and self.errors[0]['timestamp'] < cutoff_time:
            old_error = self.errors.popleft()
            signature = old_error['signature']
            self.error_counts[signature] -= 1

            if self.error_counts[signature] <= 0:
                del self.error_counts[signature]

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        with self._lock:
            self._clean_old_errors()

            total_errors = len(self.errors)
            unique_errors = len(self.error_counts)

            # Get top errors by frequency
            top_errors = sorted(
                self.error_signatures.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:10]

            # Count by category
            category_counts = defaultdict(int)
            severity_counts = defaultdict(int)

            for error in self.errors:
                category_counts[error['category']] += 1
                severity_counts[error['severity']] += 1

            return {
                'total_errors': total_errors,
                'unique_errors': unique_errors,
                'window_size_seconds': self.window_size,
                'top_errors': [
                    {
                        'signature': sig,
                        'count': data['count'],
                        'category': data['category'],
                        'severity': data['severity'],
                        'first_seen': datetime.fromtimestamp(data['first_seen']).isoformat(),
                        'last_seen': datetime.fromtimestamp(data['last_seen']).isoformat(),
                        'message': data['example']['message']
                    }
                    for sig, data in top_errors
                ],
                'by_category': dict(category_counts),
                'by_severity': dict(severity_counts)
            }

    def get_error_details(self, signature: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific error signature."""
        with self._lock:
            return self.error_signatures.get(signature)


class SelfHealingSystem:
    """
    Orchestrates self-healing capabilities for common errors.
    """

    def __init__(self):
        self.healing_strategies = {}
        self.healing_history = deque(maxlen=1000)
        self._lock = threading.Lock()

    def register_strategy(self, category: ErrorCategory,
                         healing_func: Callable[[Exception, Dict], bool]) -> None:
        """
        Register a healing strategy for an error category.

        Args:
            category: Error category to handle
            healing_func: Function that attempts to heal the error.
                         Should return True if healing was successful.
        """
        self.healing_strategies[category] = healing_func
        logger.info(f"Registered healing strategy for {category.value}")

    def attempt_healing(self, exception: Exception,
                       context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Attempt to heal an error using registered strategies.

        Returns:
            True if healing was successful, False otherwise
        """
        category, severity = ErrorClassifier.classify_error(exception)
        context = context or {}

        healing_record = {
            'timestamp': time.time(),
            'category': category.value,
            'severity': severity.value,
            'exception': str(exception),
            'success': False,
            'strategy_used': None
        }

        try:
            if category in self.healing_strategies:
                healing_func = self.healing_strategies[category]
                healing_record['strategy_used'] = healing_func.__name__

                logger.info(
                    f"Attempting self-healing for {category.value} error using "
                    f"{healing_func.__name__}"
                )

                success = healing_func(exception, context)
                healing_record['success'] = success

                if success:
                    logger.info(f"Successfully healed {category.value} error")
                else:
                    logger.warning(f"Failed to heal {category.value} error")

                return success
            else:
                logger.warning(f"No healing strategy registered for {category.value}")
                return False

        except Exception as heal_error:
            logger.error(f"Error during healing attempt: {heal_error}")
            healing_record['healing_error'] = str(heal_error)
            return False

        finally:
            with self._lock:
                self.healing_history.append(healing_record)

    def get_healing_stats(self) -> Dict[str, Any]:
        """Get statistics about healing attempts."""
        with self._lock:
            total_attempts = len(self.healing_history)
            successful_heals = sum(1 for h in self.healing_history if h['success'])
            success_rate = (successful_heals / total_attempts * 100) if total_attempts > 0 else 0

            by_category = defaultdict(lambda: {'attempts': 0, 'successes': 0})

            for heal in self.healing_history:
                category = heal['category']
                by_category[category]['attempts'] += 1
                if heal['success']:
                    by_category[category]['successes'] += 1

            return {
                'total_attempts': total_attempts,
                'successful_heals': successful_heals,
                'success_rate_percentage': round(success_rate, 2),
                'by_category': {
                    cat: {
                        **stats,
                        'success_rate': (stats['successes'] / stats['attempts'] * 100)
                        if stats['attempts'] > 0 else 0
                    }
                    for cat, stats in by_category.items()
                }
            }


class ErrorRemediationSystem:
    """
    Main error remediation system integrating all components.
    """

    def __init__(self):
        self.classifier = ErrorClassifier()
        self.aggregator = ErrorAggregator()
        self.self_healing = SelfHealingSystem()
        self.active_circuit_breakers = {}

        # Register default healing strategies
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register default healing strategies for common errors."""

        def heal_network_error(exception: Exception, context: Dict) -> bool:
            """Attempt to heal network errors."""
            # Could implement connection reset, DNS cache clear, etc.
            logger.info("Attempting network error healing...")
            time.sleep(1)  # Simulate healing action
            return False  # In real implementation, would check if network is restored

        def heal_database_error(exception: Exception, context: Dict) -> bool:
            """Attempt to heal database errors."""
            # Could implement connection pool reset, transaction rollback, etc.
            logger.info("Attempting database error healing...")
            return False  # Would implement actual database recovery

        self.self_healing.register_strategy(ErrorCategory.NETWORK, heal_network_error)
        self.self_healing.register_strategy(ErrorCategory.DATABASE, heal_database_error)

    def handle_error(self, exception: Exception,
                    context: Optional[Dict[str, Any]] = None,
                    attempt_healing: bool = True) -> Dict[str, Any]:
        """
        Comprehensive error handling.

        Returns:
            Error handling result with healing status
        """
        # Record the error
        signature = self.aggregator.record_error(exception, context)
        category, severity = self.classifier.classify_error(exception)

        result = {
            'signature': signature,
            'category': category.value,
            'severity': severity.value,
            'timestamp': datetime.now().isoformat(),
            'healed': False
        }

        # Attempt healing for non-critical errors
        if attempt_healing and severity != ErrorSeverity.CRITICAL:
            healed = self.self_healing.attempt_healing(exception, context)
            result['healed'] = healed

        return result

    def create_circuit_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Create and register a circuit breaker."""
        breaker = CircuitBreaker(name=name, **kwargs)
        self.active_circuit_breakers[name] = breaker
        return breaker

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        error_summary = self.aggregator.get_error_summary()
        healing_stats = self.self_healing.get_healing_stats()

        circuit_breaker_stats = {
            name: breaker.get_stats()
            for name, breaker in self.active_circuit_breakers.items()
        }

        # Determine overall health status
        total_errors = error_summary['total_errors']
        critical_count = error_summary['by_severity'].get('critical', 0)

        if critical_count > 0:
            health_status = 'critical'
        elif total_errors > 100:
            health_status = 'degraded'
        elif total_errors > 10:
            health_status = 'warning'
        else:
            health_status = 'healthy'

        return {
            'status': health_status,
            'timestamp': datetime.now().isoformat(),
            'errors': error_summary,
            'healing': healing_stats,
            'circuit_breakers': circuit_breaker_stats
        }


# Global instance
remediation_system = ErrorRemediationSystem()

# Convenience functions
def retry_with_backoff(max_attempts: int = 3, base_delay: float = 1.0):
    """Convenience decorator for retry with exponential backoff."""
    strategy = RetryStrategy(max_attempts=max_attempts, base_delay=base_delay)
    return strategy


def with_circuit_breaker(name: str, failure_threshold: int = 5, recovery_timeout: float = 60.0):
    """Convenience decorator for circuit breaker protection."""
    breaker = remediation_system.create_circuit_breaker(
        name=name,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout
    )
    return breaker


if __name__ == "__main__":
    # Example usage and testing
    print("Error Remediation System - Example Usage")
    print("=" * 50)

    # Test error classification
    print("\n1. Testing Error Classification:")
    try:
        raise ConnectionError("Failed to connect to database")
    except Exception as e:
        category, severity = ErrorClassifier.classify_error(e)
        print(f"Error: {e}")
        print(f"Category: {category.value}, Severity: {severity.value}")
        result = remediation_system.handle_error(e)
        print(f"Handling result: {result}")

    # Test retry strategy
    print("\n2. Testing Retry Strategy:")

    @retry_with_backoff(max_attempts=3, base_delay=0.5)
    def flaky_function():
        import random
        if random.random() < 0.7:
            raise Exception("Random failure")
        return "Success"

    try:
        result = flaky_function()
        print(f"Function result: {result}")
    except Exception as e:
        print(f"Function failed after retries: {e}")

    # Test circuit breaker
    print("\n3. Testing Circuit Breaker:")

    @with_circuit_breaker(name='test_service', failure_threshold=3)
    def unreliable_service():
        raise Exception("Service unavailable")

    for i in range(5):
        try:
            unreliable_service()
        except Exception as e:
            print(f"Attempt {i+1}: {e}")

    # Get system health
    print("\n4. System Health Report:")
    health = remediation_system.get_system_health()
    print(json.dumps(health, indent=2))

    print("\nAll tests completed!")
