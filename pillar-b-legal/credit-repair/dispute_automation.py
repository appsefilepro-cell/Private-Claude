"""
CREDIT REPAIR AUTOMATION - 3-BUREAU DISPUTE SYSTEM
Automates credit disputes for Equifax, Experian, TransUnion
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import sqlite3


@dataclass
class DisputeItem:
    """Represents a single item to dispute"""
    account_name: str
    account_number: str
    dispute_reason: str
    description: str
    bureau: str  # 'Equifax', 'Experian', or 'TransUnion'
    status: str = 'pending'  # pending, sent, resolved, escalated
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class CreditDisputeAutomation:
    """Automate credit repair disputes across all 3 bureaus"""

    BUREAU_ADDRESSES = {
        'Equifax': {
            'address': 'Equifax Information Services LLC\nP.O. Box 740256\nAtlanta, GA 30374',
            'online': 'https://www.equifax.com/personal/credit-report-services/credit-dispute/'
        },
        'Experian': {
            'address': 'Experian\nP.O. Box 4500\nAllen, TX 75013',
            'online': 'https://www.experian.com/disputes/main.html'
        },
        'TransUnion': {
            'address': 'TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016',
            'online': 'https://dispute.transunion.com/'
        }
    }

    def __init__(self, db_path: str = "credit_disputes.db"):
        """Initialize dispute automation system"""
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Create database for tracking disputes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disputes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_name TEXT,
                account_number TEXT,
                dispute_reason TEXT,
                description TEXT,
                bureau TEXT,
                status TEXT,
                created_at TIMESTAMP,
                sent_at TIMESTAMP,
                response_date TIMESTAMP,
                resolution TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cfpb_complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispute_id INTEGER,
                complaint_number TEXT,
                filed_at TIMESTAMP,
                status TEXT,
                FOREIGN KEY (dispute_id) REFERENCES disputes(id)
            )
        ''')

        conn.commit()
        conn.close()

    def create_dispute(self, dispute: DisputeItem) -> int:
        """
        Create a new dispute

        Args:
            dispute: DisputeItem object

        Returns:
            Dispute ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO disputes
            (account_name, account_number, dispute_reason, description, bureau, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            dispute.account_name,
            dispute.account_number,
            dispute.reason,
            dispute.description,
            dispute.bureau,
            dispute.status,
            dispute.created_at
        ))

        dispute_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return dispute_id

    def generate_411_method_letter(self, dispute: DisputeItem) -> str:
        """
        Generate 411 method dispute letter

        Args:
            dispute: DisputeItem object

        Returns:
            Letter text
        """
        template = f"""
{datetime.now().strftime('%B %d, %Y')}

{self.BUREAU_ADDRESSES[dispute.bureau]['address']}

Re: Formal Dispute of Inaccurate Information
File Number: [Your File Number]

To Whom It May Concern:

I am writing to formally dispute inaccurate information appearing on my credit report. Under the Fair Credit Reporting Act (FCRA) 15 U.S.C. § 1681, I have the right to dispute incomplete or inaccurate information.

DISPUTED ITEM:
Account Name: {dispute.account_name}
Account Number: {dispute.account_number}

REASON FOR DISPUTE:
{dispute.dispute_reason}

DETAILED EXPLANATION:
{dispute.description}

Under FCRA § 1681i(a)(1)(A), you are required to conduct a reasonable investigation of this dispute within 30 days. If you cannot verify this information with the furnisher, you must delete it from my credit file per FCRA § 1681i(a)(5)(A).

I am requesting that you:
1. Conduct a thorough investigation of this matter
2. Provide me with the method of verification
3. Remove this item if it cannot be verified
4. Send me an updated copy of my credit report upon completion

Please provide your findings in writing within 30 days as required by law.

Sincerely,

[Your Name]
[Your Address]
[Your Phone Number]

Enclosures:
- Copy of credit report (highlighted)
- Supporting documentation
- Copy of ID
"""
        return template

    def generate_goodwill_letter(
        self,
        creditor_name: str,
        account_number: str,
        payment_history: str,
        reason: str
    ) -> str:
        """Generate goodwill letter requesting deletion"""
        template = f"""
{datetime.now().strftime('%B %d, %Y')}

{creditor_name}
Customer Service Department

Re: Goodwill Request for Account {account_number}

Dear {creditor_name} Customer Service,

I am writing to request your consideration in removing a late payment from my credit report for account {account_number}.

PAYMENT HISTORY:
{payment_history}

CIRCUMSTANCES:
{reason}

I have been a valued customer and have maintained a positive relationship with your company. This isolated incident does not reflect my overall financial responsibility and commitment to meeting my obligations.

I am respectfully requesting that you exercise goodwill and remove this late payment from my credit report. I understand this is at your discretion, and I would be grateful for your consideration.

Thank you for your time and understanding.

Sincerely,

[Your Name]
[Your Contact Information]
"""
        return template

    def parse_credit_report_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Parse credit report PDF and extract disputable items

        Args:
            pdf_path: Path to credit report PDF

        Returns:
            List of potential dispute items
        """
        disputable_items = []

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()

                # Look for common negative items
                negative_keywords = [
                    'late payment', 'collection', 'charge-off',
                    'foreclosure', 'repossession', 'bankruptcy',
                    'delinquent', 'past due'
                ]

                for keyword in negative_keywords:
                    if keyword.lower() in text.lower():
                        # Extract context around keyword
                        # This is simplified - in production, use more sophisticated parsing
                        disputable_items.append({
                            'type': keyword,
                            'found_in_report': True,
                            'needs_review': True
                        })

        except Exception as e:
            print(f"Error parsing PDF: {e}")

        return disputable_items

    def track_dispute_status(self, dispute_id: int) -> Dict:
        """
        Get current status of a dispute

        Args:
            dispute_id: Dispute ID

        Returns:
            Dispute status info
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM disputes WHERE id = ?
        ''', (dispute_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'account_name': row[1],
                'status': row[6],
                'created_at': row[7],
                'days_pending': (datetime.now() - datetime.fromisoformat(row[7])).days
            }

        return None

    def calculate_fcra_damages(self, violations: List[str]) -> float:
        """
        Calculate potential FCRA damages

        Args:
            violations: List of FCRA violations

        Returns:
            Estimated damages ($100-$1000 per violation)
        """
        per_violation = 500  # Average
        total = len(violations) * per_violation

        # Statutory damages: $100-$1000 per violation
        # Actual damages: varies
        # Punitive damages: possible if willful

        return total

    def export_dispute_package(
        self,
        dispute_id: int,
        output_path: str
    ):
        """
        Generate complete dispute package (letter + evidence)

        Args:
            dispute_id: Dispute ID
            output_path: Where to save PDF
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM disputes WHERE id = ?', (dispute_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Dispute {dispute_id} not found")

        dispute = DisputeItem(
            account_name=row[1],
            account_number=row[2],
            dispute_reason=row[3],
            description=row[4],
            bureau=row[5],
            status=row[6],
            created_at=row[7]
        )

        # Generate PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add letter
        letter_text = self.generate_411_method_letter(dispute)
        for line in letter_text.split('\n'):
            p = Paragraph(line, styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 12))

        doc.build(story)
        print(f"Dispute package saved: {output_path}")


# Example usage
if __name__ == "__main__":
    automation = CreditDisputeAutomation()

    # Create dispute
    dispute = DisputeItem(
        account_name="Capital One",
        account_number="XXXX1234",
        dispute_reason="Not mine",
        description="I have never had an account with Capital One",
        bureau="Equifax"
    )

    dispute_id = automation.create_dispute(dispute)
    print(f"Dispute created: ID {dispute_id}")

    # Generate letter
    letter = automation.generate_411_method_letter(dispute)
    print(letter)

    # Export package
    automation.export_dispute_package(dispute_id, "dispute_package.pdf")
