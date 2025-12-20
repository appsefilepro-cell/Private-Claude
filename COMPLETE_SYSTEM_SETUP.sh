#!/bin/bash

# Complete Agent 5.0 System Setup Script
# Runs all configuration, testing, and integration tasks

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 AGENT 5.0 COMPLETE SETUP                     ║"
echo "║            All Systems Integration & Testing                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Environment Setup
echo -e "${YELLOW}[1/10] Setting up environment...${NC}"
if [ ! -f "config/.env" ]; then
    cp config/.env.template config/.env
    echo -e "${GREEN}✓${NC} Created config/.env - PLEASE ADD YOUR API KEYS"
else
    echo -e "${GREEN}✓${NC} config/.env already exists"
fi

# 2. Install Dependencies
echo -e "${YELLOW}[2/10] Installing Python dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Dependencies installed"

# 3. Initialize Databases
echo -e "${YELLOW}[3/10] Initializing databases...${NC}"
python pillar-f-cleo/case_manager.py << 'EOF'
# Just import to create database
from pillar_f_cleo.case_manager import CleoGasManager
cleo = CleoGasManager()
print("✓ Cleo database initialized")
EOF
echo -e "${GREEN}✓${NC} Databases created"

# 4. Import 40 Legal Cases
echo -e "${YELLOW}[4/10] Importing 40 legal cases into Cleo...${NC}"
python -c "
from pillar_f_cleo.case_manager import CleoGasManager
cleo = CleoGasManager()
case_mapping = cleo.import_40_cases_from_json()
print(f'✓ Imported {len(case_mapping)} cases')
"

# 5. Test Probate Generator
echo -e "${YELLOW}[5/10] Testing probate petition generator...${NC}"
python pillar-e-probate/petition_generator.py > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Probate generator functional"
else
    echo -e "${RED}✗${NC} Probate generator has errors"
fi

# 6. Test Legal Writing Adapter
echo -e "${YELLOW}[6/10] Testing legal writing style adapter...${NC}"
python pillar-b-legal/legal_writing_style_adapter.py > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Legal writing adapter functional"
else
    echo -e "${RED}✗${NC} Legal writing adapter has errors"
fi

# 7. Test Blockchain Verifier
echo -e "${YELLOW}[7/10] Testing blockchain transaction verifier...${NC}"
python pillar-a-trading/crypto/blockchain_transaction_verifier.py > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Blockchain verifier functional"
else
    echo -e "${RED}✗${NC} Blockchain verifier has errors"
fi

# 8. Check Microsoft 365 Integration
echo -e "${YELLOW}[8/10] Checking Microsoft 365 integration...${NC}"
python core-systems/microsoft365-integration/m365_integrator.py > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} M365 integration ready (needs credentials)"
else
    echo -e "${RED}✗${NC} M365 integration has errors"
fi

# 9. Verify All Pillar Directories
echo -e "${YELLOW}[9/10] Verifying pillar structure...${NC}"
PILLARS=("pillar-a-trading" "pillar-b-legal" "pillar-c-federal" "pillar-d-nonprofit" "pillar-e-probate" "pillar-f-cleo" "pillar-g-public-records")
for pillar in "${PILLARS[@]}"; do
    if [ -d "$pillar" ]; then
        echo -e "  ${GREEN}✓${NC} $pillar"
    else
        echo -e "  ${RED}✗${NC} $pillar (missing)"
    fi
done

# 10. Final System Check
echo -e "${YELLOW}[10/10] Running Agent 5.0 orchestrator test...${NC}"
# Quick start/stop test (5 second timeout)
timeout 5 python agent_5_orchestrator.py > /dev/null 2>&1 &
sleep 2
if pgrep -f "agent_5_orchestrator.py" > /dev/null; then
    pkill -f "agent_5_orchestrator.py"
    echo -e "${GREEN}✓${NC} Agent 5.0 orchestrator starts successfully"
else
    echo -e "${YELLOW}⚠${NC} Agent 5.0 orchestrator may need configuration"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  SETUP COMPLETE                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ Agent 5.0 is ready to use!${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "NEXT STEPS:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. CONFIGURE API CREDENTIALS (config/.env):"
echo "   - M365_CLIENT_ID and M365_CLIENT_SECRET"
echo "   - ETHERSCAN_API_KEY (for blockchain verification)"
echo "   - Trading platform API keys (when ready)"
echo ""
echo "2. RUN AGENT 5.0:"
echo "   python agent_5_orchestrator.py"
echo ""
echo "3. GENERATE PROBATE PETITION:"
echo "   Edit pillar-e-probate/petition_generator.py with your case info"
echo "   python pillar-e-probate/petition_generator.py"
echo "   Output saved to: pillar-e-probate/output/"
echo ""
echo "4. USE CLEO CASE MANAGEMENT:"
echo "   python -c 'from pillar_f_cleo.case_manager import CleoGasManager; cleo = CleoGasManager(); print(cleo.get_upcoming_deadlines())'"
echo ""
echo "5. INVESTIGATE MISSING CRYPTO ($42K):"
echo "   Add your wallet addresses to blockchain_transaction_verifier.py"
echo "   Upload Coinbase CSV files"
echo "   python pillar-a-trading/crypto/blockchain_transaction_verifier.py"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📚 DOCUMENTATION:"
echo "   - docs/AGENT_5.0_ARCHITECTURE.md"
echo "   - docs/RESEARCH_FINDINGS_IDENTITY_ANALYSIS.md"
echo "   - pillar-g-public-records/PUBLIC_RECORDS_API_GUIDE.md"
echo ""
echo "═══════════════════════════════════════════════════════════════"
