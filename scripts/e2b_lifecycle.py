#!/usr/bin/env python3
"""
E2B Sandbox Lifecycle Management
Automated creation, execution, monitoring, and cleanup of sandboxes
Integrates with GitHub workflows and Zapier for event-driven automation
"""

import os
import sys
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
import traceback

try:
    import aiohttp
except ImportError:
    os.system("pip install aiohttp")
    import aiohttp


# Logging configuration
logger = logging.getLogger("E2B-Lifecycle")
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class LifecyclePhase(Enum):
    """Lifecycle phases"""
    INITIALIZATION = "init"
    PREPARATION = "prep"
    EXECUTION = "exec"
    MONITORING = "monitor"
    COMPLETION = "complete"
    CLEANUP = "cleanup"
    ERROR = "error"


class EventType(Enum):
    """Event types for lifecycle hooks"""
    BEFORE_CREATE = "before_create"
    AFTER_CREATE = "after_create"
    BEFORE_EXECUTE = "before_execute"
    AFTER_EXECUTE = "after_execute"
    BEFORE_CLEANUP = "before_cleanup"
    AFTER_CLEANUP = "after_cleanup"
    ON_ERROR = "on_error"
    ON_TIMEOUT = "on_timeout"
    ON_COMPLETION = "on_completion"


@dataclass
class LifecycleEvent:
    """Lifecycle event data"""
    event_type: EventType
    sandbox_id: str
    phase: LifecyclePhase
    timestamp: str
    data: Dict[str, Any]
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "event_type": self.event_type.value,
            "sandbox_id": self.sandbox_id,
            "phase": self.phase.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "error": self.error
        }


@dataclass
class LifecycleConfig:
    """Lifecycle configuration"""
    sandbox_id: str
    template: str
    timeout: int
    max_retries: int
    retry_delay: int
    cleanup_on_error: bool
    monitor_interval: int
    enable_webhooks: bool
    environment: Dict[str, str]
    files: List[tuple]
    scripts: List[str]
    on_completion: Optional[Callable] = None


