"""
Zapier MCP Integration Test Suite
Automated testing for email alerts, Google Sheets logging, and all Zapier integrations
Run after 3am when spending cap resets
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-a-trading' / 'zapier-integration'))

from zapier_mcp_connector import ZapierMCPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ZapierTests')


class ZapierIntegrationTester:
    """Comprehensive Zapier MCP integration tester"""

    def __init__(self):
        """Initialize Zapier tester"""
        self.connector = ZapierMCPConnector()
        self.results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tests": []
        }
        self.passed = 0
        self.failed = 0

    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results["tests"].append({
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        if passed:
            self.passed += 1
            logger.info(f"{status}: {test_name}")
        else:
            self.failed += 1
            logger.error(f"{status}: {test_name} - {details}")

        if details and passed:
            logger.info(f"  → {details}")

    def test_connection(self):
        """Test basic Zapier MCP connection"""
        logger.info("\n" + "="*70)
        logger.info("TEST 1: ZAPIER MCP CONNECTION")
        logger.info("="*70)

        try:
            status = self.connector.check_connection()
            self.log_result("Connection Test", True, "Connected successfully")
            return True
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Forbidden" in error_msg:
                self.log_result("Connection Test", False, "Spending cap still active - wait for 3am reset")
            else:
                self.log_result("Connection Test", False, error_msg)
            return False

    def test_email_alert(self):
        """Test email alert functionality"""
        logger.info("\n" + "="*70)
        logger.info("TEST 2: EMAIL ALERTS")
        logger.info("="*70)

        try:
            # Test email alert
            test_alert = {
                "subject": "🧪 Agent X2.0 Test Alert",
                "body": f"""This is a test email from Agent X2.0 Trading System.

                Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                Test Type: Zapier MCP Email Alert
                Status: System Operational ✅

                If you receive this email, the Zapier email integration is working correctly.
                """,
                "recipients": [os.getenv('ALERT_EMAIL', 'appsefilepro@gmail.com')]
            }

            result = self.connector.send_email_alert(
                subject=test_alert['subject'],
                body=test_alert['body'],
                recipients=test_alert['recipients']
            )

            self.log_result("Email Alert Test", True, f"Test email sent to {test_alert['recipients'][0]}")
            return True

        except Exception as e:
            self.log_result("Email Alert Test", False, str(e))
            return False

    def test_trading_signal(self):
        """Test trading signal transmission"""
        logger.info("\n" + "="*70)
        logger.info("TEST 3: TRADING SIGNAL TRANSMISSION")
        logger.info("="*70)

        try:
            # Test trading signal
            test_signal = {
                "timestamp": datetime.now().isoformat(),
                "pair": "BTC/USD",
                "action": "BUY",
                "pattern": "HAMMER",
                "confidence": 0.82,
                "price": 50000.00,
                "quantity": 0.01,
                "stop_loss": 49000.00,
                "take_profit": 51000.00,
                "risk_profile": "novice",
                "test": True
            }

            result = self.connector.send_trading_signal(test_signal)
            self.log_result("Trading Signal Test", True, f"Sent {test_signal['action']} signal for {test_signal['pair']}")
            return True

        except Exception as e:
            self.log_result("Trading Signal Test", False, str(e))
            return False

    def test_google_sheets_logging(self):
        """Test Google Sheets logging"""
        logger.info("\n" + "="*70)
        logger.info("TEST 4: GOOGLE SHEETS LOGGING")
        logger.info("="*70)

        try:
            # Test Google Sheets logging
            test_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "TEST",
                "pair": "BTC/USD",
                "price": 50000.00,
                "profit_loss": 0.00,
                "status": "Test Entry",
                "risk_profile": "novice",
                "test": True
            }

            result = self.connector.log_to_sheets(
                data=test_data,
                sheet_name="Agent 3.0 Trading Log"
            )

            self.log_result("Google Sheets Test", True, "Test data logged to Google Sheets")
            return True

        except Exception as e:
            self.log_result("Google Sheets Test", False, str(e))
            return False

    def test_sharepoint_upload(self):
        """Test SharePoint upload functionality"""
        logger.info("\n" + "="*70)
        logger.info("TEST 5: SHAREPOINT UPLOAD")
        logger.info("="*70)

        try:
            # Create test report file
            test_file = "/tmp/agent_x2_test_report.txt"
            with open(test_file, 'w') as f:
                f.write(f"""Agent X2.0 Test Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test Type: SharePoint Upload Integration
