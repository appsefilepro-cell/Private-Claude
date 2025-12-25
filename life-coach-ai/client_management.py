"""
Client Management System
Comprehensive client tracking, profiles, and relationship management
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set
from datetime import datetime, date
from enum import Enum
import json
import uuid


class ClientStatus(Enum):
    """Client engagement status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    PROSPECTIVE = "prospective"


class CoachingPackage(Enum):
    """Available coaching packages"""
    DISCOVERY = "discovery_session"  # Single session
    STARTER = "starter_package"  # 4 sessions
    GROWTH = "growth_package"  # 12 sessions
    TRANSFORMATION = "transformation_package"  # 24 sessions
    EXECUTIVE = "executive_coaching"  # Custom
    CUSTOM = "custom"


@dataclass
class ClientContact:
    """Client contact information"""
    email: str
    phone: Optional[str] = None
    preferred_contact: str = "email"  # email, phone, text
    timezone: str = "UTC"
    address: Optional[str] = None
    emergency_contact: Optional[str] = None


@dataclass
class ClientValues:
    """Client's core values and what matters to them"""
    core_values: List[str] = field(default_factory=list)
    life_priorities: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    growth_areas: List[str] = field(default_factory=list)
    motivators: List[str] = field(default_factory=list)


@dataclass
class ClientBackground:
    """Client's background and context"""
    occupation: Optional[str] = None
    industry: Optional[str] = None
    life_stage: Optional[str] = None  # e.g., "early career", "midlife transition"
    relationship_status: Optional[str] = None
    family_situation: Optional[str] = None
    education: Optional[str] = None
    significant_life_events: List[str] = field(default_factory=list)
    relevant_history: Optional[str] = None


@dataclass
class CoachingFocus:
    """Areas of focus for coaching"""
    primary_focus: str
    secondary_focuses: List[str] = field(default_factory=list)
    life_areas_to_develop: List[str] = field(default_factory=list)  # Career, relationships, health, etc.
    challenges: List[str] = field(default_factory=list)
    desired_outcomes: List[str] = field(default_factory=list)
    transformation_vision: Optional[str] = None


