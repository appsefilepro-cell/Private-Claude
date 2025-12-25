#!/usr/bin/env python3
"""
Central Event Bus System for Inter-App Communication
Handles events from all systems and routes notifications appropriately
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, asdict
import aiohttp
from collections import defaultdict
import hashlib


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """All supported event types in the system"""
    # Git events
    GITLAB_PUSH = "gitlab.push"
    GITLAB_MERGE_REQUEST = "gitlab.merge_request"
    GITHUB_PUSH = "github.push"
    GITHUB_PULL_REQUEST = "github.pull_request"

    # API Testing events
    POSTMAN_TEST_START = "postman.test.start"
    POSTMAN_TEST_COMPLETE = "postman.test.complete"
    POSTMAN_TEST_FAILURE = "postman.test.failure"

    # Zapier workflow events
    ZAPIER_WORKFLOW_TRIGGER = "zapier.workflow.trigger"
    ZAPIER_WORKFLOW_COMPLETE = "zapier.workflow.complete"

    # Python app events
    APP_STATUS_UPDATE = "app.status.update"
    APP_ERROR = "app.error"
    APP_SUCCESS = "app.success"

    # System events
    SYSTEM_HEALTH_CHECK = "system.health_check"
    SYSTEM_ERROR = "system.error"

    # Email events
    EMAIL_SENT = "email.sent"
    EMAIL_FAILED = "email.failed"


class Priority(Enum):
    """Event priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """Event data structure"""
    event_type: EventType
    source: str
    timestamp: str
    data: Dict[str, Any]
    priority: Priority = Priority.MEDIUM
    event_id: Optional[str] = None

    def __post_init__(self):
        if not self.event_id:
            # Generate unique event ID
            content = f"{self.event_type.value}{self.source}{self.timestamp}"
            self.event_id = hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'source': self.source,
            'timestamp': self.timestamp,
            'priority': self.priority.value,
            'data': self.data
        }

    def should_notify_user(self) -> bool:
        """Determine if this event should trigger user notification"""
        # Notify on high/critical priority or specific event types
        if self.priority in [Priority.HIGH, Priority.CRITICAL]:
            return True

        # Always notify on errors, test failures, and workflow completions
        notify_types = [
            EventType.APP_ERROR,
            EventType.SYSTEM_ERROR,
            EventType.POSTMAN_TEST_FAILURE,
            EventType.ZAPIER_WORKFLOW_COMPLETE,
            EventType.GITHUB_PULL_REQUEST,
            EventType.GITLAB_MERGE_REQUEST
        ]

        return self.event_type in notify_types


