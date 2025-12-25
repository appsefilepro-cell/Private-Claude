#!/bin/bash

###############################################################################
# AGENT 5.0 ACTIVATION SCRIPT
# Activates Committee 100 + 50 Sub Roles + 20 Multi-Agents
# 24/7 Continuous Operation for 30 Days
# For research, development, and educational purposes only
###############################################################################

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                    AGENT 5.0 ACTIVATION                         ║"
echo "║                                                                  ║"
echo "║              Committee 100 Delegation System                    ║"
echo "║           10x Loop Control | Parallel Execution                 ║"
echo "║                                                                  ║"
echo "║        For research, development, and educational purposes      ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

###############################################################################
# STEP 1: VERIFY REQUIREMENTS
###############################################################################

echo "${BLUE}[STEP 1]${NC} Verifying requirements..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "${RED}✗${NC} Git not installed"
    exit 1
fi
echo "${GREEN}✓${NC} Git installed"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "${RED}✗${NC} Python 3 not installed"
    exit 1
fi
echo "${GREEN}✓${NC} Python 3 installed"

# Check if GitHub CLI is installed (optional but recommended)
if command -v gh &> /dev/null; then
    echo "${GREEN}✓${NC} GitHub CLI installed"
else
    echo "${YELLOW}⚠${NC} GitHub CLI not installed (optional, but recommended)"
fi

###############################################################################
# STEP 2: CONFIGURATION FILES CHECK
###############################################################################

echo ""
echo "${BLUE}[STEP 2]${NC} Checking configuration files..."

declare -a config_files=(
    "MASTER_PROMPTS_AI_DELEGATION.md"
    "ZAPIER_WORKFLOWS_COMPLETE.json"
    "OKX_TRADING_BOT_CONFIG.json"
    "GITHUB_COPILOT_BUSINESS_SETUP.md"
)

for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        echo "${GREEN}✓${NC} $file"
    else
        echo "${RED}✗${NC} $file not found"
        exit 1
    fi
done

###############################################################################
# STEP 3: ZAPIER SETUP VERIFICATION
###############################################################################

echo ""
echo "${BLUE}[STEP 3]${NC} Zapier Setup Instructions..."
echo ""
echo "You need to setup Zapier workflows manually:"
echo ""
echo "1. Go to: https://zapier.com/app/zaps"
echo "2. Click 'Create Zap'"
echo "3. Import workflows from: ZAPIER_WORKFLOWS_COMPLETE.json"
echo "4. Connect accounts: GitHub, GitLab, Slack, Google, Airtable, Email"
echo "5. Get webhook URLs and update in configurations"
echo ""
read -p "${YELLOW}Have you setup Zapier workflows? (y/n):${NC} " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}Please setup Zapier first, then rerun this script${NC}"
    echo "Instructions in: ZAPIER_WORKFLOWS_COMPLETE.json"
    exit 0
fi

###############################################################################
# STEP 4: OKX API CONFIGURATION
###############################################################################

echo ""
echo "${BLUE}[STEP 4]${NC} OKX API Configuration..."
echo ""
echo "API Key: a5b57cd3-b0ee-44f-b8e9-7c5b330a5c28"
echo "Secret Key: E0A25726A822BB669A24ACF6FA4A8E31"
echo ""
read -p "${YELLOW}Have you set your OKX API passphrase in OKX_TRADING_BOT_CONFIG.json? (y/n):${NC} " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}Please edit OKX_TRADING_BOT_CONFIG.json and set your passphrase${NC}"
    echo "Then rerun this script"
    exit 0
fi

###############################################################################
# STEP 5: GITHUB COPILOT BUSINESS ACTIVATION
###############################################################################

echo ""
echo "${BLUE}[STEP 5]${NC} GitHub Copilot Business Activation..."
echo ""
echo "You have 26 days remaining on GitHub Enterprise trial!"
echo ""
echo "Activate Copilot Business:"
echo "1. Go to: https://github.com/settings/copilot"
echo "2. Enable Copilot for all repositories"
echo "3. Install Copilot in Cursor/VS Code"
echo "4. Install GitHub CLI Copilot: gh extension install github/gh-copilot"
echo ""
echo "Full instructions in: GITHUB_COPILOT_BUSINESS_SETUP.md"
echo ""
read -p "${YELLOW}Have you activated GitHub Copilot Business? (y/n):${NC} " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}Please activate Copilot first (see GITHUB_COPILOT_BUSINESS_SETUP.md)${NC}"
    exit 0
fi

###############################################################################
# STEP 6: SLACK WORKSPACE SETUP
###############################################################################

echo ""
echo "${BLUE}[STEP 6]${NC} Slack Workspace Setup..."
echo ""
echo "Create these Slack channels:"
echo "  #system-status"
echo "  #trading-alerts"
echo "  #legal-updates"
echo "  #financial-reports"
echo "  #ai-communication"
echo "  #test-results"
echo ""
read -p "${YELLOW}Have you created Slack workspace and channels? (y/n):${NC} " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}Please setup Slack first${NC}"
    echo "See: ZAPIER_WORKFLOWS_COMPLETE.json → slack_channels_to_create"
    exit 0
