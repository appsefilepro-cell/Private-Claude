"""
Progress Monitoring and Analytics
Track client progress, generate insights, and create reports
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


@dataclass
class ProgressMetrics:
    """Client progress metrics"""
    client_id: str
    client_name: str

    # Overall metrics
    total_sessions: int = 0
    sessions_completed: int = 0
    coaching_start_date: Optional[datetime] = None
    days_in_coaching: int = 0

    # Goal metrics
    total_goals: int = 0
    active_goals: int = 0
    achieved_goals: int = 0
    average_goal_progress: float = 0.0

    # Engagement metrics
    session_attendance_rate: float = 0.0
    commitment_completion_rate: float = 0.0
    average_session_rating: float = 0.0

    # Growth indicators
    total_breakthroughs: int = 0
    total_insights: int = 0
    total_wins: int = 0
    growth_areas_count: int = 0

    # Recent activity
    last_session_date: Optional[datetime] = None
    days_since_last_session: int = 0
    next_session_date: Optional[datetime] = None

    # Patterns
    common_topics: List[str] = field(default_factory=list)
    recurring_patterns: List[str] = field(default_factory=list)
    strongest_values: List[str] = field(default_factory=list)


@dataclass
class ProgressReport:
    """Comprehensive progress report"""
    client_id: str
    client_name: str
    report_period_start: datetime
    report_period_end: datetime
    generated_at: datetime = field(default_factory=datetime.now)

    # Summary
    executive_summary: str = ""
    key_highlights: List[str] = field(default_factory=list)

    # Progress by area
    goals_progress: Dict = field(default_factory=dict)
    life_areas_improvement: Dict = field(default_factory=dict)

    # Session analysis
    sessions_in_period: int = 0
    topics_explored: List[str] = field(default_factory=list)
    frameworks_used: List[str] = field(default_factory=list)

    # Achievements
    goals_achieved: List[str] = field(default_factory=list)
    significant_wins: List[str] = field(default_factory=list)
    breakthroughs: List[str] = field(default_factory=list)

    # Insights
    emerging_patterns: List[str] = field(default_factory=list)
    areas_of_growth: List[str] = field(default_factory=list)
    areas_of_strength: List[str] = field(default_factory=list)

    # Recommendations
    focus_areas_next_period: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)


class ProgressAnalyzer:
    """
    Analyzes client progress and generates insights
    """

    def __init__(self, client_manager, session_manager, goal_tracker):
        self.client_manager = client_manager
        self.session_manager = session_manager
        self.goal_tracker = goal_tracker

    def calculate_client_metrics(self, client_id: str) -> ProgressMetrics:
        """Calculate comprehensive progress metrics for a client"""
        client = self.client_manager.get_client(client_id)
        if not client:
            return None

        metrics = ProgressMetrics(
            client_id=client_id,
            client_name=client.full_name,
            coaching_start_date=client.start_date,
            total_sessions=client.total_sessions
        )

        # Calculate days in coaching
        if client.start_date:
            metrics.days_in_coaching = (datetime.now().date() - client.start_date).days

        # Session metrics
        sessions = self.session_manager.get_client_sessions(client_id)
        completed_sessions = [s for s in sessions if s.status.value == 'completed']
        metrics.sessions_completed = len(completed_sessions)

        if sessions:
            metrics.session_attendance_rate = len(completed_sessions) / len(sessions) * 100
            metrics.last_session_date = sessions[-1].scheduled_datetime
            metrics.days_since_last_session = (
                datetime.now() - metrics.last_session_date
            ).days if metrics.last_session_date else 0

        # Session ratings
        ratings = [s.session_rating for s in completed_sessions if s.session_rating]
        if ratings:
            metrics.average_session_rating = statistics.mean(ratings)

        # Goal metrics
        goals = self.goal_tracker.get_client_goals(client_id)
        metrics.total_goals = len(goals)

        active_goals = [g for g in goals if g.status.value in ['active', 'in_progress']]
        metrics.active_goals = len(active_goals)

        achieved_goals = [g for g in goals if g.status.value == 'achieved']
        metrics.achieved_goals = len(achieved_goals)

        if active_goals:
            metrics.average_goal_progress = statistics.mean(
                [g.progress_percentage for g in active_goals]
            )

        # Breakthroughs and insights
        for session in completed_sessions:
            metrics.total_breakthroughs += len(session.insights.breakthroughs)
            metrics.total_insights += len(session.insights.key_insights)

        # Wins
        for goal in goals:
            metrics.total_wins += len(goal.wins)

        # Common topics
        topic_frequency = defaultdict(int)
        for session in completed_sessions:
            for topic in session.topics_discussed:
                topic_frequency[topic] += 1

        metrics.common_topics = sorted(
            topic_frequency.keys(),
            key=lambda t: topic_frequency[t],
            reverse=True
        )[:5]

        # Recurring patterns
        metrics.recurring_patterns = client.recurring_patterns[:5]

        # Values
        if client.values and client.values.core_values:
            metrics.strongest_values = client.values.core_values[:3]

        return metrics

    def generate_progress_report(self,
                                client_id: str,
                                period_days: int = 30) -> ProgressReport:
        """Generate a comprehensive progress report"""
        client = self.client_manager.get_client(client_id)
        if not client:
            return None

        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        report = ProgressReport(
            client_id=client_id,
            client_name=client.full_name,
            report_period_start=start_date,
            report_period_end=end_date
        )

        # Get data for the period
        all_sessions = self.session_manager.get_client_sessions(client_id)
        period_sessions = [
            s for s in all_sessions
            if start_date <= s.scheduled_datetime <= end_date
               and s.status.value == 'completed'
        ]

        report.sessions_in_period = len(period_sessions)

        # Analyze sessions
        topics = set()
        frameworks = set()
        significant_wins = []
        breakthroughs = []

        for session in period_sessions:
            topics.update(session.topics_discussed)
            frameworks.update(session.frameworks_used)

            if session.insights.breakthroughs:
                breakthroughs.extend(session.insights.breakthroughs)

            # Extract wins from session outcomes
            for commitment in session.outcomes.commitments_made:
                # This would ideally check if commitment was completed
                pass

        report.topics_explored = list(topics)
        report.frameworks_used = list(frameworks)
        report.breakthroughs = breakthroughs

        # Goal achievements in period
        all_goals = self.goal_tracker.get_client_goals(client_id)
        period_achievements = [
            g for g in all_goals
            if g.achieved_date and start_date.date() <= g.achieved_date <= end_date.date()
        ]

        report.goals_achieved = [g.title for g in period_achievements]

        # Collect wins
        for goal in all_goals:
            for win in goal.wins:
                win_date = datetime.fromisoformat(win['date'])
                if start_date <= win_date <= end_date:
                    report.significant_wins.append(win['win'])

        # Generate executive summary
        report.executive_summary = self._generate_executive_summary(
            client,
            report,
            period_sessions
        )

        # Generate recommendations
        report.focus_areas_next_period = self._generate_recommendations(
            client,
            all_goals,
            period_sessions
        )

        return report

    def _generate_executive_summary(self,
                                   client,
                                   report: ProgressReport,
                                   sessions: List) -> str:
        """Generate executive summary of progress"""
        summary = f"{client.full_name} has "

        if report.sessions_in_period > 0:
            summary += f"completed {report.sessions_in_period} coaching session"
            summary += "s" if report.sessions_in_period > 1 else ""
            summary += " during this period. "
        else:
            summary += "not had any sessions during this period. "

        if report.goals_achieved:
            summary += f"Notably, {len(report.goals_achieved)} goal"
            summary += "s were" if len(report.goals_achieved) > 1 else " was"
            summary += " achieved. "

        if report.breakthroughs:
            summary += f"{len(report.breakthroughs)} significant breakthrough"
            summary += "s were" if len(report.breakthroughs) > 1 else " was"
            summary += " experienced. "

        if report.significant_wins:
            summary += f"Progress is evident through {len(report.significant_wins)} documented wins. "

        summary += "Coaching is creating measurable impact."

        return summary

    def _generate_recommendations(self,
                                 client,
                                 goals: List,
                                 sessions: List) -> List[str]:
        """Generate recommendations for next period"""
        recommendations = []

        # Check for overdue goals
        overdue = [g for g in goals if g.is_overdue]
        if overdue:
            recommendations.append(
                f"Address {len(overdue)} overdue goal(s) - revisit or revise timeline"
            )

        # Check for inactive goals
        inactive = [
            g for g in goals
            if g.status.value == 'active' and g.progress_percentage < 10
        ]
        if inactive:
            recommendations.append(
                "Several goals show minimal progress - may need renewed focus or revision"
            )

        # Check session frequency
        if sessions and len(sessions) < 2:
            recommendations.append(
                "Consider increasing session frequency for momentum"
            )

        # Suggest areas to explore
        if client.values and client.values.growth_areas:
            unexplored = [
                area for area in client.values.growth_areas
                if not any(area in s.topics_discussed for s in sessions)
            ]
            if unexplored:
                recommendations.append(
                    f"Explore identified growth areas: {', '.join(unexplored[:2])}"
                )

        if not recommendations:
            recommendations.append("Continue current momentum and focus")

        return recommendations

    def compare_periods(self,
                       client_id: str,
                       period1_days: int = 30,
                       period2_days: int = 30) -> Dict:
        """Compare two time periods for trends"""
        end_period1 = datetime.now()
        start_period1 = end_period1 - timedelta(days=period1_days)

        end_period2 = start_period1
        start_period2 = end_period2 - timedelta(days=period2_days)

        sessions = self.session_manager.get_client_sessions(client_id)

        period1_sessions = [
            s for s in sessions
            if start_period1 <= s.scheduled_datetime <= end_period1
        ]

        period2_sessions = [
            s for s in sessions
            if start_period2 <= s.scheduled_datetime <= end_period2
        ]

        return {
            'period1': {
                'sessions': len(period1_sessions),
                'date_range': f"{start_period1.date()} to {end_period1.date()}"
            },
            'period2': {
                'sessions': len(period2_sessions),
                'date_range': f"{start_period2.date()} to {end_period2.date()}"
            },
            'trend': 'increasing' if len(period1_sessions) > len(period2_sessions) else 'decreasing',
            'change': len(period1_sessions) - len(period2_sessions)
        }

    def generate_visual_report(self, client_id: str) -> str:
        """Generate a text-based visual progress report"""
        metrics = self.calculate_client_metrics(client_id)

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              COACHING PROGRESS DASHBOARD                      ║
╠══════════════════════════════════════════════════════════════╣
║ Client: {metrics.client_name:48} ║
║ Days in Coaching: {str(metrics.days_in_coaching):43} ║
╚══════════════════════════════════════════════════════════════╝

SESSIONS
────────────────────────────────────────────────────────────────
Total Sessions:        {metrics.total_sessions}
Completed:             {metrics.sessions_completed}
Attendance Rate:       {metrics.session_attendance_rate:.1f}%
Average Rating:        {metrics.average_session_rating:.1f}/10
Days Since Last:       {metrics.days_since_last_session}

GOALS
────────────────────────────────────────────────────────────────
Total Goals:           {metrics.total_goals}
Active Goals:          {metrics.active_goals}
Achieved Goals:        {metrics.achieved_goals}
Average Progress:      {metrics.average_goal_progress:.1f}%

GROWTH INDICATORS
────────────────────────────────────────────────────────────────
Breakthroughs:         {metrics.total_breakthroughs}
Key Insights:          {metrics.total_insights}
Wins Celebrated:       {metrics.total_wins}

TOP FOCUS AREAS
────────────────────────────────────────────────────────────────
"""
        for i, topic in enumerate(metrics.common_topics[:5], 1):
            report += f"{i}. {topic}\n"

        if metrics.strongest_values:
            report += "\nCORE VALUES\n"
            report += "─" * 64 + "\n"
            for value in metrics.strongest_values:
                report += f"• {value}\n"

        return report
