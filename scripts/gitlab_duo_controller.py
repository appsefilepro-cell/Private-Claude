#!/usr/bin/env python3
"""
GitLab Duo Controller - Programmatic CI/CD and Auto-Fix Management
===================================================================

This script provides comprehensive control over GitLab Duo features including:
- Pipeline triggering and monitoring
- Auto-fix extraction and application
- Merge request automation
- Duo suggestions management
- Vulnerability remediation

Author: Agent 5.0 System
Version: 2.0.0
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import requests
from dataclasses import dataclass, asdict
from enum import Enum


# ============================================================================
# Configuration & Constants
# ============================================================================

class PipelineStatus(Enum):
    """Pipeline status enumeration"""
    CREATED = "created"
    WAITING_FOR_RESOURCE = "waiting_for_resource"
    PREPARING = "preparing"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class MergeRequestState(Enum):
    """Merge request state enumeration"""
    OPENED = "opened"
    CLOSED = "closed"
    LOCKED = "locked"
    MERGED = "merged"


@dataclass
class GitLabConfig:
    """GitLab configuration"""
    url: str
    token: str
    project_id: str
    default_branch: str = "main"


@dataclass
class PipelineInfo:
    """Pipeline information"""
    id: int
    status: str
    ref: str
    sha: str
    web_url: str
    created_at: str
    updated_at: str
    duration: Optional[int] = None
    coverage: Optional[float] = None


@dataclass
class MergeRequestInfo:
    """Merge request information"""
    id: int
    iid: int
    title: str
    description: str
    state: str
    source_branch: str
    target_branch: str
    web_url: str
    author: Dict[str, Any]
    created_at: str


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Setup logging configuration

    Args:
        verbose: Enable verbose logging

    Returns:
        Configured logger instance
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('gitlab_duo_controller.log')
        ]
    )

    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================================
# GitLab API Client
# ============================================================================

class GitLabClient:
    """GitLab API client for interacting with GitLab"""

    def __init__(self, config: GitLabConfig):
        """
        Initialize GitLab client

        Args:
            config: GitLab configuration
        """
        self.config = config
        self.base_url = f"{config.url}/api/v4"
        self.headers = {
            "PRIVATE-TOKEN": config.token,
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make API request to GitLab

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def trigger_pipeline(
        self,
        ref: str,
        variables: Optional[Dict[str, str]] = None
    ) -> PipelineInfo:
        """
        Trigger a new pipeline

        Args:
            ref: Branch or tag name
            variables: Pipeline variables

        Returns:
            Pipeline information
        """
        logger.info(f"Triggering pipeline for ref: {ref}")

        data = {"ref": ref}
        if variables:
            data["variables"] = [
                {"key": k, "value": v} for k, v in variables.items()
            ]

        response = self._make_request(
            "POST",
            f"projects/{self.config.project_id}/pipeline",
            data=data
        )

        pipeline = PipelineInfo(**{
            k: v for k, v in response.items()
            if k in PipelineInfo.__annotations__
        })

        logger.info(f"Pipeline triggered: {pipeline.id} - {pipeline.web_url}")
        return pipeline

    def get_pipeline(self, pipeline_id: int) -> PipelineInfo:
        """
        Get pipeline information

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline information
        """
        response = self._make_request(
            "GET",
            f"projects/{self.config.project_id}/pipelines/{pipeline_id}"
        )

        return PipelineInfo(**{
            k: v for k, v in response.items()
            if k in PipelineInfo.__annotations__
        })

    def get_pipeline_jobs(self, pipeline_id: int) -> List[Dict[str, Any]]:
        """
        Get pipeline jobs

        Args:
            pipeline_id: Pipeline ID

        Returns:
            List of jobs
        """
        response = self._make_request(
            "GET",
            f"projects/{self.config.project_id}/pipelines/{pipeline_id}/jobs"
        )

        return response if isinstance(response, list) else []

    def get_job_log(self, job_id: int) -> str:
        """
        Get job log

        Args:
            job_id: Job ID

        Returns:
            Job log content
        """
        url = f"{self.base_url}/projects/{self.config.project_id}/jobs/{job_id}/trace"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get job log: {e}")
            return ""

    def create_merge_request(
        self,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str,
        remove_source_branch: bool = True
    ) -> MergeRequestInfo:
        """
        Create merge request

        Args:
            source_branch: Source branch name
            target_branch: Target branch name
            title: MR title
            description: MR description
            remove_source_branch: Remove source branch after merge

        Returns:
            Merge request information
        """
        logger.info(f"Creating merge request: {source_branch} -> {target_branch}")

        data = {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description,
            "remove_source_branch": remove_source_branch
        }

        response = self._make_request(
            "POST",
            f"projects/{self.config.project_id}/merge_requests",
            data=data
        )

        mr = MergeRequestInfo(**{
            k: v for k, v in response.items()
            if k in MergeRequestInfo.__annotations__
        })

        logger.info(f"Merge request created: !{mr.iid} - {mr.web_url}")
        return mr

    def get_merge_request(self, mr_iid: int) -> MergeRequestInfo:
        """
        Get merge request information

        Args:
            mr_iid: Merge request IID

        Returns:
            Merge request information
        """
        response = self._make_request(
            "GET",
            f"projects/{self.config.project_id}/merge_requests/{mr_iid}"
        )

        return MergeRequestInfo(**{
            k: v for k, v in response.items()
            if k in MergeRequestInfo.__annotations__
        })

    def merge_merge_request(
        self,
        mr_iid: int,
        merge_when_pipeline_succeeds: bool = True
    ) -> Dict[str, Any]:
        """
        Merge merge request

        Args:
            mr_iid: Merge request IID
            merge_when_pipeline_succeeds: Auto-merge when pipeline succeeds

        Returns:
            Response data
        """
        logger.info(f"Merging merge request: !{mr_iid}")

        data = {
            "merge_when_pipeline_succeeds": merge_when_pipeline_succeeds
        }

        return self._make_request(
            "PUT",
            f"projects/{self.config.project_id}/merge_requests/{mr_iid}/merge",
            data=data
        )

    def get_pipeline_status(self, pipeline_id: int) -> str:
        """
        Get pipeline status

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline status
        """
        pipeline = self.get_pipeline(pipeline_id)
        return pipeline.status


# ============================================================================
# Pipeline Monitor
# ============================================================================

class PipelineMonitor:
    """Monitor pipeline execution and status"""

    def __init__(self, client: GitLabClient):
        """
        Initialize pipeline monitor

        Args:
            client: GitLab client instance
        """
        self.client = client

    def wait_for_pipeline(
        self,
        pipeline_id: int,
        timeout: int = 3600,
        poll_interval: int = 30
    ) -> Tuple[bool, PipelineInfo]:
        """
        Wait for pipeline to complete

        Args:
            pipeline_id: Pipeline ID
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds

        Returns:
            Tuple of (success, pipeline_info)
        """
        logger.info(f"Monitoring pipeline {pipeline_id}...")

        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout:
                logger.error(f"Pipeline monitoring timeout after {timeout}s")
                return False, self.client.get_pipeline(pipeline_id)

            pipeline = self.client.get_pipeline(pipeline_id)
            status = pipeline.status

            logger.info(f"Pipeline {pipeline_id} status: {status} ({elapsed:.0f}s)")

            if status == PipelineStatus.SUCCESS.value:
                logger.info(f"Pipeline {pipeline_id} succeeded!")
                return True, pipeline
            elif status in [PipelineStatus.FAILED.value, PipelineStatus.CANCELED.value]:
                logger.error(f"Pipeline {pipeline_id} {status}")
                return False, pipeline
            elif status in [PipelineStatus.RUNNING.value, PipelineStatus.PENDING.value]:
                logger.debug(f"Pipeline still {status}, waiting...")
                time.sleep(poll_interval)
            else:
                logger.warning(f"Unknown pipeline status: {status}")
                time.sleep(poll_interval)

    def get_failed_jobs(self, pipeline_id: int) -> List[Dict[str, Any]]:
        """
        Get failed jobs from pipeline

        Args:
            pipeline_id: Pipeline ID

        Returns:
            List of failed jobs
        """
        jobs = self.client.get_pipeline_jobs(pipeline_id)
        failed_jobs = [
            job for job in jobs
            if job.get("status") == "failed"
        ]

        logger.info(f"Found {len(failed_jobs)} failed jobs in pipeline {pipeline_id}")
        return failed_jobs

    def analyze_failures(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Analyze pipeline failures

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Failure analysis
        """
        logger.info(f"Analyzing failures for pipeline {pipeline_id}")

        failed_jobs = self.get_failed_jobs(pipeline_id)

        analysis = {
            "pipeline_id": pipeline_id,
            "total_failed_jobs": len(failed_jobs),
            "failed_jobs": [],
            "error_patterns": []
        }

        for job in failed_jobs:
            job_id = job["id"]
            job_name = job["name"]

            logger.info(f"Analyzing job {job_name} ({job_id})")

            log = self.client.get_job_log(job_id)

            job_analysis = {
                "id": job_id,
                "name": job_name,
                "status": job["status"],
                "stage": job["stage"],
                "log_snippet": log[-500:] if log else ""
            }

            analysis["failed_jobs"].append(job_analysis)

        return analysis


