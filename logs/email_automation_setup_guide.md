# Email Data Extraction and Automation System - Setup Guide

## Overview
This system automatically extracts tasks, reminders, deadlines, and document requests from your Gmail inbox and creates actionable items in Google Tasks and Calendar.

**Email**: terobinsonwy@gmail.com

---

## 1. Gmail API Access Setup

### Step 1.1: Enable IMAP Access
1. Go to Gmail Settings: https://mail.google.com/mail/u/0/#settings/fwdandpop
2. Click on "Forwarding and POP/IMAP" tab
3. Enable IMAP access
4. Click "Save Changes"

### Step 1.2: Generate App Password
1. Visit: https://myaccount.google.com/apppasswords
2. Sign in with terobinsonwy@gmail.com
3. Select "Mail" as the app
4. Select "Other (Custom name)" as the device
5. Enter: "Private Claude Email Automation"
6. Click "Generate"
7. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)
8. Save this password - you won't see it again!

**Important**: App passwords only work if 2-Step Verification is enabled on your Google account.

### Step 1.3: Enable 2-Step Verification (if not already enabled)
1. Visit: https://myaccount.google.com/signinoptions/two-step-verification
2. Follow the prompts to set up 2-Step Verification
3. Once enabled, return to Step 1.2 to generate the app password

### Step 1.4: Update .env File
Open `/home/user/Private-Claude/config/.env` and update:

```bash
GOOGLE_EMAIL=terobinsonwy@gmail.com
GOOGLE_APP_PASSWORD=your_16_char_app_password_here
```

Remove spaces from the app password (e.g., `xxxxyyyyzzzzaaaa`)

---

## 2. Google API OAuth2 Setup (Optional - for advanced features)

### Step 2.1: Create Google Cloud Project
1. Visit: https://console.cloud.google.com/
2. Create a new project or select existing one
3. Name it: "Private Claude Integration"

### Step 2.2: Enable Required APIs
Enable these APIs in your project:
- Gmail API
- Google Calendar API
- Google Tasks API
- Google Drive API
- Google Sheets API

Visit: https://console.cloud.google.com/apis/library

### Step 2.3: Create OAuth2 Credentials
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "Private Claude Desktop"
5. Download the JSON file
6. Extract these values:
   - `client_id`
   - `client_secret`

### Step 2.4: Update .env File
```bash
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

---

## 3. Zapier Integration Setup

### Step 3.1: Create Zapier Account
1. Sign up at: https://zapier.com/
2. Use the same email: terobinsonwy@gmail.com

### Step 3.2: Create Task Creation Zap

**Zap 1: Email Task to Google Tasks**
1. Trigger: Webhooks by Zapier → "Catch Hook"
2. Copy the webhook URL
3. Action: Google Tasks → "Create Task"
4. Map fields:
   - Task List: Choose your list
   - Title: `{{title}}`
   - Notes: `{{description}}`
   - Due Date: `{{due_date}}` (if available)

5. Test the Zap
6. Turn it on

**Save the webhook URL to .env**:
```bash
ZAPIER_TASK_WEBHOOK=https://hooks.zapier.com/hooks/catch/XXXXXX/YYYYYY/
```

### Step 3.3: Create Reminder Zap

**Zap 2: Email Reminder to Google Calendar**
1. Trigger: Webhooks by Zapier → "Catch Hook"
2. Copy the webhook URL
3. Action: Google Calendar → "Create Detailed Event"
4. Map fields:
   - Calendar: Choose your calendar
   - Event Title: `Email Reminder: {{reminder}}`
   - Description: `{{reminder}}`
   - Start Date & Time: `{{start_time}}` or use current time + 1 hour
   - End Date & Time: `{{end_time}}` or start + 30 minutes
   - Reminder: 30 minutes before

5. Test the Zap
6. Turn it on

**Save the webhook URL to .env**:
```bash
ZAPIER_REMINDER_WEBHOOK=https://hooks.zapier.com/hooks/catch/XXXXXX/ZZZZZZ/
```

### Step 3.4: Create Agent 5.0 Integration Zap (Optional)

**Zap 3: Email Data to Agent 5.0**
1. Trigger: Webhooks by Zapier → "Catch Hook"
2. Copy the webhook URL
3. Action: Webhooks by Zapier → "POST"
4. Configure to send to your Agent 5.0 endpoint
5. Test and turn on

**Save the webhook URL to .env**:
```bash
AGENT_5_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/XXXXXX/AAAAAA/
```

---

## 4. Directory Structure

The system creates and uses these directories:

```
/home/user/Private-Claude/
├── config/
│   └── .env                          # Environment variables
├── scripts/
│   ├── email_data_extractor.py       # Core extraction logic
│   └── email_automation_runner.py    # Scheduled automation
├── data/
│   └── email_tasks/
│       ├── tasks/                    # Extracted tasks (JSON)
│       ├── reminders/                # Extracted reminders (JSON)
│       ├── documents/                # Document requests (JSON)
│       ├── processed_emails/         # Email metadata (JSON)
│       └── logs/                     # Automation run logs
└── logs/
    ├── email_automation_setup_guide.md
    └── email_automation_live_test.json
