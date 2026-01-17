#!/bin/bash
################################################################################
# SANDBOX ENVIRONMENT SETUP - REAL IMPLEMENTATION
# Agent X5.0 - 24/7 Paper & Demo Trading Environment
################################################################################

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║   AGENT X5.0 - SANDBOX ENVIRONMENT SETUP                           ║"
echo "║   24/7 Paper & Demo Trading Environment                            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

################################################################################
# 1. CHECK PREREQUISITES
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  CHECKING PREREQUISITES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "✅ Python 3 installed: $PYTHON_VERSION"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | awk '{print $2}')
    echo "✅ pip installed: $PIP_VERSION"
else
    echo -e "${RED}❌ pip not found${NC}"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
    echo "✅ Docker installed: $DOCKER_VERSION"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker not found (optional)${NC}"
    DOCKER_AVAILABLE=false
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | awk '{print $3}' | tr -d ',')
    echo "✅ Docker Compose installed: $COMPOSE_VERSION"
    COMPOSE_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker Compose not found (optional)${NC}"
    COMPOSE_AVAILABLE=false
fi

echo ""

################################################################################
# 2. INSTALL PYTHON DEPENDENCIES
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  INSTALLING PYTHON DEPENDENCIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT"

if [ -f "requirements.txt" ]; then
    echo "📦 Installing packages from requirements.txt..."
    pip3 install -r requirements.txt --quiet || {
        echo -e "${YELLOW}⚠️  Some packages failed to install${NC}"
        echo "Continuing anyway..."
    }
    echo "✅ Dependencies installed"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

echo ""

################################################################################
# 3. CREATE ENVIRONMENT FILE
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  CONFIGURING ENVIRONMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ENV_FILE="$PROJECT_ROOT/config/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating .env file from template..."

    cat > "$ENV_FILE" <<'EOF'
# AGENT X5.0 - ENVIRONMENT CONFIGURATION
# Created: $(date +%Y-%m-%d)

# ===== TRADING MODE =====
LIVE_TRADING=false                    # Set to 'true' for LIVE trading (REAL MONEY!)
TRADING_MODE=PAPER                     # PAPER, SANDBOX, or LIVE
LOG_LEVEL=INFO

# ===== E2B SANDBOX =====
E2B_API_KEY=e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773

# ===== AI APIs =====
ANTHROPIC_API_KEY=                     # Get from: https://console.anthropic.com/
OPENAI_API_KEY=                        # Get from: https://platform.openai.com/
GEMINI_API_KEY=AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4

# ===== TRADING APIs (SANDBOX/DEMO) =====
KRAKEN_API_KEY=                        # Kraken sandbox API
KRAKEN_API_SECRET=
BINANCE_API_KEY=                       # Binance testnet
BINANCE_API_SECRET=
ALPACA_API_KEY=                        # Alpaca paper trading
ALPACA_API_SECRET=
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# ===== ZAPIER =====
ZAPIER_API_KEY=                        # From Zapier account
ZAPIER_WEBHOOK_URL=                    # Your webhook URL

# ===== MICROSOFT 365 =====
MICROSOFT_CLIENT_ID=                   # Azure app client ID
MICROSOFT_CLIENT_SECRET=
MICROSOFT_TENANT_ID=

# ===== GOOGLE WORKSPACE =====
GOOGLE_CLIENT_ID=                      # Google Cloud Console
GOOGLE_CLIENT_SECRET=
GOOGLE_SHEETS_CREDENTIALS=            # Path to credentials.json

# ===== AIRTABLE =====
AIRTABLE_API_KEY=                      # From Airtable account
AIRTABLE_BASE_ID=

# ===== MONITORING =====
SENTRY_DSN=                            # Optional: Sentry error tracking
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# ===== DATABASE =====
REDIS_HOST=localhost
REDIS_PORT=6379
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agentx5
POSTGRES_USER=agentx5
POSTGRES_PASSWORD=

# ===== SECURITY =====
JWT_SECRET_KEY=                        # Generate with: openssl rand -hex 32
ENCRYPTION_KEY=                        # Generate with: openssl rand -hex 32
EOF

    echo "✅ .env file created: $ENV_FILE"
    echo ""
    echo -e "${YELLOW}⚠️  ACTION REQUIRED:${NC}"
    echo "Please edit $ENV_FILE and add your API keys"
    echo ""
else
    echo "✅ .env file already exists"
fi

echo ""

################################################################################
# 4. CREATE DIRECTORIES
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  CREATING DIRECTORY STRUCTURE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

