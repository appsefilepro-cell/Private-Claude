"""
Probate and Estate Administration Automation System
Provides comprehensive tools for managing estate probate processes including
inventory, court forms, asset valuation, creditor claims, and distributions.
"""

import json
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetType(Enum):
    """Types of estate assets"""
    REAL_PROPERTY = "real_property"
    PERSONAL_PROPERTY = "personal_property"
    BANK_ACCOUNT = "bank_account"
    INVESTMENT = "investment"
    VEHICLE = "vehicle"
    BUSINESS_INTEREST = "business_interest"
    LIFE_INSURANCE = "life_insurance"
    RETIREMENT_ACCOUNT = "retirement_account"
    OTHER = "other"


class CreditorType(Enum):
    """Types of creditors"""
    SECURED = "secured"
    UNSECURED = "unsecured"
    PRIORITY = "priority"
    ADMINISTRATIVE = "administrative"


class ProbateStatus(Enum):
    """Probate process status"""
    INITIATED = "initiated"
    PETITION_FILED = "petition_filed"
    HEARING_SCHEDULED = "hearing_scheduled"
    PROBATE_GRANTED = "probate_granted"
    INVENTORY_FILED = "inventory_filed"
    ACCOUNTS_FILED = "accounts_filed"
    CREDITOR_PERIOD_OPEN = "creditor_period_open"
    ASSETS_DISTRIBUTED = "assets_distributed"
    CLOSED = "closed"


@dataclass
class Asset:
    """Represents an estate asset"""
    id: str
    asset_type: AssetType
    description: str
    location: str
    estimated_value: float
    fair_market_value: Optional[float] = None
    appraisal_date: Optional[str] = None
    encumbered_by: Optional[List[str]] = None  # List of creditor IDs
    debt_amount: float = 0.0
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['asset_type'] = self.asset_type.value
        if self.encumbered_by is None:
            data['encumbered_by'] = []
        return data

    def net_value(self) -> float:
        """Calculate net asset value after debts"""
        return max(0, (self.fair_market_value or self.estimated_value) - self.debt_amount)


@dataclass
class Creditor:
    """Represents a creditor claim against the estate"""
    id: str
    creditor_type: CreditorType
    name: str
    amount_claimed: float
    amount_allowed: float = 0.0
    priority_level: int = 0  # Lower number = higher priority
    description: str = ""
    proof_of_claim_received: bool = False
    proof_of_claim_date: Optional[str] = None
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['creditor_type'] = self.creditor_type.value
        return data


@dataclass
class Beneficiary:
    """Represents an estate beneficiary"""
    id: str
    name: str
    relationship: str
    share_percentage: float
    address: str
    contact_info: str
    date_of_birth: str = ""
    ssn_last_4: str = ""
    distribution_amount: float = 0.0
    distribution_status: str = "pending"
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Estate:
    """Represents the estate being administered"""
    id: str
    decedent_name: str
    date_of_death: str
    ssn_last_4: str
    state: str
    court_county: str
    case_number: Optional[str] = None
    personal_representative: str = ""
    pr_address: str = ""
    pr_phone: str = ""
    pr_email: str = ""
    will_on_file: bool = True
    estimated_gross_value: float = 0.0
    assets: Dict[str, Asset] = field(default_factory=dict)
    creditors: Dict[str, Creditor] = field(default_factory=dict)
    beneficiaries: Dict[str, Beneficiary] = field(default_factory=dict)
    status: ProbateStatus = ProbateStatus.INITIATED
    filing_date: Optional[str] = None
    hearing_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'decedent_name': self.decedent_name,
            'date_of_death': self.date_of_death,
            'ssn_last_4': self.ssn_last_4,
            'state': self.state,
            'court_county': self.court_county,
            'case_number': self.case_number,
            'personal_representative': self.personal_representative,
            'pr_address': self.pr_address,
            'pr_phone': self.pr_phone,
            'pr_email': self.pr_email,
            'will_on_file': self.will_on_file,
            'estimated_gross_value': self.estimated_gross_value,
            'assets': {k: v.to_dict() for k, v in self.assets.items()},
            'creditors': {k: v.to_dict() for k, v in self.creditors.items()},
            'beneficiaries': {k: v.to_dict() for k, v in self.beneficiaries.items()},
            'status': self.status.value,
            'filing_date': self.filing_date,
            'hearing_date': self.hearing_date,
            'created_at': self.created_at,
            'last_updated': self.last_updated
        }


