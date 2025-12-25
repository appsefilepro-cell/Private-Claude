#!/usr/bin/env python3
"""
End-to-End Integration Tests
Tests the complete system integration framework
"""

import asyncio
import pytest
import json
from datetime import datetime
from typing import Dict, List

# Import services
from event_bus import (
    event_bus, Event, EventType, Priority,
    publish_git_event, publish_app_status, publish_test_result
)
from email_notifier import EmailNotifier, EmailConfig
from zapier_integration import ZapierIntegration, ZapierConfig
from postman_runner import PostmanRunner


class TestEventBus:
    """Test event bus functionality"""

    @pytest.mark.asyncio
    async def test_event_publishing(self):
        """Test publishing events to event bus"""
        # Create test event
        event = Event(
            event_type=EventType.APP_SUCCESS,
            source='test-app',
            timestamp=datetime.utcnow().isoformat(),
            data={'test': 'data'},
            priority=Priority.LOW
        )

        # Publish event
        await event_bus.publish(event)

        # Check event in history
        recent = event_bus.get_recent_events(limit=1)
        assert len(recent) >= 1
        assert recent[-1]['event_type'] == EventType.APP_SUCCESS.value

    @pytest.mark.asyncio
    async def test_event_subscription(self):
        """Test subscribing to events"""
        received_events = []

        async def test_handler(event: Event):
            received_events.append(event)

        # Subscribe
        event_bus.subscribe(EventType.APP_ERROR, test_handler)

        # Publish event
        await publish_app_status(
            app_name='test',
            status='error',
            details='test error',
            success=False
        )

        # Wait for async processing
        await asyncio.sleep(0.1)

        # Check handler received event
        assert len(received_events) > 0
        assert received_events[-1].event_type == EventType.APP_ERROR

    def test_event_stats(self):
        """Test event bus statistics"""
        stats = event_bus.get_stats()

        assert 'total_events' in stats
        assert 'events_by_type' in stats
        assert 'events_by_priority' in stats

    @pytest.mark.asyncio
    async def test_git_event_publishing(self):
        """Test publishing git events"""
        await publish_git_event(
            source='github',
            event_type=EventType.GITHUB_PUSH,
            repo='test-repo',
            branch='main',
            author='test@example.com',
            message='Test commit'
        )

        recent = event_bus.get_recent_events(limit=1)
        assert recent[-1]['event_type'] == EventType.GITHUB_PUSH.value

    @pytest.mark.asyncio
    async def test_test_result_publishing(self):
        """Test publishing test results"""
        await publish_test_result(
            test_name='Integration Tests',
            passed=True,
            total_tests=10,
            failed_tests=0,
            duration=5.2
        )

        recent = event_bus.get_recent_events(limit=1)
        assert recent[-1]['event_type'] == EventType.POSTMAN_TEST_COMPLETE.value


class TestEmailNotifier:
    """Test email notification service"""

    def test_email_config(self):
        """Test email configuration"""
        config = EmailConfig()
        assert config.smtp_host is not None
        assert config.from_email is not None

    def test_email_template_loading(self):
        """Test email template loading"""
        notifier = EmailNotifier()
        assert 'event_notification' in notifier.email_templates
        assert 'test_results' in notifier.email_templates

    @pytest.mark.asyncio
    async def test_event_summary_generation(self):
        """Test event summary generation"""
        notifier = EmailNotifier()

        # Test push event
        event = Event(
            event_type=EventType.GITHUB_PUSH,
            source='github',
            timestamp=datetime.utcnow().isoformat(),
            data={
                'repository': 'test-repo',
                'branch': 'main',
                'author': 'test@example.com'
            }
        )

        summary = notifier._generate_event_summary(event)
        assert 'test-repo' in summary
        assert 'main' in summary


class TestZapierIntegration:
    """Test Zapier integration"""

    def test_zapier_config(self):
        """Test Zapier configuration"""
        config = ZapierConfig()
        assert isinstance(config.webhook_urls, dict)

    @pytest.mark.asyncio
    async def test_webhook_type_detection(self):
        """Test webhook type detection"""
        integration = ZapierIntegration()

        # Test git event
        git_event = Event(
            event_type=EventType.GITHUB_PUSH,
            source='github',
            timestamp=datetime.utcnow().isoformat(),
            data={}
        )
        assert integration._get_webhook_type(git_event) == 'git_events'

        # Test error event
        error_event = Event(
            event_type=EventType.APP_ERROR,
            source='app',
            timestamp=datetime.utcnow().isoformat(),
            data={},
            priority=Priority.CRITICAL
        )
        assert integration._get_webhook_type(error_event) == 'app_errors'


