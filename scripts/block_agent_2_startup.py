
# Agent 2 Startup Blocker
# This script prevents Agent 2 from auto-starting

import sys
import os

print("🛑 Agent 2 startup blocked by control panel")
print("   To enable Agent 2, use: python scripts/agent_control_panel.py --enable 2")
sys.exit(0)
