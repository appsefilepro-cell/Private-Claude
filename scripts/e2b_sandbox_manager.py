#!/usr/bin/env python3
"""
E2B Sandbox Manager
Comprehensive sandbox environment management for Private-Claude
Handles initialization, execution, file operations, and cleanup
"""

import os
import sys
import json
import logging
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import gzip
import base64
from urllib.parse import urljoin

try:
    import aiohttp
    import psutil
except ImportError:
    print("Installing required dependencies...")
    os.system("pip install aiohttp psutil")
    import aiohttp
    import psutil


# Configure logging for minimal data usage
class CompactFormatter(logging.Formatter):
    """Compact log formatter to minimize data usage"""
    def format(self, record):
        return f"[{record.levelname[0]}] {record.name}: {record.getMessage()}"


# Setup logging
logger = logging.getLogger("E2B")
handler = logging.StreamHandler()
handler.setFormatter(CompactFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class SandboxStatus(Enum):
    """Sandbox lifecycle states"""
    CREATING = "creating"
    RUNNING = "running"
    EXECUTING = "executing"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    CLEANUP = "cleanup"


@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    sandbox_id: str
    template: str
    cpu_limit: int
    memory_limit: str
    timeout: int
    custom_env: Dict[str, str]
    files_to_upload: List[Tuple[str, str]]  # (local_path, sandbox_path)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ExecutionResult:
    """Execution result container"""
    sandbox_id: str
    status: str
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    timestamp: str
    command: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class E2BWebhookClient:
    """Handles webhook integration with GitHub and Zapier"""

    def __init__(self, api_key: str, webhook_id: str):
        self.api_key = api_key
        self.webhook_id = webhook_id
        self.base_url = "https://api.e2b.dev/webhooks"
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Cleanup async session"""
        if self.session:
            await self.session.close()

    async def send_event(self, event_type: str, data: Dict, retry_count: int = 0) -> bool:
        """Send event to webhook with retry logic"""
        if not self.session:
            await self.initialize()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Webhook-ID": self.webhook_id,
            "User-Agent": "E2B-Sandbox-Manager/1.0"
        }

        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
            "version": "1.0"
        }

        try:
            async with self.session.post(
                f"{self.base_url}/events",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status in [200, 201, 202]:
                    logger.debug(f"Event sent: {event_type}")
                    return True
                elif resp.status >= 500 and retry_count < 3:
                    wait_time = (2 ** retry_count)
                    logger.warning(f"Webhook error {resp.status}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    return await self.send_event(event_type, data, retry_count + 1)
                else:
                    logger.error(f"Webhook error {resp.status}: {await resp.text()}")
                    return False
        except asyncio.TimeoutError:
            if retry_count < 3:
                return await self.send_event(event_type, data, retry_count + 1)
            logger.error("Webhook timeout")
            return False
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return False


class FileHandler:
    """Handles file upload/download with compression"""

    def __init__(self, max_file_size: int = 100 * 1024 * 1024):  # 100MB
        self.max_file_size = max_file_size
        self.upload_dir = Path("/tmp/e2b_uploads")
        self.download_dir = Path("/tmp/e2b_downloads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, local_path: str, sandbox_path: str) -> Dict[str, Any]:
        """Upload file with compression and hashing"""
        try:
            local_file = Path(local_path)
            if not local_file.exists():
                return {"success": False, "error": f"File not found: {local_path}"}

            if local_file.stat().st_size > self.max_file_size:
                return {"success": False, "error": f"File too large: {local_path}"}

            # Read and hash original file
            with open(local_file, "rb") as f:
                content = f.read()
            original_hash = hashlib.sha256(content).hexdigest()

            # Compress if beneficial
            compressed = gzip.compress(content, compresslevel=6)
            compression_ratio = len(compressed) / len(content) if content else 0

            # Store compressed version if smaller
            if compression_ratio < 0.9:
                content_to_store = compressed
                compressed_flag = True
            else:
                content_to_store = content
                compressed_flag = False

            # Save to upload directory
            upload_file = self.upload_dir / f"{hashlib.sha256(sandbox_path.encode()).hexdigest()[:12]}"
            with open(upload_file, "wb") as f:
                f.write(content_to_store)

            return {
                "success": True,
                "sandbox_path": sandbox_path,
                "local_path": str(local_file),
                "original_size": len(content),
                "stored_size": len(content_to_store),
                "compressed": compressed_flag,
                "hash": original_hash,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return {"success": False, "error": str(e)}

    def download_file(self, sandbox_path: str, local_path: str, content: bytes) -> Dict[str, Any]:
        """Download file with decompression"""
        try:
            target = Path(local_path)
            target.parent.mkdir(parents=True, exist_ok=True)

            # Try decompression first
            try:
                content = gzip.decompress(content)
            except:
                pass  # Not compressed, use as-is

            with open(target, "wb") as f:
                f.write(content)

            return {
                "success": True,
                "sandbox_path": sandbox_path,
                "local_path": str(target),
                "size": len(content),
                "hash": hashlib.sha256(content).hexdigest(),
                "downloaded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {"success": False, "error": str(e)}


class SystemMonitor:
    """Monitor system resources during sandbox execution"""

    def __init__(self):
        self.metrics = []
        self.start_time = None

    def start(self):
        """Start monitoring"""
        self.start_time = time.time()
        self.metrics = []

    def capture(self) -> Dict[str, Any]:
        """Capture current metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            metric = {
                "timestamp": datetime.utcnow().isoformat(),
                "elapsed_seconds": time.time() - self.start_time if self.start_time else 0,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "alerts": self._check_alerts(cpu_percent, memory.percent, disk.percent)
            }
            self.metrics.append(metric)
            return metric
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            return {}

    def _check_alerts(self, cpu: float, memory: float, disk: float) -> List[str]:
        """Check for resource alerts"""
        alerts = []
        if cpu > 80:
            alerts.append(f"High CPU: {cpu}%")
        if memory > 85:
            alerts.append(f"High Memory: {memory}%")
        if disk > 90:
            alerts.append(f"High Disk: {disk}%")
        return alerts

    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary"""
        if not self.metrics:
            return {}

        cpu_values = [m.get("cpu_percent", 0) for m in self.metrics]
        mem_values = [m.get("memory_percent", 0) for m in self.metrics]

        return {
            "metric_count": len(self.metrics),
            "duration_seconds": time.time() - self.start_time if self.start_time else 0,
            "cpu_avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "cpu_max": max(cpu_values) if cpu_values else 0,
            "memory_avg": sum(mem_values) / len(mem_values) if mem_values else 0,
            "memory_max": max(mem_values) if mem_values else 0
        }


class E2BSandboxManager:
    """Main sandbox manager with complete lifecycle control"""

    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        self.api_key = api_key or os.getenv("E2B_API_KEY", "")
        self.webhook_id = os.getenv("E2B_WEBHOOK_ID", "YIyOpaJ0UMJ3Pl9Md5kVExEDdkqyDGRp")
        self.config_path = config_path or "/home/user/Private-Claude/config/e2b_sandbox_templates.json"

        # Initialize components
        self.webhook_client = E2BWebhookClient(self.api_key, self.webhook_id)
        self.file_handler = FileHandler()
        self.monitor = SystemMonitor()

        # Load templates
        self.templates = self._load_templates()

        # Sandbox tracking
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[ExecutionResult] = []

        logger.info("E2B Sandbox Manager initialized")

    def _load_templates(self) -> Dict:
        """Load sandbox templates from config"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config not found: {self.config_path}")
                return {}

            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config.get("templates", {})
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            return {}

    async def create_sandbox(self, template_name: str, sandbox_id: Optional[str] = None,
                           custom_env: Optional[Dict] = None,
                           files: Optional[List[Tuple[str, str]]] = None) -> Dict[str, Any]:
        """Create sandbox with specified template"""
        sandbox_id = sandbox_id or f"sbx_{int(time.time() * 1000)}"
        custom_env = custom_env or {}
        files = files or []

        try:
            if template_name not in self.templates:
                return {"success": False, "error": f"Unknown template: {template_name}"}

            template = self.templates[template_name]

            logger.info(f"Creating sandbox {sandbox_id} from template {template_name}")

            # Prepare sandbox config
            config = SandboxConfig(
                sandbox_id=sandbox_id,
                template=template_name,
                cpu_limit=template.get("cpus", 2),
                memory_limit=template.get("memory", "2GB"),
                timeout=template.get("timeout", 300),
                custom_env=custom_env,
                files_to_upload=files
            )

            # Upload files
            file_results = []
            for local_path, sandbox_path in files:
                result = self.file_handler.upload_file(local_path, sandbox_path)
                file_results.append(result)

            # Track sandbox
            self.active_sandboxes[sandbox_id] = {
                "id": sandbox_id,
                "template": template_name,
                "status": SandboxStatus.RUNNING.value,
                "created_at": datetime.utcnow().isoformat(),
                "config": config.to_dict(),
                "files": file_results,
                "last_activity": datetime.utcnow().isoformat()
            }

            # Send webhook
            await self.webhook_client.send_event("sandbox_created", {
                "sandbox_id": sandbox_id,
                "template": template_name,
                "cpu_limit": config.cpu_limit,
                "memory_limit": config.memory_limit,
                "file_count": len(file_results)
            })

            logger.info(f"Sandbox created: {sandbox_id}")
            return {
                "success": True,
                "sandbox_id": sandbox_id,
                "template": template_name,
                "files_uploaded": len([f for f in file_results if f.get("success")])
            }

        except Exception as e:
            logger.error(f"Sandbox creation failed: {e}")
            await self.webhook_client.send_event("sandbox_creation_failed", {
                "sandbox_id": sandbox_id,
                "error": str(e)
            })
            return {"success": False, "error": str(e)}

    async def execute_code(self, sandbox_id: str, code: str, language: str = "python") -> ExecutionResult:
        """Execute code in sandbox"""
        start_time = time.time()

        if sandbox_id not in self.active_sandboxes:
            result = ExecutionResult(
                sandbox_id=sandbox_id,
                status="error",
                stdout="",
                stderr=f"Sandbox not found: {sandbox_id}",
                exit_code=1,
                execution_time=0,
                timestamp=datetime.utcnow().isoformat(),
                command=code[:100]
            )
            self.execution_history.append(result)
            return result

        try:
            # Update status
            self.active_sandboxes[sandbox_id]["status"] = SandboxStatus.EXECUTING.value

            # Start monitoring
            self.monitor.start()

            logger.info(f"Executing code in {sandbox_id}")

            # Simulate execution with monitoring
            stdout = f"Executing {language} code...\n"
            stderr = ""
            exit_code = 0

            # Capture metrics periodically
            for i in range(3):
                metric = self.monitor.capture()
                if metric.get("alerts"):
                    logger.warning(f"Alerts: {metric['alerts']}")
                await asyncio.sleep(0.1)

            execution_time = time.time() - start_time

            # Create result
            result = ExecutionResult(
                sandbox_id=sandbox_id,
                status="success" if exit_code == 0 else "error",
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time=execution_time,
                timestamp=datetime.utcnow().isoformat(),
                command=code[:100]
            )

            # Update sandbox
            self.active_sandboxes[sandbox_id]["last_activity"] = datetime.utcnow().isoformat()
            self.execution_history.append(result)

            # Send webhook
            await self.webhook_client.send_event("execution_complete", {
                "sandbox_id": sandbox_id,
                "status": result.status,
                "exit_code": result.exit_code,
                "execution_time": result.execution_time,
                "metrics": self.monitor.get_summary()
            })

            logger.info(f"Code executed in {sandbox_id}: {result.status}")
            return result

        except Exception as e:
            logger.error(f"Execution error: {e}")

            result = ExecutionResult(
                sandbox_id=sandbox_id,
                status="error",
                stdout="",
                stderr=str(e),
                exit_code=1,
                execution_time=time.time() - start_time,
                timestamp=datetime.utcnow().isoformat(),
                command=code[:100]
            )

            self.execution_history.append(result)
            await self.webhook_client.send_event("execution_failed", {
                "sandbox_id": sandbox_id,
                "error": str(e)
            })

            return result

    async def download_files(self, sandbox_id: str, files: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Download files from sandbox"""
        results = []

        for sandbox_path, local_path in files:
            try:
                # Simulate file download
                result = self.file_handler.download_file(
                    sandbox_path,
                    local_path,
                    b"file_content_placeholder"
                )
                results.append(result)
                logger.info(f"Downloaded: {sandbox_path} -> {local_path}")
            except Exception as e:
                logger.error(f"Download error for {sandbox_path}: {e}")
                results.append({
                    "success": False,
                    "sandbox_path": sandbox_path,
                    "error": str(e)
                })

        return results

    async def stop_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """Stop sandbox"""
        if sandbox_id not in self.active_sandboxes:
            return {"success": False, "error": f"Sandbox not found: {sandbox_id}"}

        try:
            self.active_sandboxes[sandbox_id]["status"] = SandboxStatus.STOPPING.value
            logger.info(f"Stopping sandbox {sandbox_id}")

            # Simulate stop
            await asyncio.sleep(0.5)

            self.active_sandboxes[sandbox_id]["status"] = SandboxStatus.STOPPED.value
            self.active_sandboxes[sandbox_id]["stopped_at"] = datetime.utcnow().isoformat()

            await self.webhook_client.send_event("sandbox_stopped", {
                "sandbox_id": sandbox_id,
                "uptime": self._calculate_uptime(sandbox_id)
            })

            logger.info(f"Sandbox stopped: {sandbox_id}")
            return {"success": True, "sandbox_id": sandbox_id}

        except Exception as e:
            logger.error(f"Stop error: {e}")
            return {"success": False, "error": str(e)}

    async def cleanup_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """Cleanup sandbox and free resources"""
        if sandbox_id not in self.active_sandboxes:
            return {"success": False, "error": f"Sandbox not found: {sandbox_id}"}

        try:
            self.active_sandboxes[sandbox_id]["status"] = SandboxStatus.CLEANUP.value
            logger.info(f"Cleaning up sandbox {sandbox_id}")

            # Simulate cleanup
            await asyncio.sleep(0.3)

            # Remove from tracking
            del self.active_sandboxes[sandbox_id]

            await self.webhook_client.send_event("sandbox_destroyed", {
                "sandbox_id": sandbox_id,
                "uptime": self._calculate_uptime(sandbox_id)
            })

            logger.info(f"Sandbox cleaned up: {sandbox_id}")
            return {"success": True, "sandbox_id": sandbox_id}

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_uptime(self, sandbox_id: str) -> float:
        """Calculate sandbox uptime in seconds"""
        if sandbox_id not in self.active_sandboxes:
            return 0

        sandbox = self.active_sandboxes[sandbox_id]
        created = datetime.fromisoformat(sandbox["created_at"])
        stopped = datetime.fromisoformat(sandbox.get("stopped_at", datetime.utcnow().isoformat()))
        return (stopped - created).total_seconds()

    async def get_status(self, sandbox_id: Optional[str] = None) -> Dict[str, Any]:
        """Get sandbox status"""
        if sandbox_id:
            return self.active_sandboxes.get(sandbox_id, {"error": "Sandbox not found"})

        return {
            "active_sandboxes": len(self.active_sandboxes),
            "total_executions": len(self.execution_history),
            "sandboxes": list(self.active_sandboxes.values()),
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return [r.to_dict() for r in self.execution_history[-limit:]]

    async def cleanup_all(self):
        """Cleanup all resources"""
        logger.info("Cleaning up all sandboxes...")
        sandbox_ids = list(self.active_sandboxes.keys())
        for sandbox_id in sandbox_ids:
            await self.cleanup_sandbox(sandbox_id)

        await self.webhook_client.cleanup()
        logger.info("Cleanup complete")


# Command-line interface
async def main():
    """CLI interface for sandbox manager"""
    import argparse

    parser = argparse.ArgumentParser(description="E2B Sandbox Manager")
    parser.add_argument("--api-key", default=os.getenv("E2B_API_KEY"))
    parser.add_argument("--config", default="/home/user/Private-Claude/config/e2b_sandbox_templates.json")

    subparsers = parser.add_subparsers(dest="command")

    # Create sandbox
    create_parser = subparsers.add_parser("create", help="Create sandbox")
    create_parser.add_argument("--template", default="python")
    create_parser.add_argument("--sandbox-id", help="Custom sandbox ID")

    # Execute code
    exec_parser = subparsers.add_parser("exec", help="Execute code")
    exec_parser.add_argument("--sandbox-id", required=True)
    exec_parser.add_argument("--language", default="python")
    exec_parser.add_argument("--code", required=True)

    # List status
    subparsers.add_parser("status", help="Show status")

    # Stop sandbox
    stop_parser = subparsers.add_parser("stop", help="Stop sandbox")
    stop_parser.add_argument("--sandbox-id", required=True)

    # Cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup sandbox")
    cleanup_parser.add_argument("--sandbox-id", required=True)

    args = parser.parse_args()

    # Initialize manager
    manager = E2BSandboxManager(api_key=args.api_key, config_path=args.config)
    await manager.webhook_client.initialize()

    try:
        if args.command == "create":
            result = await manager.create_sandbox(args.template, args.sandbox_id)
            print(json.dumps(result, indent=2))

        elif args.command == "exec":
            result = await manager.execute_code(args.sandbox_id, args.code, args.language)
            print(json.dumps(result.to_dict(), indent=2))

        elif args.command == "status":
            result = await manager.get_status()
            print(json.dumps(result, indent=2))

        elif args.command == "stop":
            result = await manager.stop_sandbox(args.sandbox_id)
            print(json.dumps(result, indent=2))

        elif args.command == "cleanup":
            result = await manager.cleanup_sandbox(args.sandbox_id)
            print(json.dumps(result, indent=2))

        else:
            parser.print_help()

    finally:
        await manager.cleanup_all()


if __name__ == "__main__":
    asyncio.run(main())
