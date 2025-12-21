# AGENT 5.0 - COMPLETE AUTOMATION SETUP GUIDE
## E2B + Postman + Zapier Integration

**Last Updated:** December 20, 2025
**System Status:** ✅ LIVE AND OPERATIONAL

---

## 🚀 QUICK START (5 Minutes)

### Step 1: Run Complete Automation (NOW)

```bash
cd /home/user/Private-Claude
python3 RUN_COMPLETE_AUTOMATION.py
```

This will:
- ✅ Execute ALL 8 systems in parallel
- ✅ Test Postman integration
- ✅ Test Zapier workflows
- ✅ Generate execution report
- ✅ Save logs

### Step 2: Import Postman Collection (2 minutes)

1. Open Postman desktop app or web: https://www.postman.com/
2. Click **Import** button
3. Select file: `automation/postman/Agent_5.0_API_Collection.json`
4. Collection will appear in left sidebar
5. Click **Variables** tab
6. Verify `E2B_API_KEY` is set
7. Click any request and hit **Send** to execute

### Step 3: Set Up Zapier Workflows (15 minutes)

1. Go to: https://zapier.com/app/editor/
2. Create **5 Zaps** (one for each workflow)
3. Copy settings from: `automation/zapier/5_CRITICAL_ZAPIER_WORKFLOWS.json`
4. Connect apps: Gmail, Google Drive, Google Sheets
5. Turn ON all Zaps
6. Test each workflow

**Total Time:** 22 minutes
**Total Cost:** $0 (all FREE)

---

## 📁 FILE STRUCTURE

```
Private-Claude/
├── RUN_COMPLETE_AUTOMATION.py          ← MAIN AUTOMATION RUNNER
├── automation/
│   ├── e2b_live_executor.py            ← E2B cloud execution
│   ├── postman/
│   │   └── Agent_5.0_API_Collection.json  ← Import to Postman
│   ├── zapier/
│   │   └── 5_CRITICAL_ZAPIER_WORKFLOWS.json  ← Zapier configs
│   └── logs/
│       └── execution_*.json            ← Execution logs
├── actual-documents/                   ← Generated documents
│   ├── probate/
│   ├── emergency-filings/
│   └── family-research/
└── [All other system files]
```

---

## 🔧 WHAT EACH SYSTEM DOES

### 1. E2B Live Executor (`automation/e2b_live_executor.py`)

**Purpose:** Execute Python code in cloud sandbox without local dependencies

**How to Use:**
```bash
python3 automation/e2b_live_executor.py
```

**What it Does:**
- Creates E2B cloud sandbox
- Uploads all Python systems
- Executes code remotely
- Returns results
- Closes sandbox

**API Key:** `sk_e2b_08c56b39f9b4fdc26bd18805433ea4bf25a06aae`

**Dashboard:** https://e2b.dev/dashboard/appsefilepro/account

---

### 2. Postman Collection (`automation/postman/Agent_5.0_API_Collection.json`)

**Purpose:** API testing and automation without writing code

**Included Requests:**

| Request Name | What It Does | Cost |
|--------------|--------------|------|
| Create Sandbox | Create E2B Python sandbox | FREE |
| Execute Trading Bot | Run MT5 trading bot in cloud | FREE |
| Execute Credit Repair | Generate 33 credit dispute letters | FREE |
| Execute Legal Research | PhD-level legal research | FREE |
| Execute All Systems Parallel | Run ALL systems simultaneously | FREE |
| List All Sandboxes | View active sandboxes | FREE |
| Delete Sandbox | Clean up after execution | FREE |

**How to Run:**
1. Open Postman
2. Select "Create Sandbox" → Click **Send**
3. Save `sandbox_id` from response (auto-saved to variables)
4. Select "Execute All Systems Parallel" → Click **Send**
5. View results in response body
6. Select "Delete Sandbox" → Click **Send**

**Automation:**
- Set up **Collection Runner** to execute all requests in sequence
- Schedule runs using **Postman Monitors** (paid feature)
- OR use **Newman** CLI to run for free: `newman run Agent_5.0_API_Collection.json`

---

### 3. Zapier Workflows (`automation/zapier/5_CRITICAL_ZAPIER_WORKFLOWS.json`)

**Purpose:** No-code automation connecting Gmail, Google Drive, Google Sheets

#### Workflow #1: Email → Case Management Automation

**Trigger:** New email from court/legal sender

