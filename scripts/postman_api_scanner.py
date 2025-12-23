#!/usr/bin/env python3
"""
Postman API Auto-Discovery and Collection Generator
Scans codebase for API endpoints and automatically generates Postman requests
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/Private-Claude/logs/postman_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class APIEndpoint:
    """Data class for discovered API endpoints"""
    url: str
    method: str
    service: str
    description: str = ""
    headers: Dict[str, str] = None
    body: Optional[str] = None
    auth_type: str = "bearer"
    auth_token_var: str = ""

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


class PostmanAPIScanner:
    """Scans codebase for API endpoints and generates Postman collection"""

    def __init__(self):
        """Initialize API scanner"""
        self.base_dir = Path('/home/user/Private-Claude')
        self.config_dir = self.base_dir / 'config'
        self.scripts_dir = self.base_dir / 'scripts'
        self.logs_dir = self.base_dir / 'logs'

        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.discovered_endpoints: List[APIEndpoint] = []
        self.api_keys: Dict[str, str] = {}
        self.base_urls: Dict[str, str] = {}

        logger.info("Postman API Scanner initialized")

    def load_env_file(self, env_path: Path) -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_vars = {}
        try:
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
                logger.info(f"Loaded {len(env_vars)} environment variables from {env_path}")
        except Exception as e:
            logger.error(f"Error loading .env file: {str(e)}")
        return env_vars

    def scan_config_files(self):
        """Scan all config files for API endpoints"""
        logger.info("Scanning config files for API endpoints")

        # Load environment variables
        env_file = self.config_dir / '.env'
        self.api_keys = self.load_env_file(env_file)

        # Extract base URLs from common services
        self.base_urls = {
            'e2b': 'https://api.e2b.dev',
            'github': 'https://api.github.com',
            'gitlab': 'https://gitlab.com/api/v4',
            'slack': 'https://slack.com/api',
            'zapier': self.api_keys.get('ZAPIER_WEBHOOK_URL', ''),
            'kraken': 'https://api.kraken.com',
            'google_gmail': 'https://gmail.googleapis.com',
            'google_drive': 'https://www.googleapis.com/drive',
            'google_sheets': 'https://sheets.googleapis.com',
            'google_docs': 'https://docs.googleapis.com',
            'google_calendar': 'https://www.googleapis.com/calendar',
            'microsoft_graph': 'https://graph.microsoft.com/v1.0',
            'dropbox': 'https://api.dropboxapi.com',
            'sendgrid': 'https://api.sendgrid.com',
            'gemini': 'https://generativelanguage.googleapis.com',
            'sam_gov': 'https://api.sam.gov/prod/opportunities/v2'
        }

        # Scan JSON config files
        for config_file in self.config_dir.rglob('*.json'):
            self._scan_json_config(config_file)

    def _scan_json_config(self, config_path: Path):
        """Scan a JSON config file for API endpoints"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Recursively search for API endpoints in config
            self._extract_endpoints_from_dict(config, config_path.stem)

        except Exception as e:
            logger.debug(f"Error scanning {config_path}: {str(e)}")

    def _extract_endpoints_from_dict(self, data: dict, service: str, parent_key: str = ""):
        """Recursively extract API endpoints from nested dictionaries"""
        if not isinstance(data, dict):
            return

        for key, value in data.items():
            current_key = f"{parent_key}.{key}" if parent_key else key

            # Check if this looks like an API endpoint configuration
            if isinstance(value, dict):
                # Check for common API endpoint patterns
                if 'url' in value or 'endpoint' in value or 'api_endpoint' in value:
                    url = value.get('url') or value.get('endpoint') or value.get('api_endpoint')
                    method = value.get('method', 'GET')
                    description = value.get('description', '') or value.get('name', '')

                    if url and isinstance(url, str):
                        endpoint = APIEndpoint(
                            url=url,
                            method=method,
                            service=service,
                            description=description or current_key
                        )
                        self.discovered_endpoints.append(endpoint)

                # Recurse into nested dictionaries
                self._extract_endpoints_from_dict(value, service, current_key)

            elif isinstance(value, list):
                # Handle lists of endpoint configurations
                for item in value:
                    if isinstance(item, dict):
                        self._extract_endpoints_from_dict(item, service, current_key)

    def scan_python_files(self):
        """Scan Python files for API calls"""
        logger.info("Scanning Python files for API calls")

        # Common API call patterns
        patterns = [
            r'requests\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
            r'\.api\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
            r'requests\.(get|post|put|delete|patch)\(f[\'"]([^\'"]+)[\'"]',
            r'requests\.(get|post|put|delete|patch)\(url=f?[\'"]([^\'"]+)[\'"]',
        ]

        for py_file in self.base_dir.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        method = match.group(1).upper()
                        url = match.group(2)

                        # Skip if URL is a variable or placeholder
                        if not url.startswith('http') and '{' not in url:
                            continue

                        # Determine service from URL
                        service = self._determine_service_from_url(url)

                        endpoint = APIEndpoint(
                            url=url,
                            method=method,
                            service=service,
                            description=f"Found in {py_file.name}"
                        )
                        self.discovered_endpoints.append(endpoint)

            except Exception as e:
                logger.debug(f"Error scanning {py_file}: {str(e)}")

    def _determine_service_from_url(self, url: str) -> str:
        """Determine service name from URL"""
        url_lower = url.lower()

        service_patterns = {
            'e2b.dev': 'e2b',
            'github.com': 'github',
            'gitlab.com': 'gitlab',
            'slack.com': 'slack',
            'zapier.com': 'zapier',
            'kraken.com': 'kraken',
            'googleapis.com': 'google',
            'microsoft.com': 'microsoft',
            'dropbox': 'dropbox',
            'sendgrid': 'sendgrid',
            'sam.gov': 'sam_gov'
        }

        for pattern, service in service_patterns.items():
            if pattern in url_lower:
                return service

        return 'unknown'

    def generate_postman_requests(self) -> List[Dict]:
        """Generate Postman request objects from discovered endpoints"""
        logger.info(f"Generating Postman requests from {len(self.discovered_endpoints)} discovered endpoints")

        # Group endpoints by service
        endpoints_by_service: Dict[str, List[APIEndpoint]] = {}
        for endpoint in self.discovered_endpoints:
            if endpoint.service not in endpoints_by_service:
                endpoints_by_service[endpoint.service] = []
            endpoints_by_service[endpoint.service].append(endpoint)

        # Remove duplicates within each service
        for service in endpoints_by_service:
            seen = set()
            unique = []
            for ep in endpoints_by_service[service]:
                key = (ep.url, ep.method)
                if key not in seen:
                    seen.add(key)
                    unique.append(ep)
            endpoints_by_service[service] = unique

        # Generate Postman folder structure
        postman_items = []

        for service, endpoints in sorted(endpoints_by_service.items()):
            if not endpoints:
                continue

            service_folder = {
                "name": f"{service.title()} API (Auto-discovered)",
                "item": []
            }

            for endpoint in endpoints:
                request = self._create_postman_request(endpoint)
                service_folder["item"].append(request)

            postman_items.append(service_folder)

        return postman_items

    def _create_postman_request(self, endpoint: APIEndpoint) -> Dict:
        """Create a Postman request from an endpoint"""
        # Determine authentication
        auth_header = self._get_auth_header(endpoint.service)

        # Build headers
        headers = [
            {
                "key": "Content-Type",
                "value": "application/json",
                "type": "text"
            }
        ]

        if auth_header:
            headers.append(auth_header)

        # Add any custom headers from endpoint
        for key, value in endpoint.headers.items():
            headers.append({
                "key": key,
                "value": value,
                "type": "text"
            })

        # Build request
        request_obj = {
            "name": endpoint.description or f"{endpoint.method} {endpoint.url}",
            "request": {
                "method": endpoint.method,
                "header": headers,
                "url": {
                    "raw": endpoint.url,
                    "protocol": "https",
                    "host": self._parse_url_host(endpoint.url),
                    "path": self._parse_url_path(endpoint.url)
                }
            },
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": self._generate_test_script(endpoint)
                    }
                }
            ]
        }

        # Add body if it's a POST/PUT/PATCH request
        if endpoint.method in ['POST', 'PUT', 'PATCH'] and endpoint.body:
            request_obj["request"]["body"] = {
                "mode": "raw",
                "raw": endpoint.body
            }

        return request_obj

    def _get_auth_header(self, service: str) -> Optional[Dict]:
        """Get authentication header for a service"""
        auth_mapping = {
            'e2b': {'key': 'Authorization', 'value': 'Bearer {{e2b_api_key}}'},
            'github': {'key': 'Authorization', 'value': 'Bearer {{github_token}}'},
            'gitlab': {'key': 'PRIVATE-TOKEN', 'value': '{{gitlab_token}}'},
            'slack': {'key': 'Authorization', 'value': 'Bearer {{slack_bot_token}}'},
            'google': {'key': 'Authorization', 'value': 'Bearer {{google_access_token}}'},
            'microsoft': {'key': 'Authorization', 'value': 'Bearer {{microsoft_graph_token}}'},
            'dropbox': {'key': 'Authorization', 'value': 'Bearer {{dropbox_access_token}}'},
            'sendgrid': {'key': 'Authorization', 'value': 'Bearer {{sendgrid_api_key}}'},
        }

        if service in auth_mapping:
            return {
                "key": auth_mapping[service]['key'],
                "value": auth_mapping[service]['value'],
                "type": "text"
            }

        return None

    def _parse_url_host(self, url: str) -> List[str]:
        """Parse host from URL"""
        try:
            # Remove protocol
            url = re.sub(r'^https?://', '', url)
            # Get host part
            host = url.split('/')[0]
            # Split into parts
            return host.split('.')
        except:
            return ["{{base_url}}"]

    def _parse_url_path(self, url: str) -> List[str]:
        """Parse path from URL"""
        try:
            # Remove protocol
            url = re.sub(r'^https?://', '', url)
            # Get path part
            parts = url.split('/')
            if len(parts) > 1:
                # Remove query string
                path = '/'.join(parts[1:]).split('?')[0]
                return [p for p in path.split('/') if p]
            return []
        except:
            return []

    def _generate_test_script(self, endpoint: APIEndpoint) -> List[str]:
        """Generate test script for an endpoint"""
        scripts = [
            "// Auto-generated test script",
            f"pm.test('Status code is successful', function() {{",
            "    pm.response.to.be.success;",
            "});",
            "",
            "pm.test('Response time is acceptable', function() {",
            "    pm.expect(pm.response.responseTime).to.be.below(5000);",
            "});"
        ]

        if endpoint.method == 'GET':
            scripts.extend([
                "",
                "pm.test('Response has data', function() {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData).to.be.an('object').or.to.be.an('array');",
                "});"
            ])

        elif endpoint.method in ['POST', 'PUT']:
            scripts.extend([
                "",
                "pm.test('Resource created/updated successfully', function() {",
                "    pm.expect([200, 201, 204]).to.include(pm.response.code);",
                "});"
            ])

        return scripts

    def update_postman_collection(self, collection_path: Path, auto_discovered_items: List[Dict]):
        """Update existing Postman collection with auto-discovered endpoints"""
        logger.info(f"Updating Postman collection at {collection_path}")

        try:
            # Load existing collection
            with open(collection_path, 'r') as f:
                collection = json.load(f)

            # Add auto-discovered items to collection
            if 'item' not in collection:
                collection['item'] = []

            # Add a separator folder for auto-discovered APIs
            auto_folder = {
                "name": "Auto-Discovered APIs",
                "description": f"Automatically discovered on {datetime.now().isoformat()}",
                "item": auto_discovered_items
            }

            # Check if auto-discovered folder already exists
            existing_auto_idx = None
            for idx, item in enumerate(collection['item']):
                if item.get('name') == 'Auto-Discovered APIs':
                    existing_auto_idx = idx
                    break

            if existing_auto_idx is not None:
                # Update existing auto-discovered section
                collection['item'][existing_auto_idx] = auto_folder
            else:
                # Add new section
                collection['item'].append(auto_folder)

            # Update collection metadata
            if 'info' in collection:
                collection['info']['_updated_at'] = datetime.now().isoformat()

            # Save updated collection
            with open(collection_path, 'w') as f:
                json.dump(collection, f, indent=2)

            logger.info(f"Updated collection saved to {collection_path}")
            return True

        except Exception as e:
            logger.error(f"Error updating Postman collection: {str(e)}")
            return False

    def generate_environment_file(self, output_path: Path):
        """Generate Postman environment file with discovered API keys"""
        logger.info("Generating Postman environment file")

        environment = {
            "id": "private-claude-environment",
            "name": "Private-Claude Environment",
            "values": [],
            "_postman_variable_scope": "environment",
            "_postman_exported_at": datetime.now().isoformat(),
            "_postman_exported_using": "Postman API Scanner"
        }

        # Add environment variables from .env file
        for key, value in self.api_keys.items():
            # Skip sensitive full values, use placeholders
            display_value = value if len(value) < 20 else f"{value[:10]}..."

            environment['values'].append({
                "key": key,
                "value": value,
                "type": "default",
                "enabled": True
            })

        # Add base URLs
        for service, url in self.base_urls.items():
            environment['values'].append({
                "key": f"{service}_base_url",
                "value": url,
                "type": "default",
                "enabled": True
            })

        # Save environment file
        with open(output_path, 'w') as f:
            json.dump(environment, f, indent=2)

        logger.info(f"Environment file saved to {output_path}")
        return True

    def generate_scan_report(self, output_path: Path):
        """Generate a scan report with statistics"""
        logger.info("Generating scan report")

        # Group endpoints by service
        endpoints_by_service = {}
        for endpoint in self.discovered_endpoints:
            if endpoint.service not in endpoints_by_service:
                endpoints_by_service[endpoint.service] = []
            endpoints_by_service[endpoint.service].append(endpoint)

        # Calculate statistics
        stats = {
            "total_endpoints": len(self.discovered_endpoints),
            "services_count": len(endpoints_by_service),
            "endpoints_by_service": {
                service: len(endpoints)
                for service, endpoints in endpoints_by_service.items()
            },
            "endpoints_by_method": {},
            "api_keys_found": len(self.api_keys),
            "base_urls_found": len(self.base_urls)
        }

        # Count by method
        for endpoint in self.discovered_endpoints:
            method = endpoint.method
            if method not in stats["endpoints_by_method"]:
                stats["endpoints_by_method"][method] = 0
            stats["endpoints_by_method"][method] += 1

        report = {
            "scan_timestamp": datetime.now().isoformat(),
            "scanner_version": "1.0.0",
            "statistics": stats,
            "discovered_endpoints": [
                {
                    "service": ep.service,
                    "method": ep.method,
                    "url": ep.url,
                    "description": ep.description
                }
                for ep in self.discovered_endpoints
            ]
        }

        # Save report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Scan report saved to {output_path}")
        logger.info(f"Total endpoints discovered: {stats['total_endpoints']}")
        logger.info(f"Services: {stats['services_count']}")

        return report

    def run_full_scan(self):
        """Run a complete scan of the codebase"""
        logger.info("Starting full API scan")

        # Scan config files
        self.scan_config_files()

        # Scan Python files
        self.scan_python_files()

        # Generate Postman requests
        auto_discovered_items = self.generate_postman_requests()

        # Update Postman collection
        collection_path = self.config_dir / 'postman_complete_collection.json'
        self.update_postman_collection(collection_path, auto_discovered_items)

        # Generate environment file
        env_path = self.config_dir / 'postman_environment.json'
        self.generate_environment_file(env_path)

        # Generate scan report
        report_path = self.logs_dir / f'postman_scan_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report = self.generate_scan_report(report_path)

        logger.info("Full API scan completed successfully")
        return report


def main():
    """Main entry point"""
    scanner = PostmanAPIScanner()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'scan':
            report = scanner.run_full_scan()
            print(json.dumps(report['statistics'], indent=2))

        elif command == 'config-only':
            scanner.scan_config_files()
            items = scanner.generate_postman_requests()
            print(f"Discovered {len(scanner.discovered_endpoints)} endpoints from config files")

        elif command == 'python-only':
            scanner.scan_python_files()
            items = scanner.generate_postman_requests()
            print(f"Discovered {len(scanner.discovered_endpoints)} endpoints from Python files")

        elif command == 'report':
            scanner.run_full_scan()

        else:
            print(f"Unknown command: {command}")
            print("Usage: python postman_api_scanner.py [scan|config-only|python-only|report]")
            sys.exit(1)
    else:
        # Default: run full scan
        report = scanner.run_full_scan()
        print(f"\nScan completed!")
        print(f"Total endpoints: {report['statistics']['total_endpoints']}")
        print(f"Services: {report['statistics']['services_count']}")
        print(f"API keys found: {report['statistics']['api_keys_found']}")


if __name__ == '__main__':
    main()
