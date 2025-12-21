"""
Complete Example: Probate and Estate Administration Workflow
Demonstrates comprehensive use of the probate automation system
for a realistic estate administration scenario.
"""

import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pillar_b_legal.probate import (
    Estate,
    AssetType,
    CreditorType,
    ProbateStatus,
    EstateInventoryManager,
    CreditorClaimManager,
    DistributionCalculator,
    ProbateFormGenerator,
    ProbateWorkflowManager
)


def create_estate():
    """Create an estate with realistic data"""
    print("\n" + "="*80)
    print("STEP 1: CREATING ESTATE")
    print("="*80)

    estate = Estate(
        id="EST-2024-001",
        decedent_name="Margaret Elizabeth Johnson",
        date_of_death="2024-11-15",
        ssn_last_4="5678",
        state="California",
        court_county="Los Angeles",
        personal_representative="David Johnson",
        pr_address="456 Maple Street, Los Angeles, CA 90001",
        pr_phone="(213) 555-0200",
        pr_email="david.johnson@email.com",
        will_on_file=True,
        estimated_gross_value=750000.00
    )

    print(f"Estate Created:")
    print(f"  ID: {estate.id}")
    print(f"  Decedent: {estate.decedent_name}")
    print(f"  Death Date: {estate.date_of_death}")
    print(f"  Personal Representative: {estate.personal_representative}")
    print(f"  Estimated Value: ${estate.estimated_gross_value:,.2f}")
    print(f"  State: {estate.state}")
    print(f"  County: {estate.court_county}")

    return estate


def add_inventory(estate):
    """Add assets to the estate inventory"""
    print("\n" + "="*80)
    print("STEP 2: ADDING ESTATE ASSETS")
    print("="*80)

    inv_mgr = EstateInventoryManager(estate)

    assets = [
        {
            'type': AssetType.REAL_PROPERTY,
            'description': 'Primary Residence - Single Family Home',
            'location': '456 Maple Street, Los Angeles, CA 90001',
            'value': 450000.00,
            'notes': '3 bed, 2 bath, built 1985, well-maintained'
        },
        {
            'type': AssetType.REAL_PROPERTY,
            'description': 'Investment Property - Apartment Building',
            'location': '789 Oak Avenue, Los Angeles, CA 90002',
            'value': 280000.00,
            'notes': '12-unit apartment complex, rents income-producing'
        },
        {
            'type': AssetType.BANK_ACCOUNT,
            'description': 'Primary Checking Account',
            'location': 'Bank of America, Main Branch',
            'value': 75000.00,
            'notes': 'Account #: ****1234'
        },
        {
            'type': AssetType.INVESTMENT,
            'description': 'Stock Portfolio',
            'location': 'Charles Schwab Brokerage',
            'value': 125000.00,
            'notes': 'Diversified stock holdings, index funds'
        },
        {
            'type': AssetType.INVESTMENT,
            'description': 'Municipal Bond Fund',
            'location': 'Charles Schwab Brokerage',
            'value': 45000.00,
            'notes': 'Tax-exempt municipal bonds'
        },
        {
            'type': AssetType.VEHICLE,
            'description': '2019 Honda Accord',
            'location': 'Los Angeles, CA',
            'value': 18000.00,
            'notes': 'Excellent condition, low mileage'
        },
        {
            'type': AssetType.LIFE_INSURANCE,
            'description': 'Life Insurance Policy',
            'location': 'Nationwide Insurance',
            'value': 200000.00,
            'notes': 'Face value $200,000, payable to estate'
        },
        {
            'type': AssetType.RETIREMENT_ACCOUNT,
            'description': 'Traditional IRA',
            'location': 'Fidelity Investments',
            'value': 85000.00,
            'notes': 'Balance at time of death'
        },
        {
            'type': AssetType.PERSONAL_PROPERTY,
            'description': 'Household Furnishings and Effects',
            'location': '456 Maple Street, Los Angeles, CA 90001',
            'value': 12000.00,
            'notes': 'Furniture, appliances, household items'
        },
        {
            'type': AssetType.PERSONAL_PROPERTY,
            'description': 'Jewelry and Personal Items',
            'location': 'Safe deposit box',
            'value': 8500.00,
            'notes': 'Jewelry, watches, personal mementos'
        }
    ]

    print(f"\nAdding {len(assets)} assets to inventory:\n")

    total_value = 0
    for asset in assets:
        asset_id = inv_mgr.add_asset(
            asset['type'],
            asset['description'],
            asset['location'],
            asset['value'],
            asset['notes']
        )
        total_value += asset['value']
        print(f"  ✓ {asset['description']}: ${asset['value']:>12,.2f}")

    print(f"\nTotal Asset Value: ${total_value:,.2f}")

    # Update some valuations with fair market values
    print("\nUpdating fair market valuations:")
    assets_list = list(estate.assets.values())
    inv_mgr.update_asset_valuation(
        assets_list[0].id,
        460000.00,
        "2024-12-01"
    )
    print(f"  ✓ Primary residence appraised: $460,000.00")

    inv_mgr.update_asset_valuation(
        assets_list[1].id,
        290000.00,
        "2024-12-01"
    )
    print(f"  ✓ Investment property appraised: $290,000.00")

    return inv_mgr


