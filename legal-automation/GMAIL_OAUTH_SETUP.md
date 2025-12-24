# Gmail OAuth Setup Guide

**Complete step-by-step guide to set up Gmail API for legal automation**

---

## Prerequisites

- Google Account (terobinsonwy@gmail.com)
- Access to Google Cloud Console
- Python 3.7+ installed

---

## Step 1: Create Google Cloud Project

1. Go to **Google Cloud Console**:
   ```
   https://console.cloud.google.com/
   ```

2. Click **"Select a project"** → **"NEW PROJECT"**

3. Enter project details:
   - Project name: `Legal Automation System`
   - Organization: (leave blank or select your org)
   - Location: (leave default)

4. Click **"CREATE"**

5. Wait for project creation (about 30 seconds)

6. Select your new project from the dropdown

---

## Step 2: Enable Gmail API

1. In the Google Cloud Console, go to **"APIs & Services" → "Library"**
   ```
   https://console.cloud.google.com/apis/library
   ```

2. Search for **"Gmail API"**

3. Click on **"Gmail API"** from the results

4. Click **"ENABLE"**

5. Wait for API to be enabled

---

## Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" → "Credentials"**
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**

3. If prompted to configure consent screen:
   - Click **"CONFIGURE CONSENT SCREEN"**
   - Select **"Internal"** (if available) or **"External"**
   - Click **"CREATE"**

4. Fill out OAuth consent screen:
   - App name: `Legal Automation System`
   - User support email: `terobinsonwy@gmail.com`
   - Developer contact email: `terobinsonwy@gmail.com`
   - Click **"SAVE AND CONTINUE"**

5. Add scopes:
   - Click **"ADD OR REMOVE SCOPES"**
   - Search and select:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.modify`
     - `https://www.googleapis.com/auth/gmail.compose`
   - Click **"UPDATE"**
   - Click **"SAVE AND CONTINUE"**

6. Add test users (if External):
   - Click **"ADD USERS"**
   - Enter: `terobinsonwy@gmail.com`
   - Click **"ADD"**
   - Click **"SAVE AND CONTINUE"**

7. Review and click **"BACK TO DASHBOARD"**

8. Go back to **"Credentials"** tab

9. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**

10. Configure OAuth client:
    - Application type: **"Desktop app"**
    - Name: `Legal Automation Desktop Client`
    - Click **"CREATE"**

11. **Download credentials**:
    - Click **"DOWNLOAD JSON"** button
    - Save file as: `gmail_credentials.json`

---

## Step 4: Install Credentials

1. Create config directory:
   ```bash
   mkdir -p config
   ```

2. Move downloaded file:
   ```bash
   mv ~/Downloads/client_secret_*.json config/gmail_credentials.json
   ```

3. Verify file exists:
   ```bash
   ls -l config/gmail_credentials.json
   ```

---

## Step 5: Install Required Python Packages

```bash
pip install --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## Step 6: Run Authentication

```bash
python3 legal-automation/gmail_automation.py
```

**What will happen:**
1. Browser will open automatically
2. Sign in with `terobinsonwy@gmail.com`
3. Review permissions and click **"Allow"**
4. You'll see: "The authentication flow has completed"
5. Close the browser tab
6. Token will be saved to: `config/gmail_token.pickle`

---

## Step 7: Verify Authentication

Run the test script:
```bash
python3 legal-automation/gmail_automation.py
```

Expected output:
```
✅ Gmail API authenticated successfully
```

---

## Troubleshooting

### Error: `invalid_grant`
**Solution:** Delete `config/gmail_token.pickle` and re-authenticate

### Error: `Redirect URI mismatch`
**Solution:**
1. Go to Google Cloud Console → Credentials
2. Edit your OAuth 2.0 Client ID
3. Add authorized redirect URIs:
   - `http://localhost:8080/`
   - `http://localhost:8080`

### Error: `Access blocked: This app's request is invalid`
**Solution:**
1. Verify OAuth consent screen is configured
2. Add yourself as a test user
3. Make sure all scopes are added

### Error: `The file gmail_credentials.json does not exist`
**Solution:**
```bash
# Check file location
ls -l config/gmail_credentials.json

# If missing, download again from Google Cloud Console
```

---

## Security Notes

1. **Never commit credentials to Git:**
   ```bash
   echo "config/gmail_credentials.json" >> .gitignore
   echo "config/gmail_token.pickle" >> .gitignore
   ```

2. **Protect your credentials file:**
   ```bash
   chmod 600 config/gmail_credentials.json
   chmod 600 config/gmail_token.pickle
   ```

3. **Token expires after 1 hour** - script will auto-refresh

4. **Revoke access anytime:**
   - Go to: https://myaccount.google.com/permissions
   - Find "Legal Automation System"
   - Click "Remove Access"

---

## API Quotas & Limits

**Gmail API Free Tier:**
- **Send:** 100 emails per day (user-imposed quota)
- **Read:** 1 billion quota units per day
- **Modify:** 500 quota units per user per second

**Cost:** FREE (within quotas)

**Monitor usage:**
```
https://console.cloud.google.com/apis/api/gmail.googleapis.com/quotas
```

---

## Next Steps

Once Gmail is authenticated:

1. **Send test email:**
   ```python
   from legal_automation.gmail_automation import LegalGmailAutomation

   gmail = LegalGmailAutomation()
   gmail.authenticate()
   gmail.send_email(
       to='your_email@example.com',
       subject='Test',
       body='This is a test email'
   )
   ```

2. **Send probate dismissal notices:**
   - Review recipients list
   - Uncomment send code in `master_legal_orchestrator.py`
   - Run workflow

3. **Monitor legal inbox:**
   ```python
   gmail.monitor_legal_inbox()
   ```

---

## Support

**Gmail API Documentation:**
- https://developers.google.com/gmail/api

**Python Quickstart:**
- https://developers.google.com/gmail/api/quickstart/python

**OAuth 2.0 Guide:**
- https://developers.google.com/identity/protocols/oauth2

---

**Last Updated:** December 23, 2025
**Contact:** terobinsonwy@gmail.com
