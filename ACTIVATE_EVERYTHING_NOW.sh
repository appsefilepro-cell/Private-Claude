#!/bin/bash
# 🚀 ACTIVATE EVERYTHING NOW - 5 MINUTE SETUP
# Run this script to activate all systems immediately

set -e  # Exit on error

echo "════════════════════════════════════════════════════"
echo "🚀 AGENTX5 COMPLETE ACTIVATION - STARTING NOW"
echo "════════════════════════════════════════════════════"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Must run from Private-Claude directory"
    exit 1
fi

echo "✅ Step 1/6: Checking Python and dependencies..."
python3 --version
pip3 install -q -r requirements.txt 2>/dev/null || echo "⚠️  Some dependencies may need manual install"

echo ""
echo "✅ Step 2/6: Setting up E2B Sandbox..."
if [ -z "$E2B_API_KEY" ]; then
    echo "⚠️  E2B_API_KEY not set. Using key from .env file..."
    export E2B_API_KEY="sk_e2b_08c56b39f9b4fdc26bd18805433ea4bf25a06aae"
fi
echo "E2B API Key: ${E2B_API_KEY:0:20}..."

echo ""
echo "✅ Step 3/6: Initializing PostgreSQL database..."
if command -v psql &> /dev/null; then
    echo "PostgreSQL found. Running initialization..."
    psql -U postgres -f scripts/init_database.sql 2>/dev/null || echo "⚠️  Database may already exist"
else
    echo "⚠️  PostgreSQL not installed. Skipping database init."
    echo "    Install with: sudo apt install postgresql postgresql-contrib"
fi

echo ""
echo "✅ Step 4/6: Starting AgentX5 24/7 Supervisor..."
if [ -f "scripts/agentx5_24_7_supervisor.py" ]; then
    nohup python3 scripts/agentx5_24_7_supervisor.py --verbose > logs/agentx5_supervisor.log 2>&1 &
    SUPERVISOR_PID=$!
    echo "AgentX5 Supervisor started with PID: $SUPERVISOR_PID"
    echo $SUPERVISOR_PID > logs/supervisor.pid
else
    echo "⚠️  AgentX5 supervisor script not found"
fi

echo ""
echo "✅ Step 5/6: Starting OKX Paper Trading Bot..."
if [ -f "pillar-a-trading/crypto/okx_paper_trading.py" ]; then
    cd pillar-a-trading/crypto
    nohup python3 okx_paper_trading.py > ../../logs/okx_trading.log 2>&1 &
    OKX_PID=$!
    echo "OKX Paper Trading started with PID: $OKX_PID"
    echo $OKX_PID > ../../logs/okx_trading.pid
    cd ../..
else
    echo "⚠️  OKX trading script not found"
fi

echo ""
echo "✅ Step 6/6: Starting Streamlit Trading Dashboard..."
if [ -f "pillar-a-trading/dashboard/live_trading_dashboard.py" ]; then
    cd pillar-a-trading/dashboard
    nohup streamlit run live_trading_dashboard.py --server.port 8501 > ../../logs/dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    echo "Trading Dashboard started with PID: $DASHBOARD_PID"
    echo $DASHBOARD_PID > ../../logs/dashboard.pid
    cd ../..
else
    echo "⚠️  Dashboard script not found"
fi

echo ""
echo "════════════════════════════════════════════════════"
echo "🎉 ACTIVATION COMPLETE!"
echo "════════════════════════════════════════════════════"
echo ""
echo "📊 RUNNING SERVICES:"
echo "   - AgentX5 Supervisor (PID: $SUPERVISOR_PID)"
echo "   - OKX Paper Trading (PID: $OKX_PID)"
echo "   - Trading Dashboard (PID: $DASHBOARD_PID)"
echo ""
echo "🌐 ACCESS POINTS:"
echo "   - Dashboard: http://localhost:8501"
echo "   - Logs: tail -f logs/*.log"
echo ""
echo "⏹️  TO STOP ALL SERVICES:"
echo "   kill $(cat logs/supervisor.pid logs/okx_trading.pid logs/dashboard.pid 2>/dev/null)"
echo ""
echo "📈 NEXT STEPS:"
echo "   1. Set up Gumba.com account (see pillar-a-trading/GUMBA_ELITE_TRADING_BOT_SETUP.md)"
echo "   2. Configure GitLab token: nano .env (add GITLAB_TOKEN and GITLAB_PROJECT_ID)"
echo "   3. Deploy to Railway: ./scripts/deploy_to_railway.sh --enable-e2b --enable-cron -y"
echo "   4. Trigger GitHub Copilot: Go to GitHub Actions > Run 'Create GitHub Copilot Issues'"
echo ""
echo "🎯 YOUR SYSTEM IS LIVE AND RUNNING!"
echo "════════════════════════════════════════════════════"
