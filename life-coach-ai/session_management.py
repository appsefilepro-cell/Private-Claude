"""
Session Management System
Track, manage, and analyze coaching sessions
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid


class SessionType(Enum):
    """Types of coaching sessions"""
    DISCOVERY = "discovery"
    REGULAR = "regular"
    INTENSIVE = "intensive"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"
    CLOSURE = "closure"


class SessionStatus(Enum):
    """Session status"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


@dataclass
class SessionGoals:
    """Goals and intentions for a session"""
    primary_intention: str
    desired_outcomes: List[str] = field(default_factory=list)
    topics_to_explore: List[str] = field(default_factory=list)
    questions_to_address: List[str] = field(default_factory=list)


@dataclass
class SessionInsights:
    """Insights and observations from a session"""
    key_insights: List[str] = field(default_factory=list)
    breakthroughs: List[str] = field(default_factory=list)
    aha_moments: List[str] = field(default_factory=list)
    patterns_observed: List[str] = field(default_factory=list)
    resistance_points: List[str] = field(default_factory=list)
    emotional_shifts: List[str] = field(default_factory=list)
    coach_observations: List[str] = field(default_factory=list)


@dataclass
class SessionOutcomes:
    """Outcomes and actions from a session"""
    commitments_made: List[Dict] = field(default_factory=list)  # {action, deadline, accountability}
    decisions_made: List[str] = field(default_factory=list)
    new_perspectives: List[str] = field(default_factory=list)
    homework_assigned: List[str] = field(default_factory=list)
    resources_shared: List[str] = field(default_factory=list)
    next_session_focus: Optional[str] = None


