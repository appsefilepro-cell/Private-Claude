"""
Secure Email Automation System
FIX: Insufficient Input Validation in Email Automation System
"""

import re
import asyncio
from typing import List, Dict, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

import aiosmtplib
import bleach
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, validator

from config import get_settings
from logging_system import logging_system, AuditEventType
from rate_limiter import email_rate_limiter


class EmailRecipient(BaseModel):
    """Email recipient with validation"""
    email: str
    name: Optional[str] = None

    @validator("email")
    def validate_email_address(cls, v):
        """Validate email address format"""
        try:
            # Normalize and validate email
            validated = validate_email(v, check_deliverability=False)
            return validated.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {e}")


class EmailTemplate(BaseModel):
    """Email template with validation"""
    name: str
    subject: str
    body_text: str
    body_html: Optional[str] = None
    variables: List[str] = []

    @validator("subject")
    def validate_subject(cls, v):
        """Validate and sanitize subject"""
        # Remove potentially dangerous characters
        v = bleach.clean(v, tags=[], strip=True)

        # Limit length
        if len(v) > 200:
            raise ValueError("Subject line too long (max 200 characters)")

        return v

    @validator("body_text")
    def validate_body_text(cls, v):
        """Validate and sanitize plain text body"""
        # Limit length
        if len(v) > 100000:  # ~100KB
            raise ValueError("Email body too long")

        return v

    @validator("body_html")
    def validate_body_html(cls, v):
        """Validate and sanitize HTML body"""
        if v is None:
            return v

        # Sanitize HTML to prevent XSS
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'a', 'img', 'table', 'tr', 'td', 'th', 'thead',
            'tbody', 'div', 'span',
        ]

        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height'],
            'div': ['class'],
            'span': ['class'],
        }

        v = bleach.clean(
            v,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True,
        )

        # Limit length
        if len(v) > 200000:  # ~200KB
            raise ValueError("HTML email body too long")

        return v

    def render(self, variables: Dict[str, str]) -> tuple:
        """
        Render template with variables

        Returns (subject, body_text, body_html)
        """
        # Validate all required variables are provided
        for var in self.variables:
            if var not in variables:
                raise ValueError(f"Missing required variable: {var}")

        # Sanitize all variable values
        sanitized_vars = {}
        for key, value in variables.items():
            # Remove potentially dangerous content
            sanitized_vars[key] = bleach.clean(str(value), tags=[], strip=True)

        # Render subject
        subject = self.subject
        for key, value in sanitized_vars.items():
            subject = subject.replace(f"{{{{{key}}}}}", value)

        # Render text body
        body_text = self.body_text
        for key, value in sanitized_vars.items():
            body_text = body_text.replace(f"{{{{{key}}}}}", value)

        # Render HTML body
        body_html = None
        if self.body_html:
            body_html = self.body_html
            for key, value in sanitized_vars.items():
                # HTML escape variables in HTML templates
                escaped_value = bleach.clean(value, tags=[], strip=True)
                body_html = body_html.replace(f"{{{{{key}}}}}", escaped_value)

        return subject, body_text, body_html


