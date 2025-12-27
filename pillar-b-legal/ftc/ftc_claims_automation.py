#!/usr/bin/env python3
"""
FTC CLAIMS AUTOMATION SYSTEM
Automate FTC settlement claims submission and tracking

Features:
- Claimant status verification
- Documentation requirements checker
- Form auto-fill with acceptable formatting
- Receipt/proof attachment system
- Exhibit list extraction
- Claim tracking and status monitoring
- Multi-settlement support

Author: Thurman Robinson Jr
Date: 2025-12-27
"""

import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import re


# ============================================================================
# ENUMERATIONS AND CONSTANTS
# ============================================================================

class ClaimStatus(Enum):
    """Status of FTC claim"""
    DRAFT = "Draft"
    READY_TO_SUBMIT = "Ready to Submit"
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    DENIED = "Denied"
    PAYMENT_ISSUED = "Payment Issued"
    PAYMENT_RECEIVED = "Payment Received"


class DocumentType(Enum):
    """Types of supporting documents"""
    RECEIPT = "Receipt"
    INVOICE = "Invoice"
    BANK_STATEMENT = "Bank Statement"
    CREDIT_CARD_STATEMENT = "Credit Card Statement"
    CONTRACT = "Contract"
    EMAIL_CONFIRMATION = "Email Confirmation"
    SCREENSHOT = "Screenshot"
    DECLARATION = "Declaration"
    OTHER = "Other"


