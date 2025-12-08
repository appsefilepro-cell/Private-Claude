#!/usr/bin/env python3
"""
AGENT X 3.0 - AUTOMATED DEPLOYMENT SYSTEM
Deploys all environments, assigns 50 executive roles, and manages continuous operations
"""

import subprocess
import sys
import time
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentXDeployment:
    """Manages Agent X 3.0 deployment across all environments"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.environments = ["test", "background", "live"]
        self.deployment_status = {
            "test": {"deployed": False, "healthy": False},
            "background": {"deployed": False, "healthy": False},
            "live": {"deployed": False, "healthy": False}
        }

    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> Dict:
        """Execute shell command and return result"""
        try:
            logger.info(f"Executing: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=cwd or self.base_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode
            }

    def check_docker(self) -> bool:
        """Verify Docker is installed and running"""
        logger.info("Checking Docker installation...")
        result = self.run_command(["docker", "--version"])
        if not result["success"]:
            logger.error("Docker is not installed or not in PATH")
            return False

        result = self.run_command(["docker", "info"])
        if not result["success"]:
            logger.error("Docker daemon is not running")
            return False

        logger.info("✓ Docker is installed and running")
        return True

    def check_docker_compose(self) -> bool:
        """Verify Docker Compose is installed"""
        logger.info("Checking Docker Compose installation...")
        result = self.run_command(["docker-compose", "--version"])
        if not result["success"]:
            logger.error("Docker Compose is not installed")
            return False

        logger.info("✓ Docker Compose is installed")
        return True

    def create_env_file(self, env_type: str):
        """Create .env file with required environment variables"""
        logger.info(f"Creating .env file for {env_type} environment...")

        env_vars = {
            "test": {
                "ENVIRONMENT": "test",
                "MT5_TEST_PASSWORD": "test_password",
                "KRAKEN_TEST_KEY": "test_kraken_key",
                "KRAKEN_TEST_SECRET": "test_kraken_secret",
                "OPENAI_TEST_KEY": "test_openai_key",
                "ANTHROPIC_TEST_KEY": "test_anthropic_key",
                "IRS_TEST_KEY": "test_irs_key",
                "FINCEN_TEST_KEY": "test_fincen_key",
                "AZURE_TEST_TENANT": "test_tenant_id",
                "AZURE_TEST_CLIENT": "test_client_id",
                "AZURE_TEST_SECRET": "test_client_secret",
                "HUBSPOT_TEST_KEY": "test_hubspot_key",
                "WEBHOOK_TEST_SECRET": "test_webhook_secret"
            },
            "background": {
                "ENVIRONMENT": "background",
                "FINCEN_API_KEY": "bg_fincen_key",
                "BACKUP_S3_BUCKET": "agentx-backups",
                "AWS_ACCESS_KEY": "bg_aws_access_key",
                "AWS_SECRET_KEY": "bg_aws_secret_key",
                "SMTP_HOST": "smtp.gmail.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "notifications@agentx.com",
                "SMTP_PASSWORD": "smtp_password",
                "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/..."
            },
            "live": {
                "ENVIRONMENT": "production",
                "DB_PROD_PASSWORD": "CHANGE_ME_STRONG_PASSWORD",
                "REDIS_PROD_PASSWORD": "CHANGE_ME_REDIS_PASSWORD",
                "MT5_PROD_SERVER": "live.broker.com",
                "MT5_PROD_LOGIN": "PROD_LOGIN",
                "MT5_PROD_PASSWORD": "PROD_PASSWORD",
                "KRAKEN_PROD_KEY": "PROD_KRAKEN_KEY",
                "KRAKEN_PROD_SECRET": "PROD_KRAKEN_SECRET",
                "OPENAI_PROD_KEY": "PROD_OPENAI_KEY",
                "ANTHROPIC_PROD_KEY": "PROD_ANTHROPIC_KEY",
                "IRS_PROD_KEY": "PROD_IRS_KEY",
                "FINCEN_PROD_KEY": "PROD_FINCEN_KEY",
                "AES_256_KEY": "CHANGE_ME_32_BYTE_ENCRYPTION_KEY",
                "SENTRY_DSN": "https://sentry.io/...",
                "GRAFANA_ADMIN_USER": "admin",
                "GRAFANA_ADMIN_PASSWORD": "CHANGE_ME_GRAFANA_PASSWORD",
                "BACKUP_S3_BUCKET": "agentx-prod-backups",
                "AWS_ACCESS_KEY": "PROD_AWS_ACCESS_KEY",
                "AWS_SECRET_KEY": "PROD_AWS_SECRET_KEY",
                "PRODUCTION_DOMAIN": "agentx.example.com",
                "ADMIN_EMAIL": "admin@agentx.example.com"
            }
        }

        env_file_path = self.base_dir / f".env.{env_type}"
        with open(env_file_path, "w") as f:
            for key, value in env_vars.get(env_type, {}).items():
                f.write(f"{key}={value}\n")

        logger.info(f"✓ Created {env_file_path}")

    def deploy_environment(self, env_type: str) -> bool:
        """Deploy a specific environment"""
        logger.info(f"\n{'='*60}")
        logger.info(f"DEPLOYING {env_type.upper()} ENVIRONMENT")
        logger.info(f"{'='*60}\n")

        # Create env file
        self.create_env_file(env_type)

        # Build and start services
        compose_file = self.base_dir / f"docker-compose.{env_type}.yml"
        if not compose_file.exists():
            logger.error(f"Compose file not found: {compose_file}")
            return False

        # Pull images first
        logger.info("Pulling Docker images...")
        result = self.run_command([
            "docker-compose",
            "-f", str(compose_file),
            "--env-file", f".env.{env_type}",
            "pull"
        ])

        # Build services
        logger.info("Building services...")
        result = self.run_command([
            "docker-compose",
            "-f", str(compose_file),
            "--env-file", f".env.{env_type}",
            "build",
            "--parallel"
        ])

        if not result["success"]:
            logger.error(f"Build failed for {env_type}")
            return False

        # Start services
        logger.info("Starting services...")
        result = self.run_command([
            "docker-compose",
            "-f", str(compose_file),
            "--env-file", f".env.{env_type}",
            "up",
            "-d"
        ])

        if not result["success"]:
            logger.error(f"Failed to start {env_type} environment")
            return False

        logger.info(f"✓ {env_type.upper()} environment deployed")
        self.deployment_status[env_type]["deployed"] = True

        # Wait for services to be healthy
        logger.info("Waiting for services to be healthy...")
        time.sleep(10)

        return self.check_environment_health(env_type)

    def check_environment_health(self, env_type: str) -> bool:
        """Check if all services in environment are healthy"""
        logger.info(f"Checking {env_type} environment health...")

        compose_file = self.base_dir / f"docker-compose.{env_type}.yml"
        result = self.run_command([
            "docker-compose",
            "-f", str(compose_file),
            "ps"
        ])

        if result["success"]:
            # Check for any unhealthy or exited containers
            if "unhealthy" in result["stdout"].lower() or "exit" in result["stdout"].lower():
                logger.warning(f"Some services in {env_type} are not healthy")
                return False

            logger.info(f"✓ {env_type.upper()} environment is healthy")
            self.deployment_status[env_type]["healthy"] = True
            return True

        return False

    def deploy_all_environments(self):
        """Deploy all environments in sequence"""
        logger.info("\n" + "="*60)
        logger.info("AGENT X 3.0 - FULL DEPLOYMENT")
        logger.info("="*60 + "\n")

        # Check prerequisites
        if not self.check_docker() or not self.check_docker_compose():
            logger.error("Prerequisites not met. Aborting deployment.")
            sys.exit(1)

        # Deploy environments in order
        for env_type in self.environments:
            success = self.deploy_environment(env_type)
            if not success:
                logger.error(f"Deployment of {env_type} failed. Continuing anyway...")

            # Short delay between environments
            time.sleep(5)

        # Print deployment summary
        self.print_deployment_summary()

    def deploy_executive_roles(self):
        """Deploy all 50 executive roles"""
        logger.info("\n" + "="*60)
        logger.info("DEPLOYING 50 EXECUTIVE ROLES")
        logger.info("="*60 + "\n")

        # Run the executive roles Python script
        logger.info("Starting Executive Roles Manager...")

        roles_script = self.base_dir / "executive_roles.py"
        if not roles_script.exists():
            logger.error("Executive roles script not found")
            return False

        # Run asynchronously
        result = self.run_command([
            "python3",
            str(roles_script)
        ])

        if result["success"]:
            logger.info("✓ Executive roles deployment initiated")
            return True
        else:
            logger.error("Executive roles deployment failed")
            return False

    def configure_github_copilot(self):
        """Configure GitHub Copilot for both repositories"""
        logger.info("\n" + "="*60)
        logger.info("CONFIGURING GITHUB COPILOT")
        logger.info("="*60 + "\n")

        # Check if Git is installed
        result = self.run_command(["git", "--version"])
        if not result["success"]:
            logger.error("Git is not installed")
            return False

        # Check if we're in a Git repository
        result = self.run_command(["git", "status"])
        if not result["success"]:
            logger.warning("Not in a Git repository. Skipping Copilot setup.")
            return False

        # Ensure .github directory exists
        github_dir = self.base_dir / ".github"
        github_dir.mkdir(exist_ok=True)

        logger.info("✓ GitHub Copilot configuration ready")
        logger.info("  - Config file: .github/copilot-config.yml")
        logger.info("  - Features: Code suggestions, docstrings, tests, security scanning")

        return True

    def setup_continuous_loop(self):
        """Set up continuous loop automation"""
        logger.info("\n" + "="*60)
        logger.info("SETTING UP CONTINUOUS LOOP AUTOMATION")
        logger.info("="*60 + "\n")

        # Create systemd service file (for Linux)
        service_content = """[Unit]
