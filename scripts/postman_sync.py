#!/usr/bin/env python3
"""
Postman API Configuration Sync Manager
Synchronizes API configurations to Postman, runs Newman tests, and generates reports
"""

import json
import os
import sys
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/Private-Claude/logs/postman_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class PostmanConfig:
    """Configuration for Postman integration"""
    api_key: str
    workspace_id: str
    collection_path: str
    environment_path: str
    newman_config: Dict


class PostmanSyncManager:
    """Manages Postman collection synchronization and testing"""

    def __init__(self):
        """Initialize Postman sync manager"""
        self.config_dir = Path('/home/user/Private-Claude/config')
        self.scripts_dir = Path('/home/user/Private-Claude/scripts')
        self.logs_dir = Path('/home/user/Private-Claude/logs')
        self.test_results_dir = Path('/home/user/Private-Claude/test-results')

        # Create directories if they don't exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.test_results_dir.mkdir(parents=True, exist_ok=True)

        self.postman_api_base = "https://api.getpostman.com"
        self.postman_api_key = os.getenv('POSTMAN_API_KEY')
        self.workspace_id = os.getenv('POSTMAN_WORKSPACE_ID')

        logger.info("Postman Sync Manager initialized")

    def load_collection(self, collection_path: str) -> Dict:
        """Load Postman collection from file"""
        try:
            with open(collection_path, 'r') as f:
                collection = json.load(f)
            logger.info(f"Loaded collection from {collection_path}")
            return collection
        except FileNotFoundError:
            logger.error(f"Collection file not found: {collection_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in collection file: {collection_path}")
            raise

    def load_environment(self, env_path: str) -> Dict:
        """Load Postman environment variables"""
        try:
            with open(env_path, 'r') as f:
                environment = json.load(f)
            logger.info(f"Loaded environment from {env_path}")
            return environment
        except FileNotFoundError:
            logger.warning(f"Environment file not found: {env_path}, creating new one")
            return self._create_default_environment()
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in environment file: {env_path}")
            raise

    def _create_default_environment(self) -> Dict:
        """Create a default Postman environment"""
        return {
            "name": "Private-Claude Environment",
            "values": [
                {"key": "base_url", "value": "http://localhost:5000", "enabled": True},
                {"key": "E2B_API_KEY", "value": os.getenv('E2B_API_KEY', ''), "enabled": True},
                {"key": "GITHUB_TOKEN", "value": os.getenv('GITHUB_TOKEN', ''), "enabled": True},
                {"key": "SLACK_BOT_TOKEN", "value": os.getenv('SLACK_BOT_TOKEN', ''), "enabled": True},
                {"key": "GEMINI_API_KEY", "value": os.getenv('GEMINI_API_KEY', ''), "enabled": True},
                {"key": "ZAPIER_WEBHOOK_URL", "value": os.getenv('ZAPIER_WEBHOOK_URL', ''), "enabled": True},
                {"key": "DROPBOX_ACCESS_TOKEN", "value": os.getenv('DROPBOX_ACCESS_TOKEN', ''), "enabled": True},
                {"key": "MICROSOFT_GRAPH_TOKEN", "value": os.getenv('MICROSOFT_GRAPH_TOKEN', ''), "enabled": True},
                {"key": "SENDGRID_API_KEY", "value": os.getenv('SENDGRID_API_KEY', ''), "enabled": True},
            ]
        }

    def sync_to_postman(self, collection: Dict) -> Tuple[bool, str]:
        """Sync collection to Postman via API"""
        if not self.postman_api_key:
            logger.warning("POSTMAN_API_KEY not set, skipping Postman sync")
            return False, "POSTMAN_API_KEY not configured"

        try:
            headers = {
                "X-API-Key": self.postman_api_key,
                "Content-Type": "application/json"
            }

            # Create or update collection
            payload = {"collection": collection}

            # Check if collection exists
            collection_name = collection.get('info', {}).get('name')
            existing_id = self._find_collection_id(collection_name)

            if existing_id:
                # Update existing collection
                url = f"{self.postman_api_base}/collections/{existing_id}"
                response = requests.put(url, json=payload, headers=headers)
                if response.status_code == 200:
                    logger.info(f"Updated collection {collection_name} in Postman")
                    return True, f"Collection {collection_name} updated successfully"
                else:
                    logger.error(f"Failed to update collection: {response.text}")
                    return False, f"Update failed: {response.text}"
            else:
                # Create new collection
                url = f"{self.postman_api_base}/collections"
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 201:
                    logger.info(f"Created new collection {collection_name} in Postman")
                    return True, f"Collection {collection_name} created successfully"
                else:
                    logger.error(f"Failed to create collection: {response.text}")
                    return False, f"Creation failed: {response.text}"

        except Exception as e:
            logger.error(f"Error syncing to Postman: {str(e)}")
            return False, str(e)

    def _find_collection_id(self, collection_name: str) -> Optional[str]:
        """Find collection ID by name"""
        if not self.postman_api_key:
            return None

        try:
            headers = {"X-API-Key": self.postman_api_key}
            url = f"{self.postman_api_base}/collections"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                collections = response.json().get('collections', [])
                for collection in collections:
                    if collection.get('name') == collection_name:
                        return collection.get('id')
            return None
        except Exception as e:
            logger.error(f"Error finding collection: {str(e)}")
            return None

    def run_newman_tests(self, collection_path: str, environment_path: Optional[str] = None,
                        reporters: Optional[List[str]] = None) -> Tuple[bool, Dict]:
        """Run Newman tests on collection"""
        if reporters is None:
            reporters = ['cli', 'json', 'html']

        try:
            # Build Newman command
            cmd = ['newman', 'run', collection_path]

            # Add environment if provided
            if environment_path:
                cmd.extend(['-e', environment_path])

            # Add reporters
            report_name = f"postman_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            for reporter in reporters:
                if reporter == 'json':
                    cmd.extend(['--reporter', 'json', '--reporter-json-export',
                               f'{self.test_results_dir}/{report_name}.json'])
                elif reporter == 'html':
                    cmd.extend(['--reporter', 'html', '--reporter-html-export',
                               f'{self.test_results_dir}/{report_name}.html'])
                elif reporter == 'cli':
                    cmd.extend(['--reporter', 'cli'])

            # Add other options
            cmd.extend([
                '--bail',  # Stop on first request error
                '--timeout-request', '5000',  # 5 second timeout per request
                '--timeout', '30000'  # 30 second overall timeout
            ])

            logger.info(f"Running Newman tests: {' '.join(cmd)}")

            # Run Newman
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("Newman tests passed")
                return True, {
                    "status": "passed",
                    "message": "All tests passed",
                    "report_name": report_name,
                    "output": result.stdout
                }
            else:
                logger.error(f"Newman tests failed: {result.stderr}")
                return False, {
                    "status": "failed",
                    "message": "Some tests failed",
                    "report_name": report_name,
                    "output": result.stdout,
                    "error": result.stderr
                }

        except FileNotFoundError:
            logger.error("Newman CLI not found. Install with: npm install -g newman")
            return False, {
                "status": "error",
                "message": "Newman CLI not installed",
                "suggestion": "npm install -g newman"
            }
        except Exception as e:
            logger.error(f"Error running Newman tests: {str(e)}")
            return False, {
                "status": "error",
                "message": str(e)
            }

    def update_environment_variables(self, environment_path: str, env_vars: Dict) -> bool:
        """Update environment variables from current environment"""
        try:
            environment = self.load_environment(environment_path)

            # Update existing variables or add new ones
            for key, value in env_vars.items():
                found = False
                for var in environment.get('values', []):
                    if var.get('key') == key:
                        var['value'] = value
                        found = True
                        break

                if not found:
                    environment['values'].append({
                        'key': key,
                        'value': value,
                        'enabled': True
                    })

            # Save updated environment
            with open(environment_path, 'w') as f:
                json.dump(environment, f, indent=2)

            logger.info(f"Updated environment variables in {environment_path}")
            return True

        except Exception as e:
            logger.error(f"Error updating environment variables: {str(e)}")
            return False

    def generate_test_report(self, test_results: Dict) -> str:
        """Generate a test report from results"""
        try:
            report_path = self.test_results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            report = {
                "timestamp": datetime.now().isoformat(),
                "results": test_results,
                "summary": {
                    "total_tests": len(test_results),
                    "passed": sum(1 for r in test_results if r.get('status') == 'passed'),
                    "failed": sum(1 for r in test_results if r.get('status') == 'failed'),
                }
            }

            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Generated test report: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"Error generating test report: {str(e)}")
            return ""

    def validate_collection(self, collection: Dict) -> Tuple[bool, List[str]]:
        """Validate Postman collection structure"""
        errors = []

        # Check required fields
        if 'info' not in collection:
            errors.append("Missing 'info' field in collection")

        if 'item' not in collection:
            errors.append("Missing 'item' field in collection")

        # Check items
        items = collection.get('item', [])
        if not isinstance(items, list):
            errors.append("'item' field must be a list")

        # Check each request
        for idx, item in enumerate(items):
            if isinstance(item, dict):
                if 'item' in item:
                    # It's a folder
                    for sub_idx, sub_item in enumerate(item.get('item', [])):
                        if 'request' in sub_item:
                            if 'url' not in sub_item['request']:
                                errors.append(f"Request at [{idx}][{sub_idx}] missing 'url' field")
                elif 'request' in item:
                    # It's a request
                    if 'url' not in item['request']:
                        errors.append(f"Request at [{idx}] missing 'url' field")

        if errors:
            logger.error(f"Collection validation failed with {len(errors)} errors")
            return False, errors

        logger.info("Collection validation passed")
        return True, []

    def sync_all_apis(self):
        """Sync all API configurations"""
        logger.info("Starting complete API synchronization")

        collection_path = str(self.config_dir / 'postman_complete_collection.json')
        environment_path = str(self.config_dir / 'postman_environment.json')

        try:
            # Load collection
            collection = self.load_collection(collection_path)

            # Validate collection
            is_valid, errors = self.validate_collection(collection)
            if not is_valid:
                logger.error(f"Collection validation failed: {errors}")
                return False

            # Update environment variables from OS environment
            env_vars = {
                'E2B_API_KEY': os.getenv('E2B_API_KEY', ''),
                'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN', ''),
                'GITLAB_TOKEN': os.getenv('GITLAB_TOKEN', ''),
                'SLACK_BOT_TOKEN': os.getenv('SLACK_BOT_TOKEN', ''),
                'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
                'ZAPIER_WEBHOOK_URL': os.getenv('ZAPIER_WEBHOOK_URL', ''),
                'DROPBOX_ACCESS_TOKEN': os.getenv('DROPBOX_ACCESS_TOKEN', ''),
                'GOOGLE_SHEETS_API_KEY': os.getenv('GOOGLE_SHEETS_API_KEY', ''),
                'MICROSOFT_GRAPH_TOKEN': os.getenv('MICROSOFT_GRAPH_TOKEN', ''),
                'SENDGRID_API_KEY': os.getenv('SENDGRID_API_KEY', ''),
            }

            # Save environment
            self.update_environment_variables(environment_path, env_vars)

            # Sync to Postman
            success, message = self.sync_to_postman(collection)
            logger.info(f"Postman sync: {message}")

            # Run tests
            logger.info("Running Newman tests")
            test_success, test_results = self.run_newman_tests(
                collection_path,
                environment_path,
                reporters=['cli', 'json']
            )

            if test_success:
                logger.info("All tests passed successfully")
            else:
                logger.warning(f"Some tests failed: {test_results}")

            return success and test_success

        except Exception as e:
            logger.error(f"Error in sync_all_apis: {str(e)}")
            return False


def main():
    """Main entry point"""
    manager = PostmanSyncManager()

    # Parse arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'sync':
            success = manager.sync_all_apis()
            sys.exit(0 if success else 1)

        elif command == 'test':
            collection_path = str(Path('/home/user/Private-Claude/config/postman_complete_collection.json'))
            environment_path = str(Path('/home/user/Private-Claude/config/postman_environment.json'))
            success, results = manager.run_newman_tests(collection_path, environment_path)
            print(json.dumps(results, indent=2))
            sys.exit(0 if success else 1)

        elif command == 'validate':
            collection = manager.load_collection(
                str(Path('/home/user/Private-Claude/config/postman_complete_collection.json'))
            )
            is_valid, errors = manager.validate_collection(collection)
            if is_valid:
                print("Collection is valid")
            else:
                print("Collection validation errors:")
                for error in errors:
                    print(f"  - {error}")
            sys.exit(0 if is_valid else 1)

        else:
            print(f"Unknown command: {command}")
            print("Usage: python postman_sync.py [sync|test|validate]")
            sys.exit(1)

    else:
        # Default: sync all APIs
        success = manager.sync_all_apis()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