class SecureEmailAutomation:
    """
    Secure email automation system with input validation and rate limiting

    Security Features:
    - Email address validation
    - HTML sanitization to prevent XSS
    - Subject and body length limits
    - Rate limiting to prevent spam
    - Audit logging
    - Template variable sanitization
    """

    def __init__(self):
        self.settings = get_settings()
        self._templates: Dict[str, EmailTemplate] = {}

    def register_template(self, template: EmailTemplate):
        """Register an email template"""
        self._templates[template.name] = template

        logging_system.info(
            f"Email template registered: {template.name}",
            template_name=template.name,
        )

    def get_template(self, name: str) -> EmailTemplate:
        """Get email template by name"""
        if name not in self._templates:
            raise ValueError(f"Template not found: {name}")

        return self._templates[name]

    async def send_email(
        self,
        sender: str,
        recipients: List[EmailRecipient],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        user: Optional[str] = None,
    ) -> bool:
        """
        Send email with validation and rate limiting

        Args:
            sender: Sender email address
            recipients: List of recipients
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
            user: Username for audit logging

        Returns:
            True if sent successfully
        """

        # Validate sender
        try:
            sender_validated = validate_email(sender, check_deliverability=False)
            sender = sender_validated.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid sender email: {e}")

        # Check rate limit
        if not email_rate_limiter.can_send_email(sender):
            raise Exception(
                f"Rate limit exceeded for sender: {sender}. "
                f"Maximum {self.settings.email_rate_limit_per_hour} emails per hour."
            )

        # Validate recipients
        if not recipients:
            raise ValueError("At least one recipient required")

        if len(recipients) > 50:
            raise ValueError("Too many recipients (max 50 per email)")

        # Sanitize subject
        subject = bleach.clean(subject, tags=[], strip=True)
        if len(subject) > 200:
            raise ValueError("Subject too long (max 200 characters)")

        # Sanitize bodies
        if len(body_text) > 100000:
            raise ValueError("Email body too long")

        if body_html and len(body_html) > 200000:
            raise ValueError("HTML email body too long")

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = sender
            message["To"] = ", ".join([r.email for r in recipients])
            message["Subject"] = subject

            # Add text part
            text_part = MIMEText(body_text, "plain", "utf-8")
            message.attach(text_part)

            # Add HTML part if provided
            if body_html:
                # Sanitize HTML
                body_html = bleach.clean(
                    body_html,
                    tags=[
                        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3',
                        'ul', 'ol', 'li', 'a', 'img', 'table', 'tr', 'td',
                        'th', 'div', 'span',
                    ],
                    attributes={
                        'a': ['href', 'title'],
                        'img': ['src', 'alt', 'width', 'height'],
                    },
                    strip=True,
                )

                html_part = MIMEText(body_html, "html", "utf-8")
                message.attach(html_part)

            # Send email
            await self._send_smtp(message)

            # Audit log success
            for recipient in recipients:
                logging_system.audit_email_event(
                    user=user or sender,
                    recipient=recipient.email,
                    subject=subject,
                    success=True,
                    error=None,
                )

            logging_system.info(
                "Email sent successfully",
                sender=sender,
                recipient_count=len(recipients),
                subject=subject,
            )

            return True

        except Exception as e:
            # Audit log failure
            for recipient in recipients:
                logging_system.audit_email_event(
                    user=user or sender,
                    recipient=recipient.email,
                    subject=subject,
                    success=False,
                    error=str(e),
                )

            logging_system.error(
                f"Failed to send email: {e}",
                sender=sender,
                error=str(e),
            )

            raise

    async def send_templated_email(
        self,
        sender: str,
        recipients: List[EmailRecipient],
        template_name: str,
        variables: Dict[str, str],
        user: Optional[str] = None,
    ) -> bool:
        """
        Send email using a template

        Args:
            sender: Sender email address
            recipients: List of recipients
            template_name: Name of registered template
            variables: Template variables
            user: Username for audit logging

        Returns:
            True if sent successfully
        """

        # Get and render template
        template = self.get_template(template_name)
        subject, body_text, body_html = template.render(variables)

        # Send email
        return await self.send_email(
            sender=sender,
            recipients=recipients,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            user=user,
        )

    async def _send_smtp(self, message: MIMEMultipart):
        """Send email via SMTP"""
        try:
            # Connect to SMTP server
            if self.settings.smtp_use_tls:
                await aiosmtplib.send(
                    message,
                    hostname=self.settings.smtp_host,
                    port=self.settings.smtp_port,
                    username=self.settings.smtp_username,
                    password=self.settings.smtp_password,
                    start_tls=True,
                )
            else:
                await aiosmtplib.send(
                    message,
                    hostname=self.settings.smtp_host,
                    port=self.settings.smtp_port,
                    username=self.settings.smtp_username,
                    password=self.settings.smtp_password,
                )

        except Exception as e:
            raise Exception(f"SMTP error: {e}")


# Global email automation instance
email_automation = SecureEmailAutomation()


# Example templates for legal automation
def register_default_templates():
    """Register default email templates"""

    # Legal document ready notification
    legal_doc_template = EmailTemplate(
        name="legal_document_ready",
        subject="Legal Document Ready: {{document_name}}",
        body_text="""
Dear {{recipient_name}},

Your legal document "{{document_name}}" is ready for review.

Document ID: {{document_id}}
Created: {{created_date}}

Please log in to the system to review and download the document.

Best regards,
Business Automation System
        """,
        body_html="""
<html>
<body>
    <p>Dear {{recipient_name}},</p>

    <p>Your legal document "<strong>{{document_name}}</strong>" is ready for review.</p>

    <ul>
        <li>Document ID: {{document_id}}</li>
        <li>Created: {{created_date}}</li>
    </ul>

    <p>Please log in to the system to review and download the document.</p>

    <p>Best regards,<br>Business Automation System</p>
</body>
</html>
        """,
        variables=["recipient_name", "document_name", "document_id", "created_date"],
    )

    email_automation.register_template(legal_doc_template)

    # Trade execution notification
    trade_notification = EmailTemplate(
        name="trade_notification",
        subject="Trade Executed: {{action}} {{symbol}}",
        body_text="""
Trade Execution Notification

Action: {{action}}
Symbol: {{symbol}}
Quantity: {{quantity}}
Price: {{price}}
Total Value: {{total_value}}
Time: {{timestamp}}

This is an automated notification from your trading bot.
        """,
        variables=["action", "symbol", "quantity", "price", "total_value", "timestamp"],
    )

    email_automation.register_template(trade_notification)
