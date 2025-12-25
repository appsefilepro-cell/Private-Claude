#!/usr/bin/env python3
"""
Main Integration Orchestrator
Coordinates all system integrations and services
"""

import asyncio
import logging
import signal
import sys
import os
from typing import List
from datetime import datetime

# Import all services
from event_bus import event_bus, Event, EventType, Priority, publish_app_status
from email_notifier import EmailNotifier, EmailConfig
from gitlab_github_sync import start_webhook_server, GitSyncService
from postman_runner import PostmanRunner, PostmanMonitor, PostmanConfig
from zapier_integration import setup_zapier_integration, ZapierIntegration


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/home/user/Private-Claude/logs/system-integration.log')
    ]
)
logger = logging.getLogger(__name__)


class IntegrationOrchestrator:
    """Main orchestrator for all integrations"""

    def __init__(self):
        self.services = {}
        self.running = False
        self.tasks: List[asyncio.Task] = []

    async def initialize(self):
        """Initialize all services"""
        logger.info("Initializing integration orchestrator...")

        try:
            # Initialize email notifier
            logger.info("Setting up email notifier...")
            email_notifier = EmailNotifier(EmailConfig())
            event_bus.set_email_notifier(email_notifier)
            self.services['email'] = email_notifier

            # Initialize Zapier integration
            logger.info("Setting up Zapier integration...")
            zapier = await setup_zapier_integration()
            self.services['zapier'] = zapier

            # Initialize Git sync service
            logger.info("Setting up Git sync service...")
            git_sync = GitSyncService()
            self.services['git_sync'] = git_sync

            # Initialize Postman runner
            logger.info("Setting up Postman runner...")
            postman = PostmanRunner(PostmanConfig())
            self.services['postman'] = postman

            # Initialize Postman monitor
            logger.info("Setting up Postman monitor...")
            postman_monitor = PostmanMonitor(PostmanConfig())
            self.services['postman_monitor'] = postman_monitor

            logger.info("All services initialized successfully")

            # Publish system startup event
            await publish_app_status(
                app_name='system-integration',
                status='started',
                details='All integration services initialized and running',
                success=True
            )

        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            raise

    async def start(self):
        """Start all services"""
        logger.info("Starting all services...")
        self.running = True

        try:
            # Start webhook server
            webhook_port = int(os.getenv('WEBHOOK_PORT', '8080'))
            logger.info(f"Starting webhook server on port {webhook_port}...")
            webhook_task = asyncio.create_task(start_webhook_server(webhook_port))
            self.tasks.append(webhook_task)

            # Start Postman scheduled tests (if enabled)
            if os.getenv('POSTMAN_SCHEDULED_TESTS', 'false').lower() == 'true':
                test_interval = int(os.getenv('POSTMAN_TEST_INTERVAL', '3600'))
                logger.info(f"Starting scheduled Postman tests (every {test_interval}s)...")
                postman_task = asyncio.create_task(
                    self.services['postman'].run_scheduled_tests(test_interval)
                )
                self.tasks.append(postman_task)

            # Start Postman collection monitor (if enabled)
            if os.getenv('POSTMAN_MONITOR_ENABLED', 'false').lower() == 'true':
                monitor_interval = int(os.getenv('POSTMAN_MONITOR_INTERVAL', '300'))
                logger.info(f"Starting Postman collection monitor (every {monitor_interval}s)...")
                monitor_task = asyncio.create_task(
                    self.services['postman_monitor'].monitor_collection_changes(monitor_interval)
                )
                self.tasks.append(monitor_task)

            # Start health check task
            health_task = asyncio.create_task(self._health_check_loop())
            self.tasks.append(health_task)

            logger.info("All services started successfully")

            # Wait for all tasks
            await asyncio.gather(*self.tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Error starting services: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Stop all services"""
        logger.info("Stopping all services...")
        self.running = False

        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)

        # Publish shutdown event
        try:
            await publish_app_status(
                app_name='system-integration',
                status='stopped',
                details='All integration services stopped',
                success=True
            )
        except:
            pass

        logger.info("All services stopped")

    async def _health_check_loop(self):
        """Periodic health check"""
        while self.running:
            try:
                # Publish health check event
                stats = event_bus.get_stats()

                health_event = Event(
                    event_type=EventType.SYSTEM_HEALTH_CHECK,
                    source='orchestrator',
                    timestamp=datetime.utcnow().isoformat(),
                    data={
                        'services_running': len(self.services),
                        'tasks_running': len([t for t in self.tasks if not t.done()]),
                        'event_bus_stats': stats
                    },
                    priority=Priority.LOW
                )
                await event_bus.publish(health_event)

                # Check service health
                for name, service in self.services.items():
                    logger.debug(f"Service {name}: OK")

            except Exception as e:
                logger.error(f"Health check error: {e}")

            # Wait 5 minutes between checks
            await asyncio.sleep(300)

    def get_status(self) -> dict:
        """Get orchestrator status"""
        return {
            'running': self.running,
            'services': list(self.services.keys()),
            'tasks': len(self.tasks),
            'active_tasks': len([t for t in self.tasks if not t.done()]),
            'event_bus_stats': event_bus.get_stats()
        }


# Global orchestrator instance
orchestrator = IntegrationOrchestrator()


async def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("Private Claude - System Integration Framework")
    logger.info("="*60)

    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        asyncio.create_task(orchestrator.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize and start
        await orchestrator.initialize()
        await orchestrator.start()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await orchestrator.stop()
        logger.info("Shutdown complete")


if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('/home/user/Private-Claude/logs', exist_ok=True)

    # Run main
    asyncio.run(main())
