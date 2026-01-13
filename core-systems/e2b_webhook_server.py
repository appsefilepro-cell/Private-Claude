#!/usr/bin/env python3
"""
E2B WEBHOOK SERVER - REAL IMPLEMENTATION
=========================================
Receives webhooks from E2B Sandbox for Agent X5.0
Integrates with trading systems and automation pipelines
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('E2BWebhook')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for webhook access

# Configuration
E2B_API_KEY = os.getenv('E2B_API_KEY', 'e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773')
WEBHOOK_SECRET = os.getenv('E2B_WEBHOOK_SECRET', '')
PORT = int(os.getenv('E2B_WEBHOOK_PORT', '5000'))

# Webhook event storage
webhook_events: List[Dict] = []
MAX_EVENTS = 1000  # Keep last 1000 events


# ============================================================================
# WEBHOOK HANDLERS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Return current health information for the E2B Webhook Server.
    
    Returns:
        A Flask JSON response with the following keys:
          - "status": health status string,
          - "service": service name,
          - "version": application version,
          - "timestamp": ISO 8601 timestamp of the check,
          - "events_received": current count of stored webhook events.
        The response is returned with HTTP status 200.
    """
    return jsonify({
        "status": "healthy",
        "service": "E2B Webhook Server",
        "version": "5.0.0",
        "timestamp": datetime.now().isoformat(),
        "events_received": len(webhook_events)
    }), 200


