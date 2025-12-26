#!/usr/bin/env python3
"""
GOOGLE APIS SETUP - Gmail, Drive, Sheets, Calendar
Complete integration for Agent 5.0
Email: appefilepro@gmail.com
"""
import os
import json
from datetime import datetime

print("=" * 80)
print("GOOGLE APIS INTEGRATION SETUP")
print("=" * 80)
print(f"Email Account: appefilepro@gmail.com")
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Create config directory
os.makedirs("config/google", exist_ok=True)
os.makedirs("data/google_credentials", exist_ok=True)

# Google APIs to enable
google_apis = {
    "Gmail API": {
        "purpose": "Email automation and data extraction",
        "scope": "https://www.googleapis.com/auth/gmail.modify",
        "features": [
            "Read emails from appefilepro@gmail.com",
            "Send automated emails",
            "Extract attachments",
            "Label and filter messages",
            "Integration with Zapier workflows"
        ]
    },
    "Google Drive API": {
        "purpose": "Cloud storage for all documents",
        "scope": "https://www.googleapis.com/auth/drive",
        "features": [
            "Upload legal documents",
            "Store market data",
            "Organize files in folders",
            "Share documents with team",
            "100GB free storage"
        ]
    },
    "Google Sheets API": {
        "purpose": "Data tracking and automation logs",
        "scope": "https://www.googleapis.com/auth/spreadsheets",
        "features": [
            "Log legal document downloads",
            "Track trading bot performance",
            "Agent 5.0 status dashboard",
            "Integration Division workflow tracking",
            "Real-time collaboration"
        ]
    },
    "Google Calendar API": {
        "purpose": "Schedule automation and reminders",
        "scope": "https://www.googleapis.com/auth/calendar",
        "features": [
            "Schedule weekly legal downloads",
            "Trading bot execution times",
            "Agent 5.0 task scheduling",
            "Meeting coordination",
            "Deadline tracking"
        ]
    }
}

print("\nGOOGLE APIS TO ENABLE:")
print("=" * 80)
for api_name, api_info in google_apis.items():
    print(f"\n{api_name}")
    print(f"  Purpose: {api_info['purpose']}")
    print(f"  Scope: {api_info['scope']}")
    print(f"  Features:")
    for feature in api_info['features']:
        print(f"    - {feature}")

# OAuth 2.0 Configuration
oauth_config = {
    "web": {
        "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "project_id": "agent-5-automation",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_uris": ["http://localhost:8080/"],
        "javascript_origins": ["http://localhost:8080"]
    }
}

# Save OAuth config template
with open("config/google/oauth_credentials_template.json", "w") as f:
    json.dump(oauth_config, f, indent=2)

print("\n" + "=" * 80)
print("OAUTH 2.0 SETUP INSTRUCTIONS")
print("=" * 80)
print("\n1. Go to Google Cloud Console:")
print("   https://console.cloud.google.com/")
print("\n2. Create a new project (or select existing):")
print("   Project Name: Agent 5.0 Automation")
print("   Project ID: agent-5-automation")
print("\n3. Enable APIs (one by one):")
print("   - Gmail API")
print("   - Google Drive API")
print("   - Google Sheets API")
print("   - Google Calendar API")
print("\n4. Create OAuth 2.0 Credentials:")
print("   - Go to: APIs & Services > Credentials")
print("   - Click: + CREATE CREDENTIALS > OAuth client ID")
print("   - Application type: Web application")
print("   - Name: Agent 5.0 Automation")
print("   - Authorized redirect URIs: http://localhost:8080/")
print("\n5. Download credentials:")
print("   - Click download icon next to created OAuth 2.0 Client ID")
print("   - Save as: config/google/oauth_credentials.json")
print("\n6. Run authentication:")
print("   $ python scripts/google_oauth_flow.py")

# Create OAuth flow script
oauth_flow_script = """#!/usr/bin/env python3
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes for all APIs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/calendar'
]

def authenticate_google_apis():
    creds = None
    token_file = 'data/google_credentials/token.json'
    credentials_file = 'config/google/oauth_credentials.json'

    # Check if token already exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                print("ERROR: OAuth credentials file not found!")
                print(f"Please download from Google Cloud Console and save to:")
                print(f"  {credentials_file}")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save credentials for next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

        print("✅ Google APIs authenticated successfully!")
        print(f"   Token saved to: {token_file}")

    return creds

if __name__ == '__main__':
    print("=" * 80)
    print("GOOGLE APIs AUTHENTICATION")
    print("=" * 80)
    creds = authenticate_google_apis()
    if creds:
        print("\\n✅ Authentication complete!")
        print("   All Google APIs are now accessible")
    else:
        print("\\n⚠️ Authentication failed")
        print("   Follow setup instructions to configure OAuth 2.0")
"""

with open("scripts/google_oauth_flow.py", "w") as f:
    f.write(oauth_flow_script)

os.chmod("scripts/google_oauth_flow.py", 0o755)
print("\n✅ OAuth flow script created: scripts/google_oauth_flow.py")

# Integration config
integration_config = {
    "timestamp": datetime.now().isoformat(),
    "email_account": "appefilepro@gmail.com",
    "apis_enabled": list(google_apis.keys()),
    "oauth_status": "pending_credentials",
    "delegation": {
        "Communication Division": "Gmail API for email automation",
        "Integration Division": "Drive API for cloud storage",
        "Data Division": "Sheets API for tracking",
        "Management Division": "Calendar API for scheduling"
    },
    "zapier_integrations": [
        {
            "workflow": "Legal Document Auto-Download",
            "trigger": "Gmail (new attachment)",
            "action": "Drive (upload to folder)"
        },
        {
            "workflow": "Trading Bot Alerts",
            "trigger": "Python script (via webhook)",
            "action": "Gmail (send notification to appefilepro@gmail.com)"
        },
        {
            "workflow": "Agent 5.0 Status Log",
            "trigger": "Schedule (every hour)",
            "action": "Sheets (append row)"
        },
        {
            "workflow": "Deadline Reminders",
            "trigger": "Calendar (event start)",
            "action": "Gmail (send reminder)"
        }
    ]
}

with open("config/google/integration_config.json", "w") as f:
    json.dump(integration_config, f, indent=2)

print("✅ Integration config saved: config/google/integration_config.json")

print("\n" + "=" * 80)
print("GOOGLE APIS SETUP COMPLETE")
print("=" * 80)
print("\n📧 Email Account: appefilepro@gmail.com")
print(f"\n📋 APIs to Enable ({len(google_apis)}):")
for api_name in google_apis.keys():
    print(f"   • {api_name}")

print("\n📁 Configuration Files:")
print("   • config/google/oauth_credentials_template.json (template)")
print("   • config/google/oauth_credentials.json (download from Google)")
print("   • data/google_credentials/token.json (created after auth)")
print("   • config/google/integration_config.json (integration settings)")

print("\n🔄 Zapier Integrations:")
print(f"   • {len(integration_config['zapier_integrations'])} workflows configured")

print("\n🚀 Next Steps:")
print("   1. Follow instructions above to create OAuth 2.0 credentials")
print("   2. Download credentials to config/google/oauth_credentials.json")
print("   3. Run: python scripts/google_oauth_flow.py")
print("   4. Authorize in browser when prompted")
print("   5. Token will be saved for future use")

print("\n💰 Cost: FREE")
print("   • All Google APIs are free for personal use")
print("   • Gmail: 15GB storage free")
print("   • Drive: 15GB storage free (shared with Gmail)")
print("   • Sheets: Unlimited spreadsheets")
print("   • Calendar: Unlimited calendars")

print("\n" + "=" * 80)
print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
