"""
GitHub Connector for E2B Sandbox Integration
Handles automated deployments and CI/CD integration
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import base64

from e2b_sandbox import E2BSandboxClient, Language, ExecutionResult


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"


@dataclass
class DeploymentResult:
    """Result from deployment"""
    deployment_id: str
    status: DeploymentStatus
    repository: str
    branch: str
    commit_sha: str
    timestamp: datetime
    sandbox_id: Optional[str]
    execution_result: Optional[ExecutionResult]
    logs: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['status'] = self.status.value
        result['timestamp'] = self.timestamp.isoformat()
        if self.execution_result:
            result['execution_result'] = self.execution_result.to_dict()
        return result


class GitHubConnector:
    """
    GitHub integration for E2B sandbox
    Handles repository operations and automated deployments
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, github_token: str, e2b_client: E2BSandboxClient):
        """
        Initialize GitHub connector

        Args:
            github_token: GitHub personal access token
            e2b_client: E2B sandbox client instance
        """
        self.github_token = github_token
        self.e2b_client = e2b_client
        self.headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        logger.info("GitHub connector initialized")

    def get_repository(self, owner: str, repo: str) -> Dict:
        """
        Get repository information

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository information
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get repository: {e}")
            return {}

    def get_file_content(self,
                        owner: str,
                        repo: str,
                        path: str,
                        ref: str = "main") -> Optional[str]:
        """
        Get file content from repository

        Args:
            owner: Repository owner
            repo: Repository name
            path: File path in repository
            ref: Branch or commit reference

        Returns:
            File content as string or None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            content_encoded = data.get("content", "")

            # Decode base64 content
            content = base64.b64decode(content_encoded).decode('utf-8')
            return content

        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
            return None

    def list_repository_files(self,
                             owner: str,
                             repo: str,
                             path: str = "",
                             ref: str = "main") -> List[Dict]:
        """
        List files in repository directory

        Args:
            owner: Repository owner
            repo: Repository name
            path: Directory path
            ref: Branch or commit reference

        Returns:
            List of file information dictionaries
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref},
                timeout=30
            )
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Failed to list repository files: {e}")
            return []

    def get_latest_commit(self,
                         owner: str,
                         repo: str,
                         branch: str = "main") -> Optional[Dict]:
        """
        Get latest commit from branch

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Commit information or None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/commits/{branch}",
                timeout=30
            )
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Failed to get latest commit: {e}")
            return None

    def create_deployment_status(self,
                                owner: str,
                                repo: str,
                                deployment_id: int,
                                state: str,
                                description: str = "",
                                log_url: str = "") -> bool:
        """
        Create deployment status

        Args:
            owner: Repository owner
            repo: Repository name
            deployment_id: Deployment ID
            state: Deployment state (pending, success, failure, etc.)
            description: Status description
            log_url: URL to deployment logs

        Returns:
            Success status
        """
        try:
            payload = {
                "state": state,
                "description": description,
                "log_url": log_url
            }

            response = self.session.post(
                f"{self.BASE_URL}/repos/{owner}/{repo}/deployments/{deployment_id}/statuses",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Created deployment status: {state}")
            return True

        except Exception as e:
            logger.error(f"Failed to create deployment status: {e}")
            return False

    def deploy_to_sandbox(self,
                         owner: str,
                         repo: str,
                         branch: str = "main",
                         entry_file: str = "main.py",
                         language: Language = Language.PYTHON) -> DeploymentResult:
        """
        Deploy repository code to E2B sandbox

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch to deploy
            entry_file: Entry point file to execute
            language: Programming language

        Returns:
            DeploymentResult with execution details
        """
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logs = []

        try:
            # Get latest commit
            logs.append(f"Fetching latest commit from {branch}...")
            commit = self.get_latest_commit(owner, repo, branch)
            if not commit:
                raise Exception("Failed to get latest commit")

            commit_sha = commit['sha']
            logs.append(f"Latest commit: {commit_sha[:7]}")

            # Get entry file content
            logs.append(f"Fetching {entry_file}...")
            code = self.get_file_content(owner, repo, entry_file, branch)
            if not code:
                raise Exception(f"Failed to get {entry_file}")

            logs.append(f"Code retrieved ({len(code)} bytes)")

            # Create sandbox and execute
            logs.append("Creating E2B sandbox...")
            sandbox_id = self.e2b_client.create_sandbox(template=language.value)
            logs.append(f"Sandbox created: {sandbox_id}")

            # Execute code
            logs.append("Executing code in sandbox...")
            execution_result = self.e2b_client.execute_code(
                code=code,
                language=language,
                sandbox_id=sandbox_id
            )

            logs.append(f"Execution completed in {execution_result.execution_time:.2f}s")

            # Determine deployment status
            if execution_result.is_success():
                status = DeploymentStatus.SUCCESS
                logs.append("Deployment successful!")
            else:
                status = DeploymentStatus.FAILURE
                logs.append(f"Deployment failed with exit code {execution_result.exit_code}")

            result = DeploymentResult(
                deployment_id=deployment_id,
                status=status,
                repository=f"{owner}/{repo}",
                branch=branch,
                commit_sha=commit_sha,
                timestamp=datetime.now(),
                sandbox_id=sandbox_id,
                execution_result=execution_result,
                logs=logs,
                metadata={
                    "entry_file": entry_file,
                    "language": language.value
                }
            )

            logger.info(f"Deployment {deployment_id}: {status.value}")
            return result

        except Exception as e:
            logs.append(f"Deployment error: {str(e)}")
            logger.error(f"Deployment failed: {e}")

            return DeploymentResult(
                deployment_id=deployment_id,
                status=DeploymentStatus.FAILURE,
                repository=f"{owner}/{repo}",
                branch=branch,
                commit_sha="",
                timestamp=datetime.now(),
                sandbox_id=None,
                execution_result=None,
                logs=logs,
                metadata={"error": str(e)}
            )

    def setup_webhook(self,
                     owner: str,
                     repo: str,
                     webhook_url: str,
                     events: List[str] = None) -> bool:
        """
        Setup GitHub webhook for repository

        Args:
            owner: Repository owner
            repo: Repository name
            webhook_url: Webhook endpoint URL
            events: List of events to trigger webhook

        Returns:
            Success status
        """
        if events is None:
            events = ["push", "pull_request", "deployment"]

        try:
            payload = {
                "name": "web",
                "active": True,
                "events": events,
                "config": {
                    "url": webhook_url,
                    "content_type": "json",
                    "insecure_ssl": "0"
                }
            }

            response = self.session.post(
                f"{self.BASE_URL}/repos/{owner}/{repo}/hooks",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            webhook_id = response.json().get('id')
            logger.info(f"Created webhook {webhook_id} for {owner}/{repo}")
            return True

        except Exception as e:
            logger.error(f"Failed to create webhook: {e}")
            return False

    def trigger_deployment_from_push(self, push_event: Dict) -> Optional[DeploymentResult]:
        """
        Trigger deployment from GitHub push event

        Args:
            push_event: GitHub push event payload

        Returns:
            DeploymentResult or None
        """
        try:
            # Extract repository info
            repository = push_event.get('repository', {})
            owner = repository.get('owner', {}).get('login')
            repo_name = repository.get('name')
            branch = push_event.get('ref', '').replace('refs/heads/', '')

            if not all([owner, repo_name, branch]):
                logger.error("Invalid push event payload")
                return None

            # Check if deployment should be triggered
            # (e.g., only for main branch, specific files changed, etc.)
            if branch not in ['main', 'master', 'develop']:
                logger.info(f"Skipping deployment for branch: {branch}")
                return None

            logger.info(f"Triggering deployment for {owner}/{repo_name}:{branch}")

            # Deploy to sandbox
            result = self.deploy_to_sandbox(
                owner=owner,
                repo=repo_name,
                branch=branch
            )

            return result

        except Exception as e:
            logger.error(f"Failed to trigger deployment: {e}")
            return None

    def run_tests_in_sandbox(self,
                           owner: str,
                           repo: str,
                           branch: str = "main",
                           test_command: str = "pytest") -> ExecutionResult:
        """
        Run tests in E2B sandbox

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch to test
            test_command: Test command to execute

        Returns:
            ExecutionResult
        """
        try:
            # Create sandbox
            sandbox_id = self.e2b_client.create_sandbox(template="python")

            # Clone repository (simplified - in practice you'd use git)
            # For now, we'll execute the test command directly
            result = self.e2b_client.execute_code(
                code=test_command,
                language=Language.BASH,
                sandbox_id=sandbox_id
            )

            logger.info(f"Tests completed with exit code: {result.exit_code}")

            # Cleanup
            self.e2b_client.delete_sandbox(sandbox_id)

            return result

        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            raise

    def close(self):
        """Close session"""
        self.session.close()
        logger.info("GitHub connector closed")


class GitHubActionsIntegration:
    """
    Integration with GitHub Actions for CI/CD workflows
    """

    def __init__(self, github_connector: GitHubConnector):
        """
        Initialize GitHub Actions integration

        Args:
            github_connector: GitHubConnector instance
        """
        self.connector = github_connector
        logger.info("GitHub Actions integration initialized")

    def create_workflow_file(self) -> str:
        """
        Generate GitHub Actions workflow file for E2B integration

        Returns:
            YAML workflow content
        """
        workflow = """
name: E2B Sandbox CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-in-sandbox:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install requests

    - name: Run tests in E2B sandbox
      env:
        E2B_API_KEY: ${{ secrets.E2B_API_KEY }}
      run: |
        python -c "
        import os
        import sys
        sys.path.insert(0, 'system-integration/e2b')
        from e2b_sandbox import E2BSandboxClient, Language

        client = E2BSandboxClient(os.getenv('E2B_API_KEY'))

        # Read and execute test file
        with open('tests/test_main.py', 'r') as f:
            code = f.read()

        result = client.execute_code(code, Language.PYTHON)

        if not result.is_success():
            print(f'Tests failed: {result.stderr}')
            sys.exit(1)
        else:
            print('Tests passed!')
            print(result.stdout)

        client.delete_sandbox(result.sandbox_id)
        "

    - name: Deploy to E2B
      if: github.ref == 'refs/heads/main'
      env:
        E2B_API_KEY: ${{ secrets.E2B_API_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        python system-integration/e2b/github_connector.py deploy
"""
        return workflow

    def generate_deployment_script(self) -> str:
        """
        Generate deployment script for GitHub Actions

        Returns:
            Python script content
        """
        script = """
#!/usr/bin/env python3
import os
import sys
from e2b_sandbox import E2BSandboxClient, Language
from github_connector import GitHubConnector

# Initialize clients
e2b_client = E2BSandboxClient(os.getenv('E2B_API_KEY'))
github_connector = GitHubConnector(
    github_token=os.getenv('GITHUB_TOKEN'),
    e2b_client=e2b_client
)

# Get repository info from environment
repo_full_name = os.getenv('GITHUB_REPOSITORY')
owner, repo = repo_full_name.split('/')
branch = os.getenv('GITHUB_REF_NAME', 'main')

# Deploy to sandbox
result = github_connector.deploy_to_sandbox(
    owner=owner,
    repo=repo,
    branch=branch
)

# Print results
print(f"Deployment ID: {result.deployment_id}")
print(f"Status: {result.status.value}")
print(f"Logs:")
for log in result.logs:
    print(f"  {log}")

if result.status.value == 'success':
    print(f"\\nOutput:\\n{result.execution_result.stdout}")
    sys.exit(0)
else:
    print(f"\\nError:\\n{result.execution_result.stderr if result.execution_result else 'Unknown error'}")
    sys.exit(1)
"""
        return script


def main():
    """Example usage"""
    # Initialize clients
    github_token = os.getenv("GITHUB_TOKEN")
    e2b_api_key = os.getenv("E2B_API_KEY", "e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773")

    if not github_token:
        logger.error("GITHUB_TOKEN environment variable not set")
        return

    e2b_client = E2BSandboxClient(e2b_api_key)
    connector = GitHubConnector(github_token, e2b_client)

    # Example: Deploy repository to sandbox
    result = connector.deploy_to_sandbox(
        owner="your-username",
        repo="your-repo",
        branch="main",
        entry_file="main.py"
    )

    print(f"Deployment Status: {result.status.value}")
    print(f"Logs:")
    for log in result.logs:
        print(f"  {log}")

    if result.execution_result:
        print(f"\nOutput:\n{result.execution_result.stdout}")

    # Cleanup
    connector.close()
    e2b_client.close()


if __name__ == "__main__":
    main()