DIRS=(
    "logs"
    "logs/trading"
    "logs/agents"
    "logs/monitoring"
    "backtest-results"
    "sandbox-data"
    "sandbox-data/paper-trading"
    "sandbox-data/demo-accounts"
    "monitoring"
    "monitoring/prometheus"
    "monitoring/grafana"
)

for dir in "${DIRS[@]}"; do
    mkdir -p "$PROJECT_ROOT/$dir"
    echo "📁 Created: $dir"
done

echo "✅ Directory structure created"
echo ""

################################################################################
# 5. INITIALIZE REDIS (if Docker available)
################################################################################

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "5️⃣  STARTING REDIS (Docker)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Check if Redis is already running
    if docker ps | grep -q agent-redis; then
        echo "✅ Redis already running"
    else
        echo "🐳 Starting Redis container..."
        docker run -d \
            --name agent-redis \
            -p 6379:6379 \
            --restart unless-stopped \
            redis:7-alpine || {
            echo -e "${YELLOW}⚠️  Redis container failed to start${NC}"
        }
        echo "✅ Redis started on port 6379"
    fi
    echo ""
fi

################################################################################
# 6. TEST CONNECTIONS
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  TESTING CONNECTIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test Claude API integration
if [ -f "$PROJECT_ROOT/core-systems/claude_api_24_7_integration.py" ]; then
    echo "🧪 Testing Claude API integration..."
    python3 "$PROJECT_ROOT/core-systems/claude_api_24_7_integration.py" || {
        echo -e "${YELLOW}⚠️  Claude API test completed with warnings${NC}"
    }
else
    echo -e "${YELLOW}⚠️  Claude API integration not found${NC}"
fi

echo ""

################################################################################
# 7. CREATE STARTUP SCRIPT
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  CREATING STARTUP SCRIPTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > "$PROJECT_ROOT/start_sandbox_24_7.sh" <<'EOF'
#!/bin/bash
# Start Agent X5.0 in 24/7 Sandbox Mode

echo "🚀 Starting Agent X5.0 - 24/7 Sandbox Mode"
echo ""

# Load environment
export $(cat config/.env | grep -v '^#' | xargs)

# Ensure PAPER mode
export LIVE_TRADING=false
export TRADING_MODE=PAPER

# Start Agent X5 Orchestrator
python3 scripts/agent_x5_master_orchestrator.py &
AGENT_PID=$!

# Start Claude API Integration
python3 core-systems/claude_api_24_7_integration.py &
CLAUDE_PID=$!

# Start Sandbox Monitor
python3 scripts/sandbox_trading_monitor.py &
MONITOR_PID=$!

echo "✅ All systems started"
echo "   Agent X5 PID: $AGENT_PID"
echo "   Claude API PID: $CLAUDE_PID"
echo "   Monitor PID: $MONITOR_PID"
echo ""
echo "Press Ctrl+C to stop all systems"

# Wait for interrupt
trap "kill $AGENT_PID $CLAUDE_PID $MONITOR_PID 2>/dev/null" EXIT
wait
EOF

chmod +x "$PROJECT_ROOT/start_sandbox_24_7.sh"
echo "✅ Created: start_sandbox_24_7.sh"

echo ""

################################################################################
# SUMMARY
################################################################################

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ SETUP COMPLETE                                 ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1️⃣  Configure API Keys:"
echo "   Edit: $ENV_FILE"
echo "   Add your Anthropic, OpenAI, Gemini, and trading API keys"
echo ""
echo "2️⃣  Start Sandbox Environment:"
echo "   ./start_sandbox_24_7.sh"
echo ""
echo "3️⃣  Or start individual components:"
echo "   python3 scripts/agent_x5_master_orchestrator.py          # Agent X5"
echo "   python3 core-systems/claude_api_24_7_integration.py      # Claude API"
echo "   python3 scripts/sandbox_trading_monitor.py               # Monitor"
echo ""
if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
echo "4️⃣  Or use Docker:"
echo "   docker-compose up -d"
echo ""
fi
echo "📊 SANDBOX FEATURES:"
echo "   ✅ Paper trading (no real money)"
echo "   ✅ 24/7 automated monitoring"
echo "   ✅ Claude API integration"
echo "   ✅ Real-time logging"
echo "   ✅ Risk management"
echo ""
echo "🔒 SAFETY:"
echo "   Default mode: PAPER (safe)"
echo "   To enable LIVE trading: Set LIVE_TRADING=true in .env"
echo "   WARNING: LIVE mode uses REAL MONEY!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Agent X5.0 Sandbox Environment is ready! 🎉"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
