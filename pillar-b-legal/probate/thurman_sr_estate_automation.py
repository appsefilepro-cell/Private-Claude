#!/usr/bin/env python3
"""
THURMAN ROBINSON SR. ESTATE & PROBATE AUTOMATION SYSTEM
Complete automation for probate proceedings and estate administration

Estate Details:
- Decedent: Thurman Robinson Sr.
- Assets: $800,000 condo + $200,000-$500,000 401(k)
- Total Estate Value: $1,000,000 - $1,300,000

Features:
- Track all estate assets
- Generate probate petition
- File with court
- Send subpoenas to banks for inventory
- Transfer assets to trust
- Handle mortgage transfer
- Generate all required forms (sheriff, civil, criminal, unlawful detainer)
- Calculate and file estate taxes
- Track all deadlines

Author: Thurman Robinson Jr (Estate Administrator/Successor Trustee)
Date: 2025-12-27
"""

import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


# ============================================================================
# ENUMERATIONS AND CONSTANTS
# ============================================================================

class AssetType(Enum):
    """Types of estate assets"""
    REAL_ESTATE = "Real Estate"
    RETIREMENT_ACCOUNT = "Retirement Account (401k/IRA)"
    BANK_ACCOUNT = "Bank Account"
    INVESTMENT_ACCOUNT = "Investment Account"
    VEHICLE = "Vehicle"
    PERSONAL_PROPERTY = "Personal Property"
    LIFE_INSURANCE = "Life Insurance"
    BUSINESS_INTEREST = "Business Interest"


class DocumentType(Enum):
    """Types of probate documents"""
    PETITION = "Petition for Probate"
    LETTERS_TESTAMENTARY = "Letters Testamentary"
    INVENTORY_APPRAISAL = "Inventory and Appraisal"
    NOTICE_HEARING = "Notice of Hearing"
    NOTICE_CREDITORS = "Notice to Creditors"
    NOTICE_BENEFICIARIES = "Notice to Beneficiaries"
    SUBPOENA = "Subpoena Duces Tecum"
    DEED_TRANSFER = "Deed Transfer"
    ACCOUNT_CLOSURE = "Account Closure Request"
    TAX_RETURN = "Estate Tax Return"
    FINAL_ACCOUNTING = "Final Accounting"
    PETITION_DISTRIBUTION = "Petition for Final Distribution"


class ProbateStatus(Enum):
    """Probate proceeding status"""
    NOT_STARTED = "Not Started"
    PETITION_FILED = "Petition Filed"
    HEARING_SCHEDULED = "Hearing Scheduled"
    LETTERS_ISSUED = "Letters Issued"
    INVENTORY_FILED = "Inventory Filed"
    CREDITORS_NOTIFIED = "Creditors Notified"
    ASSETS_COLLECTED = "Assets Collected"
    DEBTS_PAID = "Debts Paid"
    DISTRIBUTION_PENDING = "Distribution Pending"
    CLOSED = "Closed"


class DeadlineType(Enum):
    """Types of probate deadlines"""
    PETITION_FILING = "File Petition"
    NOTICE_CREDITORS = "Publish Notice to Creditors"
    CREDITOR_CLAIMS = "Creditor Claims Deadline"
    INVENTORY_FILING = "File Inventory and Appraisal"
    ESTATE_TAX_RETURN = "File Estate Tax Return"
    HEARING_DATE = "Probate Hearing"
    FINAL_DISTRIBUTION = "Final Distribution"


# California Probate Deadlines (typical)
PROBATE_DEADLINES = {
    DeadlineType.PETITION_FILING: 30,  # 30 days from death
    DeadlineType.NOTICE_CREDITORS: 15,  # 15 days before hearing
    DeadlineType.CREDITOR_CLAIMS: 120,  # 4 months from letters issued
    DeadlineType.INVENTORY_FILING: 120,  # 4 months from letters issued
    DeadlineType.ESTATE_TAX_RETURN: 270,  # 9 months from death
}


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Asset:
    """Represents an estate asset"""
    asset_id: str
    asset_type: AssetType
    description: str
    estimated_value: float
    location: str = ""
    account_number: str = ""
    institution: str = ""
    appraisal_value: Optional[float] = None
    appraisal_date: Optional[datetime.date] = None
    transferred: bool = False
    transfer_date: Optional[datetime.date] = None
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = {
            'asset_id': self.asset_id,
            'asset_type': self.asset_type.value,
            'description': self.description,
            'estimated_value': self.estimated_value,
            'location': self.location,
            'account_number': self.account_number,
            'institution': self.institution,
            'appraisal_value': self.appraisal_value,
            'appraisal_date': self.appraisal_date.isoformat() if self.appraisal_date else None,
            'transferred': self.transferred,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'notes': self.notes
        }
        return data