class EstateInventoryManager:
    """Manages estate inventory and asset tracking"""

    def __init__(self, estate: Estate):
        self.estate = estate

    def add_asset(
        self,
        asset_type: AssetType,
        description: str,
        location: str,
        estimated_value: float,
        notes: str = ""
    ) -> str:
        """Add an asset to the estate inventory"""
        asset_id = str(uuid.uuid4())
        asset = Asset(
            id=asset_id,
            asset_type=asset_type,
            description=description,
            location=location,
            estimated_value=estimated_value,
            notes=notes
        )
        self.estate.assets[asset_id] = asset
        self.estate.last_updated = datetime.now().isoformat()
        logger.info(f"Added asset {asset_id}: {description} (${estimated_value:,.2f})")
        return asset_id

    def update_asset_valuation(
        self,
        asset_id: str,
        fair_market_value: float,
        appraisal_date: Optional[str] = None
    ) -> bool:
        """Update asset's fair market value based on appraisal"""
        if asset_id not in self.estate.assets:
            logger.warning(f"Asset {asset_id} not found")
            return False

        asset = self.estate.assets[asset_id]
        asset.fair_market_value = fair_market_value
        asset.appraisal_date = appraisal_date or datetime.now().isoformat()
        self.estate.last_updated = datetime.now().isoformat()
        logger.info(f"Updated asset {asset_id} valuation to ${fair_market_value:,.2f}")
        return True

    def encumber_asset(self, asset_id: str, creditor_id: str, debt_amount: float) -> bool:
        """Mark asset as encumbered by a creditor"""
        if asset_id not in self.estate.assets:
            logger.warning(f"Asset {asset_id} not found")
            return False

        asset = self.estate.assets[asset_id]
        if asset.encumbered_by is None:
            asset.encumbered_by = []
        asset.encumbered_by.append(creditor_id)
        asset.debt_amount += debt_amount
        self.estate.last_updated = datetime.now().isoformat()
        logger.info(f"Asset {asset_id} encumbered by creditor {creditor_id}: ${debt_amount:,.2f}")
        return True

    def get_inventory_summary(self) -> Dict:
        """Generate inventory summary"""
        total_estimated = sum(a.estimated_value for a in self.estate.assets.values())
        total_fair_market = sum(a.fair_market_value or a.estimated_value for a in self.estate.assets.values())
        total_encumbrances = sum(a.debt_amount for a in self.estate.assets.values())
        net_estate_value = total_fair_market - total_encumbrances

        assets_by_type = {}
        for asset in self.estate.assets.values():
            asset_type = asset.asset_type.value
            if asset_type not in assets_by_type:
                assets_by_type[asset_type] = []
            assets_by_type[asset_type].append(asset.to_dict())

        return {
            'total_estimated_value': total_estimated,
            'total_fair_market_value': total_fair_market,
            'total_encumbrances': total_encumbrances,
            'net_estate_value': net_estate_value,
            'asset_count': len(self.estate.assets),
            'assets_by_type': assets_by_type
        }


class CreditorClaimManager:
    """Manages creditor claims against the estate"""

    def __init__(self, estate: Estate):
        self.estate = estate

    def add_creditor(
        self,
        creditor_type: CreditorType,
        name: str,
        amount_claimed: float,
        priority_level: int = 0,
        description: str = ""
    ) -> str:
        """Add a creditor claim to the estate"""
        creditor_id = str(uuid.uuid4())
        creditor = Creditor(
            id=creditor_id,
            creditor_type=creditor_type,
            name=name,
            amount_claimed=amount_claimed,
            priority_level=priority_level,
            description=description
        )
        self.estate.creditors[creditor_id] = creditor
        self.estate.last_updated = datetime.now().isoformat()
        logger.info(f"Added creditor {creditor_id}: {name} (${amount_claimed:,.2f})")
        return creditor_id

    def process_proof_of_claim(self, creditor_id: str, allowed_amount: float) -> bool:
        """Process proof of claim and determine allowed amount"""
        if creditor_id not in self.estate.creditors:
            logger.warning(f"Creditor {creditor_id} not found")
            return False

        creditor = self.estate.creditors[creditor_id]
        creditor.proof_of_claim_received = True
        creditor.proof_of_claim_date = datetime.now().isoformat()
        creditor.amount_allowed = min(allowed_amount, creditor.amount_claimed)
        self.estate.last_updated = datetime.now().isoformat()
        logger.info(f"Processed proof of claim for {creditor_id}: ${creditor.amount_allowed:,.2f} allowed")
        return True

    def get_creditor_report(self) -> Dict:
        """Generate creditor claims report"""
        total_claimed = sum(c.amount_claimed for c in self.estate.creditors.values())
        total_allowed = sum(c.amount_allowed for c in self.estate.creditors.values())
        claims_processed = sum(1 for c in self.estate.creditors.values() if c.proof_of_claim_received)

        creditors_by_type = {}
        creditors_by_priority = {}

        for creditor in self.estate.creditors.values():
            cred_type = creditor.creditor_type.value
            if cred_type not in creditors_by_type:
                creditors_by_type[cred_type] = []
            creditors_by_type[cred_type].append(creditor.to_dict())

            priority = creditor.priority_level
            if priority not in creditors_by_priority:
                creditors_by_priority[priority] = []
            creditors_by_priority[priority].append(creditor.to_dict())

        return {
            'total_claimed': total_claimed,
            'total_allowed': total_allowed,
            'creditor_count': len(self.estate.creditors),
            'claims_processed': claims_processed,
            'claims_pending': len(self.estate.creditors) - claims_processed,
            'creditors_by_type': creditors_by_type,
            'creditors_by_priority': sorted(creditors_by_priority.items(), key=lambda x: x[0])
        }