class TestPostmanRunner:
    """Test Postman runner"""

    def test_postman_config(self):
        """Test Postman configuration"""
        runner = PostmanRunner()
        assert runner.config is not None

    def test_newman_check(self):
        """Test Newman CLI check"""
        runner = PostmanRunner()
        # Newman may or may not be installed
        assert isinstance(runner.newman_installed, bool)

    def test_result_parsing(self):
        """Test Newman result parsing"""
        runner = PostmanRunner()

        # Mock Newman results
        mock_results = {
            'run': {
                'info': {'name': 'Test Collection'},
                'stats': {
                    'assertions': {'total': 10, 'failed': 2},
                    'requests': {'total': 5, 'failed': 1}
                },
                'executions': [
                    {
                        'assertions': [
                            {
                                'assertion': 'Status code is 200',
                                'error': {'message': 'Expected 200, got 404'}
                            }
                        ]
                    }
                ]
            }
        }

        results = runner._parse_newman_results(mock_results, 10.5)

        assert results['success'] is False
        assert results['total_tests'] == 10
        assert results['failed_tests'] == 2
        assert results['passed_tests'] == 8
        assert len(results['failures']) > 0


class TestEndToEndFlow:
    """Test complete end-to-end integration flow"""

    @pytest.mark.asyncio
    async def test_git_push_flow(self):
        """Test complete flow for git push event"""
        events_received = []

        async def capture_events(event: Event):
            events_received.append(event)

        # Subscribe to all events
        event_bus.subscribe_all(capture_events)

        # Simulate git push
        await publish_git_event(
            source='github',
            event_type=EventType.GITHUB_PUSH,
            repo='test-repo',
            branch='main',
            author='developer@example.com',
            message='Feature update',
            commits_count=3
        )

        # Wait for processing
        await asyncio.sleep(0.2)

        # Verify event was received
        assert len(events_received) > 0
        git_events = [e for e in events_received if e.event_type == EventType.GITHUB_PUSH]
        assert len(git_events) > 0

    @pytest.mark.asyncio
    async def test_test_failure_notification_flow(self):
        """Test complete flow for test failure"""
        events_received = []

        async def capture_events(event: Event):
            events_received.append(event)

        event_bus.subscribe(EventType.POSTMAN_TEST_FAILURE, capture_events)

        # Simulate test failure
        await publish_test_result(
            test_name='API Tests',
            passed=False,
            total_tests=20,
            failed_tests=3,
            duration=15.7,
            failures=[
                {'name': 'test_auth', 'error': 'Token expired'},
                {'name': 'test_db', 'error': 'Connection failed'}
            ]
        )

        # Wait for processing
        await asyncio.sleep(0.2)

        # Verify notification was triggered
        failure_events = [e for e in events_received if e.event_type == EventType.POSTMAN_TEST_FAILURE]
        assert len(failure_events) > 0
        assert failure_events[0].should_notify_user() is True

    @pytest.mark.asyncio
    async def test_app_error_flow(self):
        """Test complete flow for app error"""
        events_received = []

        async def capture_events(event: Event):
            events_received.append(event)

        event_bus.subscribe(EventType.APP_ERROR, capture_events)

        # Simulate app error
        await publish_app_status(
            app_name='trading-bot',
            status='error',
            details='Database connection lost',
            success=False
        )

        # Wait for processing
        await asyncio.sleep(0.2)

        # Verify error was captured
        error_events = [e for e in events_received if e.event_type == EventType.APP_ERROR]
        assert len(error_events) > 0
        assert error_events[0].priority == Priority.HIGH


class TestSystemHealth:
    """Test system health and monitoring"""

    def test_event_bus_stats(self):
        """Test event bus statistics collection"""
        stats = event_bus.get_stats()

        assert isinstance(stats, dict)
        assert 'total_events' in stats
        assert isinstance(stats['total_events'], int)

    @pytest.mark.asyncio
    async def test_health_check_event(self):
        """Test health check event publishing"""
        event = Event(
            event_type=EventType.SYSTEM_HEALTH_CHECK,
            source='test',
            timestamp=datetime.utcnow().isoformat(),
            data={
                'services_running': 5,
                'memory_usage': 125.5,
                'cpu_usage': 15.2
            },
            priority=Priority.LOW
        )

        await event_bus.publish(event)

        recent = event_bus.get_recent_events(
            limit=10,
            event_type=EventType.SYSTEM_HEALTH_CHECK
        )
        assert len(recent) > 0


# Test runner
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
