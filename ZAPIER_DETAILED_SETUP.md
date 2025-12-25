# ZAPIER DETAILED SETUP GUIDE

**Complete step-by-step instructions for each Zap**
**NO coding required - just follow along!**

---

## TABLE OF CONTENTS

1. [OKX Trading Alerts](#1-okx-trading-alerts)
2. [Daily Trading Report](#2-daily-trading-report)
3. [Legal Document Generator](#3-legal-document-generator)
4. [Error Notification System](#4-error-notification-system)
5. [Google Drive File Alerts](#5-google-drive-file-alerts)
6. [Case Dismissal Workflow](#6-case-dismissal-workflow)
7. [Nonprofit Form 1023-EZ](#7-nonprofit-form-1023-ez)
8. [Test Completion Alerts](#8-test-completion-alerts)
9. [Weekly Financial Reports](#9-weekly-financial-reports)
10. [Life Coach Session Reminders](#10-life-coach-session-reminders)

---

## 1. OKX TRADING ALERTS

**What it does**: Sends you email + Slack alert + logs to Google Sheets every time a trade happens

**Time to setup**: 10 minutes

### Step-by-Step:

#### A. Create Google Sheet First

1. Go to: https://sheets.google.com
2. Click "Blank" to create new sheet
3. Name it: **OKX Trading Log**
4. In Row 1, add these headers:
   - A1: `Timestamp`
   - B1: `Pair`
   - C1: `Side`
   - D1: `Amount`
   - E1: `Price`
   - F1: `Pattern`
   - G1: `P&L`
5. Click Share → Copy link (save this link!)

#### B. Create the Zap

1. Go to https://zapier.com
2. Click **Create** → **Zaps**
3. Name it: `OKX Trading Alerts`

#### C. Set Up Trigger

1. **Search for**: `Webhooks by Zapier`
2. Click it
3. **Event**: Choose `Catch Hook`
4. Click **Continue**
5. **IMPORTANT**: Copy the webhook URL shown
   - Example: `https://hooks.zapier.com/hooks/catch/12345678/abc123/`
   - Save this URL - you'll use it to send trade data
6. Click **Test trigger**
7. Click **Continue**

#### D. Add Action #1: Log to Google Sheets

1. Click **+** to add action
2. **Search for**: `Google Sheets`
3. Click it
4. **Event**: Choose `Create Spreadsheet Row`
5. Click **Continue**
6. **Choose Account**: Select your Google account
7. Click **Continue**
8. **Configure**:
   - **Drive**: My Google Drive
   - **Spreadsheet**: OKX Trading Log
   - **Worksheet**: Sheet1
   - **Timestamp**: Click + and type `timestamp` → select from dropdown
   - **Pair**: Click + and type `pair` → select from dropdown
   - **Side**: Click + and type `side` → select from dropdown
   - **Amount**: Click + and type `amount` → select from dropdown
   - **Price**: Click + and type `price` → select from dropdown
   - **Pattern**: Click + and type `pattern` → select from dropdown
   - **P&L**: Click + and type `pnl` → select from dropdown
9. Click **Continue**
10. Click **Test action** (should add a row to your sheet!)
11. **Check your Google Sheet** - you should see test data!

#### E. Add Action #2: Email Alert

1. Click **+** to add another action
2. **Search for**: `Gmail`
3. Click it
4. **Event**: Choose `Send Email`
5. Click **Continue**
6. **Choose Account**: Select your Gmail
7. Click **Continue**
8. **Configure**:
   - **To**: terobinsonwy@gmail.com
   - **Subject**: `OKX Trade Alert - {{pair}}`
     - Click the + button and find "Pair" to insert {{pair}}
   - **Body**:
     ```
     New trade executed!

     Pair: {{pair}}
     Side: {{side}}
     Amount: {{amount}}
     Price: {{price}}
     Pattern: {{pattern}}
     P&L: {{pnl}}
     Time: {{timestamp}}

     View full log: [YOUR GOOGLE SHEET LINK]
     ```
     - For each {{variable}}, click + and select from dropdown
9. Click **Continue**
10. Click **Test action**
11. **CHECK YOUR EMAIL!** You should receive a test email

#### F. Add Action #3: Slack Alert (Optional)

1. Click **+** to add another action
2. **Search for**: `Slack`
3. Click it
4. **Event**: Choose `Send Channel Message`
5. Click **Continue**
6. **Choose Account**: Connect your Slack workspace
7. Click **Continue**
8. **Configure**:
   - **Channel**: #trading-alerts (create this channel first!)
   - **Message Text**:
     ```
     🔔 OKX Trade Alert

     {{side}} {{amount}} {{pair}} at {{price}}
     Pattern: {{pattern}}
     P&L: {{pnl}}
     ```
   - For each {{variable}}, click + and select from dropdown
9. Click **Continue**
10. Click **Test action**
11. **CHECK SLACK!** You should see a message in #trading-alerts

#### G. Publish Your Zap

1. Click **Publish** (top right)
2. Toggle the switch to **ON** (should be blue)
3. **DONE!**

#### H. Save Your Webhook URL

Your webhook URL from step C is what you'll use to send trade data. Save it as:
```
OKX Trading Webhook: https://hooks.zapier.com/hooks/catch/XXXXX/XXXXX/
```

#### I. Test It!

1. Open `verify_zapier.html`
2. Paste your webhook URL
3. Click "Send Test Trade Alert"
4. Check:
   - ✅ Email received
   - ✅ Google Sheets updated
   - ✅ Slack message sent

**SUCCESS! Your trading alerts are now automated!**

---

## 2. DAILY TRADING REPORT

**What it does**: Sends you a daily email at 8 PM with your trading summary

**Time to setup**: 5 minutes

### Step-by-Step:

#### A. Create the Zap

1. Go to https://zapier.com
2. Click **Create** → **Zaps**
3. Name it: `Daily Trading Report`

#### B. Set Up Trigger

1. **Search for**: `Schedule by Zapier`
2. Click it
3. **Event**: Choose `Every Day`
4. Click **Continue**
5. **Configure**:
   - **Time of Day**: 8:00 PM
   - **Timezone**: (GMT-06:00) Central Time
6. Click **Continue**
7. Click **Test trigger**
8. Click **Continue**

#### C. Add Action: Send Email

1. Click **Action**
2. **Search for**: `Gmail`
3. Click it
4. **Event**: Choose `Send Email`
5. Click **Continue**
6. **Choose Account**: Your Gmail
7. Click **Continue**
8. **Configure**:
   - **To**: terobinsonwy@gmail.com
   - **Subject**: `Daily Trading Report - {{today}}`
     - Click + and find "Scheduled Time Humanized" for today's date
   - **Body**:
     ```
     Daily Trading Summary for {{today}}

     📊 Your trading activity:

     Total Trades: Check your Google Sheet
     Link: [PASTE YOUR GOOGLE SHEET LINK]

     Best regards,
     Your Trading System
     ```
9. Click **Continue**
10. Click **Test action**
11. **CHECK EMAIL!**

#### D. Publish

1. Click **Publish**
2. Toggle **ON**
3. **DONE!**

**You'll now get a daily report every day at 8 PM!**

---

## 3. LEGAL DOCUMENT GENERATOR

**What it does**: Creates legal documents from templates when triggered

**Time to setup**: 15 minutes

### Prerequisites:

1. Create a Google Docs template:
   - Go to https://docs.google.com
   - Create a new document
   - Name it: "Legal Notice Template"
   - Add placeholders like:
     ```
     Case Number: {{case_number}}
     Court: {{court}}
     Plaintiff: {{plaintiff}}
     Defendant: {{defendant}}
     Date: {{date}}
     ```
   - Save it

### Step-by-Step:

#### A. Create the Zap

1. Go to https://zapier.com
2. Click **Create** → **Zaps**
3. Name it: `Legal Document Generator`

#### B. Set Up Trigger

1. **Search for**: `Webhooks by Zapier`
2. Click it
3. **Event**: Choose `Catch Hook`
4. Click **Continue**
5. **Copy the webhook URL** and save it as:
   ```
   Legal Docs Webhook: https://hooks.zapier.com/hooks/catch/XXXXX/legal/
   ```
6. Click **Continue**

#### C. Add Action #1: Create Document

1. Click **Action**
2. **Search for**: `Google Docs`
3. Click it
4. **Event**: Choose `Create Document from Template`
5. Click **Continue**
6. **Choose Account**: Your Google account
7. Click **Continue**
8. **Configure**:
   - **Template Document**: Select "Legal Notice Template"
   - **New Document Name**: `Legal_{{case_number}}_{{date}}`
   - Click + to insert variables
9. Click **Continue**
10. Click **Test action**

#### D. Add Action #2: Email Document

1. Click **+** to add action
2. **Search for**: `Gmail`
3. Click it
4. **Event**: Choose `Send Email`
5. Click **Continue**
6. **Configure**:
   - **To**: terobinsonwy@gmail.com
   - **Subject**: `Legal Document Ready: {{case_number}}`
   - **Body**:
     ```
     Your legal document has been generated.

     Case: {{case_number}}
     Court: {{court}}

     View document: {{Alternate Link}}
     ```
     - Use the + button to insert variables
7. Click **Continue**
8. Click **Test action**
9. **CHECK EMAIL!**

#### E. Publish

1. Click **Publish**
2. Toggle **ON**
3. **DONE!**

---

## 4. ERROR NOTIFICATION SYSTEM

**What it does**: Sends urgent alerts when system errors occur

**Time to setup**: 5 minutes

### Step-by-Step:

#### A. Create the Zap

1. Click **Create** → **Zaps**
2. Name it: `Error Alerts`

#### B. Set Up Trigger

1. **Search for**: `Webhooks by Zapier`
2. Click it
3. **Event**: `Catch Hook`
4. Click **Continue**
5. **Save webhook URL** as:
   ```
   Error Webhook: https://hooks.zapier.com/hooks/catch/XXXXX/errors/
   ```

#### C. Add Action #1: Email Alert

1. **Search for**: `Gmail`
2. **Event**: `Send Email`
3. **Configure**:
   - **To**: terobinsonwy@gmail.com
   - **Subject**: `🚨 URGENT: System Error in {{system}}`
   - **Body**:
     ```
     URGENT SYSTEM ERROR

     System: {{system}}
     Error: {{error_message}}
     Severity: {{severity}}
     Time: {{timestamp}}

     Please investigate immediately.
     ```
4. Click **Continue**
5. Click **Test action**

#### D. Add Action #2: SMS Alert (Optional)

1. Click **+** to add action
2. **Search for**: `SMS by Zapier`
3. **Event**: `Send SMS`
4. **Configure**:
   - **To Phone Number**: Your phone number
   - **Message**: `System error in {{system}}: {{error_message}}`
5. Click **Continue**
6. Click **Test action**

#### E. Publish

1. Click **Publish**
2. Toggle **ON**
3. **DONE!**

---

## 5. GOOGLE DRIVE FILE ALERTS

**What it does**: Emails you when new files are added to a specific folder

**Time to setup**: 5 minutes

### Prerequisites:

1. Create a folder in Google Drive:
   - Go to https://drive.google.com
   - Click "New" → "Folder"
   - Name it: "Legal Automation"

### Step-by-Step:

#### A. Create the Zap

1. Click **Create** → **Zaps**
2. Name it: `Google Drive File Alerts`

#### B. Set Up Trigger

1. **Search for**: `Google Drive`
2. Click it
3. **Event**: Choose `New File in Folder`
4. Click **Continue**
5. **Choose Account**: Your Google account
6. Click **Continue**
7. **Configure**:
   - **Drive**: My Google Drive
   - **Folder**: Legal Automation
8. Click **Continue**
9. Click **Test trigger** (add a test file to that folder first!)

#### C. Add Action: Email Alert

1. **Search for**: `Gmail`
2. **Event**: `Send Email`
3. **Configure**:
   - **To**: terobinsonwy@gmail.com
   - **Subject**: `New File Ready: {{Name}}`
   - **Body**:
     ```
     A new file has been added to Legal Automation

     File Name: {{Name}}
     Created: {{Created Time}}
     Size: {{Size}}

     View file: {{Web View Link}}
     ```
4. Click **Continue**
5. Click **Test action**
6. **CHECK EMAIL!**

#### D. Publish

1. Click **Publish**
2. Toggle **ON**
3. **DONE!**

**Now you'll be notified whenever a file is added to that folder!**

---

## 6. CASE DISMISSAL WORKFLOW (Case 1241511)

**What it does**: Auto-generates dismissal notice from template with one click

**Time to setup**: 10 minutes

### Step-by-Step:

#### A. Create Template Document

1. Go to https://docs.google.com
2. Create new document: "Probate Dismissal Notice Template"
3. Add this content:
   ```
   IN THE DISTRICT COURT OF {{court}}

   {{plaintiff}}
               vs.                          Case No. {{case_number}}
   {{defendant}}

   NOTICE OF DISMISSAL

   TO THE HONORABLE JUDGE:

   COMES NOW {{plaintiff}}, and hereby gives notice of dismissal
   of the above-styled case pursuant to applicable law.

   This {{date}}.

   Respectfully submitted,

   _______________________
   [Your Name]
   Attorney for Plaintiff
   ```

#### B. Create the Zap

1. Click **Create** → **Zaps**
2. Name it: `Case 1241511 Dismissal`

#### C. Set Up Trigger (Webhook)

1. **Webhooks by Zapier** → **Catch Hook**
2. Save the webhook URL

#### D. Add Action: Create Document

1. **Google Docs** → **Create Document from Template**
2. Select your template
3. Map fields:
   - court → `Harris County - County Civil Court at Law No. 2`
   - plaintiff → `NEW FOREST HOUSTON 2020 LLC`
   - defendant → `THURMAN ROBINSON, ET AL.`
   - case_number → `1241511`
   - date → (insert from webhook)

#### E. Add Action: Email Document

1. **Gmail** → **Send Email**
2. Attach the created document
3. Send to: terobinsonwy@gmail.com

#### F. Publish

1. Click **Publish**
2. Toggle **ON**

#### G. Create Bookmark Button (Easy Trigger!)

1. Open `verify_zapier.html`
2. Find the "Legal Document Test" section
3. Paste your webhook URL
4. Bookmark this page
5. **Now you can generate the dismissal notice with one click!**

---

## 7. NONPROFIT FORM 1023-EZ

**What it does**: Auto-fills IRS Form 1023-EZ from your data

**Time to setup**: 15 minutes

### Prerequisites:

You'll need PDF.co account (free tier available):
1. Go to https://pdf.co
2. Sign up for free account
3. Get your API key from dashboard

**OR** use a simpler method with Google Forms:

### Simple Method (Recommended):

#### A. Create Google Form

1. Go to https://forms.google.com
2. Create new form: "Form 1023-EZ Data"
3. Add these fields:
   - Organization Name
   - EIN
   - Address
   - City
   - State
   - ZIP
   - Formation Date
   - Purpose
4. Click **Send** and copy the form link

#### B. Create Google Sheet

1. In your form, click **Responses**
2. Click the Google Sheets icon
3. Create new sheet: "Nonprofit Form Data"

#### C. Create the Zap

1. **Trigger**: Google Forms → New Response
2. **Action 1**: Google Sheets → Create Row (in "Nonprofit Form Data")
3. **Action 2**: Gmail → Send Email to you with the data
4. Publish and turn ON

#### D. Fill Out Form

1. Go to your form link
2. Fill in your nonprofit info
3. Submit
4. You'll receive email with all data
5. Use this data to manually fill the IRS form

**This is much easier than PDF automation!**

---

## 8. TEST COMPLETION ALERTS

**What it does**: Notifies you when tests finish running

**Time to setup**: 5 minutes

### Step-by-Step:

#### A. Create the Zap

1. Click **Create** → **Zaps**
2. Name it: `Test Completion Alerts`

#### B. Set Up Trigger

1. **Webhooks by Zapier** → **Catch Hook**
2. Save webhook URL as:
   ```
   Test Webhook: https://hooks.zapier.com/hooks/catch/XXXXX/tests/
   ```

#### C. Add Action: Email Results

1. **Gmail** → **Send Email**
2. **Configure**:
   - **To**: terobinsonwy@gmail.com
   - **Subject**: `Test Results: {{test_name}}`
   - **Body**:
     ```
     Test Completed: {{test_name}}

     Status: {{status}}
     Pass Rate: {{pass_rate}}%
     Results: {{results}}

     Time: {{timestamp}}
     ```

#### D. Publish

1. Click **Publish**
2. Toggle **ON**
3. **DONE!**

---

## 9. WEEKLY FINANCIAL REPORTS

**What it does**: Sends weekly financial summary every Monday

**Time to setup**: 5 minutes

### Step-by-Step:

#### A. Create the Zap

1. Click **Create** → **Zaps**
2. Name it: `Weekly Financial Report`

#### B. Set Up Trigger

1. **Schedule by Zapier** → **Every Week**
2. **Configure**:
   - **Day**: Monday
   - **Time**: 9:00 AM
   - **Timezone**: Central Time

#### C. Add Action: Send Email

1. **Gmail** → **Send Email**
2. **Configure**:
   - **To**: terobinsonwy@gmail.com
   - **Subject**: `Weekly Financial Report - Week of {{date}}`
   - **Body**:
     ```
     Weekly Financial Summary

     This is your weekly financial report.

     Key Metrics:
     - Review your expenses
     - Check account balances
     - Update budgets

     View full data in Google Sheets:
     [PASTE YOUR SHEET LINK]
     ```

#### D. Publish

1. Click **Publish**
2. Toggle **ON**

**You'll now get weekly reports every Monday at 9 AM!**

---

## 10. LIFE COACH SESSION REMINDERS

**What it does**: Sends reminder emails for coaching sessions

**Time to setup**: 10 minutes

### Prerequisites:

1. Create Airtable account (free): https://airtable.com
2. Create base: "Life Coach AI"
3. Create table: "Sessions"
4. Add fields:
   - Client Name (Single line text)
   - Client Email (Email)
   - Session Date (Date)
   - Session Time (Single line text)
   - Session Topic (Long text)

### Step-by-Step:

#### A. Connect Airtable to Zapier

1. In Zapier, go to **My Apps**
2. Click **Add Connection**
3. Search **Airtable**
4. Click **Connect**
5. Follow prompts to authorize

#### B. Create the Zap

1. Click **Create** → **Zaps**
2. Name it: `Session Reminders`

#### C. Set Up Trigger

1. **Airtable** → **New Record in View**
2. **Configure**:
   - **Account**: Your Airtable account
   - **Base**: Life Coach AI
   - **Table**: Sessions
3. Click **Continue**
4. Click **Test trigger**

#### D. Add Action #1: Delay

1. **Delay by Zapier** → **Delay Until**
2. **Configure**:
   - **Delay Until**: {{Session Date}} (1 day before)
3. Click **Continue**

#### E. Add Action #2: Send Reminder Email

1. **Gmail** → **Send Email**
2. **Configure**:
   - **To**: {{Client Email}}
   - **Subject**: `Coaching Session Reminder - Tomorrow`
   - **Body**:
     ```
     Hi {{Client Name}},

     This is a reminder that we have a coaching session tomorrow.

     Date: {{Session Date}}
     Time: {{Session Time}}
     Topic: {{Session Topic}}

     Looking forward to our session!

     Best regards,
     Thurman Robinson
     Certified Life Coach
     ```

#### F. Publish

1. Click **Publish**
2. Toggle **ON**

#### G. Test It

1. Go to your Airtable
2. Add a new session record
3. Set date to tomorrow
4. Wait a few minutes
5. **CHECK EMAIL!** (or check Zapier History)

**DONE! Now all session reminders are automated!**

---

## QUICK TROUBLESHOOTING

### Zap Not Working?

1. **Check if Zap is ON**
   - Go to https://zapier.com/app/zaps
   - Make sure toggle is blue

2. **Check Zapier History**
   - Go to https://zapier.com/app/history
   - Look for errors (red X)
   - Click error to see details

3. **Reconnect Apps**
   - Go to https://zapier.com/app/connections
   - Click "Reconnect" on any app
   - Re-authorize

4. **Test Manually**
   - Edit your Zap
   - Click "Test" on each step
   - Fix any errors

5. **Check Email/Spam**
   - Check spam folder
   - Make sure email address is correct

### Still Not Working?

1. Delete the Zap and recreate it
2. Contact Zapier support: https://zapier.com/app/get-help
3. Check Zapier status: https://status.zapier.com

---

## SUMMARY OF YOUR WEBHOOK URLS

After creating all Zaps, you should have these webhook URLs:

```
1. OKX Trading: https://hooks.zapier.com/hooks/catch/[ID]/okx/
2. Legal Docs: https://hooks.zapier.com/hooks/catch/[ID]/legal/
3. Errors: https://hooks.zapier.com/hooks/catch/[ID]/errors/
4. Tests: https://hooks.zapier.com/hooks/catch/[ID]/tests/
5. Case 1241511: https://hooks.zapier.com/hooks/catch/[ID]/case1241511/
```

**Save these URLs in a safe place!**

---

## NEXT STEPS

1. ✅ Test each Zap using `verify_zapier.html`
2. ✅ Check Zapier History to ensure all are working
3. ✅ Monitor your email for notifications
4. ✅ Check Google Sheets for logged data
5. ✅ Verify Slack messages (if using Slack)

**You're all set! Everything is automated with ZERO code!**