class DistributionCalculator:
    """Calculates distributions to beneficiaries"""

    def __init__(self, estate: Estate):
        self.estate = estate

    def add_beneficiary(
        self,
        name: str,
        relationship: str,
        share_percentage: float,
        address: str,
        contact_info: str
    ) -> str:
        """Add a beneficiary to the estate"""
        beneficiary_id = str(uuid.uuid4())
        beneficiary = Beneficiary(
            id=beneficiary_id,
            name=name,
            relationship=relationship,
            share_percentage=share_percentage,
            address=address,
            contact_info=contact_info
        )
        self.estate.beneficiaries[beneficiary_id] = beneficiary
        self.estate.last_updated = datetime.now().isoformat()
        logger.info(f"Added beneficiary {beneficiary_id}: {name} ({share_percentage}%)")
        return beneficiary_id

    def calculate_distributions(self) -> Dict[str, float]:
        """Calculate net distribution for each beneficiary"""
        # Get net estate value
        inventory_mgr = EstateInventoryManager(self.estate)
        summary = inventory_mgr.get_inventory_summary()
        net_estate_value = summary['net_estate_value']

        distributions = {}
        for beneficiary in self.estate.beneficiaries.values():
            distribution = (net_estate_value * beneficiary.share_percentage) / 100
            distributions[beneficiary.id] = distribution
            beneficiary.distribution_amount = distribution
            logger.info(f"Calculated distribution for {beneficiary.name}: ${distribution:,.2f}")

        return distributions

    def approve_distributions(self) -> bool:
        """Approve all distributions and update status"""
        self.calculate_distributions()
        for beneficiary in self.estate.beneficiaries.values():
            beneficiary.distribution_status = "approved"
        self.estate.last_updated = datetime.now().isoformat()
        logger.info("All distributions approved")
        return True

    def record_distribution(self, beneficiary_id: str) -> bool:
        """Record that distribution was made to beneficiary"""
        if beneficiary_id not in self.estate.beneficiaries:
            logger.warning(f"Beneficiary {beneficiary_id} not found")
            return False

        beneficiary = self.estate.beneficiaries[beneficiary_id]
        beneficiary.distribution_status = "distributed"
        self.estate.last_updated = datetime.now().isoformat()
        logger.info(f"Recorded distribution to {beneficiary.name}")
        return True

    def get_distribution_summary(self) -> Dict:
        """Generate distribution summary"""
        distributions = self.calculate_distributions()
        total_to_distribute = sum(distributions.values())

        beneficiary_details = []
        for beneficiary in self.estate.beneficiaries.values():
            beneficiary_details.append({
                'id': beneficiary.id,
                'name': beneficiary.name,
                'relationship': beneficiary.relationship,
                'share_percentage': beneficiary.share_percentage,
                'distribution_amount': beneficiary.distribution_amount,
                'distribution_status': beneficiary.distribution_status
            })

        return {
            'total_to_distribute': total_to_distribute,
            'beneficiary_count': len(self.estate.beneficiaries),
            'beneficiaries': sorted(
                beneficiary_details,
                key=lambda x: x['distribution_amount'],
                reverse=True
            )
        }


