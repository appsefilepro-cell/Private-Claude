# Agent X2.0 - Complete API Setup Instructions

This document provides step-by-step instructions for setting up all required API connections.

---

## Table of Contents

1. [Microsoft 365 / Azure AD Setup](#microsoft-365--azure-ad-setup)
2. [Gmail API Setup](#gmail-api-setup)
3. [Dropbox API Setup](#dropbox-api-setup)
4. [Zapier Setup](#zapier-setup)
5. [Kraken Trading API Setup](#kraken-trading-api-setup)
6. [SAM.gov API Setup](#samgov-api-setup)
7. [Power Automate Setup](#power-automate-setup)
8. [Testing API Connections](#testing-api-connections)

---

## Microsoft 365 / Azure AD Setup

### Prerequisites
- Microsoft 365 tenant: `APPSHOLDINGSWYINC.onmicrosoft.com`
- Global Administrator access

### Step 1: Register Application in Azure AD

1. Sign in to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
   - Name: `Agent X2.0 Integration`
   - Supported account types: `Accounts in this organizational directory only (APPSHOLDINGSWYINC only - Single tenant)`
   - Redirect URI: Leave blank for daemon app
4. Click **Register**

### Step 2: Note Application Details

After registration, copy these values:
- **Application (client) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Directory (tenant) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### Step 3: Create Client Secret

1. In your app, go to **Certificates & secrets**
2. Click **New client secret**
   - Description: `Agent X2.0 Production`
   - Expires: `24 months`
3. Click **Add**
4. **IMPORTANT:** Copy the **Value** immediately (shown only once!)

### Step 4: Add API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Application permissions** (not Delegated)
5. Add these permissions:
   - `Files.Read.All` - Read files in all site collections
   - `Files.ReadWrite.All` - Read and write files in all site collections
   - `Sites.Read.All` - Read items in all site collections
   - `Sites.ReadWrite.All` - Edit or delete items in all site collections
   - `Mail.Read` - Read mail in all mailboxes (if needed)
   - `User.Read.All` - Read all users' full profiles (if needed)

6. Click **Add permissions**

### Step 5: Grant Admin Consent

1. Click **Grant admin consent for APPSHOLDINGSWYINC**
2. Click **Yes** to confirm
3. Verify all permissions show green checkmarks under "Status"

### Step 6: Update Configuration

Add to `.env`:
```bash
MICROSOFT_TENANT_ID=your_tenant_id
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
```

### Step 7: Test Connection

```bash
python core-systems/api-connectors/microsoft_365_connector.py
```

Expected output: "Microsoft 365 authentication successful"

---

## Gmail API Setup

### Prerequisites
- Gmail account: `appsefilepro@gmail.com`
- Google Cloud Platform access

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** > **New Project**
   - Project name: `Agent-X2-Integration`
   - Organization: (Your organization)
3. Click **Create**

### Step 2: Enable Gmail API

1. In your project, go to **APIs & Services** > **Library**
2. Search for `Gmail API`
3. Click on **Gmail API**
4. Click **Enable**

### Step 3: Create OAuth Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure OAuth consent screen:
   - User Type: `Internal` (if using Google Workspace) or `External`
   - App name: `Agent X2.0`
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `https://www.googleapis.com/auth/gmail.readonly`
4. Return to **Credentials** > **Create Credentials** > **OAuth client ID**
   - Application type: `Desktop app`
   - Name: `Agent X2.0 Desktop Client`
5. Click **Create**
6. Download the JSON file (click download icon)
7. Save as `config/gmail_credentials.json`

### Step 4: First-Time Authentication

1. Run the Gmail connector:
```bash
python core-systems/api-connectors/gmail_connector.py
```

2. A browser window will open
3. Sign in with your Gmail account
4. Grant permissions
5. Token will be saved automatically

### Step 5: Update .env

```bash
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
```

---

## Dropbox API Setup

### Step 1: Create Dropbox App

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click **Create app**
   - Choose an API: `Scoped access`
   - Choose type of access: `Full Dropbox`
   - Name: `Agent-X2-Integration`
3. Click **Create app**

### Step 2: Configure Permissions

1. In your app, go to **Permissions** tab
2. Enable these permissions:
   - `files.metadata.read`
   - `files.content.read`
   - `files.content.write` (if needed)
3. Click **Submit**

### Step 3: Generate Access Token

1. Go to **Settings** tab
2. Scroll to **Generated access token**
3. Click **Generate**
4. Copy the access token

### Step 4: Update .env

```bash
DROPBOX_ACCESS_TOKEN=your_access_token
```

**Note:** For production, implement OAuth 2.0 flow instead of using long-lived tokens.

---

## Zapier Setup

### Prerequisites
- Zapier Professional plan (for multi-step Zaps)

### Step 1: Create Zapier Account

1. Go to [Zapier.com](https://zapier.com/)
2. Sign up or sign in
3. Upgrade to Professional plan if needed

### Step 2: Create Trading Signal Zap

**Zap Name:** "Trading Signal → Execution & Logging"

1. Click **Create Zap**
2. **Trigger:** Webhooks by Zapier
   - Event: Catch Hook
   - Copy webhook URL (you'll need this)
3. **Action 1:** Filter by Zapier
   - Continue only if...
   - `confidence` (Number) Greater than `0.75`
4. **Action 2:** Gmail - Send Email
   - To: `appsefilepro@gmail.com`
   - Subject: `Trading Alert: {{action}} {{pair}}`
   - Body: Format signal details
5. **Action 3:** Google Sheets - Create Spreadsheet Row
   - Spreadsheet: Create "Trade Log" sheet
   - Worksheet: Sheet1
   - Map fields: timestamp, pair, action, confidence
6. **Action 4:** Webhooks by Zapier - POST
   - URL: Your execution bot endpoint (if using)
   - Payload: Pass through signal data
7. Turn Zap **ON**

### Step 3: Update .env

```bash
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/XXXXXXX/XXXXXXX/
```

### Step 4: Test Webhook

```bash
curl -X POST https://hooks.zapier.com/hooks/catch/YOUR_ID/ \
  -H "Content-Type: application/json" \
  -d '{"pair":"BTC/USD","action":"BUY","confidence":0.85}'
```

Check Zapier dashboard for successful trigger.

---

## Kraken Trading API Setup

### Prerequisites
- Kraken account with KYC verification
- Two-factor authentication enabled

### Step 1: Create API Key

1. Log in to [Kraken.com](https://www.kraken.com/)
2. Go to **Settings** > **API**
3. Click **Generate New Key**
4. **Key Description:** `Agent X2.0 Trading Bot`
5. **Key Permissions:**
   - Query Funds: ✓
   - Query Open Orders & Trades: ✓
   - Query Closed Orders & Trades: ✓
   - Query Ledger Entries: ✓
   - Create & Modify Orders: ✓ (only if executing trades)
   - Cancel/Close Orders: ✓ (only if executing trades)
   - **Do NOT enable:** Withdraw Funds, Export Data
6. Click **Generate Key**
7. Copy **API Key** and **Private Key**
8. **IMPORTANT:** Private key shown only once!

### Step 2: Restrict API Key

1. **IP Whitelist:** Add your server IP
2. **Nonce Window:** 5 seconds (recommended)

### Step 3: Update .env

```bash
KRAKEN_API_KEY=your_api_key
KRAKEN_API_SECRET=your_private_key
```

### Step 4: Test API Connection

```python
import requests
import hashlib
import hmac
import base64
import time

api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

# Test: Get account balance
url = "https://api.kraken.com/0/private/Balance"
nonce = str(int(time.time() * 1000))

# Create signature
message = nonce + "Balance"
message_encoded = message.encode()
secret_decoded = base64.b64decode(api_secret)
signature = hmac.new(secret_decoded, message_encoded, hashlib.sha512)
signature_digest = base64.b64encode(signature.digest())

headers = {
    "API-Key": api_key,
    "API-Sign": signature_digest.decode()
}

response = requests.post(url, headers=headers, data={"nonce": nonce})
print(response.json())
```

Expected: Your account balance

---

## SAM.gov API Setup

### Step 1: Register on SAM.gov

1. Go to [SAM.gov](https://sam.gov/)
2. Click **Sign In** > **Create Account**
3. Complete registration
4. Verify email address

### Step 2: Request API Key

1. Log in to SAM.gov
2. Go to **Account** menu > **System Account**
3. Select **API Key Request**
4. Purpose: `Federal contracting opportunity monitoring`
5. Submit request
6. API key will be emailed (usually instant for public API)

### Step 3: Update .env

```bash
SAM_GOV_API_KEY=your_api_key
```

### Step 4: Test API

```bash
curl "https://api.sam.gov/prod/opportunities/v2/search?api_key=YOUR_KEY&postedFrom=01/01/2024&limit=1"
```

Expected: JSON response with opportunities

### API Rate Limits

- **Public Tier:** 1,000 requests/day, 10 requests/10 seconds
- **FOUO Tier:** Higher limits (requires justification)

---

## Power Automate Setup

### Prerequisites
- Microsoft 365 license with Power Automate access
- SharePoint admin permissions

### Creating the Legal Document Flow

1. Go to [Power Automate](https://flow.microsoft.com/)
2. Click **Create** > **Automated cloud flow**
3. **Flow name:** `Legal Document Auto-Generator`
4. **Trigger:** Skip for now
5. Click **Create**

### Configure Trigger

1. Search for `SharePoint`
2. Select **When a file is created or modified (properties only)**
3. Configure:
   - Site Address: `https://appsholdingswyinc.sharepoint.com`
   - Library Name: `Legal Operations`
   - Folder: `/02_Active_Cases/`
   - Select "Include SubFolders" Yes

### Add Get File Content Action

1. Click **New step**
2. Search `SharePoint`
3. Select **Get file content**
4. File Identifier: From trigger dynamic content

### Add Condition for File Type

1. **New step** > **Condition**
2. Check if file name ends with `.pdf`

### Add HTTP Action to Claude API

1. **New step** > **HTTP**
2. Method: `POST`
3. URI: `https://api.anthropic.com/v1/messages`
4. Headers:
   ```
   x-api-version: 2023-06-01
   anthropic-api-key: YOUR_CLAUDE_API_KEY
   Content-Type: application/json
   ```
5. Body:
   ```json
   {
     "model": "claude-3-5-sonnet-20241022",
     "max_tokens": 4096,
     "messages": [{
       "role": "user",
       "content": "Generate a Motion for Summary Judgment using this evidence: [File Content]"
     }]
   }
   ```

### Add Create File Action

1. **New step** > SharePoint **Create file**
2. Site Address: Same
3. Folder Path: `/02_Active_Cases/[Case Name]/Drafts/`
4. File Name: Dynamic (case name + timestamp + .docx)
5. File Content: Parse HTTP response

### Add Send Email

1. **New step** > Outlook **Send an email**
2. To: Attorney email
3. Subject: `Document Ready: [Doc Type] for [Case Name]`
4. Body: Include link to generated document

### Save and Test

1. Click **Save**
2. Upload a test PDF to Evidence folder
3. Check flow run history

---

## Testing API Connections

### Comprehensive Test Script

Create `tests/test_all_apis.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

def test_microsoft_365():
    print("Testing Microsoft 365...")
    from core_systems.api_connectors.microsoft_365_connector import Microsoft365Connector
    connector = Microsoft365Connector()
    result = connector.authenticate()
    print(f"  Microsoft 365: {'✓ PASS' if result else '✗ FAIL'}")
    return result

def test_gmail():
    print("Testing Gmail...")
    from core_systems.api_connectors.gmail_connector import GmailConnector
    connector = GmailConnector()
    result = connector.authenticate()
    print(f"  Gmail: {'✓ PASS' if result else '✗ FAIL'}")
    return result

def test_zapier():
    print("Testing Zapier webhook...")
    import requests
    webhook_url = os.getenv('ZAPIER_WEBHOOK_URL')
    if not webhook_url:
        print("  Zapier: ✗ FAIL (no webhook URL)")
        return False
    try:
        response = requests.post(webhook_url, json={"test": True})
        result = response.status_code == 200
        print(f"  Zapier: {'✓ PASS' if result else '✗ FAIL'}")
        return result
    except:
        print("  Zapier: ✗ FAIL")
        return False

def main():
    print("=" * 50)
    print("Agent X2.0 - API Connection Tests")
    print("=" * 50)

    results = {
        "Microsoft 365": test_microsoft_365(),
        "Gmail": test_gmail(),
        "Zapier": test_zapier()
    }

    print("\n" + "=" * 50)
    passed = sum(results.values())
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 50)

    if passed == total:
        print("✓ ALL API CONNECTIONS VERIFIED")
    else:
        print("✗ SOME CONNECTIONS FAILED - Review logs above")

if __name__ == "__main__":
    main()
```

Run:
```bash
python tests/test_all_apis.py
```

---

## Security Best Practices

1. **Never commit credentials**
   - Always use `.env` file
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Rotate credentials regularly**
   - Every 90 days minimum
   - Immediately if compromised

3. **Use least privilege**
   - Only grant necessary permissions
   - Separate read-only and read-write keys

4. **Monitor API usage**
   - Set up alerts for unusual activity
   - Review audit logs weekly

5. **Use secrets management in production**
   - Azure Key Vault
   - AWS Secrets Manager
   - HashiCorp Vault

6. **Enable MFA on all accounts**

7. **IP whitelist where possible**

---

## Troubleshooting

### Microsoft 365: "Insufficient privileges"
**Solution:** Re-grant admin consent in Azure AD

### Gmail: "invalid_client"
**Solution:** Re-download credentials.json from Google Cloud Console

### Zapier: Webhook not receiving data
**Solution:** Check webhook URL is correct. Test with curl.

### Kraken: "Invalid signature"
**Solution:** Check API secret is correct. Verify nonce is current timestamp.

### SAM.gov: Rate limit exceeded
**Solution:** Implement exponential backoff. Consider upgrading to FOUO tier.

---

*Last Updated: December 5, 2025*
*Maintained by: Thurman Malik Robinson*
*Organization: APPS Holdings WY Inc.*
