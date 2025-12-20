"""
Cleo Case Management System
Multi-client, multi-matter legal case management with cross-referencing
Designed for handling 40+ cases per client across multiple estates/generations
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class CleoGas Manager:
    """Core case management engine for legal practice"""

    def __init__(self, db_path="pillar-f-cleo/data/cleo.db"):
        self.db_path = db_path
        self.ensure_database()

    def ensure_database(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                client_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL, -- 'individual', 'estate', 'trust', 'business'
                contact_email TEXT,
                contact_phone TEXT,
                notes TEXT,
                created_date TEXT,
                updated_date TEXT
            )
        ''')

        # Matters (cases) table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matters (
                matter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                caption TEXT NOT NULL,
                jurisdiction TEXT,
                case_number TEXT,
                case_type TEXT,
                status TEXT DEFAULT 'active', -- 'active', 'settled', 'dismissed', 'won', 'lost'
                priority TEXT DEFAULT 'medium', -- 'high', 'medium', 'low'
                total_damages REAL DEFAULT 0.0,
                filing_date TEXT,
                settlement_date TEXT,
                notes TEXT,
                created_date TEXT,
                updated_date TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(client_id)
            )
        ''')

        # Tasks & deadlines table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                matter_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                due_date TEXT,
                status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
                assigned_role INTEGER, -- References Agent 5.0 role number (1-75)
                priority TEXT DEFAULT 'medium',
                notes TEXT,
                created_date TEXT,
                completed_date TEXT,
                FOREIGN KEY (matter_id) REFERENCES matters(matter_id)
            )
        ''')

        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                document_id INTEGER PRIMARY KEY AUTOINCREMENT,
                matter_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                document_type TEXT, -- 'pleading', 'evidence', 'correspondence', 'discovery', 'order'
                file_path TEXT,
                sharepoint_url TEXT,
                created_date TEXT,
                tags TEXT, -- JSON array of tags
                FOREIGN KEY (matter_id) REFERENCES matters(matter_id)
            )
        ''')

        # Calendar events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                matter_id INTEGER NOT NULL,
                event_type TEXT NOT NULL, -- 'hearing', 'deadline', 'reminder', 'trial', 'deposition'
                event_date TEXT NOT NULL,
                description TEXT,
                location TEXT,
                status TEXT DEFAULT 'scheduled', -- 'scheduled', 'completed', 'continued', 'cancelled'
                reminder_sent INTEGER DEFAULT 0,
                created_date TEXT,
                FOREIGN KEY (matter_id) REFERENCES matters(matter_id)
            )
        ''')

        # Cross-references table (for linking related matters)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cross_references (
                reference_id INTEGER PRIMARY KEY AUTOINCREMENT,
                matter_id_1 INTEGER NOT NULL,
                matter_id_2 INTEGER NOT NULL,
                relationship_type TEXT, -- 'related', 'consolidated', 'same_defendant', 'same_incident'
                notes TEXT,
                FOREIGN KEY (matter_id_1) REFERENCES matters(matter_id),
                FOREIGN KEY (matter_id_2) REFERENCES matters(matter_id)
            )
        ''')

        # Timeline events table (for chronology building)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timeline_events (
                timeline_id INTEGER PRIMARY KEY AUTOINCREMENT,
                matter_id INTEGER NOT NULL,
                event_date TEXT NOT NULL,
                event_description TEXT NOT NULL,
                event_type TEXT, -- 'incident', 'discovery', 'filing', 'communication'
                source_document_id INTEGER,
                witnesses TEXT, -- JSON array
                evidence_refs TEXT, -- JSON array of document_ids
                created_date TEXT,
                FOREIGN KEY (matter_id) REFERENCES matters(matter_id),
                FOREIGN KEY (source_document_id) REFERENCES documents(document_id)
            )
        ''')

        conn.commit()
        conn.close()

        print("✅ Cleo database initialized")

    def add_client(self, name: str, client_type: str, email: str = None,
                   phone: str = None, notes: str = None) -> int:
        """
        Add a new client to the system

        Args:
            name: Client full name or entity name
            client_type: 'individual', 'estate', 'trust', or 'business'
            email: Contact email
            phone: Contact phone
            notes: Additional notes

        Returns:
            client_id of newly created client
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO clients (name, type, contact_email, contact_phone, notes, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, client_type, email, phone, notes, now, now))

        client_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"✅ Added client: {name} (ID: {client_id})")
        return client_id

    def add_matter(self, client_id: int, caption: str, case_type: str = None,
                   jurisdiction: str = None, priority: str = "medium",
                   total_damages: float = 0.0, notes: str = None) -> int:
        """
        Add a new matter (case) for a client

        Args:
            client_id: ID of client this matter belongs to
            caption: Case caption (e.g., "Smith v. Jones")
            case_type: Type of case ('civil', 'probate', 'criminal', etc.)
            jurisdiction: Court jurisdiction
            priority: 'high', 'medium', or 'low'
            total_damages: Estimated total damages
            notes: Case notes

        Returns:
            matter_id of newly created matter
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO matters (client_id, caption, case_type, jurisdiction, priority,
                                total_damages, notes, created_date, updated_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        ''', (client_id, caption, case_type, jurisdiction, priority, total_damages, notes, now, now))

        matter_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"✅ Added matter: {caption} (ID: {matter_id})")
        return matter_id

    def add_task(self, matter_id: int, description: str, due_date: str = None,
                 assigned_role: int = None, priority: str = "medium") -> int:
        """
        Add a task/deadline to a matter

        Args:
            matter_id: Matter this task belongs to
            description: Task description
            due_date: Due date (YYYY-MM-DD format)
            assigned_role: Agent 5.0 role number (1-75) or None
            priority: 'high', 'medium', or 'low'

        Returns:
            task_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO tasks (matter_id, description, due_date, assigned_role, priority,
                              status, created_date)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        ''', (matter_id, description, due_date, assigned_role, priority, now))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"✅ Added task: {description[:50]}... (ID: {task_id})")
        return task_id

    def add_document(self, matter_id: int, title: str, document_type: str = None,
                     file_path: str = None, sharepoint_url: str = None,
                     tags: List[str] = None) -> int:
        """
        Add a document to a matter

        Args:
            matter_id: Matter this document belongs to
            title: Document title
            document_type: Type ('pleading', 'evidence', 'correspondence', etc.)
            file_path: Local file path
            sharepoint_url: SharePoint URL if applicable
            tags: List of tags for search/categorization

        Returns:
            document_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        tags_json = json.dumps(tags) if tags else None

        cursor.execute('''
            INSERT INTO documents (matter_id, title, document_type, file_path, sharepoint_url,
                                  tags, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (matter_id, title, document_type, file_path, sharepoint_url, tags_json, now))

        document_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"✅ Added document: {title} (ID: {document_id})")
        return document_id

    def add_calendar_event(self, matter_id: int, event_type: str, event_date: str,
                          description: str, location: str = None) -> int:
        """
        Add calendar event (hearing, deadline, etc.)

        Args:
            matter_id: Matter this event belongs to
            event_type: 'hearing', 'deadline', 'reminder', 'trial', 'deposition'
            event_date: Event date (YYYY-MM-DD format)
            description: Event description
            location: Event location

        Returns:
            event_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO calendar_events (matter_id, event_type, event_date, description,
                                        location, created_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'scheduled')
        ''', (matter_id, event_type, event_date, description, location, now))

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"✅ Added calendar event: {description} on {event_date}")
        return event_id

    def link_matters(self, matter_id_1: int, matter_id_2: int,
                    relationship_type: str, notes: str = None):
        """Link two related matters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO cross_references (matter_id_1, matter_id_2, relationship_type, notes)
            VALUES (?, ?, ?, ?)
        ''', (matter_id_1, matter_id_2, relationship_type, notes))

        conn.commit()
        conn.close()

        print(f"✅ Linked matters {matter_id_1} <-> {matter_id_2} ({relationship_type})")

    def add_timeline_event(self, matter_id: int, event_date: str,
                          event_description: str, event_type: str = None,
                          source_document_id: int = None) -> int:
        """
        Add an event to the master timeline for a matter

        Args:
            matter_id: Matter ID
            event_date: Date of event (YYYY-MM-DD)
            event_description: What happened
            event_type: Category of event
            source_document_id: Document that proves this event

        Returns:
            timeline_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO timeline_events (matter_id, event_date, event_description, event_type,
                                        source_document_id, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (matter_id, event_date, event_description, event_type, source_document_id, now))

        timeline_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return timeline_id

    def get_client_matters(self, client_id: int) -> List[Dict[str, Any]]:
        """Get all matters for a client"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM matters WHERE client_id = ? ORDER BY priority DESC, created_date DESC
        ''', (client_id,))

        matters = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return matters

    def get_matter_timeline(self, matter_id: int) -> List[Dict[str, Any]]:
        """Get chronological timeline for a matter"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM timeline_events
            WHERE matter_id = ?
            ORDER BY event_date ASC
        ''', (matter_id,))

        timeline = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return timeline

    def get_upcoming_deadlines(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get all upcoming deadlines across all matters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cutoff_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

        cursor.execute('''
            SELECT t.*, m.caption, m.case_number, c.name as client_name
            FROM tasks t
            JOIN matters m ON t.matter_id = m.matter_id
            JOIN clients c ON m.client_id = c.client_id
            WHERE t.due_date <= ? AND t.status != 'completed'
            ORDER BY t.due_date ASC
        ''', (cutoff_date,))

        deadlines = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return deadlines

    def generate_case_summary(self, matter_id: int) -> str:
        """Generate comprehensive case summary"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get matter info
        cursor.execute('SELECT * FROM matters WHERE matter_id = ?', (matter_id,))
        matter = dict(cursor.fetchone())

        # Get client info
        cursor.execute('SELECT * FROM clients WHERE client_id = ?', (matter['client_id'],))
        client = dict(cursor.fetchone())

        # Get tasks
        cursor.execute('SELECT * FROM tasks WHERE matter_id = ?', (matter_id,))
        tasks = [dict(row) for row in cursor.fetchall()]

        # Get documents
        cursor.execute('SELECT * FROM documents WHERE matter_id = ?', (matter_id,))
        documents = [dict(row) for row in cursor.fetchall()]

        # Get calendar events
        cursor.execute('SELECT * FROM calendar_events WHERE matter_id = ?', (matter_id,))
        events = [dict(row) for row in cursor.fetchall()]

        conn.close()

        # Generate summary
        summary = f"""# CASE SUMMARY
## {matter['caption']}

---

### Client Information

**Client:** {client['name']} ({client['type']})
**Contact:** {client.get('contact_email', 'N/A')} | {client.get('contact_phone', 'N/A')}

---

### Matter Details

**Case Number:** {matter.get('case_number', 'Not yet filed')}
**Jurisdiction:** {matter['jurisdiction']}
**Case Type:** {matter['case_type']}
**Status:** {matter['status'].upper()}
**Priority:** {matter['priority'].upper()}
**Total Damages:** ${matter['total_damages']:,.2f}
**Filing Date:** {matter.get('filing_date', 'Not yet filed')}

---

### Tasks & Deadlines ({len(tasks)} total)

"""

        for task in tasks:
            summary += f"- **[{task['status'].upper()}]** {task['description']} (Due: {task.get('due_date', 'No deadline')})\n"

        summary += f"""

---

### Documents ({len(documents)} total)

"""

        for doc in documents:
            summary += f"- **{doc['title']}** ({doc['document_type']}) - {doc.get('file_path', 'No path')}\n"

        summary += f"""

---

### Calendar ({len(events)} events)

"""

        for event in events:
            summary += f"- **{event['event_date']}** - {event['event_type'].upper()}: {event['description']}\n"

        summary += f"""

---

**Summary Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

"""

        return summary

    def import_40_cases_from_json(self, json_path="legal-forensics/master_case_list.json"):
        """
        Import the 40 existing cases from master_case_list.json

        Returns:
            Dictionary mapping case numbers to matter_ids
        """
        # Load JSON
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Get or create client for Thurman Robinson Jr.
        client_id = self.add_client(
            name="Thurman Malik Robinson Jr. & APPS Holdings WY Inc.",
            client_type="individual",
            email="appsefilepro@gmail.com",
            notes="Primary plaintiff in 40 civil litigation matters"
        )

        case_mapping = {}

        for case in data['master_case_list']:
            matter_id = self.add_matter(
                client_id=client_id,
                caption=case['caption'],
                case_type=' '.join(case.get('claims', [])),
                jurisdiction=case.get('jurisdiction', 'Unknown'),
                priority=case['priority'].lower(),
                total_damages=0.0,  # To be determined
                notes=f"Keywords: {', '.join(case.get('keywords', []))}\nIncident Date: {case.get('incident_date', 'Unknown')}"
            )

            case_mapping[case['number']] = matter_id

        print(f"\n✅ Imported {len(case_mapping)} cases into Cleo")
        return case_mapping