```

---

## 5. Running the System

### Option A: Run Once (Manual Test)

Process the last 20 unread emails:
```bash
cd /home/user/Private-Claude
python3 scripts/email_data_extractor.py
```

### Option B: Run Automation Once

Process up to 10 unread emails:
```bash
cd /home/user/Private-Claude
python3 scripts/email_automation_runner.py --once --limit 20
```

### Option C: Run Continuously (Production Mode)

Process emails every hour:
```bash
cd /home/user/Private-Claude
python3 scripts/email_automation_runner.py --continuous --interval 60 --limit 10
```

Run in background with nohup:
```bash
nohup python3 scripts/email_automation_runner.py --continuous --interval 60 --limit 10 > logs/email_automation.log 2>&1 &
```

---

## 6. Testing the System

### Test 1: Basic Connection
```bash
python3 -c "
from scripts.email_data_extractor import EmailDataExtractor
extractor = EmailDataExtractor()
imap = extractor.connect_to_gmail()
if imap:
    print('✅ Gmail connection successful!')
    imap.logout()
else:
    print('❌ Gmail connection failed')
"
```

### Test 2: Send Test Email to Yourself

Send an email to terobinsonwy@gmail.com with this content:

```
Subject: Test - Task Extraction

Hi there,

Here are some things I need to do:

TODO: Review the quarterly financial report
TODO: Schedule meeting with the team for next week
- Prepare presentation slides
- Update project documentation

Please send me the following documents:
- Form 1023 for tax-exempt status
- W-2 forms for 2024

Deadline: Submit everything by December 31, 2024

Remind me to follow up with the client on Friday.

Thanks!
```

### Test 3: Run Extraction

```bash
python3 scripts/email_automation_runner.py --once --limit 5
```

Expected output:
- 2-4 tasks extracted from TODO items and bullet points
- 1 reminder extracted ("follow up with the client")
- 2 documents identified (Form 1023, W-2 forms)
- 1 deadline extracted (December 31, 2024)

### Test 4: Verify Results

Check the data directory:
```bash
ls -lah /home/user/Private-Claude/data/email_tasks/tasks/
ls -lah /home/user/Private-Claude/data/email_tasks/reminders/
ls -lah /home/user/Private-Claude/data/email_tasks/documents/
ls -lah /home/user/Private-Claude/data/email_tasks/processed_emails/
```

View today's tasks:
```bash
cat /home/user/Private-Claude/data/email_tasks/tasks/tasks_$(date +%Y%m%d).json
```

---

## 7. What Gets Extracted

### Tasks
The system identifies tasks from these patterns:
- **TODO/To do**: "TODO: Review the report"
- **Action verbs**: "Please submit the form", "Need to call John"
- **Bullet points**: "- Update documentation"
- **Numbered lists**: "1. Prepare slides"

### Reminders
Detected from patterns like:
- "Remind me to..."
- "Don't forget to..."
- "Follow up on..."
- "Check in with..."

### Deadlines
Extracted from:
- "Due by December 31, 2024"
- "Deadline: 12/31/2024"
- "Before 2024-12-31"

### Documents
Identified from:
- Document types: "form", "document", "file", "PDF", "contract", "agreement"
- Tax forms: "W-2", "1099", "1040", "Form 1023"
- Action verbs: "send", "attach", "submit", "need", "require"

---

## 8. Zapier Webhook Testing

### Test Task Webhook
```bash
curl -X POST https://hooks.zapier.com/hooks/catch/XXXXXX/YYYYYY/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task from Email Automation",
    "description": "This is a test task created via webhook",
    "source": "email",
    "created_at": "2024-12-22T20:00:00Z"
  }'
```

### Test Reminder Webhook
```bash
curl -X POST https://hooks.zapier.com/hooks/catch/XXXXXX/ZZZZZZ/ \
  -H "Content-Type: application/json" \
  -d '{
    "reminder": "Follow up on test automation",
    "created_at": "2024-12-22T20:00:00Z"
  }'
