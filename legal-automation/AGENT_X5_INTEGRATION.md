# AGENT X5 BROWSER INTEGRATION GUIDE

**Deploy Agent X5 across Chrome/Edge extensions with Claude AI integration**

---

## 🌐 Overview

Agent X5 works across:
- **Desktop:** Chrome Extension, Edge Extension
- **Mobile:** Edge Mobile Browser
- **Claude AI:** Full API integration
- **Web Apps:** Progressive Web App (PWA)

---

## 🔧 Chrome Extension Setup

### 1. Install Claude AI Chrome Extension

**Method A: Chrome Web Store**
```
1. Go to: https://chrome.google.com/webstore
2. Search: "Claude AI"
3. Click "Add to Chrome"
4. Pin extension to toolbar
```

**Method B: Developer Mode (Custom)**
```
1. Download extension files
2. Open Chrome → Settings → Extensions
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select extension directory
```

### 2. Configure API Key

```javascript
// In Chrome extension settings
{
  "api_key": "{{CLAUDE_API_KEY}}",
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "temperature": 1.0
}
```

### 3. Custom Prompts for Legal Automation

Create custom prompts in extension:

**Prompt 1: Document Drafter**
```
You are a legal document automation expert. When I provide:
- Document type (complaint, motion, letter)
- Case details (number, parties, court)
- Key facts

Generate a properly formatted legal document following court rules.
```

**Prompt 2: Form Filler**
```
You are an expert at filling government forms. When I provide:
- Form type (1023, grant application, court filing)
- Organization/person details
- Required information

Extract the data and map it to the correct form fields.
```

**Prompt 3: Email Assistant**
```
You are a legal correspondence expert. When I forward an email or provide email text:
- Classify urgency and type
- Extract case numbers and key dates
- Draft appropriate response
- Suggest next actions
```

---

## 🌊 Edge Extension Setup

### Desktop Edge

```
1. Edge is Chromium-based - Chrome extensions work!
2. Go to: edge://extensions/
3. Enable "Allow extensions from other stores"
4. Install Claude AI from Chrome Web Store
```

### Mobile Edge

```
1. Open Edge on Android/iOS
2. Go to: edge://flags
3. Enable: "Mobile Extensions"
4. Restart browser
5. Install extensions as on desktop
```

**Edge Mobile Features:**
- Sync across devices
- Reading mode integration
- Collections for case management
- Built-in screenshot OCR

---

## 🤖 Claude AI Integration

### API Configuration

**File:** `config/claude_config.json`
```json
{
  "api_key": "{{CLAUDE_API_KEY}}",
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "temperature": 1.0,
  "system_prompts": {
    "legal_assistant": "You are Agent X5, a legal automation expert...",
    "document_drafter": "You draft legal documents following court rules...",
    "form_filler": "You fill government forms accurately..."
  }
}
```

### Python Integration

```python
import anthropic
import os
from pathlib import Path

class AgentX5Claude:
    """Agent X5 with Claude AI integration"""

    def __init__(self):
        self.api_key = os.getenv('CLAUDE_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def draft_legal_document(
        self,
        doc_type: str,
        case_data: dict,
        context: str
    ) -> str:
        """Draft legal document using Claude"""

        prompt = f"""
        Document Type: {doc_type}
        Case Number: {case_data.get('case_number')}
        Court: {case_data.get('court')}
        Parties: {case_data.get('plaintiff')} vs {case_data.get('defendant')}

        Context: {context}

        Generate a properly formatted legal {doc_type} following all court rules
        and professional standards.
        """

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return message.content[0].text

    def extract_email_actions(self, email_body: str) -> dict:
        """Extract actionable items from legal email"""

        prompt = f"""
        Analyze this legal email and extract:
        1. Case numbers mentioned
        2. Deadlines and important dates
        3. Required actions
        4. Urgency level
        5. Suggested response

        Email:
        {email_body}

        Return as JSON.
        """

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return message.content[0].text

    def fill_form_fields(
        self,
        form_type: str,
        org_data: dict
    ) -> dict:
        """Generate form field mappings"""

        prompt = f"""
        Form Type: {form_type}
        Organization Data: {org_data}

        Map the organization data to the correct form fields for {form_type}.
        Return as JSON with field names and values.
        """

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return message.content[0].text
```

---

## 🔗 Browser Automation with Selenium

**File:** `browser_automation.py`

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserAutomation:
    """Automate browser for web form filling"""

    def __init__(self, browser='chrome'):
        if browser == 'chrome':
            options = webdriver.ChromeOptions()
            # Load Claude extension
            options.add_extension('path/to/claude_extension.crx')
            self.driver = webdriver.Chrome(options=options)
        elif browser == 'edge':
            options = webdriver.EdgeOptions()
            self.driver = webdriver.Edge(options=options)

    def fill_web_form(
        self,
        url: str,
        field_mappings: dict
    ):
        """Fill web form automatically"""

        self.driver.get(url)
        wait = WebDriverWait(self.driver, 10)

        for field_id, value in field_mappings.items():
            try:
                element = wait.until(
                    EC.presence_of_element_located((By.ID, field_id))
                )
                element.clear()
                element.send_keys(value)
            except Exception as e:
                print(f"Error filling {field_id}: {e}")

    def submit_form(self, submit_button_id: str):
        """Submit web form"""
        submit_btn = self.driver.find_element(By.ID, submit_button_id)
        submit_btn.click()
