"""
E2B Webhook Handler
Handles incoming webhook events from E2B sandbox executions
"""

import os
import json
import hmac
import hashlib
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from flask import Flask, request, jsonify
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from queue import Queue


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookEventType(Enum):
    """Types of webhook events"""
    SANDBOX_CREATED = "sandbox.created"
    SANDBOX_STARTED = "sandbox.started"
    SANDBOX_STOPPED = "sandbox.stopped"
    SANDBOX_DELETED = "sandbox.deleted"
    EXECUTION_STARTED = "execution.started"
    EXECUTION_COMPLETED = "execution.completed"
    EXECUTION_FAILED = "execution.failed"
    FILE_UPLOADED = "file.uploaded"
    FILE_DOWNLOADED = "file.downloaded"


@dataclass
class WebhookEvent:
    """Webhook event data structure"""
    event_id: str
    event_type: WebhookEventType
    sandbox_id: str
    timestamp: datetime
    data: Dict[str, Any]
    webhook_id: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


class WebhookEventHandler:
    """
    Event handler for webhook events
    Allows registration of custom handlers for different event types
    """

    def __init__(self):
        """Initialize event handler"""
        self.handlers: Dict[WebhookEventType, List[Callable]] = {}
        self.event_queue = Queue()
        self.processing_thread = None
        self.running = False

        logger.info("Webhook event handler initialized")

    def register_handler(self,
                        event_type: WebhookEventType,
                        handler: Callable[[WebhookEvent], None]):
        """
        Register handler for specific event type

        Args:
            event_type: Type of event to handle
            handler: Callback function to handle event
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type.value}")

    def remove_handler(self,
                      event_type: WebhookEventType,
                      handler: Callable):
        """
        Remove handler for specific event type

        Args:
            event_type: Type of event
            handler: Handler to remove
        """
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
                logger.info(f"Removed handler for {event_type.value}")
            except ValueError:
                logger.warning(f"Handler not found for {event_type.value}")

    def handle_event(self, event: WebhookEvent):
        """
        Handle incoming webhook event

        Args:
            event: Webhook event to handle
        """
        logger.info(f"Handling event: {event.event_type.value} for sandbox {event.sandbox_id}")

        # Add to queue for async processing
        self.event_queue.put(event)

        # Execute registered handlers
        handlers = self.handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.event_type.value}: {e}")

    def start_processing(self):
        """Start background event processing"""
        if self.running:
            logger.warning("Event processing already running")
            return

        self.running = True
        self.processing_thread = threading.Thread(target=self._process_events)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        logger.info("Started background event processing")

    def stop_processing(self):
        """Stop background event processing"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("Stopped background event processing")

    def _process_events(self):
        """Process events from queue"""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                logger.debug(f"Processing queued event: {event.event_id}")
                # Events are already processed in handle_event
                self.event_queue.task_done()
            except:
                continue

    def get_stats(self) -> Dict:
        """
        Get handler statistics

        Returns:
            Statistics dictionary
        """
        return {
            "total_handlers": sum(len(handlers) for handlers in self.handlers.values()),
            "event_types": [et.value for et in self.handlers.keys()],
            "queue_size": self.event_queue.qsize(),
            "processing": self.running
        }


