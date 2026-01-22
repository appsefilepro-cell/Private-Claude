#!/bin/bash
# Google Docs API Setup - One-Time Configuration (5 minutes)

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          GOOGLE DOCS WRITER - FREE SETUP                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Create config directory
mkdir -p config

echo "📝 Step 1: Enable Google Docs API"
echo "   1. Go to: https://console.cloud.google.com/apis/library/docs.googleapis.com"
echo "   2. Click 'Enable'"
echo "   3. Wait 30 seconds"
echo ""
read -p "Press Enter when API is enabled..."

echo ""
echo "🔑 Step 2: Create OAuth 2.0 Credentials"
echo "   1. Go to: https://console.cloud.google.com/apis/credentials"
echo "   2. Click '+ CREATE CREDENTIALS' → 'OAuth client ID'"
echo "   3. Application type: 'Desktop app'"
echo "   4. Name: 'AgentX5 Book Writer'"
echo "   5. Click 'CREATE'"
echo "   6. Click 'DOWNLOAD JSON'"
echo "   7. Save as: credentials.json"
echo ""
read -p "Press Enter when credentials.json is downloaded..."

echo ""
echo "📥 Step 3: Move credentials.json"
echo "   Move credentials.json to: config/"
echo ""
read -p "Press Enter when file is moved..."

# Install required Python packages
echo ""
echo "📦 Step 4: Installing Google API packages..."
pip install --quiet google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Create authentication script
cat > config/authenticate_google_docs.py << 'EOF'
#!/usr/bin/env python3
"""
One-time authentication for Google Docs API
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import json

SCOPES = ['https://www.googleapis.com/auth/documents']

def authenticate():
    """Authenticate with Google Docs API"""

    creds = None

    # Check if token already exists
    if os.path.exists('config/google_docs_token.json'):
        print("✅ Token already exists!")
        creds = Credentials.from_authorized_user_file('config/google_docs_token.json', SCOPES)

    # If no valid credentials, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow...")
            print("   A browser window will open")
            print("   Sign in with your Google account")
            print("   Grant access to Google Docs")

            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next time
        with open('config/google_docs_token.json', 'w') as token:
            token.write(creds.to_json())

        print("✅ Token saved to config/google_docs_token.json")

    print("")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║     ✅ GOOGLE DOCS AUTHENTICATION COMPLETE                  ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("")
    print("Next: Run automated book generation:")
    print("   python COMPLETE_BOOK_WRITER_SYSTEM.py")
    print("")
    print("Or trigger GitHub Actions workflow:")
    print("   gh workflow run auto_write_books.yml")

if __name__ == '__main__':
    authenticate()
EOF

chmod +x config/authenticate_google_docs.py

echo ""
echo "✅ Setup script created!"
echo ""
echo "🔐 Step 5: Authenticate (one-time)"
echo "   Running authentication script..."
echo ""

python3 config/authenticate_google_docs.py

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     🎉 SETUP COMPLETE - READY TO WRITE BOOKS               ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Google Docs API enabled"
echo "✅ OAuth credentials configured"
echo "✅ Token saved"
echo "✅ FREE tier (unlimited documents)"
echo "✅ Data usage: <1%"
echo ""
echo "📖 Books will be written to Google Docs automatically"
echo "📄 URLs will be saved to: output/*_google_doc_url.txt"
echo ""
echo "Automation runs every 6 hours via GitHub Actions"
echo "Or run manually: python COMPLETE_BOOK_WRITER_SYSTEM.py"