class SettlementProgram(Enum):
    """FTC Settlement Programs"""
    GENERAL = "General FTC Settlement"
    CONSUMER_REFUND = "Consumer Refund Program"
    REDRESS = "Consumer Redress"
    EQUITABLE_MONETARY_RELIEF = "Equitable Monetary Relief"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Claimant:
    """Represents a claimant"""
    first_name: str
    last_name: str
    email: str
    phone: str
    address_line1: str
    address_line2: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = "United States"

    # Identification
    ssn_last4: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None

    # Banking (for payment)
    bank_name: Optional[str] = None
    account_type: Optional[str] = None  # Checking/Savings
    routing_number: Optional[str] = None
    account_number: Optional[str] = None

    def get_full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"

    def get_full_address(self) -> str:
        """Get formatted address"""
        addr = self.address_line1
        if self.address_line2:
            addr += f"\n{self.address_line2}"
        addr += f"\n{self.city}, {self.state} {self.zip_code}"
        if self.country != "United States":
            addr += f"\n{self.country}"
        return addr

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate claimant information"""
        errors = []

        if not self.first_name:
            errors.append("First name is required")
        if not self.last_name:
            errors.append("Last name is required")
        if not self.email or '@' not in self.email:
            errors.append("Valid email is required")
        if not self.phone:
            errors.append("Phone number is required")
        if not self.address_line1:
            errors.append("Address is required")
        if not self.city:
            errors.append("City is required")
        if not self.state:
            errors.append("State is required")
        if not self.zip_code:
            errors.append("ZIP code is required")

        # ZIP code format
        if self.zip_code and not re.match(r'^\d{5}(-\d{4})?$', self.zip_code):
            errors.append("ZIP code must be in format 12345 or 12345-6789")

        # Phone format
        if self.phone:
            cleaned = re.sub(r'\D', '', self.phone)
            if len(cleaned) != 10:
                errors.append("Phone number must be 10 digits")

        return (len(errors) == 0, errors)


@dataclass
class SupportingDocument:
    """Represents a supporting document"""
    document_id: str
    document_type: DocumentType
    filename: str
    file_path: str
    description: str
    date_of_document: Optional[datetime.date] = None
    amount: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'document_id': self.document_id,
            'document_type': self.document_type.value,
            'filename': self.filename,
            'file_path': self.file_path,
            'description': self.description,
            'date_of_document': self.date_of_document.isoformat() if self.date_of_document else None,
            'amount': self.amount
        }


@dataclass
class ClaimItem:
    """Represents a single claim item/transaction"""
    item_id: str
    description: str
    amount: float
    transaction_date: datetime.date
    merchant_name: Optional[str] = None
    payment_method: Optional[str] = None
    supporting_docs: List[SupportingDocument] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'item_id': self.item_id,
            'description': self.description,
            'amount': self.amount,
            'transaction_date': self.transaction_date.isoformat(),
            'merchant_name': self.merchant_name,
            'payment_method': self.payment_method,
            'supporting_docs': [doc.to_dict() for doc in self.supporting_docs]
        }


@dataclass
class FTCClaim:
    """Represents a complete FTC claim"""
    claim_id: str
    settlement_name: str
    settlement_program: SettlementProgram
    claimant: Claimant
    claim_items: List[ClaimItem]
    status: ClaimStatus = ClaimStatus.DRAFT
    submission_date: Optional[datetime.date] = None
    confirmation_number: Optional[str] = None
    claim_amount: float = 0.0

    def calculate_total(self) -> float:
        """Calculate total claim amount"""
        self.claim_amount = sum(item.amount for item in self.claim_items)
        return self.claim_amount

    def get_total_items(self) -> int:
        """Get total number of claim items"""
        return len(self.claim_items)

    def get_total_documents(self) -> int:
        """Get total number of supporting documents"""
        return sum(len(item.supporting_docs) for item in self.claim_items)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'claim_id': self.claim_id,
            'settlement_name': self.settlement_name,
            'settlement_program': self.settlement_program.value,
            'claimant_name': self.claimant.get_full_name(),
            'claim_items': [item.to_dict() for item in self.claim_items],
            'status': self.status.value,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'confirmation_number': self.confirmation_number,
            'claim_amount': self.claim_amount
        }


# ============================================================================
# FTC CLAIMS AUTOMATION SYSTEM
# ============================================================================

class FTCClaimsSystem:
    """Complete FTC claims automation system"""

    def __init__(self):
        self.claims: List[FTCClaim] = []

        self.data_dir = Path("/home/user/Private-Claude/pillar-b-legal/ftc/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.forms_dir = Path("/home/user/Private-Claude/pillar-b-legal/ftc/forms")
        self.forms_dir.mkdir(parents=True, exist_ok=True)

        self.documents_dir = Path("/home/user/Private-Claude/pillar-b-legal/ftc/documents")
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # CLAIM MANAGEMENT
    # ========================================================================

    def create_claim(self, settlement_name: str, settlement_program: SettlementProgram,
                    claimant: Claimant) -> FTCClaim:
        """Create a new FTC claim"""
        claim = FTCClaim(
            claim_id=f"FTC-{len(self.claims) + 1:04d}",
            settlement_name=settlement_name,
            settlement_program=settlement_program,
            claimant=claimant,
            claim_items=[]
        )
        self.claims.append(claim)
        self.save_data()
        return claim

    def add_claim_item(self, claim_id: str, item: ClaimItem) -> bool:
        """Add an item to a claim"""
        for claim in self.claims:
            if claim.claim_id == claim_id:
                claim.claim_items.append(item)
                claim.calculate_total()
                self.save_data()
                return True
        return False

    def add_supporting_document(self, claim_id: str, item_id: str,
                               document: SupportingDocument) -> bool:
        """Add a supporting document to a claim item"""
        for claim in self.claims:
            if claim.claim_id == claim_id:
                for item in claim.claim_items:
                    if item.item_id == item_id:
                        item.supporting_docs.append(document)
                        self.save_data()
                        return True
        return False

    def get_claim(self, claim_id: str) -> Optional[FTCClaim]:
        """Get a claim by ID"""
        for claim in self.claims:
            if claim.claim_id == claim_id:
                return claim
        return None

    # ========================================================================
    # CLAIMANT VERIFICATION
    # ========================================================================

    def verify_claimant(self, claimant: Claimant) -> Tuple[bool, List[str], List[str]]:
        """
        Verify claimant information

        Returns:
            (is_valid, errors, warnings)
        """
        is_valid, errors = claimant.validate()
        warnings = []

        # Additional checks
        if not claimant.ssn_last4:
            warnings.append("SSN last 4 digits not provided (may be required)")

        if not claimant.date_of_birth:
            warnings.append("Date of birth not provided (may be required)")

        if not claimant.bank_name or not claimant.routing_number or not claimant.account_number:
            warnings.append("Banking information incomplete (required for direct deposit)")

        return (is_valid, errors, warnings)

    # ========================================================================
    # DOCUMENTATION REQUIREMENTS CHECKER
    # ========================================================================

    def check_documentation_requirements(self, claim: FTCClaim) -> Dict[str, any]:
        """Check if claim has sufficient documentation"""
        requirements = {
            'has_items': len(claim.claim_items) > 0,
            'all_items_documented': True,
            'missing_docs': [],
            'warnings': [],
            'ready_to_submit': False
        }

        if not claim.claim_items:
            requirements['warnings'].append("No claim items added")
            return requirements

        # Check each item for documentation
        for item in claim.claim_items:
            if len(item.supporting_docs) == 0:
                requirements['all_items_documented'] = False
                requirements['missing_docs'].append(
                    f"Item {item.item_id}: {item.description} - No supporting documents"
                )

        # Check claimant info
        is_valid, errors, warnings = self.verify_claimant(claim.claimant)
        if not is_valid:
            requirements['warnings'].extend(errors)
            requirements['ready_to_submit'] = False
        else:
            if warnings:
                requirements['warnings'].extend(warnings)

            if requirements['all_items_documented'] and claim.claim_amount > 0:
                requirements['ready_to_submit'] = True

        return requirements

    # ========================================================================
    # FORM AUTO-FILL
    # ========================================================================

    def generate_claim_form(self, claim: FTCClaim) -> str:
        """Generate auto-filled claim form"""
        today = datetime.date.today()

        form = f"""