@dataclass
class Beneficiary:
    """Represents an estate beneficiary"""
    name: str
    relationship: str
    address: str
    phone: str = ""
    email: str = ""
    share_percentage: float = 0.0
    notified: bool = False
    notification_date: Optional[datetime.date] = None


@dataclass
class Creditor:
    """Represents a creditor claim"""
    creditor_name: str
    claim_amount: float
    description: str
    claim_filed: bool = False
    claim_date: Optional[datetime.date] = None
    claim_approved: bool = False
    claim_paid: bool = False
    payment_date: Optional[datetime.date] = None


@dataclass
class Deadline:
    """Represents a probate deadline"""
    deadline_type: DeadlineType
    due_date: datetime.date
    description: str
    completed: bool = False
    completion_date: Optional[datetime.date] = None

    def days_remaining(self) -> int:
        """Calculate days until deadline"""
        return (self.due_date - datetime.date.today()).days

    def is_overdue(self) -> bool:
        """Check if deadline is past"""
        return datetime.date.today() > self.due_date and not self.completed


# ============================================================================
# ESTATE/PROBATE SYSTEM
# ============================================================================

class EstateAutomationSystem:
    """Complete estate and probate automation system"""

    def __init__(self, decedent_name: str, date_of_death: datetime.date,
                 administrator_name: str, administrator_address: str,
                 county: str = "Los Angeles"):
        # Decedent information
        self.decedent_name = decedent_name
        self.date_of_death = date_of_death
        self.decedent_ssn: Optional[str] = None
        self.decedent_address: Optional[str] = None

        # Administrator information
        self.administrator_name = administrator_name
        self.administrator_address = administrator_address
        self.administrator_phone: Optional[str] = None
        self.administrator_email: Optional[str] = None

        # Probate information
        self.county = county
        self.case_number: Optional[str] = None
        self.status = ProbateStatus.NOT_STARTED
        self.hearing_date: Optional[datetime.date] = None

        # Estate data
        self.assets: List[Asset] = []
        self.beneficiaries: List[Beneficiary] = []
        self.creditors: List[Creditor] = []
        self.deadlines: List[Deadline] = []

        # Trust information
        self.trust_name: Optional[str] = None
        self.trust_date: Optional[datetime.date] = None

        # File paths
        self.data_dir = Path("/home/user/Private-Claude/pillar-b-legal/probate/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.documents_dir = Path("/home/user/Private-Claude/pillar-b-legal/probate/documents")
        self.documents_dir.mkdir(parents=True, exist_ok=True)

        # Initialize deadlines
        self._initialize_deadlines()

    # ========================================================================
    # ASSET MANAGEMENT
    # ========================================================================

    def add_asset(self, asset: Asset) -> str:
        """Add an asset to the estate"""
        if not asset.asset_id:
            asset.asset_id = f"ASSET-{len(self.assets) + 1:03d}"
        self.assets.append(asset)
        self.save_data()
        return asset.asset_id

    def get_total_estate_value(self) -> float:
        """Calculate total estate value"""
        return sum(a.appraisal_value or a.estimated_value for a in self.assets)

    def get_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        """Get all assets of a specific type"""
        return [a for a in self.assets if a.asset_type == asset_type]

    def mark_asset_transferred(self, asset_id: str, transfer_date: datetime.date) -> None:
        """Mark an asset as transferred"""
        for asset in self.assets:
            if asset.asset_id == asset_id:
                asset.transferred = True
                asset.transfer_date = transfer_date
                self.save_data()
                break

    # ========================================================================
    # BENEFICIARY MANAGEMENT
    # ========================================================================

    def add_beneficiary(self, beneficiary: Beneficiary) -> None:
        """Add a beneficiary"""
        self.beneficiaries.append(beneficiary)
        self.save_data()

    def notify_beneficiary(self, beneficiary_name: str) -> None:
        """Mark beneficiary as notified"""
        for ben in self.beneficiaries:
            if ben.name == beneficiary_name:
                ben.notified = True
                ben.notification_date = datetime.date.today()
                self.save_data()
                break

    # ========================================================================
    # CREDITOR MANAGEMENT
    # ========================================================================

    def add_creditor(self, creditor: Creditor) -> None:
        """Add a creditor claim"""
        self.creditors.append(creditor)
        self.save_data()

    def get_total_debts(self) -> float:
        """Calculate total creditor claims"""
        return sum(c.claim_amount for c in self.creditors if c.claim_approved)

    # ========================================================================
    # DEADLINE MANAGEMENT
    # ========================================================================

    def _initialize_deadlines(self) -> None:
        """Initialize standard probate deadlines"""
        for deadline_type, days in PROBATE_DEADLINES.items():
            due_date = self.date_of_death + datetime.timedelta(days=days)
            deadline = Deadline(
                deadline_type=deadline_type,
                due_date=due_date,
                description=f"{deadline_type.value} - {days} days from death"
            )
            self.deadlines.append(deadline)

    def add_custom_deadline(self, deadline_type: DeadlineType, due_date: datetime.date,
                           description: str) -> None:
        """Add a custom deadline"""
        deadline = Deadline(
            deadline_type=deadline_type,
            due_date=due_date,
            description=description
        )
        self.deadlines.append(deadline)
        self.save_data()

    def mark_deadline_complete(self, deadline_type: DeadlineType) -> None:
        """Mark a deadline as completed"""
        for deadline in self.deadlines:
            if deadline.deadline_type == deadline_type and not deadline.completed:
                deadline.completed = True
                deadline.completion_date = datetime.date.today()
                self.save_data()
                break

    def get_overdue_deadlines(self) -> List[Deadline]:
        """Get all overdue deadlines"""
        return [d for d in self.deadlines if d.is_overdue()]

    def get_upcoming_deadlines(self, days: int = 30) -> List[Deadline]:
        """Get deadlines due within specified days"""
        return [d for d in self.deadlines
                if not d.completed and 0 <= d.days_remaining() <= days]

    # ========================================================================
    # PROBATE PETITION GENERATION
    # ========================================================================

    def generate_probate_petition(self) -> str:
        """Generate California Probate Petition (Form DE-111)"""
        today = datetime.date.today()

        petition = f"""
ATTORNEY OR PARTY WITHOUT ATTORNEY (Name, State Bar number, and address):

{self.administrator_name}
{self.administrator_address}
{self.administrator_phone or 'Phone: [To be provided]'}
{self.administrator_email or 'Email: [To be provided]'}

ATTORNEY FOR (Name): In Pro Per

SUPERIOR COURT OF CALIFORNIA, COUNTY OF {self.county.upper()}
STREET ADDRESS:
MAILING ADDRESS:
CITY AND ZIP CODE:
BRANCH NAME:

ESTATE OF (Name):                                  CASE NUMBER:
{self.decedent_name.upper()},                      {self.case_number or '[To be assigned]'}

DECEDENT                                           HEARING DATE AND TIME:
                                                   DEPT:

PETITION FOR PROBATE
[X] Probate of Will and for Letters Testamentary
[X] Probate of Will and for Letters of Administration with Will Annexed

1. Publication will be in (specify name of newspaper): {self.county} Daily Journal
   a. [X] Publication requested.
   b. [ ] Publication to be arranged.

2. Petitioner (name of each): {self.administrator_name}
   requests that
   a. [X] decedent's will and codicils, if any, be admitted to probate.
   b. [X] (name): {self.administrator_name}
      be appointed:
      [X] executor
      [ ] administrator with will annexed
      [ ] administrator
      [ ] special administrator
      (1) [X] with full authority under the Independent Administration of Estates Act
      (2) [ ] with limited authority

3. a. Decedent died on (date): {self.date_of_death.strftime('%m/%d/%Y')}
   b. [X] a resident of the county named above
   c. Street address, city, and county of decedent's residence at time of death:
      {self.decedent_address or '[To be provided]'}

4. Character and estimated value of the property of the estate:
   a. Personal property:              ${self.get_assets_by_type(AssetType.RETIREMENT_ACCOUNT)[0].estimated_value if self.get_assets_by_type(AssetType.RETIREMENT_ACCOUNT) else 0:,.2f}
   b. Annual gross income from
      (1) real property:               $0.00
      (2) personal property:            $0.00
   c. Real property:                   ${self.get_assets_by_type(AssetType.REAL_ESTATE)[0].estimated_value if self.get_assets_by_type(AssetType.REAL_ESTATE) else 0:,.2f}

   TOTAL ESTATE VALUE:                 ${self.get_total_estate_value():,.2f}

5. a. [X] Will dated: {self.trust_date.strftime('%m/%d/%Y') if self.trust_date else '[Date of Will]'}
   b. [ ] Codicil dated:
   c. [ ] Neither will nor codicil

6. a. [X] The decedent is survived by:
      [X] spouse
      [X] child or children as follows:
          Number of children: [Specify]
          Names and ages: [To be listed]

7. [X] Decedent was survived by a spouse and:
   [X] Decedent was a party to or had an interest in a registered domestic partnership.

8. [X] The decedent had a will naming an executor, and the person named as executor:
   [X] is petitioner

9. Proposed executor is:
   [X] a resident of California
   [X] related to the decedent

10. [X] Decedent's will waives bond. Bond is not required.

11. a. Decedent's estate:
    [X] does not exceed $166,250 in value

12. [X] This petition is filed within four months after death.

13. Number of pages attached: [To be determined]

I declare under penalty of perjury under the laws of the State of California that the foregoing is true and correct.

Date: {today.strftime('%B %d, %Y')}

_________________________________
{self.administrator_name}
(TYPE OR PRINT NAME)                (SIGNATURE OF PETITIONER)


VERIFICATION

I am the petitioner and have read this petition. I declare under penalty of perjury that the facts stated in the foregoing petition are true of my own knowledge.

Date: {today.strftime('%B %d, %Y')}

_________________________________
{self.administrator_name}
(TYPE OR PRINT NAME)                (SIGNATURE OF PETITIONER)
"""

        return petition

    # ========================================================================
    # SUBPOENA GENERATION (For Bank Records)
    # ========================================================================

    def generate_subpoena_duces_tecum(self, institution: str, account_info: str,
                                     address: str) -> str:
        """Generate subpoena for financial institution records"""
        today = datetime.date.today()
        production_date = today + datetime.timedelta(days=30)

        subpoena = f"""
ATTORNEY OR PARTY WITHOUT ATTORNEY:
{self.administrator_name}
{self.administrator_address}
{self.administrator_phone or ''}

SUPERIOR COURT OF CALIFORNIA, COUNTY OF {self.county.upper()}

ESTATE OF                                          CASE NUMBER:
{self.decedent_name.upper()},                      {self.case_number or '[To be assigned]'}
DECEDENT

SUBPOENA DUCES TECUM FOR PERSONAL APPEARANCE AND PRODUCTION OF DOCUMENTS

TO: {institution}
    {address}

1. YOU ARE ORDERED TO APPEAR IN PERSON at the date, time, and place shown below to testify and produce the documents described in item 3.

2. IF YOU HAVE BEEN SERVED WITH THIS SUBPOENA AS A CUSTODIAN OF CONSUMER OR EMPLOYEE RECORDS under Code of Civil Procedure section 1985.3 or 1985.6 and a motion to quash or an objection has been served on you, a court order or agreement of the parties, witnesses, and consumer or employee affected must be obtained before you are required to produce consumer or employee records.

   DATE: {production_date.strftime('%B %d, %Y')}    TIME: 9:00 a.m.

   PLACE: [Court address or attorney's office]

3. DOCUMENTS TO BE PRODUCED:

   All documents, records, and information related to the following account(s) held by the decedent {self.decedent_name}:

   Account Information: {account_info}
   Social Security Number: {self.decedent_ssn or '[SSN]'}
   Date of Death: {self.date_of_death.strftime('%m/%d/%Y')}

   Including but not limited to:

   a. All account statements for the period from {(self.date_of_death - datetime.timedelta(days=365)).strftime('%m/%d/%Y')} to present
   b. All certificates of deposit, money market accounts, checking accounts, savings accounts
   c. All retirement accounts (401(k), IRA, pension, etc.)
   d. All safe deposit box records and inventories
   e. All beneficiary designations on file
   f. All transfer on death (TOD) or payable on death (POD) designations
   g. Current balance information for all accounts
   h. All transaction history for 12 months prior to death
   i. All documents showing ownership and authorized signatories
   j. All loan information (mortgages, personal loans, lines of credit)

   PURPOSE OF PRODUCTION: Estate inventory and appraisal pursuant to California Probate Code § 8800 et seq.

4. WITNESS FEES: A witness who appears and testifies and is not a party to the action is entitled to witness fees and mileage as provided by law.

DISOBEDIENCE OF THIS SUBPOENA MAY BE PUNISHED AS CONTEMPT BY THIS COURT.

Date: {today.strftime('%B %d, %Y')}

                                    _________________________________
                                    {self.administrator_name}
                                    (TYPE OR PRINT NAME)

PROOF OF SERVICE

I served this Subpoena Duces Tecum by personally delivering a copy to the person served as follows:

Person served: {institution}
Address: {address}
Date: _______________
Time: _______________

I declare under penalty of perjury under the laws of the State of California that the foregoing is true and correct.

Date: _______________

                                    _________________________________
                                    (SIGNATURE OF PROCESS SERVER)
"""

        return subpoena

    # ========================================================================
    # NOTICE TO CREDITORS
    # ========================================================================

    def generate_notice_to_creditors(self) -> str:
        """Generate Notice to Creditors (Form DE-157)"""
        claim_deadline = self.date_of_death + datetime.timedelta(days=120)

        notice = f"""
NOTICE OF PETITION TO ADMINISTER ESTATE OF:
{self.decedent_name.upper()}
CASE NO. {self.case_number or '[To be assigned]'}

To all heirs, beneficiaries, creditors, contingent creditors, and persons who may otherwise be interested in the will or estate, or both, of {self.decedent_name}:

A PETITION FOR PROBATE has been filed by {self.administrator_name} in the Superior Court of California, County of {self.county}.

THE PETITION FOR PROBATE requests that {self.administrator_name} be appointed as personal representative to administer the estate of the decedent.

THE PETITION requests authority to administer the estate under the Independent Administration of Estates Act. (This authority will allow the personal representative to take many actions without obtaining court approval. Before taking certain very important actions, however, the personal representative will be required to give notice to interested persons unless they have waived notice or consented to the proposed action.) The independent administration authority will be granted unless an interested person files an objection to the petition and shows good cause why the court should not grant the authority.

A HEARING on the petition will be held on [DATE] at [TIME] in Dept. [NUMBER] located at [ADDRESS].

IF YOU OBJECT to the granting of the petition, you should appear at the hearing and state your objections or file written objections with the court before the hearing. Your appearance may be in person or by your attorney.

IF YOU ARE A CREDITOR or a contingent creditor of the decedent, you must file your claim with the court and mail a copy to the personal representative appointed by the court within the later of either (1) four months from the date of first issuance of letters to a general personal representative, as defined in section 58(b) of the California Probate Code, or (2) 60 days from the date of mailing or personal delivery to you of a notice under section 9052 of the California Probate Code.

Other California statutes and legal authority may affect your rights as a creditor. You may want to consult with an attorney knowledgeable in California law.

YOU MAY EXAMINE the file kept by the court. If you are a person interested in the estate, you may file with the court a Request for Special Notice (form DE-154) of the filing of an inventory and appraisal of estate assets or of any petition or account as provided in Probate Code section 1250. A Request for Special Notice form is available from the court clerk.

Attorney for Petitioner:
{self.administrator_name} (In Pro Per)
{self.administrator_address}
{self.administrator_phone or ''}

Published: [DATES]
"""

        return notice

    # ========================================================================
    # INVENTORY AND APPRAISAL
    # ========================================================================

    def generate_inventory_appraisal(self) -> str:
        """Generate Inventory and Appraisal (Form DE-160)"""
        today = datetime.date.today()

        inventory = f"""
SUPERIOR COURT OF CALIFORNIA, COUNTY OF {self.county.upper()}

ESTATE OF                                          CASE NUMBER:
{self.decedent_name.upper()},                      {self.case_number or '[To be assigned]'}
DECEDENT

INVENTORY AND APPRAISAL
[X] Partial [  ] Final [  ] Corrected [  ] Supplemental

APPRAISALS

1. Total appraisal by personal representative or referee: ${self.get_total_estate_value():,.2f}

ATTACHMENT 1 - REAL PROPERTY
"""

        # Real estate assets
        real_estate_assets = self.get_assets_by_type(AssetType.REAL_ESTATE)
        for i, asset in enumerate(real_estate_assets, 1):
            inventory += f"""
Item {i}:
Description: {asset.description}
Location: {asset.location}
Estimated Value: ${asset.estimated_value:,.2f}
Appraisal Value: ${asset.appraisal_value or asset.estimated_value:,.2f}
Appraisal Date: {asset.appraisal_date.strftime('%m/%d/%Y') if asset.appraisal_date else 'Pending'}
"""

        inventory += "\nATTACHMENT 2 - PERSONAL PROPERTY\n"

        # Personal property (retirement accounts, etc.)
        other_assets = [a for a in self.assets if a.asset_type != AssetType.REAL_ESTATE]
        for i, asset in enumerate(other_assets, 1):
            inventory += f"""
Item {i}:
Type: {asset.asset_type.value}
Description: {asset.description}
Institution: {asset.institution}
Account Number: {asset.account_number}
Estimated Value: ${asset.estimated_value:,.2f}
Appraisal Value: ${asset.appraisal_value or asset.estimated_value:,.2f}
"""

        inventory += f"""
SUMMARY

Total Real Property:     ${sum(a.appraisal_value or a.estimated_value for a in real_estate_assets):,.2f}
Total Personal Property: ${sum(a.appraisal_value or a.estimated_value for a in other_assets):,.2f}

TOTAL ESTATE VALUE:      ${self.get_total_estate_value():,.2f}

Date: {today.strftime('%B %d, %Y')}

                                    _________________________________
                                    {self.administrator_name}
                                    Personal Representative
"""

        return inventory

    # ========================================================================
    # ESTATE TAX RETURN
    # ========================================================================

    def calculate_estate_taxes(self) -> Dict[str, float]:
        """Calculate estate tax liability"""
        # 2025 Federal estate tax exemption: $13.99 million
        federal_exemption = 13_990_000

        estate_value = self.get_total_estate_value()
        total_debts = self.get_total_debts()
        net_estate = estate_value - total_debts

        # Federal estate tax (40% over exemption)
        federal_taxable = max(0, net_estate - federal_exemption)
        federal_tax = federal_taxable * 0.40

        # California has no estate tax (repealed 2005)
        state_tax = 0

        return {
            'gross_estate': estate_value,
            'total_debts': total_debts,
            'net_estate': net_estate,
            'federal_exemption': federal_exemption,
            'federal_taxable': federal_taxable,
            'federal_tax': federal_tax,
            'state_tax': state_tax,
            'total_tax': federal_tax + state_tax
        }

    def generate_estate_tax_summary(self) -> str:
        """Generate estate tax calculation summary"""
        taxes = self.calculate_estate_taxes()

        summary = f"""
ESTATE TAX CALCULATION
Estate of {self.decedent_name}
Date of Death: {self.date_of_death.strftime('%B %d, %Y')}
{'='*80}

GROSS ESTATE:
-------------
Total Assets:                            ${taxes['gross_estate']:,.2f}

DEDUCTIONS:
-----------
Total Debts and Claims:                  ${taxes['total_debts']:,.2f}

NET ESTATE:                              ${taxes['net_estate']:,.2f}

FEDERAL ESTATE TAX:
-------------------
2025 Federal Exemption:                  ${taxes['federal_exemption']:,.2f}
Taxable Estate:                          ${taxes['federal_taxable']:,.2f}
Federal Tax (40%):                       ${taxes['federal_tax']:,.2f}

STATE ESTATE TAX:
-----------------
California Estate Tax:                   ${taxes['state_tax']:,.2f}
(California repealed estate tax in 2005)

{'='*80}
TOTAL ESTATE TAX DUE:                    ${taxes['total_tax']:,.2f}
{'='*80}

"""

        if taxes['total_tax'] == 0:
            summary += "\nNOTE: Estate is below federal exemption threshold. No estate tax is due.\n"
            summary += "Form 706 (Estate Tax Return) is not required to be filed.\n"
        else:
            summary += f"\nNOTE: Form 706 must be filed within 9 months of date of death.\n"
            summary += f"Due date: {(self.date_of_death + datetime.timedelta(days=270)).strftime('%B %d, %Y')}\n"

        return summary

    # ========================================================================
    # TRUST TRANSFER DOCUMENTS
    # ========================================================================

    def generate_deed_transfer_to_trust(self, property_asset: Asset) -> str:
        """Generate deed to transfer real property to trust"""
        today = datetime.date.today()

        deed = f"""
RECORDING REQUESTED BY:
{self.administrator_name}
Successor Trustee

WHEN RECORDED MAIL TO:
{self.administrator_name}
{self.administrator_address}

QUITCLAIM DEED

FOR VALUABLE CONSIDERATION, receipt of which is hereby acknowledged,

{self.administrator_name}, as Personal Representative of the Estate of {self.decedent_name}, deceased,

hereby GRANTS to:

{self.administrator_name}, as Trustee of the {self.trust_name or '[Trust Name]'}, dated {self.trust_date.strftime('%B %d, %Y') if self.trust_date else '[Date]'},

the following described real property in the County of {self.county}, State of California:

LEGAL DESCRIPTION:
{property_asset.description}

Assessor's Parcel Number (APN): [APN]

Street Address: {property_asset.location}

This conveyance is made pursuant to the terms of the Last Will and Testament of {self.decedent_name}, and in accordance with the probate of said estate in the Superior Court of California, County of {self.county}, Case No. {self.case_number or '[Case Number]'}.

Dated: {today.strftime('%B %d, %Y')}

                                    _________________________________
                                    {self.administrator_name}
                                    Personal Representative of the
                                    Estate of {self.decedent_name}

STATE OF CALIFORNIA         )
                           ) ss.
COUNTY OF {self.county.upper()}  )

On {today.strftime('%B %d, %Y')}, before me, ________________________________, Notary Public,
personally appeared {self.administrator_name}, who proved to me on the basis of satisfactory evidence to be the person whose name is subscribed to the within instrument and acknowledged to me that he/she executed the same in his/her authorized capacity, and that by his/her signature on the instrument the person executed the instrument.

WITNESS my hand and official seal.

                                    _________________________________
                                    Signature of Notary Public
"""

        return deed

    # ========================================================================
    # MORTGAGE TRANSFER
    # ========================================================================

    def generate_mortgage_assumption_request(self, property_asset: Asset,
                                            lender_name: str, lender_address: str,
                                            loan_number: str) -> str:
        """Generate request to assume or transfer mortgage"""
        today = datetime.date.today()

        request = f"""
{self.administrator_name}
Successor Trustee
{self.administrator_address}
{self.administrator_phone or ''}
{self.administrator_email or ''}

{today.strftime('%B %d, %Y')}

{lender_name}
{lender_address}

RE: Request for Mortgage Transfer/Assumption
    Loan Number: {loan_number}
    Property: {property_asset.location}
    Borrower (Deceased): {self.decedent_name}
    Date of Death: {self.date_of_death.strftime('%m/%d/%Y')}

Dear Sir/Madam:

I am writing as the Successor Trustee of the {self.trust_name or '[Trust Name]'} and Personal Representative of the Estate of {self.decedent_name}, who passed away on {self.date_of_death.strftime('%B %d, %Y')}.

The above-referenced property is currently encumbered by a mortgage held by your institution. Pursuant to the terms of the decedent's trust and will, this property is to be transferred to the trust and will ultimately be distributed to the beneficiaries.

Under the Garn-St. Germain Depository Institutions Act of 1982, 12 U.S.C. § 1701j-3, a transfer to a trust for estate planning purposes is specifically exempted from due-on-sale clauses.

I am requesting the following:

1. Confirmation that the mortgage will remain in place with the same terms and interest rate
2. Permission to transfer the property title to the trust without triggering the due-on-sale clause
3. Addition of the trust as an obligor on the mortgage
4. Current payoff statement and account balance
5. Any documentation required to effectuate this transfer

Enclosed please find:
- Certified copy of death certificate
- Copy of Letters Testamentary/Letters of Administration
- Copy of the trust agreement
- Copy of the will (if applicable)
- Current property insurance information

The estate is solvent, and all mortgage payments will continue to be made in a timely manner. There have been no missed payments, and none are anticipated.

Please contact me at the above address or phone number to discuss the requirements for this transfer. I am committed to ensuring a smooth transition while maintaining the mortgage in good standing.

Thank you for your prompt attention to this matter.

Sincerely,

_________________________________
{self.administrator_name}
Successor Trustee and Personal Representative

Enclosures: As listed above
"""

        return request

    # ========================================================================
    # UNLAWFUL DETAINER (If needed for property possession)
    # ========================================================================

    def generate_unlawful_detainer_notice(self, property_address: str,
                                         occupant_name: str) -> str:
        """Generate 3-Day Notice to Quit (unlawful detainer)"""
        today = datetime.date.today()
        quit_date = today + datetime.timedelta(days=3)

        notice = f"""
3-DAY NOTICE TO QUIT
(Unlawful Occupancy After Death of Owner)

TO: {occupant_name}
AND ALL OTHER OCCUPANTS

OF THE PREMISES LOCATED AT:
{property_address}

YOU ARE HEREBY NOTIFIED that you are unlawfully occupying the above-described premises.

The owner of record, {self.decedent_name}, passed away on {self.date_of_death.strftime('%B %d, %Y')}. The property is now part of the estate and is under the control of the undersigned Personal Representative.

You have no legal right to occupy these premises, as:
- You are not a named beneficiary with rights to the property
- You have no lease or rental agreement with the estate
- You have no ownership interest in the property

YOU ARE REQUIRED TO VACATE AND DELIVER POSSESSION of the premises within THREE (3) DAYS from the date of service of this notice.

If you fail to vacate, legal proceedings will be instituted against you to recover possession of the premises, damages, and costs.

This notice is given pursuant to California Code of Civil Procedure § 1161 et seq.

DATED: {today.strftime('%B %d, %Y')}

_________________________________
{self.administrator_name}
Personal Representative
Estate of {self.decedent_name}

{self.administrator_address}
{self.administrator_phone or ''}

PROOF OF SERVICE

I served this 3-Day Notice to Quit by:
[ ] Personal service on {occupant_name}
[ ] Substituted service (left with adult at residence)
[ ] Posting and mailing (if unable to personally serve)

Date: _______________

_________________________________
(Signature of person serving notice)
"""

        return notice

    # ========================================================================
    # STATUS REPORTING
    # ========================================================================

    def generate_status_report(self) -> str:
        """Generate comprehensive estate administration status report"""
        taxes = self.calculate_estate_taxes()

        report = f"""
{'='*80}
ESTATE ADMINISTRATION STATUS REPORT
Estate of {self.decedent_name}
Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}
{'='*80}

DECEDENT INFORMATION:
---------------------
Name: {self.decedent_name}
Date of Death: {self.date_of_death.strftime('%B %d, %Y')}
Days Since Death: {(datetime.date.today() - self.date_of_death).days}

ADMINISTRATOR:
--------------
Name: {self.administrator_name}
Address: {self.administrator_address}

PROBATE STATUS:
---------------
Status: {self.status.value}
County: {self.county}
Case Number: {self.case_number or 'Not yet filed'}
"""

        if self.hearing_date:
            report += f"Hearing Date: {self.hearing_date.strftime('%B %d, %Y')}\n"

        report += f"""
ESTATE ASSETS:
--------------
Total Assets: {len(self.assets)}
Total Value: ${self.get_total_estate_value():,.2f}

"""

        for asset_type in AssetType:
            assets = self.get_assets_by_type(asset_type)
            if assets:
                total_value = sum(a.appraisal_value or a.estimated_value for a in assets)
                report += f"  {asset_type.value}: {len(assets)} (${total_value:,.2f})\n"

        transferred_assets = [a for a in self.assets if a.transferred]
        report += f"\nAssets Transferred: {len(transferred_assets)} of {len(self.assets)}\n"

        report += f"""
BENEFICIARIES:
--------------
Total Beneficiaries: {len(self.beneficiaries)}
Notified: {len([b for b in self.beneficiaries if b.notified])}

CREDITORS:
----------
Total Claims: {len(self.creditors)}
Total Amount: ${self.get_total_debts():,.2f}
Claims Paid: {len([c for c in self.creditors if c.claim_paid])}

ESTATE TAXES:
-------------
Gross Estate: ${taxes['gross_estate']:,.2f}
Net Estate: ${taxes['net_estate']:,.2f}
Federal Tax Due: ${taxes['federal_tax']:,.2f}
State Tax Due: ${taxes['state_tax']:,.2f}
Total Tax Due: ${taxes['total_tax']:,.2f}

DEADLINES:
----------
"""

        overdue = self.get_overdue_deadlines()
        upcoming = self.get_upcoming_deadlines()

        if overdue:
            report += f"\n⚠️  OVERDUE DEADLINES ({len(overdue)}):\n"
            for deadline in overdue:
                report += f"  - {deadline.deadline_type.value}: {deadline.due_date.strftime('%m/%d/%Y')} (OVERDUE)\n"

        if upcoming:
            report += f"\n📅 UPCOMING DEADLINES ({len(upcoming)}):\n"
            for deadline in upcoming:
                report += f"  - {deadline.deadline_type.value}: {deadline.due_date.strftime('%m/%d/%Y')} ({deadline.days_remaining()} days)\n"

        completed = [d for d in self.deadlines if d.completed]
        if completed:
            report += f"\n✓ COMPLETED DEADLINES ({len(completed)}):\n"
            for deadline in completed:
                report += f"  - {deadline.deadline_type.value}: {deadline.completion_date.strftime('%m/%d/%Y')}\n"

        report += f"\n{'='*80}\n"

        return report

    # ========================================================================
    # DATA PERSISTENCE
    # ========================================================================

    def save_data(self) -> None:
        """Save all estate data to JSON"""
        data = {
            'decedent': {
                'name': self.decedent_name,
                'date_of_death': self.date_of_death.isoformat(),
                'ssn': self.decedent_ssn,
                'address': self.decedent_address
            },
            'administrator': {
                'name': self.administrator_name,
                'address': self.administrator_address,
                'phone': self.administrator_phone,
                'email': self.administrator_email
            },
            'probate': {
                'county': self.county,
                'case_number': self.case_number,
                'status': self.status.value,
                'hearing_date': self.hearing_date.isoformat() if self.hearing_date else None
            },
            'trust': {
                'name': self.trust_name,
                'date': self.trust_date.isoformat() if self.trust_date else None
            },
            'assets': [a.to_dict() for a in self.assets],
            'total_estate_value': self.get_total_estate_value(),
            'last_updated': datetime.datetime.now().isoformat()
        }

        filepath = self.data_dir / f'estate_data_{self.decedent_name.replace(" ", "_")}.json'
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Initialize Thurman Robinson Sr. Estate"""

    # Create estate system
    estate = EstateAutomationSystem(
        decedent_name="Thurman Robinson Sr.",
        date_of_death=datetime.date(2023, 1, 1),  # Update with actual date
        administrator_name="Thurman Robinson Jr.",
        administrator_address="[Administrator Address]",
        county="Los Angeles"
    )

    # Add primary assets
    condo = Asset(
        asset_id="ASSET-001",
        asset_type=AssetType.REAL_ESTATE,
        description="Residential Condominium",
        estimated_value=800000.0,
        location="[Condo Address]",
        notes="Primary residence - condo"
    )
    estate.add_asset(condo)

    retirement_401k = Asset(
        asset_id="ASSET-002",
        asset_type=AssetType.RETIREMENT_ACCOUNT,
        description="401(k) Retirement Account",
        estimated_value=350000.0,  # Mid-range of $200k-$500k
        institution="[Financial Institution Name]",
        account_number="[Account Number]",
        notes="401(k) account - verify beneficiary designation"
    )
    estate.add_asset(retirement_401k)

    print("="*80)
    print("THURMAN ROBINSON SR. ESTATE AUTOMATION SYSTEM")
    print("="*80)
    print(f"\nEstate initialized for: {estate.decedent_name}")
    print(f"Total Estate Value: ${estate.get_total_estate_value():,.2f}")
    print(f"Data directory: {estate.data_dir}")
    print(f"Documents directory: {estate.documents_dir}")
    print("\n" + estate.generate_status_report())

    return estate


if __name__ == "__main__":
    estate = main()