class WebhookServer:
    """
    Flask-based webhook server for receiving E2B events
    """

    def __init__(self,
                 webhook_id: str,
                 secret_key: Optional[str] = None,
                 port: int = 5000):
        """
        Initialize webhook server

        Args:
            webhook_id: E2B webhook ID
            secret_key: Secret key for signature verification
            port: Server port
        """
        self.webhook_id = webhook_id
        self.secret_key = secret_key
        self.port = port
        self.app = Flask(__name__)
        self.event_handler = WebhookEventHandler()

        # Setup routes
        self._setup_routes()

        logger.info(f"Webhook server initialized on port {port}")

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/webhook', methods=['POST'])
        def webhook_endpoint():
            """Handle incoming webhook POST requests"""
            try:
                # Get request data
                payload = request.get_data()
                headers = dict(request.headers)

                # Verify signature if secret key is set
                if self.secret_key:
                    signature = headers.get('X-E2B-Signature')
                    if not self._verify_signature(payload, signature):
                        logger.warning("Invalid webhook signature")
                        return jsonify({"error": "Invalid signature"}), 401

                # Parse event data
                data = json.loads(payload)
                event = self._parse_event(data)

                if event:
                    # Handle event
                    self.event_handler.handle_event(event)

                    return jsonify({
                        "status": "success",
                        "event_id": event.event_id,
                        "message": "Event received and processed"
                    }), 200
                else:
                    return jsonify({"error": "Invalid event data"}), 400

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON payload: {e}")
                return jsonify({"error": "Invalid JSON"}), 400

            except Exception as e:
                logger.error(f"Webhook processing error: {e}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "webhook_id": self.webhook_id,
                "timestamp": datetime.now().isoformat()
            }), 200

        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """Get webhook statistics"""
            return jsonify(self.event_handler.get_stats()), 200

    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature

        Args:
            payload: Request payload
            signature: Signature from headers

        Returns:
            True if signature is valid
        """
        if not signature or not self.secret_key:
            return False

        expected = hmac.new(
            self.secret_key.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    def _parse_event(self, data: Dict) -> Optional[WebhookEvent]:
        """
        Parse event data into WebhookEvent object

        Args:
            data: Raw event data

        Returns:
            WebhookEvent or None if invalid
        """
        try:
            event_type_str = data.get('type') or data.get('event')
            if not event_type_str:
                logger.error("Missing event type in webhook data")
                return None

            # Map event type string to enum
            try:
                event_type = WebhookEventType(event_type_str)
            except ValueError:
                logger.warning(f"Unknown event type: {event_type_str}")
                # Create a generic event type for unknown events
                event_type = WebhookEventType.EXECUTION_COMPLETED

            event = WebhookEvent(
                event_id=data.get('id', data.get('event_id', '')),
                event_type=event_type,
                sandbox_id=data.get('sandbox_id', data.get('sandboxId', '')),
                timestamp=datetime.fromisoformat(
                    data.get('timestamp', datetime.now().isoformat())
                ),
                data=data.get('data', data),
                webhook_id=self.webhook_id
            )

            return event

        except Exception as e:
            logger.error(f"Failed to parse event: {e}")
            return None

    def register_handler(self,
                        event_type: WebhookEventType,
                        handler: Callable[[WebhookEvent], None]):
        """
        Register event handler

        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        self.event_handler.register_handler(event_type, handler)

    def run(self, host: str = '0.0.0.0', debug: bool = False):
        """
        Run webhook server

        Args:
            host: Host to bind to
            debug: Enable debug mode
        """
        logger.info(f"Starting webhook server on {host}:{self.port}")
        self.event_handler.start_processing()

        try:
            self.app.run(host=host, port=self.port, debug=debug)
        finally:
            self.event_handler.stop_processing()


# Example event handlers

def execution_completed_handler(event: WebhookEvent):
    """Handle execution completed events"""
    logger.info(f"Execution completed for sandbox: {event.sandbox_id}")
    logger.info(f"Event data: {json.dumps(event.data, indent=2)}")

    # Extract execution results
    stdout = event.data.get('stdout', '')
    stderr = event.data.get('stderr', '')
    exit_code = event.data.get('exitCode', -1)

    if exit_code == 0:
        logger.info(f"Execution successful\nOutput: {stdout}")
    else:
        logger.error(f"Execution failed (exit code: {exit_code})\nError: {stderr}")


def execution_failed_handler(event: WebhookEvent):
    """Handle execution failed events"""
    logger.error(f"Execution failed for sandbox: {event.sandbox_id}")
    logger.error(f"Error details: {json.dumps(event.data, indent=2)}")

    # Could trigger alerts, notifications, etc.


def sandbox_created_handler(event: WebhookEvent):
    """Handle sandbox created events"""
    logger.info(f"New sandbox created: {event.sandbox_id}")
    logger.info(f"Sandbox details: {json.dumps(event.data, indent=2)}")


def main():
    """Example usage"""
    # Get configuration from environment
    webhook_id = os.getenv("E2B_WEBHOOK_ID", "YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp")
    secret_key = os.getenv("E2B_WEBHOOK_SECRET")
    port = int(os.getenv("WEBHOOK_PORT", "5000"))

    # Create webhook server
    server = WebhookServer(
        webhook_id=webhook_id,
        secret_key=secret_key,
        port=port
    )

    # Register event handlers
    server.register_handler(
        WebhookEventType.EXECUTION_COMPLETED,
        execution_completed_handler
    )
    server.register_handler(
        WebhookEventType.EXECUTION_FAILED,
        execution_failed_handler
    )
    server.register_handler(
        WebhookEventType.SANDBOX_CREATED,
        sandbox_created_handler
    )

    # Run server
    logger.info("Starting E2B webhook server...")
    server.run(host='0.0.0.0', debug=False)


if __name__ == "__main__":
    main()