def add_creditors(estate, inv_mgr):
    """Add creditor claims against the estate"""
    print("\n" + "="*80)
    print("STEP 3: ADDING CREDITOR CLAIMS")
    print("="*80)

    cred_mgr = CreditorClaimManager(estate)

    creditors = [
        {
            'type': CreditorType.ADMINISTRATIVE,
            'name': 'Superior Court of Los Angeles County',
            'amount': 2500.00,
            'priority': 1,
            'description': 'Court filing fees and probate costs'
        },
        {
            'type': CreditorType.ADMINISTRATIVE,
            'name': 'Anderson & Associates Attorneys',
            'amount': 25000.00,
            'priority': 1,
            'description': 'Probate attorney fees'
        },
        {
            'type': CreditorType.ADMINISTRATIVE,
            'name': 'Smith Professional Appraisers',
            'amount': 3000.00,
            'priority': 1,
            'description': 'Real property appraisal fees'
        },
        {
            'type': CreditorType.PRIORITY,
            'name': 'Forest Lawn Memorial Parks',
            'amount': 8500.00,
            'priority': 2,
            'description': 'Funeral and burial expenses'
        },
        {
            'type': CreditorType.SECURED,
            'name': 'First Mortgage Bank',
            'amount': 325000.00,
            'priority': 3,
            'description': 'Mortgage on primary residence'
        },
        {
            'type': CreditorType.SECURED,
            'name': 'Harbor Commercial Loan Co',
            'amount': 95000.00,
            'priority': 3,
            'description': 'Loan against investment property'
        },
        {
            'type': CreditorType.PRIORITY,
            'name': 'California Franchise Tax Board',
            'amount': 15000.00,
            'priority': 4,
            'description': 'Final state income tax return'
        },
        {
            'type': CreditorType.UNSECURED,
            'name': 'Cedars-Sinai Medical Center',
            'amount': 12500.00,
            'priority': 6,
            'description': 'Hospital and medical bills'
        },
        {
            'type': CreditorType.UNSECURED,
            'name': 'Visa Card Account',
            'amount': 8750.00,
            'priority': 6,
            'description': 'Credit card balance'
        },
        {
            'type': CreditorType.UNSECURED,
            'name': 'Southern California Edison',
            'amount': 125.00,
            'priority': 6,
            'description': 'Utility bills'
        }
    ]

    print(f"\nAdding {len(creditors)} creditor claims:\n")

    total_claims = 0
    for creditor in creditors:
        creditor_id = cred_mgr.add_creditor(
            creditor['type'],
            creditor['name'],
            creditor['amount'],
            creditor['priority'],
            creditor['description']
        )
        total_claims += creditor['amount']
        print(f"  ✓ {creditor['name']}: ${creditor['amount']:>12,.2f} (Priority {creditor['priority']})")

    print(f"\nTotal Claims: ${total_claims:,.2f}")

    # Process some claims
    print("\nProcessing proof of claims:")
    creditors_list = list(estate.creditors.values())
    for i, creditor in enumerate(creditors_list[:8]):  # Process first 8
        cred_mgr.process_proof_of_claim(creditor.id, creditor.amount_claimed)
        print(f"  ✓ Claim from {creditor.name} approved: ${creditor.amount_allowed:,.2f}")

    return cred_mgr


