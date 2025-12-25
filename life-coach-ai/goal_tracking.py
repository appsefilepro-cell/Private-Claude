"""
Goal Setting and Accountability System
Track goals, progress, and accountability measures
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from enum import Enum
import json
import uuid


class GoalCategory(Enum):
    """Life areas for goals"""
    CAREER = "career"
    HEALTH = "health"
    RELATIONSHIPS = "relationships"
    PERSONAL_GROWTH = "personal_growth"
    FINANCIAL = "financial"
    SPIRITUAL = "spiritual"
    RECREATION = "recreation"
    CONTRIBUTION = "contribution"
    ENVIRONMENT = "environment"
    LEARNING = "learning"


class GoalStatus(Enum):
    """Goal progress status"""
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    ON_HOLD = "on_hold"
    ABANDONED = "abandoned"
    REVISED = "revised"


class GoalTimeframe(Enum):
    """Goal timeframes"""
    IMMEDIATE = "immediate"  # This week
    SHORT_TERM = "short_term"  # 1-3 months
    MEDIUM_TERM = "medium_term"  # 3-12 months
    LONG_TERM = "long_term"  # 1+ years
    LIFETIME = "lifetime"


@dataclass
class SMARTCriteria:
    """SMART goal criteria"""
    specific: str  # What exactly will you accomplish?
    measurable: str  # How will you measure success?
    achievable: str  # What makes this achievable?
    relevant: str  # Why is this important to you?
    time_bound: str  # When will you achieve this?


@dataclass
class GoalMilestone:
    """Milestone toward a goal"""
    milestone_id: str
    description: str
    target_date: date
    completed: bool = False
    completed_date: Optional[date] = None
    notes: Optional[str] = None


@dataclass
class Goal:
    """Comprehensive goal tracking"""
    goal_id: str
    client_id: str
    title: str
    description: str

    # Classification
    category: GoalCategory
    timeframe: GoalTimeframe
    status: GoalStatus = GoalStatus.DRAFT

    # SMART criteria
    smart_criteria: Optional[SMARTCriteria] = None

    # Timing
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    achieved_date: Optional[date] = None

    # Motivation
    why_important: str = ""
    values_aligned: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    cost_of_not_achieving: Optional[str] = None

    # Planning
    action_steps: List[str] = field(default_factory=list)
    milestones: List[GoalMilestone] = field(default_factory=list)
    resources_needed: List[str] = field(default_factory=list)
    potential_obstacles: List[str] = field(default_factory=list)
    support_needed: List[str] = field(default_factory=list)

    # Progress tracking
    progress_percentage: int = 0
    progress_notes: List[Dict] = field(default_factory=list)
    wins: List[str] = field(default_factory=list)
    challenges_faced: List[str] = field(default_factory=list)

    # Accountability
    accountability_partner: Optional[str] = None
    check_in_frequency: Optional[str] = None  # daily, weekly, bi-weekly
    last_check_in: Optional[date] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['category'] = self.category.value
        data['timeframe'] = self.timeframe.value
        data['status'] = self.status.value
        if self.start_date:
            data['start_date'] = self.start_date.isoformat()
        if self.target_date:
            data['target_date'] = self.target_date.isoformat()
        if self.achieved_date:
            data['achieved_date'] = self.achieved_date.isoformat()
        if self.last_check_in:
            data['last_check_in'] = self.last_check_in.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    def update_progress(self, percentage: int, note: str = ""):
        """Update goal progress"""
        self.progress_percentage = max(0, min(100, percentage))
        self.progress_notes.append({
            'date': datetime.now().isoformat(),
            'percentage': percentage,
            'note': note
        })
        self.updated_at = datetime.now()

        if percentage >= 100:
            self.status = GoalStatus.ACHIEVED
            self.achieved_date = date.today()

    def add_milestone(self, description: str, target_date: date) -> GoalMilestone:
        """Add a milestone to the goal"""
        milestone = GoalMilestone(
            milestone_id=str(uuid.uuid4()),
            description=description,
            target_date=target_date
        )
        self.milestones.append(milestone)
        self.updated_at = datetime.now()
        return milestone

    def complete_milestone(self, milestone_id: str, note: str = ""):
        """Mark a milestone as completed"""
        for milestone in self.milestones:
            if milestone.milestone_id == milestone_id:
                milestone.completed = True
                milestone.completed_date = date.today()
                milestone.notes = note
                self.updated_at = datetime.now()

                # Update overall progress
                completed_count = sum(1 for m in self.milestones if m.completed)
                if self.milestones:
                    progress = int((completed_count / len(self.milestones)) * 100)
                    self.update_progress(progress, f"Milestone completed: {milestone.description}")
                break

    def add_win(self, win: str):
        """Celebrate a win toward this goal"""
        self.wins.append({
            'win': win,
            'date': datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def add_challenge(self, challenge: str):
        """Record a challenge faced"""
        self.challenges_faced.append({
            'challenge': challenge,
            'date': datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def check_in(self):
        """Record an accountability check-in"""
        self.last_check_in = date.today()
        self.updated_at = datetime.now()

    @property
    def days_until_target(self) -> Optional[int]:
        """Calculate days until target date"""
        if self.target_date:
            return (self.target_date - date.today()).days
        return None

    @property
    def is_overdue(self) -> bool:
        """Check if goal is overdue"""
        if self.target_date and self.status not in [GoalStatus.ACHIEVED, GoalStatus.ABANDONED]:
            return date.today() > self.target_date
        return False

    @property
    def milestones_completed(self) -> int:
        """Count completed milestones"""
        return sum(1 for m in self.milestones if m.completed)


class GoalTracker:
    """
    Manages goals and accountability
    """

    def __init__(self, storage_path: str = "data/goals.json"):
        self.storage_path = storage_path
        self.goals: Dict[str, Goal] = {}
        self.load_goals()

    def create_goal(self,
                   client_id: str,
                   title: str,
                   description: str,
                   category: GoalCategory,
                   timeframe: GoalTimeframe) -> Goal:
        """Create a new goal"""
        goal_id = str(uuid.uuid4())

        goal = Goal(
            goal_id=goal_id,
            client_id=client_id,
            title=title,
            description=description,
            category=category,
            timeframe=timeframe
        )

        self.goals[goal_id] = goal
        self.save_goals()

        return goal

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a specific goal"""
        return self.goals.get(goal_id)

    def get_client_goals(self, client_id: str, status: Optional[GoalStatus] = None) -> List[Goal]:
        """Get all goals for a client"""
        goals = [
            goal for goal in self.goals.values()
            if goal.client_id == client_id
        ]

        if status:
            goals = [g for g in goals if g.status == status]

        return sorted(goals, key=lambda g: g.created_at, reverse=True)

    def get_active_goals(self, client_id: str) -> List[Goal]:
        """Get client's active goals"""
        return [
            goal for goal in self.goals.values()
            if goal.client_id == client_id and goal.status in [GoalStatus.ACTIVE, GoalStatus.IN_PROGRESS]
        ]

    def get_goals_by_category(self, client_id: str, category: GoalCategory) -> List[Goal]:
        """Get goals in a specific category"""
        return [
            goal for goal in self.goals.values()
            if goal.client_id == client_id and goal.category == category
        ]

    def get_overdue_goals(self, client_id: str) -> List[Goal]:
        """Get overdue goals"""
        return [
            goal for goal in self.goals.values()
            if goal.client_id == client_id and goal.is_overdue
        ]

    def update_goal(self, goal_id: str, updates: Dict) -> bool:
        """Update goal details"""
        goal = self.get_goal(goal_id)
        if not goal:
            return False

        for key, value in updates.items():
            if hasattr(goal, key):
                setattr(goal, key, value)

        goal.updated_at = datetime.now()
        self.save_goals()
        return True

    def achieve_goal(self, goal_id: str, reflection: str = "") -> bool:
        """Mark a goal as achieved"""
        goal = self.get_goal(goal_id)
        if not goal:
            return False

        goal.status = GoalStatus.ACHIEVED
        goal.achieved_date = date.today()
        goal.progress_percentage = 100

        if reflection:
            goal.progress_notes.append({
                'date': datetime.now().isoformat(),
                'percentage': 100,
                'note': f"GOAL ACHIEVED! Reflection: {reflection}"
            })

        goal.updated_at = datetime.now()
        self.save_goals()
        return True

    def get_goal_summary(self, goal_id: str) -> Dict:
        """Get a summary of a goal"""
        goal = self.get_goal(goal_id)
        if not goal:
            return {}

        return {
            'title': goal.title,
            'category': goal.category.value,
            'status': goal.status.value,
            'progress': goal.progress_percentage,
            'target_date': goal.target_date.isoformat() if goal.target_date else None,
            'days_remaining': goal.days_until_target,
            'is_overdue': goal.is_overdue,
            'milestones_total': len(goal.milestones),
            'milestones_completed': goal.milestones_completed,
            'wins': len(goal.wins),
            'last_check_in': goal.last_check_in.isoformat() if goal.last_check_in else None
        }

    def get_client_goal_overview(self, client_id: str) -> Dict:
        """Get an overview of all client goals"""
        all_goals = self.get_client_goals(client_id)

        if not all_goals:
            return {'message': 'No goals set yet'}

        status_counts = {}
        for goal in all_goals:
            status = goal.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        category_counts = {}
        for goal in all_goals:
            category = goal.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        active_goals = [g for g in all_goals if g.status in [GoalStatus.ACTIVE, GoalStatus.IN_PROGRESS]]
        avg_progress = sum(g.progress_percentage for g in active_goals) / len(active_goals) if active_goals else 0

        return {
            'total_goals': len(all_goals),
            'active_goals': len(active_goals),
            'achieved_goals': status_counts.get('achieved', 0),
            'goals_by_status': status_counts,
            'goals_by_category': category_counts,
            'average_progress': round(avg_progress, 1),
            'overdue_goals': len(self.get_overdue_goals(client_id)),
            'total_wins': sum(len(g.wins) for g in all_goals)
        }

    def generate_accountability_report(self, client_id: str) -> str:
        """Generate an accountability report"""
        active_goals = self.get_active_goals(client_id)

        if not active_goals:
            return "No active goals to report on."

        report = "ACCOUNTABILITY REPORT\n"
        report += "=" * 50 + "\n\n"

        for goal in active_goals:
            report += f"Goal: {goal.title}\n"
            report += f"Progress: {goal.progress_percentage}%\n"

            if goal.target_date:
                days = goal.days_until_target
                if days and days > 0:
                    report += f"Days remaining: {days}\n"
                elif goal.is_overdue:
                    report += "STATUS: OVERDUE\n"

            if goal.last_check_in:
                days_since = (date.today() - goal.last_check_in).days
                report += f"Last check-in: {days_since} days ago\n"

            # Recent wins
            if goal.wins:
                recent_wins = goal.wins[-3:]
                report += f"Recent wins:\n"
                for win in recent_wins:
                    report += f"  - {win['win']}\n"

            # Pending milestones
            pending = [m for m in goal.milestones if not m.completed]
            if pending:
                report += f"Next milestones:\n"
                for milestone in pending[:3]:
                    report += f"  - {milestone.description} (by {milestone.target_date})\n"

            report += "\n"

        return report

    def save_goals(self):
        """Save all goals to storage"""
        import os
        os.makedirs(os.path.dirname(self.storage_path) if os.path.dirname(self.storage_path) else '.', exist_ok=True)

        data = {
            goal_id: goal.to_dict()
            for goal_id, goal in self.goals.items()
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_goals(self):
        """Load goals from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.goals = {}
        except FileNotFoundError:
            self.goals = {}