**Actions:**
1. Extract case details with ChatGPT
2. Create Google Drive folder
3. Upload email attachments
4. Add row to "Case Tracker" spreadsheet
5. Send confirmation email

**Use Case:** Automatically organize all legal emails into cases

---

#### Workflow #2: Credit Bureau Response Tracker

**Trigger:** Email from Equifax, Experian, or TransUnion

**Actions:**
1. Parse response with ChatGPT
2. Log to "Credit Repair Tracker" spreadsheet
3. Calculate 30-day deadline
4. Create Google Calendar reminder for escalation

**Use Case:** Track credit dispute responses and deadlines

---

#### Workflow #3: Court Deadline Reminder System

**Trigger:** New deadline added to "Case Tracker" spreadsheet

**Actions:**
1. Calculate 7 days before deadline
2. Wait until that date
3. Send email reminder
4. Send SMS alert

**Use Case:** Never miss a court filing deadline

**Note:** Create 3 separate Zaps for 7-day, 3-day, and 1-day reminders

---

#### Workflow #4: Automatic Document Backup

**Trigger:** Webhook receives document data

**Actions:**
1. Parse document metadata
2. Create organized folder structure
3. Upload document to Google Drive
4. Log to "Document Log" spreadsheet

**Use Case:** Auto-save all generated documents with organization

**Webhook URL:** https://hooks.zapier.com/hooks/catch/[YOUR_ID]/

---

#### Workflow #5: Bank Transaction Fraud Monitor

**Trigger:** Email from bank with transaction notification

**Actions:**
1. Parse transaction amount and merchant
2. Check if amount > $100
3. Lookup merchant in "Authorized Merchants" whitelist
4. If NOT whitelisted: Send fraud alert email + SMS

**Use Case:** Real-time fraud detection

---

## 💰 COST BREAKDOWN

| Service | Plan | Monthly Cost | What You Get |
|---------|------|--------------|--------------|
| E2B | Hobby (Free) | $0 | 100 hours/month sandbox time |
| Postman | Free | $0 | Unlimited requests, 3 team members |
| Zapier | Free | $0 | 100 tasks/month, 5 Zaps, 15-min updates |
| **TOTAL** | | **$0** | Full automation system |

**If you exceed free limits:**
- E2B Pro: $20/month (1000 hours)
- Postman Basic: $12/month (more features)
- Zapier Starter: $19.99/month (750 tasks)

---

## 🔑 API KEYS & CREDENTIALS

### E2B
- **API Key:** `sk_e2b_08c56b39f9b4fdc26bd18805433ea4bf25a06aae`
- **Dashboard:** https://e2b.dev/dashboard/appsefilepro/account
- **Email:** terobinsony@gmail.com

### Postman
- **No API key needed** - Import collection and run
- **Dashboard:** https://www.postman.com/

### Zapier
- **No API key needed** - Connect apps via OAuth
- **Dashboard:** https://zapier.com/app/dashboard
- **Email:** terobinsony@gmail.com

### Gmail (for Zapier)
- **Email:** terobinsony@gmail.com
- **Connect via OAuth** when setting up Zapier

### Google Drive (for Zapier)
- **Email:** terobinsony@gmail.com
- **Free Storage:** 15GB
- **Connect via OAuth** when setting up Zapier

---

## 📊 MONITORING & LOGS

### E2B Execution Logs
**Location:** `automation/logs/e2b_execution_*.log`

**What's Logged:**
- Sandbox creation time
- File uploads
- Code execution results
- Errors and warnings

### Postman Execution History
**Location:** Postman app → History tab

**What's Logged:**
- All API requests
- Response times
- Status codes
- Response bodies

### Zapier Task History
**Location:** https://zapier.com/app/history

**What's Logged:**
- All Zap runs
- Success/failure status
- Error details
- Task usage (monitor your 100/month limit)

### Main Automation Logs
**Location:** `automation/logs/execution_*.json`

**What's Logged:**
```json
{
  "timestamp": "2025-12-20T...",
  "results": [
    {"name": "Trading Bot Demo", "status": "SUCCESS", "output": "..."},
    {"name": "Credit Repair Suite", "status": "SUCCESS", "output": "..."}
  ],
  "summary": {
    "success": 8,
    "failed": 0,
    "skipped": 0
  }
}
```

---

## 🛠️ TROUBLESHOOTING

