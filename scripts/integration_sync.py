#!/usr/bin/env python3
"""
Integration Sync Manager
Orchestrates data synchronization between Zapier, Slack, GitHub, E2B, and other services
Features: Webhook routing, retry logic, data compression, batching, rate limiting
Optimized for minimal data usage on free tier
"""

import os
import json
import gzip
import logging
import hashlib
import time
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
E2B_API_KEY = os.getenv('E2B_API_KEY')
E2B_WEBHOOK_URL = os.getenv('E2B_WEBHOOK_URL')
ZAPIER_WEBHOOK_URL = os.getenv('ZAPIER_WEBHOOK_URL')
SLACK_WEBHOOK_GENERAL = os.getenv('SLACK_WEBHOOK_GENERAL')
SLACK_WEBHOOK_E2B = os.getenv('SLACK_WEBHOOK_E2B')
SLACK_WEBHOOK_TRADING = os.getenv('SLACK_WEBHOOK_TRADING')
SLACK_WEBHOOK_ERRORS = os.getenv('SLACK_WEBHOOK_ERRORS')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'integrations')
DATA_OPTIMIZATION_ENABLED = True
BATCH_SIZE_LIMIT = 10
BATCH_TIMEOUT_SECONDS = 60
MAX_RETRIES = 3
RETRY_BACKOFF_MULTIPLIER = 2
INITIAL_RETRY_DELAY = 1


class EventType(Enum):
    """Supported event types"""
    E2B_EXECUTION_SUCCESS = "e2b.execution.success"
    E2B_EXECUTION_FAILURE = "e2b.execution.failure"
    GITHUB_PUSH = "github.push"
    GITHUB_PR = "github.pull_request"
    TRADING_SIGNAL_BUY = "trading.signal.buy"
    TRADING_SIGNAL_SELL = "trading.signal.sell"
    ERROR_ALERT = "error.alert"
    SLACK_MESSAGE = "slack.message"
    ZAPIER_EVENT = "zapier.event"


class SeverityLevel(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Event:
    """Represents a synchronization event"""
    event_type: EventType
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    priority: int = 5
    severity: SeverityLevel = SeverityLevel.LOW
    batch_key: Optional[str] = None
    retry_count: int = 0
    max_retries: int = MAX_RETRIES

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type.value,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'priority': self.priority
        }


class DataCompressor:
    """Handles data compression and optimization"""

    @staticmethod
    def compress_payload(data: Dict[str, Any]) -> bytes:
        """Compress JSON payload using gzip"""
        json_str = json.dumps(data, separators=(',', ':'))
        return gzip.compress(json_str.encode('utf-8'))

    @staticmethod
    def decompress_payload(data: bytes) -> Dict[str, Any]:
        """Decompress gzip payload"""
        decompressed = gzip.decompress(data)
        return json.loads(decompressed.decode('utf-8'))

    @staticmethod
    def minimize_payload(data: Dict[str, Any], max_size: int = 256) -> Dict[str, Any]:
        """Remove unnecessary fields and truncate long strings"""
        minimized = {}

        # Keep only essential fields
        essential_fields = [
            'event_type', 'status', 'id', 'timestamp', 'source',
            'asset', 'signal_type', 'confidence', 'output', 'error'
        ]

        for key, value in data.items():
            if key in essential_fields:
                if isinstance(value, str) and len(value) > max_size:
                    minimized[key] = value[:max_size] + '...'
                else:
                    minimized[key] = value

        return minimized

    @staticmethod
    def calculate_compression_ratio(original: Dict[str, Any]) -> float:
        """Calculate compression ratio"""
        original_size = len(json.dumps(original))
        compressed_size = len(DataCompressor.compress_payload(original))
        return (1 - compressed_size / original_size) * 100 if original_size > 0 else 0


