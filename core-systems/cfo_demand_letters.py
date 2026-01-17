#!/usr/bin/env python3
"""
CFO Master AI Suite - Demand Letter Generator
Part 2 Implementation - Pillar B (Legal) Integration

Automated generation of final demand letters for estate asset restitution.
Integrates with Integer Watchdog for financial data and CFO division agents.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json


class DemandLetterGenerator:
    """
    Generates professional demand letters for asset restitution.
    
    Features:
    - Multiple letter templates (initial, follow-up, final)
    - Financial data integration from Integer Watchdog
    - Executive resolution channel routing
    - Audit trail documentation
    """
    
    def __init__(self):
        self.letters_generated = []
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load letter templates."""
        return {
            'initial_demand': {
                'subject': 'Notice of Asset Discrepancy and Request for Restitution',
                'tone': 'professional',
                'urgency': 'high'
            },
            'follow_up': {
                'subject': 'Follow-Up: Outstanding Asset Restitution Matter',
                'tone': 'firm',
                'urgency': 'urgent'
            },
            'final_demand': {
                'subject': 'FINAL DEMAND: Immediate Restitution Required',
                'tone': 'formal',
                'urgency': 'critical'
            }
        }
    
    def generate_demand_letter(self,
                               recipient_info: Dict,
                               financial_data: Dict,
                               letter_type: str = 'final_demand') -> Dict:
        """
        Generate a demand letter.
        
        Args:
            recipient_info: Dictionary with recipient details
                - name: Recipient name
                - title: Recipient title
                - organization: Organization name
                - address: Mailing address
            financial_data: Financial discrepancy data
                - total_amount: Total amount in dispute
                - breakdown: List of discrepancy items
                - date_range: Period of discrepancies
            letter_type: Type of letter (initial_demand, follow_up, final_demand)
            
        Returns:
            Dictionary with letter details and content
        """
        template = self.templates.get(letter_type, self.templates['final_demand'])
        
        # Create letter document structure first
        letter = {
            'letter_id': f"DL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'letter_type': letter_type,
            'generated_date': datetime.now().isoformat(),
            'recipient': recipient_info,
            'financial_summary': {
                'total_amount': financial_data.get('total_amount', 0),
                'currency': 'USD',
                'item_count': len(financial_data.get('breakdown', []))
            },
            'subject': template['subject'],
            'content': '',  # Will be filled by _compose_letter
            'urgency': template['urgency'],
            'response_deadline': (datetime.now() + timedelta(days=15)).isoformat(),
            'status': 'GENERATED',
            'delivery_channel': 'executive_resolution'
        }
        
        # Generate letter content with letter metadata
        letter['content'] = self._compose_letter(
            recipient_info,
            financial_data,
            template,
            letter
        )
        
        self.letters_generated.append(letter)
        
        return letter
    
    def _compose_letter(self,
                       recipient_info: Dict,
                       financial_data: Dict,
                       template: Dict,
                       letter: Dict) -> str:
        """Compose the letter content."""
        total_amount = financial_data.get('total_amount', 0)
        breakdown = financial_data.get('breakdown', [])
        date_range = financial_data.get('date_range', 'unspecified period')
        
        # Letter header
        content = f"""
{datetime.now().strftime('%B %d, %Y')}

{recipient_info.get('name', 'To Whom It May Concern')}
{recipient_info.get('title', '')}
{recipient_info.get('organization', '')}
{recipient_info.get('address', '')}

RE: {template['subject']}

Dear {recipient_info.get('name', 'Sir/Madam')}:

This letter serves as formal notice regarding significant financial discrepancies 
identified through our comprehensive audit of estate assets during the period of 
{date_range}.

EXECUTIVE SUMMARY OF FINDINGS:

Our CFO Master AI Suite, in conjunction with the Integer Watchdog financial 
monitoring system, has identified the following discrepancies requiring immediate 
attention and restitution:

FINANCIAL BREAKDOWN:
"""
        
        # Add breakdown items
        for idx, item in enumerate(breakdown, 1):
            content += f"\n{idx}. {item.get('description', 'Unspecified Item')}"
            content += f"\n   Amount: ${item.get('amount', 0):,.2f}"
            content += f"\n   Date: {item.get('date', 'N/A')}"
            content += f"\n   Reference: {item.get('reference', 'N/A')}\n"
        
        # Add total
        content += f"\nTOTAL AMOUNT REQUIRING RESTITUTION: ${total_amount:,.2f}\n"
        
        # Add demand section based on letter type
        if template['urgency'] == 'critical':
            demand_section = f"""
DEMAND FOR IMMEDIATE ACTION:

This matter has escalated to critical status. We hereby make a FINAL DEMAND for 
immediate restitution of the above-referenced amounts. This letter constitutes 
formal notice that:

1. Full restitution in the amount of ${total_amount:,.2f} is required within fifteen (15) 
   business days from the date of this letter.

2. Failure to provide complete restitution by the specified deadline will result 
   in escalation to executive resolution channels and appropriate legal remedies.

3. All communications regarding this matter should be directed to our executive 
   resolution team immediately.

REQUIRED RESPONSE:

You are required to:
- Acknowledge receipt of this demand within 48 hours
- Provide a detailed response addressing each item listed above
- Submit a restitution plan with timeline for full payment
- Coordinate with our executive resolution team for verification

"""
            content += demand_section
        else:
            content += """
REQUIRED ACTION:

We request your immediate attention to this matter and expect:
- Acknowledgment of receipt within 5 business days
- Detailed explanation of the discrepancies identified
- Proposed timeline for restitution
- Direct communication with our resolution team

"""
        
        # Closing
        closing_section = f"""
This matter is being monitored by our automated systems and executive oversight 
team. We trust this issue will be resolved promptly and professionally.

For questions or to coordinate restitution, please contact our executive 
resolution channel immediately.

Sincerely,

CFO Master AI Suite
Estate Asset Management Division
Automated Financial Oversight System

---
This letter was generated by the CFO Master AI Suite in conjunction with 
Integer Watchdog financial monitoring. All findings are based on comprehensive 
automated audit procedures and real-time cashflow analysis.

Document ID: {letter['letter_id']}
Generated: {letter['generated_date']}
Response Required By: {letter['response_deadline']}
Priority: {letter['urgency'].upper()}
"""
        content += closing_section
        
        return content.strip()
    
    def generate_batch_letters(self,
                              recipients: List[Dict],
                              financial_data_list: List[Dict],
                              letter_type: str = 'final_demand') -> List[Dict]:
        """
        Generate multiple demand letters in batch.
        
        Args:
            recipients: List of recipient information dictionaries
            financial_data_list: List of financial data for each recipient
            letter_type: Type of letters to generate
            
        Returns:
            List of generated letter dictionaries
        """
        letters = []
        
        for recipient, financial_data in zip(recipients, financial_data_list):
            letter = self.generate_demand_letter(
                recipient,
                financial_data,
                letter_type
            )
            letters.append(letter)
        
        return letters
    
    def export_letter_to_file(self, letter: Dict, output_path: str) -> bool:
        """
        Export a letter to a text file.
        
        Args:
            letter: Letter dictionary
            output_path: Path to save the letter
            
        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(letter['content'])
            
            print(f"Letter exported: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting letter: {e}")
            return False
    
    def export_letter_package(self, letter: Dict, output_dir: str) -> bool:
        """
        Export complete letter package (letter + metadata).
        
        Args:
            letter: Letter dictionary
            output_dir: Directory to save package
            
        Returns:
            True if successful
        """
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Export letter content
            letter_file = Path(output_dir) / f"{letter['letter_id']}_letter.txt"
            with open(letter_file, 'w', encoding='utf-8') as f:
                f.write(letter['content'])
            
            # Export metadata
            metadata_file = Path(output_dir) / f"{letter['letter_id']}_metadata.json"
            metadata = {k: v for k, v in letter.items() if k != 'content'}
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Letter package exported to: {output_dir}")
            return True
            
        except Exception as e:
            print(f"Error exporting letter package: {e}")
            return False
    
    def get_letters_summary(self) -> Dict:
        """Get summary of generated letters."""
        by_type = {}
        by_urgency = {}
        
        for letter in self.letters_generated:
            # Count by type
            letter_type = letter['letter_type']
            by_type[letter_type] = by_type.get(letter_type, 0) + 1
            
            # Count by urgency
            urgency = letter['urgency']
            by_urgency[urgency] = by_urgency.get(urgency, 0) + 1
        
        total_amount = sum(
            letter['financial_summary']['total_amount']
            for letter in self.letters_generated
        )
        
        return {
            'total_letters': len(self.letters_generated),
            'by_type': by_type,
            'by_urgency': by_urgency,
            'total_amount_in_demand': f"${total_amount:,.2f}"
        }


def main():
    """Example usage of Demand Letter Generator."""
    generator = DemandLetterGenerator()
    
    print("CFO Master AI Suite - Demand Letter Generator")
    print("Part 2 Implementation\n")
    
    # Example: Generate a final demand letter
    recipient = {
        'name': 'John Smith',
        'title': 'Chief Financial Officer',
        'organization': 'Example Corporation',
        'address': '123 Business St, Suite 100\nCity, ST 12345'
    }
    
    financial_data = {
        'total_amount': 151320.29,
        'date_range': 'January 2020 - December 2024',
        'breakdown': [
            {
                'description': 'Unauthorized estate asset transfer',
                'amount': 75000.00,
                'date': '2020-07-15',
                'reference': 'TXN-2020-0715-001'
            },
            {
                'description': 'Cashflow spike requiring explanation',
                'amount': 18000.00,
                'date': '2020-07-20',
                'reference': 'WATCHDOG-ALERT-0720'
            },
            {
                'description': 'Unexplained account discrepancies',
                'amount': 58320.29,
                'date': '2021-03-10',
                'reference': 'AUDIT-2021-Q1-003'
            }
        ]
    }
    
    letter = generator.generate_demand_letter(
        recipient,
        financial_data,
        letter_type='final_demand'
    )
    
    print(f"Generated Letter ID: {letter['letter_id']}")
    print(f"Subject: {letter['subject']}")
    print(f"Total Amount: ${letter['financial_summary']['total_amount']:,.2f}")
    print(f"Response Deadline: {letter['response_deadline']}")
    print(f"\nLetter Content Preview:")
    print("-" * 70)
    print(letter['content'][:500] + "...\n")
    
    # Show summary
    summary = generator.get_letters_summary()
    print(f"Generation Summary:")
    print(f"  Total Letters: {summary['total_letters']}")
    print(f"  Total in Demand: {summary['total_amount_in_demand']}")


if __name__ == "__main__":
    main()
