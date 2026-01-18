#!/bin/bash
# AgentX5 Ubuntu Native Deployment Script
# Deploys all pillars natively on Ubuntu 22.04+

set -e

echo "🚀 AgentX5 Ubuntu Native Deployment"
echo "======================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.11+ required. Current: $PYTHON_VERSION"
    echo "Installing Python 3.11..."
    sudo apt-get update
    sudo apt-get install -y python3.11 python3.11-venv python3-pip
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

echo "📦 Creating virtual environment..."
if [ ! -d "agentx5_env" ]; then
    python3 -m venv agentx5_env
fi

echo "🔧 Activating virtual environment..."
source agentx5_env/bin/activate

echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Creating necessary directories..."
mkdir -p logs data/gmail_attachments data/dropbox data/onedrive data/sharepoint

echo "✅ Dependencies installed successfully"
echo ""
echo "🚀 Starting AgentX5 Multi-Pillar System..."
echo "=========================================="

# Start agent revival system in background
echo "Starting Agent Revival System..."
python3 agent-4.0/orchestrator/agent_revival_system.py &
REVIVAL_PID=$!
echo "  ✓ Agent Revival System started (PID: $REVIVAL_PID)"

# Wait a moment for initialization
sleep 2

# Start Pillar B (Legal) in background
echo "Starting Pillar B (Legal)..."
python3 pillar-b-legal/legal_automation_framework.py &
LEGAL_PID=$!
echo "  ✓ Legal Automation started (PID: $LEGAL_PID)"

# Start Pillar C (Federal) in background
echo "Starting Pillar C (Federal)..."
python3 pillar-c-federal/federal_automation_framework.py &
FEDERAL_PID=$!
echo "  ✓ Federal Automation started (PID: $FEDERAL_PID)"

# Start Pillar D (Nonprofit) in background
echo "Starting Pillar D (Nonprofit)..."
python3 pillar-d-nonprofit/nonprofit_automation_framework.py &
NONPROFIT_PID=$!
echo "  ✓ Nonprofit Automation started (PID: $NONPROFIT_PID)"

echo ""
echo "✅ All systems deployed successfully!"
echo "======================================"
echo ""
echo "📊 Process IDs:"
echo "  Agent Revival: $REVIVAL_PID"
echo "  Legal:         $LEGAL_PID"
echo "  Federal:       $FEDERAL_PID"
echo "  Nonprofit:     $NONPROFIT_PID"
echo ""
echo "📋 Useful commands:"
echo "  View logs:        tail -f logs/*.log"
echo "  Check agent state: cat agent-4.0/state/agent_state.json"
echo "  Stop all:         kill $REVIVAL_PID $LEGAL_PID $FEDERAL_PID $NONPROFIT_PID"
echo ""
echo "🌐 Agent Revival System running on: http://localhost:8080"
echo ""

# Save PIDs to file for easy management
echo "$REVIVAL_PID" > logs/agentx5.pid
echo "$LEGAL_PID" >> logs/agentx5.pid
echo "$FEDERAL_PID" >> logs/agentx5.pid
echo "$NONPROFIT_PID" >> logs/agentx5.pid

echo "💾 PIDs saved to logs/agentx5.pid"
echo ""
echo "Press Ctrl+C to stop monitoring, services will continue running..."

# Wait for user interrupt
trap "echo ''; echo 'Services still running. To stop: kill \$(cat logs/agentx5.pid)'; exit 0" INT

# Monitor the processes
wait $REVIVAL_PID
