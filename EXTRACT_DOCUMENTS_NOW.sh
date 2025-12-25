#!/bin/bash
###############################################################################
# MICROSOFT 365 DOCUMENT EXTRACTION - ONE-CLICK SOLUTION
# Run this script to extract ALL your documents before subscription ends
###############################################################################

set -e  # Exit on error

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     🚨 URGENT: MICROSOFT 365 DOCUMENT EXTRACTION 🚨             ║"
echo "║                                                                  ║"
echo "║     This will extract ALL your documents from:                  ║"
echo "║     • OneDrive                                                   ║"
echo "║     • SharePoint                                                 ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Change to the correct directory
cd /home/user/Private-Claude/system-integration

# Step 1: Install dependencies
echo "📦 Step 1/4: Installing required packages..."
pip3 install -q msal requests || {
    echo "⚠️  Failed to install dependencies. Trying with --user flag..."
    pip3 install --user -q msal requests
}
echo "✅ Dependencies installed"
echo ""

# Step 2: Check for Azure AD client ID
echo "🔑 Step 2/4: Checking authentication setup..."
if [ -z "$MICROSOFT365_CLIENT_ID" ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  ⚠️  AUTHENTICATION SETUP REQUIRED (ONE-TIME ONLY)              ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "You need to create an Azure AD app to access your documents."
    echo "This is FREE and takes 2 minutes. Here's how:"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "STEP-BY-STEP INSTRUCTIONS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Open this URL in your browser:"
    echo "   👉 https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade"
    echo ""
    echo "2. Click the '+ New registration' button"
    echo ""
    echo "3. Fill in the form:"
    echo "   • Name: Document Migration Tool"
    echo "   • Supported account types: Select the THIRD option"
    echo "     'Accounts in any organizational directory and personal Microsoft accounts'"
    echo "   • Redirect URI: Leave BLANK"
    echo ""
    echo "4. Click 'Register'"
    echo ""
    echo "5. You'll see the app page. Copy the 'Application (client) ID'"
    echo "   (It looks like: 12345678-1234-1234-1234-123456789abc)"
    echo ""
    echo "6. On the left menu, click 'API permissions'"
    echo ""
    echo "7. Click '+ Add a permission'"
    echo "   • Select 'Microsoft Graph'"
    echo "   • Select 'Delegated permissions'"
    echo "   • Search and check these permissions:"
    echo "     ✓ Files.Read.All"
    echo "     ✓ Sites.Read.All"
    echo "     ✓ User.Read"
    echo "   • Click 'Add permissions'"
    echo ""
    echo "8. Back in this terminal, run:"
    echo "   export MICROSOFT365_CLIENT_ID='paste-your-client-id-here'"
    echo ""
    echo "9. Then run this script again:"
    echo "   ./EXTRACT_DOCUMENTS_NOW.sh"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "❓ Need help? The full guide is at:"
    echo "   /home/user/Private-Claude/system-integration/MIGRATION_SETUP_GUIDE.md"
    echo ""
    exit 1
fi

echo "✅ Client ID found: ${MICROSOFT365_CLIENT_ID:0:8}..."
echo ""

# Step 3: Prepare output directory
echo "📁 Step 3/4: Preparing output directory..."
OUTPUT_DIR="/home/user/Private-Claude/migrated-docs"
mkdir -p "$OUTPUT_DIR"
echo "✅ Documents will be saved to: $OUTPUT_DIR"
echo ""

# Step 4: Run migration
echo "🚀 Step 4/4: Starting document extraction..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "IMPORTANT: You will need to authenticate with Microsoft"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "In a moment, you'll see a code and a URL."
echo "Follow these steps:"
echo ""
echo "1. Open the URL in your browser"
echo "2. Enter the code shown below"
echo "3. Sign in with your Microsoft 365 account"
echo "4. Approve the permissions"
echo "5. Come back here - download will start automatically!"
echo ""
echo "Press ENTER when ready to continue..."
read -r

# Run the migration tool
python3 microsoft365_migration.py

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                    ✅ EXTRACTION COMPLETE! ✅                    ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Your documents are in: $OUTPUT_DIR"
echo ""
echo "📊 Check these files for details:"
echo "   • $OUTPUT_DIR/migration_report.json"
echo "   • $OUTPUT_DIR/migration_report.csv"
echo ""
echo "📂 Your files are organized in:"
echo "   • $OUTPUT_DIR/onedrive/     (OneDrive files)"
echo "   • $OUTPUT_DIR/sharepoint/   (SharePoint files)"
echo ""
echo "🎉 Your documents are safe! You can cancel your subscription now."
echo ""
