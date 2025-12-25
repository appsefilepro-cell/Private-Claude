#!/usr/bin/env python3
"""
Postman Collection Runner
Automates API testing and publishes results to event bus
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import subprocess
import tempfile

from event_bus import event_bus, EventType, Event, Priority, publish_test_result


logger = logging.getLogger(__name__)


class PostmanConfig:
    """Postman configuration"""
    def __init__(self):
        self.api_key = os.getenv('POSTMAN_API_KEY', '')
        self.collection_id = os.getenv('POSTMAN_COLLECTION_ID', '')
        self.environment_id = os.getenv('POSTMAN_ENVIRONMENT_ID', '')
        self.workspace_id = os.getenv('POSTMAN_WORKSPACE_ID', '')


class PostmanRunner:
    """Postman collection runner"""

    def __init__(self, config: Optional[PostmanConfig] = None):
        self.config = config or PostmanConfig()
        self.newman_installed = self._check_newman()

    def _check_newman(self) -> bool:
        """Check if newman CLI is installed"""
        try:
            result = subprocess.run(['newman', '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Newman version: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            logger.warning("Newman CLI not installed. Install with: npm install -g newman")
        return False

    async def download_collection(self, collection_id: Optional[str] = None) -> Optional[Dict]:
        """Download collection from Postman API"""
        collection_id = collection_id or self.config.collection_id

        if not self.config.api_key or not collection_id:
            logger.error("Postman API key or collection ID not configured")
            return None

        url = f"https://api.getpostman.com/collections/{collection_id}"
        headers = {'X-API-Key': self.config.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Downloaded collection: {data.get('collection', {}).get('info', {}).get('name')}")
                        return data.get('collection')
                    else:
                        logger.error(f"Failed to download collection: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading collection: {e}")
            return None

    async def download_environment(self, environment_id: Optional[str] = None) -> Optional[Dict]:
        """Download environment from Postman API"""
        environment_id = environment_id or self.config.environment_id

        if not self.config.api_key or not environment_id:
            return None

        url = f"https://api.getpostman.com/environments/{environment_id}"
        headers = {'X-API-Key': self.config.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Downloaded environment: {data.get('environment', {}).get('name')}")
                        return data.get('environment')
                    else:
                        logger.error(f"Failed to download environment: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading environment: {e}")
            return None

    async def run_collection(self, collection: Optional[Dict] = None,
                           environment: Optional[Dict] = None,
                           collection_path: Optional[str] = None) -> Dict:
        """Run Postman collection using Newman"""
        if not self.newman_installed:
            logger.error("Newman not installed")
            return {'success': False, 'error': 'Newman not installed'}

        # Download collection if not provided
        if not collection and not collection_path:
            collection = await self.download_collection()
            if not collection:
                return {'success': False, 'error': 'Failed to download collection'}

        # Download environment if not provided
        if not environment:
            environment = await self.download_environment()

        # Publish start event
        start_event = Event(
            event_type=EventType.POSTMAN_TEST_START,
            source='postman',
            timestamp=datetime.utcnow().isoformat(),
            data={
                'collection_name': collection.get('info', {}).get('name', 'Unknown') if collection else 'Unknown'
            },
            priority=Priority.MEDIUM
        )
        await event_bus.publish(start_event)

        # Save collection and environment to temp files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            if collection_path:
                collection_file = collection_path
            else:
                json.dump(collection, f)
                collection_file = f.name

        environment_file = None
        if environment:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(environment, f)
                environment_file = f.name

        try:
            # Run newman
            cmd = [
                'newman', 'run', collection_file,
                '--reporters', 'cli,json',
                '--reporter-json-export', '/tmp/newman-results.json'
            ]

            if environment_file:
                cmd.extend(['--environment', environment_file])

            start_time = datetime.utcnow()
            result = subprocess.run(cmd, capture_output=True, text=True)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Parse results
            try:
                with open('/tmp/newman-results.json', 'r') as f:
                    newman_results = json.load(f)

                results = self._parse_newman_results(newman_results, duration)

                # Publish results
                await publish_test_result(
                    test_name=results['collection_name'],
                    passed=results['success'],
                    total_tests=results['total_tests'],
                    failed_tests=results['failed_tests'],
                    duration=duration,
                    failures=results.get('failures', [])
                )

                return results

            except Exception as e:
                logger.error(f"Error parsing results: {e}")
                return {
                    'success': result.returncode == 0,
                    'output': result.stdout,
                    'error': result.stderr
                }

        finally:
            # Cleanup temp files
            if not collection_path:
                os.unlink(collection_file)
            if environment_file:
                os.unlink(environment_file)

    def _parse_newman_results(self, results: Dict, duration: float) -> Dict:
        """Parse Newman JSON results"""
        run = results.get('run', {})
        stats = run.get('stats', {})

        total_tests = stats.get('assertions', {}).get('total', 0)
        failed_tests = stats.get('assertions', {}).get('failed', 0)
        passed_tests = total_tests - failed_tests

        failures = []
        for execution in run.get('executions', []):
            for assertion in execution.get('assertions', []):
                if assertion.get('error'):
                    failures.append({
                        'name': assertion.get('assertion', 'Unknown'),
                        'error': assertion.get('error', {}).get('message', 'Unknown error')
                    })

        return {
            'success': failed_tests == 0,
            'collection_name': run.get('info', {}).get('name', 'Unknown'),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'duration': duration,
            'failures': failures[:10],  # Limit to first 10 failures
            'total_requests': stats.get('requests', {}).get('total', 0),
            'failed_requests': stats.get('requests', {}).get('failed', 0)
        }

    async def run_scheduled_tests(self, interval: int = 3600):
        """Run tests on a schedule"""
        logger.info(f"Starting scheduled tests (every {interval} seconds)")

        while True:
            try:
                results = await self.run_collection()
                logger.info(f"Test results: {results.get('passed_tests', 0)}/{results.get('total_tests', 0)} passed")
            except Exception as e:
                logger.error(f"Error running scheduled tests: {e}")

            await asyncio.sleep(interval)


class PostmanMonitor:
    """Monitor Postman API for collection updates"""

    def __init__(self, config: Optional[PostmanConfig] = None):
        self.config = config or PostmanConfig()

    async def get_collections(self) -> List[Dict]:
        """Get all collections in workspace"""
        if not self.config.api_key:
            return []

        url = "https://api.getpostman.com/collections"
        headers = {'X-API-Key': self.config.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('collections', [])
                    return []
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return []

    async def monitor_collection_changes(self, interval: int = 300):
        """Monitor collections for changes"""
        logger.info("Starting collection monitor")
        last_collections = {}

        while True:
            try:
                collections = await self.get_collections()

                for collection in collections:
                    collection_id = collection.get('id')
                    updated_at = collection.get('updatedAt')

                    if collection_id in last_collections:
                        if last_collections[collection_id] != updated_at:
                            logger.info(f"Collection updated: {collection.get('name')}")
                            # Trigger test run
                            runner = PostmanRunner(self.config)
                            await runner.run_collection(collection_id=collection_id)

                    last_collections[collection_id] = updated_at

            except Exception as e:
                logger.error(f"Error monitoring collections: {e}")

            await asyncio.sleep(interval)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def main():
        runner = PostmanRunner()

        # Example: Run collection from file
        results = await runner.run_collection(
            collection_path='/path/to/collection.json'
        )

        print(json.dumps(results, indent=2))

    asyncio.run(main())
