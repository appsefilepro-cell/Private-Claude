"""
Probate Workflow Orchestration System
Orchestrates the complete probate process including document generation,
deadline tracking, and SharePoint integration for document storage.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import uuid
from typing import Dict, List, Optional, Tuple
from enum import Enum
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pillar_b_legal.probate.probate_automation import (
    Estate, ProbateStatus, AssetType, CreditorType,
    EstateInventoryManager, CreditorClaimManager, DistributionCalculator,
    ProbateFormGenerator, ProbateWorkflowManager
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeadlineType(Enum):
    """Types of probate deadlines"""
    FILING = "filing"
    HEARING = "hearing"
    INVENTORY = "inventory"
    CREDITOR_CLAIM = "creditor_claim"
    FINAL_ACCOUNT = "final_account"
    DISTRIBUTION = "distribution"
    CLOSURE = "closure"


class DocumentType(Enum):
    """Types of probate documents"""
    PETITION = "petition"
    NOTICE_CREDITORS = "notice_creditors"
    INVENTORY = "inventory"
    FINAL_ACCOUNT = "final_account"
    DISTRIBUTION = "distribution"
    ORDER = "order"
    OTHER = "other"


class DocumentStatus(Enum):
    """Status of documents in workflow"""
    DRAFT = "draft"
    GENERATED = "generated"
    REVIEWED = "reviewed"
    FILED = "filed"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ProbateDeadline:
    """Represents a probate deadline with tracking"""

    def __init__(
        self,
        deadline_type: DeadlineType,
        description: str,
        due_date: datetime,
        days_before_warning: int = 7
    ):
        self.id = str(uuid.uuid4())
        self.deadline_type = deadline_type
        self.description = description
        self.due_date = due_date
        self.days_before_warning = days_before_warning
        self.completed = False
        self.completed_date: Optional[datetime] = None
        self.notes = ""

    def is_overdue(self) -> bool:
        """Check if deadline is overdue"""
        return datetime.now() > self.due_date and not self.completed

    def is_warning(self) -> bool:
        """Check if within warning period"""
        days_until = (self.due_date - datetime.now()).days
        return 0 < days_until <= self.days_before_warning and not self.completed

    def mark_completed(self):
        """Mark deadline as completed"""
        self.completed = True
        self.completed_date = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type': self.deadline_type.value,
            'description': self.description,
            'due_date': self.due_date.isoformat(),
            'completed': self.completed,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'status': 'overdue' if self.is_overdue() else 'warning' if self.is_warning() else 'on_track',
            'notes': self.notes
        }


class WorkflowDocument:
    """Represents a document in the probate workflow"""

    def __init__(
        self,
        document_type: DocumentType,
        title: str,
        template_path: Optional[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.document_type = document_type
        self.title = title
        self.template_path = template_path
        self.status = DocumentStatus.DRAFT
        self.created_date = datetime.now()
        self.modified_date = datetime.now()
        self.content: Optional[Dict] = None
        self.file_path: Optional[str] = None
        self.sharepoint_url: Optional[str] = None
        self.reviewed_by: Optional[str] = None
        self.review_date: Optional[datetime] = None
        self.filed_date: Optional[datetime] = None
        self.published_date: Optional[datetime] = None
        self.version = "1.0"
        self.notes = ""

    def update_status(self, new_status: DocumentStatus):
        """Update document status"""
        self.status = new_status
        self.modified_date = datetime.now()

        if new_status == DocumentStatus.FILED:
            self.filed_date = datetime.now()
        elif new_status == DocumentStatus.PUBLISHED:
            self.published_date = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type': self.document_type.value,
            'title': self.title,
            'status': self.status.value,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'file_path': self.file_path,
            'sharepoint_url': self.sharepoint_url,
            'reviewed_by': self.reviewed_by,
            'version': self.version
        }


class SharePointIntegration:
    """Handles SharePoint document storage integration"""

    def __init__(self, site_url: str, client_id: str, client_secret: str):
        self.site_url = site_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.connected = False
        logger.info(f"SharePoint Integration initialized for {site_url}")

    def connect(self) -> bool:
        """Establish connection to SharePoint"""
        # In a real implementation, this would authenticate with Azure AD
        self.connected = True
        logger.info("Connected to SharePoint")
        return True

    def upload_document(self, estate_id: str, document: WorkflowDocument, file_content: str) -> bool:
        """Upload document to SharePoint"""
        if not self.connected:
            logger.error("Not connected to SharePoint")
            return False

        # In a real implementation, this would upload to SharePoint library
        folder_path = f"/Estates/{estate_id}/{document.document_type.value}"
        file_name = f"{document.id}_{document.title}.pdf"

        # Simulated SharePoint URL
        document.sharepoint_url = f"{self.site_url}{folder_path}/{file_name}"

        logger.info(f"Uploaded document to SharePoint: {document.sharepoint_url}")
        return True

    def create_folder_structure(self, estate_id: str, estate_name: str) -> Dict:
        """Create folder structure for estate documents"""
        if not self.connected:
            logger.error("Not connected to SharePoint")
            return {}

        folders = {
            'root': f"/Estates/{estate_id}_{estate_name}",
            'petitions': f"/Estates/{estate_id}_{estate_name}/1_Petitions",
            'notices': f"/Estates/{estate_id}_{estate_name}/2_Notices",
            'inventory': f"/Estates/{estate_id}_{estate_name}/3_Inventory",
            'accounts': f"/Estates/{estate_id}_{estate_name}/4_Final_Accounts",
            'distributions': f"/Estates/{estate_id}_{estate_name}/5_Distributions",
            'court_orders': f"/Estates/{estate_id}_{estate_name}/6_Court_Orders",
            'supporting': f"/Estates/{estate_id}_{estate_name}/7_Supporting_Documents"
        }

        logger.info(f"Created SharePoint folder structure for estate {estate_id}")
        return folders

    def get_document_url(self, estate_id: str, document_id: str) -> str:
        """Get document URL from SharePoint"""
        return f"{self.site_url}/Estates/{estate_id}/{document_id}"


class ProbateWorkflowOrchestrator:
    """Orchestrates the complete probate workflow"""

    def __init__(
        self,
        estate: Estate,
        config: Dict,
        sharepoint_config: Optional[Dict] = None
    ):
        self.estate = estate
        self.config = config
        self.workflow_mgr = ProbateWorkflowManager(estate, config)
        self.deadlines: Dict[str, ProbateDeadline] = {}
        self.documents: Dict[str, WorkflowDocument] = {}
        self.sharepoint: Optional[SharePointIntegration] = None

        if sharepoint_config:
            self.sharepoint = SharePointIntegration(
                site_url=sharepoint_config.get('site_url'),
                client_id=sharepoint_config.get('client_id'),
                client_secret=sharepoint_config.get('client_secret')
            )

        self._initialize_deadlines()
        logger.info(f"Probate Workflow Orchestrator initialized for estate {estate.id}")

    def _initialize_deadlines(self):
        """Initialize deadlines based on estate and config"""
        death_date = datetime.fromisoformat(self.estate.date_of_death)
        state_config = self.config['state_rules'].get(
            self.estate.state.lower(),
            self.config['state_rules']['default']
        )

        # Create deadlines based on state rules
        deadlines = [
            {
                'type': DeadlineType.FILING,
                'description': 'File petition for probate',
                'days_offset': 14
            },
            {
                'type': DeadlineType.HEARING,
                'description': 'Probate hearing',
                'days_offset': 44
            },
            {
                'type': DeadlineType.INVENTORY,
                'description': f"File inventory and appraisal",
                'days_offset': state_config.get('inventory_due_days', 90)
            },
            {
                'type': DeadlineType.CREDITOR_CLAIM,
                'description': 'Creditor claim deadline',
                'days_offset': state_config.get('creditor_claim_period_days', 120)
            },
            {
                'type': DeadlineType.FINAL_ACCOUNT,
                'description': 'File final account and report',
                'days_offset': state_config.get('creditor_claim_period_days', 120) + 60
            },
            {
                'type': DeadlineType.DISTRIBUTION,
                'description': 'Complete distributions to beneficiaries',
                'days_offset': state_config.get('creditor_claim_period_days', 120) + 90
            },
            {
                'type': DeadlineType.CLOSURE,
                'description': 'Close estate administration',
                'days_offset': state_config.get('creditor_claim_period_days', 120) + 100
            }
        ]

        for deadline_info in deadlines:
            due_date = death_date + timedelta(days=deadline_info['days_offset'])
            deadline = ProbateDeadline(
                deadline_type=deadline_info['type'],
                description=deadline_info['description'],
                due_date=due_date
            )
            self.deadlines[deadline.id] = deadline

    def initialize_sharepoint(self) -> bool:
        """Initialize SharePoint connection and folder structure"""
        if not self.sharepoint:
            logger.warning("SharePoint not configured")
            return False

        if not self.sharepoint.connect():
            logger.error("Failed to connect to SharePoint")
            return False

        folders = self.sharepoint.create_folder_structure(
            self.estate.id,
            self.estate.decedent_name
        )
        logger.info(f"SharePoint initialized with folder structure: {folders}")
        return True

    def generate_petition_document(self) -> bool:
        """Generate petition for probate document"""
        logger.info("Generating petition for probate...")

        form_gen = ProbateFormGenerator(self.estate, self.config)
        petition_data = form_gen.generate_petition_for_probate()

        doc = WorkflowDocument(
            document_type=DocumentType.PETITION,
            title="Petition for Probate",
            template_path="petition_for_probate.txt"
        )
        doc.content = petition_data
        doc.update_status(DocumentStatus.GENERATED)

        self.documents[doc.id] = doc

        if self.sharepoint:
            petition_text = self._render_petition_template(petition_data)
            self.sharepoint.upload_document(self.estate.id, doc, petition_text)

        logger.info(f"Petition generated: {doc.id}")
        return True

    def generate_notice_to_creditors(self) -> bool:
        """Generate notice to creditors document"""
        logger.info("Generating notice to creditors...")

        form_gen = ProbateFormGenerator(self.estate, self.config)
        notice_data = form_gen.generate_notice_to_creditors()

        doc = WorkflowDocument(
            document_type=DocumentType.NOTICE_CREDITORS,
            title="Notice to Creditors",
            template_path="notice_to_creditors.txt"
        )
        doc.content = notice_data
        doc.update_status(DocumentStatus.GENERATED)

        self.documents[doc.id] = doc

        if self.sharepoint:
            notice_text = self._render_notice_template(notice_data)
            self.sharepoint.upload_document(self.estate.id, doc, notice_text)

        logger.info(f"Notice to creditors generated: {doc.id}")
        return True

    def generate_inventory_document(self) -> bool:
        """Generate inventory and appraisal document"""
        logger.info("Generating inventory and appraisal...")

        form_gen = ProbateFormGenerator(self.estate, self.config)
        inventory_data = form_gen.generate_inventory_and_appraisal()

        doc = WorkflowDocument(
            document_type=DocumentType.INVENTORY,
            title="Inventory and Appraisal",
            template_path="inventory_and_appraisal.txt"
        )
        doc.content = inventory_data
        doc.update_status(DocumentStatus.GENERATED)

        self.documents[doc.id] = doc

        if self.sharepoint:
            inventory_text = self._render_inventory_template(inventory_data)
            self.sharepoint.upload_document(self.estate.id, doc, inventory_text)

        logger.info(f"Inventory and appraisal generated: {doc.id}")
        return True

    def generate_final_account_document(self) -> bool:
        """Generate final account and report document"""
        logger.info("Generating final account and report...")

        form_gen = ProbateFormGenerator(self.estate, self.config)
        final_data = form_gen.generate_final_account_and_report()

        doc = WorkflowDocument(
            document_type=DocumentType.FINAL_ACCOUNT,
            title="Final Account and Report",
            template_path="final_account_and_report.txt"
        )
        doc.content = final_data
        doc.update_status(DocumentStatus.GENERATED)

        self.documents[doc.id] = doc

        if self.sharepoint:
            account_text = self._render_final_account_template(final_data)
            self.sharepoint.upload_document(self.estate.id, doc, account_text)

        logger.info(f"Final account and report generated: {doc.id}")
        return True

    def mark_deadline_completed(self, deadline_type: DeadlineType) -> bool:
        """Mark a deadline as completed"""
        for deadline in self.deadlines.values():
            if deadline.deadline_type == deadline_type:
                deadline.mark_completed()
                logger.info(f"Deadline marked completed: {deadline.description}")
                return True
        return False

    def get_upcoming_deadlines(self, days_ahead: int = 30) -> List[Dict]:
        """Get upcoming deadlines"""
        upcoming = []
        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        for deadline in self.deadlines.values():
            if not deadline.completed and deadline.due_date <= cutoff_date:
                upcoming.append(deadline.to_dict())

        return sorted(upcoming, key=lambda x: x['due_date'])

    def get_overdue_deadlines(self) -> List[Dict]:
        """Get overdue deadlines"""
        overdue = []
        for deadline in self.deadlines.values():
            if deadline.is_overdue():
                overdue.append(deadline.to_dict())
        return overdue

    def get_deadline_warnings(self) -> List[Dict]:
        """Get deadlines in warning period"""
        warnings = []
        for deadline in self.deadlines.values():
            if deadline.is_warning():
                warnings.append(deadline.to_dict())
        return warnings

    def get_document_status_report(self) -> Dict:
        """Get comprehensive document status report"""
        status_by_type = {}
        for doc in self.documents.values():
            doc_type = doc.document_type.value
            if doc_type not in status_by_type:
                status_by_type[doc_type] = []
            status_by_type[doc_type].append(doc.to_dict())

        return {
            'total_documents': len(self.documents),
            'documents_by_type': status_by_type,
            'draft_count': sum(1 for d in self.documents.values() if d.status == DocumentStatus.DRAFT),
            'generated_count': sum(1 for d in self.documents.values() if d.status == DocumentStatus.GENERATED),
            'filed_count': sum(1 for d in self.documents.values() if d.status == DocumentStatus.FILED),
            'published_count': sum(1 for d in self.documents.values() if d.status == DocumentStatus.PUBLISHED)
        }

    def export_workflow_status(self) -> Dict:
        """Export complete workflow status"""
        return {
            'estate_id': self.estate.id,
            'decedent_name': self.estate.decedent_name,
            'case_number': self.estate.case_number,
            'status': self.estate.status.value,
            'export_date': datetime.now().isoformat(),
            'estate_summary': self.workflow_mgr.get_estate_summary(),
            'deadlines': {
                'all': [d.to_dict() for d in self.deadlines.values()],
                'upcoming': self.get_upcoming_deadlines(30),
                'overdue': self.get_overdue_deadlines(),
                'warnings': self.get_deadline_warnings()
            },
            'documents': self.get_document_status_report()
        }

    def _render_petition_template(self, data: Dict) -> str:
        """Render petition template with data"""
        return f"PETITION FOR PROBATE\n{json.dumps(data, indent=2)}"

    def _render_notice_template(self, data: Dict) -> str:
        """Render notice template with data"""
        return f"NOTICE TO CREDITORS\n{json.dumps(data, indent=2)}"

    def _render_inventory_template(self, data: Dict) -> str:
        """Render inventory template with data"""
        return f"INVENTORY AND APPRAISAL\n{json.dumps(data, indent=2)}"

    def _render_final_account_template(self, data: Dict) -> str:
        """Render final account template with data"""
        return f"FINAL ACCOUNT AND REPORT\n{json.dumps(data, indent=2)}"

    def get_workflow_summary(self) -> str:
        """Get human-readable workflow summary"""
        summary = f"""
