# Email Automation System - Quick Start Guide

**System Status**: READY FOR ACTIVATION
**Email Account**: terobinsonwy@gmail.com
**Deployment Date**: 2025-12-22
**Version**: 1.0.0

---

## What Was Deployed

A complete email data extraction and automation system that:
- Connects to Gmail via IMAP
- Automatically extracts tasks, reminders, deadlines, and document requests from emails
- Creates tasks in Google Tasks (via Zapier)
- Sets reminders in Google Calendar (via Zapier)
- Sends data to Agent 5.0 for AI processing
- Runs on a schedule (hourly, or custom interval)
- Saves all data locally as JSON

**Test Results**: Successfully extracted 44 tasks, 7 reminders, 8 documents, and 4 deadlines from 5 sample emails.

---

## Quick Start (3 Steps)

### Step 1: Set Up Gmail (Required)

1. **Enable IMAP**: https://mail.google.com/mail/u/0/#settings/fwdandpop
   - Go to "Forwarding and POP/IMAP" tab
   - Enable IMAP
   - Save changes

2. **Enable 2-Step Verification**: https://myaccount.google.com/signinoptions/two-step-verification
   - Follow prompts to enable (if not already enabled)

3. **Generate App Password**: https://myaccount.google.com/apppasswords
   - Select "Mail" app
   - Select "Other (Custom name)" device
   - Enter: "Private Claude Email Automation"
   - Click "Generate"
   - Copy the 16-character password (remove spaces)

4. **Update .env file**:
   ```bash
   nano /home/user/Private-Claude/config/.env
   ```

   Find this line and replace with your app password:
   ```
   GOOGLE_APP_PASSWORD=your_16_char_app_password_here
   ```

### Step 2: Test the System

Send yourself a test email to terobinsonwy@gmail.com:

```
Subject: Test - Email Automation

Hi,

Here are my tasks:
TODO: Review the quarterly report by Friday
TODO: Schedule team meeting for next week
- Prepare presentation slides
- Update project documentation

Please send me Form 1023 and the W-2 forms.

Remind me to follow up with John next Monday.

Thanks!
```

Then run:
```bash
cd /home/user/Private-Claude
python3 scripts/email_automation_runner.py --once --limit 5
```

Expected output:
- Multiple tasks extracted
- 1 reminder extracted
- 2 documents identified
- Data saved to `/home/user/Private-Claude/data/email_tasks/`

### Step 3: Set Up Zapier (Optional - For Automation)

1. **Sign up**: https://zapier.com/ (use terobinsonwy@gmail.com)

2. **Create Task Zap**:
   - Trigger: Webhooks → Catch Hook
   - Copy webhook URL
   - Action: Google Tasks → Create Task
   - Map: `title` → Title, `description` → Notes
   - Turn on Zap

3. **Update .env**:
   ```
   ZAPIER_TASK_WEBHOOK=https://hooks.zapier.com/hooks/catch/XXXXX/YYYYY/
   ```

4. **Create Reminder Zap**:
   - Trigger: Webhooks → Catch Hook
   - Copy webhook URL
   - Action: Google Calendar → Create Event
   - Map: `reminder` → Event Title
   - Turn on Zap

5. **Update .env**:
   ```
   ZAPIER_REMINDER_WEBHOOK=https://hooks.zapier.com/hooks/catch/XXXXX/ZZZZZ/
   ```

---

## Running the System

### Option 1: Run Once (Manual)
```bash
cd /home/user/Private-Claude
python3 scripts/email_automation_runner.py --once --limit 10
```
Processes up to 10 unread emails and exits.

### Option 2: Run Continuously (Every Hour)
```bash
cd /home/user/Private-Claude
python3 scripts/email_automation_runner.py --continuous --interval 60 --limit 10
```
Runs forever, processing emails every 60 minutes.

### Option 3: Background Service
```bash
cd /home/user/Private-Claude
nohup python3 scripts/email_automation_runner.py --continuous --interval 60 --limit 10 > logs/email_automation.log 2>&1 &
```
Runs in background, survives terminal disconnection.

### Option 4: Cron Job (Every Hour)
```bash
crontab -e
```
Add this line:
```
0 * * * * cd /home/user/Private-Claude && python3 scripts/email_automation_runner.py --once --limit 10 >> logs/email_cron.log 2>&1
```

---

## What Gets Extracted

### Tasks
- **TODO items**: "TODO: Review the report"
- **Action verbs**: "Please submit the form", "Need to call John"
- **Bullet points**: "- Update documentation"
- **Numbered lists**: "1. Prepare slides"