@dataclass
class SessionNotes:
    """Comprehensive session notes"""
    session_id: str
    client_id: str
    client_name: str

    # Session details
    session_type: SessionType
    session_number: int
    status: SessionStatus

    # Timing
    scheduled_datetime: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    duration_minutes: int = 60

    # Content
    goals: Optional[SessionGoals] = None
    topics_discussed: List[str] = field(default_factory=list)
    frameworks_used: List[str] = field(default_factory=list)

    # Client state
    client_energy_level: int = 5  # 1-10 scale
    client_mood: Optional[str] = None
    client_openness: int = 5  # 1-10 scale

    # Session content
    key_quotes: List[str] = field(default_factory=list)
    insights: SessionInsights = field(default_factory=SessionInsights)
    outcomes: SessionOutcomes = field(default_factory=SessionOutcomes)

    # Notes
    session_summary: Optional[str] = None
    coach_reflection: Optional[str] = None
    client_feedback: Optional[str] = None
    session_rating: Optional[int] = None  # 1-10 from client

    # Follow-up
    follow_up_needed: bool = False
    follow_up_notes: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['session_type'] = self.session_type.value
        data['status'] = self.status.value
        data['scheduled_datetime'] = self.scheduled_datetime.isoformat()
        if self.actual_start:
            data['actual_start'] = self.actual_start.isoformat()
        if self.actual_end:
            data['actual_end'] = self.actual_end.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @property
    def actual_duration(self) -> Optional[int]:
        """Calculate actual session duration"""
        if self.actual_start and self.actual_end:
            return int((self.actual_end - self.actual_start).total_seconds() / 60)
        return None

    def start_session(self):
        """Mark session as started"""
        self.actual_start = datetime.now()
        self.status = SessionStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def end_session(self):
        """Mark session as completed"""
        self.actual_end = datetime.now()
        self.status = SessionStatus.COMPLETED
        self.updated_at = datetime.now()

    def add_commitment(self, action: str, deadline: datetime, accountability_method: str = "next session"):
        """Add a client commitment"""
        self.outcomes.commitments_made.append({
            'action': action,
            'deadline': deadline.isoformat(),
            'accountability_method': accountability_method,
            'created_at': datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def add_insight(self, insight: str, insight_type: str = "general"):
        """Add an insight from the session"""
        if insight_type == "breakthrough":
            self.insights.breakthroughs.append(insight)
        elif insight_type == "aha":
            self.insights.aha_moments.append(insight)
        elif insight_type == "pattern":
            self.insights.patterns_observed.append(insight)
        else:
            self.insights.key_insights.append(insight)
        self.updated_at = datetime.now()


class SessionManager:
    """
    Manages coaching sessions - scheduling, tracking, and analysis
    """

    def __init__(self, storage_path: str = "data/sessions.json"):
        self.storage_path = storage_path
        self.sessions: Dict[str, SessionNotes] = {}
        self.load_sessions()

    def schedule_session(self,
                        client_id: str,
                        client_name: str,
                        scheduled_datetime: datetime,
                        session_type: SessionType = SessionType.REGULAR,
                        duration_minutes: int = 60) -> SessionNotes:
        """Schedule a new session"""
        session_id = str(uuid.uuid4())

        # Get session number for this client
        client_sessions = self.get_client_sessions(client_id)
        session_number = len(client_sessions) + 1

        session = SessionNotes(
            session_id=session_id,
            client_id=client_id,
            client_name=client_name,
            session_type=session_type,
            session_number=session_number,
            status=SessionStatus.SCHEDULED,
            scheduled_datetime=scheduled_datetime,
            duration_minutes=duration_minutes
        )

        self.sessions[session_id] = session
        self.save_sessions()

        return session

    def get_session(self, session_id: str) -> Optional[SessionNotes]:
        """Get a specific session"""
        return self.sessions.get(session_id)

    def get_client_sessions(self, client_id: str) -> List[SessionNotes]:
        """Get all sessions for a client"""
        sessions = [
            session for session in self.sessions.values()
            if session.client_id == client_id
        ]
        return sorted(sessions, key=lambda s: s.scheduled_datetime)

    def get_upcoming_sessions(self, days_ahead: int = 7) -> List[SessionNotes]:
        """Get upcoming sessions within specified days"""
        now = datetime.now()
        future = now + timedelta(days=days_ahead)

        upcoming = [
            session for session in self.sessions.values()
            if (session.status in [SessionStatus.SCHEDULED, SessionStatus.CONFIRMED] and
                now <= session.scheduled_datetime <= future)
        ]

        return sorted(upcoming, key=lambda s: s.scheduled_datetime)

    def get_sessions_today(self) -> List[SessionNotes]:
        """Get sessions scheduled for today"""
        today = datetime.now().date()

        today_sessions = [
            session for session in self.sessions.values()
            if (session.scheduled_datetime.date() == today and
                session.status not in [SessionStatus.CANCELLED, SessionStatus.NO_SHOW])
        ]

        return sorted(today_sessions, key=lambda s: s.scheduled_datetime)

    def update_session(self, session_id: str, updates: Dict) -> bool:
        """Update session details"""
        session = self.get_session(session_id)
        if not session:
            return False

        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.updated_at = datetime.now()
        self.save_sessions()
        return True

    def cancel_session(self, session_id: str, reason: Optional[str] = None) -> bool:
        """Cancel a session"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = SessionStatus.CANCELLED
        if reason:
            session.follow_up_notes = f"Cancellation reason: {reason}"
        session.updated_at = datetime.now()

        self.save_sessions()
        return True

    def reschedule_session(self, session_id: str, new_datetime: datetime) -> bool:
        """Reschedule a session"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = SessionStatus.RESCHEDULED
        session.scheduled_datetime = new_datetime
        session.updated_at = datetime.now()

        self.save_sessions()
        return True

    def get_session_summary(self, session_id: str) -> Dict:
        """Get a comprehensive summary of a session"""
        session = self.get_session(session_id)
        if not session:
            return {}

        return {
            'session_number': session.session_number,
            'client_name': session.client_name,
            'date': session.scheduled_datetime.isoformat(),
            'duration': session.actual_duration or session.duration_minutes,
            'status': session.status.value,
            'topics_discussed': session.topics_discussed,
            'key_insights': session.insights.key_insights,
            'breakthroughs': session.insights.breakthroughs,
            'commitments': len(session.outcomes.commitments_made),
            'session_rating': session.session_rating,
            'summary': session.session_summary
        }

    def generate_session_report(self, session_id: str) -> str:
        """Generate a detailed session report"""
        session = self.get_session(session_id)
        if not session:
            return ""

        report = f"""
COACHING SESSION REPORT
========================

Client: {session.client_name}
Session #{session.session_number}
Date: {session.scheduled_datetime.strftime('%B %d, %Y at %I:%M %p')}
Duration: {session.actual_duration or session.duration_minutes} minutes
Type: {session.session_type.value.title()}

SESSION FOCUS
-------------
"""
        if session.goals:
            report += f"Primary Intention: {session.goals.primary_intention}\n"
            if session.goals.desired_outcomes:
                report += "Desired Outcomes:\n"
                for outcome in session.goals.desired_outcomes:
                    report += f"  - {outcome}\n"

        report += f"\nTOPICS EXPLORED\n--------------\n"
        for topic in session.topics_discussed:
            report += f"  - {topic}\n"

        if session.insights.key_insights:
            report += f"\nKEY INSIGHTS\n------------\n"
            for insight in session.insights.key_insights:
                report += f"  - {insight}\n"

        if session.insights.breakthroughs:
            report += f"\nBREAKTHROUGHS\n-------------\n"
            for breakthrough in session.insights.breakthroughs:
                report += f"  - {breakthrough}\n"

        if session.outcomes.commitments_made:
            report += f"\nCOMMITMENTS & ACTION ITEMS\n-------------------------\n"
            for commitment in session.outcomes.commitments_made:
                report += f"  - {commitment['action']}\n"
                report += f"    Deadline: {commitment['deadline']}\n"

        if session.outcomes.next_session_focus:
            report += f"\nNEXT SESSION FOCUS\n-----------------\n{session.outcomes.next_session_focus}\n"

        if session.session_summary:
            report += f"\nSESSION SUMMARY\n--------------\n{session.session_summary}\n"

        return report

    def get_client_progress_summary(self, client_id: str) -> Dict:
        """Get an overview of client's progress across sessions"""
        sessions = self.get_client_sessions(client_id)
        completed_sessions = [s for s in sessions if s.status == SessionStatus.COMPLETED]

        if not completed_sessions:
            return {'message': 'No completed sessions yet'}

        total_insights = sum(
            len(s.insights.key_insights) + len(s.insights.breakthroughs)
            for s in completed_sessions
        )

        total_commitments = sum(
            len(s.outcomes.commitments_made)
            for s in completed_sessions
        )

        avg_rating = None
        ratings = [s.session_rating for s in completed_sessions if s.session_rating]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)

        return {
            'total_sessions': len(sessions),
            'completed_sessions': len(completed_sessions),
            'total_insights': total_insights,
            'total_breakthroughs': sum(len(s.insights.breakthroughs) for s in completed_sessions),
            'total_commitments': total_commitments,
            'average_rating': avg_rating,
            'frameworks_used': list(set(
                framework
                for s in completed_sessions
                for framework in s.frameworks_used
            )),
            'common_topics': self._get_common_topics(completed_sessions)
        }

    def _get_common_topics(self, sessions: List[SessionNotes]) -> List[str]:
        """Identify common topics across sessions"""
        topic_counts = {}
        for session in sessions:
            for topic in session.topics_discussed:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # Return topics mentioned in multiple sessions
        return [
            topic for topic, count in topic_counts.items()
            if count >= 2
        ]

    def save_sessions(self):
        """Save all session data"""
        import os
        os.makedirs(os.path.dirname(self.storage_path) if os.path.dirname(self.storage_path) else '.', exist_ok=True)

        data = {
            session_id: session.to_dict()
            for session_id, session in self.sessions.items()
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_sessions(self):
        """Load session data"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.sessions = {}
        except FileNotFoundError:
            self.sessions = {}