```

---

## 📱 Progressive Web App (PWA)

### Create PWA Manifest

**File:** `manifest.json`

```json
{
  "name": "Agent X5 Legal Automation",
  "short_name": "Agent X5",
  "description": "Complete legal automation system",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2563eb",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "permissions": [
    "storage",
    "notifications",
    "fileSystem"
  ]
}
```

### Service Worker

**File:** `service-worker.js`

```javascript
// Cache legal documents for offline access
const CACHE_NAME = 'agent-x5-v1';
const urlsToCache = [
  '/',
  '/styles/main.css',
  '/scripts/app.js',
  '/templates/complaint.html',
  '/templates/motion.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

---

## 🔄 Multi-Platform Sync

### Cloud Sync Configuration

**File:** `sync_config.yaml`

```yaml
sync:
  providers:
    - google_cloud_storage
    - sharepoint
    - onedrive

  sync_items:
    - legal_documents/*.pdf
    - completed_forms/*.pdf
    - case_logs/*.json
    - email_drafts/*.txt

  schedule:
    interval: 15  # minutes
    on_change: true

  conflict_resolution: latest_timestamp
```

### Sync Script

```python
from google.cloud import storage
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DocumentSyncHandler(FileSystemEventHandler):
    """Sync legal documents to cloud"""

    def __init__(self, bucket_name):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)

    def on_created(self, event):
        """Upload new document"""
        if event.src_path.endswith('.pdf'):
            self.upload_file(event.src_path)

    def on_modified(self, event):
        """Upload modified document"""
        if event.src_path.endswith('.pdf'):
            self.upload_file(event.src_path)

    def upload_file(self, file_path):
        """Upload to cloud storage"""
        blob = self.bucket.blob(Path(file_path).name)
        blob.upload_from_filename(file_path)
        print(f"✅ Synced: {file_path}")

# Start sync
observer = Observer()
observer.schedule(
    DocumentSyncHandler('legal-docs-bucket'),
    path='../legal-docs/completed',
    recursive=False
)
observer.start()
```

---

## 🎯 Complete Workflow Example

### Scenario: Process Incoming Court Email

**Step 1: Email arrives in Gmail**
```python
# Gmail automation detects new email
gmail = LegalGmailAutomation()
emails = gmail.monitor_legal_inbox()
```

**Step 2: Claude AI analyzes email**
```python
# Extract actions using Claude
agent = AgentX5Claude()
actions = agent.extract_email_actions(email['body'])
```

**Step 3: Auto-generate response**
```python
# Draft response
response = agent.draft_legal_document(
    doc_type='email_response',
    case_data={'case_number': actions['case_number']},
    context=actions['suggested_response']
)
```

**Step 4: Human review in browser**
```
# Chrome extension shows draft
# User can edit and approve
```

**Step 5: Send via Gmail API**
```python
# Send approved response
gmail.send_email(
    to=email['from'],
    subject=f"RE: {email['subject']}",
    body=response
)
```

**Step 6: Sync to cloud**
```python
# Auto-synced via watchdog
# Available on all devices
```

---

## 📊 Dashboard Integration

### Streamlit Dashboard

**File:** `legal_dashboard.py`

```python
import streamlit as st
from master_legal_orchestrator import MasterLegalOrchestrator

st.set_page_config(
    page_title="Agent X5 Legal Dashboard",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Agent X5 Legal Automation Dashboard")

# Initialize orchestrator
orchestrator = MasterLegalOrchestrator()

# Sidebar
with st.sidebar:
    st.header("Quick Actions")
    if st.button("Run Probate Workflow"):
        with st.spinner("Processing..."):
            orchestrator.execute_probate_case_workflow()
        st.success("Workflow complete!")

    if st.button("Download IRS Forms"):
        with st.spinner("Downloading..."):
            orchestrator.pdf_automation.batch_download_forms()
        st.success("Forms downloaded!")

# Main area
col1, col2 = st.columns(2)

with col1:
    st.subheader("Case No. 1241511")
    st.json(orchestrator.probate_case)

with col2:
    st.subheader("Nonprofit Data")
    st.json(orchestrator.nonprofit_data)

# Metrics
st.subheader("System Status")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Gmail", "✅ Connected")
col2.metric("PDF Tools", "✅ Ready")
col3.metric("Scraper", "✅ Active")
col4.metric("AI Tools", "4 Integrated")
```

Run with:
```bash
streamlit run legal_dashboard.py
```

---

## 🔐 Security Best Practices

1. **API Keys:** Store in environment variables
   ```bash
   export CLAUDE_API_KEY='your_key'
   export GOOGLE_CLOUD_PROJECT='your_project'
   ```

2. **OAuth Tokens:** Never commit to Git
   ```bash
   echo "*.pickle" >> .gitignore
   echo "config/gmail_credentials.json" >> .gitignore
   ```

3. **Encryption:** Encrypt sensitive documents
   ```python
   from cryptography.fernet import Fernet

   key = Fernet.generate_key()
   cipher = Fernet(key)
   encrypted = cipher.encrypt(pdf_data)
   ```

4. **Access Control:** Implement role-based access
   ```python
   ROLES = {
       'admin': ['read', 'write', 'delete', 'send'],
       'user': ['read', 'write'],
       'viewer': ['read']
   }
   ```

---

## 📞 Support & Resources

**Documentation:**
- Claude API: https://docs.anthropic.com/
- Chrome Extensions: https://developer.chrome.com/docs/extensions/
- Edge Extensions: https://docs.microsoft.com/en-us/microsoft-edge/extensions-chromium/

**Community:**
- Claude Discord: https://discord.gg/claude-ai
- Legal Tech Forum: https://www.legaltech.com/

---

**Last Updated:** December 23, 2025
**Version:** 1.0.0
**Contact:** terobinsonwy@gmail.com
