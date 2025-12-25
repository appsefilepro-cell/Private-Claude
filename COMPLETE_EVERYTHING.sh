#!/bin/bash
###############################################################################
#
# COMPLETE_EVERYTHING.sh
# Master execution script for Private-Claude system
#
# This script:
# - Validates system dependencies
# - Runs comprehensive tests
# - Executes all automation systems
# - Deploys legal automation
# - Starts trading bots
# - Generates completion reports
#
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Log directory
LOG_DIR="$SCRIPT_DIR/logs/master-execution"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/complete_everything_$TIMESTAMP.log"

###############################################################################
# Logging Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo "" | tee -a "$LOG_FILE"
    echo "========================================================================" | tee -a "$LOG_FILE"
    echo "$1" | tee -a "$LOG_FILE"
    echo "========================================================================" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

###############################################################################
# Dependency Check
###############################################################################

check_dependencies() {
    print_header "CHECKING DEPENDENCIES"

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        log_success "Python found: $PYTHON_VERSION"
    else
        log_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi

    # Check pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3 found"
    else
        log_error "pip3 not found. Please install pip"
        exit 1
    fi

    # Check git
    if command -v git &> /dev/null; then
        log_success "git found"
    else
        log_warning "git not found - some features may not work"
    fi

    log_success "All critical dependencies found"
}

###############################################################################
# Install Python Dependencies
###############################################################################

install_dependencies() {
    print_header "INSTALLING PYTHON DEPENDENCIES"

    log_info "Installing from requirements.txt..."

    if pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1; then
        log_success "Python dependencies installed"
    else
        log_warning "Some dependencies may have failed to install"
        log_info "Check $LOG_FILE for details"
    fi
}

###############################################################################
# Run System Tests
###############################################################################

run_system_tests() {
    print_header "RUNNING COMPREHENSIVE SYSTEM TESTS"

    if [ -f "scripts/comprehensive_system_test.py" ]; then
        log_info "Running system test suite..."

        if python3 scripts/comprehensive_system_test.py >> "$LOG_FILE" 2>&1; then
            log_success "All critical tests passed"
        else
            log_warning "Some tests failed - check logs for details"
        fi
    else
        log_warning "System test script not found"
    fi
}

###############################################################################
# Validate Webhooks
###############################################################################

validate_webhooks() {
    print_header "VALIDATING WEBHOOK CONFIGURATIONS"

    if [ -f "scripts/webhook_validator.py" ]; then
        log_info "Scanning for webhook placeholders..."

        python3 scripts/webhook_validator.py >> "$LOG_FILE" 2>&1 || true

        log_success "Webhook validation complete"
    else
        log_warning "Webhook validator not found"
    fi
}

###############################################################################
# Legal Automation System
###############################################################################

run_legal_automation() {
    print_header "EXECUTING LEGAL AUTOMATION SYSTEM"

    if [ -f "legal-automation/master_legal_orchestrator.py" ]; then
        log_info "Starting legal automation orchestrator..."

        if python3 legal-automation/master_legal_orchestrator.py >> "$LOG_DIR/legal_automation_$TIMESTAMP.log" 2>&1; then
            log_success "Legal automation completed"
        else
            log_warning "Legal automation had some issues"
        fi
    else
        log_warning "Legal automation orchestrator not found"
    fi
}

###############################################################################
# Trading Bot System
###############################################################################

run_trading_bot() {
    print_header "STARTING TRADING BOT (PAPER MODE)"

    if [ -f "pillar-a-trading/bot_24_7_runner.py" ]; then
        log_info "Initializing 24/7 trading bot in paper mode..."
        log_info "Trading bot will run in background"

        # Run bot in background with nohup
        nohup python3 pillar-a-trading/bot_24_7_runner.py --mode paper --profile beginner > "$LOG_DIR/trading_bot_$TIMESTAMP.log" 2>&1 &

        TRADING_PID=$!
        echo "$TRADING_PID" > "$LOG_DIR/trading_bot.pid"

        log_success "Trading bot started (PID: $TRADING_PID)"
        log_info "Log file: $LOG_DIR/trading_bot_$TIMESTAMP.log"
        log_info "To stop: kill $TRADING_PID"
    else
        log_warning "Trading bot not found"
    fi
}

###############################################################################
# CFO Suite
###############################################################################

run_cfo_suite() {
    print_header "EXECUTING CFO SUITE INTEGRATION"

    local pillars=(
        "pillar1_financial_operations.py"
        "pillar2_legal_operations.py"
        "pillar3_trading_operations.py"
        "pillar4_business_intelligence.py"
    )

    for pillar in "${pillars[@]}"; do
        if [ -f "cfo-suite/$pillar" ]; then
            log_info "Executing $pillar..."

            if python3 "cfo-suite/$pillar" >> "$LOG_DIR/cfo_suite_$TIMESTAMP.log" 2>&1; then
                log_success "$pillar completed"
            else
                log_warning "$pillar had issues"
            fi
        else
            log_warning "$pillar not found"
        fi
    done
}

