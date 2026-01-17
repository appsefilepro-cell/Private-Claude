"""
Pull Request Management and Task Organization System
Organizes, tracks, and manages open pull requests and associated tasks
"""
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PRStatus(Enum):
    """Pull request status"""
    OPEN = "open"
    DRAFT = "draft"
    REVIEW_REQUIRED = "review_required"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    MERGED = "merged"
    CLOSED = "closed"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    """Individual task within a PR"""
    id: str
    title: str
    description: str
    priority: TaskPriority
    status: str
    assignee: Optional[str] = None
    created_at: str = None
    completed_at: Optional[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class PullRequest:
    """Pull request with associated tasks"""
    number: int
    title: str
    status: PRStatus
    author: str
    created_at: str
    tasks: List[Task]
    labels: List[str] = None
    branch: str = None
    target_branch: str = "main"
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []


class PRManager:
    """Manages pull requests and tasks"""
    
    def __init__(self, storage_dir: str = "pr-data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.prs: Dict[int, PullRequest] = {}
        self.tasks_by_pr: Dict[int, List[Task]] = {}
        
    def add_pull_request(self, pr: PullRequest) -> bool:
        """Add new pull request"""
        try:
            self.prs[pr.number] = pr
            self.tasks_by_pr[pr.number] = pr.tasks
            logger.info(f"Added PR #{pr.number}: {pr.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to add PR: {e}")
            return False
    
    def organize_prs(self) -> Dict[str, List[PullRequest]]:
        """Organize PRs by status and priority"""
        organized = {
            'critical': [],
            'needs_review': [],
            'approved': [],
            'changes_needed': [],
            'ready_to_merge': [],
            'draft': []
        }
        
        for pr in self.prs.values():
            # Check for critical tasks
            critical_tasks = [t for t in pr.tasks if t.priority == TaskPriority.CRITICAL]
            if critical_tasks:
                organized['critical'].append(pr)
                continue
            
            # Organize by status
            if pr.status == PRStatus.DRAFT:
                organized['draft'].append(pr)
            elif pr.status == PRStatus.REVIEW_REQUIRED:
                organized['needs_review'].append(pr)
            elif pr.status == PRStatus.APPROVED:
                organized['approved'].append(pr)
            elif pr.status == PRStatus.CHANGES_REQUESTED:
                organized['changes_needed'].append(pr)
            
            # Check if ready to merge
            if self._is_ready_to_merge(pr):
                organized['ready_to_merge'].append(pr)
        
        return organized
    
    def _is_ready_to_merge(self, pr: PullRequest) -> bool:
        """Check if PR is ready to merge"""
        if pr.status != PRStatus.APPROVED:
            return False
        
        # All tasks must be completed
        incomplete_tasks = [t for t in pr.tasks if t.status != 'completed']
        return len(incomplete_tasks) == 0
    
    def get_task_dependencies(self, task_id: str) -> List[Task]:
        """Get all dependencies for a task"""
        for pr in self.prs.values():
            for task in pr.tasks:
                if task.id == task_id:
                    return [self._find_task(dep_id) for dep_id in task.dependencies]
        return []
    
    def _find_task(self, task_id: str) -> Optional[Task]:
        """Find task by ID across all PRs"""
        for pr in self.prs.values():
            for task in pr.tasks:
                if task.id == task_id:
                    return task
        return None
    
    def update_task_status(self, pr_number: int, task_id: str, new_status: str) -> bool:
        """Update task status"""
        if pr_number not in self.prs:
            logger.error(f"PR #{pr_number} not found")
            return False
        
        pr = self.prs[pr_number]
        for task in pr.tasks:
            if task.id == task_id:
                task.status = new_status
                if new_status == 'completed':
                    task.completed_at = datetime.now().isoformat()
                logger.info(f"Updated task {task_id} to {new_status}")
                return True
        
        logger.error(f"Task {task_id} not found in PR #{pr_number}")
        return False
    
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """Generate comprehensive PR management report"""
        organized = self.organize_prs()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_prs': len(self.prs),
            'total_tasks': sum(len(pr.tasks) for pr in self.prs.values()),
            'summary': {
                'critical_prs': len(organized['critical']),
                'needs_review': len(organized['needs_review']),
                'approved': len(organized['approved']),
                'changes_needed': len(organized['changes_needed']),
                'ready_to_merge': len(organized['ready_to_merge']),
                'draft': len(organized['draft'])
            },
            'task_status': self._get_task_statistics(),
            'recommendations': self._generate_recommendations(organized)
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_file}")
        
        return report
    
    def _get_task_statistics(self) -> Dict[str, int]:
        """Get task completion statistics"""
        stats = {
            'total': 0,
            'completed': 0,
            'in_progress': 0,
            'pending': 0,
            'blocked': 0
        }
        
        for pr in self.prs.values():
            for task in pr.tasks:
                stats['total'] += 1
                stats[task.status] = stats.get(task.status, 0) + 1
        
        return stats
    
    def _generate_recommendations(self, organized: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if organized['critical']:
            recommendations.append(
                f"URGENT: {len(organized['critical'])} PRs have critical tasks requiring immediate attention"
            )
        
        if organized['changes_needed']:
            recommendations.append(
                f"{len(organized['changes_needed'])} PRs need changes based on review feedback"
            )
        
        if organized['ready_to_merge']:
            recommendations.append(
                f"{len(organized['ready_to_merge'])} PRs are approved and ready to merge"
            )
        
        if organized['needs_review']:
            recommendations.append(
                f"{len(organized['needs_review'])} PRs are waiting for code review"
            )
        
        return recommendations
    
    def create_task_from_pr_141(self) -> List[Task]:
        """Create tasks from PR #141 requirements"""
        tasks = [
            Task(
                id="t1",
                title="Fix path traversal vulnerabilities",
                description="Scan and fix path traversal security issues",
                priority=TaskPriority.CRITICAL,
                status="in_progress"
            ),
            Task(
                id="t2",
                title="Execute 100 trading tasks",
                description="Run comprehensive trading analysis and backtesting",
                priority=TaskPriority.HIGH,
                status="in_progress"
            ),
            Task(
                id="t3",
                title="Complete GitLab integration",
                description="Implement GitLab MCP connector and CI/CD integration",
                priority=TaskPriority.HIGH,
                status="pending"
            ),
            Task(
                id="t4",
                title="Complete Zapier integration",
                description="Enhance Zapier MCP connector with advanced workflows",
                priority=TaskPriority.HIGH,
                status="pending"
            ),
            Task(
                id="t5",
                title="Extend multi-agent with Copilot",
                description="Integrate GitHub Copilot into agent orchestration",
                priority=TaskPriority.MEDIUM,
                status="pending"
            ),
            Task(
                id="t6",
                title="Troubleshoot job failure 59014433637",
                description="Debug and resolve CI/CD job failure",
                priority=TaskPriority.HIGH,
                status="pending"
            ),
            Task(
                id="t7",
                title="Set up AgentX 5.0 container",
                description="Configure Docker container with AgentX 5.0",
                priority=TaskPriority.MEDIUM,
                status="pending"
            ),
            Task(
                id="t8",
                title="Create sub-issue tracking system",
                description="Implement sub-issue management for GitHub Issues",
                priority=TaskPriority.MEDIUM,
                status="pending"
            ),
            Task(
                id="t9",
                title="Agent sync and orchestration",
                description="Create agent synchronization and merge system",
                priority=TaskPriority.HIGH,
                status="pending"
            ),
            Task(
                id="t10",
                title="AI integration testing plan",
                description="Develop comprehensive test suite for AI integrations",
                priority=TaskPriority.MEDIUM,
                status="pending"
            )
        ]
        
        # Add PR #141
        pr = PullRequest(
            number=141,
            title="Complete all system tasks and integrations",
            status=PRStatus.OPEN,
            author="appsefilepro-cell",
            created_at=datetime.now().isoformat(),
            tasks=tasks,
            labels=["enhancement", "security", "integration"],
            branch="copilot/fix-button-issue-part-2"
        )
        
        self.add_pull_request(pr)
        return tasks


def main():
    """Run PR management system"""
    manager = PRManager()
    
    # Create tasks from PR #141
    tasks = manager.create_task_from_pr_141()
    
    # Generate report
    report = manager.generate_report('pr_management_report.json')
    
    print(f"\n{'='*60}")
    print("PULL REQUEST MANAGEMENT REPORT")
    print(f"{'='*60}")
    print(f"Total PRs: {report['total_prs']}")
    print(f"Total Tasks: {report['total_tasks']}")
    print(f"\nSummary:")
    for key, value in report['summary'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    print(f"{'='*60}\n")
    
    return report


if __name__ == "__main__":
    main()