PROBATE WORKFLOW SUMMARY
{'='*80}

Estate Information:
  Decedent: {self.estate.decedent_name}
  Date of Death: {self.estate.date_of_death}
  State: {self.estate.state}
  County: {self.estate.court_county}
  Case Number: {self.estate.case_number or 'Not yet assigned'}
  Status: {self.estate.status.value}

Estate Assets:
  Total Estimated Value: ${self.estate.estimated_gross_value:,.2f}
  Number of Assets: {len(self.estate.assets)}

Creditors:
  Total Creditor Claims: {len(self.estate.creditors)}

Beneficiaries:
  Total Beneficiaries: {len(self.estate.beneficiaries)}

Upcoming Deadlines:
"""
        for deadline in self.get_upcoming_deadlines(30):
            status = deadline['status']
            due = deadline['due_date']
            summary += f"  [{status.upper()}] {deadline['description']} - Due: {due}\n"

        summary += f"\nDocument Status:\n"
        doc_status = self.get_document_status_report()
        summary += f"  Total Documents: {doc_status['total_documents']}\n"
        summary += f"  Draft: {doc_status['draft_count']}\n"
        summary += f"  Generated: {doc_status['generated_count']}\n"
        summary += f"  Filed: {doc_status['filed_count']}\n"
        summary += f"  Published: {doc_status['published_count']}\n"

        return summary

    def export_to_json(self) -> str:
        """Export complete workflow to JSON"""
        return json.dumps(self.export_workflow_status(), indent=2)


def create_sample_probate_case() -> Estate:
    """Create a sample probate case for demonstration"""
    estate = Estate(
        id=str(uuid.uuid4()),
        decedent_name="John Smith",
        date_of_death="2024-11-15",
        ssn_last_4="1234",
        state="California",
        court_county="Los Angeles",
        personal_representative="Jane Smith",
        pr_address="123 Main St, Los Angeles, CA 90001",
        pr_phone="(213) 555-0100",
        pr_email="jane.smith@email.com",
        will_on_file=True,
        estimated_gross_value=500000.00
    )

    # Add inventory manager and assets
    inv_mgr = EstateInventoryManager(estate)
    inv_mgr.add_asset(
        AssetType.REAL_PROPERTY,
        "Primary Residence",
        "123 Oak Ave, Los Angeles, CA",
        300000.00
    )
    inv_mgr.add_asset(
        AssetType.BANK_ACCOUNT,
        "Checking Account",
        "Bank of America",
        50000.00
    )
    inv_mgr.add_asset(
        AssetType.INVESTMENT,
        "Stock Portfolio",
        "Charles Schwab",
        100000.00
    )
    inv_mgr.add_asset(
        AssetType.VEHICLE,
        "2020 Honda Civic",
        "Los Angeles, CA",
        20000.00
    )

    # Add creditors
    cred_mgr = CreditorClaimManager(estate)
    cred_mgr.add_creditor(
        CreditorType.SECURED,
        "First Mortgage Bank",
        175000.00,
        priority_level=3,
        description="Mortgage on primary residence"
    )
    cred_mgr.add_creditor(
        CreditorType.UNSECURED,
        "Medical Provider",
        15000.00,
        priority_level=6,
        description="Hospital bills"
    )

    # Add beneficiaries
    dist_mgr = DistributionCalculator(estate)
    dist_mgr.add_beneficiary(
        "Jane Smith",
        "Spouse",
        60.0,
        "456 Main St, Los Angeles, CA 90001",
        "jane.smith@email.com"
    )
    dist_mgr.add_beneficiary(
        "John Smith Jr.",
        "Child",
        40.0,
        "789 Elm St, Los Angeles, CA 90002",
        "john.jr@email.com"
    )

    return estate


if __name__ == "__main__":
    # Create sample estate
    sample_estate = create_sample_probate_case()

    # Load configuration
    config_path = Path(__file__).parent.parent / "pillar-b-legal" / "probate" / "probate_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Initialize orchestrator (without SharePoint for demo)
    orchestrator = ProbateWorkflowOrchestrator(sample_estate, config)

    # Generate documents
    orchestrator.generate_petition_document()
    orchestrator.generate_notice_to_creditors()
    orchestrator.generate_inventory_document()
    orchestrator.generate_final_account_document()

    # Print workflow summary
    print(orchestrator.get_workflow_summary())

    # Export status
    status = orchestrator.export_workflow_status()
    print("\n\nWorkflow Status Export:")
    print(json.dumps(status, indent=2))
