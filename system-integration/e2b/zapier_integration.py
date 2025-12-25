"""
Zapier Integration for E2B Sandbox
Handles notifications and automation workflows via Zapier
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from e2b_sandbox import ExecutionResult
from webhook_handler import WebhookEvent


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationLevel(Enum):
    """Notification severity levels"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    SMS = "sms"
    WEBHOOK = "webhook"


@dataclass
class Notification:
    """Notification data structure"""
    notification_id: str
    level: NotificationLevel
    title: str
    message: str
    timestamp: datetime
    channels: List[NotificationChannel]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['level'] = self.level.value
        result['timestamp'] = self.timestamp.isoformat()
        result['channels'] = [ch.value for ch in self.channels]
        return result


class ZapierClient:
    """
    Zapier webhook client for sending notifications and triggers
    """

    def __init__(self, webhook_url: str):
        """
        Initialize Zapier client

        Args:
            webhook_url: Zapier webhook URL
        """
        self.webhook_url = webhook_url
        self.session = requests.Session()
        logger.info("Zapier client initialized")

    def send_notification(self,
                         title: str,
                         message: str,
                         level: NotificationLevel = NotificationLevel.INFO,
                         metadata: Dict[str, Any] = None) -> bool:
        """
        Send notification via Zapier

        Args:
            title: Notification title
            message: Notification message
            level: Notification level
            metadata: Additional metadata

        Returns:
            Success status
        """
        if metadata is None:
            metadata = {}

        payload = {
            "title": title,
            "message": message,
            "level": level.value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }

        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Notification sent: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def send_execution_notification(self,
                                   execution_result: ExecutionResult,
                                   context: str = "") -> bool:
        """
        Send notification about code execution

        Args:
            execution_result: Execution result
            context: Additional context information

        Returns:
            Success status
        """
        # Determine notification level
        if execution_result.is_success():
            level = NotificationLevel.SUCCESS
            title = "Code Execution Successful"
        else:
            level = NotificationLevel.ERROR
            title = "Code Execution Failed"

        # Build message
        message_parts = [
            f"Sandbox: {execution_result.sandbox_id}",
            f"Language: {execution_result.language.value}",
            f"Status: {execution_result.status.value}",
            f"Exit Code: {execution_result.exit_code}",
            f"Execution Time: {execution_result.execution_time:.2f}s"
        ]

        if context:
            message_parts.insert(0, context)

        message = "\n".join(message_parts)

        # Add output/error to metadata
        metadata = {
            "sandbox_id": execution_result.sandbox_id,
            "exit_code": execution_result.exit_code,
            "execution_time": execution_result.execution_time,
            "stdout": execution_result.stdout[:500],  # Limit size
            "stderr": execution_result.stderr[:500]
        }

        return self.send_notification(title, message, level, metadata)

    def send_deployment_notification(self,
                                    deployment_result: Dict,
                                    context: str = "") -> bool:
        """
        Send notification about deployment

        Args:
            deployment_result: Deployment result dictionary
            context: Additional context

        Returns:
            Success status
        """
        status = deployment_result.get('status', 'unknown')

        if status == 'success':
            level = NotificationLevel.SUCCESS
            title = "Deployment Successful"
        elif status == 'failure':
            level = NotificationLevel.ERROR
            title = "Deployment Failed"
        else:
            level = NotificationLevel.WARNING
            title = f"Deployment {status.title()}"

        # Build message
        message_parts = [
            f"Repository: {deployment_result.get('repository', 'N/A')}",
            f"Branch: {deployment_result.get('branch', 'N/A')}",
            f"Commit: {deployment_result.get('commit_sha', 'N/A')[:7]}",
            f"Status: {status}"
        ]

        if context:
            message_parts.insert(0, context)

        # Add logs
        logs = deployment_result.get('logs', [])
        if logs:
            message_parts.append("\nLogs:")
            message_parts.extend([f"  {log}" for log in logs[-5:]])  # Last 5 logs

        message = "\n".join(message_parts)

        return self.send_notification(title, message, level, deployment_result)

    def send_webhook_event_notification(self,
                                       event: WebhookEvent,
                                       context: str = "") -> bool:
        """
        Send notification about webhook event

        Args:
            event: Webhook event
            context: Additional context

        Returns:
            Success status
        """
        title = f"Webhook Event: {event.event_type.value}"

        message_parts = [
            f"Event ID: {event.event_id}",
            f"Sandbox: {event.sandbox_id}",
            f"Type: {event.event_type.value}",
            f"Timestamp: {event.timestamp.isoformat()}"
        ]

        if context:
            message_parts.insert(0, context)

        message = "\n".join(message_parts)

        return self.send_notification(
            title,
            message,
            NotificationLevel.INFO,
            event.to_dict()
        )

    def trigger_zap(self,
                   event_name: str,
                   data: Dict[str, Any]) -> bool:
        """
        Trigger Zapier zap with custom event

        Args:
            event_name: Name of the event/trigger
            data: Event data

        Returns:
            Success status
        """
        payload = {
            "event": event_name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Triggered zap: {event_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to trigger zap: {e}")
            return False

    def close(self):
        """Close session"""
        self.session.close()
        logger.info("Zapier client closed")


class MultiChannelNotifier:
    """
    Multi-channel notification system
    Supports email, Slack, Discord, Teams, etc. via Zapier
    """

    def __init__(self, zapier_webhooks: Dict[NotificationChannel, str]):
        """
        Initialize multi-channel notifier

        Args:
            zapier_webhooks: Dictionary mapping channels to Zapier webhook URLs
        """
        self.clients = {
            channel: ZapierClient(url)
            for channel, url in zapier_webhooks.items()
        }
        logger.info(f"Multi-channel notifier initialized with {len(self.clients)} channels")

    def send_notification(self,
                         notification: Notification) -> Dict[NotificationChannel, bool]:
        """
        Send notification to specified channels

        Args:
            notification: Notification to send

        Returns:
            Dictionary mapping channels to success status
        """
        results = {}

        for channel in notification.channels:
            client = self.clients.get(channel)
            if client:
                success = client.send_notification(
                    title=notification.title,
                    message=notification.message,
                    level=notification.level,
                    metadata=notification.metadata
                )
                results[channel] = success
            else:
                logger.warning(f"No client configured for channel: {channel.value}")
                results[channel] = False

        return results

    def broadcast_notification(self,
                              title: str,
                              message: str,
                              level: NotificationLevel = NotificationLevel.INFO,
                              metadata: Dict[str, Any] = None) -> Dict[NotificationChannel, bool]:
        """
        Broadcast notification to all configured channels

        Args:
            title: Notification title
            message: Notification message
            level: Notification level
            metadata: Additional metadata

        Returns:
            Dictionary mapping channels to success status
        """
        notification = Notification(
            notification_id=f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now(),
            channels=list(self.clients.keys()),
            metadata=metadata or {}
        )

        return self.send_notification(notification)

    def close_all(self):
        """Close all clients"""
        for client in self.clients.values():
            client.close()
        logger.info("All notification clients closed")


class NotificationRules:
    """
    Rule-based notification system
    Automatically triggers notifications based on conditions
    """

    def __init__(self, notifier: MultiChannelNotifier):
        """
        Initialize notification rules

        Args:
            notifier: Multi-channel notifier instance
        """
        self.notifier = notifier
        self.rules = []
        logger.info("Notification rules initialized")

    def add_rule(self,
                name: str,
                condition: callable,
                channels: List[NotificationChannel],
                level: NotificationLevel = NotificationLevel.INFO):
        """
        Add notification rule

        Args:
            name: Rule name
            condition: Callable that returns True if notification should be sent
            channels: Channels to notify
            level: Notification level
        """
        rule = {
            "name": name,
            "condition": condition,
            "channels": channels,
            "level": level
        }
        self.rules.append(rule)
        logger.info(f"Added notification rule: {name}")

    def evaluate_execution(self, execution_result: ExecutionResult):
        """
        Evaluate execution result against rules

        Args:
            execution_result: Execution result to evaluate
        """
        for rule in self.rules:
            try:
                if rule["condition"](execution_result):
                    notification = Notification(
                        notification_id=f"rule_{rule['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        level=rule["level"],
                        title=f"Rule Triggered: {rule['name']}",
                        message=f"Execution in sandbox {execution_result.sandbox_id}",
                        timestamp=datetime.now(),
                        channels=rule["channels"],
                        metadata=execution_result.to_dict()
                    )

                    self.notifier.send_notification(notification)
                    logger.info(f"Triggered rule: {rule['name']}")

            except Exception as e:
                logger.error(f"Error evaluating rule {rule['name']}: {e}")


def setup_default_rules(notifier: MultiChannelNotifier) -> NotificationRules:
    """
    Setup default notification rules

    Args:
        notifier: Multi-channel notifier

    Returns:
        NotificationRules instance with default rules
    """
    rules = NotificationRules(notifier)

    # Rule: Notify on execution failure
    rules.add_rule(
        name="execution_failure",
        condition=lambda r: not r.is_success(),
        channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
        level=NotificationLevel.ERROR
    )

    # Rule: Notify on long execution time
    rules.add_rule(
        name="long_execution",
        condition=lambda r: r.execution_time > 60,
        channels=[NotificationChannel.SLACK],
        level=NotificationLevel.WARNING
    )

    # Rule: Notify on timeout
    rules.add_rule(
        name="execution_timeout",
        condition=lambda r: r.status.value == "timeout",
        channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
        level=NotificationLevel.CRITICAL
    )

    return rules


def main():
    """Example usage"""
    # Setup Zapier webhook URLs (replace with your actual Zapier webhook URLs)
    zapier_webhooks = {
        NotificationChannel.EMAIL: os.getenv("ZAPIER_EMAIL_WEBHOOK", "https://hooks.zapier.com/hooks/catch/your-email-hook"),
        NotificationChannel.SLACK: os.getenv("ZAPIER_SLACK_WEBHOOK", "https://hooks.zapier.com/hooks/catch/your-slack-hook"),
    }

    # Initialize notifier
    notifier = MultiChannelNotifier(zapier_webhooks)

    # Setup default rules
    rules = setup_default_rules(notifier)

    # Example: Send test notification
    notifier.broadcast_notification(
        title="E2B Integration Test",
        message="Testing Zapier integration for E2B sandbox notifications",
        level=NotificationLevel.INFO,
        metadata={"test": True}
    )

    # Cleanup
    notifier.close_all()


if __name__ == "__main__":
    main()