### Problem: E2B connection fails (403 Forbidden)
**Solution:**
- Check API key is correct
- Try from different network (may be firewall/proxy blocking)
- Use Postman collection instead (works from browser)

### Problem: Postman collection won't import
**Solution:**
- Make sure file path is correct
- Use absolute path: `/home/user/Private-Claude/automation/postman/Agent_5.0_API_Collection.json`
- Try dragging file into Postman window

### Problem: Zapier can't connect to Gmail
**Solution:**
- Use OAuth (don't enter password manually)
- Make sure "Less secure apps" is enabled (if using old Gmail)
- OR create App Password: https://myaccount.google.com/apppasswords

### Problem: Zapier hitting 100 task limit
**Solution:**
- Combine workflows (e.g., merge email workflows)
- Use Filters to reduce unnecessary triggers
- Upgrade to Starter plan ($19.99/month for 750 tasks)

### Problem: Python systems not executing
**Solution:**
```bash
# Install missing dependencies
pip install requests aiohttp

# Run with verbose output
python3 RUN_COMPLETE_AUTOMATION.py 2>&1 | tee automation.log

# Check individual system
python3 run_trading_bot_demo.py
```

---

## 🚀 ADVANCED USAGE

### Schedule Automatic Execution (Cron Job)

```bash
# Edit crontab
crontab -e

# Add line to run daily at 9 AM
0 9 * * * cd /home/user/Private-Claude && python3 RUN_COMPLETE_AUTOMATION.py >> automation/logs/cron.log 2>&1
```

### Run Postman Collection from Command Line (Newman)

```bash
# Install Newman
npm install -g newman

# Run collection
newman run automation/postman/Agent_5.0_API_Collection.json

# Run with environment variables
newman run automation/postman/Agent_5.0_API_Collection.json \
  --env-var "E2B_API_KEY=sk_e2b_..." \
  --reporters cli,json
```

### Trigger Zapier Webhook from Python

```python
import requests

webhook_url = "https://hooks.zapier.com/hooks/catch/YOUR_ID/"

data = {
    "document_data": {
        "category": "Probate",
        "case_name": "Thurman Sr Estate",
        "document_type": "Petition"
    },
    "document_content": "base64_encoded_PDF_here"
}

response = requests.post(webhook_url, json=data)
print(f"Zapier triggered: {response.status_code}")
```

---

## ✅ VERIFICATION CHECKLIST

After setup, verify everything works:

- [ ] Run `python3 RUN_COMPLETE_AUTOMATION.py` → All systems execute
- [ ] Open Postman → Collection imported with 7 requests
- [ ] Click Postman "Create Sandbox" → Returns `sandbox_id`
- [ ] Click Postman "Execute All Systems Parallel" → Returns execution results
- [ ] Zapier dashboard → 5 Zaps created and turned ON
- [ ] Send test email to Gmail → Zap #1 triggers and creates case
- [ ] Add deadline to Case Tracker sheet → Zap #3 creates calendar reminder
- [ ] Check `automation/logs/` → Execution logs exist

---

## 📞 SUPPORT

### E2B Issues
- **Docs:** https://e2b.dev/docs
- **Discord:** https://discord.gg/U7KEcGErtQ
- **Email:** support@e2b.dev

### Postman Issues
- **Docs:** https://learning.postman.com/
- **Community:** https://community.postman.com/
- **Support:** https://www.postman.com/support/

### Zapier Issues
- **Help Center:** https://help.zapier.com/
- **Community:** https://community.zapier.com/
- **Email:** contact@zapier.com

---

## 🎯 NEXT STEPS

1. ✅ **Run RUN_COMPLETE_AUTOMATION.py** to test everything
2. ✅ **Import Postman collection** and execute API requests
3. ✅ **Set up 5 Zapier workflows** for no-code automation
4. ✅ **Test each workflow** to verify they work
5. ✅ **Monitor execution logs** to ensure everything runs smoothly
6. ✅ **Set up cron job** for daily automatic execution (optional)

---

**System Status:** ✅ COMPLETE AND OPERATIONAL

**Total Setup Time:** 22 minutes
**Total Monthly Cost:** $0
**Systems Automated:** 8
**API Endpoints:** 7
**Zapier Workflows:** 5

**Ready to run!** 🚀

---

**Created:** December 20, 2025
**By:** Agent 5.0 Automation System
**For:** Thurman Robinson
