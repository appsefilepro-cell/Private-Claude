# Probate and Estate Administration Automation System

## Overview

The Probate and Estate Administration Automation System provides comprehensive tools for managing the entire probate process, from initial estate inventory through final distributions to beneficiaries. The system automates complex calculations, generates required court documents, tracks critical deadlines, and integrates with SharePoint for secure document management.

## Features

### 1. Estate Inventory Automation
- **Asset Management**: Add, track, and manage all types of estate assets
- **Asset Types Supported**:
  - Real property (homes, land)
  - Personal property (household items, jewelry)
  - Bank accounts and cash
  - Investments (stocks, bonds, mutual funds)
  - Vehicles
  - Business interests
  - Life insurance proceeds
  - Retirement accounts

- **Valuation Tracking**:
  - Estimated value at death
  - Fair market value determination
  - Appraisal date tracking
  - Encumbrance tracking (liens, mortgages)

### 2. Probate Court Form Generation
Automatically generates required court documents:
- **Petition for Probate**: Initial petition to establish probate
- **Notice to Creditors**: Published notice to claim creditors
- **Inventory and Appraisal**: Complete asset listing with valuations
- **Final Account and Report**: Final accounting before estate closure

### 3. Asset Valuation and Management
- Track estimated and fair market values
- Record appraisal dates and methods
- Calculate net asset values after encumbrances
- Generate inventory summaries by asset type
- Support for appraisal tracking and verification

### 4. Creditor Claim Management
- Track all creditor claims against the estate
- Process proof of claims
- Determine allowed vs. claimed amounts
- Organize by creditor type and priority
- Support for priority-based claim payment
- Generate creditor reports and summaries

### 5. Distribution Calculation
- Calculate net distributions to beneficiaries
- Track share percentages
- Support for percentage-based distributions
- Approve and record distributions
- Generate distribution summaries
- Track distribution status (pending, approved, distributed)

### 6. State-Specific Rules
Configured for multiple states with:
- Small estate thresholds
- Bond requirements
- Timeline specifications
- Special procedures (e.g., succession without administration)
- Court filing requirements

## Quick Start

### Installation

1. Ensure Python 3.8+ is installed
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from pillar_b_legal.probate import (
    Estate, AssetType, CreditorType,
    EstateInventoryManager, CreditorClaimManager,
    DistributionCalculator, ProbateWorkflowManager
)

# Create an estate
estate = Estate(
    id="EST-2024-001",
    decedent_name="John Smith",
    date_of_death="2024-11-15",
    ssn_last_4="1234",
    state="California",
    court_county="Los Angeles",
    personal_representative="Jane Smith",
    estimated_gross_value=500000.00
)

# Add assets
inv_mgr = EstateInventoryManager(estate)
inv_mgr.add_asset(
    AssetType.REAL_PROPERTY,
    "Primary Residence",
    "123 Oak Ave, Los Angeles, CA",
    300000.00
)

# Add creditors
cred_mgr = CreditorClaimManager(estate)
cred_mgr.add_creditor(
    CreditorType.SECURED,
    "Bank of America",
    175000.00,
    priority_level=3
)

# Add beneficiaries
dist_mgr = DistributionCalculator(estate)
dist_mgr.add_beneficiary(
    "Jane Smith",
    "Spouse",
    60.0,
    "456 Main St, Los Angeles, CA",
    "jane@email.com"
)

# Calculate and approve distributions
dist_mgr.approve_distributions()