class ProbateFormGenerator:
    """Generates required probate court forms"""

    def __init__(self, estate: Estate, config: Dict):
        self.estate = estate
        self.config = config

    def generate_petition_for_probate(self) -> Dict:
        """Generate petition for probate form"""
        return {
            'form_type': 'Petition for Probate',
            'decedent_name': self.estate.decedent_name,
            'date_of_death': self.estate.date_of_death,
            'state': self.estate.state,
            'county': self.estate.court_county,
            'personal_representative': self.estate.personal_representative,
            'pr_address': self.estate.pr_address,
            'will_on_file': self.estate.will_on_file,
            'estimated_value': self.estate.estimated_gross_value,
            'generated_date': datetime.now().isoformat(),
            'template_name': 'petition_for_probate.txt'
        }

    def generate_notice_to_creditors(self) -> Dict:
        """Generate notice to creditors form"""
        deadline = datetime.now() + timedelta(
            days=self.config.get('creditor_claim_deadline_days', 120)
        )
        return {
            'form_type': 'Notice to Creditors',
            'case_number': self.estate.case_number,
            'decedent_name': self.estate.decedent_name,
            'date_of_death': self.estate.date_of_death,
            'personal_representative': self.estate.personal_representative,
            'pr_address': self.estate.pr_address,
            'pr_email': self.estate.pr_email,
            'claim_deadline': deadline.isoformat(),
            'county': self.estate.court_county,
            'generated_date': datetime.now().isoformat(),
            'template_name': 'notice_to_creditors.txt'
        }

    def generate_inventory_and_appraisal(self) -> Dict:
        """Generate inventory and appraisal form"""
        inventory_mgr = EstateInventoryManager(self.estate)
        summary = inventory_mgr.get_inventory_summary()

        return {
            'form_type': 'Inventory and Appraisal',
            'case_number': self.estate.case_number,
            'decedent_name': self.estate.decedent_name,
            'assets': self.estate.assets,
            'total_value': summary['total_fair_market_value'],
            'appraiser_name': 'Professional Appraiser',
            'appraised_date': datetime.now().isoformat(),
            'generated_date': datetime.now().isoformat(),
            'template_name': 'inventory_and_appraisal.txt'
        }

    def generate_final_account_and_report(self) -> Dict:
        """Generate final account and report form"""
        inventory_mgr = EstateInventoryManager(self.estate)
        creditor_mgr = CreditorClaimManager(self.estate)
        dist_mgr = DistributionCalculator(self.estate)

        inventory_summary = inventory_mgr.get_inventory_summary()
        creditor_summary = creditor_mgr.get_creditor_report()
        distribution_summary = dist_mgr.get_distribution_summary()

        return {
            'form_type': 'Final Account and Report',
            'case_number': self.estate.case_number,
            'decedent_name': self.estate.decedent_name,
            'personal_representative': self.estate.personal_representative,
            'inventory_value': inventory_summary['total_fair_market_value'],
            'encumbrances': inventory_summary['total_encumbrances'],
            'total_claims': creditor_summary['total_allowed'],
            'net_estate': inventory_summary['net_estate_value'],
            'distributions': distribution_summary,
            'generated_date': datetime.now().isoformat(),
            'template_name': 'final_account_and_report.txt'
        }


class ProbateWorkflowManager:
    """Orchestrates the overall probate workflow and process management"""

    def __init__(self, estate: Estate, config: Dict):
        self.estate = estate
        self.config = config
        self.inventory_mgr = EstateInventoryManager(estate)
        self.creditor_mgr = CreditorClaimManager(estate)
        self.distribution_mgr = DistributionCalculator(estate)
        self.form_generator = ProbateFormGenerator(estate, config)

    def get_estate_summary(self) -> Dict:
        """Get comprehensive estate summary"""
        inventory_summary = self.inventory_mgr.get_inventory_summary()
        creditor_summary = self.creditor_mgr.get_creditor_report()
        distribution_summary = self.distribution_mgr.get_distribution_summary()

        return {
            'estate_id': self.estate.id,
            'decedent_name': self.estate.decedent_name,
            'case_number': self.estate.case_number,
            'status': self.estate.status.value,
            'filing_date': self.estate.filing_date,
            'assets': inventory_summary,
            'creditors': creditor_summary,
            'distributions': distribution_summary,
            'last_updated': self.estate.last_updated
        }

    def advance_status(self, new_status: ProbateStatus) -> bool:
        """Advance the estate's probate status"""
        self.estate.status = new_status
        self.estate.last_updated = datetime.now().isoformat()

        if new_status == ProbateStatus.PETITION_FILED:
            self.estate.filing_date = datetime.now().isoformat()
            self.estate.hearing_date = (
                datetime.now() + timedelta(days=self.config.get('hearing_days', 30))
            ).isoformat()

        logger.info(f"Estate status advanced to {new_status.value}")
        return True

    def export_to_json(self) -> str:
        """Export estate data to JSON"""
        return json.dumps(self.estate.to_dict(), indent=2)

    def export_summary_report(self) -> str:
        """Export comprehensive summary report"""
        summary = self.get_estate_summary()
        return json.dumps(summary, indent=2)
