#!/bin/bash
#
# Install Agent 5.0 systemd services for 24/7 operation
# Run with: sudo bash scripts/install_systemd_services.sh
#

set -e

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║       Installing Agent 5.0 systemd services for 24/7 operation   ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)"
    exit 1
fi

PROJECT_ROOT="/home/user/Private-Claude"
SERVICE_DIR="/etc/systemd/system"

echo "Step 1: Copying service files..."
cp "$PROJECT_ROOT/config/agent-5-orchestrator.service" "$SERVICE_DIR/"
cp "$PROJECT_ROOT/config/committee-100-orchestrator.service" "$SERVICE_DIR/"
echo "✓ Service files copied"

echo ""
echo "Step 2: Setting correct permissions..."
chmod 644 "$SERVICE_DIR/agent-5-orchestrator.service"
chmod 644 "$SERVICE_DIR/committee-100-orchestrator.service"
echo "✓ Permissions set"

echo ""
echo "Step 3: Reloading systemd daemon..."
systemctl daemon-reload
echo "✓ Systemd daemon reloaded"

echo ""
echo "Step 4: Enabling services..."
systemctl enable agent-5-orchestrator.service
systemctl enable committee-100-orchestrator.service
echo "✓ Services enabled"

echo ""
echo "═════════════════════════════════════════════════════════════════════"
echo "Installation complete!"
echo ""
echo "Available commands:"
echo ""
echo "  Start Agent 5.0:"
echo "    sudo systemctl start agent-5-orchestrator"
echo ""
echo "  Start Committee 100:"
echo "    sudo systemctl start committee-100-orchestrator"
echo ""
echo "  Check status:"
echo "    sudo systemctl status agent-5-orchestrator"
echo "    sudo systemctl status committee-100-orchestrator"
echo ""
echo "  View logs:"
echo "    sudo journalctl -u agent-5-orchestrator -f"
echo "    sudo journalctl -u committee-100-orchestrator -f"
echo ""
echo "  Stop services:"
echo "    sudo systemctl stop agent-5-orchestrator"
echo "    sudo systemctl stop committee-100-orchestrator"
echo ""
echo "  Disable services:"
echo "    sudo systemctl disable agent-5-orchestrator"
echo "    sudo systemctl disable committee-100-orchestrator"
echo ""
echo "═════════════════════════════════════════════════════════════════════"
