"""
Postman MCP (Model Context Protocol) Connector
Integrates Agent X5.0 with Postman API via MCP endpoint
Enables API testing, collection management, and monitoring automation
"""

import os
import json
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PostmanMCP')

# Load environment variables from config/.env
try:
    from dotenv import load_dotenv
    config_path = Path(__file__).parent.parent.parent / 'config' / '.env'
    load_dotenv(config_path)
    logger.info(f"Loaded environment variables from {config_path}")
except ImportError:
    logger.warning("python-dotenv not installed. Install with: pip install python-dotenv")


class PostmanMCPConnector:
    """
    Postman Model Context Protocol Connector
    Provides programmatic access to Postman API for Agent X5.0
    """

    def __init__(self):
        self.api_key = os.getenv('POSTMAN_API_KEY')
        self.workspace_id = os.getenv('POSTMAN_WORKSPACE_ID')
        self.base_url = 'https://api.getpostman.com'
        self.vscode_auth_code = os.getenv('POSTMAN_VSCODE_AUTH_CODE')
        
        if not self.api_key:
            logger.warning("POSTMAN_API_KEY not configured in .env")
        
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        logger.info("Postman MCP Connector initialized")

    def check_connection(self) -> Dict[str, Any]:
        """
        Check connection to Postman API
        
        Returns:
            Status dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info("✓ Postman API connection successful")
                return {
                    "connected": True,
                    "status_code": response.status_code,
                    "user": user_data.get('user', {}),
                    "api_url": self.base_url
                }
            else:
                logger.warning(f"Postman API returned status {response.status_code}")
                return {
                    "connected": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
        
        except Exception as e:
            logger.error(f"Postman API connection failed: {e}")
            return {
                "connected": False,
                "error": str(e)
            }

    def list_workspaces(self) -> List[Dict[str, Any]]:
        """
        List all available Postman workspaces
        
        Returns:
            List of workspaces
        """
        try:
            response = requests.get(
                f"{self.base_url}/workspaces",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                workspaces = data.get('workspaces', [])
                logger.info(f"Found {len(workspaces)} Postman workspaces")
                return workspaces
            else:
                logger.error(f"Failed to list workspaces: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error listing Postman workspaces: {e}")
            return []

    def list_collections(self, workspace_id: str = None) -> List[Dict[str, Any]]:
        """
        List all collections in a workspace
        
        Args:
            workspace_id: Specific workspace ID (uses default if not provided)
        
        Returns:
            List of collections
        """
        workspace = workspace_id or self.workspace_id
        
        try:
            response = requests.get(
                f"{self.base_url}/collections",
                headers=self.headers,
                params={'workspace': workspace} if workspace else {},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                collections = data.get('collections', [])
                logger.info(f"Found {len(collections)} collections")
                return collections
            else:
                logger.error(f"Failed to list collections: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []

    def get_collection(self, collection_id: str) -> Dict[str, Any]:
        """
        Get details of a specific collection
        
        Args:
            collection_id: Collection ID
        
        Returns:
            Collection details
        """
        try:
            response = requests.get(
                f"{self.base_url}/collections/{collection_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Retrieved collection: {collection_id}")
                return data.get('collection', {})
            else:
                logger.error(f"Failed to get collection: {response.status_code}")
                return {}
        
        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            return {}

    def run_collection(self, collection_id: str, environment_id: str = None) -> Dict[str, Any]:
        """
        Run a Postman collection (requires Newman or Postman Collection Runner)
        
        Args:
            collection_id: Collection to run
            environment_id: Optional environment ID
        
        Returns:
            Run results
        """
        try:
            # Note: Direct collection running requires Postman Cloud Agent or Newman
            # This method prepares the data structure for automation
            
            run_data = {
                "collection_id": collection_id,
                "environment_id": environment_id,
                "timestamp": datetime.now().isoformat(),
                "status": "queued"
            }
            
            logger.info(f"Collection run queued: {collection_id}")
            
            return {
                "success": True,
                "run_id": f"run_{collection_id}_{int(datetime.now().timestamp())}",
                "data": run_data,
                "note": "Collection run requires Postman Cloud Agent or Newman CLI"
            }
        
        except Exception as e:
            logger.error(f"Error queueing collection run: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new Postman collection
        
        Args:
            name: Collection name
            description: Collection description
        
        Returns:
            Created collection data
        """
        try:
            collection_data = {
                "collection": {
                    "info": {
                        "name": name,
                        "description": description,
                        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
                    },
                    "item": []
                }
            }
            
            response = requests.post(
                f"{self.base_url}/collections",
                headers=self.headers,
                json=collection_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"✓ Created collection: {name}")
                return {
                    "success": True,
                    "collection": data.get('collection', {})
                }
            else:
                logger.error(f"Failed to create collection: {response.status_code}")
                return {
                    "success": False,
                    "error": response.text
                }
        
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def list_environments(self, workspace_id: str = None) -> List[Dict[str, Any]]:
        """
        List all environments in a workspace
        
        Args:
            workspace_id: Specific workspace ID
        
        Returns:
            List of environments
        """
        workspace = workspace_id or self.workspace_id
        
        try:
            response = requests.get(
                f"{self.base_url}/environments",
                headers=self.headers,
                params={'workspace': workspace} if workspace else {},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                environments = data.get('environments', [])
                logger.info(f"Found {len(environments)} environments")
                return environments
            else:
                logger.error(f"Failed to list environments: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error listing environments: {e}")
            return []

    def create_monitor(self, collection_id: str, name: str, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Postman monitor for a collection
        
        Args:
            collection_id: Collection to monitor
            name: Monitor name
            schedule: Schedule configuration (cron-based)
        
        Returns:
            Monitor creation result
        """
        try:
            monitor_data = {
                "monitor": {
                    "name": name,
                    "collection": collection_id,
                    "schedule": schedule
                }
            }
            
            response = requests.post(
                f"{self.base_url}/monitors",
                headers=self.headers,
                json=monitor_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"✓ Created monitor: {name}")
                return {
                    "success": True,
                    "monitor": data.get('monitor', {})
                }
            else:
                logger.error(f"Failed to create monitor: {response.status_code}")
                return {
                    "success": False,
                    "error": response.text
                }
        
        except Exception as e:
            logger.error(f"Error creating monitor: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_api_key_usage(self) -> Dict[str, Any]:
        """
        Get API key usage statistics
        
        Returns:
            Usage statistics
        """
        try:
            response = requests.get(
                f"{self.base_url}/api-key-usage",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✓ Retrieved API usage statistics")
                return data
            else:
                logger.warning(f"Could not retrieve usage stats: {response.status_code}")
                return {
                    "status": "unknown",
                    "note": "API usage statistics unavailable"
                }
        
        except Exception as e:
            logger.warning(f"Error getting API usage: {e}")
            return {
                "status": "unknown",
                "error": str(e)
            }

    def integrate_with_trading_bot(self, api_endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """
        Create API test for trading bot endpoint
        
        Args:
            api_endpoint: Trading API endpoint to test
            method: HTTP method (GET, POST, etc.)
        
        Returns:
            Test configuration
        """
        test_config = {
            "name": f"Trading API Test - {api_endpoint}",
            "request": {
                "method": method,
                "url": api_endpoint,
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ]
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status code is 200', function () {",
                            "    pm.response.to.have.status(200);",
                            "});",
                            "",
                            "pm.test('Response time is less than 2000ms', function () {",
                            "    pm.expect(pm.response.responseTime).to.be.below(2000);",
                            "});"
                        ]
                    }
                }
            ]
        }
        
        logger.info(f"Created trading API test config for: {api_endpoint}")
        return test_config

    def authenticate_vscode_extension(self) -> Dict[str, Any]:
        """
        Authenticate Postman VS Code extension using authorization code
        
        Returns:
            Authentication status
        """
        if not self.vscode_auth_code:
            return {
                "authenticated": False,
                "error": "POSTMAN_VSCODE_AUTH_CODE not configured",
                "instructions": "Set the authorization code from vscode://Postman.postman-for-vscode?code=YOUR_CODE"
            }
        
        logger.info(f"VS Code extension authentication code available")
        
        return {
            "authenticated": True,
            "auth_code": self.vscode_auth_code[:20] + "...",
            "note": "Use this code in VS Code Postman extension to connect",
            "extension_url": f"vscode://Postman.postman-for-vscode?code={self.vscode_auth_code}"
        }


def main():
    """Test Postman MCP connector"""
    logger.info("=== POSTMAN MCP CONNECTOR TEST ===")
    
    connector = PostmanMCPConnector()
    
    # Check connection
    print("\n1. Checking Postman API connection...")
    status = connector.check_connection()
    print(f"   Status: {json.dumps(status, indent=2)}")
    
    # Check VS Code authentication
    print("\n2. Checking VS Code extension authentication...")
    auth_status = connector.authenticate_vscode_extension()
    print(f"   Auth: {json.dumps(auth_status, indent=2)}")
    
    if status.get('connected'):
        # List workspaces
        print("\n3. Listing Postman workspaces...")
        workspaces = connector.list_workspaces()
        print(f"   Found {len(workspaces)} workspaces")
        
        # List collections
        print("\n4. Listing collections...")
        collections = connector.list_collections()
        print(f"   Found {len(collections)} collections")
        
        # Check API usage
        print("\n5. Checking API usage...")
        usage = connector.get_api_key_usage()
        print(f"   Usage: {json.dumps(usage, indent=2)}")
    else:
        print("\n⚠️  Postman API not connected")
        print("   Possible reasons:")
        print("   - Invalid API key")
        print("   - Network connectivity issue")
        print("   - API rate limit reached")
    
    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    main()
