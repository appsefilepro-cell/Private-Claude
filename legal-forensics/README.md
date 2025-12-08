# Forensic Legal Data Analysis System - Agent X2.0

**40-Case Litigation Portfolio - Multi-Source Data Extraction & Assembly**

---

## Overview

This system performs forensic analysis across multiple data sources (Gmail, Dropbox, SharePoint, OneDrive) to extract, organize, and structure all information necessary for drafting 40 distinct litigation packets.

### Key Features

- **Multi-Source Integration**: Gmail, SharePoint, OneDrive, Dropbox
- **Automated Case Mapping**: Links documents to relevant cases using keyword analysis
- **Complete Case Dossiers**: Generates comprehensive markdown reports for all 40 cases
- **Entity Extraction**: Automatically identifies names, emails, phones, dates, dollar amounts
- **Chronological Assembly**: Builds date-sorted timelines with source documentation
- **Evidence Inventory**: Categorizes and indexes all evidentiary materials

---

## Quick Start

### Prerequisites

- Python 3.9+
- API credentials for data sources (see Configuration)

### Installation

```bash
# Navigate to directory
cd legal-forensics

# Install dependencies
pip install -r ../requirements.txt

# Configure credentials
cp ../config/.env.template ../config/.env
# Edit .env with your API credentials
```

### Execution

```bash
# Run master forensic analysis
python execute_forensic_analysis.py
```

---

## System Architecture

```
legal-forensics/
├── forensic_data_analyzer.py     # Core analyzer & case dossier generator
├── data_source_connectors.py     # Multi-source API connectors
├── execute_forensic_analysis.py  # Master execution script
├── master_case_list.json         # Complete 40-case definition
├── case-dossiers/                # Output directory (generated)
│   ├── MASTER_ALL_40_CASES.md   # Consolidated report
│   └── case_01_dossier.md       # Individual case files (x40)
└── logs/                         # Execution logs (generated)
```

---

## 40-Case Master List

### High Priority (Cases 1-2)

1. **LAPD Excessive Force** - City of Los Angeles; LAPD; Adilah Robinson
2. **Wrongful Eviction** - New Forest Houston / Novu Apartments

### Medium Priority (Cases 3-40)

3-10: Financial institutions (BMO Harris, Bank of America, etc.)
11-20: Various creditors, landlords, government agencies
21-40: Airlines, utilities, retailers, government entities

**See `master_case_list.json` for complete details**

---

## Case Dossier Structure

Each generated dossier contains:

### 1. Core Metadata
- Case caption, jurisdiction, parties
- Legal claims/causes of action
- Case theme and summary

### 2. Master Chronology
- Date-sorted timeline of all events
- Source documentation for each entry
- Extracted entities (people, companies, dates)

### 3. Key Individuals & Entities
- Profile for each person/company
- Contact information
- Role in case
- Linked communications

### 4. Evidence Inventory
- Contracts & agreements
- Financial records
- Official reports
- Written communications
- Supporting documents

### 5. Verbatim Extractions
- Direct quotes from defendants
- Factual statements by plaintiffs
- Key contract terms

### 6. Damages Analysis
- Economic losses (quantified)
- Emotional distress indicators
- Statutory violation evidence

---

## Data Source Configuration

### Gmail API

```bash
# Set in .env:
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_secret
```

**Setup Instructions:**
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download credentials.json
4. Save to `config/gmail_credentials.json`

### Microsoft 365 (SharePoint & OneDrive)

```bash
# Set in .env:
MICROSOFT_TENANT_ID=your_tenant_id
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_secret
SHAREPOINT_SITE_URL=https://appsholdingswyinc.sharepoint.com
```

**Setup Instructions:**
1. Register app in Azure AD
2. Grant permissions: Files.Read.All, Sites.Read.All
3. Create client secret
4. Update .env file

### Dropbox

```bash
# Set in .env:
DROPBOX_ACCESS_TOKEN=your_token
```

**Setup Instructions:**
1. Create app at dropbox.com/developers
2. Generate access token
3. Update .env file

**See `../docs/API_SETUP_INSTRUCTIONS.md` for detailed configuration**

---

## Usage Examples

### Generate All 40 Case Dossiers

```bash
python execute_forensic_analysis.py
```

### Generate Specific Case Dossier

```python
from forensic_data_analyzer import ForensicDataAnalyzer

analyzer = ForensicDataAnalyzer()
dossier = analyzer.generate_case_dossier(case_number=1)
print(dossier)
```

### Check Data Source Status

```python
from data_source_connectors import MultiSourceOrchestrator

orchestrator = MultiSourceOrchestrator()
status = orchestrator.get_connection_status()
for source, state in status.items():
    print(f"{source}: {state}")
```

---

## Output Files

### Master Report
`case-dossiers/MASTER_ALL_40_CASES.md`
- Consolidated report with all 40 cases
- Complete evidence inventory
- Cross-case analysis ready

### Individual Case Dossiers
`case-dossiers/case_01_dossier.md` through `case_40_dossier.md`
- Self-contained markdown files
- Ready for legal team review
- Direct links to source documents

### Execution Logs
`logs/forensic_execution_YYYYMMDD_HHMMSS.log`
- Complete audit trail
- Source attribution
- Error tracking

---

## Integration with Agent 3.0

This forensic system integrates with Agent X2.0's orchestrator:

```python
# In pillar-a-trading/agent-3.0/agent_3_orchestrator.py
from legal_forensics.forensic_data_analyzer import ForensicDataAnalyzer

# Agent 3.0 can trigger forensic analysis
analyzer = ForensicDataAnalyzer()
analyzer.generate_all_dossiers()
```

---

## Security & Compliance

### Attorney-Client Privilege
- All data treated as privileged
- Read-only access to sources
- No modification of original files
- Complete audit logging

### Data Handling
- Temporary in-memory processing
- Encrypted credential storage
- No persistent copies outside output
- Secure API authentication

### Access Controls
- OAuth 2.0 for Gmail/Microsoft 365
- API tokens for Dropbox
- Least privilege permissions
- Audit trail for all access

---

## Troubleshooting

### No Data Sources Authenticated

**Problem:** All connectors show "NOT AUTHENTICATED"

**Solution:**
1. Verify credentials in `config/.env`
2. Check API is enabled (Gmail API, Microsoft Graph)
3. Confirm permissions granted
4. Review `logs/` for specific error messages

### Documents Not Mapping to Cases

**Problem:** Zero case-document mappings

**Solution:**
1. Check keywords in `master_case_list.json`
2. Verify document content is being indexed
3. Review case mapping logic in `forensic_data_analyzer.py`

### Missing Evidence in Dossiers

**Problem:** Dossiers generated but incomplete

**Solution:**
1. Ensure all target SharePoint folders exist
2. Check file permissions on data sources
3. Verify keyword matching is working
4. Review logs for extraction errors

---

## Next Steps

1. **Configure API Credentials** - Update `config/.env`
2. **Authenticate Data Sources** - Run connectors
3. **Execute Forensic Analysis** - Run master script
4. **Review Generated Dossiers** - Check `case-dossiers/`
5. **Provide to Legal Team** - Distribute for pleading drafting

---

## Support

**For Technical Issues:**
- Check logs in `logs/` directory
- Review documentation in `../docs/`
- Verify API credentials and permissions

**For Legal Questions:**
- Contact: Thurman Malik Robinson, Jr.
- Email: appsefilepro@gmail.com
- Organization: APPS Holdings WY Inc.

---

**System Version:** 2.0.0
**Last Updated:** December 5, 2025
**Classification:** Attorney-Client Work Product