# Example usage and test
if __name__ == "__main__":
    # Initialize system
    cleo = CleoGasManager()

    # Import 40 existing cases
    print("\n=== Importing 40 Cases ===")
    case_mapping = cleo.import_40_cases_from_json()

    # Add example estate clients
    print("\n=== Adding Estate Clients ===")

    estate_thurman_sr = cleo.add_client(
        name="Estate of Thurman Earl Robinson Sr.",
        client_type="estate",
        notes="Probate administration with elder abuse allegations"
    )

    estate_rosetta = cleo.add_client(
        name="Estate of Rosetta Burnett Stuckey",
        client_type="estate",
        notes="Missing assets investigation"
    )

    estate_grover = cleo.add_client(
        name="Estate of Grover Burnett Singer",
        client_type="estate",
        notes="22 missing properties - 22 LLC defendants"
    )

    # Add probate matter for Thurman Sr.
    probate_matter = cleo.add_matter(
        client_id=estate_thurman_sr,
        caption="Estate of Thurman Earl Robinson Sr.",
        case_type="Probate Administration",
        jurisdiction="Los Angeles County Superior Court - Probate Division",
        priority="high",
        total_damages=500000.0,
        notes="Elder abuse by surviving spouse Fatimah Calvin Moore"
    )

    # Add tasks
    cleo.add_task(
        matter_id=probate_matter,
        description="File Petition for Probate (DE-111)",
        due_date=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        assigned_role=2,  # Probate Administrator role
        priority="high"
    )

    cleo.add_task(
        matter_id=probate_matter,
        description="Serve Notice of Petition on all heirs and beneficiaries",
        due_date=(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
        assigned_role=12,  # Court Filing Manager
        priority="high"
    )

    # Add calendar event
    cleo.add_calendar_event(
        matter_id=probate_matter,
        event_type="hearing",
        event_date=(datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d'),
        description="Probate Petition Hearing",
        location="Stanley Mosk Courthouse, Probate Department"
    )

    # Get upcoming deadlines
    print("\n=== Upcoming Deadlines (Next 30 Days) ===")
    deadlines = cleo.get_upcoming_deadlines(days_ahead=30)
    for deadline in deadlines[:5]:  # Show first 5
        print(f"- {deadline['due_date']}: {deadline['description']} ({deadline['caption']})")

    # Generate case summary
    print("\n=== Case Summary for Probate Matter ===")
    summary = cleo.generate_case_summary(probate_matter)
    print(summary[:500] + "...")

    print("\n✅ Cleo Case Management System Test Complete")
    print(f"Total clients: {estate_thurman_sr + 2}")  # Rough count
    print(f"Total matters: {len(case_mapping) + 1}")
