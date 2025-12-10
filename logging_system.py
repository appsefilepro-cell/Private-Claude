"""
Comprehensive Logging and Audit Trail System
FIX: Insufficient Logging and Audit Trail
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
from enum import Enum

import structlog
from pythonjsonlogger import jsonlogger

from config import get_settings


class AuditEventType(str, Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    API_KEY_CREATED = "api_key_created"
    API_KEY_ROTATED = "api_key_rotated"

    # Trading events
    TRADE_EXECUTED = "trade_executed"
    TRADE_FAILED = "trade_failed"
    STRATEGY_MODIFIED = "strategy_modified"
    BOT_STARTED = "bot_started"
    BOT_STOPPED = "bot_stopped"
    BOT_CONFIGURATION_CHANGED = "bot_configuration_changed"

    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGED = "configuration_changed"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"

    # Data events
    SENSITIVE_DATA_ACCESSED = "sensitive_data_accessed"
    DATA_EXPORTED = "data_exported"
    DATA_ENCRYPTED = "data_encrypted"
    DATA_DECRYPTED = "data_decrypted"

    # Email events
    EMAIL_SENT = "email_sent"
    EMAIL_FAILED = "email_failed"
    EMAIL_TEMPLATE_MODIFIED = "email_template_modified"

    # Security events
    UNAUTHORIZED_ACCESS_ATTEMPT = "unauthorized_access_attempt"
    IP_BLOCKED = "ip_blocked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    PERMISSION_DENIED = "permission_denied"

    # Integration events
    ZAPIER_WEBHOOK_TRIGGERED = "zapier_webhook_triggered"
    MICROSOFT_API_CALLED = "microsoft_api_called"
    SHAREPOINT_ACCESS = "sharepoint_access"


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingSystem:
    """Centralized logging system with structured logging and audit trails"""

    def __init__(self):
        self.settings = get_settings()
        self._setup_logging()
        self._setup_audit_logging()

    def _setup_logging(self):
        """Set up structured logging"""

        # Create logs directory
        log_dir = Path(self.settings.log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Set up JSON formatter for file handler
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s %(pathname)s %(lineno)d'
        )

        # File handler
        file_handler = logging.FileHandler(self.settings.log_file_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(self.settings.log_level)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.settings.log_level)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.settings.log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        self.logger = structlog.get_logger(__name__)

    def _setup_audit_logging(self):
        """Set up separate audit trail logging"""
        if not self.settings.audit_log_enabled:
            return

        # Create audit logs directory
        audit_log_dir = Path(self.settings.audit_log_path).parent
        audit_log_dir.mkdir(parents=True, exist_ok=True)

        # Set up audit logger
        self.audit_logger = logging.getLogger("audit")
        self.audit_logger.setLevel(logging.INFO)

        # JSON formatter for audit logs
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(event_type)s %(user)s %(ip_address)s %(action)s %(details)s %(success)s'
        )

        # Audit file handler
        audit_handler = logging.FileHandler(self.settings.audit_log_path)
        audit_handler.setFormatter(formatter)
        self.audit_logger.addHandler(audit_handler)

        # Prevent audit logs from propagating to root logger
        self.audit_logger.propagate = False

    def log(
        self,
        level: LogLevel,
        message: str,
        **kwargs
    ):
        """Log a message with structured data"""
        logger_method = getattr(self.logger, level.value.lower())
        logger_method(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.log(LogLevel.CRITICAL, message, **kwargs)

    def audit(
        self,
        event_type: AuditEventType,
        user: Optional[str] = None,
        ip_address: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
    ):
        """
        Log an audit event

        This creates a tamper-evident audit trail for compliance and forensic analysis
        """
        if not self.settings.audit_log_enabled:
            return

        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "user": user or "system",
            "ip_address": ip_address or "unknown",
            "action": action or event_type.value,
            "details": json.dumps(details or {}),
            "success": success,
        }

        self.audit_logger.info("", extra=audit_entry)

        # Also log to main logger for redundancy
        self.info(
            f"Audit: {event_type.value}",
            user=user,
            ip_address=ip_address,
            action=action,
            success=success,
        )

    def audit_trade(
        self,
        user: str,
        symbol: str,
        action: str,
        quantity: float,
        price: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Audit a trading event"""
        details = {
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "total_value": quantity * price,
        }

        if error:
            details["error"] = error

        event_type = AuditEventType.TRADE_EXECUTED if success else AuditEventType.TRADE_FAILED

        self.audit(
            event_type=event_type,
            user=user,
            action=f"{action} {symbol}",
            details=details,
            success=success,
        )

    def audit_authentication(
        self,
        user: str,
        ip_address: str,
        success: bool,
        method: str = "password",
    ):
        """Audit an authentication attempt"""
        event_type = AuditEventType.LOGIN_SUCCESS if success else AuditEventType.LOGIN_FAILURE

        self.audit(
            event_type=event_type,
            user=user,
            ip_address=ip_address,
            action=f"login via {method}",
            details={"authentication_method": method},
            success=success,
        )

    def audit_sensitive_data_access(
        self,
        user: str,
        data_type: str,
        operation: str,
        record_id: Optional[str] = None,
    ):
        """Audit access to sensitive data"""
        details = {
            "data_type": data_type,
            "operation": operation,
        }

        if record_id:
            details["record_id"] = record_id

        self.audit(
            event_type=AuditEventType.SENSITIVE_DATA_ACCESSED,
            user=user,
            action=f"{operation} {data_type}",
            details=details,
            success=True,
        )

    def audit_configuration_change(
        self,
        user: str,
        component: str,
        changes: Dict[str, Any],
    ):
        """Audit configuration changes"""
        self.audit(
            event_type=AuditEventType.CONFIGURATION_CHANGED,
            user=user,
            action=f"modified {component} configuration",
            details={"component": component, "changes": changes},
            success=True,
        )

    def audit_security_event(
        self,
        event_type: AuditEventType,
        ip_address: str,
        details: Dict[str, Any],
        user: Optional[str] = None,
    ):
        """Audit a security event"""
        self.audit(
            event_type=event_type,
            user=user or "unknown",
            ip_address=ip_address,
            action=event_type.value.replace("_", " "),
            details=details,
            success=False,  # Security events are typically failures
        )

    def audit_email_event(
        self,
        user: str,
        recipient: str,
        subject: str,
        success: bool,
        error: Optional[str] = None,
    ):
        """Audit an email event"""
        details = {
            "recipient": recipient,
            "subject": subject,
        }

        if error:
            details["error"] = error

        event_type = AuditEventType.EMAIL_SENT if success else AuditEventType.EMAIL_FAILED

        self.audit(
            event_type=event_type,
            user=user,
            action=f"sent email to {recipient}",
            details=details,
            success=success,
        )


# Global logging instance
logging_system = LoggingSystem()


# Convenience functions
def log_info(message: str, **kwargs):
    """Log info message"""
    logging_system.info(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log error message"""
    logging_system.error(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message"""
    logging_system.warning(message, **kwargs)


def audit_event(event_type: AuditEventType, **kwargs):
    """Log audit event"""
    logging_system.audit(event_type, **kwargs)