class EventBus:
    """Event bus for lifecycle events"""

    def __init__(self):
        self.listeners: Dict[EventType, List[Callable]] = {}
        self.event_history: List[LifecycleEvent] = []

    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to event type"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type.value}")

    async def emit(self, event: LifecycleEvent):
        """Emit event to listeners"""
        self.event_history.append(event)
        logger.debug(f"Event: {event.event_type.value}")

        if event.event_type in self.listeners:
            for callback in self.listeners[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")

    def get_history(self, event_type: Optional[EventType] = None) -> List[LifecycleEvent]:
        """Get event history"""
        if event_type:
            return [e for e in self.event_history if e.event_type == event_type]
        return self.event_history


class LifecycleManager:
    """Manages sandbox lifecycle with automation"""

    def __init__(self, sandbox_manager, webhook_client):
        self.sandbox_manager = sandbox_manager
        self.webhook_client = webhook_client
        self.event_bus = EventBus()
        self.active_lifecycles: Dict[str, Dict] = {}

        logger.info("Lifecycle Manager initialized")

    async def create_lifecycle(self, config: LifecycleConfig) -> Dict[str, Any]:
        """Create and manage sandbox lifecycle"""
        sandbox_id = config.sandbox_id
        self.active_lifecycles[sandbox_id] = {
            "config": config,
            "status": LifecyclePhase.INITIALIZATION.value,
            "created_at": datetime.utcnow().isoformat(),
            "events": [],
            "results": []
        }

        try:
            # Phase 1: Initialization
            await self._emit_event(
                EventType.BEFORE_CREATE,
                sandbox_id,
                LifecyclePhase.INITIALIZATION,
                {"template": config.template}
            )

            # Phase 2: Preparation
            logger.info(f"Preparing sandbox {sandbox_id}")
            self.active_lifecycles[sandbox_id]["status"] = LifecyclePhase.PREPARATION.value

            result = await self.sandbox_manager.create_sandbox(
                template_name=config.template,
                sandbox_id=sandbox_id,
                custom_env=config.environment,
                files=config.files
            )

            if not result.get("success"):
                raise Exception(f"Sandbox creation failed: {result.get('error')}")

            await self._emit_event(
                EventType.AFTER_CREATE,
                sandbox_id,
                LifecyclePhase.PREPARATION,
                {"sandbox_id": sandbox_id, "files_uploaded": result.get("files_uploaded", 0)}
            )

            # Phase 3: Execution
            logger.info(f"Executing scripts in {sandbox_id}")
            self.active_lifecycles[sandbox_id]["status"] = LifecyclePhase.EXECUTION.value

            await self._emit_event(
                EventType.BEFORE_EXECUTE,
                sandbox_id,
                LifecyclePhase.EXECUTION,
                {"script_count": len(config.scripts)}
            )

            execution_results = []
            for script in config.scripts:
                try:
                    result = await self._execute_with_timeout(
                        sandbox_id,
                        script,
                        config.timeout
                    )
                    execution_results.append(result)
                    self.active_lifecycles[sandbox_id]["results"].append(result)
                except asyncio.TimeoutError:
                    error_msg = f"Execution timeout: {script[:50]}"
                    logger.error(error_msg)
                    await self._emit_event(
                        EventType.ON_TIMEOUT,
                        sandbox_id,
                        LifecyclePhase.EXECUTION,
                        {"script": script[:100]}
                    )
                    raise

            await self._emit_event(
                EventType.AFTER_EXECUTE,
                sandbox_id,
                LifecyclePhase.EXECUTION,
                {"execution_count": len(execution_results)}
            )

            # Phase 4: Completion
            self.active_lifecycles[sandbox_id]["status"] = LifecyclePhase.COMPLETION.value
            logger.info(f"Lifecycle completed for {sandbox_id}")

            await self._emit_event(
                EventType.ON_COMPLETION,
                sandbox_id,
                LifecyclePhase.COMPLETION,
                {
                    "executions": len(execution_results),
                    "uptime": self._get_uptime(sandbox_id)
                }
            )

            return {
                "success": True,
                "sandbox_id": sandbox_id,
                "executions": len(execution_results),
                "status": "completed"
            }

        except Exception as e:
            logger.error(f"Lifecycle error: {e}\n{traceback.format_exc()}")
            self.active_lifecycles[sandbox_id]["status"] = LifecyclePhase.ERROR.value
            self.active_lifecycles[sandbox_id]["error"] = str(e)

            await self._emit_event(
                EventType.ON_ERROR,
                sandbox_id,
                LifecyclePhase.ERROR,
                {"error": str(e)},
                error=str(e)
            )

            if config.cleanup_on_error:
                await self.cleanup_sandbox(sandbox_id)

            return {
                "success": False,
                "sandbox_id": sandbox_id,
                "error": str(e),
                "status": "error"
            }

        finally:
            # Phase 5: Cleanup
            if sandbox_id in self.active_lifecycles:
                await self.cleanup_sandbox(sandbox_id)

    async def _execute_with_timeout(self, sandbox_id: str, script: str, timeout: int) -> Dict:
        """Execute script with timeout"""
        try:
            task = asyncio.create_task(
                self.sandbox_manager.execute_code(sandbox_id, script)
            )
            result = await asyncio.wait_for(task, timeout=timeout)
            return result.to_dict()
        except asyncio.TimeoutError:
            logger.error(f"Execution timeout for {sandbox_id}")
            raise
        except Exception as e:
            logger.error(f"Execution error: {e}")
            raise

    async def _emit_event(self, event_type: EventType, sandbox_id: str, phase: LifecyclePhase,
                         data: Dict, error: Optional[str] = None):
        """Emit lifecycle event"""
        event = LifecycleEvent(
            event_type=event_type,
            sandbox_id=sandbox_id,
            phase=phase,
            timestamp=datetime.utcnow().isoformat(),
            data=data,
            error=error
        )

        if sandbox_id in self.active_lifecycles:
            self.active_lifecycles[sandbox_id]["events"].append(event.to_dict())

        await self.event_bus.emit(event)

    async def cleanup_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """Cleanup sandbox"""
        try:
            await self._emit_event(
                EventType.BEFORE_CLEANUP,
                sandbox_id,
                LifecyclePhase.CLEANUP,
                {}
            )

            logger.info(f"Cleaning up sandbox {sandbox_id}")

            await self.sandbox_manager.stop_sandbox(sandbox_id)
            result = await self.sandbox_manager.cleanup_sandbox(sandbox_id)

            await self._emit_event(
                EventType.AFTER_CLEANUP,
                sandbox_id,
                LifecyclePhase.CLEANUP,
                {"success": result.get("success", False)}
            )

            if sandbox_id in self.active_lifecycles:
                self.active_lifecycles[sandbox_id]["status"] = LifecyclePhase.CLEANUP.value
                self.active_lifecycles[sandbox_id]["cleaned_up_at"] = datetime.utcnow().isoformat()

            return result

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return {"success": False, "error": str(e)}

    def _get_uptime(self, sandbox_id: str) -> float:
        """Get sandbox uptime"""
        if sandbox_id not in self.active_lifecycles:
            return 0

        lifecycle = self.active_lifecycles[sandbox_id]
        created = datetime.fromisoformat(lifecycle["created_at"])
        now = datetime.utcnow()
        return (now - created).total_seconds()

    def get_lifecycle_status(self, sandbox_id: str) -> Dict[str, Any]:
        """Get lifecycle status"""
        if sandbox_id not in self.active_lifecycles:
            return {"error": "Lifecycle not found"}

        lifecycle = self.active_lifecycles[sandbox_id]
        return {
            "sandbox_id": sandbox_id,
            "status": lifecycle["status"],
            "created_at": lifecycle["created_at"],
            "uptime": self._get_uptime(sandbox_id),
            "event_count": len(lifecycle.get("events", [])),
            "result_count": len(lifecycle.get("results", [])),
            "error": lifecycle.get("error")
        }

    def get_all_lifecycles(self) -> Dict[str, Dict[str, Any]]:
        """Get all active lifecycles"""
        return {
            sid: self.get_lifecycle_status(sid)
            for sid in self.active_lifecycles.keys()
        }


class GitHubWorkflowIntegration:
    """Integration with GitHub workflows"""

    def __init__(self, webhook_client):
        self.webhook_client = webhook_client
        self.workflows = {}

    async def register_workflow(self, workflow_name: str, trigger: str,
                               config: LifecycleConfig) -> Dict[str, Any]:
        """Register GitHub workflow trigger"""
        self.workflows[workflow_name] = {
            "name": workflow_name,
            "trigger": trigger,
            "config": config,
            "registered_at": datetime.utcnow().isoformat(),
            "execution_count": 0
        }

        logger.info(f"Registered workflow: {workflow_name}")
        return {"success": True, "workflow": workflow_name}

    async def trigger_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Trigger workflow execution"""
        if workflow_name not in self.workflows:
            return {"success": False, "error": f"Workflow not found: {workflow_name}"}

        workflow = self.workflows[workflow_name]
        workflow["execution_count"] += 1

        logger.info(f"Triggering workflow: {workflow_name}")

        # Send webhook event
        await self.webhook_client.send_event("workflow_triggered", {
            "workflow": workflow_name,
            "trigger": workflow["trigger"],
            "execution_count": workflow["execution_count"]
        })

        return {
            "success": True,
            "workflow": workflow_name,
            "execution_count": workflow["execution_count"]
        }

    def get_workflows(self) -> Dict[str, Dict]:
        """Get all registered workflows"""
        return self.workflows


class ZapierIntegration:
    """Integration with Zapier for multi-app automation"""

    def __init__(self, webhook_client):
        self.webhook_client = webhook_client
        self.integrations = {}

    async def register_integration(self, integration_name: str, apps: List[str],
                                  actions: List[str]) -> Dict[str, Any]:
        """Register Zapier integration"""
        self.integrations[integration_name] = {
            "name": integration_name,
            "apps": apps,
            "actions": actions,
            "registered_at": datetime.utcnow().isoformat(),
            "trigger_count": 0
        }

        logger.info(f"Registered Zapier integration: {integration_name}")

        # Sync with Zapier
        await self.webhook_client.send_event("zapier_integration_registered", {
            "integration": integration_name,
            "apps": apps,
            "actions": actions
        })

        return {"success": True, "integration": integration_name}

    async def trigger_integration(self, integration_name: str, data: Dict) -> Dict[str, Any]:
        """Trigger Zapier integration"""
        if integration_name not in self.integrations:
            return {"success": False, "error": f"Integration not found: {integration_name}"}

        integration = self.integrations[integration_name]
        integration["trigger_count"] += 1

        logger.info(f"Triggering Zapier integration: {integration_name}")

        # Send webhook event
        await self.webhook_client.send_event("zapier_integration_triggered", {
            "integration": integration_name,
            "apps": integration["apps"],
            "data": data,
            "trigger_count": integration["trigger_count"]
        })

        return {
            "success": True,
            "integration": integration_name,
            "trigger_count": integration["trigger_count"]
        }

    def get_integrations(self) -> Dict[str, Dict]:
        """Get all registered integrations"""
        return self.integrations


class AutomationOrchestrator:
    """Orchestrates automated workflows"""

    def __init__(self, lifecycle_manager: LifecycleManager,
                 github_integration: GitHubWorkflowIntegration,
                 zapier_integration: ZapierIntegration):
        self.lifecycle = lifecycle_manager
        self.github = github_integration
        self.zapier = zapier_integration
        self.scheduled_tasks = {}

    async def create_automated_workflow(self, name: str, trigger_type: str,
                                       lifecycle_config: LifecycleConfig,
                                       github_workflow: Optional[str] = None,
                                       zapier_integration: Optional[str] = None) -> Dict[str, Any]:
        """Create automated workflow with multiple integrations"""

        logger.info(f"Creating automated workflow: {name}")

        workflow = {
            "name": name,
            "trigger_type": trigger_type,
            "lifecycle_config": lifecycle_config,
            "github_workflow": github_workflow,
            "zapier_integration": zapier_integration,
            "created_at": datetime.utcnow().isoformat(),
            "execution_count": 0
        }

        self.scheduled_tasks[name] = workflow

        # Register with GitHub if specified
        if github_workflow:
            await self.github.register_workflow(github_workflow, trigger_type, lifecycle_config)

        # Register with Zapier if specified
        if zapier_integration:
            await self.zapier.register_integration(
                zapier_integration,
                apps=["GitHub", "E2B", "Slack"],
                actions=["trigger", "log", "notify"]
            )

        logger.info(f"Automated workflow created: {name}")
        return {"success": True, "workflow": name}

    async def execute_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Execute automated workflow"""
        if workflow_name not in self.scheduled_tasks:
            return {"success": False, "error": f"Workflow not found: {workflow_name}"}

        workflow = self.scheduled_tasks[workflow_name]
        workflow["execution_count"] += 1

        logger.info(f"Executing workflow: {workflow_name}")

        # Execute lifecycle
        result = await self.lifecycle.create_lifecycle(workflow["lifecycle_config"])

        # Trigger GitHub workflow if configured
        if workflow["github_workflow"]:
            await self.github.trigger_workflow(workflow["github_workflow"])

        # Trigger Zapier integration if configured
        if workflow["zapier_integration"]:
            await self.zapier.trigger_integration(
                workflow["zapier_integration"],
                data={
                    "workflow": workflow_name,
                    "result": result,
                    "execution_count": workflow["execution_count"]
                }
            )

        return {
            "success": True,
            "workflow": workflow_name,
            "result": result,
            "execution_count": workflow["execution_count"]
        }

    def get_workflows(self) -> Dict[str, Dict]:
        """Get all workflows"""
        return self.scheduled_tasks


# CLI Interface
async def main():
    """CLI for lifecycle management"""
    import argparse

    parser = argparse.ArgumentParser(description="E2B Lifecycle Manager")
    parser.add_argument("--api-key", default=os.getenv("E2B_API_KEY"))
    parser.add_argument("--config", default="/home/user/Private-Claude/config/e2b_sandbox_templates.json")

    subparsers = parser.add_subparsers(dest="command")

    # Create lifecycle
    create_parser = subparsers.add_parser("create-lifecycle", help="Create sandbox lifecycle")
    create_parser.add_argument("--sandbox-id", required=True)
    create_parser.add_argument("--template", default="python")
    create_parser.add_argument("--timeout", type=int, default=300)
    create_parser.add_argument("--script", action="append", help="Script to execute")

    # Create workflow
    workflow_parser = subparsers.add_parser("create-workflow", help="Create automated workflow")
    workflow_parser.add_argument("--name", required=True)
    workflow_parser.add_argument("--trigger", default="manual")
    workflow_parser.add_argument("--template", default="python")

    # List workflows
    subparsers.add_parser("list-workflows", help="List all workflows")

    # Get status
    status_parser = subparsers.add_parser("status", help="Get lifecycle status")
    status_parser.add_argument("--sandbox-id")

    args = parser.parse_args()

    # Import sandbox manager here to avoid circular imports
    sys.path.insert(0, '/home/user/Private-Claude/scripts')
    from e2b_sandbox_manager import E2BSandboxManager

    # Initialize
    sandbox_manager = E2BSandboxManager(api_key=args.api_key, config_path=args.config)
    await sandbox_manager.webhook_client.initialize()

    lifecycle_manager = LifecycleManager(sandbox_manager, sandbox_manager.webhook_client)
    github_integration = GitHubWorkflowIntegration(sandbox_manager.webhook_client)
    zapier_integration = ZapierIntegration(sandbox_manager.webhook_client)
    orchestrator = AutomationOrchestrator(lifecycle_manager, github_integration, zapier_integration)

    try:
        if args.command == "create-lifecycle":
            config = LifecycleConfig(
                sandbox_id=args.sandbox_id,
                template=args.template,
                timeout=args.timeout,
                max_retries=3,
                retry_delay=5,
                cleanup_on_error=True,
                monitor_interval=5,
                enable_webhooks=True,
                environment={},
                files=[],
                scripts=args.script or ["print('Hello from E2B')"]
            )
            result = await lifecycle_manager.create_lifecycle(config)
            print(json.dumps(result, indent=2))

        elif args.command == "create-workflow":
            config = LifecycleConfig(
                sandbox_id=f"{args.name}_sbx",
                template=args.template,
                timeout=300,
                max_retries=3,
                retry_delay=5,
                cleanup_on_error=True,
                monitor_interval=5,
                enable_webhooks=True,
                environment={},
                files=[],
                scripts=[]
            )
            result = await orchestrator.create_automated_workflow(
                name=args.name,
                trigger_type=args.trigger,
                lifecycle_config=config
            )
            print(json.dumps(result, indent=2))

        elif args.command == "list-workflows":
            workflows = orchestrator.get_workflows()
            print(json.dumps({k: str(v) for k, v in workflows.items()}, indent=2))

        elif args.command == "status":
            if args.sandbox_id:
                status = lifecycle_manager.get_lifecycle_status(args.sandbox_id)
            else:
                status = lifecycle_manager.get_all_lifecycles()
            print(json.dumps(status, indent=2))

        else:
            parser.print_help()

    finally:
        await sandbox_manager.cleanup_all()


if __name__ == "__main__":
    asyncio.run(main())
