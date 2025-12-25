#!/usr/bin/env python3
"""
PILLAR 2: LEGAL OPERATIONS
Complete legal automation including document management, case tracking, compliance, and contracts
Part of Agent 5.0 CFO Suite
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import sqlite3


class CaseStatus(Enum):
    """Case status"""
    ACTIVE = "active"
    PENDING = "pending"
    DISMISSED = "dismissed"
    CLOSED = "closed"
    APPEALED = "appealed"


class DocumentType(Enum):
    """Legal document types"""
    CONTRACT = "contract"
    MOTION = "motion"
    BRIEF = "brief"
    AFFIDAVIT = "affidavit"
    NOTICE = "notice"
    PLEADING = "pleading"
    DISCOVERY = "discovery"
    SETTLEMENT = "settlement"


class ComplianceStatus(Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REMEDIATION_REQUIRED = "remediation_required"


@dataclass
class LegalCase:
    """Legal case record"""
    id: str
    case_number: str
    case_name: str
    court: str
    case_type: str
    plaintiff: str
    defendant: str
    status: str
    filed_date: str
    next_hearing: Optional[str] = None
    assigned_attorney: Optional[str] = None
    estimated_value: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class LegalDocument:
    """Legal document record"""
    id: str
    case_id: str
    document_type: str
    title: str
    file_path: str
    created_date: str
    due_date: Optional[str] = None
    signed: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Contract:
    """Contract record"""
    id: str
    contract_name: str
    parties: List[str]
    contract_type: str
    start_date: str
    end_date: str
    value: float
    status: str
    renewal_date: Optional[str] = None
    auto_renew: bool = False
    terms: Optional[Dict[str, Any]] = None


@dataclass
class ComplianceCheck:
    """Compliance check record"""
    id: str
    regulation: str
    check_name: str
    frequency: str  # daily, weekly, monthly, quarterly, annual
    last_check: str
    next_check: str
    status: str
    findings: Optional[str] = None
    remediation_plan: Optional[str] = None


class LegalOperations:
    """
    Complete legal operations management system
    Handles case management, document automation, compliance tracking, and contracts
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize legal operations"""
        if data_dir is None:
            self.base_dir = Path(__file__).parent
            self.data_dir = self.base_dir / 'data' / 'legal'
        else:
            self.data_dir = data_dir

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = self.base_dir / 'logs' / 'legal'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir = self.data_dir / 'documents'
        self.documents_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        self.logger = logging.getLogger('LegalOps')
        handler = logging.FileHandler(
            self.logs_dir / f'legal_{datetime.now().strftime("%Y%m%d")}.log'
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Initialize database
        self.db_path = self.data_dir / 'legal.db'
        self.init_database()

        # Compliance regulations tracking
        self.regulations = {
            'GDPR': 'General Data Protection Regulation',
            'HIPAA': 'Health Insurance Portability and Accountability Act',
            'SOX': 'Sarbanes-Oxley Act',
            'PCI_DSS': 'Payment Card Industry Data Security Standard',
            'CCPA': 'California Consumer Privacy Act',
            'SOC2': 'Service Organization Control 2'
        }

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                case_number TEXT UNIQUE NOT NULL,
                case_name TEXT NOT NULL,
                court TEXT NOT NULL,
                case_type TEXT NOT NULL,
                plaintiff TEXT NOT NULL,
                defendant TEXT NOT NULL,
                status TEXT NOT NULL,
                filed_date TEXT NOT NULL,
                next_hearing TEXT,
                assigned_attorney TEXT,
                estimated_value REAL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_date TEXT NOT NULL,
                due_date TEXT,
                signed INTEGER DEFAULT 0,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')

        # Contracts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id TEXT PRIMARY KEY,
                contract_name TEXT NOT NULL,
                parties TEXT NOT NULL,
                contract_type TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                value REAL NOT NULL,
                status TEXT NOT NULL,
                renewal_date TEXT,
                auto_renew INTEGER DEFAULT 0,
                terms TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Compliance checks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_checks (
                id TEXT PRIMARY KEY,
                regulation TEXT NOT NULL,
                check_name TEXT NOT NULL,
                frequency TEXT NOT NULL,
                last_check TEXT NOT NULL,
                next_check TEXT NOT NULL,
                status TEXT NOT NULL,
                findings TEXT,
                remediation_plan TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        self.logger.info("Legal database initialized successfully")

    # ==================== CASE MANAGEMENT ====================

    def create_case(self, case: LegalCase) -> str:
        """Create a new legal case"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO cases
            (id, case_number, case_name, court, case_type, plaintiff, defendant,
             status, filed_date, next_hearing, assigned_attorney, estimated_value, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case.id,
            case.case_number,
            case.case_name,
            case.court,
            case.case_type,
            case.plaintiff,
            case.defendant,
            case.status,
            case.filed_date,
            case.next_hearing,
            case.assigned_attorney,
            case.estimated_value,
            case.notes
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Case created: {case.case_number} - {case.case_name}")
        return case.id

    def update_case_status(self, case_id: str, status: CaseStatus, notes: Optional[str] = None) -> bool:
        """Update case status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if notes:
            cursor.execute(
                "UPDATE cases SET status = ?, notes = ? WHERE id = ?",
                (status.value, notes, case_id)
            )
        else:
            cursor.execute(
                "UPDATE cases SET status = ? WHERE id = ?",
                (status.value, case_id)
            )

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        if updated:
            self.logger.info(f"Case {case_id} status updated to {status.value}")

        return updated

    def get_active_cases(self) -> List[LegalCase]:
        """Get all active cases"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cases WHERE status = 'active' ORDER BY next_hearing")
        rows = cursor.fetchall()
        conn.close()

        cases = []
        for row in rows:
            cases.append(LegalCase(
                id=row[0],
                case_number=row[1],
                case_name=row[2],
                court=row[3],
                case_type=row[4],
                plaintiff=row[5],
                defendant=row[6],
                status=row[7],
                filed_date=row[8],
                next_hearing=row[9],
                assigned_attorney=row[10],
                estimated_value=row[11],
                notes=row[12]
            ))

        return cases

    def get_upcoming_hearings(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming court hearings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        end_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

        cursor.execute('''
            SELECT case_number, case_name, court, next_hearing
            FROM cases
            WHERE next_hearing IS NOT NULL
            AND next_hearing <= ?
            AND status IN ('active', 'pending')
            ORDER BY next_hearing
        ''', (end_date,))

        rows = cursor.fetchall()
        conn.close()

        hearings = []
        for row in rows:
            hearings.append({
                'case_number': row[0],
                'case_name': row[1],
                'court': row[2],
                'hearing_date': row[3]
            })

        return hearings

    # ==================== DOCUMENT MANAGEMENT ====================

    def add_document(self, document: LegalDocument) -> str:
        """Add a legal document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO documents
            (id, case_id, document_type, title, file_path, created_date,
             due_date, signed, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            document.id,
            document.case_id,
            document.document_type,
            document.title,
            document.file_path,
            document.created_date,
            document.due_date,
            1 if document.signed else 0,
            json.dumps(document.metadata) if document.metadata else None
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Document added: {document.title} for case {document.case_id}")
        return document.id

    def get_case_documents(self, case_id: str) -> List[LegalDocument]:
        """Get all documents for a case"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM documents WHERE case_id = ? ORDER BY created_date DESC",
            (case_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        documents = []
        for row in rows:
            documents.append(LegalDocument(
                id=row[0],
                case_id=row[1],
                document_type=row[2],
                title=row[3],
                file_path=row[4],
                created_date=row[5],
                due_date=row[6],
                signed=bool(row[7]),
                metadata=json.loads(row[8]) if row[8] else None
            ))

        return documents

    # ==================== CONTRACT MANAGEMENT ====================

    def create_contract(self, contract: Contract) -> str:
        """Create a new contract"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO contracts
            (id, contract_name, parties, contract_type, start_date, end_date,
             value, status, renewal_date, auto_renew, terms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contract.id,
            contract.contract_name,
            json.dumps(contract.parties),
            contract.contract_type,
            contract.start_date,
            contract.end_date,
            contract.value,
            contract.status,
            contract.renewal_date,
            1 if contract.auto_renew else 0,
            json.dumps(contract.terms) if contract.terms else None
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Contract created: {contract.contract_name} - ${contract.value}")
        return contract.id

    def get_expiring_contracts(self, days_ahead: int = 60) -> List[Contract]:
        """Get contracts expiring soon"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        end_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

        cursor.execute('''
            SELECT * FROM contracts
            WHERE end_date <= ?
            AND status = 'active'
            ORDER BY end_date
        ''', (end_date,))

        rows = cursor.fetchall()
        conn.close()

        contracts = []
        for row in rows:
            contracts.append(Contract(
                id=row[0],
                contract_name=row[1],
                parties=json.loads(row[2]),
                contract_type=row[3],
                start_date=row[4],
                end_date=row[5],
                value=row[6],
                status=row[7],
                renewal_date=row[8],
                auto_renew=bool(row[9]),
                terms=json.loads(row[10]) if row[10] else None
            ))

        return contracts

    # ==================== COMPLIANCE TRACKING ====================

    def create_compliance_check(self, check: ComplianceCheck) -> str:
        """Create a compliance check"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO compliance_checks
            (id, regulation, check_name, frequency, last_check, next_check,
             status, findings, remediation_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            check.id,
            check.regulation,
            check.check_name,
            check.frequency,
            check.last_check,
            check.next_check,
            check.status,
            check.findings,
            check.remediation_plan
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Compliance check created: {check.regulation} - {check.check_name}")
        return check.id

    def get_due_compliance_checks(self) -> List[ComplianceCheck]:
        """Get compliance checks that are due"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')

        cursor.execute(
            "SELECT * FROM compliance_checks WHERE next_check <= ? ORDER BY next_check",
            (today,)
        )

        rows = cursor.fetchall()
        conn.close()

        checks = []
        for row in rows:
            checks.append(ComplianceCheck(
                id=row[0],
                regulation=row[1],
                check_name=row[2],
                frequency=row[3],
                last_check=row[4],
                next_check=row[5],
                status=row[6],
                findings=row[7],
                remediation_plan=row[8]
            ))

        return checks

    def update_compliance_status(self, check_id: str, status: ComplianceStatus,
                                 findings: Optional[str] = None) -> bool:
        """Update compliance check status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE compliance_checks SET status = ?, findings = ?, last_check = ? WHERE id = ?",
            (status.value, findings, datetime.now().strftime('%Y-%m-%d'), check_id)
        )

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        if updated:
            self.logger.info(f"Compliance check {check_id} updated to {status.value}")

        return updated

    # ==================== REPORTING ====================

    def generate_case_summary(self) -> Dict[str, Any]:
        """Generate summary of all cases"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count by status
        cursor.execute('''
            SELECT status, COUNT(*) FROM cases GROUP BY status
        ''')
        status_counts = dict(cursor.fetchall())

        # Total estimated value
        cursor.execute('''
            SELECT SUM(estimated_value) FROM cases WHERE status = 'active'
        ''')
        total_value = cursor.fetchone()[0] or 0

        # Count by case type
        cursor.execute('''
            SELECT case_type, COUNT(*) FROM cases GROUP BY case_type
        ''')
        type_counts = dict(cursor.fetchall())

        conn.close()

        return {
            'report_type': 'case_summary',
            'status_breakdown': status_counts,
            'total_active_value': total_value,
            'type_breakdown': type_counts,
            'generated_at': datetime.now().isoformat()
        }

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance status report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count by regulation
        cursor.execute('''
            SELECT regulation, COUNT(*) FROM compliance_checks GROUP BY regulation
        ''')
        regulation_counts = dict(cursor.fetchall())

        # Count by status
        cursor.execute('''
            SELECT status, COUNT(*) FROM compliance_checks GROUP BY status
        ''')
        status_counts = dict(cursor.fetchall())

        # Get non-compliant items
        cursor.execute('''
            SELECT regulation, check_name, findings
            FROM compliance_checks
            WHERE status IN ('non_compliant', 'remediation_required')
        ''')
        non_compliant = cursor.fetchall()

        conn.close()

        return {
            'report_type': 'compliance_report',
            'regulation_breakdown': regulation_counts,
            'status_breakdown': status_counts,
            'non_compliant_items': [
                {'regulation': r, 'check': c, 'findings': f}
                for r, c, f in non_compliant
            ],
            'generated_at': datetime.now().isoformat()
        }


def main():
    """Demo and testing"""
    print("\n" + "="*70)
    print("PILLAR 2: LEGAL OPERATIONS")
    print("="*70 + "\n")

    legal_ops = LegalOperations()

    # Demo: Create sample case
    sample_case = LegalCase(
        id=f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        case_number="2024-CV-12345",
        case_name="Smith v. Jones Corporation",
        court="District Court, Southern District",
        case_type="contract_dispute",
        plaintiff="John Smith",
        defendant="Jones Corporation",
        status=CaseStatus.ACTIVE.value,
        filed_date=datetime.now().strftime('%Y-%m-%d'),
        next_hearing=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        assigned_attorney="Attorney J. Williams",
        estimated_value=250000.00
    )
    case_id = legal_ops.create_case(sample_case)
    print(f"Sample case created: {sample_case.case_number}")

    # Demo: Create compliance check
    sample_compliance = ComplianceCheck(
        id=f"COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        regulation="GDPR",
        check_name="Data Privacy Audit",
        frequency="quarterly",
        last_check=datetime.now().strftime('%Y-%m-%d'),
        next_check=(datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
        status=ComplianceStatus.COMPLIANT.value
    )
    comp_id = legal_ops.create_compliance_check(sample_compliance)
    print(f"Compliance check created: {sample_compliance.check_name}")

    # Generate reports
    print("\n" + "-"*70)
    print("LEGAL REPORTS")
    print("-"*70)

    case_summary = legal_ops.generate_case_summary()
    print(f"\nCase Summary:")
    print(f"  Status Breakdown: {case_summary['status_breakdown']}")
    print(f"  Total Active Value: ${case_summary['total_active_value']:,.2f}")

    compliance_report = legal_ops.generate_compliance_report()
    print(f"\nCompliance Report:")
    print(f"  Status Breakdown: {compliance_report['status_breakdown']}")
    print(f"  Non-Compliant Items: {len(compliance_report['non_compliant_items'])}")

    print("\n" + "="*70)
    print("Legal Operations Module Ready")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