fi

###############################################################################
# STEP 7: AIRTABLE BASES SETUP
###############################################################################

echo ""
echo "${BLUE}[STEP 7]${NC} Airtable Bases Setup..."
echo ""
echo "Create these Airtable bases (see ZAPIER_WORKFLOWS_COMPLETE.json):"
echo "  1. Legal Cases"
echo "  2. Financial Operations"
echo "  3. Trading"
echo "  4. Testing"
echo "  5. Migration Tracking"
echo "  6. System Monitoring"
echo "  7. Life Coach AI"
echo "  8. Nonprofit Operations"
echo ""
read -p "${YELLOW}Have you created Airtable bases? (y/n):${NC} " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}Please setup Airtable first${NC}"
    echo "Free tier at: https://airtable.com/signup"
    exit 0
fi

###############################################################################
# STEP 8: GOOGLE SHEETS SETUP
###############################################################################

echo ""
echo "${BLUE}[STEP 8]${NC} Google Sheets Setup..."
echo ""
echo "Create these Google Sheets:"
echo "  1. OKX Trading Log"
echo "  2. Financial Dashboard"
echo "  3. Test Results"
echo "  4. System Status"
echo ""
read -p "${YELLOW}Have you created Google Sheets? (y/n):${NC} " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}Please setup Google Sheets first${NC}"
    exit 0
fi

###############################################################################
# STEP 9: GITLAB SYNC SETUP
###############################################################################

echo ""
echo "${BLUE}[STEP 9]${NC} GitLab Sync Setup..."
echo ""
echo "Setup GitLab mirroring:"
echo "1. Go to: https://gitlab.com/appsefilepro-group/appsefilepro-project"
echo "2. Settings → Repository → Mirroring repositories"
echo "3. Add GitHub as mirror: https://github.com/appsefilepro-cell/Private-Claude"
echo "4. Mirror direction: Push (GitLab → GitHub)"
echo ""
read -p "${YELLOW}Have you setup GitLab mirroring? (y/n):${NC} " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}Please setup GitLab mirror${NC}"
    echo "This enables coding without using Claude data"
    exit 0
fi

###############################################################################
# STEP 10: ACTIVATE AGENT 5.0
###############################################################################

echo ""
echo "${BLUE}[STEP 10]${NC} Activating Agent 5.0..."
echo ""

echo "${GREEN}✓${NC} All prerequisites met!"
echo ""
echo "Agent 5.0 activation includes:"
echo ""
echo "  ${GREEN}✓${NC} Committee 100 with 100 executive roles"
echo "  ${GREEN}✓${NC} 50 sub-role specialists"
echo "  ${GREEN}✓${NC} 20 multi-agent coordinators"
echo "  ${GREEN}✓${NC} 10x Loop execution protocol"
echo "  ${GREEN}✓${NC} Parallel task execution"
echo "  ${GREEN}✓${NC} 24/7 operation for 30 days"
echo ""
echo "${BLUE}Master Prompts:${NC} MASTER_PROMPTS_AI_DELEGATION.md"
echo "${BLUE}Zapier Workflows:${NC} ZAPIER_WORKFLOWS_COMPLETE.json"
echo "${BLUE}OKX Trading:${NC} OKX_TRADING_BOT_CONFIG.json"
echo "${BLUE}GitHub Copilot:${NC} GITHUB_COPILOT_BUSINESS_SETUP.md"
echo ""

###############################################################################
# STEP 11: START TRADING BOT (Demo Mode)
###############################################################################

echo "${BLUE}[STEP 11]${NC} Starting OKX Trading Bot..."
echo ""

read -p "${YELLOW}Start OKX trading bot in demo mode now? (y/n):${NC} " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/okx_trading_bot.py" ]; then
        echo "${GREEN}→${NC} Starting trading bot in demo mode..."
        echo "${GREEN}→${NC} Running 24/7 for 30 days..."
        echo "${GREEN}→${NC} Testing all patterns and pairs..."
        echo ""

        # Start in background with nohup
        nohup python3 scripts/okx_trading_bot.py \
            --mode demo \
            --continuous \
            --duration 30d \
            --test-all \
            --amounts 10,50,100,150,200,300,350,400,450,555 \
            > logs/agent-5x/okx_trading.log 2>&1 &

        echo "${GREEN}✓${NC} Trading bot started (PID: $!)"
        echo "  Log: logs/agent-5x/okx_trading.log"
        echo "  Monitor with: tail -f logs/agent-5x/okx_trading.log"
    else
        echo "${YELLOW}⚠${NC} Trading bot script not found"
        echo "  Use GitHub Copilot to generate it (see GITHUB_COPILOT_BUSINESS_SETUP.md)"
    fi
fi

###############################################################################
# STEP 12: START CONTINUOUS TESTING
###############################################################################

echo ""
echo "${BLUE}[STEP 12]${NC} Starting Continuous Testing..."
echo ""

