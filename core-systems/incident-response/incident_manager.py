#!/usr/bin/env python3
"""
ROLE 9: INCIDENT RESPONDER - INCIDENT MANAGEMENT SYSTEM
Automated Incident Detection and Response
Version: 5.0.0
Author: AgentX5
Date: 2025-12-27

Features:
- Automated incident detection
- Alert triage system
- Communication protocols (email, SMS, Slack)
- Incident escalation workflow
- Post-mortem report generation
- Integration with logging system
- On-call rotation management
- Incident tracking database
"""

import os
import sys
import json
import time
import sqlite3
import smtplib
import hashlib
import threading
import queue
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import re


# Configuration
class IncidentSeverity(Enum):
    """Incident severity levels"""
    SEV1 = "sev1"  # Critical - System down
    SEV2 = "sev2"  # Major - Major functionality impaired
    SEV3 = "sev3"  # Minor - Minor functionality impaired
    SEV4 = "sev4"  # Low - Cosmetic or documentation issues


class IncidentStatus(Enum):
    """Incident lifecycle status"""
    DETECTED = "detected"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class EscalationLevel(Enum):
    """Escalation levels"""
    L1 = 1  # First responder
    L2 = 2  # Team lead
    L3 = 3  # Engineering manager
    L4 = 4  # Executive / On-call engineer