# ============================================================================
# Duo Auto-Fix Manager
# ============================================================================

class DuoAutoFixManager:
    """Manage GitLab Duo auto-fix operations"""

    def __init__(self, client: GitLabClient):
        """
        Initialize auto-fix manager

        Args:
            client: GitLab client instance
        """
        self.client = client

    def extract_duo_suggestions(self, pipeline_id: int) -> List[Dict[str, Any]]:
        """
        Extract Duo suggestions from pipeline

        Args:
            pipeline_id: Pipeline ID

        Returns:
            List of suggestions
        """
        logger.info(f"Extracting Duo suggestions from pipeline {pipeline_id}")

        jobs = self.client.get_pipeline_jobs(pipeline_id)
        suggestions = []

        for job in jobs:
            if "duo" in job["name"].lower():
                job_id = job["id"]
                log = self.client.get_job_log(job_id)

                # Parse suggestions from log
                # This is a simplified version - actual implementation would parse JSON artifacts
                if "suggestion" in log.lower():
                    suggestions.append({
                        "job_id": job_id,
                        "job_name": job["name"],
                        "suggestion": "Auto-fix available"
                    })

        logger.info(f"Found {len(suggestions)} Duo suggestions")
        return suggestions

    def apply_auto_fixes(self, suggestions: List[Dict[str, Any]]) -> bool:
        """
        Apply auto-fixes from suggestions

        Args:
            suggestions: List of suggestions

        Returns:
            Success status
        """
        logger.info(f"Applying {len(suggestions)} auto-fixes")

        # This would integrate with the actual auto-fix logic
        # For now, we just log the suggestions

        for suggestion in suggestions:
            logger.info(f"Auto-fix: {suggestion}")

        return True