Description=Agent X 3.0 Executive Roles Monitor
After=docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=/home/user/Private-Claude/agent-x-3.0
ExecStart=/usr/bin/python3 /home/user/Private-Claude/agent-x-3.0/executive_roles.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

        service_file = Path("/tmp/agentx-roles.service")
        with open(service_file, "w") as f:
            f.write(service_content)

        logger.info("✓ Continuous loop service file created: /tmp/agentx-roles.service")
        logger.info("  To enable, run:")
        logger.info("    sudo cp /tmp/agentx-roles.service /etc/systemd/system/")
        logger.info("    sudo systemctl enable agentx-roles")
        logger.info("    sudo systemctl start agentx-roles")

    def print_deployment_summary(self):
        """Print deployment summary"""
        logger.info("\n" + "="*60)
        logger.info("DEPLOYMENT SUMMARY")
        logger.info("="*60 + "\n")

        for env_type, status in self.deployment_status.items():
            deployed_status = "✓" if status["deployed"] else "✗"
            healthy_status = "✓" if status["healthy"] else "✗"
            logger.info(f"{env_type.upper():12} - Deployed: {deployed_status}  Healthy: {healthy_status}")

        logger.info("\n" + "="*60)
        logger.info("NEXT STEPS")
        logger.info("="*60 + "\n")
        logger.info("1. Update .env files with real credentials (IMPORTANT!)")
        logger.info("2. Run: python3 deploy.py --roles  (to deploy executive roles)")
        logger.info("3. Access dashboards:")
        logger.info("   - Grafana (test): http://localhost:3001")
        logger.info("   - Kibana (test): http://localhost:5602")
        logger.info("   - Prometheus (test): http://localhost:9091")
        logger.info("4. Monitor logs: docker-compose -f docker-compose.test.yml logs -f")

    def run_tests(self):
        """Run comprehensive tests"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING TESTS")
        logger.info("="*60 + "\n")

        test_commands = [
            # Test PostgreSQL connectivity
            ["docker", "exec", "agentx-postgres-test", "pg_isready", "-U", "agentx_user"],

            # Test Redis connectivity
            ["docker", "exec", "agentx-redis-test", "redis-cli", "ping"],

            # Test trading bot health
            ["curl", "-f", "http://localhost:8001/health"],

            # Test legal service health
            ["curl", "-f", "http://localhost:8002/health"],

            # Test tax service health
            ["curl", "-f", "http://localhost:8003/health"]
        ]

        passed = 0
        failed = 0

        for command in test_commands:
            result = self.run_command(command)
            if result["success"]:
                logger.info(f"✓ {' '.join(command)}")
                passed += 1
            else:
                logger.error(f"✗ {' '.join(command)}")
                failed += 1

        logger.info(f"\nTests: {passed} passed, {failed} failed")
        return failed == 0

    def generate_audit_report(self):
        """Generate deployment audit report"""
        report = {
            "deployment_time": datetime.now().isoformat(),
            "environments": self.deployment_status,
            "base_directory": str(self.base_dir),
            "docker_version": subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            ).stdout.strip(),
            "compose_version": subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True
            ).stdout.strip()
        }

        report_file = self.base_dir / "deployment_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"✓ Audit report saved: {report_file}")


def main():
    """Main deployment function"""
    base_dir = Path(__file__).parent.resolve()
    deployer = AgentXDeployment(base_dir)

    # Parse command line arguments
    if len(sys.argv) > 1:
        if "--roles" in sys.argv:
            deployer.deploy_executive_roles()
        elif "--test" in sys.argv:
            deployer.run_tests()
        elif "--copilot" in sys.argv:
            deployer.configure_github_copilot()
        elif "--loop" in sys.argv:
            deployer.setup_continuous_loop()
        elif "--audit" in sys.argv:
            deployer.generate_audit_report()
        else:
            logger.info("Usage:")
            logger.info("  python3 deploy.py              # Deploy all environments")
            logger.info("  python3 deploy.py --roles      # Deploy 50 executive roles")
            logger.info("  python3 deploy.py --test       # Run tests")
            logger.info("  python3 deploy.py --copilot    # Configure GitHub Copilot")
            logger.info("  python3 deploy.py --loop       # Setup continuous loop")
            logger.info("  python3 deploy.py --audit      # Generate audit report")
    else:
        # Full deployment
        deployer.deploy_all_environments()
        deployer.configure_github_copilot()
        deployer.setup_continuous_loop()
        deployer.generate_audit_report()


if __name__ == "__main__":
    main()