class WebhookRouter:
    """Routes events to appropriate webhook endpoints"""

    def __init__(self):
        self.config = self._load_slack_config()
        self.routing_rules = self.config.get('alert_routing', {}).get('rules', [])
        self.webhooks = self.config.get('webhooks', {})

    def _load_slack_config(self) -> Dict[str, Any]:
        """Load Slack configuration"""
        config_path = os.path.join(CONFIG_PATH, 'slack_config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Slack config: {e}")
            return {}

    def route_event(self, event: Event) -> List[str]:
        """Determine target webhooks for event"""
        targets = []

        for rule in self.routing_rules:
            if self._matches_rule(event, rule):
                targets.append(rule['target'])
                logger.info(f"Event matched routing rule: {rule['id']}")

        return targets if targets else [self.config.get('alert_routing', {}).get('default_target', 'general')]

    def _matches_rule(self, event: Event, rule: Dict[str, Any]) -> bool:
        """Check if event matches routing rule"""
        condition = rule.get('condition', {})

        # Check source
        source_match = condition.get('source') == '*' or condition.get('source') == event.source
        if not source_match:
            return False

        # Check event type
        event_types = condition.get('type', [])
        if event_types and isinstance(event_types, list):
            event_match = event.event_type.value in [t.replace('_', '.') for t in event_types]
            if not event_match:
                return False

        # Check severity
        severity = condition.get('severity')
        if severity and event.severity.value != severity:
            return False

        return rule.get('enabled', True)

    def get_webhook_url(self, target: str) -> Optional[str]:
        """Get webhook URL for target"""
        webhook_config = self.webhooks.get(target, {})
        url = webhook_config.get('url', '').replace('${', '').replace('}', '')

        # Resolve environment variables
        if url.startswith('SLACK_'):
            return os.getenv(url)
        elif url.startswith('ZAPIER_'):
            return os.getenv(url)
        elif url.startswith('E2B_'):
            return os.getenv(url)

        return webhook_config.get('url')


class BatchManager:
    """Manages event batching for efficient data transmission"""

    def __init__(self, batch_size: int = BATCH_SIZE_LIMIT, timeout: int = BATCH_TIMEOUT_SECONDS):
        self.batch_size = batch_size
        self.timeout = timeout
        self.batches: Dict[str, List[Event]] = defaultdict(list)
        self.batch_timers: Dict[str, threading.Timer] = {}
        self.lock = threading.Lock()

    def add_event(self, event: Event, callback) -> bool:
        """Add event to batch"""
        batch_key = event.batch_key or event.source

        with self.lock:
            self.batches[batch_key].append(event)

            # Cancel existing timer if any
            if batch_key in self.batch_timers:
                self.batch_timers[batch_key].cancel()

            # Check if batch is full
            if len(self.batches[batch_key]) >= self.batch_size:
                batch = self.batches.pop(batch_key)
                if batch_key in self.batch_timers:
                    self.batch_timers[batch_key].cancel()
                    del self.batch_timers[batch_key]
                callback(batch)
                return True

            # Set timeout timer
            timer = threading.Timer(
                self.timeout,
                self._flush_batch,
                args=[batch_key, callback]
            )
            timer.daemon = True
            timer.start()
            self.batch_timers[batch_key] = timer

        return False

    def _flush_batch(self, batch_key: str, callback):
        """Flush batch after timeout"""
        with self.lock:
            if batch_key in self.batches and self.batches[batch_key]:
                batch = self.batches.pop(batch_key)
                if batch_key in self.batch_timers:
                    del self.batch_timers[batch_key]
                callback(batch)

    def flush_all(self, callback):
        """Flush all pending batches"""
        with self.lock:
            for batch_key in list(self.batches.keys()):
                if self.batch_timers.get(batch_key):
                    self.batch_timers[batch_key].cancel()
                batch = self.batches.pop(batch_key)
                callback(batch)


class RetryManager:
    """Manages retry logic with exponential backoff"""

    def __init__(self, max_retries: int = MAX_RETRIES):
        self.max_retries = max_retries
        self.retry_queue = queue.Queue()
        self.retry_thread = threading.Thread(target=self._process_retries, daemon=True)
        self.retry_thread.start()

    def should_retry(self, event: Event) -> bool:
        """Check if event should be retried"""
        return event.retry_count < event.max_retries

    def get_retry_delay(self, event: Event) -> float:
        """Calculate retry delay with exponential backoff"""
        delay = INITIAL_RETRY_DELAY * (RETRY_BACKOFF_MULTIPLIER ** event.retry_count)
        return min(delay, 60)  # Cap at 60 seconds

    def schedule_retry(self, event: Event, callback):
        """Schedule event for retry"""
        event.retry_count += 1
        delay = self.get_retry_delay(event)
        self.retry_queue.put((event, callback, time.time() + delay))
        logger.info(f"Scheduled retry for event {event.event_type.value} (attempt {event.retry_count})")

    def _process_retries(self):
        """Process queued retries"""
        while True:
            try:
                if not self.retry_queue.empty():
                    event, callback, retry_time = self.retry_queue.get(timeout=1)

                    # Check if ready to retry
                    if time.time() >= retry_time:
                        callback(event)
                    else:
                        # Put back in queue
                        self.retry_queue.put((event, callback, retry_time))
                        time.sleep(0.1)
            except queue.Empty:
                time.sleep(1)
            except Exception as e:
                logger.error(f"Retry processing error: {e}")
                time.sleep(1)


class WebhookSender:
    """Sends data to webhooks with retry logic"""

    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10
        self.retry_manager = RetryManager()
        self.batch_manager = BatchManager()

    def send_webhook(self, url: str, data: Dict[str, Any], compress: bool = True) -> Tuple[bool, str]:
        """Send data to webhook"""
        if not url:
            return False, "No webhook URL provided"

        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Private-Claude/2.0'
            }

            if compress:
                compressed_data = DataCompressor.compress_payload(data)
                headers['Content-Encoding'] = 'gzip'
                response = self.session.post(url, data=compressed_data, headers=headers)
            else:
                response = self.session.post(url, json=data, headers=headers)

            if response.status_code == 200:
                return True, "Success"
            else:
                return False, f"Status {response.status_code}"

        except requests.Timeout:
            return False, "Request timeout"
        except requests.ConnectionError:
            return False, "Connection error"
        except Exception as e:
            return False, str(e)

    def send_batch(self, events: List[Event], target: str) -> bool:
        """Send batch of events"""
        webhook_url = self._get_webhook_url(target)
        if not webhook_url:
            return False

        batch_data = {
            'batch': [event.to_dict() for event in events],
            'batch_size': len(events),
            'timestamp': datetime.utcnow().isoformat()
        }

        success, message = self.send_webhook(webhook_url, batch_data, compress=True)
        if success:
            logger.info(f"Batch of {len(events)} events sent to {target}")
        else:
            logger.warning(f"Failed to send batch to {target}: {message}")

        return success

    def _get_webhook_url(self, target: str) -> Optional[str]:
        """Get webhook URL for target"""
        mapping = {
            'e2b_alerts': SLACK_WEBHOOK_E2B,
            'trading_signals': SLACK_WEBHOOK_TRADING,
            'error_alerts': SLACK_WEBHOOK_ERRORS,
            'general': SLACK_WEBHOOK_GENERAL,
            'zapier': ZAPIER_WEBHOOK_URL,
            'e2b': E2B_WEBHOOK_URL
        }
        return mapping.get(target)


