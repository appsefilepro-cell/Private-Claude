"""
Zapier MCP (Model Context Protocol) Connector
Integrates Agent X2.0 with Zapier via MCP endpoint
"""

import os
import json
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ZapierMCP')


class ZapierMCPConnector:
    """
    Zapier Model Context Protocol Connector
    Provides programmatic access to Zapier Zaps via MCP
    """

    def __init__(self):
        self.endpoint = os.getenv('ZAPIER_MCP_ENDPOINT', 'https://mcp.zapier.com/api/mcp/mcp')
        self.bearer_token = os.getenv('ZAPIER_MCP_BEARER_TOKEN')
        self.webhook_url = os.getenv('ZAPIER_WEBHOOK_URL')

        if not self.bearer_token:
            logger.warning("ZAPIER_MCP_BEARER_TOKEN not configured in .env")

        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        logger.info("Zapier MCP Connector initialized")

    def check_connection(self) -> Dict[str, Any]:
        """
        Check connection to Zapier MCP endpoint

        Returns:
            Status dictionary
        """
        try:
            response = requests.get(
                self.endpoint,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("✓ Zapier MCP connection successful")
                return {
                    "connected": True,
                    "status_code": response.status_code,
                    "endpoint": self.endpoint
                }
            else:
                logger.warning(f"Zapier MCP returned status {response.status_code}")
                return {
                    "connected": False,
                    "status_code": response.status_code,
                    "error": response.text
                }

        except Exception as e:
            logger.error(f"Zapier MCP connection failed: {e}")
            return {
                "connected": False,
                "error": str(e)
            }

    def list_available_actions(self) -> List[Dict[str, Any]]:
        """
        List all available Zapier actions via MCP

        Returns:
            List of available actions
        """
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json={"method": "list_actions"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                actions = data.get('actions', [])
                logger.info(f"Found {len(actions)} Zapier actions")
                return actions
            else:
                logger.error(f"Failed to list actions: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error listing Zapier actions: {e}")
            return []

    def trigger_zap(self, zap_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger a specific Zap via MCP

        Args:
            zap_name: Name of the Zap to trigger
            payload: Data to send to the Zap

        Returns:
            Response from Zapier
        """
        try:
            logger.info(f"Triggering Zap: {zap_name}")

            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json={
                    "method": "trigger_zap",
                    "zap_name": zap_name,
                    "payload": payload
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Zap triggered successfully: {zap_name}")
                return {
                    "success": True,
                    "zap_name": zap_name,
                    "response": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Zap trigger failed: {response.status_code}")
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            logger.error(f"Error triggering Zap: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def send_trading_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send trading signal to Zapier for processing

        Args:
            signal: Trading signal data
            {
                "pair": "BTC/USD",
                "action": "BUY",
                "confidence": 0.85,
                "price": 50000,
                "pattern": "HAMMER"
            }

        Returns:
            Zapier response
        """
        logger.info(f"Sending trading signal: {signal.get('action')} {signal.get('pair')}")

        return self.trigger_zap("Trading Signal Handler", signal)

    def log_to_sheets(self, data: Dict[str, Any], sheet_name: str = "Trade Log") -> Dict[str, Any]:
        """
        Log data to Google Sheets via Zapier

        Args:
            data: Data to log
            sheet_name: Name of the Google Sheet

        Returns:
            Zapier response
        """
        payload = {
            "sheet_name": sheet_name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        return self.trigger_zap("Log to Google Sheets", payload)

    def send_email_alert(self, subject: str, body: str, recipients: List[str] = None) -> Dict[str, Any]:
        """
        Send email alert via Zapier

        Args:
            subject: Email subject
            body: Email body
            recipients: List of recipient emails

        Returns:
            Zapier response
        """
        if recipients is None:
            recipients = [os.getenv('ALERT_EMAIL', 'appsefilepro@gmail.com')]

        payload = {
            "subject": subject,
            "body": body,
            "recipients": recipients,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Sending email alert: {subject}")
        return self.trigger_zap("Email Alert", payload)

    def send_to_sharepoint(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload file to SharePoint via Zapier

        Args:
            file_data: File data to upload
            {
                "filename": "trade_log.csv",
                "content": "...",
                "folder": "Trading Operations"
            }

        Returns:
            Zapier response
        """
        logger.info(f"Uploading to SharePoint: {file_data.get('filename')}")
        return self.trigger_zap("Upload to SharePoint", file_data)

    def create_case_notification(self, case_number: int, case_caption: str, status: str) -> Dict[str, Any]:
        """
        Create notification for legal case update

        Args:
            case_number: Case number
            case_caption: Case caption
            status: Status update

        Returns:
            Zapier response
        """
        payload = {
            "case_number": case_number,
            "case_caption": case_caption,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "url": f"https://appsholdingswyinc.sharepoint.com/Legal/Case_{case_number:02d}"
        }

        logger.info(f"Creating case notification: Case {case_number} - {status}")
        return self.trigger_zap("Legal Case Notification", payload)

    def trigger_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger Zapier webhook directly (fallback method)

        Args:
            data: Data to send to webhook

        Returns:
            Response from webhook
        """
        if not self.webhook_url:
            logger.error("ZAPIER_WEBHOOK_URL not configured")
            return {"success": False, "error": "Webhook URL not configured"}

        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("✓ Webhook triggered successfully")
                return {
                    "success": True,
                    "status_code": response.status_code
                }
            else:
                logger.error(f"Webhook failed: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code
                }

        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_spending_status(self) -> Dict[str, Any]:
        """
        Check Zapier MCP spending status

        Returns:
            Spending status information
        """
        try:
            response = requests.get(
                f"{self.endpoint}/status",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "unknown",
                    "note": "Spending cap may be active. Resets at 3am."
                }

        except Exception as e:
            logger.warning(f"Could not check spending status: {e}")
            return {
                "status": "unknown",
                "note": "Spending cap resets at 3am"
            }


def main():
    """Test Zapier MCP connector"""
    logger.info("=== ZAPIER MCP CONNECTOR TEST ===")

    connector = ZapierMCPConnector()

    # Check connection
    print("\n1. Checking Zapier MCP connection...")
    status = connector.check_connection()
    print(f"   Status: {json.dumps(status, indent=2)}")

    # Check spending status
    print("\n2. Checking spending status...")
    spending = connector.get_spending_status()
    print(f"   Spending: {json.dumps(spending, indent=2)}")

    if status.get('connected'):
        # List available actions
        print("\n3. Listing available Zapier actions...")
        actions = connector.list_available_actions()
        print(f"   Found {len(actions)} actions")

        # Test email alert
        print("\n4. Testing email alert...")
        result = connector.send_email_alert(
            subject="Zapier MCP Test",
            body="This is a test email from Agent X2.0 Zapier MCP connector"
        )
        print(f"   Result: {json.dumps(result, indent=2)}")

    else:
        print("\n⚠️  Zapier MCP not connected")
        print("   Possible reasons:")
        print("   - Spending cap reached (resets at 3am)")
        print("   - Invalid bearer token")
        print("   - Network connectivity issue")

    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    main()