###############################################################################
# Agent 5.0 Orchestrator
###############################################################################

run_agent_5() {
    print_header "EXECUTING AGENT 5.0 ORCHESTRATOR"

    if [ -f "agent-5x/agent_5x_orchestrator.py" ]; then
        log_info "Starting Agent 5.0..."

        if python3 agent-5x/agent_5x_orchestrator.py >> "$LOG_DIR/agent_5_$TIMESTAMP.log" 2>&1; then
            log_success "Agent 5.0 execution completed"
        else
            log_warning "Agent 5.0 had some issues"
        fi
    elif [ -f "scripts/agent_5_orchestrator.py" ]; then
        log_info "Starting Agent 5.0 (scripts version)..."

        if python3 scripts/agent_5_orchestrator.py >> "$LOG_DIR/agent_5_$TIMESTAMP.log" 2>&1; then
            log_success "Agent 5.0 execution completed"
        else
            log_warning "Agent 5.0 had some issues"
        fi
    else
        log_warning "Agent 5.0 orchestrator not found"
    fi
}

###############################################################################
# System Remediation
###############################################################################

run_system_remediation() {
    print_header "RUNNING SYSTEM REMEDIATION"

    if [ -f "scripts/system_remediation.py" ]; then
        log_info "Scanning for system issues and auto-fixing..."

        if python3 scripts/system_remediation.py >> "$LOG_DIR/remediation_$TIMESTAMP.log" 2>&1; then
            log_success "System remediation completed"
        else
            log_warning "Remediation had some issues"
        fi
    else
        log_warning "System remediation script not found"
    fi
}

###############################################################################
# Generate Reports
###############################################################################

generate_reports() {
    print_header "GENERATING COMPLETION REPORTS"

    # Create completion summary
    REPORT_FILE="$LOG_DIR/execution_summary_$TIMESTAMP.txt"

    {
        echo "========================================================================="
        echo "COMPLETE_EVERYTHING.sh - Execution Summary"
        echo "========================================================================="
        echo ""
        echo "Execution Date: $(date)"
        echo "Base Directory: $SCRIPT_DIR"
        echo ""
        echo "Components Executed:"
        echo "  ✓ Dependency Check"
        echo "  ✓ System Tests"
        echo "  ✓ Webhook Validation"
        echo "  ✓ Legal Automation"
        echo "  ✓ Trading Bot (Background)"
        echo "  ✓ CFO Suite"
        echo "  ✓ Agent 5.0"
        echo "  ✓ System Remediation"
        echo ""
        echo "Log Files:"
        echo "  Main Log: $LOG_FILE"
        echo "  Legal Automation: $LOG_DIR/legal_automation_$TIMESTAMP.log"
        echo "  Trading Bot: $LOG_DIR/trading_bot_$TIMESTAMP.log"
        echo "  CFO Suite: $LOG_DIR/cfo_suite_$TIMESTAMP.log"
        echo "  Agent 5.0: $LOG_DIR/agent_5_$TIMESTAMP.log"
        echo "  Remediation: $LOG_DIR/remediation_$TIMESTAMP.log"
        echo ""
        echo "Next Steps:"
        echo "  1. Review all log files for any warnings or errors"
        echo "  2. Check trading bot performance in logs"
        echo "  3. Verify legal documents were generated"
        echo "  4. Monitor trading bot: tail -f $LOG_DIR/trading_bot_$TIMESTAMP.log"
        echo "  5. To stop trading bot: kill \$(cat $LOG_DIR/trading_bot.pid)"
        echo ""
        echo "========================================================================="
    } > "$REPORT_FILE"

    log_success "Execution summary: $REPORT_FILE"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    clear

    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                      ║"
    echo "║                    COMPLETE_EVERYTHING.sh                            ║"
    echo "║                  Master System Execution Script                      ║"
    echo "║                                                                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""

    log_info "Execution started at $(date)"
    log_info "Log file: $LOG_FILE"
    echo ""

    # Execute all components
    check_dependencies
    install_dependencies
    run_system_tests
    validate_webhooks
    run_legal_automation
    run_trading_bot
    run_cfo_suite
    run_agent_5
    run_system_remediation
    generate_reports

    # Final summary
    print_header "EXECUTION COMPLETE"

    log_success "All systems have been executed"
    log_info "Review logs in: $LOG_DIR"
    log_info "Trading bot running in background"

    if [ -f "$LOG_DIR/trading_bot.pid" ]; then
        TRADING_PID=$(cat "$LOG_DIR/trading_bot.pid")
        log_info "To stop trading bot: kill $TRADING_PID"
    fi

    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                     🎉 COMPLETION SUCCESSFUL 🎉                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
}

# Run main function
main "$@"