# Get comprehensive summary
workflow_mgr = ProbateWorkflowManager(estate, config)
summary = workflow_mgr.get_estate_summary()
```

## Module Components

### Core Classes

#### Estate
The main container for all estate information:
- Decedent details
- Personal representative information
- Assets dictionary
- Creditors dictionary
- Beneficiaries dictionary
- Status tracking
- Timeline information

#### Asset
Represents individual estate assets:
- Asset type enumeration
- Description and location
- Estimated and fair market values
- Appraisal tracking
- Encumbrance tracking
- Net value calculation

#### Creditor
Represents claims against the estate:
- Creditor type (secured, unsecured, priority)
- Claimed vs. allowed amounts
- Proof of claim tracking
- Priority level assignment
- Claim status

#### Beneficiary
Represents beneficiary information:
- Name and relationship
- Share percentage
- Contact information
- Distribution amount and status
- Additional notes

### Manager Classes

#### EstateInventoryManager
Manages all estate assets:
- `add_asset()`: Add new asset to inventory
- `update_asset_valuation()`: Update fair market value
- `encumber_asset()`: Record liens or mortgages
- `get_inventory_summary()`: Generate comprehensive asset summary

#### CreditorClaimManager
Manages creditor claims:
- `add_creditor()`: Register new creditor claim
- `process_proof_of_claim()`: Process and approve claims
- `get_creditor_report()`: Generate creditor summary by type/priority

#### DistributionCalculator
Calculates beneficiary distributions:
- `add_beneficiary()`: Add beneficiary to estate
- `calculate_distributions()`: Compute distribution amounts
- `approve_distributions()`: Approve all distributions
- `record_distribution()`: Track completed distributions
- `get_distribution_summary()`: Generate distribution report

#### ProbateFormGenerator
Generates required court documents:
- `generate_petition_for_probate()`: Initial probate petition
- `generate_notice_to_creditors()`: Creditor notice
- `generate_inventory_and_appraisal()`: Asset inventory form
- `generate_final_account_and_report()`: Final accounting document

#### ProbateWorkflowManager
Orchestrates the overall probate process:
- `get_estate_summary()`: Comprehensive estate overview
- `advance_status()`: Update probate status
- `export_to_json()`: Export estate data
- `export_summary_report()`: Export comprehensive report

## Workflow Orchestration

The workflow orchestration script (`scripts/probate_workflow.py`) provides:

### Features
- **Deadline Tracking**: Automatic deadline calculation based on state rules
- **Document Management**: Track document generation and filing status
- **SharePoint Integration**: Upload and manage documents in SharePoint
- **Workflow Status**: Monitor overall probate progress
- **Deadline Warnings**: Alert system for upcoming deadlines

### Usage

```python
from scripts.probate_workflow import ProbateWorkflowOrchestrator

# Initialize orchestrator
orchestrator = ProbateWorkflowOrchestrator(
    estate=estate,
    config=config,
    sharepoint_config={
        'site_url': 'https://yourorg.sharepoint.com/sites/legal',
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET'
    }
)

# Initialize SharePoint connection
orchestrator.initialize_sharepoint()

# Generate documents
orchestrator.generate_petition_document()
orchestrator.generate_notice_to_creditors()
orchestrator.generate_inventory_document()
orchestrator.generate_final_account_document()

# Track deadlines
upcoming = orchestrator.get_upcoming_deadlines(days_ahead=30)
overdue = orchestrator.get_overdue_deadlines()
warnings = orchestrator.get_deadline_warnings()