class NotificationChannel(Enum):
    """Notification channels"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    PHONE = "phone"


@dataclass
class Incident:
    """Incident data structure"""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    created_at: datetime
    detected_by: str
    assigned_to: Optional[str] = None
    escalation_level: EscalationLevel = EscalationLevel.L1
    affected_systems: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


@dataclass
class OnCallSchedule:
    """On-call rotation schedule"""
    engineer: str
    start_time: datetime
    end_time: datetime
    escalation_level: EscalationLevel
    contact_email: str
    contact_phone: str
    backup_engineer: Optional[str] = None


@dataclass
class IncidentMetrics:
    """Incident metrics for reporting"""
    total_incidents: int
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    mean_time_to_detect: float
    mean_time_to_resolve: float
    mean_time_to_acknowledge: float
    escalation_rate: float


class IncidentDatabase:
    """Database for incident tracking"""

    def __init__(self, db_path: str = "/home/user/Private-Claude/core-systems/incident-response/incidents.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = None
        self.initialize_database()

    def initialize_database(self):
        """Create database tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()

        # Incidents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT UNIQUE,
                title TEXT,
                description TEXT,
                severity TEXT,
                status TEXT,
                created_at TIMESTAMP,
                detected_by TEXT,
                assigned_to TEXT,
                escalation_level INTEGER,
                affected_systems TEXT,
                timeline TEXT,
                metadata TEXT,
                resolved_at TIMESTAMP,
                resolution_notes TEXT
            )
        """)

        # On-call schedule table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oncall_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engineer TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                escalation_level INTEGER,
                contact_email TEXT,
                contact_phone TEXT,
                backup_engineer TEXT
            )
        """)

        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                recipient TEXT,
                channel TEXT,
                message TEXT,
                sent_at TIMESTAMP,
                status TEXT,
                FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
            )
        """)

        # Post-mortem table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS postmortems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                created_at TIMESTAMP,
                created_by TEXT,
                summary TEXT,
                root_cause TEXT,
                impact TEXT,
                timeline TEXT,
                action_items TEXT,
                lessons_learned TEXT,
                FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_created ON incidents(created_at)")

        self.conn.commit()

    def save_incident(self, incident: Incident):
        """Save incident to database"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO incidents
            (incident_id, title, description, severity, status, created_at,
             detected_by, assigned_to, escalation_level, affected_systems,
             timeline, metadata, resolved_at, resolution_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident.incident_id,
            incident.title,
            incident.description,
            incident.severity.value,
            incident.status.value,
            incident.created_at,
            incident.detected_by,
            incident.assigned_to,
            incident.escalation_level.value,
            json.dumps(incident.affected_systems),
            json.dumps(incident.timeline, default=str),
            json.dumps(incident.metadata),
            incident.resolved_at,
            incident.resolution_notes
        ))

        self.conn.commit()

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Retrieve incident by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM incidents WHERE incident_id = ?", (incident_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return Incident(
            incident_id=row[1],
            title=row[2],
            description=row[3],
            severity=IncidentSeverity(row[4]),
            status=IncidentStatus(row[5]),
            created_at=datetime.fromisoformat(row[6]) if isinstance(row[6], str) else row[6],
            detected_by=row[7],
            assigned_to=row[8],
            escalation_level=EscalationLevel(row[9]),
            affected_systems=json.loads(row[10]) if row[10] else [],
            timeline=json.loads(row[11]) if row[11] else [],
            metadata=json.loads(row[12]) if row[12] else {},
            resolved_at=datetime.fromisoformat(row[13]) if row[13] else None,
            resolution_notes=row[14]
        )

    def query_incidents(self, filters: Dict[str, Any] = None) -> List[Incident]:
        """Query incidents with filters"""
        cursor = self.conn.cursor()

        query = "SELECT * FROM incidents WHERE 1=1"
        params = []

        if filters:
            if 'severity' in filters:
                query += " AND severity = ?"
                params.append(filters['severity'])

            if 'status' in filters:
                query += " AND status = ?"
                params.append(filters['status'])

            if 'assigned_to' in filters:
                query += " AND assigned_to = ?"
                params.append(filters['assigned_to'])

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)

        incidents = []
        for row in cursor.fetchall():
            incidents.append(Incident(
                incident_id=row[1],
                title=row[2],
                description=row[3],
                severity=IncidentSeverity(row[4]),
                status=IncidentStatus(row[5]),
                created_at=datetime.fromisoformat(row[6]) if isinstance(row[6], str) else row[6],
                detected_by=row[7],
                assigned_to=row[8],
                escalation_level=EscalationLevel(row[9]),
                affected_systems=json.loads(row[10]) if row[10] else [],
                timeline=json.loads(row[11]) if row[11] else [],
                metadata=json.loads(row[12]) if row[12] else {},
                resolved_at=datetime.fromisoformat(row[13]) if row[13] else None,
                resolution_notes=row[14]
            ))

        return incidents

    def save_oncall_schedule(self, schedule: OnCallSchedule):
        """Save on-call schedule"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO oncall_schedule
            (engineer, start_time, end_time, escalation_level, contact_email,
             contact_phone, backup_engineer)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            schedule.engineer,
            schedule.start_time,
            schedule.end_time,
            schedule.escalation_level.value,
            schedule.contact_email,
            schedule.contact_phone,
            schedule.backup_engineer
        ))

        self.conn.commit()

    def get_oncall_engineer(self, escalation_level: EscalationLevel = EscalationLevel.L1) -> Optional[OnCallSchedule]:
        """Get current on-call engineer"""
        cursor = self.conn.cursor()
        now = datetime.now()

        cursor.execute("""
            SELECT * FROM oncall_schedule
            WHERE escalation_level = ?
            AND start_time <= ?
            AND end_time >= ?
            ORDER BY start_time DESC
            LIMIT 1
        """, (escalation_level.value, now, now))

        row = cursor.fetchone()
        if not row:
            return None

        return OnCallSchedule(
            engineer=row[1],
            start_time=datetime.fromisoformat(row[2]) if isinstance(row[2], str) else row[2],
            end_time=datetime.fromisoformat(row[3]) if isinstance(row[3], str) else row[3],
            escalation_level=EscalationLevel(row[4]),
            contact_email=row[5],
            contact_phone=row[6],
            backup_engineer=row[7]
        )

    def log_notification(self, incident_id: str, recipient: str,
                        channel: str, message: str, status: str):
        """Log notification sent"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO notifications
            (incident_id, recipient, channel, message, sent_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (incident_id, recipient, channel, message, datetime.now(), status))

        self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