Status: Testing...

This is a test file to verify SharePoint upload functionality via Zapier MCP.
""")

            result = self.connector.send_to_sharepoint(
                file_path=test_file,
                folder_path="/Trading Operations/Test Reports"
            )

            self.log_result("SharePoint Upload Test", True, "Test file uploaded to SharePoint")
            return True

        except Exception as e:
            self.log_result("SharePoint Upload Test", False, str(e))
            return False

    def test_case_notification(self):
        """Test legal case notification"""
        logger.info("\n" + "="*70)
        logger.info("TEST 6: LEGAL CASE NOTIFICATION")
        logger.info("="*70)

        try:
            # Test case notification
            test_case = {
                "case_number": 0,
                "case_caption": "Test Case - Integration Testing",
                "status": "Testing Zapier Integration",
                "priority": "TEST",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            result = self.connector.create_case_notification(
                case_number=test_case['case_number'],
                case_caption=test_case['case_caption'],
                status=test_case['status']
            )

            self.log_result("Case Notification Test", True, "Legal case notification sent")
            return True

        except Exception as e:
            self.log_result("Case Notification Test", False, str(e))
            return False

    def run_all_tests(self):
        """Run complete Zapier integration test suite"""
        logger.info("\n" + "="*70)
        logger.info("ZAPIER MCP - COMPREHENSIVE INTEGRATION TEST SUITE")
        logger.info("="*70)
        logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70 + "\n")

        # Test 1: Connection
        connection_ok = self.test_connection()

        if not connection_ok:
            logger.warning("\n⚠️  Zapier MCP connection failed - spending cap may still be active")
            logger.info("Scheduled reset: 3:00 AM")
            logger.info("Run this test again after 3:00 AM\n")
            self.export_results()
            return False

        # Run all integration tests
        self.test_email_alert()
        self.test_trading_signal()
        self.test_google_sheets_logging()
        self.test_sharepoint_upload()
        self.test_case_notification()

        # Summary
        self.print_summary()
        self.export_results()

        return self.failed == 0

    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        logger.info("\n" + "="*70)
        logger.info("ZAPIER INTEGRATION TEST SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {self.passed} ✅")
        logger.info(f"Failed: {self.failed} ❌")
        logger.info(f"Pass Rate: {pass_rate:.1f}%")
        logger.info("="*70 + "\n")

        if self.failed == 0:
            logger.info("🎉 ALL ZAPIER INTEGRATIONS WORKING PERFECTLY!")
            logger.info("\nNext Steps:")
            logger.info("1. Check your email for test alert")
            logger.info("2. Verify Google Sheets has test entry")
            logger.info("3. Check SharePoint for test file upload")
            logger.info("4. System ready for live trading signal transmission")
        else:
            logger.warning(f"⚠️  {self.failed} test(s) failed - review errors above")

    def export_results(self):
        """Export test results to JSON"""
        output_dir = Path(__file__).parent.parent / 'test-results'
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f'zapier_integration_tests_{timestamp}.json'

        self.results["summary"] = {
            "total": self.passed + self.failed,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": round((self.passed / (self.passed + self.failed) * 100), 2) if (self.passed + self.failed) > 0 else 0
        }

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Test results exported to: {output_file}")


def main():
    """Run Zapier integration tests"""
    print("\n" + "🔔"*35)
    print("    ZAPIER MCP INTEGRATION TEST SUITE")
    print("    Run after 3am when spending cap resets")
    print("🔔"*35 + "\n")

    tester = ZapierIntegrationTester()
    success = tester.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