### Reminders
- "Remind me to call John"
- "Don't forget to submit the form"
- "Follow up with the client"

### Deadlines
- "Due by December 31, 2024"
- "Deadline: 12/31/2024"
- "Before 2024-12-31"

### Documents
- "Form 1023", "W-2", "1099", "990"
- "Please send the contract"
- "Need the technical specification PDF"

---

## Where Data Is Saved

All extracted data is saved to:
```
/home/user/Private-Claude/data/email_tasks/
├── tasks/tasks_YYYYMMDD.json
├── reminders/reminders_YYYYMMDD.json
├── documents/document_requests_YYYYMMDD.json
├── processed_emails/processed_YYYYMMDD.json
└── logs/automation_runs.json
```

View today's tasks:
```bash
cat /home/user/Private-Claude/data/email_tasks/tasks/tasks_$(date +%Y%m%d).json
```

---

## Monitoring

### Check Automation Logs
```bash
tail -f /home/user/Private-Claude/data/email_tasks/logs/automation_runs.json
```

### Check Continuous Mode Output
```bash
tail -f /home/user/Private-Claude/logs/email_automation.log
```

### Check Cron Logs
```bash
tail -f /home/user/Private-Claude/logs/email_cron.log
```

---

## Troubleshooting

### "Gmail connection error"
- Verify IMAP is enabled in Gmail settings
- Check 2-Step Verification is enabled
- Generate a new app password
- Update .env file with new password (no spaces)

### "No unread emails found"
- Emails must be in main INBOX (not labels/folders)
- Mark some emails as unread to test

### "Zapier webhook failed"
- Verify webhook URL in .env is correct
- Check Zap is turned ON in Zapier dashboard
- Test webhook manually in Zapier

### Tasks not appearing in Google Tasks
- Check Zap history in Zapier dashboard
- Verify Google Tasks connection is active
- Ensure correct task list is selected

---

## File Locations

### Scripts
- `/home/user/Private-Claude/scripts/email_data_extractor.py` - Core extraction
- `/home/user/Private-Claude/scripts/email_automation_runner.py` - Scheduled automation
- `/home/user/Private-Claude/scripts/test_email_extraction.py` - Test with sample data

### Configuration
- `/home/user/Private-Claude/config/.env` - Environment variables
- `/home/user/Private-Claude/config/connectors/email.json` - Email config
- `/home/user/Private-Claude/config/connectors/google_workspace.json` - Google config

### Documentation
- `/home/user/Private-Claude/logs/email_automation_setup_guide.md` - Full setup guide (15 sections)
- `/home/user/Private-Claude/logs/email_automation_deployment_report.json` - Complete deployment details
- `/home/user/Private-Claude/logs/email_automation_test_report.json` - Test results

### Data
- `/home/user/Private-Claude/data/email_tasks/` - All extracted data

---

## Commands Cheat Sheet

```bash
# Test extraction with sample data (no Gmail needed)
python3 scripts/test_email_extraction.py

# Process real emails once
python3 scripts/email_automation_runner.py --once --limit 10

# Run continuously (every hour)
python3 scripts/email_automation_runner.py --continuous --interval 60 --limit 10

# Run in background
nohup python3 scripts/email_automation_runner.py --continuous --interval 60 --limit 10 > logs/email_automation.log 2>&1 &

# View today's tasks
cat data/email_tasks/tasks/tasks_$(date +%Y%m%d).json | python3 -m json.tool

# View automation logs
tail -f data/email_tasks/logs/automation_runs.json

# Check system status
ls -lah data/email_tasks/*/
```

---

## Next Steps

1. ✅ **Complete Gmail setup** (Step 1 above)
2. ✅ **Send test email** and run extraction
3. ✅ **Verify data** is extracted correctly
4. ⬜ Set up Zapier webhooks (optional)
5. ⬜ Configure continuous automation (cron or background)
6. ⬜ Monitor logs and optimize patterns

---

## Support

- **Full Setup Guide**: `/home/user/Private-Claude/logs/email_automation_setup_guide.md`
- **Deployment Report**: `/home/user/Private-Claude/logs/email_automation_deployment_report.json`
- **Test Report**: `/home/user/Private-Claude/logs/email_automation_test_report.json`

**Gmail Account**: terobinsonwy@gmail.com
**System Status**: Ready for activation - requires Gmail credentials
**Last Updated**: 2025-12-22
