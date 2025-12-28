"""
Agent Control Panel - Stop Agent 2 Python Popups
Controls which agents auto-start and run in background
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Optional


class AgentControlPanel:
    """Control panel for managing agent execution"""

    def __init__(self):
        """Initialize agent control panel"""
        self.state_file = Path("agent-4.0/state/agent_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        self.agents = self.load_agent_state()

    def load_agent_state(self) -> dict:
        """Load current agent state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        else:
            # Create default state
            return {
                "agents": [
                    {
                        "agent_id": i,
                        "status": "enabled" if i != 2 else "disabled",
                        "auto_start": i != 2,
                        "name": f"Agent {i}"
                    }
                    for i in range(1, 21)
                ],
                "last_updated": None
            }

    def save_agent_state(self):
        """Save agent state to file"""
        from datetime import datetime
        self.agents["last_updated"] = datetime.now().isoformat()

        with open(self.state_file, 'w') as f:
            json.dump(self.agents, f, indent=2)

        print(f"✅ Agent state saved to {self.state_file}")

    def disable_agent(self, agent_id: int):
        """Disable specific agent"""
        for agent in self.agents.get("agents", []):
            # Handle both 'id' and 'agent_id' keys
            current_id = agent.get("agent_id") or agent.get("id")
            if current_id == agent_id:
                agent["status"] = "disabled"
                agent["auto_start"] = False
                print(f"🛑 Agent {agent_id} ({agent.get('name', 'Unknown')}) disabled - will NOT auto-start")
                return

        print(f"❌ Agent {agent_id} not found")

    def enable_agent(self, agent_id: int):
        """Enable specific agent"""
        for agent in self.agents.get("agents", []):
            # Handle both 'id' and 'agent_id' keys
            current_id = agent.get("agent_id") or agent.get("id")
            if current_id == agent_id:
                agent["status"] = "enabled"
                agent["auto_start"] = True
                print(f"✅ Agent {agent_id} ({agent.get('name', 'Unknown')}) enabled - will auto-start")
                return

        print(f"❌ Agent {agent_id} not found")

    def disable_multiple(self, agent_ids: List[int]):
        """Disable multiple agents"""
        for agent_id in agent_ids:
            self.disable_agent(agent_id)

    def enable_multiple(self, agent_ids: List[int]):
        """Enable multiple agents"""
        for agent_id in agent_ids:
            self.enable_agent(agent_id)

    def disable_all_except(self, keep_enabled: List[int]):
        """Disable all agents except specified ones"""
        for agent in self.agents.get("agents", []):
            # Handle both 'id' and 'agent_id' keys
            current_id = agent.get("agent_id") or agent.get("id")
            if current_id in keep_enabled:
                agent["status"] = "enabled"
                agent["auto_start"] = True
            else:
                agent["status"] = "disabled"
                agent["auto_start"] = False

        print(f"✅ Enabled only agents: {keep_enabled}")
        print(f"🛑 Disabled all others")

    def show_status(self):
        """Show status of all agents"""
        print("\n" + "=" * 70)
        print("AGENT STATUS PANEL")
        print("=" * 70)

        enabled_count = 0
        disabled_count = 0

        print(f"\n{'ID':<5} {'Name':<15} {'Status':<12} {'Auto-Start':<12}")
        print("-" * 70)

        for agent in self.agents.get("agents", []):
            # Handle both 'id' and 'agent_id' keys
            agent_id = agent.get("agent_id") or agent.get("id", 0)
            name = agent.get("name", "Unknown")
            status = agent.get("status", "idle")
            auto_start = "Yes" if agent.get("auto_start", False) else "No"

            # Status icons
            if status == "enabled":
                status_icon = "✅"
                enabled_count += 1
            elif status == "disabled":
                status_icon = "🛑"
                disabled_count += 1
            else:
                status_icon = "🛑"  # idle/unknown = disabled
                disabled_count += 1

            print(f"{agent_id:<5} {name:<30} {status_icon} {status:<10} {auto_start:<12}")

        print("-" * 70)
        print(f"\nEnabled: {enabled_count} | Disabled: {disabled_count} | Total: {len(self.agents.get('agents', []))}")
        print(f"Last Updated: {self.agents.get('last_updated', 'Never')}\n")

    def stop_agent_2_popup(self):
        """Specifically stop Agent 2 from auto-starting (fixes popup issue)"""
        print("\n🛑 STOPPING AGENT 2 PYTHON POPUP...")

        # Disable Agent 2
        self.disable_agent(2)

        # Also check for any startup scripts
        startup_scripts = [
            Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup",
            Path("/etc/init.d"),
            Path.home() / ".config/autostart"
        ]

        for startup_dir in startup_scripts:
            if startup_dir.exists():
                for script in startup_dir.glob("*agent*2*.py"):
                    print(f"⚠️  Found startup script: {script}")
                    print(f"   Consider removing it to prevent auto-start")

        print("\n✅ Agent 2 disabled in configuration")
        print("   It will no longer auto-start or show popups")

    def create_startup_blocker(self):
        """Create a blocker script that prevents Agent 2 from starting"""
        blocker_script = Path("scripts/block_agent_2_startup.py")

        blocker_code = """
# Agent 2 Startup Blocker
# This script prevents Agent 2 from auto-starting

import sys
import os

print("🛑 Agent 2 startup blocked by control panel")
print("   To enable Agent 2, use: python scripts/agent_control_panel.py --enable 2")
sys.exit(0)
"""

        with open(blocker_script, 'w') as f:
            f.write(blocker_code)

        print(f"✅ Blocker script created: {blocker_script}")


