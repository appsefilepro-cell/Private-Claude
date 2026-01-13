#!/bin/bash
#
# Execute Optimized Master Protocol
# Auth: Thurman Malik Robinson (Global Admin)
# 
# This script executes the master protocol in background mode
# with complete reporting upon 100% completion.
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROTOCOL_SCRIPT="$PROJECT_ROOT/core-systems/optimized_master_protocol.py"
LOGS_DIR="$PROJECT_ROOT/logs"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}OPTIMIZED MASTER PROTOCOL EXECUTOR${NC}"
echo -e "${BLUE}Auth: Thurman Malik Robinson (Global Admin)${NC}"
echo -e "${BLUE}Mode: Background Execution - Low Data Mode${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}ERROR: Python not found${NC}"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
echo -e "${GREEN}✓${NC} Python found: $PYTHON_CMD"

# Check if protocol script exists
if [ ! -f "$PROTOCOL_SCRIPT" ]; then
    echo -e "${RED}ERROR: Protocol script not found at $PROTOCOL_SCRIPT${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Protocol script found"

echo ""
echo -e "${YELLOW}Executing protocol...${NC}"
echo ""

# Execute protocol
if $PYTHON_CMD "$PROTOCOL_SCRIPT"; then
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}PROTOCOL EXECUTION SUCCESSFUL${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo "Results available in:"
    echo "  - $PROJECT_ROOT/core-systems/protocol_output/"
    echo "  - $PROJECT_ROOT/logs/master_protocol.log"
    echo ""
    echo "Dashboard updated:"
    echo "  - $PROJECT_ROOT/core-systems/cfo_dashboard_data.json"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}PROTOCOL EXECUTION FAILED${NC}"
    echo -e "${RED}============================================================${NC}"
    echo ""
    echo "Check logs for details:"
    echo "  - $PROJECT_ROOT/logs/master_protocol.log"
    echo ""
    exit 1
fi
