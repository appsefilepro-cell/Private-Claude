#!/bin/bash
################################################################################
# AGENT 5.0 MASTER ACTIVATION SCRIPT
# Activates all 176 AI agents in the system
#
# Usage:
#   ./ACTIVATE_ALL_AGENTS.sh              # Start all agents
#   ./ACTIVATE_ALL_AGENTS.sh status       # Check status
#   ./ACTIVATE_ALL_AGENTS.sh stop         # Stop all agents
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
BASE_DIR="/home/user/Private-Claude"
ORCHESTRATOR_DIR="$BASE_DIR/agent-orchestrator"
LOG_FILE="$ORCHESTRATOR_DIR/activation.log"
PID_FILE="$ORCHESTRATOR_DIR/master.pid"

# Functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          AGENT 5.0 MASTER ACTIVATION SYSTEM               ║${NC}"
    echo -e "${BLUE}║          176 AI Agents + CFO Orchestrator                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

check_requirements() {
    print_info "Checking requirements..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"

    # Check orchestrator directory
    if [ ! -d "$ORCHESTRATOR_DIR" ]; then
        print_error "Orchestrator directory not found: $ORCHESTRATOR_DIR"
        exit 1
    fi
    print_success "Orchestrator directory exists"

    # Check required files
    required_files=(
        "$ORCHESTRATOR_DIR/agent_base.py"
        "$ORCHESTRATOR_DIR/agent_cfo.py"
        "$ORCHESTRATOR_DIR/agent_factory.py"
        "$ORCHESTRATOR_DIR/master_orchestrator.py"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    print_success "All required files present"

    echo ""
}

activate_agents() {
    print_header

    check_requirements

    echo -e "${GREEN}[ACTIVATION SEQUENCE INITIATED]${NC}\n"

    # Change to orchestrator directory
    cd "$ORCHESTRATOR_DIR"

    # Check if already running
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            print_error "Agent system is already running (PID: $OLD_PID)"
            echo ""
            echo "Use './ACTIVATE_ALL_AGENTS.sh stop' to stop it first"
            echo "Or use './ACTIVATE_ALL_AGENTS.sh status' to check status"
            exit 1
        else
            print_info "Removing stale PID file"
            rm -f "$PID_FILE"
        fi
    fi

    # Create log directory
    mkdir -p "$ORCHESTRATOR_DIR/logs"
    mkdir -p "$ORCHESTRATOR_DIR/status"
    mkdir -p "$ORCHESTRATOR_DIR/communication"

    print_info "Starting master orchestrator..."
    echo ""

    # Start the master orchestrator in background
    nohup python3 -u master_orchestrator.py > "$LOG_FILE" 2>&1 &
    MASTER_PID=$!

    # Save PID
    echo $MASTER_PID > "$PID_FILE"

    # Wait a moment for initialization
    sleep 3

    # Check if process is running
    if ps -p $MASTER_PID > /dev/null 2>&1; then
        print_success "Master orchestrator started (PID: $MASTER_PID)"
        echo ""

        echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  AGENT 5.0 SYSTEM ACTIVATED                               ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""

        echo "System Status:"
        echo "  • Master PID: $MASTER_PID"
        echo "  • CFO Agent: Starting..."
        echo "  • Worker Agents: 176 agents initializing..."
        echo ""

        echo "Monitoring:"
        echo "  • View logs: tail -f $LOG_FILE"
        echo "  • View executive report: cat $ORCHESTRATOR_DIR/EXECUTIVE_REPORT.md"
        echo "  • View system health: cat $ORCHESTRATOR_DIR/SYSTEM_HEALTH.json"
        echo "  • View agent status: ls -lh $ORCHESTRATOR_DIR/status/"
        echo ""

        echo "Control:"
        echo "  • Check status: $0 status"
        echo "  • Stop system: $0 stop"
        echo "  • View real-time logs: $0 logs"
        echo ""

        print_info "Agents will run for 72 hours (CFO) and complete 10x loops (workers)"
        echo ""

        # Show initial log output
        print_info "Initial system output:"
        echo ""
        sleep 2
        tail -n 20 "$LOG_FILE" 2>/dev/null || echo "  (Logs initializing...)"
        echo ""

    else
        print_error "Failed to start master orchestrator"
        echo ""
        echo "Check logs: cat $LOG_FILE"
        exit 1
    fi
}

check_status() {
    print_header

    echo -e "${BLUE}[SYSTEM STATUS CHECK]${NC}\n"

    # Check if PID file exists
    if [ ! -f "$PID_FILE" ]; then
        print_error "Agent system is not running (no PID file found)"
        echo ""
        echo "Use './ACTIVATE_ALL_AGENTS.sh' to start the system"
        exit 0
    fi

    # Check if process is running
    MASTER_PID=$(cat "$PID_FILE")
    if ! ps -p "$MASTER_PID" > /dev/null 2>&1; then
        print_error "Agent system is not running (PID $MASTER_PID not found)"
        rm -f "$PID_FILE"
        exit 0
    fi

    print_success "Master orchestrator is running (PID: $MASTER_PID)"
    echo ""

    # Check uptime
    START_TIME=$(ps -p "$MASTER_PID" -o lstart= 2>/dev/null)
    if [ -n "$START_TIME" ]; then
        echo "Started: $START_TIME"
    fi
    echo ""

    # Count agent status files
    if [ -d "$ORCHESTRATOR_DIR/status" ]; then
        TOTAL_AGENTS=$(ls -1 "$ORCHESTRATOR_DIR/status"/*.json 2>/dev/null | wc -l)
        echo "Agent Status Files: $TOTAL_AGENTS"

        # Analyze status
        if [ $TOTAL_AGENTS -gt 0 ]; then
            RUNNING=$(grep -l '"status".*running' "$ORCHESTRATOR_DIR/status"/*.json 2>/dev/null | wc -l)
            COMPLETED=$(grep -l '"status".*completed' "$ORCHESTRATOR_DIR/status"/*.json 2>/dev/null | wc -l)
            ERRORS=$(grep -l '"status".*error' "$ORCHESTRATOR_DIR/status"/*.json 2>/dev/null | wc -l)

            echo "  • Running: $RUNNING"
            echo "  • Completed: $COMPLETED"
            echo "  • Errors: $ERRORS"
        fi
    fi
    echo ""

    # Check for reports
    if [ -f "$ORCHESTRATOR_DIR/EXECUTIVE_REPORT.md" ]; then
        REPORT_TIME=$(stat -c %y "$ORCHESTRATOR_DIR/EXECUTIVE_REPORT.md" 2>/dev/null | cut -d'.' -f1)
        echo "Last Executive Report: $REPORT_TIME"
    fi

    if [ -f "$ORCHESTRATOR_DIR/SYSTEM_HEALTH.json" ]; then
        HEALTH=$(python3 -c "import json; print(json.load(open('$ORCHESTRATOR_DIR/SYSTEM_HEALTH.json'))['system_status'])" 2>/dev/null || echo "unknown")
        echo "System Health: $HEALTH"
    fi
    echo ""

    # Show recent log activity
    if [ -f "$LOG_FILE" ]; then
        echo "Recent Activity (last 10 lines):"
        echo "─────────────────────────────────────────────────────────────"
        tail -n 10 "$LOG_FILE" 2>/dev/null || echo "  (No logs yet)"
        echo "─────────────────────────────────────────────────────────────"
    fi
    echo ""
}

stop_agents() {
    print_header

    echo -e "${RED}[STOPPING AGENT SYSTEM]${NC}\n"

    if [ ! -f "$PID_FILE" ]; then
        print_info "No PID file found - system may not be running"
        exit 0
    fi

    MASTER_PID=$(cat "$PID_FILE")

    if ! ps -p "$MASTER_PID" > /dev/null 2>&1; then
        print_info "Process $MASTER_PID not found - cleaning up PID file"
        rm -f "$PID_FILE"
        exit 0
    fi

    print_info "Stopping master orchestrator (PID: $MASTER_PID)..."

    # Send SIGTERM
    kill -TERM "$MASTER_PID" 2>/dev/null || true

    # Wait for graceful shutdown
    for i in {1..10}; do
        if ! ps -p "$MASTER_PID" > /dev/null 2>&1; then
            print_success "System stopped gracefully"
            rm -f "$PID_FILE"
            exit 0
        fi
        sleep 1
    done

    # Force kill if still running
    print_info "Force stopping..."
    kill -KILL "$MASTER_PID" 2>/dev/null || true
    rm -f "$PID_FILE"

    print_success "System stopped"
    echo ""
}

view_logs() {
    print_header

    if [ ! -f "$LOG_FILE" ]; then
        print_error "Log file not found: $LOG_FILE"
        exit 1
    fi

    echo -e "${BLUE}[VIEWING REAL-TIME LOGS]${NC}"
    echo "Press Ctrl+C to stop"
    echo ""

    tail -f "$LOG_FILE"
}

# Main command handling
case "${1:-activate}" in
    activate|start)
        activate_agents
        ;;
    status)
        check_status
        ;;
    stop)
        stop_agents
        ;;
    logs)
        view_logs
        ;;
    *)
        echo "Usage: $0 {activate|start|status|stop|logs}"
        echo ""
        echo "Commands:"
        echo "  activate, start  - Activate all 176 agents"
        echo "  status           - Check system status"
        echo "  stop             - Stop all agents"
        echo "  logs             - View real-time logs"
        exit 1
        ;;
esac
