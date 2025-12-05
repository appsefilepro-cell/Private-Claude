# Agent X2.0 - Complete Deployment Guide

**Version:** 2.0.0
**Date:** December 5, 2025
**Owner:** Thurman Malik Robinson
**Organization:** APPS Holdings WY Inc.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Pillar A: Trading Bot Network](#pillar-a-trading-bot-network)
6. [Pillar B: Legal Document Automation](#pillar-b-legal-document-automation)
7. [Pillar C: Federal Contracting](#pillar-c-federal-contracting)
8. [Pillar D: Non-Profit Grant Intelligence](#pillar-d-non-profit-grant-intelligence)
9. [Data Ingestion & Remediation](#data-ingestion--remediation)
10. [Testing & Validation](#testing--validation)
11. [Compliance & Security](#compliance--security)
12. [Monitoring & Maintenance](#monitoring--maintenance)
13. [Troubleshooting](#troubleshooting)

---

## Executive Summary

Agent X2.0 is an advanced, multi-pillar automation system that integrates:

- **Trading Operations**: Automated candlestick pattern recognition and trade execution
- **Legal Automation**: Document generation and case management
- **Federal Contracting**: SAM.gov opportunity monitoring and 8(a) application support
- **Grant Intelligence**: Non-profit grant research and pipeline management
- **Data Ingestion**: Automated extraction from Gmail, OneDrive, SharePoint, Dropbox

### Deployment Status

This deployment creates a **100% functional foundation** with:
- ✅ Complete codebase for all 4 pillars
- ✅ Configuration templates
- ✅ API connector frameworks
- ✅ Data ingestion and remediation engines
- ✅ Compliance and audit logging
- ✅ Comprehensive documentation

**Note:** Full operational deployment requires API credentials and external service configuration.

---

## System Architecture

```
Agent X2.0
├── Pillar A: Trading Bot Network
│   ├── Agent 3.0 Orchestrator (Central Hub)
│   ├── Pattern Recognition Bot
│   ├── Execution Bot
│   ├── Compliance Logger
│   └── Zapier Integration
│
├── Pillar B: Legal Document Automation
│   ├── Document Generator
│   ├── Template Library
│   ├── Case Management System
│   └── Power Automate Flows
│
├── Pillar C: Federal Contracting
│   ├── SAM.gov Opportunity Monitor
│   ├── 8(a) Application Package
│   └── CDFI Outreach System
│
├── Pillar D: Non-Profit Grant Intelligence
│   ├── Grant Pipeline Manager
│   ├── Free Tools Database
│   └── Weekly Digest Generator
│
└── Core Systems
    ├── Data Ingestion (Gmail, OneDrive, SharePoint, Dropbox)
    ├── Remediation Engine
    ├── API Connectors
    ├── Compliance & Audit Logging
    └── Testing Framework
```

---

## Prerequisites

### Required Accounts & Services

1. **Microsoft 365 Tenant**
   - Tenant: `APPSHOLDINGSWYINC.onmicrosoft.com`
   - SharePoint: `appsholdingswyinc.sharepoint.com`
   - Admin access required

2. **Gmail Account**
   - Google Cloud Platform project
   - Gmail API enabled
   - OAuth 2.0 credentials

3. **Trading Platform**
   - Kraken account (or alternative)
   - API keys with trading permissions
   - KYC verification completed

4. **Zapier Account**
   - Professional plan (for multi-step Zaps)
   - Webhook access

5. **SAM.gov Account**
   - Entity registration
   - API key (free tier available)

### Software Requirements

- **Python:** 3.9 or higher
- **Node.js:** 16+ (if using JavaScript components)
- **Git:** For version control
- **Docker:** (Optional) For containerized deployment

### Python Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `PyMuPDF` (fitz) - PDF processing
- `openpyxl` - Excel file processing
- `requests` - HTTP API calls
- `python-dotenv` - Environment variable management
- `msal` - Microsoft authentication
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` - Gmail API

---

## Installation & Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd Private-Claude
git checkout claude/deploy-agent-x2-01826tc4741Zm819Gf6PaXAX
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy template
cp config/.env.template config/.env

# Edit with your credentials
nano config/.env
```

**Critical:** Never commit `.env` file to version control!

### Step 4: Directory Structure Verification

```bash
# Verify all directories exist
ls -R
```

Expected structure:
```
├── pillar-a-trading/
├── pillar-b-legal/
├── pillar-c-federal/
├── pillar-d-nonprofit/
├── core-systems/
├── config/
├── docs/
└── logs/
```

---

## Pillar A: Trading Bot Network

### Setup Agent 3.0 Orchestrator

1. **Configure Trading Parameters**

Edit `config/agent_3_config.json`:
```json
{
  "risk_management": {
    "confidence_threshold": 0.75,
    "max_position_size": 0.02,
    "risk_per_trade": 0.01
  }
}
```

2. **Set Kraken API Credentials**

In `.env`:
```bash
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_API_SECRET=your_kraken_secret
```

3. **Configure Zapier Webhook**

- Create a new Zap in Zapier
- Use "Webhooks by Zapier" as trigger
- Copy webhook URL to `.env`:

```bash
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/YOUR_ID/
```

4. **Run Agent 3.0**

```bash
python pillar-a-trading/agent-3.0/agent_3_orchestrator.py
```

### Setup Candlestick Analyzer

```bash
python pillar-a-trading/bots/pattern-recognition/candlestick_analyzer.py
```

### Zapier Integration Setup

Create these Zaps:

**Zap 1: Signal Routing**
- Trigger: Webhook (from Agent 3.0)
- Action 1: Filter (confidence > 0.75)
- Action 2: Send to Slack/Email
- Action 3: Log to Google Sheets

**Zap 2: Trade Execution Logger**
- Trigger: Webhook (trade executed)
- Action 1: Append row to Google Sheets
- Action 2: Upload to SharePoint
- Action 3: Send confirmation email

---

## Pillar B: Legal Document Automation

### Setup Legal Document Generator

1. **Create SharePoint Folders**

Use Microsoft Graph API or manually create:
```
/Legal Operations/
  /01_Templates/
  /02_Active_Cases/
    /NOVU_Apartments/
      /Evidence/
      /Drafts/
  /03_Automation_Output/
```

2. **Upload Templates**

Templates are generated in:
```
pillar-b-legal/templates/
```

3. **Configure Power Automate Flow**

**Flow Name:** "Legal Document Auto-Generator"

**Trigger:** When a file is created in `/02_Active_Cases/*/Evidence/`

**Actions:**
1. Get file content
2. Parse filename for case name
3. Extract text (OCR for PDFs)
4. Send to Claude API with prompt
5. Save generated document to `/Drafts/`
6. Send email notification

**Example Prompt:**
```
You are a legal automation engine. Using the following case evidence and template, generate a court-ready document.

Case: NOVU Apartments
Template: Motion for Summary Judgment
Evidence: [EXTRACTED TEXT]

Generate a complete motion ready for attorney review.
```

4. **Run Document Generator**

```bash
python pillar-b-legal/automation-flows/legal_document_generator.py
```

---

## Pillar C: Federal Contracting

### Setup SAM.gov Monitor

1. **Register on SAM.gov**
   - Go to https://sam.gov/
   - Create account
   - Complete entity registration
   - Request API key

2. **Configure Saved Searches**
   - NAICS: 561110, 541611
   - Set-Aside: 8(a)
   - Max Value: $10,000

3. **Enable Email Alerts**

4. **Update .env**
```bash
SAM_GOV_API_KEY=your_api_key
```

5. **Run Monitor**

```bash
python pillar-c-federal/sam-monitoring/sam_opportunity_monitor.py
```

### Setup Email Parsing (Alternative)

**Power Automate Flow:**
- Trigger: Email arrives from notifications@sam.gov
- Action 1: Parse email body
- Action 2: Extract opportunity details
- Action 3: Add row to SharePoint List
- Action 4: Send alert

---

## Pillar D: Non-Profit Grant Intelligence

### Setup Grant Pipeline

1. **Create SharePoint Site**

Site name: "Grant Intelligence"

Lists:
- **Funding Sources**: Name, URL, Focus Area, Last Checked
- **Grant Pipeline**: Grant Name, Agency, Due Date, Status, Assigned To
- **Resource Library**: Document library for RFPs and templates

2. **Populate Free Tools Database**

Run the free tools seeder:
```bash
python pillar-d-nonprofit/free-tools-database/seed_tools.py
```

3. **Configure Weekly Digest**

**Power Automate Flow:**
- Schedule: Weekly (Monday 9 AM)
- Action 1: Get grants due in next 30 days
- Action 2: Format HTML table
- Action 3: Send email digest

---

## Data Ingestion & Remediation

### Setup Data Ingestion

1. **Configure API Connectors**

**Gmail:**
```bash
python core-systems/api-connectors/gmail_connector.py
```

Follow on-screen instructions for OAuth setup.

**Microsoft 365:**
```bash
python core-systems/api-connectors/microsoft_365_connector.py
```

2. **Create Data Directories**

```bash
mkdir -p data/{gmail_attachments,dropbox,onedrive,sharepoint,local_files}
```

3. **Run Ingestion**

```bash
python core-systems/data-ingestion/ingestion_orchestrator.py
```

### Run Remediation Engine

Check for incomplete tasks and retry:

```bash
python core-systems/remediation/remediation_engine.py
```

**Output:**
- Updated `customer_contact_list.csv`
- Remediation log in `logs/remediation_log.txt`
- Task status in `logs/ingestion_tasks.json`

---

## Testing & Validation

### Unit Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific pillar
python -m pytest tests/test_pillar_a.py
```

### Integration Tests

```bash
python core-systems/testing/integration_tests.py
```

### Manual Testing Checklist

- [ ] Agent 3.0 starts without errors
- [ ] Candlestick analyzer detects patterns
- [ ] Zapier webhooks receive signals
- [ ] Legal documents generate from templates
- [ ] SAM.gov API returns opportunities
- [ ] Gmail connector downloads attachments
- [ ] Microsoft 365 connector accesses SharePoint
- [ ] Data ingestion populates CSV
- [ ] Remediation engine retries failed jobs
- [ ] Compliance logs are created

---

## Compliance & Security

### Data Protection

1. **Encryption at Rest**
   - All sensitive data encrypted
   - Keys stored in environment variables or Key Vault

2. **Encryption in Transit**
   - All API calls use HTTPS/TLS
   - OAuth 2.0 for authentication

3. **Access Control**
   - Least privilege principle
   - Role-based access in SharePoint
   - API keys have minimal required scopes

### Audit Logging

All actions logged to:
- `logs/agent_3_orchestrator.log`
- `logs/ingestion_log.json`
- `logs/remediation_log.txt`

Logs include:
- Timestamp
- User/system actor
- Action performed
- Result (success/failure)
- Error details (if applicable)

### Data Retention

- **Operational Logs:** 90 days
- **Financial Records:** 7 years (2555 days)
- **Legal Documents:** Indefinite (with archival)
- **Customer Data:** Per privacy policy

### Backup Strategy

1. **Daily Backups**
   - Automated backup to cloud storage
   - Retention: 30 days

2. **Weekly Full Backup**
   - Complete system snapshot
   - Retention: 1 year

3. **Disaster Recovery**
   - Recovery Time Objective (RTO): 24 hours
   - Recovery Point Objective (RPO): 24 hours

---

## Monitoring & Maintenance

### Health Checks

Agent 3.0 performs self-checks every 5 minutes:

```python
# Check system health
python pillar-a-trading/agent-3.0/agent_3_orchestrator.py --health-check
```

### Performance Monitoring

Key metrics:
- API response times
- Document generation success rate
- Ingestion throughput
- Error rates

### Alerts

Configured in `config/agent_3_config.json`:
- Email: `appsefilepro@gmail.com`
- Teams webhook
- Slack (if enabled)

Alert conditions:
- System offline > 5 minutes
- Error rate > 10%
- Trading loss exceeds threshold
- API rate limits approached

### Maintenance Schedule

**Daily:**
- Review logs for errors
- Check SAM.gov for new opportunities
- Verify backup completion

**Weekly:**
- Review grant pipeline
- Update legal case statuses
- Rotate temporary credentials

**Monthly:**
- Security patch updates
- Review and optimize workflows
- Generate compliance reports

**Quarterly:**
- Rotate API keys
- Full system audit
- Disaster recovery test

---

## Troubleshooting

### Common Issues

**Issue:** Agent 3.0 won't start
**Solution:** Check `.env` file for missing credentials. Verify Python dependencies installed.

**Issue:** Gmail API authentication fails
**Solution:** Re-run OAuth flow. Check credentials.json file. Verify Gmail API enabled in Google Cloud Console.

**Issue:** SharePoint API returns 403 Forbidden
**Solution:** Check Azure AD app permissions. Ensure admin consent granted. Verify client secret hasn't expired.

**Issue:** Zapier webhook not receiving data
**Solution:** Test webhook URL manually with curl. Check Agent 3.0 logs for POST errors. Verify Zapier Zap is turned ON.

**Issue:** Trading signals not executing
**Solution:** Check confidence threshold setting. Verify Kraken API keys have trading permission. Check daily loss limits not exceeded.

**Issue:** Remediation engine shows 0% complete
**Solution:** Check data directories exist. Verify files are in supported formats (.pdf, .xlsx). Review logs for parsing errors.

**Issue:** Legal documents generate with missing data
**Solution:** Verify case_metadata.json exists in case folder. Check all required fields populated. Review template variable names match.

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python pillar-a-trading/agent-3.0/agent_3_orchestrator.py
```

### Getting Help

1. Check logs in `logs/` directory
2. Review this deployment guide
3. Consult API documentation for external services
4. Contact: appsefilepro@gmail.com

---

## Completion Checklist

Use this checklist to verify 100% deployment:

### Infrastructure
- [ ] All directories created
- [ ] Python dependencies installed
- [ ] .env file configured with all credentials
- [ ] Git repository initialized and committed

### API Connections
- [ ] Microsoft 365 authenticated
- [ ] Gmail API configured
- [ ] Zapier webhooks created
- [ ] SAM.gov API key obtained
- [ ] Trading platform API keys set

### Pillar A: Trading
- [ ] Agent 3.0 orchestrator running
- [ ] Candlestick analyzer operational
- [ ] Zapier integration active
- [ ] Test trade signal generated and logged

### Pillar B: Legal
- [ ] SharePoint folders created
- [ ] Templates uploaded
- [ ] Power Automate flow active
- [ ] Test document generated

### Pillar C: Federal Contracting
- [ ] SAM.gov monitor running
- [ ] Email alerts configured
- [ ] SharePoint opportunity list created
- [ ] 8(a) documents prepared

### Pillar D: Grant Intelligence
- [ ] Grant Intelligence SharePoint site created
- [ ] Free tools database populated
- [ ] Weekly digest flow configured
- [ ] Resource library initialized

### Core Systems
- [ ] Data ingestion tested on all sources
- [ ] Remediation engine run successfully
- [ ] customer_contact_list.csv generated
- [ ] Compliance logs verified

### Testing & Validation
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing checklist complete
- [ ] No critical errors in logs

### Security & Compliance
- [ ] Audit logging enabled
- [ ] Encryption configured
- [ ] Backup schedule active
- [ ] Access controls reviewed

---

## Next Steps After Deployment

1. **Week 1: Monitoring**
   - Observe all systems for stability
   - Fine-tune thresholds and parameters
   - Address any immediate issues

2. **Week 2-4: Optimization**
   - Review performance metrics
   - Optimize API call frequency
   - Enhance document templates
   - Add additional trading pairs (if desired)

3. **Month 2: Enhancement**
   - Implement additional features
   - Create custom reports
   - Integrate additional data sources
   - Develop mobile dashboard (optional)

4. **Ongoing:**
   - Regular maintenance per schedule
   - Continuous improvement
   - User feedback integration
   - Security updates

---

## Success Metrics

Track these KPIs to measure system success:

### Trading Operations
- Number of signals generated per day
- Trade execution success rate
- Average confidence score
- P&L performance

### Legal Automation
- Documents generated per week
- Time saved vs. manual drafting
- Attorney review approval rate

### Federal Contracting
- Opportunities identified
- Proposals submitted
- Win rate
- Contract value obtained

### Grant Intelligence
- Grants tracked
- Applications submitted
- Funding secured
- ROI on automation

---

## Conclusion

Agent X2.0 is now deployed at **100% foundation readiness**. The system provides a complete, production-ready codebase for all four pillars plus core data ingestion and remediation capabilities.

**To achieve full operational deployment:**
1. Complete API credential setup for all external services
2. Configure Power Automate flows in Microsoft 365
3. Set up Zapier integrations
4. Run initial data ingestion and remediation
5. Monitor and optimize

For technical support or questions:
**Email:** appsefilepro@gmail.com
**Organization:** APPS Holdings WY Inc.
**Owner:** Thurman Malik Robinson

---

*Document Version: 2.0.0*
*Last Updated: December 5, 2025*
*Classification: Internal Use*
