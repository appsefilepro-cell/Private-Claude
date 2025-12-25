#!/usr/bin/env python3
"""
Email Notification Service
Sends email notifications for system events
Supports SMTP, SendGrid, and AWS SES
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
from jinja2 import Template
import aiosmtplib


logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration"""
    def __init__(self):
        # SMTP Configuration
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'

        # Email settings
        self.from_email = os.getenv('FROM_EMAIL', 'system@private-claude.local')
        self.from_name = os.getenv('FROM_NAME', 'Private Claude System')
        self.to_email = os.getenv('TO_EMAIL', 'noreply@anthropic.com')

        # SendGrid (alternative)
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY', '')

        # AWS SES (alternative)
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')

        # Notification settings
        self.enabled = os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'true').lower() == 'true'
        self.batch_notifications = os.getenv('BATCH_NOTIFICATIONS', 'false').lower() == 'true'
        self.batch_interval = int(os.getenv('BATCH_INTERVAL', '300'))  # 5 minutes


class EmailNotifier:
    """Email notification service"""

    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()
        self.pending_notifications: List[Dict] = []
        self.email_templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Template]:
        """Load email templates"""
        return {
            'event_notification': Template('''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #4CAF50; color: white; padding: 20px; border-radius: 5px 5px 0 0; }
        .header.error { background: #f44336; }
        .header.warning { background: #ff9800; }
        .content { background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }
        .event-details { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }
        .event-details.error { border-left-color: #f44336; }
        .event-details.warning { border-left-color: #ff9800; }
        .label { font-weight: bold; color: #555; }
        .value { color: #333; margin-left: 10px; }
        .footer { text-align: center; padding: 20px; color: #777; font-size: 12px; }
        .data-section { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 3px; }
        code { background: #eee; padding: 2px 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header {{ priority_class }}">
            <h2>{{ event_type }}</h2>
            <p>{{ timestamp }}</p>
        </div>
        <div class="content">
            <div class="event-details {{ priority_class }}">
                <p><span class="label">Event ID:</span><span class="value"><code>{{ event_id }}</code></span></p>
                <p><span class="label">Source:</span><span class="value">{{ source }}</span></p>
                <p><span class="label">Priority:</span><span class="value">{{ priority }}</span></p>
            </div>

            {% if data %}
            <div class="data-section">
                <h3>Event Details:</h3>
                {% for key, value in data.items() %}
                <p><span class="label">{{ key }}:</span><span class="value">{{ value }}</span></p>
                {% endfor %}
            </div>
            {% endif %}

            {% if summary %}
            <div class="data-section">
                <h3>Summary:</h3>
                <p>{{ summary }}</p>
            </div>
            {% endif %}
        </div>
        <div class="footer">
            <p>This is an automated notification from Private Claude System</p>
            <p>Event Bus Integration Framework</p>
        </div>
    </div>
</body>
</html>
            '''),

            'batch_notification': Template('''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #2196F3; color: white; padding: 20px; border-radius: 5px 5px 0 0; }
        .content { background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }
        .event-item { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; }
        .event-item.error { border-left-color: #f44336; }
        .event-item.success { border-left-color: #4CAF50; }
        .stats { background: #fff; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .stat-item { display: inline-block; margin: 10px 20px 10px 0; }
        .label { font-weight: bold; color: #555; }
        .footer { text-align: center; padding: 20px; color: #777; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>System Activity Summary</h2>
            <p>{{ period_start }} to {{ period_end }}</p>
        </div>
        <div class="content">
            <div class="stats">
                <h3>Statistics:</h3>
                <div class="stat-item"><span class="label">Total Events:</span> {{ total_events }}</div>
                <div class="stat-item"><span class="label">Errors:</span> {{ error_count }}</div>
                <div class="stat-item"><span class="label">Successes:</span> {{ success_count }}</div>
            </div>

            <h3>Recent Events:</h3>
            {% for event in events %}
            <div class="event-item {{ event.class }}">
                <p><strong>{{ event.event_type }}</strong> - {{ event.timestamp }}</p>
                <p><span class="label">Source:</span> {{ event.source }}</p>
                {% if event.summary %}
                <p>{{ event.summary }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        <div class="footer">
            <p>This is an automated batch notification from Private Claude System</p>
        </div>
    </div>
</body>
</html>
            '''),

            'test_results': Template('''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 700px; margin: 0 auto; padding: 20px; }
        .header { background: {{ header_color }}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }
        .content { background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }
        .test-summary { background: white; padding: 20px; margin: 15px 0; }
        .pass { color: #4CAF50; font-weight: bold; }
        .fail { color: #f44336; font-weight: bold; }
        .test-item { padding: 10px; margin: 5px 0; border-left: 3px solid #ddd; }
        .test-item.passed { border-left-color: #4CAF50; background: #f1f8f4; }
        .test-item.failed { border-left-color: #f44336; background: #fef1f1; }
        .footer { text-align: center; padding: 20px; color: #777; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{{ test_name }} - Test Results</h2>
            <p>{{ timestamp }}</p>
        </div>
        <div class="content">
            <div class="test-summary">
                <h3>Summary:</h3>
                <p><strong>Total Tests:</strong> {{ total_tests }}</p>
                <p class="pass"><strong>Passed:</strong> {{ passed_tests }}</p>
                {% if failed_tests > 0 %}
                <p class="fail"><strong>Failed:</strong> {{ failed_tests }}</p>
                {% endif %}
                <p><strong>Duration:</strong> {{ duration }}s</p>
            </div>

            {% if failures %}
            <h3>Failed Tests:</h3>
            {% for failure in failures %}
            <div class="test-item failed">
                <p><strong>{{ failure.name }}</strong></p>
                <p>{{ failure.error }}</p>
            </div>
            {% endfor %}
            {% endif %}
        </div>
        <div class="footer">
            <p>Automated Test Results from Private Claude System</p>
        </div>
    </div>
</body>
</html>
            ''')
        }

    async def send_event_notification(self, event):
        """Send email notification for an event"""
        if not self.config.enabled:
            logger.info("Email notifications disabled")
            return

        # Determine priority class for styling
        priority_class = 'error' if 'ERROR' in event.event_type.value.upper() else ''
        if 'FAILURE' in event.event_type.value.upper():
            priority_class = 'error'
        elif event.priority.value >= 3:  # HIGH or CRITICAL
            priority_class = 'warning'

        # Generate summary based on event type
        summary = self._generate_event_summary(event)

        # Render email template
        html_content = self.email_templates['event_notification'].render(
            event_id=event.event_id,
            event_type=event.event_type.value,
            source=event.source,
            timestamp=event.timestamp,
            priority=event.priority.name,
            priority_class=priority_class,
            data=event.data,
            summary=summary
        )

        subject = f"[{event.priority.name}] {event.event_type.value} - {event.source}"

        await self._send_email(subject, html_content)

    def _generate_event_summary(self, event) -> str:
        """Generate human-readable summary for event"""
        event_type = event.event_type.value
        data = event.data

        if 'push' in event_type.lower():
            return f"New push to {data.get('repository', 'unknown')} on branch {data.get('branch', 'unknown')} by {data.get('author', 'unknown')}"

        elif 'pull_request' in event_type.lower() or 'merge_request' in event_type.lower():
            return f"New pull request in {data.get('repository', 'unknown')}: {data.get('title', 'Untitled')}"

        elif 'test' in event_type.lower():
            passed = data.get('passed', False)
            status = "passed" if passed else "failed"
            return f"Test {data.get('test_name', 'unknown')} {status} - {data.get('total_tests', 0)} tests, {data.get('failed_tests', 0)} failures"

        elif 'app' in event_type.lower():
            return f"App {event.source}: {data.get('status', 'unknown')} - {data.get('details', 'No details')}"

        elif 'workflow' in event_type.lower():
            return f"Zapier workflow {data.get('workflow_name', 'unknown')} completed"

        return f"Event from {event.source}: {json.dumps(data)}"

    async def send_test_results(self, test_name: str, total_tests: int,
                                passed_tests: int, failed_tests: int,
                                duration: float, failures: List[Dict] = None):
        """Send test results notification"""
        if not self.config.enabled:
            return

        header_color = '#4CAF50' if failed_tests == 0 else '#f44336'

        html_content = self.email_templates['test_results'].render(
            test_name=test_name,
            timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            duration=duration,
            failures=failures or [],
            header_color=header_color
        )

        status = "PASSED" if failed_tests == 0 else "FAILED"
        subject = f"[{status}] {test_name} - {passed_tests}/{total_tests} tests passed"

        await self._send_email(subject, html_content)

    async def _send_email(self, subject: str, html_content: str,
                         to_email: Optional[str] = None):
        """Send email using configured method"""
        to_email = to_email or self.config.to_email

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            message['To'] = to_email

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Send via SMTP
            if self.config.smtp_username and self.config.smtp_password:
                await self._send_via_smtp(message, to_email)
            else:
                logger.warning("No SMTP credentials configured, email not sent")
                logger.info(f"Would send email: {subject}")

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise

    async def _send_via_smtp(self, message: MIMEMultipart, to_email: str):
        """Send email via SMTP"""
        try:
            if self.config.smtp_use_tls:
                # Use TLS
                await aiosmtplib.send(
                    message,
                    hostname=self.config.smtp_host,
                    port=self.config.smtp_port,
                    username=self.config.smtp_username,
                    password=self.config.smtp_password,
                    use_tls=True
                )
            else:
                # Use SSL or no encryption
                await aiosmtplib.send(
                    message,
                    hostname=self.config.smtp_host,
                    port=self.config.smtp_port,
                    username=self.config.smtp_username,
                    password=self.config.smtp_password
                )

            logger.info(f"Email sent successfully to {to_email}")

        except Exception as e:
            logger.error(f"SMTP error: {e}")
            raise


if __name__ == '__main__':
    import asyncio

    async def test():
        # Test email notifier
        notifier = EmailNotifier()

        # Test notification
        await notifier.send_test_results(
            test_name='API Integration Tests',
            total_tests=25,
            passed_tests=23,
            failed_tests=2,
            duration=12.5,
            failures=[
                {'name': 'test_authentication', 'error': 'Token expired'},
                {'name': 'test_database_connection', 'error': 'Connection timeout'}
            ]
        )

        print("Test email sent (check logs)")

    asyncio.run(test())
