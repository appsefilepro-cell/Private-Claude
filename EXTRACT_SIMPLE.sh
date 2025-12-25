#!/bin/bash
###############################################################################
# INTERACTIVE SETUP - Walks you through Azure AD app creation
# This script helps you create the app step-by-step
###############################################################################

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     🚀 INTERACTIVE AZURE AD SETUP + EXTRACTION 🚀               ║"
echo "║                                                                  ║"
echo "║     I'll walk you through every step!                           ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -q msal requests 2>/dev/null || pip3 install --user -q msal requests
echo "✅ Dependencies ready"
echo ""

# Check if Client ID is already set
if [ -n "$MICROSOFT365_CLIENT_ID" ]; then
    echo "🔑 Client ID already configured: ${MICROSOFT365_CLIENT_ID:0:8}..."
    echo ""
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "STEP 1: CREATE AZURE AD APP (Takes 2 minutes)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "I'm opening Azure Portal in your default browser..."
    echo ""

    # Try to open browser
    if command -v xdg-open &> /dev/null; then
        xdg-open "https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade" 2>/dev/null &
    elif command -v open &> /dev/null; then
        open "https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade" 2>/dev/null &
    else
        echo "📋 Copy this URL to your browser:"
        echo "   https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade"
        echo ""
    fi

    echo "In the Azure Portal:"
    echo ""
    echo "  1. Click '+ New registration' button"
    echo "  2. Fill in:"
    echo "     • Name: Document Migration Tool"
    echo "     • Account types: Select 'Accounts in any organizational directory"
    echo "       and personal Microsoft accounts' (the THIRD option)"
    echo "     • Redirect URI: Leave BLANK"
    echo "  3. Click 'Register'"
    echo "  4. Copy the 'Application (client) ID' (looks like: abc123-def456...)"
    echo "  5. Go to 'API permissions' in left menu"
    echo "  6. Click '+ Add a permission' → Microsoft Graph → Delegated"
    echo "  7. Add these permissions:"
    echo "     ✓ Files.Read.All"
    echo "     ✓ Sites.Read.All"
    echo "     ✓ User.Read"
    echo "  8. Click 'Add permissions'"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -n "Paste your Application (client) ID here: "
    read -r CLIENT_ID

    if [ -z "$CLIENT_ID" ]; then
        echo "❌ No Client ID provided. Exiting."
        exit 1
    fi

    export MICROSOFT365_CLIENT_ID="$CLIENT_ID"
    echo ""
    echo "✅ Client ID saved for this session"
    echo ""
    echo "💡 TIP: To save permanently, run:"
    echo "   echo \"export MICROSOFT365_CLIENT_ID='$CLIENT_ID'\" >> ~/.bashrc"
    echo ""
fi

# Change to working directory
cd /home/user/Private-Claude/system-integration

# Create output directory
mkdir -p /home/user/Private-Claude/migrated-docs

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "AUTHENTICATION REQUIRED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "In a moment, you'll see a CODE and a URL."
echo ""
echo "What to do:"
echo "  1. Open the URL in your web browser"
echo "  2. Enter the CODE"
echo "  3. Sign in with your Microsoft 365 account"
echo "  4. Click 'Accept' to allow access"
echo "  5. Return here - extraction starts automatically!"
echo ""
echo "Press ENTER to continue..."
read -r
echo ""

# Run migration
python3 microsoft365_migration.py

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ EXTRACTION COMPLETE! ✅                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Your documents: /home/user/Private-Claude/migrated-docs/"
echo ""
echo "📊 Reports generated:"
echo "   • migration_report.json (detailed info)"
echo "   • migration_report.csv (spreadsheet view)"
echo ""
echo "🎉 Success! Your documents are now saved locally."
echo ""
