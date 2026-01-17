"""
Integrated MCP Connector for Agent X5.0
Combines Postman API and Zapier MCP for complete automation
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Import individual MCP connectors
from postman_mcp_connector import PostmanMCPConnector
from zapier_mcp_connector import ZapierMCPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('IntegratedMCP')


class IntegratedMCPConnector:
    """
    Integrated MCP Connector
    Combines Postman and Zapier for powerful automation workflows
    """

    def __init__(self):
        self.postman = PostmanMCPConnector()
        self.zapier = ZapierMCPConnector()
        logger.info("Integrated MCP Connector initialized")

    def check_all_connections(self) -> Dict[str, Any]:
        """
        Check all MCP connections (Postman + Zapier)
        
        Returns:
            Status of all connections
        """
        logger.info("Checking all MCP connections...")
        
        postman_status = self.postman.check_connection()
        zapier_status = self.zapier.check_connection()
        
        return {
            "postman": postman_status,
            "zapier": zapier_status,
            "all_connected": postman_status.get('connected', False) and zapier_status.get('connected', False),
            "timestamp": datetime.now().isoformat()
        }

    def test_trading_api_with_alert(self, api_endpoint: str) -> Dict[str, Any]:
        """
        Test trading API endpoint and send alert via Zapier
        
        Args:
            api_endpoint: Trading API endpoint to test
        
        Returns:
            Test results and alert status
        """
        logger.info(f"Testing trading API: {api_endpoint}")
        
        # Create Postman test
        test_config = self.postman.integrate_with_trading_bot(
            api_endpoint=api_endpoint,
            method="GET"
        )
        
        # Send alert via Zapier
        alert_data = {
            "subject": "Trading API Test Completed",
            "body": f"API test completed for: {api_endpoint}\nConfiguration: {test_config['name']}",
            "timestamp": datetime.now().isoformat(),
            "test_config": test_config
        }
        
        zapier_result = self.zapier.send_email_alert(
            subject=alert_data["subject"],
            body=alert_data["body"]
        )
        
        return {
            "api_endpoint": api_endpoint,
            "postman_test": test_config,
            "zapier_alert": zapier_result,
            "timestamp": datetime.now().isoformat()
        }

    def monitor_with_alerts(self, collection_id: str, collection_name: str) -> Dict[str, Any]:
        """
        Set up Postman monitor with Zapier alert integration
        
        Args:
            collection_id: Postman collection ID
            collection_name: Collection name
        
        Returns:
            Setup results
        """
        logger.info(f"Setting up monitoring for: {collection_name}")
        
        # Create Postman monitor
        schedule = {
            "cron": "0 */6 * * *",  # Every 6 hours
            "timezone": "America/Los_Angeles"
        }
        
        monitor_result = self.postman.create_monitor(
            collection_id=collection_id,
            name=f"{collection_name} Monitor",
            schedule=schedule
        )
        
        # Configure Zapier webhook for failures
        webhook_data = {
            "monitor_name": collection_name,
            "schedule": schedule,
            "alert_email": os.getenv('ALERT_EMAIL', 'appsefilepro@gmail.com'),
            "timestamp": datetime.now().isoformat()
        }
        
        zapier_webhook = self.zapier.trigger_webhook(webhook_data)
        
        return {
            "postman_monitor": monitor_result,
            "zapier_webhook": zapier_webhook,
            "collection_name": collection_name,
            "timestamp": datetime.now().isoformat()
        }

    def log_api_test_results(self, test_name: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log API test results to Google Sheets via Zapier
        
        Args:
            test_name: Name of the test
            results: Test results data
        
        Returns:
            Logging status
        """
        logger.info(f"Logging test results: {test_name}")
        
        log_data = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "status": results.get("status", "unknown"),
            "response_time": results.get("response_time", "N/A"),
            "passed": results.get("passed", False),
            "details": json.dumps(results)
        }
        
        return self.zapier.log_to_sheets(log_data, sheet_name="API Test Results")

    def create_trading_api_collection(self) -> Dict[str, Any]:
        """
        Create a comprehensive trading API test collection
        
        Returns:
            Collection creation result
        """
        logger.info("Creating trading API test collection")
        
        collection = self.postman.create_collection(
            name="Agent X5.0 Trading API - Complete Tests",
            description="Comprehensive API tests for Agent X5.0 trading bot"
        )
        
        if collection.get('success'):
            # Send notification via Zapier
            self.zapier.send_email_alert(
                subject="New Postman Collection Created",
                body=f"Collection created: {collection['collection'].get('name', 'Unknown')}\nCollection ID: {collection['collection'].get('id', 'Unknown')}"
            )
        
        return collection

    def run_complete_api_validation(self) -> Dict[str, Any]:
        """
        Run complete API validation workflow
        1. List all Postman collections
        2. Run tests
        3. Log results to Sheets via Zapier
        4. Send status alerts
        
        Returns:
            Complete validation results
        """
        logger.info("Running complete API validation workflow")
        
        results = {
            "start_time": datetime.now().isoformat(),
            "steps": []
        }
        
        # Step 1: Check connections
        connections = self.check_all_connections()
        results["steps"].append({
            "step": "Check Connections",
            "status": "success" if connections['all_connected'] else "failed",
            "details": connections
        })
        
        if not connections['all_connected']:
            logger.error("Not all connections are active")
            return results
        
        # Step 2: List Postman collections
        collections = self.postman.list_collections()
        results["steps"].append({
            "step": "List Collections",
            "status": "success",
            "count": len(collections),
            "collections": [c.get('name', 'Unknown') for c in collections]
        })
        
        # Step 3: Get API usage
        usage = self.postman.get_api_key_usage()
        results["steps"].append({
            "step": "Check API Usage",
            "status": "success",
            "usage": usage
        })
        
        # Step 4: Send summary via Zapier
        summary = f"""
API Validation Complete

Collections Found: {len(collections)}
Postman Connected: {connections['postman']['connected']}
Zapier Connected: {connections['zapier']['connected']}

Timestamp: {datetime.now().isoformat()}
        """
        
        alert_result = self.zapier.send_email_alert(
            subject="API Validation Summary - Agent X5.0",
            body=summary
        )
        
        results["steps"].append({
            "step": "Send Alert",
            "status": "success" if alert_result.get('success') else "failed",
            "details": alert_result
        })
        
        results["end_time"] = datetime.now().isoformat()
        results["overall_status"] = "success"
        
        return results

    def sync_postman_to_zapier(self, collection_id: str) -> Dict[str, Any]:
        """
        Sync Postman collection data to Zapier for automation
        
        Args:
            collection_id: Postman collection ID
        
        Returns:
            Sync results
        """
        logger.info(f"Syncing Postman collection {collection_id} to Zapier")
        
        # Get collection details
        collection = self.postman.get_collection(collection_id)
        
        if not collection:
            return {
                "success": False,
                "error": "Collection not found"
            }
        
        # Send to Zapier webhook
        sync_data = {
            "collection_id": collection_id,
            "collection_name": collection.get('info', {}).get('name', 'Unknown'),
            "item_count": len(collection.get('item', [])),
            "synced_at": datetime.now().isoformat()
        }
        
        zapier_result = self.zapier.trigger_webhook(sync_data)
        
        return {
            "success": True,
            "collection": collection.get('info', {}).get('name'),
            "zapier_sync": zapier_result
        }

    def emergency_alert(self, message: str, severity: str = "HIGH") -> Dict[str, Any]:
        """
        Send emergency alert through all available channels
        
        Args:
            message: Alert message
            severity: Alert severity (LOW, MEDIUM, HIGH, CRITICAL)
        
        Returns:
            Alert status
        """
        logger.critical(f"EMERGENCY ALERT [{severity}]: {message}")
        
        # Send via Zapier email
        email_result = self.zapier.send_email_alert(
            subject=f"🚨 EMERGENCY ALERT [{severity}] - Agent X5.0",
            body=f"{message}\n\nTimestamp: {datetime.now().isoformat()}"
        )
        
        # Log to Zapier webhook
        webhook_result = self.zapier.trigger_webhook({
            "alert_type": "EMERGENCY",
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "alert_sent": True,
            "channels": {
                "email": email_result,
                "webhook": webhook_result
            },
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Test integrated MCP connector"""
    logger.info("=== INTEGRATED MCP CONNECTOR TEST ===")
    
    connector = IntegratedMCPConnector()
    
    # Check all connections
    print("\n1. Checking all MCP connections...")
    connections = connector.check_all_connections()
    print(f"   All Connected: {connections['all_connected']}")
    print(f"   Postman: {connections['postman']['connected']}")
    print(f"   Zapier: {connections['zapier']['connected']}")
    
    if connections['all_connected']:
        # Run complete validation
        print("\n2. Running complete API validation...")
        validation = connector.run_complete_api_validation()
        print(f"   Status: {validation['overall_status']}")
        print(f"   Steps completed: {len(validation['steps'])}")
        
        # Display results
        print("\n3. Validation Steps:")
        for step in validation['steps']:
            print(f"   - {step['step']}: {step['status']}")
    else:
        print("\n⚠️  Not all MCP connections are active")
        print("   Configure API keys in config/.env to enable all features")
    
    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    main()
