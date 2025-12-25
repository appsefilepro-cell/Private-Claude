"""
E2B Sandbox Integration Module
Provides comprehensive API client for E2B code execution sandboxes
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import requests
from dataclasses import dataclass, asdict


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SandboxStatus(Enum):
    """Sandbox execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    BASH = "bash"
    GO = "go"
    RUST = "rust"


@dataclass
class ExecutionResult:
    """Result from code execution"""
    sandbox_id: str
    status: SandboxStatus
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    timestamp: datetime
    language: Language
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['status'] = self.status.value
        result['language'] = self.language.value
        result['timestamp'] = self.timestamp.isoformat()
        return result

    def is_success(self) -> bool:
        """Check if execution was successful"""
        return self.status == SandboxStatus.COMPLETED and self.exit_code == 0


@dataclass
class SandboxConfig:
    """Configuration for sandbox environment"""
    timeout: int = 300  # seconds
    memory_limit: int = 512  # MB
    cpu_limit: float = 1.0  # cores
    network_enabled: bool = True
    filesystem_enabled: bool = True
    environment_vars: Dict[str, str] = None

    def __post_init__(self):
        if self.environment_vars is None:
            self.environment_vars = {}


class E2BSandboxClient:
    """
    Complete E2B Sandbox API Client
    Handles code execution, file management, and sandbox lifecycle
    """

    BASE_URL = "https://api.e2b.dev/v1"

    def __init__(self, api_key: str):
        """
        Initialize E2B client

        Args:
            api_key: E2B API key
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        logger.info("E2B Sandbox Client initialized")

    def create_sandbox(self,
                      template: str = "base",
                      config: Optional[SandboxConfig] = None) -> str:
        """
        Create a new sandbox instance

        Args:
            template: Sandbox template to use
            config: Sandbox configuration

        Returns:
            Sandbox ID
        """
        if config is None:
            config = SandboxConfig()

        payload = {
            "template": template,
            "timeout": config.timeout,
            "envVars": config.environment_vars
        }

        try:
            response = self.session.post(
                f"{self.BASE_URL}/sandboxes",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            sandbox_id = data.get("sandboxId") or data.get("id")

            logger.info(f"Created sandbox: {sandbox_id}")
            return sandbox_id

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create sandbox: {e}")
            raise

    def execute_code(self,
                    code: str,
                    language: Language = Language.PYTHON,
                    sandbox_id: Optional[str] = None,
                    config: Optional[SandboxConfig] = None) -> ExecutionResult:
        """
        Execute code in sandbox

        Args:
            code: Code to execute
            language: Programming language
            sandbox_id: Existing sandbox ID (creates new if None)
            config: Sandbox configuration

        Returns:
            ExecutionResult with output and metadata
        """
        start_time = time.time()

        # Create sandbox if not provided
        if sandbox_id is None:
            sandbox_id = self.create_sandbox(
                template=language.value,
                config=config
            )

        # Execute code
        try:
            payload = {
                "code": code,
                "language": language.value
            }

            response = self.session.post(
                f"{self.BASE_URL}/sandboxes/{sandbox_id}/execute",
                json=payload,
                timeout=config.timeout if config else 300
            )
            response.raise_for_status()

            data = response.json()
            execution_time = time.time() - start_time

            result = ExecutionResult(
                sandbox_id=sandbox_id,
                status=SandboxStatus.COMPLETED,
                stdout=data.get("stdout", ""),
                stderr=data.get("stderr", ""),
                exit_code=data.get("exitCode", 0),
                execution_time=execution_time,
                timestamp=datetime.now(),
                language=language,
                metadata=data.get("metadata", {})
            )

            logger.info(f"Code executed in {execution_time:.2f}s")
            return result

        except requests.exceptions.Timeout:
            logger.error("Code execution timeout")
            return ExecutionResult(
                sandbox_id=sandbox_id,
                status=SandboxStatus.TIMEOUT,
                stdout="",
                stderr="Execution timeout",
                exit_code=-1,
                execution_time=time.time() - start_time,
                timestamp=datetime.now(),
                language=language,
                metadata={}
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Code execution failed: {e}")
            return ExecutionResult(
                sandbox_id=sandbox_id,
                status=SandboxStatus.FAILED,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=time.time() - start_time,
                timestamp=datetime.now(),
                language=language,
                metadata={}
            )

    def execute_file(self,
                    file_path: str,
                    language: Language,
                    sandbox_id: Optional[str] = None,
                    config: Optional[SandboxConfig] = None) -> ExecutionResult:
        """
        Execute code from file

        Args:
            file_path: Path to code file
            language: Programming language
            sandbox_id: Existing sandbox ID
            config: Sandbox configuration

        Returns:
            ExecutionResult
        """
        with open(file_path, 'r') as f:
            code = f.read()

        return self.execute_code(code, language, sandbox_id, config)

    def upload_file(self,
                   sandbox_id: str,
                   local_path: str,
                   remote_path: str) -> bool:
        """
        Upload file to sandbox

        Args:
            sandbox_id: Sandbox ID
            local_path: Local file path
            remote_path: Remote path in sandbox

        Returns:
            Success status
        """
        try:
            with open(local_path, 'rb') as f:
                files = {'file': f}
                data = {'path': remote_path}

                response = self.session.post(
                    f"{self.BASE_URL}/sandboxes/{sandbox_id}/files",
                    files=files,
                    data=data,
                    timeout=60
                )
                response.raise_for_status()

            logger.info(f"Uploaded {local_path} to {remote_path}")
            return True

        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return False

    def download_file(self,
                     sandbox_id: str,
                     remote_path: str,
                     local_path: str) -> bool:
        """
        Download file from sandbox

        Args:
            sandbox_id: Sandbox ID
            remote_path: Remote path in sandbox
            local_path: Local file path

        Returns:
            Success status
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/sandboxes/{sandbox_id}/files",
                params={"path": remote_path},
                timeout=60
            )
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded {remote_path} to {local_path}")
            return True

        except Exception as e:
            logger.error(f"File download failed: {e}")
            return False

    def list_files(self, sandbox_id: str, path: str = "/") -> List[Dict]:
        """
        List files in sandbox directory

        Args:
            sandbox_id: Sandbox ID
            path: Directory path

        Returns:
            List of file information dictionaries
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/sandboxes/{sandbox_id}/files/list",
                params={"path": path},
                timeout=30
            )
            response.raise_for_status()

            return response.json().get("files", [])

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def get_sandbox_status(self, sandbox_id: str) -> Dict:
        """
        Get sandbox status and information

        Args:
            sandbox_id: Sandbox ID

        Returns:
            Sandbox status dictionary
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/sandboxes/{sandbox_id}",
                timeout=30
            )
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Failed to get sandbox status: {e}")
            return {}

    def delete_sandbox(self, sandbox_id: str) -> bool:
        """
        Delete sandbox

        Args:
            sandbox_id: Sandbox ID

        Returns:
            Success status
        """
        try:
            response = self.session.delete(
                f"{self.BASE_URL}/sandboxes/{sandbox_id}",
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Deleted sandbox: {sandbox_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete sandbox: {e}")
            return False

    def list_sandboxes(self) -> List[Dict]:
        """
        List all sandboxes

        Returns:
            List of sandbox information dictionaries
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/sandboxes",
                timeout=30
            )
            response.raise_for_status()

            return response.json().get("sandboxes", [])

        except Exception as e:
            logger.error(f"Failed to list sandboxes: {e}")
            return []

    def install_package(self,
                       sandbox_id: str,
                       package: str,
                       language: Language = Language.PYTHON) -> bool:
        """
        Install package in sandbox

        Args:
            sandbox_id: Sandbox ID
            package: Package name
            language: Programming language

        Returns:
            Success status
        """
        install_commands = {
            Language.PYTHON: f"pip install {package}",
            Language.JAVASCRIPT: f"npm install {package}",
            Language.TYPESCRIPT: f"npm install {package}",
            Language.GO: f"go get {package}",
            Language.RUST: f"cargo add {package}"
        }

        command = install_commands.get(language)
        if not command:
            logger.error(f"Unsupported language: {language}")
            return False

        result = self.execute_code(
            command,
            Language.BASH,
            sandbox_id
        )

        return result.is_success()

    def close(self):
        """Close session"""
        self.session.close()
        logger.info("E2B client session closed")


class SandboxPool:
    """
    Pool of reusable sandboxes for improved performance
    """

    def __init__(self, client: E2BSandboxClient, pool_size: int = 5):
        """
        Initialize sandbox pool

        Args:
            client: E2B client instance
            pool_size: Number of sandboxes to maintain
        """
        self.client = client
        self.pool_size = pool_size
        self.available: List[str] = []
        self.in_use: set = set()
        self.lock = asyncio.Lock()

        logger.info(f"Initialized sandbox pool with size {pool_size}")

    async def initialize(self):
        """Initialize pool with sandboxes"""
        for _ in range(self.pool_size):
            try:
                sandbox_id = self.client.create_sandbox()
                self.available.append(sandbox_id)
            except Exception as e:
                logger.error(f"Failed to create pool sandbox: {e}")

    async def acquire(self) -> Optional[str]:
        """
        Acquire sandbox from pool

        Returns:
            Sandbox ID or None if unavailable
        """
        async with self.lock:
            if self.available:
                sandbox_id = self.available.pop()
                self.in_use.add(sandbox_id)
                logger.debug(f"Acquired sandbox: {sandbox_id}")
                return sandbox_id
            else:
                # Create new sandbox if pool is empty
                try:
                    sandbox_id = self.client.create_sandbox()
                    self.in_use.add(sandbox_id)
                    return sandbox_id
                except Exception as e:
                    logger.error(f"Failed to create sandbox: {e}")
                    return None

    async def release(self, sandbox_id: str):
        """
        Release sandbox back to pool

        Args:
            sandbox_id: Sandbox ID to release
        """
        async with self.lock:
            if sandbox_id in self.in_use:
                self.in_use.remove(sandbox_id)

                if len(self.available) < self.pool_size:
                    self.available.append(sandbox_id)
                    logger.debug(f"Released sandbox to pool: {sandbox_id}")
                else:
                    # Pool is full, delete sandbox
                    self.client.delete_sandbox(sandbox_id)
                    logger.debug(f"Deleted excess sandbox: {sandbox_id}")

    async def cleanup(self):
        """Clean up all sandboxes in pool"""
        async with self.lock:
            all_sandboxes = self.available + list(self.in_use)
            for sandbox_id in all_sandboxes:
                try:
                    self.client.delete_sandbox(sandbox_id)
                except Exception as e:
                    logger.error(f"Failed to delete sandbox {sandbox_id}: {e}")

            self.available.clear()
            self.in_use.clear()
            logger.info("Sandbox pool cleaned up")


def main():
    """Example usage"""
    # Initialize client
    api_key = os.getenv("E2B_API_KEY", "e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773")
    client = E2BSandboxClient(api_key)

    # Example: Execute Python code
    code = """
import sys
print("Hello from E2B Sandbox!")
print(f"Python version: {sys.version}")
    """

    result = client.execute_code(code, Language.PYTHON)

    print(f"Status: {result.status.value}")
    print(f"Exit Code: {result.exit_code}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"Output:\n{result.stdout}")

    if result.stderr:
        print(f"Errors:\n{result.stderr}")

    # Clean up
    client.delete_sandbox(result.sandbox_id)
    client.close()


if __name__ == "__main__":
    main()