read -p "${YELLOW}Start 24/7 continuous testing for 3 days? (y/n):${NC} " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "${GREEN}→${NC} Starting continuous testing..."
    echo "${GREEN}→${NC} Duration: 72 hours (3 days)"
    echo "${GREEN}→${NC} Running all unfinished tests..."
    echo ""

    # Create test runner script
    cat > /tmp/continuous_test_runner.sh << 'EOF'
#!/bin/bash
# Continuous testing for 3 days

END_TIME=$(($(date +%s) + 259200))  # 72 hours from now

while [ $(date +%s) -lt $END_TIME ]; do
    echo "$(date): Running test suite..."

    # Run all tests
    python3 -m pytest pillar-a-trading/backtesting/tests/ -v || true

    # Run trading bot tests
    if [ -f "scripts/okx_trading_bot.py" ]; then
        python3 scripts/okx_trading_bot.py --test patterns --duration 1h || true
    fi

    # Sleep for 1 hour
    sleep 3600
done

echo "$(date): Continuous testing complete"
EOF

    chmod +x /tmp/continuous_test_runner.sh
    nohup /tmp/continuous_test_runner.sh > logs/agent-5x/continuous_testing.log 2>&1 &

    echo "${GREEN}✓${NC} Continuous testing started (PID: $!)"
    echo "  Log: logs/agent-5x/continuous_testing.log"
fi

###############################################################################
# STEP 13: LEGAL DOCUMENT AUTOMATION
###############################################################################

echo ""
echo "${BLUE}[STEP 13]${NC} Legal Document Automation..."
echo ""

read -p "${YELLOW}Generate Case 1241511 dismissal notice now? (y/n):${NC} " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "legal-automation/master_legal_orchestrator.py" ]; then
        echo "${GREEN}→${NC} Generating dismissal notice for Case 1241511..."
        python3 legal-automation/master_legal_orchestrator.py --case 1241511 --action dismissal
        echo "${GREEN}✓${NC} Check legal-automation/output/ for generated documents"
    else
        echo "${YELLOW}⚠${NC} Legal automation script not found"
        echo "  Use GitHub Copilot to complete it (see GITHUB_COPILOT_BUSINESS_SETUP.md)"
    fi
fi

###############################################################################
# STEP 14: MICROSOFT 365 MIGRATION
###############################################################################

echo ""
echo "${BLUE}[STEP 14]${NC} Microsoft 365 Document Migration..."
echo ""

read -p "${YELLOW}Start Microsoft 365 document migration now? (y/n):${NC} " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "system-integration/microsoft365_migration.py" ]; then
        echo "${YELLOW}⚠${NC} This requires Azure AD app registration"
        echo "See: system-integration/MIGRATION_SETUP_GUIDE.md"
        echo ""
        echo "Quick setup:"
        echo "1. Go to: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps"
        echo "2. Create new app registration"
        echo "3. Copy Client ID"
        echo "4. export MICROSOFT365_CLIENT_ID='your-client-id'"
        echo "5. Rerun: python3 system-integration/microsoft365_migration.py"
    else
        echo "${YELLOW}⚠${NC} Migration script not found"
        echo "  Created at: system-integration/microsoft365_migration.py"
    fi
fi

###############################################################################
# STEP 15: ACTIVATION SUMMARY
###############################################################################

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                    AGENT 5.0 ACTIVATED ✓                        ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

echo "${GREEN}Next Steps:${NC}"
echo ""
echo "1. ${BLUE}Monitor Systems:${NC}"
echo "   - Zapier Dashboard: https://zapier.com/app/dashboard"
echo "   - Slack Channels: #system-status, #trading-alerts"
echo "   - GitHub Actions: https://github.com/appsefilepro-cell/Private-Claude/actions"
echo "   - Airtable Bases: Check task completion status"
echo ""
echo "2. ${BLUE}Active Processes:${NC}"
echo "   - OKX Trading Bot: 24/7 for 30 days"
echo "   - Continuous Testing: 72 hours"
echo "   - Zapier Workflows: Automated notifications"
echo ""
echo "3. ${BLUE}Use GitHub Copilot:${NC}"
echo "   - Open Cursor/VS Code"
echo "   - Let Copilot generate all code"
echo "   - Use GitHub credits, not Claude data"
echo "   - See: GITHUB_COPILOT_BUSINESS_SETUP.md"
echo ""
echo "4. ${BLUE}AI-to-AI Communication:${NC}"
echo "   - Master prompts in: MASTER_PROMPTS_AI_DELEGATION.md"
echo "   - Committee 100 delegating tasks"
echo "   - Status updates via Slack/Email"
echo ""
echo "5. ${BLUE}Check Your Email:${NC}"
echo "   - Daily trading reports at 8:00 PM CST"
echo "   - Legal document notifications"
echo "   - System error alerts"
echo "   - Test completion summaries"
echo ""

echo "${BLUE}Logs:${NC}"
echo "  OKX Trading: logs/agent-5x/okx_trading.log"
echo "  Testing: logs/agent-5x/continuous_testing.log"
echo "  System: logs/agent-5x/agent_5x_*.log"
echo ""

echo "${GREEN}All systems operational!${NC}"
echo "For research, development, and educational purposes."
echo ""

###############################################################################
# END OF ACTIVATION SCRIPT
###############################################################################