@dataclass
class ClientProfile:
    """Comprehensive client profile"""
    client_id: str
    first_name: str
    last_name: str
    contact: ClientContact

    # Core information
    status: ClientStatus = ClientStatus.PROSPECTIVE
    start_date: Optional[date] = None
    package: Optional[CoachingPackage] = None

    # Deep understanding
    values: ClientValues = field(default_factory=ClientValues)
    background: ClientBackground = field(default_factory=ClientBackground)
    coaching_focus: Optional[CoachingFocus] = None

    # Session tracking
    total_sessions: int = 0
    sessions_remaining: int = 0

    # Preferences
    communication_style: Optional[str] = None  # direct, gentle, challenging, supportive
    learning_style: Optional[str] = None  # visual, auditory, kinesthetic, reading
    best_time_for_sessions: Optional[str] = None
    session_frequency: Optional[str] = None  # weekly, bi-weekly, monthly

    # Notes and insights
    coach_notes: List[str] = field(default_factory=list)
    breakthrough_moments: List[str] = field(default_factory=list)
    recurring_patterns: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert datetime objects to strings
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.start_date:
            data['start_date'] = self.start_date.isoformat()
        # Convert enums to values
        data['status'] = self.status.value
        if self.package:
            data['package'] = self.package.value
        # Convert sets to lists for JSON
        data['tags'] = list(self.tags)
        return data

    @property
    def full_name(self) -> str:
        """Get client's full name"""
        return f"{self.first_name} {self.last_name}"

    def add_note(self, note: str):
        """Add a coach note"""
        self.coach_notes.append({
            'note': note,
            'timestamp': datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def add_breakthrough(self, breakthrough: str):
        """Record a breakthrough moment"""
        self.breakthrough_moments.append({
            'breakthrough': breakthrough,
            'timestamp': datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def add_pattern(self, pattern: str):
        """Record a recurring pattern"""
        if pattern not in self.recurring_patterns:
            self.recurring_patterns.append(pattern)
            self.updated_at = datetime.now()


class ClientManager:
    """
    Manages all client profiles and relationships
    """

    def __init__(self, storage_path: str = "data/clients.json"):
        self.storage_path = storage_path
        self.clients: Dict[str, ClientProfile] = {}
        self.load_clients()

    def create_client(self,
                     first_name: str,
                     last_name: str,
                     email: str,
                     phone: Optional[str] = None) -> ClientProfile:
        """Create a new client profile"""
        client_id = str(uuid.uuid4())

        contact = ClientContact(
            email=email,
            phone=phone
        )

        client = ClientProfile(
            client_id=client_id,
            first_name=first_name,
            last_name=last_name,
            contact=contact
        )

        self.clients[client_id] = client
        self.save_clients()

        return client

    def get_client(self, client_id: str) -> Optional[ClientProfile]:
        """Retrieve a client profile"""
        return self.clients.get(client_id)

    def get_client_by_email(self, email: str) -> Optional[ClientProfile]:
        """Find client by email"""
        for client in self.clients.values():
            if client.contact.email.lower() == email.lower():
                return client
        return None

    def update_client(self, client_id: str, updates: Dict) -> bool:
        """Update client profile"""
        client = self.get_client(client_id)
        if not client:
            return False

        # Update fields
        for key, value in updates.items():
            if hasattr(client, key):
                setattr(client, key, value)

        client.updated_at = datetime.now()
        self.save_clients()
        return True

    def get_active_clients(self) -> List[ClientProfile]:
        """Get all active clients"""
        return [
            client for client in self.clients.values()
            if client.status == ClientStatus.ACTIVE
        ]

    def get_clients_by_status(self, status: ClientStatus) -> List[ClientProfile]:
        """Get clients by status"""
        return [
            client for client in self.clients.values()
            if client.status == status
        ]

    def search_clients(self, query: str) -> List[ClientProfile]:
        """Search clients by name, email, or tags"""
        query_lower = query.lower()
        results = []

        for client in self.clients.values():
            if (query_lower in client.first_name.lower() or
                query_lower in client.last_name.lower() or
                query_lower in client.contact.email.lower() or
                any(query_lower in tag.lower() for tag in client.tags)):
                results.append(client)

        return results

    def get_client_summary(self, client_id: str) -> Dict:
        """Get a summary of client's coaching journey"""
        client = self.get_client(client_id)
        if not client:
            return {}

        return {
            'name': client.full_name,
            'status': client.status.value,
            'total_sessions': client.total_sessions,
            'sessions_remaining': client.sessions_remaining,
            'start_date': client.start_date.isoformat() if client.start_date else None,
            'primary_focus': client.coaching_focus.primary_focus if client.coaching_focus else None,
            'breakthroughs': len(client.breakthrough_moments),
            'key_patterns': client.recurring_patterns[:3],
            'recent_notes': client.coach_notes[-3:] if client.coach_notes else []
        }

    def save_clients(self):
        """Save all client data to storage"""
        import os
        os.makedirs(os.path.dirname(self.storage_path) if os.path.dirname(self.storage_path) else '.', exist_ok=True)

        data = {
            client_id: client.to_dict()
            for client_id, client in self.clients.items()
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_clients(self):
        """Load client data from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                # Note: Full deserialization would require more complex reconstruction
                # This is a simplified version
                self.clients = {}
        except FileNotFoundError:
            self.clients = {}

    def export_client_data(self, client_id: str) -> str:
        """Export client data for transfer or backup"""
        client = self.get_client(client_id)
        if not client:
            return ""

        return json.dumps(client.to_dict(), indent=2)

    def get_coaching_stats(self) -> Dict:
        """Get overall coaching statistics"""
        total_clients = len(self.clients)
        active_clients = len(self.get_active_clients())
        total_sessions = sum(client.total_sessions for client in self.clients.values())

        return {
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': total_clients - active_clients,
            'total_sessions_delivered': total_sessions,
            'average_sessions_per_client': total_sessions / total_clients if total_clients > 0 else 0,
            'clients_by_package': self._count_by_package(),
            'clients_by_status': self._count_by_status()
        }

    def _count_by_package(self) -> Dict[str, int]:
        """Count clients by coaching package"""
        counts = {}
        for client in self.clients.values():
            if client.package:
                package = client.package.value
                counts[package] = counts.get(package, 0) + 1
        return counts

    def _count_by_status(self) -> Dict[str, int]:
        """Count clients by status"""
        counts = {}
        for client in self.clients.values():
            status = client.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts
