# LEGAL AUTOMATION SYSTEM - QUICK START GUIDE

**Get up and running with the complete legal automation system in 15 minutes**

---

## 🚀 System Overview

This system provides complete automation for:

✅ **Probate Case Management** (Case No. 1241511)
✅ **Gmail Legal Correspondence**
✅ **PDF Form Filling** (Form 1023, Grant Applications)
✅ **Government Template Scraping**
✅ **AI-Powered Document Drafting**
✅ **Nonprofit Operations**

---

## 📋 Prerequisites

- Python 3.7 or higher
- Gmail account (terobinsonwy@gmail.com)
- Git installed
- 30 minutes for setup

---

## ⚡ Quick Installation (5 minutes)

### Step 1: Install Dependencies

```bash
# Navigate to legal-automation directory
cd legal-automation

# Install all required packages
pip install -r requirements.txt
```

### Step 2: Create Config Directory

```bash
mkdir -p config
```

### Step 3: Set Up Gmail OAuth

Follow the complete guide: [GMAIL_OAUTH_SETUP.md](GMAIL_OAUTH_SETUP.md)

**Quick version:**
1. Go to https://console.cloud.google.com/
2. Create new project: "Legal Automation System"
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials → save as `config/gmail_credentials.json`

---

## 🎯 Running the System

### Option 1: Run Master Orchestrator (Recommended)

```bash
python3 master_legal_orchestrator.py
```

**What it does:**
- Initializes all systems
- Processes probate Case No. 1241511
- Downloads IRS forms
- Generates grant applications
- Scrapes government templates
- Creates comprehensive report

### Option 2: Run Individual Components

**Gmail Automation:**
```bash
python3 gmail_automation.py
```

**PDF Form Automation:**
```bash
python3 pdf_form_automation.py
```

**Template Scraper:**
```bash
python3 template_scraper.py
```

---

## 📧 Probate Case No. 1241511 - Immediate Actions

### Send Dismissal Notifications

1. **Review generated PDF:**
   ```bash
   ls -l ../legal-docs/completed/Dismissal_Notice_*.pdf
   ```

2. **Edit recipient list** in `master_legal_orchestrator.py`:
   ```python
   # Line ~447
   recipients = [
       'terobinsonwy@gmail.com',
       # Add other stakeholders here
   ]
   ```

3. **Uncomment send code** (Line ~448-451):
   ```python
   if self.gmail and self.gmail.service:
       self.gmail.send_probate_dismissal_notice(recipients)
   ```

4. **Run workflow:**
   ```bash
   python3 master_legal_orchestrator.py
   ```

---

## 📄 Generate Nonprofit Forms

### Form 1023-EZ (501c3 Application)

```python
from pdf_form_automation import PDFFormAutomation

pdf = PDFFormAutomation()

# Customize organization data
org_data = {
    'organization_name': 'APPS HOLDINGS WY INC',
    'ein': 'XX-XXXXXXX',  # Add your EIN
    'address': '6301 Pale Sage Dr - 3206',
    'city': 'Houston',
    'state': 'Texas',
    'zip': '77079',
    'contact_person': 'Thurman Robinson',
    'email': 'terobinsonwy@gmail.com',
    'phone': '972-247-0653'
}

# Generate form
form_path = pdf.fill_form_1023_ez(org_data)
print(f"Form generated: {form_path}")
```

### Texas Grant Applications

```python
# Opioid grant
pdf.fill_texas_grant_application('opioid', org_data)

# Cybersecurity grant
pdf.fill_texas_grant_application('cybersecurity', org_data)
```

---

## 🤖 Activate Free AI Tools

The system integrates with these free AI tools:

1. **CaseMark** (https://casemark.ai)
   - Free tier: 10 documents/month
   - Use for: Legal document drafting

2. **Spellbook** (https://www.spellbook.legal)
   - Free trial: 14 days
   - Use for: Contract review

3. **Harvey AI** (https://harvey.ai)
   - Free trial: 7 days
   - Use for: Legal research

4. **Jotform AI** (https://www.jotform.com/ai/)
   - Free tier: 100 submissions/month
   - Use for: Form automation

### Activation Steps:

1. **Sign up** for each tool
2. **Get API keys** where available
3. **Add to config:**
   ```bash
   # Create .env file
   cat > config/.env << EOF
   CASEMARK_API_KEY=your_key_here
   SPELLBOOK_API_KEY=your_key_here
   HARVEY_API_KEY=your_key_here
   JOTFORM_API_KEY=your_key_here
   EOF
   ```

---

## 📂 Directory Structure

```
legal-automation/
├── gmail_automation.py          # Gmail integration
├── pdf_form_automation.py       # PDF form filling
├── template_scraper.py          # Government template scraper
├── master_legal_orchestrator.py # Master controller
├── requirements.txt             # Dependencies
├── QUICKSTART.md               # This file
├── GMAIL_OAUTH_SETUP.md        # Gmail setup guide
└── config/
    ├── gmail_credentials.json   # OAuth credentials
    ├── gmail_token.pickle       # Auth token (auto-generated)
    └── .env                     # API keys

../legal-docs/
├── forms/                       # Downloaded government forms
│   ├── form_1023.pdf
│   └── form_1023ez.pdf
├── completed/                   # Generated documents
│   ├── Dismissal_Notice_1241511_*.pdf
│   ├── Form_1023EZ_completed_*.pdf
│   └── Texas_*_grant_*.pdf
└── templates/                   # Scraped templates
    └── scrape_results_*.json

../logs/legal-automation/
├── probate_workflow_*.json      # Workflow logs
└── master_report_*.json         # System reports
```

---

## ✅ Testing the System

### Test 1: Gmail Authentication

```bash
python3 -c "
from gmail_automation import LegalGmailAutomation
gmail = LegalGmailAutomation()
if gmail.authenticate():
    print('✅ Gmail working!')
else:
    print('❌ Setup needed')
"
```

### Test 2: PDF Generation

```bash
python3 -c "
from pdf_form_automation import PDFFormAutomation
pdf = PDFFormAutomation()
case = {
    'case_number': '1241511',
    'court': 'Harris County',
    'plaintiff': 'NEW FOREST HOUSTON 2020 LLC',
    'defendant': 'THURMAN ROBINSON, ET AL.',
    'status': 'DISMISSED'
}
path = pdf.generate_dismissal_letter_pdf(case)
print(f'✅ PDF created: {path}')
"
```

### Test 3: Template Scraping

```bash
python3 -c "
from template_scraper import GovernmentTemplateScraper
scraper = GovernmentTemplateScraper()
results = scraper.scrape_page('https://www.txcourts.gov/')
print(f'✅ Found {results[\"link_count\"]} links')
"
```

---

## 🔄 Run Automated Loop (Agent X5 Style)

```python
from master_legal_orchestrator import MasterLegalOrchestrator

# Initialize
orchestrator = MasterLegalOrchestrator()
orchestrator.initialize_all_systems()

# Run 10 iterations
orchestrator.run_complete_automation_loop(iterations=10)
```

---

## 📊 Monitor Results

### View Generated Documents

```bash
# Dismissal notices
ls -lh ../legal-docs/completed/Dismissal_*.pdf

# Grant applications
ls -lh ../legal-docs/completed/Texas_*.pdf

# Downloaded forms
ls -lh ../legal-docs/forms/
```

### View Logs

```bash
# Probate workflow logs
cat ../logs/legal-automation/probate_workflow_latest.json | jq

# Master report
cat ../logs/legal-automation/master_report_latest.json | jq
```

---

## 🔧 Troubleshooting

### Issue: Gmail Authentication Fails

**Solution:**
1. Check `config/gmail_credentials.json` exists
2. Delete `config/gmail_token.pickle`
3. Re-run authentication
4. See [GMAIL_OAUTH_SETUP.md](GMAIL_OAUTH_SETUP.md)

### Issue: PDF Generation Error

**Solution:**
```bash
# Reinstall PDF libraries
pip install --upgrade PyPDF2 reportlab fillpdf
```

### Issue: Template Scraping Fails

**Solution:**
```bash
# Check internet connection
ping google.com

# Install/update BeautifulSoup
pip install --upgrade beautifulsoup4 lxml
```

### Issue: Missing Dependencies

**Solution:**
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 🚀 Advanced Features

### Custom Email Templates

Edit `gmail_automation.py` line ~195 to customize email body

### Custom PDF Templates

Create new templates in `pdf_form_automation.py`

### Add New Scraping Sources

Edit `template_scraper.py` `template_sources` dictionary

---

## 📞 Support & Documentation

**Email:** terobinsonwy@gmail.com
**Case No.:** 1241511

**Documentation:**
- [Master Plan](../LEGAL_AUTOMATION_MASTER_PLAN.md)
- [Gmail Setup](GMAIL_OAUTH_SETUP.md)
- [Error Fixes](../ERROR_FIXES_SUMMARY.md)

**API Documentation:**
- Gmail API: https://developers.google.com/gmail/api
- ReportLab: https://www.reportlab.com/docs/
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/

---

## ✅ Checklist

Before using the system, make sure you have:

- [ ] Installed all dependencies (`pip install -r requirements.txt`)
- [ ] Created `config/` directory
- [ ] Set up Gmail OAuth credentials
- [ ] Authenticated Gmail API (ran `gmail_automation.py`)
- [ ] Reviewed probate case details in master orchestrator
- [ ] Customized organization data for Form 1023
- [ ] Activated free AI tool trials
- [ ] Reviewed and tested all components

---

## 🎯 Next Steps

1. **Complete probate workflow** - Send dismissal notices
2. **File Form 1023-EZ** - Submit to IRS for 501(c)(3) status
3. **Apply for grants** - Submit Texas opioid and cybersecurity grants
4. **Set up automation** - Configure cron jobs for monitoring
5. **Integrate AI tools** - Add CaseMark, Spellbook API keys

---

**System Status:** 🟢 Operational
**Last Updated:** December 23, 2025
**Version:** 1.0.0
