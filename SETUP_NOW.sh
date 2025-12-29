#!/bin/bash
#############################################
# AGENT X5 - ONE-CLICK SETUP
# Run this after opening in VS Code/Codespaces
#############################################

echo "=============================================="
echo "AGENT X5 - COMPLETE SETUP"
echo "=============================================="

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install E2B
echo "Installing E2B SDK..."
pip install e2b e2b-code-interpreter

# Set environment variables
export TRADING_MODE=PAPER
export LIVE_TRADING=false
export E2B_API_KEY="e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773"
export GEMINI_API_KEY="AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4"
export OKX_API_KEY="a5b57cd3-0bee-44f-b8e9-7c5b330a5c28"

# Create .env file
cat > .env << 'EOF'
# Agent X5 Environment
TRADING_MODE=PAPER
LIVE_TRADING=false
E2B_API_KEY=e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773
GEMINI_API_KEY=AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4
OKX_API_KEY=a5b57cd3-0bee-44f-b8e9-7c5b330a5c28
EOF

echo "Environment file created: .env"

# Check Docker
if command -v docker &> /dev/null; then
    echo "Docker found. Starting containers..."
    docker-compose up -d
    echo "Containers started!"
else
    echo "Docker not found. Install Docker Desktop first."
fi

# Run tests
echo "Running system tests..."
python scripts/run_all_tests.py

# Start E2B Sandbox
echo "Starting E2B Sandbox..."
python scripts/e2b_sandbox_launcher.py &

echo ""
echo "=============================================="
echo "SETUP COMPLETE"
echo "=============================================="
echo "250 Agents: READY"
echo "Trading Mode: PAPER"
echo "Sandbox: STARTING"
echo "=============================================="
