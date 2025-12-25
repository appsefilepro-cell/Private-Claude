#!/usr/bin/env python3
"""
GitLab <-> GitHub Bidirectional Sync System
Handles webhook events and syncs code, issues, and pull requests between platforms
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
from aiohttp import web
import os
import json
import hmac
import hashlib

from event_bus import event_bus, EventType, Priority, Event, publish_git_event


logger = logging.getLogger(__name__)


class GitLabConfig:
    """GitLab configuration"""
    def __init__(self):
        self.url = os.getenv('GITLAB_URL', 'https://gitlab.com')
        self.token = os.getenv('GITLAB_TOKEN', '')
        self.webhook_secret = os.getenv('GITLAB_WEBHOOK_SECRET', '')
        self.project_id = os.getenv('GITLAB_PROJECT_ID', '')


class GitHubConfig:
    """GitHub configuration"""
    def __init__(self):
        self.url = os.getenv('GITHUB_URL', 'https://api.github.com')
        self.token = os.getenv('GITHUB_TOKEN', '')
        self.webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET', '')
        self.repo = os.getenv('GITHUB_REPO', '')  # format: owner/repo


class GitSyncService:
    """Bidirectional Git synchronization service"""

    def __init__(self):
        self.gitlab_config = GitLabConfig()
        self.github_config = GitHubConfig()
        self.sync_enabled = os.getenv('GIT_SYNC_ENABLED', 'true').lower() == 'true'
        self.sync_branches = os.getenv('SYNC_BRANCHES', 'main,develop').split(',')

    async def handle_gitlab_webhook(self, request: web.Request) -> web.Response:
        """Handle GitLab webhook events"""
        # Verify webhook secret
        token = request.headers.get('X-Gitlab-Token', '')
        if token != self.gitlab_config.webhook_secret:
            logger.warning("Invalid GitLab webhook token")
            return web.Response(status=401, text="Unauthorized")

        try:
            payload = await request.json()
            event_type = request.headers.get('X-Gitlab-Event', '')

            logger.info(f"Received GitLab event: {event_type}")

            # Process different event types
            if event_type == 'Push Hook':
                await self._handle_gitlab_push(payload)
            elif event_type == 'Merge Request Hook':
                await self._handle_gitlab_merge_request(payload)
            elif event_type == 'Issue Hook':
                await self._handle_gitlab_issue(payload)
            elif event_type == 'Pipeline Hook':
                await self._handle_gitlab_pipeline(payload)

            return web.Response(text="OK")

        except Exception as e:
            logger.error(f"Error handling GitLab webhook: {e}")
            return web.Response(status=500, text=str(e))

    async def handle_github_webhook(self, request: web.Request) -> web.Response:
        """Handle GitHub webhook events"""
        # Verify webhook signature
        signature = request.headers.get('X-Hub-Signature-256', '')
        body = await request.read()

        if not self._verify_github_signature(signature, body):
            logger.warning("Invalid GitHub webhook signature")
            return web.Response(status=401, text="Unauthorized")

        try:
            payload = json.loads(body.decode('utf-8'))
            event_type = request.headers.get('X-GitHub-Event', '')

            logger.info(f"Received GitHub event: {event_type}")

            # Process different event types
            if event_type == 'push':
                await self._handle_github_push(payload)
            elif event_type == 'pull_request':
                await self._handle_github_pull_request(payload)
            elif event_type == 'issues':
                await self._handle_github_issue(payload)
            elif event_type == 'workflow_run':
                await self._handle_github_workflow(payload)

            return web.Response(text="OK")

        except Exception as e:
            logger.error(f"Error handling GitHub webhook: {e}")
            return web.Response(status=500, text=str(e))

    def _verify_github_signature(self, signature: str, body: bytes) -> bool:
        """Verify GitHub webhook signature"""
        if not self.github_config.webhook_secret:
            return True  # Skip verification if no secret configured

        expected_signature = 'sha256=' + hmac.new(
            self.github_config.webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    async def _handle_gitlab_push(self, payload: Dict[str, Any]):
        """Handle GitLab push event"""
        project = payload.get('project', {})
        repo_name = project.get('name', 'unknown')
        branch = payload.get('ref', '').replace('refs/heads/', '')
        commits = payload.get('commits', [])

        # Publish event
        await publish_git_event(
            source='gitlab',
            event_type=EventType.GITLAB_PUSH,
            repo=repo_name,
            branch=branch,
            author=payload.get('user_name', 'unknown'),
            message=f"{len(commits)} commit(s) pushed",
            commits_count=len(commits),
            commit_messages=[c.get('message', '') for c in commits[:5]]
        )

        # Sync to GitHub if enabled
        if self.sync_enabled and branch in self.sync_branches:
            await self._sync_gitlab_to_github(payload)

    async def _handle_gitlab_merge_request(self, payload: Dict[str, Any]):
        """Handle GitLab merge request event"""
        object_attributes = payload.get('object_attributes', {})
        action = object_attributes.get('action', 'unknown')
        title = object_attributes.get('title', 'Untitled')
        source_branch = object_attributes.get('source_branch', '')
        target_branch = object_attributes.get('target_branch', '')

        await publish_git_event(
            source='gitlab',
            event_type=EventType.GITLAB_MERGE_REQUEST,
            repo=payload.get('project', {}).get('name', 'unknown'),
            branch=source_branch,
            author=object_attributes.get('author', {}).get('name', 'unknown'),
            message=f"Merge request {action}: {title}",
            action=action,
            title=title,
            target_branch=target_branch,
            url=object_attributes.get('url', '')
        )

        # Sync to GitHub if enabled
        if self.sync_enabled and action == 'open':
            await self._create_github_pull_request(payload)

    async def _handle_gitlab_issue(self, payload: Dict[str, Any]):
        """Handle GitLab issue event"""
        object_attributes = payload.get('object_attributes', {})
        action = object_attributes.get('action', 'unknown')
        title = object_attributes.get('title', 'Untitled')

        logger.info(f"GitLab issue {action}: {title}")

        # Sync to GitHub if enabled
        if self.sync_enabled and action == 'open':
            await self._create_github_issue(payload)

    async def _handle_gitlab_pipeline(self, payload: Dict[str, Any]):
        """Handle GitLab pipeline event"""
        object_attributes = payload.get('object_attributes', {})
        status = object_attributes.get('status', 'unknown')
        ref = object_attributes.get('ref', '')

        logger.info(f"GitLab pipeline {status} on {ref}")

    async def _handle_github_push(self, payload: Dict[str, Any]):
        """Handle GitHub push event"""
        repo = payload.get('repository', {}).get('name', 'unknown')
        branch = payload.get('ref', '').replace('refs/heads/', '')
        commits = payload.get('commits', [])
        pusher = payload.get('pusher', {}).get('name', 'unknown')

        # Publish event
        await publish_git_event(
            source='github',
            event_type=EventType.GITHUB_PUSH,
            repo=repo,
            branch=branch,
            author=pusher,
            message=f"{len(commits)} commit(s) pushed",
            commits_count=len(commits),
            commit_messages=[c.get('message', '') for c in commits[:5]]
        )

        # Sync to GitLab if enabled
        if self.sync_enabled and branch in self.sync_branches:
            await self._sync_github_to_gitlab(payload)

    async def _handle_github_pull_request(self, payload: Dict[str, Any]):
        """Handle GitHub pull request event"""
        action = payload.get('action', 'unknown')
        pr = payload.get('pull_request', {})
        title = pr.get('title', 'Untitled')
        source_branch = pr.get('head', {}).get('ref', '')
        target_branch = pr.get('base', {}).get('ref', '')

        await publish_git_event(
            source='github',
            event_type=EventType.GITHUB_PULL_REQUEST,
            repo=payload.get('repository', {}).get('name', 'unknown'),
            branch=source_branch,
            author=pr.get('user', {}).get('login', 'unknown'),
            message=f"Pull request {action}: {title}",
            action=action,
            title=title,
            target_branch=target_branch,
            url=pr.get('html_url', '')
        )

        # Sync to GitLab if enabled
        if self.sync_enabled and action == 'opened':
            await self._create_gitlab_merge_request(payload)

    async def _handle_github_issue(self, payload: Dict[str, Any]):
        """Handle GitHub issue event"""
        action = payload.get('action', 'unknown')
        issue = payload.get('issue', {})
        title = issue.get('title', 'Untitled')

        logger.info(f"GitHub issue {action}: {title}")

        # Sync to GitLab if enabled
        if self.sync_enabled and action == 'opened':
            await self._create_gitlab_issue(payload)

    async def _handle_github_workflow(self, payload: Dict[str, Any]):
        """Handle GitHub workflow event"""
        workflow_run = payload.get('workflow_run', {})
        status = workflow_run.get('status', 'unknown')
        name = workflow_run.get('name', 'unknown')

        logger.info(f"GitHub workflow '{name}' {status}")

    # Sync operations
    async def _sync_gitlab_to_github(self, payload: Dict[str, Any]):
        """Sync GitLab push to GitHub"""
        logger.info("Syncing GitLab push to GitHub...")
        # Implementation: Use git mirror or API to sync commits
        # This would require git operations or using GitHub API to create commits

    async def _sync_github_to_gitlab(self, payload: Dict[str, Any]):
        """Sync GitHub push to GitLab"""
        logger.info("Syncing GitHub push to GitLab...")
        # Implementation: Use git mirror or API to sync commits

    async def _create_github_pull_request(self, gitlab_payload: Dict[str, Any]):
        """Create GitHub PR from GitLab MR"""
        if not self.github_config.token or not self.github_config.repo:
            logger.warning("GitHub credentials not configured")
            return

        mr = gitlab_payload.get('object_attributes', {})

        async with aiohttp.ClientSession() as session:
            url = f"{self.github_config.url}/repos/{self.github_config.repo}/pulls"
            headers = {
                'Authorization': f'token {self.github_config.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {
                'title': f"[GitLab MR] {mr.get('title', 'Untitled')}",
                'body': f"{mr.get('description', '')}\n\n---\nSynced from GitLab MR: {mr.get('url', '')}",
                'head': mr.get('source_branch', ''),
                'base': mr.get('target_branch', 'main')
            }

            try:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Created GitHub PR: {result.get('html_url')}")
                    else:
                        logger.error(f"Failed to create GitHub PR: {response.status}")
            except Exception as e:
                logger.error(f"Error creating GitHub PR: {e}")

    async def _create_gitlab_merge_request(self, github_payload: Dict[str, Any]):
        """Create GitLab MR from GitHub PR"""
        if not self.gitlab_config.token or not self.gitlab_config.project_id:
            logger.warning("GitLab credentials not configured")
            return

        pr = github_payload.get('pull_request', {})

        async with aiohttp.ClientSession() as session:
            url = f"{self.gitlab_config.url}/api/v4/projects/{self.gitlab_config.project_id}/merge_requests"
            headers = {
                'PRIVATE-TOKEN': self.gitlab_config.token
            }
            data = {
                'source_branch': pr.get('head', {}).get('ref', ''),
                'target_branch': pr.get('base', {}).get('ref', 'main'),
                'title': f"[GitHub PR] {pr.get('title', 'Untitled')}",
                'description': f"{pr.get('body', '')}\n\n---\nSynced from GitHub PR: {pr.get('html_url', '')}"
            }

            try:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Created GitLab MR: {result.get('web_url')}")
                    else:
                        logger.error(f"Failed to create GitLab MR: {response.status}")
            except Exception as e:
                logger.error(f"Error creating GitLab MR: {e}")

    async def _create_github_issue(self, gitlab_payload: Dict[str, Any]):
        """Create GitHub issue from GitLab issue"""
        if not self.github_config.token or not self.github_config.repo:
            return

        issue = gitlab_payload.get('object_attributes', {})

        async with aiohttp.ClientSession() as session:
            url = f"{self.github_config.url}/repos/{self.github_config.repo}/issues"
            headers = {
                'Authorization': f'token {self.github_config.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {
                'title': f"[GitLab] {issue.get('title', 'Untitled')}",
                'body': f"{issue.get('description', '')}\n\n---\nSynced from GitLab issue"
            }

            try:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Created GitHub issue: {result.get('html_url')}")
            except Exception as e:
                logger.error(f"Error creating GitHub issue: {e}")

    async def _create_gitlab_issue(self, github_payload: Dict[str, Any]):
        """Create GitLab issue from GitHub issue"""
        if not self.gitlab_config.token or not self.gitlab_config.project_id:
            return

        issue = github_payload.get('issue', {})

        async with aiohttp.ClientSession() as session:
            url = f"{self.gitlab_config.url}/api/v4/projects/{self.gitlab_config.project_id}/issues"
            headers = {
                'PRIVATE-TOKEN': self.gitlab_config.token
            }
            data = {
                'title': f"[GitHub] {issue.get('title', 'Untitled')}",
                'description': f"{issue.get('body', '')}\n\n---\nSynced from GitHub issue"
            }

            try:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Created GitLab issue: {result.get('web_url')}")
            except Exception as e:
                logger.error(f"Error creating GitLab issue: {e}")


async def start_webhook_server(port: int = 8080):
    """Start webhook server"""
    service = GitSyncService()
    app = web.Application()

    # Add routes
    app.router.add_post('/webhooks/gitlab', service.handle_gitlab_webhook)
    app.router.add_post('/webhooks/github', service.handle_github_webhook)

    # Health check
    async def health_check(request):
        return web.Response(text="OK")

    app.router.add_get('/health', health_check)

    logger.info(f"Starting webhook server on port {port}")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    # Keep running
    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(start_webhook_server())
