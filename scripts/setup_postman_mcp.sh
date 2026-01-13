#!/bin/bash
# Postman API MCP Setup Script for Agent X5.0
# This script helps set up Postman API integration

set -e

echo "======================================================================"
echo "  Postman API MCP Setup for Agent X5.0"
echo "======================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_ROOT/config"
ENV_FILE="$CONFIG_DIR/.env"
ENV_TEMPLATE="$CONFIG_DIR/.env.template"

echo -e "${BLUE}Project Root:${NC} $PROJECT_ROOT"
echo -e "${BLUE}Config Directory:${NC} $CONFIG_DIR"
echo ""

# Check if .env exists, create from template if not
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp "$ENV_TEMPLATE" "$ENV_FILE"
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""
echo "======================================================================"
echo "  Step 1: Postman API Key Setup"
echo "======================================================================"
echo ""
echo "To get your Postman API key:"
echo "1. Go to https://go.postman.co/settings/me/api-keys"
echo "2. Click 'Generate API Key'"
echo "3. Name it: 'Agent-X5-Integration'"
echo "4. Copy the API key"
echo ""

read -p "Do you have your Postman API key ready? (y/n): " has_api_key

if [ "$has_api_key" = "y" ]; then
    read -p "Enter your Postman API key: " api_key
    
    # Update .env file
    if grep -q "POSTMAN_API_KEY=" "$ENV_FILE"; then
        sed -i "s|POSTMAN_API_KEY=.*|POSTMAN_API_KEY=$api_key|" "$ENV_FILE"
    else
        echo "POSTMAN_API_KEY=$api_key" >> "$ENV_FILE"
    fi
    
    echo -e "${GREEN}✓ Postman API key configured${NC}"
else
    echo -e "${YELLOW}⚠ Skipping API key setup. You can add it later to config/.env${NC}"
fi

echo ""
echo "======================================================================"
echo "  Step 2: VS Code Extension Authentication"
echo "======================================================================"
echo ""
echo "The following authentication code is available:"
echo ""
echo -e "${BLUE}vscode://Postman.postman-for-vscode?code=482ee78e89079905b270c99d578eb06ae729773eb796e9544ba5e96ea37923fe${NC}"
echo ""
echo "This code has been configured in your .env file."
echo ""

# Set the VS Code auth code
VSCODE_AUTH_CODE="482ee78e89079905b270c99d578eb06ae729773eb796e9544ba5e96ea37923fe"
if grep -q "POSTMAN_VSCODE_AUTH_CODE=" "$ENV_FILE"; then
    sed -i "s|POSTMAN_VSCODE_AUTH_CODE=.*|POSTMAN_VSCODE_AUTH_CODE=$VSCODE_AUTH_CODE|" "$ENV_FILE"
else
    echo "POSTMAN_VSCODE_AUTH_CODE=$VSCODE_AUTH_CODE" >> "$ENV_FILE"
fi

echo -e "${GREEN}✓ VS Code auth code configured${NC}"

read -p "Do you want to open this URL in VS Code now? (y/n): " open_vscode

if [ "$open_vscode" = "y" ]; then
    if command -v code &> /dev/null; then
        echo "Opening VS Code with Postman extension..."
        code --install-extension Postman.postman-for-vscode 2>/dev/null || echo "Extension may already be installed"
        sleep 2
        xdg-open "vscode://Postman.postman-for-vscode?code=$VSCODE_AUTH_CODE" 2>/dev/null || \
        open "vscode://Postman.postman-for-vscode?code=$VSCODE_AUTH_CODE" 2>/dev/null || \
        echo "Please open VS Code manually and use the URL above"
    else
        echo -e "${YELLOW}VS Code command not found. Please install VS Code or use the URL manually.${NC}"
    fi
fi

echo ""
echo "======================================================================"
echo "  Step 3: Workspace Configuration"
echo "======================================================================"
echo ""

read -p "Do you have a Postman workspace ID? (y/n): " has_workspace

if [ "$has_workspace" = "y" ]; then
    read -p "Enter your Postman workspace ID: " workspace_id
    
    if grep -q "POSTMAN_WORKSPACE_ID=" "$ENV_FILE"; then
        sed -i "s|POSTMAN_WORKSPACE_ID=.*|POSTMAN_WORKSPACE_ID=$workspace_id|" "$ENV_FILE"
    else
        echo "POSTMAN_WORKSPACE_ID=$workspace_id" >> "$ENV_FILE"
    fi
    
    echo -e "${GREEN}✓ Workspace ID configured${NC}"
else
    echo -e "${YELLOW}⚠ Skipping workspace setup. The connector will list available workspaces.${NC}"
fi

echo ""
echo "======================================================================"
echo "  Step 4: Installing Dependencies"
echo "======================================================================"
echo ""

# Check for Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python 3 found${NC}"
    
    # Check for required packages
    echo "Checking Python dependencies..."
    python3 -c "import requests" 2>/dev/null || {
        echo "Installing requests..."
        pip3 install requests
    }
    
    python3 -c "import dotenv" 2>/dev/null || {
        echo "Installing python-dotenv..."
        pip3 install python-dotenv
    }
    
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.${NC}"
fi

# Check for Newman (optional)
echo ""
echo "Checking for Newman CLI (optional)..."
if command -v newman &> /dev/null; then
    echo -e "${GREEN}✓ Newman CLI found${NC}"
    newman --version
else
    echo -e "${YELLOW}⚠ Newman CLI not found${NC}"
    echo ""
    read -p "Would you like to install Newman? (requires npm) (y/n): " install_newman
    
    if [ "$install_newman" = "y" ]; then
        if command -v npm &> /dev/null; then
            echo "Installing Newman..."
            npm install -g newman
            echo -e "${GREEN}✓ Newman installed${NC}"
        else
            echo -e "${RED}✗ npm not found. Please install Node.js and npm first.${NC}"
        fi
    fi
fi

echo ""
echo "======================================================================"
echo "  Step 5: Testing Connection"
echo "======================================================================"
echo ""

if [ "$has_api_key" = "y" ]; then
    echo "Testing Postman API connection..."
    cd "$PROJECT_ROOT"
    
    python3 pillar-a-trading/zapier-integration/postman_mcp_connector.py 2>/dev/null || {
        echo -e "${YELLOW}⚠ Could not run automated test. You can test manually later.${NC}"
    }
else
    echo -e "${YELLOW}⚠ Skipping connection test (API key not configured)${NC}"
fi

echo ""
echo "======================================================================"
echo "  Setup Complete!"
echo "======================================================================"
echo ""
echo -e "${GREEN}✓ Postman API MCP integration is configured${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Test the connection:"
echo "   cd $PROJECT_ROOT"
echo "   python3 pillar-a-trading/zapier-integration/postman_mcp_connector.py"
echo ""
echo "2. Read the documentation:"
echo "   cat docs/POSTMAN_API_INTEGRATION.md"
echo ""
echo "3. Use the integrated connector:"
echo "   python3 pillar-a-trading/zapier-integration/integrated_mcp_connector.py"
echo ""
echo "4. Configure additional settings in:"
echo "   - config/.env (credentials)"
echo "   - config/postman_mcp_config.json (collections and monitors)"
echo ""
echo "Documentation: docs/POSTMAN_API_INTEGRATION.md"
echo ""
echo "======================================================================"