# Export workflow status
status = orchestrator.export_workflow_status()
print(orchestrator.get_workflow_summary())
```

## Configuration

### State-Specific Rules
Configuration file (`probate_config.json`) includes:

```json
{
  "state_rules": {
    "california": {
      "small_estate_threshold": 166250,
      "inventory_due_days": 60,
      "creditor_claim_period_days": 120,
      "appraisal_required": false
    }
  }
}
```

### Document Checklist
Comprehensive pre-filing, filing, administration, and closing document checklists.

### Timeline Tracking
Automated milestone tracking with configurable days after death.

### Court Filing Requirements
Fee schedules, publication requirements, and filing deadlines.

## Templates

### 1. Petition for Probate
Comprehensive template for initial probate petition including:
- Decedent information
- Heirs and beneficiaries listing
- Personal representative details
- Estate valuation
- Prayer for relief

### 2. Notice to Creditors
Standard creditor notice template with:
- Publication information
- Creditor claim deadline
- Personal representative contact
- Claim presentation requirements
- Court information

### 3. Inventory and Appraisal
Detailed asset inventory form featuring:
- Real property section
- Personal property listing
- Bank account details
- Investment holdings
- Vehicle information
- Business interests
- Life insurance
- Retirement accounts
- Appraisal certification

### 4. Final Account and Report
Comprehensive final accounting document with:
- Property received summary
- Property expended detail
- Accounting reconciliation
- Creditor claims summary
- Distribution details
- Personal representative certification
- Attorney certification
- Request for approval and discharge

## State Configuration Examples

### California
- Small estate threshold: $166,250
- Inventory due: 60 days
- Creditor claim period: 120 days
- Special: Succession without administration available

### Florida
- Small estate threshold: $75,000
- Inventory due: 90 days
- Creditor claim period: 90 days
- Special: Disposition without administration available

### Texas
- Small estate threshold: $75,000
- Inventory due: 90 days
- Creditor claim period: 120 days
- Special: Independent administration available

## Creditor Priority Rules

Standard probate creditor priority hierarchy:
1. **Administrative Expenses**: Court costs, attorney fees, appraiser fees
2. **Funeral Expenses**: Reasonable funeral and burial costs
3. **Secured Claims**: Mortgages, liens on specific property
4. **Wage Claims**: Employee wages owed
5. **Tax Claims**: Federal, state, local taxes
6. **Unsecured Claims**: Credit cards, personal loans, medical bills

## Document Workflow

### Pre-Filing Stage
- Gather required documents (death certificate, will, tax returns)
- Create estate inventory
- Identify heirs and beneficiaries
- Collect financial statements

### Filing Stage
- File petition for probate
- Obtain hearing date
- Publish notice of petition
- File affidavit of domicile

### Administration Stage
- File inventory and appraisal (60-90 days)
- Publish notice to creditors (120+ day period)
- Process creditor claims
- Maintain detailed accounting

### Closing Stage
- File final account and report
- Obtain court approval
- Make distributions
- File closing documents

## Real Estate Administration

The system is specifically optimized for real estate administration:

### Real Property Management
- Track property location and description
- Record mortgages and encumbrances
- Calculate net property value
- Support for property sale proceeds
- Real estate transfer documentation

### Property Valuation
- Date of death fair market value
- Appraisal tracking and documentation
- Encumbrance deductions
- Net value calculations
- Multiple property support

### Property Transfer
- Track transfer complexity (high for complex properties)
- Timeline tracking for transfers
- Support for in-kind distributions
- Deed preparation integration

## Integration Points

### SharePoint Integration
- Automatic folder structure creation
- Document upload and versioning
- URL tracking for uploaded documents
- Permission management support

### Document Generation
- Template-based form generation
- Variable substitution and data population
- Multi-state template support
- Fillable PDF support (external)

### Reporting
- JSON export of complete estate data
- Summary report generation
- Timeline and milestone tracking
- Deadline alert generation

## Error Handling and Logging

The system includes comprehensive logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# All major operations are logged:
# - Asset additions and valuations
# - Creditor claim processing
# - Distribution calculations
# - Document generation
# - Status updates
```

## Data Export

### JSON Export
Export complete estate data as JSON:
```python
json_data = workflow_mgr.export_to_json()
```

### Summary Reports
Generate human-readable summary reports:
```python
summary = orchestrator.export_workflow_status()
print(orchestrator.get_workflow_summary())
```

## Best Practices

1. **Always create a backup** of estate data before major changes
2. **Use state-specific configuration** for accurate timelines
3. **Document all creditor communications** in the notes field
4. **Track appraisals** with dates and appraiser information
5. **Update beneficiary information** as it becomes available
6. **Mark deadlines completed** to maintain accurate status
7. **Use SharePoint integration** for regulatory compliance and audit trail
8. **Generate reports regularly** to monitor progress
9. **Verify calculations** before distribution approval
10. **Keep detailed accounting** of all estate transactions

## Compliance Features

- **Audit Trail**: Complete logging of all transactions
- **Document Versioning**: Track document updates and changes
- **Deadline Tracking**: Never miss critical probate deadlines
- **State-Specific Rules**: Comply with individual state requirements
- **Electronic Filing Support**: Generate court-ready documents
- **Beneficiary Communication**: Track beneficiary information and distributions

## Future Enhancements

Planned features:
- Multi-estate management
- Advanced tax planning integration
- Electronic filing with courts
- Beneficiary portal integration
- Automated email notifications
- Advanced reporting and analytics
- Machine learning for claim assessment

## Support and Documentation

For additional information:
- See `/pillar-b-legal/probate/probate_config.json` for configuration details
- Review templates in `/pillar-b-legal/probate/templates/` for document examples
- Check `scripts/probate_workflow.py` for orchestration examples

## License

This system is part of the comprehensive legal automation framework.

## Version History

- **1.0.0** (2024-12): Initial release with core probate functionality