FTC SETTLEMENT CLAIM FORM
{claim.settlement_name}

Claim ID: {claim.claim_id}
Submission Date: {today.strftime('%B %d, %Y')}

{'='*80}
CLAIMANT INFORMATION
{'='*80}

Name: {claim.claimant.get_full_name()}
Email: {claim.claimant.email}
Phone: {claim.claimant.phone}

Address:
{claim.claimant.get_full_address()}

"""

        if claim.claimant.ssn_last4:
            form += f"SSN (Last 4): XXX-XX-{claim.claimant.ssn_last4}\n"

        if claim.claimant.date_of_birth:
            form += f"Date of Birth: {claim.claimant.date_of_birth.strftime('%m/%d/%Y')}\n"

        form += f"""
{'='*80}
BANKING INFORMATION (For Direct Deposit)
{'='*80}

"""

        if claim.claimant.bank_name:
            form += f"Bank Name: {claim.claimant.bank_name}\n"
            form += f"Account Type: {claim.claimant.account_type or '[Not specified]'}\n"
            form += f"Routing Number: {claim.claimant.routing_number or '[Not provided]'}\n"
            form += f"Account Number: {claim.claimant.account_number or '[Not provided]'}\n"
        else:
            form += "Banking information not provided - will receive check by mail\n"

        form += f"""
{'='*80}
CLAIM DETAILS
{'='*80}

Settlement Program: {claim.settlement_program.value}
Total Claim Items: {claim.get_total_items()}
Total Claim Amount: ${claim.calculate_total():,.2f}
Total Supporting Documents: {claim.get_total_documents()}

"""

        form += f"""
{'='*80}
ITEMIZED CLAIM
{'='*80}

"""

        for i, item in enumerate(claim.claim_items, 1):
            form += f"""
Item {i}:
  ID: {item.item_id}
  Description: {item.description}
  Transaction Date: {item.transaction_date.strftime('%m/%d/%Y')}
  Amount: ${item.amount:,.2f}
"""
            if item.merchant_name:
                form += f"  Merchant: {item.merchant_name}\n"
            if item.payment_method:
                form += f"  Payment Method: {item.payment_method}\n"

            form += f"  Supporting Documents ({len(item.supporting_docs)}):\n"
            for doc in item.supporting_docs:
                form += f"    - {doc.document_type.value}: {doc.filename}\n"
                if doc.description:
                    form += f"      Description: {doc.description}\n"

        form += f"""
{'='*80}
CERTIFICATION
{'='*80}