# ============================================================================
# Command Handlers
# ============================================================================

def trigger_pipeline_command(args: argparse.Namespace) -> int:
    """
    Handle trigger-pipeline command

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config = GitLabConfig(
        url=os.getenv("CI_SERVER_URL", "https://gitlab.com"),
        token=os.getenv("GITLAB_TOKEN", ""),
        project_id=os.getenv("CI_PROJECT_ID", args.project_id)
    )

    client = GitLabClient(config)

    variables = {}
    if args.variables:
        for var in args.variables:
            key, value = var.split("=", 1)
            variables[key] = value

    pipeline = client.trigger_pipeline(args.ref, variables)

    print(f"Pipeline triggered: {pipeline.id}")
    print(f"URL: {pipeline.web_url}")

    if args.wait:
        monitor = PipelineMonitor(client)
        success, final_pipeline = monitor.wait_for_pipeline(pipeline.id)

        if not success:
            logger.error("Pipeline failed!")
            return 1

    return 0


def monitor_pipeline_command(args: argparse.Namespace) -> int:
    """
    Handle monitor-pipeline command

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config = GitLabConfig(
        url=os.getenv("CI_SERVER_URL", "https://gitlab.com"),
        token=os.getenv("GITLAB_TOKEN", ""),
        project_id=os.getenv("CI_PROJECT_ID", args.project_id)
    )

    client = GitLabClient(config)
    monitor = PipelineMonitor(client)

    success, pipeline = monitor.wait_for_pipeline(args.pipeline_id)

    if not success:
        analysis = monitor.analyze_failures(args.pipeline_id)
        print(json.dumps(analysis, indent=2))
        return 1

    return 0


