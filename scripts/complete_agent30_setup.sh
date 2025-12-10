#!/bin/bash
# Complete Agent 3.0 Setup & Execution Script
# Runs all tests, backtests, and prepares for live trading

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         AGENT 3.0 COMPLETE SETUP & ACTIVATION                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /home/user/Private-Claude

# Step 1: System Activation
echo "STEP 1: Activating all systems..."
python scripts/activate_all_systems.py
echo ""

# Step 2: Integration Tests
echo "STEP 2: Running integration tests..."
python tests/integration_test_suite.py
echo ""

# Step 3: Zapier Integration Tests (if after 3am)
echo "STEP 3: Testing Zapier integrations..."
python tests/test_zapier_integrations.py
echo ""

# Step 4: 7-Day Backtest
echo "STEP 4: Running 7-day comprehensive backtest..."
python pillar-a-trading/backtesting/run_7day_backtest.py
echo ""

# Step 5: Sandbox Trading Monitor
echo "STEP 5: Checking live trading readiness..."
python scripts/sandbox_trading_monitor.py
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              AGENT 3.0 SETUP COMPLETE ✅                     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Next Steps:"
echo "1. Review test results in test-results/"
echo "2. Review backtest results in backtest-results/"
echo "3. Configure live API credentials if ready"
echo "4. Start sandbox trading when approved"
echo ""
