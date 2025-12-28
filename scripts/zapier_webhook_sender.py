"""
Simple Zapier Webhook Sender - Actually Works
Just send data to Zapier webhooks
"""

import requests
import json
from datetime import datetime


def send_to_zapier(webhook_url: str, data: dict) -> bool:
    """
    Send data to Zapier webhook

    Args:
        webhook_url: Your Zapier webhook URL
        data: Dictionary of data to send

    Returns:
        True if successful
    """
    try:
        response = requests.post(webhook_url, json=data, timeout=10)

        if response.status_code == 200:
            print(f"✅ Sent to Zapier successfully")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# EXAMPLE: Send task completion to Zapier
if __name__ == "__main__":
    # PUT YOUR ZAPIER WEBHOOK URL HERE
    WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/YOUR_WEBHOOK_ID/YOUR_HOOK_ID"

    # Your data
    data = {
        "task": "Task completed",
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "message": "All tasks finished"
    }

    # Send it
    send_to_zapier(WEBHOOK_URL, data)