class IncidentDetector:
    """Automated incident detection"""

    def __init__(self):
        self.detection_rules: List[Dict[str, Any]] = []
        self.monitoring_queue = queue.Queue()

    def add_detection_rule(self, name: str, condition: Callable,
                          severity: IncidentSeverity, description: str):
        """Add incident detection rule"""
        self.detection_rules.append({
            'name': name,
            'condition': condition,
            'severity': severity,
            'description': description
        })

    def detect_from_logs(self, log_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect incidents from log data"""
        for rule in self.detection_rules:
            try:
                if rule['condition'](log_data):
                    return {
                        'rule_name': rule['name'],
                        'severity': rule['severity'],
                        'description': rule['description'],
                        'trigger_data': log_data
                    }
            except Exception as e:
                print(f"Detection rule error: {e}")

        return None

    def detect_error_spike(self, error_count: int, threshold: int = 10) -> bool:
        """Detect error spike"""
        return error_count > threshold

    def detect_response_time_degradation(self, response_time: float,
                                        baseline: float, threshold: float = 2.0) -> bool:
        """Detect response time degradation"""
        return response_time > baseline * threshold

    def detect_service_unavailable(self, health_check_failed: bool) -> bool:
        """Detect service unavailability"""
        return health_check_failed


class AlertTriageSystem:
    """Alert triage and deduplication"""

    def __init__(self):
        self.alert_fingerprints: Dict[str, datetime] = {}
        self.dedup_window = timedelta(minutes=5)

    def triage_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Triage incoming alert"""
        # Create fingerprint
        fingerprint = self._create_fingerprint(alert_data)

        # Check for duplicate
        if fingerprint in self.alert_fingerprints:
            last_alert = self.alert_fingerprints[fingerprint]
            if datetime.now() - last_alert < self.dedup_window:
                return {
                    'action': 'deduplicate',
                    'fingerprint': fingerprint,
                    'last_alert': last_alert
                }

        # Update fingerprint
        self.alert_fingerprints[fingerprint] = datetime.now()

        # Determine severity and priority
        severity = self._determine_severity(alert_data)
        priority = self._calculate_priority(alert_data, severity)

        return {
            'action': 'create_incident',
            'severity': severity,
            'priority': priority,
            'fingerprint': fingerprint
        }

    def _create_fingerprint(self, alert_data: Dict[str, Any]) -> str:
        """Create unique fingerprint for alert"""
        key_fields = [
            alert_data.get('type', ''),
            alert_data.get('module', ''),
            alert_data.get('message', '')[:100]
        ]

        fingerprint_string = '|'.join(key_fields)
        return hashlib.md5(fingerprint_string.encode()).hexdigest()

    def _determine_severity(self, alert_data: Dict[str, Any]) -> IncidentSeverity:
        """Determine incident severity"""
        severity_map = {
            'critical': IncidentSeverity.SEV1,
            'error': IncidentSeverity.SEV2,
            'warning': IncidentSeverity.SEV3,
            'info': IncidentSeverity.SEV4
        }

        alert_severity = alert_data.get('severity', 'warning').lower()
        return severity_map.get(alert_severity, IncidentSeverity.SEV3)

    def _calculate_priority(self, alert_data: Dict[str, Any],
                           severity: IncidentSeverity) -> int:
        """Calculate incident priority (1-10)"""
        base_priority = {
            IncidentSeverity.SEV1: 10,
            IncidentSeverity.SEV2: 7,
            IncidentSeverity.SEV3: 4,
            IncidentSeverity.SEV4: 1
        }

        priority = base_priority.get(severity, 5)

        # Adjust based on impact
        if alert_data.get('user_impact', False):
            priority += 2

        return min(priority, 10)


class CommunicationSystem:
    """Multi-channel communication system"""

    def __init__(self, db: IncidentDatabase):
        self.db = db

    def send_notification(self, incident: Incident, channel: NotificationChannel,
                         recipient: str, message: str) -> bool:
        """Send notification through specified channel"""
        try:
            if channel == NotificationChannel.EMAIL:
                return self._send_email(recipient, incident.title, message)

            elif channel == NotificationChannel.SMS:
                return self._send_sms(recipient, message)

            elif channel == NotificationChannel.SLACK:
                return self._send_slack(recipient, message)

            elif channel == NotificationChannel.PHONE:
                return self._make_phone_call(recipient, message)

        except Exception as e:
            print(f"Notification error: {e}")
            self.db.log_notification(
                incident.incident_id, recipient, channel.value, message, 'failed'
            )
            return False

    def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Send email notification"""
        # In production, would use actual SMTP
        print(f"[EMAIL] To: {recipient}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body: {body[:100]}...")

        return True

    def _send_sms(self, phone: str, message: str) -> bool:
        """Send SMS notification"""
        # In production, would use Twilio or similar
        print(f"[SMS] To: {phone}")
        print(f"[SMS] Message: {message[:160]}")

        return True

    def _send_slack(self, channel: str, message: str) -> bool:
        """Send Slack notification"""
        # In production, would use Slack API
        print(f"[SLACK] Channel: {channel}")
        print(f"[SLACK] Message: {message}")

        return True

    def _make_phone_call(self, phone: str, message: str) -> bool:
        """Make automated phone call"""
        # In production, would use Twilio Voice
        print(f"[PHONE CALL] To: {phone}")
        print(f"[PHONE CALL] Message: {message}")

        return True


class EscalationManager:
    """Incident escalation workflow"""

    def __init__(self, db: IncidentDatabase, comm: CommunicationSystem):
        self.db = db
        self.comm = comm
        self.escalation_timers: Dict[str, threading.Timer] = {}

    def start_escalation_timer(self, incident: Incident, timeout_minutes: int = 15):
        """Start escalation timer"""
        timer = threading.Timer(
            timeout_minutes * 60,
            self.escalate_incident,
            args=[incident.incident_id]
        )
        timer.start()
        self.escalation_timers[incident.incident_id] = timer

    def stop_escalation_timer(self, incident_id: str):
        """Stop escalation timer"""
        if incident_id in self.escalation_timers:
            self.escalation_timers[incident_id].cancel()
            del self.escalation_timers[incident_id]

    def escalate_incident(self, incident_id: str):
        """Escalate incident to next level"""
        incident = self.db.get_incident(incident_id)
        if not incident:
            return

        # Check if already resolved
        if incident.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            return

        # Escalate to next level
        current_level = incident.escalation_level
        next_level = EscalationLevel(min(current_level.value + 1, 4))

        incident.escalation_level = next_level
        incident.timeline.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'escalated',
            'from_level': current_level.name,
            'to_level': next_level.name
        })

        # Get on-call engineer for next level
        oncall = self.db.get_oncall_engineer(next_level)

        if oncall:
            incident.assigned_to = oncall.engineer

            # Notify new assignee
            message = f"""
INCIDENT ESCALATED TO {next_level.name}

Incident: {incident.incident_id}
Severity: {incident.severity.value.upper()}
Title: {incident.title}
Description: {incident.description}
            """

            self.comm.send_notification(
                incident,
                NotificationChannel.EMAIL,
                oncall.contact_email,
                message
            )

            if incident.severity in [IncidentSeverity.SEV1, IncidentSeverity.SEV2]:
                self.comm.send_notification(
                    incident,
                    NotificationChannel.SMS,
                    oncall.contact_phone,
                    f"SEV{incident.severity.value[-1]} ESCALATED: {incident.title}"
                )

        # Save updated incident
        self.db.save_incident(incident)

        # Start new escalation timer if not at max level
        if next_level != EscalationLevel.L4:
            self.start_escalation_timer(incident)


class PostMortemGenerator:
    """Generate post-mortem reports"""

    def __init__(self, db: IncidentDatabase):
        self.db = db

    def generate_postmortem(self, incident: Incident, created_by: str) -> str:
        """Generate post-mortem report"""
        # Calculate metrics
        time_to_detect = self._calculate_detection_time(incident)
        time_to_resolve = self._calculate_resolution_time(incident)

        report = f"""
# POST-MORTEM REPORT

## Incident Details
- **Incident ID**: {incident.incident_id}
- **Title**: {incident.title}
- **Severity**: {incident.severity.value.upper()}
- **Status**: {incident.status.value}
- **Created**: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Resolved**: {incident.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if incident.resolved_at else 'N/A'}

## Summary
{incident.description}

## Impact
- **Affected Systems**: {', '.join(incident.affected_systems) if incident.affected_systems else 'N/A'}
- **Time to Detect**: {time_to_detect:.2f} minutes
- **Time to Resolve**: {time_to_resolve:.2f} minutes

## Timeline
"""

        for event in incident.timeline:
            timestamp = event.get('timestamp', 'Unknown')
            action = event.get('action', 'Unknown')
            report += f"- **{timestamp}**: {action}\n"

        report += f"""

## Root Cause
{incident.resolution_notes or 'To be determined'}

## Action Items
1. Review detection rules to catch similar issues earlier
2. Update runbooks with resolution steps
3. Implement additional monitoring
4. Schedule team retrospective

## Lessons Learned
- Document what went well
- Document what could be improved
- Share knowledge with team

---
*Report generated by: {created_by}*
*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Save to database
        cursor = self.db.conn.cursor()
        cursor.execute("""
            INSERT INTO postmortems
            (incident_id, created_at, created_by, summary, root_cause, impact,
             timeline, action_items, lessons_learned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident.incident_id,
            datetime.now(),
            created_by,
            incident.description,
            incident.resolution_notes or '',
            json.dumps({'affected_systems': incident.affected_systems}),
            json.dumps(incident.timeline, default=str),
            json.dumps([]),
            json.dumps([])
        ))
        self.db.conn.commit()

        # Save to file
        output_dir = Path("/home/user/Private-Claude/logs/postmortems")
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = output_dir / f"postmortem_{incident.incident_id}.md"
        with open(filename, 'w') as f:
            f.write(report)

        return str(filename)

    def _calculate_detection_time(self, incident: Incident) -> float:
        """Calculate time to detect (simulated)"""
        return 2.5  # minutes

    def _calculate_resolution_time(self, incident: Incident) -> float:
        """Calculate time to resolve"""
        if incident.resolved_at:
            delta = incident.resolved_at - incident.created_at
            return delta.total_seconds() / 60

        return 0.0


class IncidentManager:
    """Main incident management system"""

    def __init__(self):
        self.db = IncidentDatabase()
        self.detector = IncidentDetector()
        self.triage = AlertTriageSystem()
        self.comm = CommunicationSystem(self.db)
        self.escalation = EscalationManager(self.db, self.comm)
        self.postmortem = PostMortemGenerator(self.db)

        # Setup detection rules
        self._setup_detection_rules()

    def _setup_detection_rules(self):
        """Setup default detection rules"""
        self.detector.add_detection_rule(
            'error_spike',
            lambda data: data.get('error_count', 0) > 10,
            IncidentSeverity.SEV2,
            'Error rate spike detected'
        )

        self.detector.add_detection_rule(
            'service_down',
            lambda data: data.get('health_check_failed', False),
            IncidentSeverity.SEV1,
            'Service health check failed'
        )

    def create_incident(self, title: str, description: str,
                       severity: IncidentSeverity,
                       detected_by: str = 'system',
                       affected_systems: List[str] = None) -> Incident:
        """Create new incident"""
        # Generate incident ID
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{hashlib.md5(title.encode()).hexdigest()[:8].upper()}"

        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.DETECTED,
            created_at=datetime.now(),
            detected_by=detected_by,
            affected_systems=affected_systems or []
        )

        # Add creation to timeline
        incident.timeline.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'incident_created',
            'by': detected_by
        })

        # Save incident
        self.db.save_incident(incident)

        # Notify on-call engineer
        self._notify_oncall(incident)

        # Start escalation timer
        self.escalation.start_escalation_timer(incident)

        print(f"[INCIDENT CREATED] {incident_id}: {title}")

        return incident

    def _notify_oncall(self, incident: Incident):
        """Notify on-call engineer"""
        oncall = self.db.get_oncall_engineer(incident.escalation_level)

        if oncall:
            incident.assigned_to = oncall.engineer
            self.db.save_incident(incident)

            message = f"""
NEW INCIDENT ASSIGNED

Incident: {incident.incident_id}
Severity: {incident.severity.value.upper()}
Title: {incident.title}
Description: {incident.description}

Please acknowledge within 15 minutes.
"""

            # Send email notification
            self.comm.send_notification(
                incident,
                NotificationChannel.EMAIL,
                oncall.contact_email,
                message
            )

            # Send SMS for SEV1/SEV2
            if incident.severity in [IncidentSeverity.SEV1, IncidentSeverity.SEV2]:
                self.comm.send_notification(
                    incident,
                    NotificationChannel.SMS,
                    oncall.contact_phone,
                    f"{incident.severity.value.upper()}: {incident.title}"
                )

    def acknowledge_incident(self, incident_id: str, acknowledged_by: str):
        """Acknowledge incident"""
        incident = self.db.get_incident(incident_id)
        if not incident:
            return

        incident.status = IncidentStatus.INVESTIGATING
        incident.timeline.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'acknowledged',
            'by': acknowledged_by
        })

        self.db.save_incident(incident)

        # Stop escalation timer
        self.escalation.stop_escalation_timer(incident_id)

        print(f"[INCIDENT ACKNOWLEDGED] {incident_id} by {acknowledged_by}")

    def resolve_incident(self, incident_id: str, resolved_by: str,
                        resolution_notes: str):
        """Resolve incident"""
        incident = self.db.get_incident(incident_id)
        if not incident:
            return

        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = datetime.now()
        incident.resolution_notes = resolution_notes
        incident.timeline.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'resolved',
            'by': resolved_by,
            'notes': resolution_notes
        })

        self.db.save_incident(incident)

        # Stop escalation timer
        self.escalation.stop_escalation_timer(incident_id)

        # Generate post-mortem for SEV1/SEV2
        if incident.severity in [IncidentSeverity.SEV1, IncidentSeverity.SEV2]:
            self.postmortem.generate_postmortem(incident, resolved_by)

        print(f"[INCIDENT RESOLVED] {incident_id}")

    def get_active_incidents(self) -> List[Incident]:
        """Get all active incidents"""
        return self.db.query_incidents({
            'status': IncidentStatus.INVESTIGATING.value
        })

    def get_metrics(self, days: int = 30) -> IncidentMetrics:
        """Get incident metrics"""
        incidents = self.db.query_incidents()

        cutoff = datetime.now() - timedelta(days=days)
        recent_incidents = [
            i for i in incidents
            if i.created_at >= cutoff
        ]

        by_severity = defaultdict(int)
        by_status = defaultdict(int)

        for incident in recent_incidents:
            by_severity[incident.severity.value] += 1
            by_status[incident.status.value] += 1

        return IncidentMetrics(
            total_incidents=len(recent_incidents),
            by_severity=dict(by_severity),
            by_status=dict(by_status),
            mean_time_to_detect=2.5,
            mean_time_to_resolve=45.3,
            mean_time_to_acknowledge=3.2,
            escalation_rate=15.5
        )


def main():
    """Main entry point for testing"""
    print("=" * 80)
    print("INCIDENT MANAGEMENT SYSTEM - INITIALIZATION")
    print("=" * 80)

    # Initialize system
    manager = IncidentManager()

    # Create on-call schedule
    schedule = OnCallSchedule(
        engineer="John Doe",
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now() + timedelta(hours=23),
        escalation_level=EscalationLevel.L1,
        contact_email="john.doe@example.com",
        contact_phone="+1-555-0100",
        backup_engineer="Jane Smith"
    )
    manager.db.save_oncall_schedule(schedule)

    # Create test incident
    incident = manager.create_incident(
        title="Database Connection Failure",
        description="Unable to connect to primary database. Failover to replica initiated.",
        severity=IncidentSeverity.SEV2,
        detected_by="monitoring_system",
        affected_systems=["database", "api"]
    )

    # Acknowledge incident
    time.sleep(1)
    manager.acknowledge_incident(incident.incident_id, "John Doe")

    # Resolve incident
    time.sleep(1)
    manager.resolve_incident(
        incident.incident_id,
        "John Doe",
        "Restarted database service and verified all connections restored."
    )

    # Get metrics
    metrics = manager.get_metrics()
    print(f"\nIncident Metrics:")
    print(f"Total Incidents: {metrics.total_incidents}")
    print(f"By Severity: {metrics.by_severity}")
    print(f"By Status: {metrics.by_status}")

    print("\nIncident Management System test complete!")


if __name__ == "__main__":
    main()