def add_beneficiaries(estate):
    """Add beneficiaries and calculate distributions"""
    print("\n" + "="*80)
    print("STEP 4: ADDING BENEFICIARIES")
    print("="*80)

    dist_mgr = DistributionCalculator(estate)

    beneficiaries = [
        {
            'name': 'David Johnson',
            'relationship': 'Son',
            'share_percentage': 50.0,
            'address': '456 Maple Street, Los Angeles, CA 90001',
            'contact': '(213) 555-0200'
        },
        {
            'name': 'Sarah Johnson-Smith',
            'relationship': 'Daughter',
            'share_percentage': 30.0,
            'address': '789 Elm Street, Santa Monica, CA 90404',
            'contact': '(310) 555-0300'
        },
        {
            'name': 'Robert Michael Johnson',
            'relationship': 'Son',
            'share_percentage': 20.0,
            'address': '321 Pine Road, San Diego, CA 92101',
            'contact': '(619) 555-0400'
        }
    ]

    print(f"\nAdding {len(beneficiaries)} beneficiaries:\n")

    total_share = 0
    for beneficiary in beneficiaries:
        beneficiary_id = dist_mgr.add_beneficiary(
            beneficiary['name'],
            beneficiary['relationship'],
            beneficiary['share_percentage'],
            beneficiary['address'],
            beneficiary['contact']
        )
        total_share += beneficiary['share_percentage']
        print(f"  ✓ {beneficiary['name']} ({beneficiary['relationship']}): {beneficiary['share_percentage']}%")

    print(f"\nTotal Share: {total_share}%")

    return dist_mgr


def calculate_distributions(estate, dist_mgr, inv_mgr, cred_mgr):
    """Calculate and approve distributions"""
    print("\n" + "="*80)
    print("STEP 5: CALCULATING DISTRIBUTIONS")
    print("="*80)

    # Get summaries
    inventory_summary = inv_mgr.get_inventory_summary()
    creditor_summary = cred_mgr.get_creditor_report()

    print(f"\nEstate Valuation Summary:")
    print(f"  Total Fair Market Value: ${inventory_summary['total_fair_market_value']:,.2f}")
    print(f"  Total Encumbrances: ${inventory_summary['total_encumbrances']:,.2f}")
    print(f"  Net Estate Value: ${inventory_summary['net_estate_value']:,.2f}")

    print(f"\nCreditor Claims Summary:")
    print(f"  Total Claims: ${creditor_summary['total_claimed']:,.2f}")
    print(f"  Total Allowed: ${creditor_summary['total_allowed']:,.2f}")
    print(f"  Claims Processed: {creditor_summary['claims_processed']}/{creditor_summary['creditor_count']}")

    # Calculate distributions
    print(f"\nCalculating beneficiary distributions:")
    dist_mgr.approve_distributions()

    distribution_summary = dist_mgr.get_distribution_summary()
    print(f"  Total to Distribute: ${distribution_summary['total_to_distribute']:,.2f}")

    print(f"\nDistribution Breakdown:")
    for beneficiary in distribution_summary['beneficiaries']:
        print(f"  ✓ {beneficiary['name']} ({beneficiary['relationship']}): ${beneficiary['distribution_amount']:,.2f}")

    return distribution_summary