I certify under penalty of perjury that:

1. I am the person named in this claim form
2. All information provided is true and correct
3. I have attached all required supporting documentation
4. I understand that providing false information may result in denial of my claim and/or legal consequences
5. I am eligible to participate in this settlement

Claimant Name: {claim.claimant.get_full_name()}
Date: {today.strftime('%B %d, %Y')}

Signature: _________________________________


{'='*80}
FOR OFFICE USE ONLY
{'='*80}

Claim ID: {claim.claim_id}
Received Date: _______________
Processed By: _______________
Status: _______________
Confirmation Number: _______________
"""

        return form

    # ========================================================================
    # EXHIBIT LIST EXTRACTION
    # ========================================================================

    def generate_exhibit_list(self, claim: FTCClaim) -> str:
        """Generate exhibit list for all supporting documents"""
        exhibit_list = f"""
EXHIBIT LIST
FTC Claim: {claim.claim_id}
Settlement: {claim.settlement_name}
Claimant: {claim.claimant.get_full_name()}

{'='*80}
"""

        exhibit_num = 1
        for item_num, item in enumerate(claim.claim_items, 1):
            exhibit_list += f"\nClaim Item {item_num}: {item.description} (${item.amount:,.2f})\n"
            exhibit_list += f"{'-'*80}\n"

            for doc in item.supporting_docs:
                exhibit_list += f"Exhibit {exhibit_num}: {doc.document_type.value}\n"
                exhibit_list += f"  Filename: {doc.filename}\n"
                exhibit_list += f"  Description: {doc.description}\n"
                if doc.date_of_document:
                    exhibit_list += f"  Date: {doc.date_of_document.strftime('%m/%d/%Y')}\n"
                if doc.amount:
                    exhibit_list += f"  Amount: ${doc.amount:,.2f}\n"
                exhibit_list += "\n"
                exhibit_num += 1

        exhibit_list += f"{'='*80}\n"
        exhibit_list += f"Total Exhibits: {exhibit_num - 1}\n"
        exhibit_list += f"Total Claim Amount: ${claim.claim_amount:,.2f}\n"

        return exhibit_list

    # ========================================================================
    # SUBMISSION CHECKLIST
    # ========================================================================

    def generate_submission_checklist(self, claim: FTCClaim) -> str:
        """Generate submission checklist"""
        requirements = self.check_documentation_requirements(claim)

        checklist = f"""
SUBMISSION CHECKLIST
FTC Claim: {claim.claim_id}
Settlement: {claim.settlement_name}

{'='*80}

CLAIMANT INFORMATION:
"""

        is_valid, errors, warnings = self.verify_claimant(claim.claimant)

        checklist += f"[ {'X' if is_valid else ' '} ] Complete claimant information provided\n"
        checklist += f"[ {'X' if claim.claimant.ssn_last4 else ' '} ] SSN (last 4 digits)\n"
        checklist += f"[ {'X' if claim.claimant.date_of_birth else ' '} ] Date of birth\n"
        checklist += f"[ {'X' if claim.claimant.bank_name else ' '} ] Banking information (for direct deposit)\n"

        checklist += f"""
CLAIM DETAILS:
[ {'X' if claim.claim_items else ' '} ] At least one claim item added
[ {'X' if requirements['all_items_documented'] else ' '} ] All items have supporting documentation
[ {'X' if claim.claim_amount > 0 else ' '} ] Total claim amount calculated: ${claim.claim_amount:,.2f}

DOCUMENTATION:
[ {'X' if claim.get_total_documents() > 0 else ' '} ] Supporting documents attached ({claim.get_total_documents()} total)
[ {'X' if requirements['ready_to_submit'] else ' '} ] All required documentation present