class IntegrationSyncManager:
    """Main orchestrator for integration synchronization"""

    def __init__(self):
        self.router = WebhookRouter()
        self.webhook_sender = WebhookSender()
        self.batch_manager = self.webhook_sender.batch_manager
        self.retry_manager = self.webhook_sender.retry_manager
        self.event_queue = queue.Queue()
        self.metrics = {
            'events_processed': 0,
            'events_failed': 0,
            'batches_sent': 0,
            'total_data_compressed': 0,
            'compression_ratio_avg': 0
        }
        self.lock = threading.Lock()

    def process_event(self, event: Event) -> bool:
        """Process a single event"""
        try:
            # Minimize payload if compression enabled
            if DATA_OPTIMIZATION_ENABLED:
                event.data = DataCompressor.minimize_payload(event.data)

            # Route event to appropriate webhooks
            targets = self.router.route_event(event)

            success = True
            for target in targets:
                # Add to batch or send directly
                if event.event_type in [EventType.E2B_EXECUTION_SUCCESS, EventType.ZAPIER_EVENT]:
                    # These types can be batched
                    self.batch_manager.add_event(
                        event,
                        lambda batch: self._send_batch_callback(batch, target)
                    )
                else:
                    # Send immediately for high-priority events
                    webhook_url = self.router.get_webhook_url(target)
                    result, message = self.webhook_sender.send_webhook(
                        webhook_url,
                        event.to_dict(),
                        compress=True
                    )

                    if not result and self.retry_manager.should_retry(event):
                        self.retry_manager.schedule_retry(
                            event,
                            lambda e: self.process_event(e)
                        )
                        success = False

            return success

        except Exception as e:
            logger.error(f"Error processing event: {e}")
            if self.retry_manager.should_retry(event):
                self.retry_manager.schedule_retry(
                    event,
                    lambda e: self.process_event(e)
                )
            return False

    def _send_batch_callback(self, batch: List[Event], target: str):
        """Callback for batch sending"""
        success = self.webhook_sender.send_batch(batch, target)
        with self.lock:
            if success:
                self.metrics['batches_sent'] += 1
                self.metrics['events_processed'] += len(batch)
            else:
                self.metrics['events_failed'] += len(batch)

    def create_e2b_event(self, status: str, execution_id: str, output: str = '') -> Event:
        """Create E2B execution event"""
        event_type = EventType.E2B_EXECUTION_SUCCESS if status == 'success' else EventType.E2B_EXECUTION_FAILURE
        severity = SeverityLevel.LOW if status == 'success' else SeverityLevel.HIGH

        return Event(
            event_type=event_type,
            source='e2b',
            timestamp=datetime.utcnow(),
            data={
                'execution_id': execution_id,
                'status': status,
                'output': output,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority=8 if status == 'failed' else 5,
            severity=severity,
            batch_key='e2b_executions'
        )

    def create_github_event(self, event_type: str, repo: str, data: Dict[str, Any]) -> Event:
        """Create GitHub event"""
        return Event(
            event_type=EventType.GITHUB_PUSH if event_type == 'push' else EventType.GITHUB_PR,
            source='github',
            timestamp=datetime.utcnow(),
            data={
                'repository': repo,
                'event_type': event_type,
                **data
            },
            priority=6,
            severity=SeverityLevel.MEDIUM
        )

    def create_trading_event(self, signal_type: str, asset: str, confidence: float,
                            entry_price: float, stop_loss: float, take_profit: float) -> Event:
        """Create trading signal event"""
        event_type = EventType.TRADING_SIGNAL_BUY if signal_type == 'buy' else EventType.TRADING_SIGNAL_SELL

        return Event(
            event_type=event_type,
            source='trading',
            timestamp=datetime.utcnow(),
            data={
                'signal_type': signal_type,
                'asset': asset,
                'confidence': confidence,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            },
            priority=9 if confidence >= 75 else 6,
            severity=SeverityLevel.HIGH if confidence >= 75 else SeverityLevel.MEDIUM
        )

    def create_error_event(self, error_type: str, service: str, severity: str,
                          error_count: int, stack_trace: str = '') -> Event:
        """Create error alert event"""
        sev = SeverityLevel[severity.upper()]

        return Event(
            event_type=EventType.ERROR_ALERT,
            source='error',
            timestamp=datetime.utcnow(),
            data={
                'error_type': error_type,
                'service': service,
                'severity': severity,
                'error_count': error_count,
                'stack_trace': stack_trace
            },
            priority=10 if severity == 'critical' else 7,
            severity=sev
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get synchronization metrics"""
        with self.lock:
            return self.metrics.copy()

    def reset_metrics(self):
        """Reset metrics"""
        with self.lock:
            self.metrics = {
                'events_processed': 0,
                'events_failed': 0,
                'batches_sent': 0,
                'total_data_compressed': 0,
                'compression_ratio_avg': 0
            }


# Global instance
sync_manager = IntegrationSyncManager()


def main():
    """Example usage and testing"""
    logger.info("Starting Integration Sync Manager")

    # Test E2B event
    e2b_event = sync_manager.create_e2b_event(
        status='success',
        execution_id='exec-12345',
        output='Python code executed successfully'
    )
    sync_manager.process_event(e2b_event)

    # Test trading event
    trading_event = sync_manager.create_trading_event(
        signal_type='buy',
        asset='AAPL',
        confidence=85.5,
        entry_price=150.25,
        stop_loss=145.00,
        take_profit=160.00
    )
    sync_manager.process_event(trading_event)

    # Test error event
    error_event = sync_manager.create_error_event(
        error_type='DatabaseConnectionError',
        service='user-service',
        severity='high',
        error_count=5,
        stack_trace='Connection timeout at line 42'
    )
    sync_manager.process_event(error_event)

    # Print metrics
    time.sleep(2)
    metrics = sync_manager.get_metrics()
    logger.info(f"Metrics: {json.dumps(metrics, indent=2)}")


if __name__ == '__main__':
    main()
