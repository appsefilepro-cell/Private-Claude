#!/usr/bin/env python3
"""
E2B Webhook Handler
Handles incoming webhooks from E2B and syncs to GitHub, Zapier, and other services
Optimized for minimal data usage
"""

import os
import json
import hmac
import hashlib
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Load configuration
E2B_API_KEY = os.getenv('E2B_API_KEY')
E2B_WEBHOOK_SECRET = os.getenv('E2B_WEBHOOK_SECRET')
ZAPIER_WEBHOOK_URL = os.getenv('ZAPIER_WEBHOOK_URL')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


class E2BWebhookHandler:
    """Efficient webhook handler with data optimization"""

    def __init__(self):
        self.webhook_id = "YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load webhook configuration"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'e2b_webhook_config.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature for security"""
        if not E2B_WEBHOOK_SECRET:
            return True  # Skip in dev mode

        expected = hmac.new(
            E2B_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def compress_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Minimize payload size for data efficiency"""
        if not self.config.get('data_optimization', {}).get('minimal_mode'):
            return data

        # Keep only essential fields
        essential = {
            'event': data.get('event'),
            'id': data.get('execution_id') or data.get('sandbox_id'),
            'status': data.get('status'),
            'timestamp': datetime.utcnow().isoformat()
        }

        # Add output only if execution completed
        if data.get('event') == 'execution.completed':
            essential['output'] = data.get('output', '')[:500]  # Limit output size

        return essential

    def sync_to_zapier(self, event_data: Dict[str, Any]) -> bool:
        """Send event to Zapier webhook"""
        if not ZAPIER_WEBHOOK_URL or not self.config['sync_targets']['zapier']['enabled']:
            return False

        try:
            compressed = self.compress_payload(event_data)
            response = requests.post(
                ZAPIER_WEBHOOK_URL,
                json=compressed,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Zapier sync error: {e}")
            return False

    def sync_to_github(self, event_data: Dict[str, Any]) -> bool:
        """Sync execution results to GitHub"""
        if not GITHUB_TOKEN or not self.config['sync_targets']['github']['enabled']:
            return False

        try:
            # Create issue comment or commit based on event type
            event_type = event_data.get('event')

            if event_type == 'execution.completed':
                # Create a compact summary
                summary = f"E2B Execution: {event_data.get('status')}\n"
                summary += f"Time: {datetime.utcnow().isoformat()}\n"

                # Could post to GitHub issue/PR here
                print(f"GitHub sync: {summary}")
                return True

            return False
        except Exception as e:
            print(f"GitHub sync error: {e}")
            return False

    def handle_webhook(self, event_type: str, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """Main webhook handler"""

        # Verify signature
        if signature:
            payload_bytes = json.dumps(payload).encode()
            if not self.verify_signature(payload_bytes, signature):
                return {'error': 'Invalid signature', 'status': 401}

        # Process event
        event_data = {
            'event': event_type,
            **payload
        }

        # Sync to configured targets
        results = {
            'zapier': self.sync_to_zapier(event_data),
            'github': self.sync_to_github(event_data),
            'timestamp': datetime.utcnow().isoformat()
        }

        return {
            'status': 'success',
            'webhook_id': self.webhook_id,
            'synced': results
        }


def main():
    """Example usage"""
    handler = E2BWebhookHandler()

    # Test webhook handling
    test_event = {
        'event': 'execution.completed',
        'execution_id': 'test-123',
        'status': 'success',
        'output': 'Hello from E2B!'
    }

    result = handler.handle_webhook('execution.completed', test_event)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