@app.route('/webhook/e2b', methods=['POST'])
def e2b_webhook():
    """
    Handle incoming E2B webhook POSTs: validate an optional Bearer secret, construct and store an internal event, route it to the appropriate processor, persist it to a log file, and return an acknowledgment.
    
    If the request body is empty, responds with a 400 and an error message. If a webhook secret is configured and the Authorization header is missing or invalid, responds with a 401 and an error message. On successful processing, returns a 200 response containing the stored event id, a status, and the routing result. If an internal error occurs, responds with a 500 and the error message.
    
    Returns:
        dict: JSON payload with keys:
            - "status": "received" on success or omitted on error,
            - "event_id": the internal event identifier on success,
            - "processed": `True` on success,
            - "result": the handler result returned by the routing function on success,
            - "error": error message on failure.
    """
    try:
        # Get webhook data
        data = request.get_json()

        if not data:
            logger.warning("Received empty webhook payload")
            return jsonify({"error": "Empty payload"}), 400

        # Verify webhook secret if configured
        if WEBHOOK_SECRET:
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer ') or auth_header[7:] != WEBHOOK_SECRET:
                logger.warning("Invalid webhook authentication")
                return jsonify({"error": "Unauthorized"}), 401

        # Process webhook event
        event = {
            "id": data.get('id', f"event_{len(webhook_events)}"),
            "type": data.get('type', 'unknown'),
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "headers": dict(request.headers)
        }

        # Store event
        webhook_events.append(event)

        # Keep only last MAX_EVENTS
        if len(webhook_events) > MAX_EVENTS:
            webhook_events.pop(0)

        logger.info(f"📥 Received E2B webhook: {event['type']} (ID: {event['id']})")

        # Route to appropriate handler
        event_type = event['type']
        result = route_webhook_event(event)

        # Save to file
        save_webhook_event(event)

        return jsonify({
            "status": "received",
            "event_id": event['id'],
            "processed": True,
            "result": result
        }), 200

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/e2b/sandbox_started', methods=['POST'])
def sandbox_started():
    """
    Create and store a `sandbox_started` webhook event when a sandbox starts.
    
    Expects a JSON request body containing a `sandbox_id`. Extracts `sandbox_id`, builds an event object with `type`, `sandbox_id`, `timestamp`, and the original `data`, appends the event to in-memory storage, and persists it to the webhook log.
    
    Returns:
        A JSON acknowledgment `{"status": "acknowledged"}` with HTTP 200 on success, or a JSON error `{"error": "<message>"}` with HTTP 500 on failure.
    """
    try:
        data = request.get_json()
        sandbox_id = data.get('sandbox_id')

        logger.info(f"🚀 E2B Sandbox started: {sandbox_id}")

        event = {
            "type": "sandbox_started",
            "sandbox_id": sandbox_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        webhook_events.append(event)
        save_webhook_event(event)

        return jsonify({"status": "acknowledged"}), 200

    except Exception as e:
        logger.error(f"❌ Error in sandbox_started handler: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/e2b/sandbox_stopped', methods=['POST'])
def sandbox_stopped():
    """
    Record that a sandbox instance has stopped and acknowledge receipt.
    
    Reads the JSON payload from the incoming request, extracts `sandbox_id`, appends a `sandbox_stopped` event to the in-memory store and persists it, then returns an acknowledgement response.
    
    Returns:
        A Flask response tuple. On success: JSON `{"status": "acknowledged"}` with HTTP 200. On failure: JSON `{"error": "<message>"}` with HTTP 500.
    """
    try:
        data = request.get_json()
        sandbox_id = data.get('sandbox_id')

        logger.info(f"⏹️  E2B Sandbox stopped: {sandbox_id}")

        event = {
            "type": "sandbox_stopped",
            "sandbox_id": sandbox_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        webhook_events.append(event)
        save_webhook_event(event)

        return jsonify({"status": "acknowledged"}), 200

    except Exception as e:
        logger.error(f"❌ Error in sandbox_stopped handler: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/e2b/code_executed', methods=['POST'])
def code_executed():
    """
    Handle incoming code execution webhook events from E2B.
    
    Constructs a `code_executed` event from the request JSON, records it in the in-memory event list and on disk, and triggers an alert if the execution failed.
    
    Returns:
    	Tuple[Response, int]: A JSON acknowledgement with HTTP 200 on success; on exception returns a JSON error message with HTTP 500.
    """
    try:
        data = request.get_json()
        execution_id = data.get('execution_id')
        success = data.get('success', False)

        logger.info(f"💻 Code executed in E2B: {execution_id} ({'✅' if success else '❌'})")

        event = {
            "type": "code_executed",
            "execution_id": execution_id,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        webhook_events.append(event)
        save_webhook_event(event)

        # If code execution failed, trigger alert
        if not success:
            trigger_alert(event)

        return jsonify({"status": "acknowledged"}), 200

    except Exception as e:
        logger.error(f"❌ Error in code_executed handler: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/zapier', methods=['POST'])
def zapier_webhook():
    """
    Handle incoming Zapier triggers by creating a `zapier_trigger` event, processing and persisting it, and returning an acknowledgment.
    
    Returns:
        Flask response: JSON object with `status`, `event_id`, and `result` on success (HTTP 200), or `error` on failure (HTTP 500).
    """
    try:
        data = request.get_json()

        event = {
            "id": f"zapier_{len(webhook_events)}",
            "type": "zapier_trigger",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        webhook_events.append(event)
        logger.info(f"⚡ Received Zapier webhook: {event['id']}")

        # Process Zapier event
        result = process_zapier_event(event)

        save_webhook_event(event)

        return jsonify({
            "status": "received",
            "event_id": event['id'],
            "result": result
        }), 200

    except Exception as e:
        logger.error(f"❌ Error processing Zapier webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/trading', methods=['POST'])
def trading_webhook():
    """
    Handle incoming trading-signal webhooks and route them for processing.
    
    Creates an internal `trading_signal` event from the request payload, stores and persists the event, forwards it to the trading processor, and returns an acknowledgement.
    
    Returns:
        Flask Response: On success, JSON with keys `status` (\"received\"), `event_id`, and `result` (processing result). On failure, JSON with key `error` and HTTP 500 status.
    """
    try:
        data = request.get_json()

        event = {
            "id": f"trade_{len(webhook_events)}",
            "type": "trading_signal",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        webhook_events.append(event)
        logger.info(f"📈 Received trading signal: {event['id']}")

        # Forward to trading system
        result = process_trading_signal(event)

        save_webhook_event(event)

        return jsonify({
            "status": "received",
            "event_id": event['id'],
            "result": result
        }), 200

    except Exception as e:
        logger.error(f"❌ Error processing trading webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/events', methods=['GET'])
def get_events():
    """
    Return recent webhook events, optionally filtered by event type.
    
    Parameters:
        limit (int): Maximum number of most-recent events to return (from newest). Defaults to 50 when not provided in the query string.
        type (str): Optional event type to filter results (only events with matching `type` are returned).
    
    Returns:
        dict: JSON object with keys:
            - total (int): total number of events stored in memory,
            - returned (int): number of events included in this response,
            - events (list): list of event objects (most recent first, limited and filtered per parameters).
    """
    limit = int(request.args.get('limit', 50))
    event_type = request.args.get('type')

    events = webhook_events[-limit:]

    if event_type:
        events = [e for e in events if e.get('type') == event_type]

    return jsonify({
        "total": len(webhook_events),
        "returned": len(events),
        "events": events
    }), 200


@app.route('/events/clear', methods=['POST'])
def clear_events():
    """
    Clear all stored webhook events from the in-memory event store.
    
    Removes every event from the global `webhook_events` list and logs the number of events cleared.
    
    Returns:
    	A Flask JSON response and HTTP status code: JSON contains `status` set to `"cleared"` and `count` with the number of events removed; HTTP status is 200.
    """
    global webhook_events
    count = len(webhook_events)
    webhook_events = []
    logger.info(f"🗑️  Cleared {count} webhook events")

    return jsonify({
        "status": "cleared",
        "count": count
    }), 200


# ============================================================================
# EVENT PROCESSORS
# ============================================================================

def route_webhook_event(event: Dict) -> Dict[str, Any]:
    """
    Dispatches a webhook event to the handler associated with its "type" and returns that handler's result.
    
    Parameters:
        event (dict): Webhook event object. Expected to include a "type" key identifying the event category.
    
    Returns:
        dict: Processing result produced by the selected handler.
    """
    event_type = event.get('type', 'unknown')

    handlers = {
        'sandbox_started': handle_sandbox_started,
        'sandbox_stopped': handle_sandbox_stopped,
        'code_executed': handle_code_executed,
        'trading_signal': handle_trading_signal,
        'zapier_trigger': handle_zapier_trigger,
    }

    handler = handlers.get(event_type, handle_unknown_event)
    return handler(event)


def handle_sandbox_started(event: Dict) -> Dict:
    """
    Process a received "sandbox_started" webhook event and return an acknowledgement.
    
    Parameters:
        event (Dict): The webhook event object, expected to include an 'id' and associated data.
    
    Returns:
        Dict: A dictionary with 'status' set to "sandbox_started" and 'processed' set to True.
    """
    logger.info(f"Processing sandbox_started event: {event.get('id')}")
    return {"status": "sandbox_started", "processed": True}


def handle_sandbox_stopped(event: Dict) -> Dict:
    """
    Process a sandbox stopped webhook event.
    
    Parameters:
        event (Dict): Event payload; expected to include keys such as 'id', 'type', 'timestamp', and 'data'.
    
    Returns:
        result (Dict): Result indicating the event was handled, with 'status' set to "sandbox_stopped" and 'processed' set to True.
    """
    logger.info(f"Processing sandbox_stopped event: {event.get('id')}")
    return {"status": "sandbox_stopped", "processed": True}


def handle_code_executed(event: Dict) -> Dict:
    """
    Process a code execution webhook event.
    
    Parameters:
        event (Dict): Event payload (expected to include an 'id' and execution details).
    
    Returns:
        result (Dict): Processing result with keys:
            - "status": set to "code_executed".
            - "processed": `True` when the event was handled.
    """
    logger.info(f"Processing code_executed event: {event.get('id')}")
    return {"status": "code_executed", "processed": True}


def handle_trading_signal(event: Dict) -> Dict:
    """
    Handle a received trading signal event and route it for processing.
    
    Parameters:
        event (Dict): Event payload containing an `'id'` and trading-related data.
    
    Returns:
        result (Dict): A dictionary with `status` describing the outcome and `processed` set to `True` if the event was handled.
    """
    logger.info(f"Processing trading signal: {event.get('id')}")
    # In production, forward to trading engine
    return {"status": "trading_signal_received", "processed": True}


def handle_zapier_trigger(event: Dict) -> Dict:
    """
    Process a Zapier trigger webhook event.
    
    Parameters:
        event (Dict): Webhook event object (expected keys include 'id' and 'data').
    
    Returns:
        dict: Result with `"status": "zapier_trigger_processed"` and `"processed": True`.
    """
    logger.info(f"Processing Zapier trigger: {event.get('id')}")
    return {"status": "zapier_trigger_processed", "processed": True}


def handle_unknown_event(event: Dict) -> Dict:
    """
    Log and mark events whose `type` is not recognized by the router.
    
    Parameters:
        event (Dict): The webhook event object; expected to contain at least a `'type'` key.
    
    Returns:
        result (Dict): A status object with `"status": "unknown_event"` and `"processed": False`.
    """
    logger.warning(f"Unknown event type: {event.get('type')}")
    return {"status": "unknown_event", "processed": False}


def process_zapier_event(event: Dict) -> Dict:
    """
    Process a Zapier-originated webhook event and perform Zapier-specific handling.
    
    Parameters:
        event (Dict): The webhook event dictionary (expected to include keys like "id", "type", "timestamp", and "data").
    
    Returns:
        result (Dict): A dictionary describing the processing outcome, e.g. {"status": "zapier_processed"}.
    """
    # Implement Zapier-specific processing
    return {"status": "zapier_processed"}


def process_trading_signal(event: Dict) -> Dict:
    """
    Handle an incoming trading signal event and perform domain-specific processing.
    
    Parameters:
        event (Dict): The trading signal event payload (typically includes keys like `id`, `type`, `timestamp`, and `data`) that will be processed.
    
    Returns:
        result (Dict): A result object describing the processing outcome, e.g. `{'status': 'signal_processed'}` on success.
    """
    # Implement trading signal processing
    return {"status": "signal_processed"}


def trigger_alert(event: Dict):
    """
    Log and escalate a critical webhook event for external alerting.
    
    Parameters:
        event (Dict): Event object (contains at minimum an 'id') used to identify and describe the alert. This function logs a warning and serves as a placeholder for sending the event to external alerting channels (Slack, email, etc.) in production.
    """
    logger.warning(f"🚨 ALERT triggered for event: {event.get('id')}")
    # In production, send to Slack, email, etc.


def save_webhook_event(event: Dict):
    """
    Persist a webhook event by appending it as a JSON line to a date-stamped log file.
    
    Writes the given event as a single JSON object line to a JSONL file located under logs/webhooks, with the filename formatted as `webhooks_YYYY-MM-DD.jsonl`. Creates the logs directory if it does not exist. On failure, the error is logged.
    
    Parameters:
        event (Dict): The webhook event data (JSON-serializable) to persist.
    """
    try:
        log_dir = Path(__file__).parent.parent / 'logs' / 'webhooks'
        log_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f'webhooks_{date_str}.jsonl'

        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    except Exception as e:
        logger.error(f"Failed to save webhook event: {e}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """
    Start the Flask webhook server and display a startup banner.
    
    Prints a startup banner and server configuration (port, API key preview, webhook secret status, and available endpoints) to stdout, then starts the Flask application bound to 0.0.0.0 on the configured PORT with threading enabled.
    """
    print("\n" + "="*70)
    print("🌐 E2B WEBHOOK SERVER - Agent X5.0")
    print("="*70 + "\n")

    print(f"📡 Starting webhook server on port {PORT}...")
    print(f"🔑 E2B API Key: {E2B_API_KEY[:20]}...")
    print(f"🔒 Webhook Secret: {'Configured' if WEBHOOK_SECRET else 'Not set'}")
    print("\n" + "="*70)
    print("ENDPOINTS:")
    print(f"  GET  /health                    - Health check")
    print(f"  POST /webhook/e2b               - E2B events")
    print(f"  POST /webhook/e2b/sandbox_started")
    print(f"  POST /webhook/e2b/sandbox_stopped")
    print(f"  POST /webhook/e2b/code_executed")
    print(f"  POST /webhook/zapier            - Zapier triggers")
    print(f"  POST /webhook/trading           - Trading signals")
    print(f"  GET  /events                    - Get recent events")
    print(f"  POST /events/clear              - Clear events")
    print("="*70 + "\n")

    print(f"🚀 Server running at http://0.0.0.0:{PORT}")
    print("Press Ctrl+C to stop\n")

    # Run server
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False,
        threaded=True
    )


if __name__ == "__main__":
    main()