"""

        if requirements['missing_docs']:
            checklist += "MISSING DOCUMENTATION:\n"
            for missing in requirements['missing_docs']:
                checklist += f"  - {missing}\n"
            checklist += "\n"

        if requirements['warnings']:
            checklist += "WARNINGS:\n"
            for warning in requirements['warnings']:
                checklist += f"  - {warning}\n"
            checklist += "\n"

        checklist += f"""
{'='*80}
SUBMISSION STATUS:
"""

        if requirements['ready_to_submit']:
            checklist += "✓ READY TO SUBMIT\n"
            checklist += "\nYour claim is complete and ready for submission.\n"
        else:
            checklist += "✗ NOT READY TO SUBMIT\n"
            checklist += "\nPlease address the items above before submitting.\n"

        checklist += f"{'='*80}\n"

        return checklist

    # ========================================================================
    # CLAIM SUBMISSION
    # ========================================================================

    def submit_claim(self, claim_id: str) -> Tuple[bool, str]:
        """Mark claim as submitted"""
        claim = self.get_claim(claim_id)
        if not claim:
            return (False, "Claim not found")

        requirements = self.check_documentation_requirements(claim)
        if not requirements['ready_to_submit']:
            return (False, "Claim is not ready to submit - missing required information/documentation")

        claim.status = ClaimStatus.SUBMITTED
        claim.submission_date = datetime.date.today()
        self.save_data()

        # Generate submission package
        self._generate_submission_package(claim)

        return (True, f"Claim {claim_id} submitted successfully on {claim.submission_date.strftime('%B %d, %Y')}")

    def _generate_submission_package(self, claim: FTCClaim) -> None:
        """Generate complete submission package"""
        package_dir = self.forms_dir / claim.claim_id
        package_dir.mkdir(exist_ok=True)

        # 1. Claim form
        form = self.generate_claim_form(claim)
        with open(package_dir / "claim_form.txt", 'w') as f:
            f.write(form)

        # 2. Exhibit list
        exhibit_list = self.generate_exhibit_list(claim)
        with open(package_dir / "exhibit_list.txt", 'w') as f:
            f.write(exhibit_list)

        # 3. Checklist
        checklist = self.generate_submission_checklist(claim)
        with open(package_dir / "submission_checklist.txt", 'w') as f:
            f.write(checklist)

        # 4. README
        readme = f"""
FTC CLAIM SUBMISSION PACKAGE
Claim ID: {claim.claim_id}
Settlement: {claim.settlement_name}
Claimant: {claim.claimant.get_full_name()}
Submission Date: {claim.submission_date.strftime('%B %d, %Y')}

CONTENTS:
---------
1. claim_form.txt - Completed claim form
2. exhibit_list.txt - List of all supporting documents
3. submission_checklist.txt - Verification checklist
4. README.txt - This file

NEXT STEPS:
-----------
1. Review all documents for accuracy
2. Ensure all supporting documents referenced in the exhibit list are included
3. Submit online at the FTC settlement website OR
4. Print and mail to the address provided in the settlement notice
5. Keep a copy of all submitted materials for your records

IMPORTANT:
----------
- Do not include this README in your submission
- Submit only the claim form and supporting documents
- Note your confirmation number when you receive it
- Monitor the settlement website for updates on your claim status
"""

        with open(package_dir / "README.txt", 'w') as f:
            f.write(readme)

    # ========================================================================
    # STATUS TRACKING
    # ========================================================================

    def update_claim_status(self, claim_id: str, status: ClaimStatus,
                           confirmation_number: Optional[str] = None) -> bool:
        """Update claim status"""
        claim = self.get_claim(claim_id)
        if not claim:
            return False

        claim.status = status
        if confirmation_number:
            claim.confirmation_number = confirmation_number

        self.save_data()
        return True

    def get_claims_by_status(self, status: ClaimStatus) -> List[FTCClaim]:
        """Get all claims with a specific status"""
        return [c for c in self.claims if c.status == status]

    # ========================================================================
    # REPORTING
    # ========================================================================

    def generate_summary_report(self) -> str:
        """Generate summary report of all claims"""
        total_claims = len(self.claims)
        total_amount = sum(c.claim_amount for c in self.claims)

        report = f"""
{'='*80}
FTC CLAIMS SUMMARY REPORT
Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}
{'='*80}

