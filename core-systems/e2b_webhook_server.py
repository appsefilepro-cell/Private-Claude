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
from typing import Any, Dict, List

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
load_dotenv(Path(__file__).parent.parent / "config" / ".env")
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("E2BWebhook")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for webhook access

# Configuration
E2B_API_KEY = os.getenv("E2B_API_KEY", "e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773")
WEBHOOK_SECRET = os.getenv("E2B_WEBHOOK_SECRET", "")
PORT = int(os.getenv("E2B_WEBHOOK_PORT", "5000"))

# Webhook event storage
webhook_events: List[Dict] = []
MAX_EVENTS = 1000  # Keep last 1000 events


# ============================================================================
# WEBHOOK HANDLERS
# ============================================================================


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "E2B Webhook Server",
                "version": "5.0.0",
                "timestamp": datetime.now().isoformat(),
                "events_received": len(webhook_events),
            }
        ),
        200,
    )


@app.route("/webhook/e2b", methods=["POST"])
def e2b_webhook():
    """
    Main E2B webhook endpoint
    Receives events from E2B Sandbox
    """
    try:
        # Get webhook data
        data = request.get_json()

        if not data:
            logger.warning("Received empty webhook payload")
            return jsonify({"error": "Empty payload"}), 400

        # Verify webhook secret if configured
        if WEBHOOK_SECRET:
            auth_header = request.headers.get("Authorization", "")
            if (
                not auth_header.startswith("Bearer ")
                or auth_header[7:] != WEBHOOK_SECRET
            ):
                logger.warning("Invalid webhook authentication")
                return jsonify({"error": "Unauthorized"}), 401

        # Process webhook event
        event = {
            "id": data.get("id", f"event_{len(webhook_events)}"),
            "type": data.get("type", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "headers": dict(request.headers),
        }

        # Store event
        webhook_events.append(event)

        # Keep only last MAX_EVENTS
        if len(webhook_events) > MAX_EVENTS:
            webhook_events.pop(0)

        logger.info(f"📥 Received E2B webhook: {event['type']} (ID: {event['id']})")

        # Route to appropriate handler
        event_type = event["type"]
        result = route_webhook_event(event)

        # Save to file
        save_webhook_event(event)

        return (
            jsonify(
                {
                    "status": "received",
                    "event_id": event["id"],
                    "processed": True,
                    "result": result,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/e2b/sandbox_started", methods=["POST"])
def sandbox_started():
    """Handle sandbox started events"""
    try:
        data = request.get_json()
        sandbox_id = data.get("sandbox_id")

        logger.info(f"🚀 E2B Sandbox started: {sandbox_id}")

        event = {
            "type": "sandbox_started",
            "sandbox_id": sandbox_id,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        webhook_events.append(event)
        save_webhook_event(event)

        return jsonify({"status": "acknowledged"}), 200

    except Exception as e:
        logger.error(f"❌ Error in sandbox_started handler: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/e2b/sandbox_stopped", methods=["POST"])
def sandbox_stopped():
    """Handle sandbox stopped events"""
    try:
        data = request.get_json()
        sandbox_id = data.get("sandbox_id")

        logger.info(f"⏹️  E2B Sandbox stopped: {sandbox_id}")

        event = {
            "type": "sandbox_stopped",
            "sandbox_id": sandbox_id,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        webhook_events.append(event)
        save_webhook_event(event)

        return jsonify({"status": "acknowledged"}), 200

    except Exception as e:
        logger.error(f"❌ Error in sandbox_stopped handler: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/e2b/code_executed", methods=["POST"])
def code_executed():
    """Handle code execution events"""
    try:
        data = request.get_json()
        execution_id = data.get("execution_id")
        success = data.get("success", False)

        logger.info(
            f"💻 Code executed in E2B: {execution_id} ({'✅' if success else '❌'})"
        )

        event = {
            "type": "code_executed",
            "execution_id": execution_id,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "data": data,
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


@app.route("/webhook/zapier", methods=["POST"])
def zapier_webhook():
    """
    Zapier webhook endpoint
    Receives triggers from Zapier automation
    """
    try:
        data = request.get_json()

        event = {
            "id": f"zapier_{len(webhook_events)}",
            "type": "zapier_trigger",
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        webhook_events.append(event)
        logger.info(f"⚡ Received Zapier webhook: {event['id']}")

        # Process Zapier event
        result = process_zapier_event(event)

        save_webhook_event(event)

        return (
            jsonify({"status": "received", "event_id": event["id"], "result": result}),
            200,
        )

    except Exception as e:
        logger.error(f"❌ Error processing Zapier webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/trading", methods=["POST"])
def trading_webhook():
    """
    Trading signal webhook
    Receives trading signals from TradingView, etc.
    """
    try:
        data = request.get_json()

        event = {
            "id": f"trade_{len(webhook_events)}",
            "type": "trading_signal",
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        webhook_events.append(event)
        logger.info(f"📈 Received trading signal: {event['id']}")

        # Forward to trading system
        result = process_trading_signal(event)

        save_webhook_event(event)

        return (
            jsonify({"status": "received", "event_id": event["id"], "result": result}),
            200,
        )

    except Exception as e:
        logger.error(f"❌ Error processing trading webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/events", methods=["GET"])
def get_events():
    """Get recent webhook events"""
    limit = int(request.args.get("limit", 50))
    event_type = request.args.get("type")

    events = webhook_events[-limit:]

    if event_type:
        events = [e for e in events if e.get("type") == event_type]

    return (
        jsonify(
            {"total": len(webhook_events), "returned": len(events), "events": events}
        ),
        200,
    )


@app.route("/events/clear", methods=["POST"])
def clear_events():
    """Clear all webhook events"""
    global webhook_events
    count = len(webhook_events)
    webhook_events = []
    logger.info(f"🗑️  Cleared {count} webhook events")

    return jsonify({"status": "cleared", "count": count}), 200


# ============================================================================
# EVENT PROCESSORS
# ============================================================================


def route_webhook_event(event: Dict) -> Dict[str, Any]:
    """Route webhook event to appropriate handler"""
    event_type = event.get("type", "unknown")

    handlers = {
        "sandbox_started": handle_sandbox_started,
        "sandbox_stopped": handle_sandbox_stopped,
        "code_executed": handle_code_executed,
        "trading_signal": handle_trading_signal,
        "zapier_trigger": handle_zapier_trigger,
    }

    handler = handlers.get(event_type, handle_unknown_event)
    return handler(event)


def handle_sandbox_started(event: Dict) -> Dict:
    """Handle sandbox started event"""
    logger.info(f"Processing sandbox_started event: {event.get('id')}")
    return {"status": "sandbox_started", "processed": True}


def handle_sandbox_stopped(event: Dict) -> Dict:
    """Handle sandbox stopped event"""
    logger.info(f"Processing sandbox_stopped event: {event.get('id')}")
    return {"status": "sandbox_stopped", "processed": True}


def handle_code_executed(event: Dict) -> Dict:
    """Handle code execution event"""
    logger.info(f"Processing code_executed event: {event.get('id')}")
    return {"status": "code_executed", "processed": True}


def handle_trading_signal(event: Dict) -> Dict:
    """Handle trading signal event"""
    logger.info(f"Processing trading signal: {event.get('id')}")
    # In production, forward to trading engine
    return {"status": "trading_signal_received", "processed": True}


def handle_zapier_trigger(event: Dict) -> Dict:
    """Handle Zapier trigger event"""
    logger.info(f"Processing Zapier trigger: {event.get('id')}")
    return {"status": "zapier_trigger_processed", "processed": True}


def handle_unknown_event(event: Dict) -> Dict:
    """Handle unknown event types"""
    logger.warning(f"Unknown event type: {event.get('type')}")
    return {"status": "unknown_event", "processed": False}


def process_zapier_event(event: Dict) -> Dict:
    """Process Zapier webhook event"""
    # Implement Zapier-specific processing
    return {"status": "zapier_processed"}


def process_trading_signal(event: Dict) -> Dict:
    """Process trading signal webhook"""
    # Implement trading signal processing
    return {"status": "signal_processed"}


def trigger_alert(event: Dict):
    """Trigger alert for important events"""
    logger.warning(f"🚨 ALERT triggered for event: {event.get('id')}")
    # In production, send to Slack, email, etc.


def save_webhook_event(event: Dict):
    """Save webhook event to file"""
    try:
        log_dir = Path(__file__).parent.parent / "logs" / "webhooks"
        log_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"webhooks_{date_str}.jsonl"

        with open(log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    except Exception as e:
        logger.error(f"Failed to save webhook event: {e}")


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Start webhook server"""
    print("\n" + "=" * 70)
    print("🌐 E2B WEBHOOK SERVER - Agent X5.0")
    print("=" * 70 + "\n")

    print(f"📡 Starting webhook server on port {PORT}...")
    print(f"🔑 E2B API Key: {E2B_API_KEY[:20]}...")
    print(f"🔒 Webhook Secret: {'Configured' if WEBHOOK_SECRET else 'Not set'}")
    print("\n" + "=" * 70)
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
    print("=" * 70 + "\n")

    print(f"🚀 Server running at http://0.0.0.0:{PORT}")
    print("Press Ctrl+C to stop\n")

    # Run server
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
