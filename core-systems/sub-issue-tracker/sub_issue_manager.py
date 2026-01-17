"""
Sub-Issue Tracking System
Creates and manages sub-issues for GitHub Issues
"""
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IssueStatus(Enum):
    """Issue status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CLOSED = "closed"


@dataclass
class SubIssue:
    """Sub-issue data structure"""
    id: str
    parent_id: str
    title: str
    description: str
    status: IssueStatus
    assignee: Optional[str] = None
    created_at: str = None
    completed_at: Optional[str] = None
    dependencies: List[str] = None
    labels: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.dependencies is None:
            self.dependencies = []
        if self.labels is None:
            self.labels = []


class SubIssueTracker:
    """Manages sub-issues and task hierarchies"""
    
    def __init__(self):
        self.issues = {}
        self.sub_issues = {}
        
    def create_parent_issue(self, issue_id: str, title: str, description: str) -> Dict:
        """Create parent issue"""
        issue = {
            'id': issue_id,
            'title': title,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'sub_issues': []
        }
        self.issues[issue_id] = issue
        logger.info(f"Created parent issue: {issue_id}")
        return issue
    
    def create_sub_issue(self, parent_id: str, title: str, description: str,
                        assignee: Optional[str] = None) -> SubIssue:
        """Create sub-issue"""
        if parent_id not in self.issues:
            raise ValueError(f"Parent issue {parent_id} not found")
        
        sub_issue_id = f"{parent_id}-sub-{len(self.issues[parent_id]['sub_issues']) + 1}"
        
        sub_issue = SubIssue(
            id=sub_issue_id,
            parent_id=parent_id,
            title=title,
            description=description,
            status=IssueStatus.OPEN,
            assignee=assignee
        )
        
        self.sub_issues[sub_issue_id] = sub_issue
        self.issues[parent_id]['sub_issues'].append(sub_issue_id)
        
        logger.info(f"Created sub-issue: {sub_issue_id}")
        return sub_issue
    
    def update_sub_issue_status(self, sub_issue_id: str, new_status: IssueStatus) -> bool:
        """Update sub-issue status"""
        if sub_issue_id not in self.sub_issues:
            logger.error(f"Sub-issue {sub_issue_id} not found")
            return False
        
        sub_issue = self.sub_issues[sub_issue_id]
        sub_issue.status = new_status
        
        if new_status == IssueStatus.COMPLETED:
            sub_issue.completed_at = datetime.now().isoformat()
        
        logger.info(f"Updated sub-issue {sub_issue_id} to {new_status.value}")
        return True
    
    def get_sub_issues_by_status(self, parent_id: str, status: IssueStatus) -> List[SubIssue]:
        """Get sub-issues by status"""
        if parent_id not in self.issues:
            return []
        
        sub_issue_ids = self.issues[parent_id]['sub_issues']
        return [
            self.sub_issues[sid] for sid in sub_issue_ids
            if self.sub_issues[sid].status == status
        ]
    
    def calculate_completion_percentage(self, parent_id: str) -> float:
        """Calculate completion percentage for parent issue"""
        if parent_id not in self.issues:
            return 0.0
        
        sub_issue_ids = self.issues[parent_id]['sub_issues']
        if not sub_issue_ids:
            return 0.0
        
        completed = len([
            sid for sid in sub_issue_ids
            if self.sub_issues[sid].status == IssueStatus.COMPLETED
        ])
        
        return (completed / len(sub_issue_ids)) * 100
    
    def create_pr_141_sub_issues(self):
        """Create sub-issues for PR #141 tasks"""
        parent = self.create_parent_issue(
            issue_id="pr-141",
            title="Complete all system tasks and integrations",
            description="Comprehensive task completion for Private-Claude project"
        )
        
        sub_issues_data = [
            ("Security: Path Traversal Scanner", "Implement vulnerability scanner and auto-fix"),
            ("Trading: 100 Task Execution", "Execute comprehensive trading analysis tasks"),
            ("PR Management System", "Organize and track open pull requests"),
            ("GitLab Integration", "Complete GitLab MCP connector"),
            ("Zapier Integration", "Enhanced Zapier workflow automation"),
            ("Copilot Multi-Agent", "Integrate GitHub Copilot with agents"),
            ("Job Failure Debugger", "Debug job 59014433637"),
            ("AgentX 5.0 Container", "Docker/K8s configuration"),
            ("Agent Orchestration", "Sync and merge agent systems"),
            ("AI Testing Framework", "Comprehensive test suite")
        ]
        
        for title, description in sub_issues_data:
            self.create_sub_issue(parent['id'], title, description)
    
    def generate_github_issue_template(self, parent_id: str) -> str:
        """Generate GitHub issue template with sub-issues"""
        if parent_id not in self.issues:
            return ""
        
        issue = self.issues[parent_id]
        sub_issue_ids = issue['sub_issues']
        
        template = f"# {issue['title']}\n\n"
        template += f"{issue['description']}\n\n"
        template += "## Sub-Tasks\n\n"
        
        for sub_id in sub_issue_ids:
            sub = self.sub_issues[sub_id]
            checkbox = "x" if sub.status == IssueStatus.COMPLETED else " "
            template += f"- [{checkbox}] {sub.title}\n"
            if sub.assignee:
                template += f"  - Assignee: @{sub.assignee}\n"
        
        completion = self.calculate_completion_percentage(parent_id)
        template += f"\n**Progress: {completion:.1f}% complete**\n"
        
        return template
    
    def generate_report(self, output_file: str = "sub_issue_tracker_report.json") -> Dict:
        """Generate sub-issue tracking report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_parent_issues': len(self.issues),
            'total_sub_issues': len(self.sub_issues),
            'issues': []
        }
        
        for issue_id, issue in self.issues.items():
            issue_report = {
                'id': issue_id,
                'title': issue['title'],
                'total_sub_issues': len(issue['sub_issues']),
                'completion': self.calculate_completion_percentage(issue_id),
                'sub_issues': []
            }
            
            for sub_id in issue['sub_issues']:
                sub = self.sub_issues[sub_id]
                issue_report['sub_issues'].append({
                    'id': sub.id,
                    'title': sub.title,
                    'status': sub.status.value,
                    'assignee': sub.assignee
                })
            
            report['issues'].append(issue_report)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


def main():
    """Initialize sub-issue tracker"""
    tracker = SubIssueTracker()
    
    # Create sub-issues for PR #141
    tracker.create_pr_141_sub_issues()
    
    # Generate GitHub issue template
    template = tracker.generate_github_issue_template("pr-141")
    print("\nGitHub Issue Template:")
    print("=" * 60)
    print(template)
    print("=" * 60)
    
    # Generate report
    report = tracker.generate_report()
    
    print(f"\n{'='*60}")
    print("SUB-ISSUE TRACKING REPORT")
    print(f"{'='*60}")
    print(f"Total Parent Issues: {report['total_parent_issues']}")
    print(f"Total Sub-Issues: {report['total_sub_issues']}")
    for issue in report['issues']:
        print(f"\n{issue['title']}")
        print(f"  Progress: {issue['completion']:.1f}%")
        print(f"  Sub-issues: {issue['total_sub_issues']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