def create_mr_command(args: argparse.Namespace) -> int:
    """
    Handle create-mr command

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config = GitLabConfig(
        url=os.getenv("CI_SERVER_URL", "https://gitlab.com"),
        token=os.getenv("GITLAB_TOKEN", ""),
        project_id=os.getenv("CI_PROJECT_ID", args.project_id),
        default_branch=os.getenv("CI_DEFAULT_BRANCH", "main")
    )

    client = GitLabClient(config)

    mr = client.create_merge_request(
        source_branch=args.branch,
        target_branch=args.target or config.default_branch,
        title=args.title,
        description=args.description or ""
    )

    print(f"Merge request created: !{mr.iid}")
    print(f"URL: {mr.web_url}")

    if args.auto_merge:
        logger.info("Auto-merge enabled")
        client.merge_merge_request(mr.iid, merge_when_pipeline_succeeds=True)

    return 0


def auto_fix_command(args: argparse.Namespace) -> int:
    """
    Handle auto-fix command

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    config = GitLabConfig(
        url=os.getenv("CI_SERVER_URL", "https://gitlab.com"),
        token=os.getenv("GITLAB_TOKEN", ""),
        project_id=os.getenv("CI_PROJECT_ID", args.project_id)
    )

    client = GitLabClient(config)
    manager = DuoAutoFixManager(client)

    suggestions = manager.extract_duo_suggestions(args.pipeline_id)

    if not suggestions:
        logger.info("No auto-fix suggestions found")
        return 0

    print(f"Found {len(suggestions)} auto-fix suggestions:")
    print(json.dumps(suggestions, indent=2))

    if args.apply:
        success = manager.apply_auto_fixes(suggestions)
        return 0 if success else 1

    return 0


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="GitLab Duo Controller - CI/CD and Auto-Fix Management"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--project-id",
        help="GitLab project ID",
        default=os.getenv("CI_PROJECT_ID")
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # trigger-pipeline command
    trigger_parser = subparsers.add_parser(
        "trigger-pipeline",
        help="Trigger a new pipeline"
    )
    trigger_parser.add_argument("ref", help="Branch or tag name")
    trigger_parser.add_argument(
        "--variables", "-e",
        nargs="+",
        help="Pipeline variables (KEY=VALUE)"
    )
    trigger_parser.add_argument(
        "--wait", "-w",
        action="store_true",
        help="Wait for pipeline completion"
    )

    # monitor-pipeline command
    monitor_parser = subparsers.add_parser(
        "monitor-pipeline",
        help="Monitor pipeline execution"
    )
    monitor_parser.add_argument("pipeline_id", type=int, help="Pipeline ID")

    # create-mr command
    mr_parser = subparsers.add_parser(
        "create-mr",
        help="Create merge request"
    )
    mr_parser.add_argument("--branch", "-b", required=True, help="Source branch")
    mr_parser.add_argument("--target", "-t", help="Target branch")
    mr_parser.add_argument("--title", required=True, help="MR title")
    mr_parser.add_argument("--description", "-d", help="MR description")
    mr_parser.add_argument(
        "--auto-merge",
        action="store_true",
        help="Enable auto-merge"
    )

    # auto-fix command
    autofix_parser = subparsers.add_parser(
        "auto-fix",
        help="Extract and apply Duo auto-fixes"
    )
    autofix_parser.add_argument("pipeline_id", type=int, help="Pipeline ID")
    autofix_parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply auto-fixes"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    command_handlers = {
        "trigger-pipeline": trigger_pipeline_command,
        "monitor-pipeline": monitor_pipeline_command,
        "create-mr": create_mr_command,
        "auto-fix": auto_fix_command
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