class EventBus:
    """Central event bus for system-wide communication"""

    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.max_history = 1000
        self.email_notifier = None
        self.webhook_urls: Dict[str, str] = {}

    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe a handler to an event type"""
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler {handler.__name__} to {event_type.value}")

    def subscribe_all(self, handler: Callable):
        """Subscribe a handler to all event types"""
        for event_type in EventType:
            self.subscribe(event_type, handler)

    def set_email_notifier(self, notifier):
        """Set the email notification service"""
        self.email_notifier = notifier

    def add_webhook(self, name: str, url: str):
        """Add a webhook endpoint"""
        self.webhook_urls[name] = url
        logger.info(f"Added webhook: {name} -> {url}")

    async def publish(self, event: Event):
        """Publish an event to all subscribers"""
        logger.info(f"Publishing event: {event.event_type.value} from {event.source}")

        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        # Notify subscribers
        handlers = self.subscribers.get(event.event_type, [])
        tasks = []

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in handler {handler.__name__}: {e}")

        # Wait for async handlers
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        # Send email notification if needed
        if event.should_notify_user() and self.email_notifier:
            try:
                await self.email_notifier.send_event_notification(event)
            except Exception as e:
                logger.error(f"Error sending email notification: {e}")

        # Send to webhooks
        await self._send_to_webhooks(event)

    async def _send_to_webhooks(self, event: Event):
        """Send event to configured webhooks"""
        if not self.webhook_urls:
            return

        async with aiohttp.ClientSession() as session:
            tasks = []
            for name, url in self.webhook_urls.items():
                tasks.append(self._post_to_webhook(session, name, url, event))

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _post_to_webhook(self, session: aiohttp.ClientSession,
                                name: str, url: str, event: Event):
        """Post event to a webhook"""
        try:
            async with session.post(
                url,
                json=event.to_dict(),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    logger.info(f"Event sent to webhook {name}")
                else:
                    logger.warning(f"Webhook {name} returned status {response.status}")
        except Exception as e:
            logger.error(f"Error sending to webhook {name}: {e}")

    def get_recent_events(self, limit: int = 50,
                         event_type: Optional[EventType] = None) -> List[Dict]:
        """Get recent events"""
        events = self.event_history[-limit:]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return [e.to_dict() for e in events]

    def get_stats(self) -> Dict:
        """Get event bus statistics"""
        stats = {
            'total_events': len(self.event_history),
            'total_subscribers': sum(len(handlers) for handlers in self.subscribers.values()),
            'events_by_type': {},
            'events_by_priority': {}
        }

        for event in self.event_history:
            # Count by type
            event_type = event.event_type.value
            stats['events_by_type'][event_type] = stats['events_by_type'].get(event_type, 0) + 1

            # Count by priority
            priority = event.priority.name
            stats['events_by_priority'][priority] = stats['events_by_priority'].get(priority, 0) + 1

        return stats


# Global event bus instance
event_bus = EventBus()


# Utility functions for common operations
async def publish_git_event(source: str, event_type: EventType,
                            repo: str, branch: str, author: str,
                            message: str, **kwargs):
    """Publish a Git-related event"""
    event = Event(
        event_type=event_type,
        source=source,
        timestamp=datetime.utcnow().isoformat(),
        data={
            'repository': repo,
            'branch': branch,
            'author': author,
            'message': message,
            **kwargs
        },
        priority=Priority.MEDIUM
    )
    await event_bus.publish(event)


async def publish_app_status(app_name: str, status: str,
                             details: str, success: bool = True):
    """Publish an app status update"""
    event_type = EventType.APP_SUCCESS if success else EventType.APP_ERROR
    priority = Priority.MEDIUM if success else Priority.HIGH

    event = Event(
        event_type=event_type,
        source=app_name,
        timestamp=datetime.utcnow().isoformat(),
        data={
            'status': status,
            'details': details,
            'success': success
        },
        priority=priority
    )
    await event_bus.publish(event)


async def publish_test_result(test_name: str, passed: bool,
                              total_tests: int, failed_tests: int,
                              duration: float, **kwargs):
    """Publish a test result event"""
    event_type = EventType.POSTMAN_TEST_COMPLETE if passed else EventType.POSTMAN_TEST_FAILURE
    priority = Priority.MEDIUM if passed else Priority.HIGH

    event = Event(
        event_type=event_type,
        source='postman',
        timestamp=datetime.utcnow().isoformat(),
        data={
            'test_name': test_name,
            'passed': passed,
            'total_tests': total_tests,
            'failed_tests': failed_tests,
            'duration': duration,
            **kwargs
        },
        priority=priority
    )
    await event_bus.publish(event)


if __name__ == '__main__':
    # Example usage
    async def example_handler(event: Event):
        print(f"Received event: {event.event_type.value}")
        print(f"Data: {event.data}")

    # Subscribe to events
    event_bus.subscribe(EventType.GITHUB_PUSH, example_handler)
    event_bus.subscribe(EventType.APP_ERROR, example_handler)

    # Publish test events
    async def test():
        await publish_git_event(
            source='github',
            event_type=EventType.GITHUB_PUSH,
            repo='test-repo',
            branch='main',
            author='user@example.com',
            message='Test commit'
        )

        await publish_app_status(
            app_name='test-app',
            status='running',
            details='Application started successfully'
        )

        print("\nEvent Bus Stats:")
        print(json.dumps(event_bus.get_stats(), indent=2))

    asyncio.run(test())