OVERALL STATISTICS:
-------------------
Total Claims: {total_claims}
Total Claim Amount: ${total_amount:,.2f}
Average Claim Amount: ${total_amount / max(total_claims, 1):,.2f}

CLAIMS BY STATUS:
-----------------
"""

        for status in ClaimStatus:
            claims = self.get_claims_by_status(status)
            if claims:
                status_amount = sum(c.claim_amount for c in claims)
                report += f"{status.value}: {len(claims)} (${status_amount:,.2f})\n"

        report += f"""
DETAILED CLAIMS:
----------------
"""

        for claim in self.claims:
            report += f"""
Claim ID: {claim.claim_id}
  Settlement: {claim.settlement_name}
  Claimant: {claim.claimant.get_full_name()}
  Status: {claim.status.value}
  Items: {claim.get_total_items()}
  Amount: ${claim.claim_amount:,.2f}
  Documents: {claim.get_total_documents()}
"""
            if claim.submission_date:
                report += f"  Submitted: {claim.submission_date.strftime('%m/%d/%Y')}\n"
            if claim.confirmation_number:
                report += f"  Confirmation: {claim.confirmation_number}\n"

        report += f"\n{'='*80}\n"

        return report

    # ========================================================================
    # DATA PERSISTENCE
    # ========================================================================

    def save_data(self) -> None:
        """Save all claims data to JSON"""
        data = {
            'claims': [claim.to_dict() for claim in self.claims],
            'total_claims': len(self.claims),
            'total_amount': sum(c.claim_amount for c in self.claims),
            'last_updated': datetime.datetime.now().isoformat()
        }

        filepath = self.data_dir / 'ftc_claims_data.json'
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# ============================================================================
# MAIN EXECUTION AND EXAMPLES
# ============================================================================

def main():
    """Example usage"""
    system = FTCClaimsSystem()

    print("="*80)
    print("FTC CLAIMS AUTOMATION SYSTEM")
    print("="*80)
    print(f"\nData directory: {system.data_dir}")
    print(f"Forms directory: {system.forms_dir}")
    print(f"Documents directory: {system.documents_dir}")

    # Example: Create a claimant
    claimant = Claimant(
        first_name="Thurman",
        last_name="Robinson",
        email="thurman@example.com",
        phone="555-123-4567",
        address_line1="123 Main Street",
        city="Los Angeles",
        state="CA",
        zip_code="90001",
        ssn_last4="1234",
        date_of_birth=datetime.date(1990, 1, 1),
        bank_name="Example Bank",
        account_type="Checking",
        routing_number="123456789",
        account_number="9876543210"
    )

    # Verify claimant
    is_valid, errors, warnings = system.verify_claimant(claimant)
    print(f"\nClaimant Validation:")
    print(f"  Valid: {is_valid}")
    if errors:
        print(f"  Errors: {errors}")
    if warnings:
        print(f"  Warnings: {warnings}")

    # Example: Create a claim
    claim = system.create_claim(
        settlement_name="Example FTC Settlement 2024",
        settlement_program=SettlementProgram.CONSUMER_REFUND,
        claimant=claimant
    )

    print(f"\nClaim created: {claim.claim_id}")

    # Example: Add claim items
    item1 = ClaimItem(
        item_id="ITEM-001",
        description="Product purchase that was fraudulent",
        amount=99.99,
        transaction_date=datetime.date(2024, 1, 15),
        merchant_name="Example Company",
        payment_method="Credit Card"
    )

    system.add_claim_item(claim.claim_id, item1)
    print(f"Added claim item: {item1.item_id} - ${item1.amount:,.2f}")

    # Example: Generate checklist
    print("\n" + "="*80)
    print("SUBMISSION CHECKLIST")
    print("="*80)
    print(system.generate_submission_checklist(claim))

    print("\n" + system.generate_summary_report())

    return system


if __name__ == "__main__":
    system = main()