```

Check your Google Tasks and Google Calendar to verify the items were created.

---

## 9. Automation Schedule

### Using Cron (Linux/Mac)

Edit crontab:
```bash
crontab -e
```

Add this line to run every hour:
```
0 * * * * cd /home/user/Private-Claude && python3 scripts/email_automation_runner.py --once --limit 10 >> logs/email_cron.log 2>&1
```

Run every 30 minutes:
```
*/30 * * * * cd /home/user/Private-Claude && python3 scripts/email_automation_runner.py --once --limit 10 >> logs/email_cron.log 2>&1
```

### Using systemd (Linux)

Create service file: `/etc/systemd/system/email-automation.service`

```ini
[Unit]
Description=Email Automation Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/user/Private-Claude
ExecStart=/usr/bin/python3 /home/user/Private-Claude/scripts/email_automation_runner.py --continuous --interval 60 --limit 10
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl enable email-automation.service
systemctl start email-automation.service
systemctl status email-automation.service
```

---

## 10. Monitoring and Logs

### Check Automation Logs
```bash
# View latest runs
tail -f /home/user/Private-Claude/data/email_tasks/logs/automation_runs.json

# View continuous mode logs
tail -f /home/user/Private-Claude/logs/email_automation.log
```

### Log Format
Each run creates a JSON entry:
```json
{
  "status": "success",
  "emails_processed": 5,
  "tasks_created": 8,
  "reminders_created": 2,
  "documents_identified": 3,
  "duration_seconds": 2.45,
  "timestamp": "2024-12-22T20:30:00Z"
}
```

---

## 11. Troubleshooting

### Issue: "Gmail connection error"
- **Cause**: Invalid app password or IMAP not enabled
- **Solution**:
  1. Verify IMAP is enabled in Gmail settings
  2. Generate a new app password
  3. Update .env file
  4. Remove spaces from app password

### Issue: "No unread emails found" but inbox has unread emails
- **Cause**: Emails might be in other folders
- **Solution**: Check that emails are in the main INBOX, not in labels/folders

### Issue: "Zapier webhook failed: 404"
- **Cause**: Invalid webhook URL
- **Solution**:
  1. Verify the webhook URL in Zapier
  2. Ensure the Zap is turned ON
  3. Test the webhook in Zapier dashboard

### Issue: Tasks not appearing in Google Tasks
- **Cause**: Zapier Zap not configured correctly
- **Solution**:
  1. Check Zap history in Zapier dashboard
  2. Verify Google Tasks connection
  3. Check task list selection
  4. Test the Zap manually

### Issue: Authentication errors with Google APIs
- **Cause**: OAuth tokens expired or invalid
- **Solution**:
  1. For IMAP: Use app password (simpler)
  2. For OAuth: Regenerate access token
  3. Ensure all required APIs are enabled in Google Cloud Console

---

## 12. Security Best Practices

1. **Never commit .env file to git**
   - Already in .gitignore
   - Contains sensitive credentials

2. **Rotate app passwords regularly**
   - Recommended: Every 90 days
   - Generate new password and update .env

3. **Monitor Zapier usage**
   - Free tier: 100 tasks/month
   - Upgrade if needed for production use

4. **Limit email processing**
   - Use `--limit` to control batch size
   - Prevent rate limiting

5. **Review extracted data**
   - Check JSON files in data/email_tasks/
   - Ensure no sensitive data is logged

---

## 13. Next Steps

1. ✅ Complete Gmail setup (IMAP + App Password)
2. ✅ Update .env file with credentials
3. ✅ Send test email to yourself
4. ✅ Run basic extraction test
5. ✅ Set up Zapier webhooks
6. ✅ Test webhook integration
7. ✅ Run automation in continuous mode
8. ✅ Set up cron or systemd for scheduling
9. ✅ Monitor logs for errors
10. ✅ Optimize patterns for your email style

---

## 14. Support and Documentation

- **System Files**:
  - `/home/user/Private-Claude/scripts/email_data_extractor.py`
  - `/home/user/Private-Claude/scripts/email_automation_runner.py`
  - `/home/user/Private-Claude/config/connectors/email.json`
  - `/home/user/Private-Claude/config/connectors/google_workspace.json`

- **Data Location**:
  - `/home/user/Private-Claude/data/email_tasks/`

- **Logs**:
  - `/home/user/Private-Claude/logs/`

---

## 15. Example Workflow

1. **Email arrives** at terobinsonwy@gmail.com with action items
2. **Automation runs** (every hour via cron or continuous mode)
3. **System scans** inbox for unread emails
4. **Extracts data**:
   - Tasks from TODO items and action verbs
   - Reminders from "remind me" phrases
   - Deadlines from date patterns
   - Documents from form/file mentions
5. **Creates items**:
   - Sends tasks to Zapier → Google Tasks
   - Sends reminders to Zapier → Google Calendar
   - Saves documents requests locally
   - Logs processed email
6. **Sends to Agent 5.0** (optional) for further processing
7. **Logs results** to JSON file
8. **You receive**:
   - Google Tasks notification
   - Google Calendar reminder
   - All data saved locally

---

**Setup Guide Version**: 1.0
**Last Updated**: 2024-12-22
**Email**: terobinsonwy@gmail.com
**Status**: Ready for deployment
