#!/bin/bash
###############################################################################
# TEST YOUR SETUP - Run this first to verify everything is configured
###############################################################################

echo ""
echo "🔍 Testing Microsoft 365 Migration Setup..."
echo ""

# Test 1: Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ Python installed: $PYTHON_VERSION"
else
    echo "   ❌ Python not found"
    exit 1
fi
echo ""

# Test 2: Check dependencies
echo "2. Checking Python packages..."
if python3 -c "import msal" 2>/dev/null; then
    echo "   ✅ msal installed"
else
    echo "   ⚠️  msal not installed - installing now..."
    pip3 install -q msal
    echo "   ✅ msal installed"
fi

if python3 -c "import requests" 2>/dev/null; then
    echo "   ✅ requests installed"
else
    echo "   ⚠️  requests not installed - installing now..."
    pip3 install -q requests
    echo "   ✅ requests installed"
fi
echo ""

# Test 3: Check Client ID
echo "3. Checking Azure AD configuration..."
if [ -z "$MICROSOFT365_CLIENT_ID" ]; then
    echo "   ⚠️  MICROSOFT365_CLIENT_ID not set"
    echo ""
    echo "   You need to:"
    echo "   1. Create an Azure AD app (see URGENT_READ_ME_FIRST.md)"
    echo "   2. Run: export MICROSOFT365_CLIENT_ID='your-client-id'"
    echo ""
    echo "   📖 Full instructions: /home/user/Private-Claude/URGENT_READ_ME_FIRST.md"
    echo ""
    exit 1
else
    echo "   ✅ Client ID configured: ${MICROSOFT365_CLIENT_ID:0:8}..."
fi
echo ""

# Test 4: Check output directory
echo "4. Checking output directory..."
OUTPUT_DIR="/home/user/Private-Claude/migrated-docs"
if [ -d "$OUTPUT_DIR" ]; then
    echo "   ✅ Output directory exists: $OUTPUT_DIR"
else
    echo "   ⚠️  Creating output directory..."
    mkdir -p "$OUTPUT_DIR"
    echo "   ✅ Output directory created: $OUTPUT_DIR"
fi
echo ""

# Test 5: Check migration script
echo "5. Checking migration script..."
SCRIPT_PATH="/home/user/Private-Claude/system-integration/microsoft365_migration.py"
if [ -f "$SCRIPT_PATH" ]; then
    echo "   ✅ Migration script found"
else
    echo "   ❌ Migration script not found at $SCRIPT_PATH"
    exit 1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL TESTS PASSED - YOU'RE READY TO EXTRACT!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Run this command to start extraction:"
echo "   ./EXTRACT_DOCUMENTS_NOW.sh"
echo ""
