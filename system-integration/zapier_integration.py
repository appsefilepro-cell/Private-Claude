#!/usr/bin/env python3
"""
Zapier Integration Service
Sends events to Zapier webhooks for workflow automation
Receives webhook callbacks from Zapier
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from aiohttp import web
import os
import json

from event_bus import event_bus, EventType, Event, Priority


logger = logging.getLogger(__name__)


class ZapierConfig:
    """Zapier configuration"""
    def __init__(self):
        # Zapier webhook URLs for different triggers
        self.webhook_urls = {
            'git_events': os.getenv('ZAPIER_GIT_WEBHOOK', ''),
            'test_results': os.getenv('ZAPIER_TEST_WEBHOOK', ''),
            'app_errors': os.getenv('ZAPIER_ERROR_WEBHOOK', ''),
            'general': os.getenv('ZAPIER_GENERAL_WEBHOOK', '')
        }

        # Email configuration for Zapier
        self.email_enabled = os.getenv('ZAPIER_EMAIL_ENABLED', 'true').lower() == 'true'
        self.email_address = os.getenv('ZAPIER_EMAIL_ADDRESS', 'noreply@anthropic.com')

        # Zapier app credentials (for premium features)
        self.api_key = os.getenv('ZAPIER_API_KEY', '')


class ZapierIntegration:
    """Zapier integration service"""

    def __init__(self, config: Optional[ZapierConfig] = None):
        self.config = config or ZapierConfig()
        self.sent_events: List[str] = []

    async def send_to_zapier(self, webhook_type: str, data: Dict[str, Any]) -> bool:
        """Send data to Zapier webhook"""
        webhook_url = self.config.webhook_urls.get(webhook_type)

        if not webhook_url:
            logger.warning(f"No webhook URL configured for type: {webhook_type}")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in [200, 201]:
                        logger.info(f"Successfully sent data to Zapier webhook: {webhook_type}")
                        return True
                    else:
                        logger.error(f"Zapier webhook returned status {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Error sending to Zapier: {e}")
            return False

    async def handle_event(self, event: Event):
        """Handle event bus events and forward to Zapier"""
        # Determine webhook type based on event
        webhook_type = self._get_webhook_type(event)

        # Prepare data for Zapier
        zapier_data = {
            'event_id': event.event_id,
            'event_type': event.event_type.value,
            'source': event.source,
            'timestamp': event.timestamp,
            'priority': event.priority.name,
            'data': event.data,
            'email_address': self.config.email_address,
            'should_send_email': event.should_notify_user() and self.config.email_enabled
        }

        # Send to Zapier
        success = await self.send_to_zapier(webhook_type, zapier_data)

        if success:
            self.sent_events.append(event.event_id)

            # Publish workflow trigger event
            workflow_event = Event(
                event_type=EventType.ZAPIER_WORKFLOW_TRIGGER,
                source='zapier',
                timestamp=datetime.utcnow().isoformat(),
                data={
                    'webhook_type': webhook_type,
                    'original_event_id': event.event_id,
                    'original_event_type': event.event_type.value
                },
                priority=Priority.LOW
            )
            await event_bus.publish(workflow_event)

    def _get_webhook_type(self, event: Event) -> str:
        """Determine which Zapier webhook to use for event"""
        event_value = event.event_type.value.lower()

        if 'git' in event_value or 'push' in event_value or 'pull_request' in event_value:
            return 'git_events'
        elif 'test' in event_value or 'postman' in event_value:
            return 'test_results'
        elif 'error' in event_value or event.priority == Priority.CRITICAL:
            return 'app_errors'
        else:
            return 'general'

    async def handle_zapier_callback(self, request: web.Request) -> web.Response:
        """Handle callbacks from Zapier workflows"""
        try:
            payload = await request.json()

            logger.info(f"Received Zapier callback: {payload.get('workflow_name', 'unknown')}")

            # Publish workflow complete event
            event = Event(
                event_type=EventType.ZAPIER_WORKFLOW_COMPLETE,
                source='zapier',
                timestamp=datetime.utcnow().isoformat(),
                data={
                    'workflow_name': payload.get('workflow_name', 'unknown'),
                    'status': payload.get('status', 'completed'),
                    'result': payload.get('result', {}),
                    'email_sent': payload.get('email_sent', False)
                },
                priority=Priority.LOW
            )
            await event_bus.publish(event)

            return web.Response(text="OK")

        except Exception as e:
            logger.error(f"Error handling Zapier callback: {e}")
            return web.Response(status=500, text=str(e))


class ZapierEmailWorkflow:
    """Helper class for Zapier email workflows"""

    def __init__(self, config: Optional[ZapierConfig] = None):
        self.config = config or ZapierConfig()

    def create_email_data(self, event: Event) -> Dict[str, Any]:
        """Create email data for Zapier email workflow"""
        subject = self._generate_email_subject(event)
        body = self._generate_email_body(event)

        return {
            'to': self.config.email_address,
            'subject': subject,
            'body': body,
            'html': True,
            'event_data': event.to_dict()
        }

    def _generate_email_subject(self, event: Event) -> str:
        """Generate email subject line"""
        priority_prefix = f"[{event.priority.name}]" if event.priority.value >= 3 else ""

        event_type = event.event_type.value

        if 'push' in event_type.lower():
            return f"{priority_prefix} New code pushed to {event.data.get('repository', 'repository')}"
        elif 'pull_request' in event_type.lower() or 'merge_request' in event_type.lower():
            return f"{priority_prefix} New PR: {event.data.get('title', 'Untitled')}"
        elif 'test' in event_type.lower():
            passed = event.data.get('passed', False)
            status = "PASSED" if passed else "FAILED"
            return f"{priority_prefix} Tests {status}: {event.data.get('test_name', 'Unknown')}"
        elif 'error' in event_type.lower():
            return f"[ERROR] {event.source}: {event.data.get('details', 'Error occurred')}"
        else:
            return f"{priority_prefix} System Event: {event_type}"

    def _generate_email_body(self, event: Event) -> str:
        """Generate email body (plain text)"""
        lines = [
            f"Event: {event.event_type.value}",
            f"Source: {event.source}",
            f"Time: {event.timestamp}",
            f"Priority: {event.priority.name}",
            "",
            "Details:",
        ]

        for key, value in event.data.items():
            lines.append(f"  {key}: {value}")

        lines.extend([
            "",
            "---",
            "This is an automated notification from Private Claude System",
            f"Event ID: {event.event_id}"
        ])

        return "\n".join(lines)


# Subscribe to event bus
async def setup_zapier_integration():
    """Setup Zapier integration with event bus"""
    integration = ZapierIntegration()

    # Subscribe to all events
    event_bus.subscribe_all(integration.handle_event)

    logger.info("Zapier integration setup complete")

    return integration


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def test():
        integration = await setup_zapier_integration()

        # Test event
        test_event = Event(
            event_type=EventType.APP_SUCCESS,
            source='test-app',
            timestamp=datetime.utcnow().isoformat(),
            data={
                'status': 'running',
                'details': 'Test notification'
            },
            priority=Priority.HIGH
        )

        await event_bus.publish(test_event)

        # Wait for async processing
        await asyncio.sleep(2)

        print(f"Sent {len(integration.sent_events)} events to Zapier")

    asyncio.run(test())
