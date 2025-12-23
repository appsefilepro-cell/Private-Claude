#!/usr/bin/env python3
"""
Postman Agent 5.0 Integration
Integrates Postman API testing with Agent 5.0 automation system
"""

import json
import os
import sys
import subprocess
import schedule
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/Private-Claude/logs/postman_agent5.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PostmanAgent5Integration:
    """Integrates Postman testing with Agent 5.0"""

    def __init__(self):
        """Initialize Agent 5.0 integration"""
        self.base_dir = Path('/home/user/Private-Claude')
        self.scripts_dir = self.base_dir / 'scripts'
        self.config_dir = self.base_dir / 'config'
        self.logs_dir = self.base_dir / 'logs'
        self.test_results_dir = self.base_dir / 'test-results'

        # Create directories
        for directory in [self.logs_dir, self.test_results_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Load Agent 5.0 configuration
        self.agent_config_path = self.config_dir / 'agent_5_config.json'
        self.agent_config = self._load_agent_config()

        logger.info("Postman Agent 5.0 Integration initialized")

    def _load_agent_config(self) -> Dict:
        """Load Agent 5.0 configuration"""
        try:
            with open(self.agent_config_path, 'r') as f:
                config = json.load(f)
            logger.info("Loaded Agent 5.0 configuration")
            return config
        except Exception as e:
            logger.error(f"Error loading Agent 5.0 config: {str(e)}")
            return {}

    def run_postman_tests(self) -> Dict:
        """Run Postman tests via Newman"""
        logger.info("Running Postman API tests")

        collection_path = self.config_dir / 'postman_complete_collection.json'
        environment_path = self.config_dir / 'postman_environment.json'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.test_results_dir / f'newman_test_{timestamp}.json'

        try:
            cmd = [
                'newman', 'run', str(collection_path),
                '-e', str(environment_path),
                '--reporters', 'json',
                '--reporter-json-export', str(report_path),
                '--timeout-request', '5000',
                '--bail'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Parse results
            if report_path.exists():
                with open(report_path, 'r') as f:
                    test_results = json.load(f)

                return {
                    'success': result.returncode == 0,
                    'timestamp': timestamp,
                    'results': test_results,
                    'report_path': str(report_path)
                }
            else:
                return {
                    'success': False,
                    'timestamp': timestamp,
                    'error': 'Report file not generated',
                    'stderr': result.stderr
                }

        except Exception as e:
            logger.error(f"Error running Postman tests: {str(e)}")
            return {
                'success': False,
                'timestamp': timestamp,
                'error': str(e)
            }

    def send_slack_notification(self, test_results: Dict):
        """Send test results to Slack"""
        if not self.agent_config.get('slack_integration', {}).get('enabled'):
            logger.info("Slack notifications disabled")
            return

        try:
            # Get Slack webhook URL
            slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
            if not slack_webhook:
                logger.warning("SLACK_WEBHOOK_URL not configured")
                return

            # Build notification message
            success = test_results.get('success', False)
            timestamp = test_results.get('timestamp', '')

            message = {
                'text': f"Postman API Test Results - {timestamp}",
                'attachments': [{
                    'color': '#36a64f' if success else '#ff0000',
                    'title': 'Test Status',
                    'text': 'All tests passed' if success else 'Some tests failed',
                    'fields': [
                        {
                            'title': 'Timestamp',
                            'value': timestamp,
                            'short': True
                        },
                        {
                            'title': 'Status',
                            'value': 'Success' if success else 'Failed',
                            'short': True
                        }
                    ],
                    'footer': 'Agent 5.0 Automated Testing'
                }]
            }

            # Send to Slack
            import requests
            response = requests.post(slack_webhook, json=message)

            if response.status_code == 200:
                logger.info("Sent Slack notification")
            else:
                logger.error(f"Failed to send Slack notification: {response.text}")

        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")

    def update_agent_config(self, test_results: Dict):
        """Update Agent 5.0 config with test results"""
        try:
            # Add postman test status to agent config
            if 'postman_integration' not in self.agent_config:
                self.agent_config['postman_integration'] = {}

            self.agent_config['postman_integration'].update({
                'last_test_run': test_results.get('timestamp'),
                'last_test_success': test_results.get('success'),
                'test_results_path': test_results.get('report_path')
            })

            # Save updated config
            with open(self.agent_config_path, 'w') as f:
                json.dump(self.agent_config, f, indent=2)

            logger.info("Updated Agent 5.0 configuration")

        except Exception as e:
            logger.error(f"Error updating agent config: {str(e)}")

    def run_scheduled_tests(self):
        """Run tests on a schedule"""
        logger.info("Starting scheduled Postman tests")

        # Schedule tests every hour
        schedule.every().hour.do(self.run_test_cycle)

        # Schedule daily full sync
        schedule.every().day.at("02:00").do(self.run_full_sync)

        logger.info("Scheduled tasks configured")
        logger.info("- API tests: Every hour")
        logger.info("- Full sync: Daily at 02:00")

        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)

    def run_test_cycle(self):
        """Run a complete test cycle"""
        logger.info("Starting test cycle")

        # Run API scanner
        scanner_cmd = ['python3', str(self.scripts_dir / 'postman_api_scanner.py'), 'scan']
        subprocess.run(scanner_cmd, cwd=str(self.base_dir))

        # Run Postman tests
        test_results = self.run_postman_tests()

        # Send notifications
        self.send_slack_notification(test_results)

        # Update Agent 5.0 config
        self.update_agent_config(test_results)

        logger.info("Test cycle completed")

        return test_results

    def run_full_sync(self):
        """Run full sync to Postman Cloud"""
        logger.info("Starting full sync")

        # Run sync script
        sync_cmd = ['python3', str(self.scripts_dir / 'postman_sync.py'), 'sync']
        result = subprocess.run(sync_cmd, cwd=str(self.base_dir), capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("Full sync completed successfully")
        else:
            logger.error(f"Full sync failed: {result.stderr}")

        return result.returncode == 0

    def generate_integration_report(self) -> Dict:
        """Generate comprehensive integration report"""
        logger.info("Generating integration report")

        report = {
            'timestamp': datetime.now().isoformat(),
            'agent_5_version': self.agent_config.get('system_metadata', {}).get('version'),
            'postman_integration': {
                'enabled': True,
                'last_test_run': self.agent_config.get('postman_integration', {}).get('last_test_run'),
                'last_test_success': self.agent_config.get('postman_integration', {}).get('last_test_success'),
                'automated_testing_enabled': True,
                'scheduled_tests': 'Hourly',
                'scheduled_sync': 'Daily at 02:00'
            },
            'integrations': {
                'e2b': self.agent_config.get('e2b_integration', {}).get('enabled', False),
                'github': self.agent_config.get('github_integration', {}).get('enabled', False),
                'zapier': self.agent_config.get('zapier_integration', {}).get('enabled', False),
                'slack': self.agent_config.get('slack_integration', {}).get('enabled', False)
            },
            'test_configuration': {
                'collection_path': str(self.config_dir / 'postman_complete_collection.json'),
                'environment_path': str(self.config_dir / 'postman_environment.json'),
                'test_results_dir': str(self.test_results_dir),
                'log_file': str(self.logs_dir / 'postman_agent5.log')
            }
        }

        # Save report
        report_path = self.logs_dir / 'postman_agent5_integration_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Integration report saved to {report_path}")
        return report


def main():
    """Main entry point"""
    integration = PostmanAgent5Integration()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'test':
            results = integration.run_test_cycle()
            print(json.dumps(results, indent=2))

        elif command == 'sync':
            success = integration.run_full_sync()
            sys.exit(0 if success else 1)

        elif command == 'schedule':
            integration.run_scheduled_tests()

        elif command == 'report':
            report = integration.generate_integration_report()
            print(json.dumps(report, indent=2))

        else:
            print(f"Unknown command: {command}")
            print("Usage: python postman_agent5_integration.py [test|sync|schedule|report]")
            sys.exit(1)
    else:
        # Default: run single test cycle
        results = integration.run_test_cycle()
        print(f"Test cycle completed. Success: {results.get('success')}")


if __name__ == '__main__':
    main()