def generate_documents(estate, config):
    """Generate required probate documents"""
    print("\n" + "="*80)
    print("STEP 6: GENERATING PROBATE DOCUMENTS")
    print("="*80)

    form_gen = ProbateFormGenerator(estate, config)

    # Generate petition
    print("\nGenerating Petition for Probate...")
    petition = form_gen.generate_petition_for_probate()
    print(f"  ✓ Petition generated (Template: {petition['template_name']})")

    # Generate notice to creditors
    print("Generating Notice to Creditors...")
    notice = form_gen.generate_notice_to_creditors()
    print(f"  ✓ Notice to creditors generated (Template: {notice['template_name']})")
    print(f"    Claim Deadline: {notice['claim_deadline']}")

    # Generate inventory
    print("Generating Inventory and Appraisal...")
    inventory = form_gen.generate_inventory_and_appraisal()
    print(f"  ✓ Inventory and appraisal generated (Template: {inventory['template_name']})")
    print(f"    Total Value: ${inventory['total_value']:,.2f}")

    # Generate final account
    print("Generating Final Account and Report...")
    final_account = form_gen.generate_final_account_and_report()
    print(f"  ✓ Final account and report generated (Template: {final_account['template_name']})")

    return {
        'petition': petition,
        'notice': notice,
        'inventory': inventory,
        'final_account': final_account
    }


def generate_reports(estate, config):
    """Generate comprehensive reports"""
    print("\n" + "="*80)
    print("STEP 7: GENERATING REPORTS")
    print("="*80)

    workflow_mgr = ProbateWorkflowManager(estate, config)

    # Get estate summary
    print("\nEstate Summary:")
    summary = workflow_mgr.get_estate_summary()

    print(f"  Decedent: {summary['decedent_name']}")
    print(f"  Status: {summary['status']}")
    print(f"  Assets:")
    print(f"    Total Assets: {summary['assets']['asset_count']}")
    print(f"    Total Value: ${summary['assets']['total_fair_market_value']:,.2f}")
    print(f"  Creditors:")
    print(f"    Total Claims: {summary['creditors']['creditor_count']}")
    print(f"    Total Allowed: ${summary['creditors']['total_allowed']:,.2f}")
    print(f"  Beneficiaries:")
    print(f"    Total Beneficiaries: {summary['distributions']['beneficiary_count']}")
    print(f"    Total to Distribute: ${summary['distributions']['total_to_distribute']:,.2f}")

    # Export to JSON
    print("\nExporting to JSON...")
    json_export = workflow_mgr.export_to_json()
    print("  ✓ Estate data exported (available for storage)")

    return summary


def main():
    """Run complete probate workflow example"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "PROBATE AND ESTATE ADMINISTRATION AUTOMATION SYSTEM".center(78) + "║")
    print("║" + "Complete Workflow Example".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    # Load configuration
    config_path = Path(__file__).parent / "probate_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Execute workflow steps
    estate = create_estate()
    inv_mgr = add_inventory(estate)
    cred_mgr = add_creditors(estate, inv_mgr)
    dist_mgr = add_beneficiaries(estate)
    distribution_summary = calculate_distributions(estate, dist_mgr, inv_mgr, cred_mgr)
    documents = generate_documents(estate, config)
    summary = generate_reports(estate, config)

    # Final summary
    print("\n" + "="*80)
    print("WORKFLOW COMPLETE")
    print("="*80)

    print(f"\nEstate: {estate.decedent_name}")
    print(f"Case ID: {estate.id}")
    print(f"\nKey Metrics:")
    print(f"  Assets: {len(estate.assets)}")
    print(f"  Creditors: {len(estate.creditors)}")
    print(f"  Beneficiaries: {len(estate.beneficiaries)}")
    print(f"  Documents Generated: 4")
    print(f"\nFinancial Summary:")
    print(f"  Gross Estate Value: ${estate.estimated_gross_value:,.2f}")
    print(f"  Total Encumbrances: ${distribution_summary['total_to_distribute'] - estate.estimated_gross_value:,.2f}")
    print(f"  Net Estate Value: ${distribution_summary['total_to_distribute']:,.2f}")

    print("\n" + "="*80)
    print("Example workflow completed successfully!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