def parse_agent_list(agent_str: str) -> List[int]:
    """Parse comma-separated agent IDs"""
    try:
        return [int(x.strip()) for x in agent_str.split(',')]
    except ValueError:
        print(f"❌ Invalid agent ID format: {agent_str}")
        return []


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Agent Control Panel - Manage which agents auto-start"
    )

    parser.add_argument(
        '--enable',
        type=str,
        help='Enable agent(s). Use comma-separated IDs: --enable 1,3,4'
    )

    parser.add_argument(
        '--disable',
        type=str,
        help='Disable agent(s). Use comma-separated IDs: --disable 2,5'
    )

    parser.add_argument(
        '--only',
        type=str,
        help='Enable only these agents, disable all others: --only 1,3,4,5'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current status of all agents'
    )

    parser.add_argument(
        '--stop-agent-2',
        action='store_true',
        help='Stop Agent 2 Python popup (quick fix)'
    )

    args = parser.parse_args()

    # Create control panel
    panel = AgentControlPanel()

    # Execute commands
    if args.stop_agent_2:
        panel.stop_agent_2_popup()
        panel.create_startup_blocker()
        panel.save_agent_state()

    elif args.enable:
        agent_ids = parse_agent_list(args.enable)
        if agent_ids:
            panel.enable_multiple(agent_ids)
            panel.save_agent_state()

    elif args.disable:
        agent_ids = parse_agent_list(args.disable)
        if agent_ids:
            panel.disable_multiple(agent_ids)
            panel.save_agent_state()

    elif args.only:
        agent_ids = parse_agent_list(args.only)
        if agent_ids:
            panel.disable_all_except(agent_ids)
            panel.save_agent_state()

    elif args.status:
        panel.show_status()

    else:
        # Default: show status
        panel.show_status()

        print("\nQuick Commands:")
        print("  Stop Agent 2 popup:  python scripts/agent_control_panel.py --stop-agent-2")
        print("  Enable agents:       python scripts/agent_control_panel.py --enable 1,3,4")
        print("  Disable agents:      python scripts/agent_control_panel.py --disable 2,5")
        print("  Show status:         python scripts/agent_control_panel.py --status")


if __name__ == "__main__":
    main()
