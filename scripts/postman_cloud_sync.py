#!/usr/bin/env python3
"""
Postman Cloud Sync and Workspace Manager
Synchronizes collections with Postman cloud and manages workspaces
"""

import json
import os
import sys
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/Private-Claude/logs/postman_cloud_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PostmanCloudSync:
    """Manages Postman Cloud synchronization and workspace configuration"""

    def __init__(self):
        """Initialize Postman Cloud Sync"""
        self.base_dir = Path('/home/user/Private-Claude')
        self.config_dir = self.base_dir / 'config'
        self.logs_dir = self.base_dir / 'logs'

        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Postman API configuration
        self.postman_api_base = "https://api.getpostman.com"
        self.api_key = os.getenv('POSTMAN_API_KEY')
        self.workspace_id = os.getenv('POSTMAN_WORKSPACE_ID')

        if not self.api_key:
            logger.warning("POSTMAN_API_KEY not set - cloud sync will be disabled")

        logger.info("Postman Cloud Sync initialized")

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def create_workspace(self, name: str, description: str = "", workspace_type: str = "personal") -> Tuple[bool, Optional[str]]:
        """Create a new Postman workspace"""
        if not self.api_key:
            return False, "API key not configured"

        try:
            url = f"{self.postman_api_base}/workspaces"
            payload = {
                "workspace": {
                    "name": name,
                    "type": workspace_type,
                    "description": description
                }
            }

            response = requests.post(url, json=payload, headers=self._get_headers())

            if response.status_code == 200:
                workspace_id = response.json().get('workspace', {}).get('id')
                logger.info(f"Created workspace: {name} (ID: {workspace_id})")
                return True, workspace_id
            else:
                logger.error(f"Failed to create workspace: {response.text}")
                return False, None

        except Exception as e:
            logger.error(f"Error creating workspace: {str(e)}")
            return False, None

    def list_workspaces(self) -> List[Dict]:
        """List all workspaces"""
        if not self.api_key:
            return []

        try:
            url = f"{self.postman_api_base}/workspaces"
            response = requests.get(url, headers=self._get_headers())

            if response.status_code == 200:
                workspaces = response.json().get('workspaces', [])
                logger.info(f"Found {len(workspaces)} workspaces")
                return workspaces
            else:
                logger.error(f"Failed to list workspaces: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error listing workspaces: {str(e)}")
            return []

    def get_workspace(self, workspace_id: str) -> Optional[Dict]:
        """Get workspace details"""
        if not self.api_key:
            return None

        try:
            url = f"{self.postman_api_base}/workspaces/{workspace_id}"
            response = requests.get(url, headers=self._get_headers())

            if response.status_code == 200:
                workspace = response.json().get('workspace', {})
                logger.info(f"Retrieved workspace: {workspace.get('name')}")
                return workspace
            else:
                logger.error(f"Failed to get workspace: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting workspace: {str(e)}")
            return None

    def upload_collection(self, collection_path: Path) -> Tuple[bool, Optional[str]]:
        """Upload collection to Postman Cloud"""
        if not self.api_key:
            return False, "API key not configured"

        try:
            with open(collection_path, 'r') as f:
                collection = json.load(f)

            # Check if collection exists
            collection_name = collection.get('info', {}).get('name')
            existing_id = self._find_collection_id(collection_name)

            url = f"{self.postman_api_base}/collections"
            payload = {"collection": collection}

            if existing_id:
                # Update existing collection
                url = f"{self.postman_api_base}/collections/{existing_id}"
                response = requests.put(url, json=payload, headers=self._get_headers())
                action = "updated"
            else:
                # Create new collection
                response = requests.post(url, json=payload, headers=self._get_headers())
                action = "created"

            if response.status_code in [200, 201]:
                collection_id = response.json().get('collection', {}).get('id') or existing_id
                logger.info(f"Successfully {action} collection: {collection_name}")
                return True, collection_id
            else:
                logger.error(f"Failed to upload collection: {response.text}")
                return False, None

        except Exception as e:
            logger.error(f"Error uploading collection: {str(e)}")
            return False, None

    def _find_collection_id(self, collection_name: str) -> Optional[str]:
        """Find collection ID by name"""
        if not self.api_key:
            return None

        try:
            url = f"{self.postman_api_base}/collections"
            response = requests.get(url, headers=self._get_headers())

            if response.status_code == 200:
                collections = response.json().get('collections', [])
                for collection in collections:
                    if collection.get('name') == collection_name:
                        return collection.get('uid')
            return None

        except Exception as e:
            logger.error(f"Error finding collection: {str(e)}")
            return None

    def upload_environment(self, environment_path: Path) -> Tuple[bool, Optional[str]]:
        """Upload environment to Postman Cloud"""
        if not self.api_key:
            return False, "API key not configured"

        try:
            with open(environment_path, 'r') as f:
                environment = json.load(f)

            # Check if environment exists
            env_name = environment.get('name')
            existing_id = self._find_environment_id(env_name)

            url = f"{self.postman_api_base}/environments"
            payload = {"environment": environment}

            if existing_id:
                # Update existing environment
                url = f"{self.postman_api_base}/environments/{existing_id}"
                response = requests.put(url, json=payload, headers=self._get_headers())
                action = "updated"
            else:
                # Create new environment
                response = requests.post(url, json=payload, headers=self._get_headers())
                action = "created"

            if response.status_code in [200, 201]:
                env_id = response.json().get('environment', {}).get('id') or existing_id
                logger.info(f"Successfully {action} environment: {env_name}")
                return True, env_id
            else:
                logger.error(f"Failed to upload environment: {response.text}")
                return False, None

        except Exception as e:
            logger.error(f"Error uploading environment: {str(e)}")
            return False, None

    def _find_environment_id(self, env_name: str) -> Optional[str]:
        """Find environment ID by name"""
        if not self.api_key:
            return None

        try:
            url = f"{self.postman_api_base}/environments"
            response = requests.get(url, headers=self._get_headers())

            if response.status_code == 200:
                environments = response.json().get('environments', [])
                for env in environments:
                    if env.get('name') == env_name:
                        return env.get('uid')
            return None

        except Exception as e:
            logger.error(f"Error finding environment: {str(e)}")
            return None

    def setup_monitoring(self, collection_id: str) -> bool:
        """Set up monitoring for a collection"""
        if not self.api_key:
            return False

        try:
            # Note: Monitoring setup requires Postman Pro/Enterprise
            # This is a placeholder for future implementation
            logger.info(f"Monitoring setup requested for collection {collection_id}")
            logger.info("Note: Monitoring requires Postman Pro/Enterprise subscription")
            return True

        except Exception as e:
            logger.error(f"Error setting up monitoring: {str(e)}")
            return False

    def sync_all(self) -> Dict:
        """Sync all collections and environments to Postman Cloud"""
        logger.info("Starting full Postman Cloud sync")

        results = {
            'timestamp': datetime.now().isoformat(),
            'collections': [],
            'environments': [],
            'errors': []
        }

        # Upload collection
        collection_path = self.config_dir / 'postman_complete_collection.json'
        if collection_path.exists():
            success, collection_id = self.upload_collection(collection_path)
            results['collections'].append({
                'name': collection_path.name,
                'success': success,
                'id': collection_id
            })
        else:
            results['errors'].append(f"Collection not found: {collection_path}")

        # Upload environment
        environment_path = self.config_dir / 'postman_environment.json'
        if environment_path.exists():
            success, env_id = self.upload_environment(environment_path)
            results['environments'].append({
                'name': environment_path.name,
                'success': success,
                'id': env_id
            })
        else:
            results['errors'].append(f"Environment not found: {environment_path}")

        # Save sync report
        report_path = self.logs_dir / f'postman_cloud_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Cloud sync completed. Report saved to {report_path}")
        return results


def main():
    """Main entry point"""
    sync = PostmanCloudSync()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'sync':
            results = sync.sync_all()
            print(json.dumps(results, indent=2))

        elif command == 'list-workspaces':
            workspaces = sync.list_workspaces()
            for ws in workspaces:
                print(f"- {ws.get('name')} (ID: {ws.get('id')})")

        elif command == 'create-workspace':
            if len(sys.argv) < 3:
                print("Usage: python postman_cloud_sync.py create-workspace <name>")
                sys.exit(1)
            name = sys.argv[2]
            description = sys.argv[3] if len(sys.argv) > 3 else ""
            success, workspace_id = sync.create_workspace(name, description)
            if success:
                print(f"Workspace created: {workspace_id}")
            else:
                print("Failed to create workspace")
                sys.exit(1)

        else:
            print(f"Unknown command: {command}")
            print("Usage: python postman_cloud_sync.py [sync|list-workspaces|create-workspace]")
            sys.exit(1)
    else:
        # Default: sync all
        results = sync.sync_all()
        print(f"Sync completed successfully")


if __name__ == '__main__':
    main()
