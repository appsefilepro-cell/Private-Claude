#!/usr/bin/env python3
"""
E2B Docker Sandbox Launcher for Agent X5.0
==========================================

This script launches the Agent X5 system with Docker containers in an E2B cloud sandbox.
It handles:
- Sandbox creation with Docker support
- File upload (Dockerfile, docker-compose.yml, all code)
- Docker container build and run
- Agent orchestration
- Result retrieval

Usage:
    python scripts/e2b_sandbox_launcher.py

Environment:
    E2B_API_KEY: Your E2B API key (required)

Documentation: https://e2b.dev/docs
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# E2B API Key from environment
E2B_API_KEY = os.getenv("E2B_API_KEY")
if not E2B_API_KEY:
    print("ERROR: E2B_API_KEY environment variable not set")
    print("Get your API key at: https://e2b.dev/dashboard")
    sys.exit(1)

WORKSPACE_ROOT = Path(__file__).parent.parent


class E2BDockerSandbox:
    """
    E2B Docker Sandbox for Agent X5.0

    Runs the full Agent X5 system with Docker containers
    inside an E2B cloud sandbox.
    """

    def __init__(self):
        self.api_key = E2B_API_KEY
        self.sandbox = None
        self.sandbox_id = None
        self.ports = {}

    async def create_sandbox(self) -> str:
        """Create E2B sandbox with Docker support"""
        try:
            from e2b import Sandbox
        except ImportError:
            print("Installing E2B SDK...")
            os.system("pip install e2b")
            from e2b import Sandbox

        print("=" * 60)
        print("CREATING E2B DOCKER SANDBOX")
        print("=" * 60)

        # Create sandbox using base template (has Docker)
        self.sandbox = Sandbox(
            template="base",
            api_key=self.api_key,
            timeout=3600  # 1 hour
        )
        self.sandbox_id = self.sandbox.id

        print(f"✅ Sandbox created: {self.sandbox_id}")
        print(f"   Template: base (Docker enabled)")
        print(f"   Timeout: 3600s")

        return self.sandbox_id

    async def upload_project_files(self):
        """Upload all project files to sandbox"""
        print("\n" + "=" * 60)
        print("UPLOADING PROJECT FILES TO SANDBOX")
        print("=" * 60)

        files_to_upload = [
            ("Dockerfile", "Dockerfile"),
            ("docker-compose.yml", "docker-compose.yml"),
            ("requirements.txt", "requirements.txt"),
            ("e2b.toml", "e2b.toml"),
        ]

        # Upload individual files
        for local_name, remote_name in files_to_upload:
            local_path = WORKSPACE_ROOT / local_name
            if local_path.exists():
                content = local_path.read_text()
                self.sandbox.filesystem.write(f"/home/user/{remote_name}", content)
                print(f"  ✅ {remote_name}")

        # Upload directories
        dirs_to_upload = [
            "scripts",
            "config",
        ]

        for dir_name in dirs_to_upload:
            dir_path = WORKSPACE_ROOT / dir_name
            if dir_path.exists():
                await self._upload_directory(dir_path, f"/home/user/{dir_name}")
                print(f"  ✅ {dir_name}/")

        print("\n✅ All files uploaded successfully")

    async def _upload_directory(self, local_dir: Path, remote_dir: str):
        """Recursively upload a directory"""
        self.sandbox.filesystem.make_dir(remote_dir)

        for item in local_dir.iterdir():
            remote_path = f"{remote_dir}/{item.name}"

            if item.is_file() and not item.name.endswith('.pyc'):
                try:
                    content = item.read_text()
                    self.sandbox.filesystem.write(remote_path, content)
                except:
                    # Binary file - read as bytes
                    content = item.read_bytes()
                    self.sandbox.filesystem.write(remote_path, content)
            elif item.is_dir() and item.name not in ['__pycache__', '.git', 'venv']:
                await self._upload_directory(item, remote_path)

    async def install_dependencies(self):
        """Install Python dependencies in sandbox"""
        print("\n" + "=" * 60)
        print("INSTALLING DEPENDENCIES")
        print("=" * 60)

        # Install Python packages
        result = self.sandbox.process.start_and_wait(
            "pip install -r /home/user/requirements.txt",
            timeout=300
        )

        if result.exit_code == 0:
            print("✅ Python dependencies installed")
        else:
            print(f"⚠️  Some packages may have failed: {result.stderr}")

    async def build_docker_images(self):
        """Build Docker images in sandbox"""
        print("\n" + "=" * 60)
        print("BUILDING DOCKER IMAGES")
        print("=" * 60)

        # Check if Docker is available
        result = self.sandbox.process.start_and_wait("docker --version")
        if result.exit_code != 0:
            print("⚠️  Docker not available in sandbox, running Python directly")
            return False

        print(f"Docker version: {result.stdout.strip()}")

        # Build the main image
        result = self.sandbox.process.start_and_wait(
            "cd /home/user && docker build -t agent-x5:latest .",
            timeout=600
        )

        if result.exit_code == 0:
            print("✅ Docker image built: agent-x5:latest")
            return True
        else:
            print(f"⚠️  Docker build failed: {result.stderr}")
            return False

    async def run_docker_compose(self):
        """Run docker-compose in sandbox"""
        print("\n" + "=" * 60)
        print("STARTING DOCKER CONTAINERS")
        print("=" * 60)

        result = self.sandbox.process.start_and_wait(
            "cd /home/user && docker-compose up -d",
            timeout=300
        )

        if result.exit_code == 0:
            print("✅ Docker containers started")

            # Get container status
            status = self.sandbox.process.start_and_wait("docker ps")
            print(f"\nRunning containers:\n{status.stdout}")
            return True
        else:
            print(f"⚠️  Docker-compose failed: {result.stderr}")
            return False

    async def run_agent_x5_direct(self):
        """Run Agent X5 directly (fallback if Docker unavailable)"""
        print("\n" + "=" * 60)
        print("RUNNING AGENT X5 DIRECTLY IN SANDBOX")
        print("=" * 60)

        # Run the orchestrator
        process = self.sandbox.process.start(
            "cd /home/user && python scripts/agent_x5_master_orchestrator.py"
        )

        # Wait for output
        output = process.wait(timeout=120)

        print(output.stdout)
        if output.stderr:
            print(f"Errors: {output.stderr}")

        return output.exit_code == 0

    async def get_sandbox_urls(self) -> Dict[str, str]:
        """Get public URLs for sandbox ports"""
        urls = {}

        try:
            # Get URLs for exposed ports
            url_8080 = self.sandbox.get_host_and_port(8080)
            urls["agent-x5"] = f"https://{url_8080}"

            url_8081 = self.sandbox.get_host_and_port(8081)
            urls["agent-4"] = f"https://{url_8081}"

            url_8082 = self.sandbox.get_host_and_port(8082)
            urls["trading"] = f"https://{url_8082}"
        except Exception as e:
            print(f"Could not get port URLs: {e}")

        return urls

    async def get_status(self) -> Dict[str, Any]:
        """Get current sandbox status"""
        status = {
            "sandbox_id": self.sandbox_id,
            "status": "RUNNING" if self.sandbox else "NOT_CREATED",
            "timestamp": datetime.utcnow().isoformat(),
            "trading_mode": "PAPER",
            "live_trading": False
        }

        if self.sandbox:
            # Check container status
            result = self.sandbox.process.start_and_wait("docker ps --format '{{.Names}}: {{.Status}}'")
            if result.exit_code == 0:
                status["containers"] = result.stdout.strip().split('\n')

        return status

    async def close(self):
        """Close and cleanup sandbox"""
        if self.sandbox:
            self.sandbox.close()
            print("\n✅ Sandbox closed")


async def main():
    """Main execution - Launch Agent X5 in E2B Docker Sandbox"""
    print("=" * 60)
    print("E2B DOCKER SANDBOX LAUNCHER - AGENT X5.0")
    print("=" * 60)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Workspace: {WORKSPACE_ROOT}")
    print(f"API Key: {E2B_API_KEY[:10]}..." if E2B_API_KEY else "NOT SET")
    print("=" * 60)

    sandbox = E2BDockerSandbox()

    try:
        # 1. Create sandbox
        await sandbox.create_sandbox()

        # 2. Upload project files
        await sandbox.upload_project_files()

        # 3. Install dependencies
        await sandbox.install_dependencies()

        # 4. Try Docker first, fallback to direct execution
        docker_available = await sandbox.build_docker_images()

        if docker_available:
            await sandbox.run_docker_compose()
            urls = await sandbox.get_sandbox_urls()
            if urls:
                print("\n" + "=" * 60)
                print("SANDBOX URLS (Public Access)")
                print("=" * 60)
                for service, url in urls.items():
                    print(f"  {service}: {url}")
        else:
            # Fallback: run directly
            await sandbox.run_agent_x5_direct()

        # 5. Get final status
        status = await sandbox.get_status()
        print("\n" + "=" * 60)
        print("FINAL STATUS")
        print("=" * 60)
        print(json.dumps(status, indent=2))

        print("\n" + "=" * 60)
        print("✅ AGENT X5 RUNNING IN E2B CLOUD SANDBOX")
        print("=" * 60)
        print("\nSandbox will remain active for 1 hour.")
        print("Press Ctrl+C to close sandbox early.")

        # Keep sandbox alive
        try:
            while True:
                await asyncio.sleep(60)
                status = await sandbox.get_status()
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Status: Running | Containers: {len(status.get('containers', []))}")
        except KeyboardInterrupt:
            print("\nShutting down...")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        await sandbox.close()


if __name__ == "__main__":
    asyncio.run(main())
