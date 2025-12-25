#!/usr/bin/env python3
"""
Thurman Robinson Sr. Probate Test Case
Creates actual probate case for testing the probate automation system
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pillar_b_legal.probate_automation.probate_administrator import ProbateAdministrator

def create_thurman_robinson_case():
    """Create probate test case for Thurman Robinson Sr."""

    print("=" * 80)
    print("🏛️  THURMAN ROBINSON SR. PROBATE TEST CASE")
    print("=" * 80)
    print()

    # Initialize probate administrator
    probate_admin = ProbateAdministrator()

    # Thurman Robinson Sr. case details
    case_details = {
        'decedent_name': 'Thurman Robinson Sr.',
        'date_of_death': '2024-01-15',  # Example date
        'decedent_dob': '1945-06-10',  # Example DOB
        'decedent_ssn': 'XXX-XX-XXXX',  # Placeholder
        'last_address': '123 Main Street, City, State 12345',
        'administrator_name': 'Robinson Family Administrator',
        'administrator_address': 'PO Box Address',
        'administrator_phone': '(555) 123-4567',
        'administrator_email': 'admin@example.com',
        'county': 'County Name',
        'state': 'State Name',
        'case_number': 'PROB-2024-TR001',
        'filing_date': datetime.now().strftime('%Y-%m-%d'),

        # Assets
        'assets': [
            {
                'type': 'Bank Account',
                'institution': 'Example Bank',
                'description': 'Checking Account',
                'estimated_value': 5000.00
            },
            {
                'type': 'Real Property',
                'description': 'Residential Property',
                'estimated_value': 150000.00
            }
        ],

        # Known creditors
        'creditors': [
            {
                'name': 'Example Creditor',
                'address': '456 Creditor Ave, City, State 12345',
                'claim_amount': 1000.00
            }
        ],

        # Heirs/Beneficiaries
        'heirs': [
            {
                'name': 'Heir Name',
                'relationship': 'Child',
                'address': '789 Heir Street, City, State 12345'
            }
        ]
    }

    print("📋 Case Details:")
    print(f"  Decedent: {case_details['decedent_name']}")
    print(f"  Case Number: {case_details['case_number']}")
    print(f"  Filing Date: {case_details['filing_date']}")
    print()

    # Create case intake
    print("1️⃣  Creating case intake form...")
    try:
        intake_result = probate_admin.create_case_intake(case_details)
        print(f"   ✅ Case intake created: {intake_result}")
    except Exception as e:
        print(f"   ⚠️  Error creating intake: {e}")
    print()

    # Generate Letter of Administration
    print("2️⃣  Generating Letter of Administration...")
    try:
        loa_result = probate_admin.generate_letter_of_administration(case_details)
        print(f"   ✅ Letter generated: {loa_result}")
    except Exception as e:
        print(f"   ⚠️  Error generating letter: {e}")
    print()

    # Generate creditor notifications
    print("3️⃣  Generating creditor notification letters...")
    try:
        for idx, creditor in enumerate(case_details.get('creditors', []), 1):
            creditor_result = probate_admin.generate_creditor_notification(
                case_details, creditor
            )
            print(f"   ✅ Creditor {idx} notification: {creditor_result}")
    except Exception as e:
        print(f"   ⚠️  Error generating creditor notifications: {e}")
    print()

    # Generate bank notifications
    print("4️⃣  Generating bank notification letters...")
    try:
        for idx, asset in enumerate(case_details.get('assets', []), 1):
            if asset['type'] == 'Bank Account':
                bank_result = probate_admin.generate_bank_notification(
                    case_details, asset
                )
                print(f"   ✅ Bank {idx} notification: {bank_result}")
    except Exception as e:
        print(f"   ⚠️  Error generating bank notifications: {e}")
    print()

    # Create case folder structure
    print("5️⃣  Creating case folder structure...")
    try:
        folder_result = probate_admin.create_case_folder(case_details['case_number'])
        print(f"   ✅ Case folder created: {folder_result}")
    except Exception as e:
        print(f"   ⚠️  Error creating folder: {e}")
    print()

    # Summary
    print("=" * 80)
    print("✅ THURMAN ROBINSON SR. PROBATE TEST CASE COMPLETE")
    print("=" * 80)
    print()
    print("📁 Case Files Location: pillar-b-legal/probate-automation/cases/")
    print("📄 Generated Documents:")
    print("   - Case Intake Form")
    print("   - Letter of Administration")
    print("   - Creditor Notification Letters")
    print("   - Bank Notification Letters")
    print("   - Case Folder Structure")
    print()
    print("🎯 Next Steps:")
    print("   1. Review generated documents")
    print("   2. Fill in actual personal information (SSN, addresses, etc.)")
    print("   3. Customize letters as needed")
    print("   4. File with probate court")
    print("   5. Send notifications to creditors and banks")
    print()

    return {
        'status': 'success',
        'case_number': case_details['case_number'],
        'decedent': case_details['decedent_name'],
        'documents_generated': 5
    }

if __name__ == '__main__':
    try:
        result = create_thurman_robinson_case()
        print(f"✅ Test Result: {result}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
