#!/usr/bin/env python3
"""
Master Orchestrator for Agent 5.0 System
Activates and manages all 176 agents
"""

import os
import sys
import json
import time
import signal
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_cfo import AgentCFO
from agent_factory import AgentFactory


class MasterOrchestrator:
    """Master orchestrator for the entire Agent 5.0 system"""

    def __init__(self):
        self.base_dir = Path("/home/user/Private-Claude/agent-orchestrator")
        self.cfo = None
        self.factory = None
        self.agents = []
        self.threads = []
        self.running = False

        print("="*60)
        print("AGENT 5.0 MASTER ORCHESTRATOR")
        print("="*60)

    def initialize_system(self):
        """Initialize the entire agent system"""
        print("\n[1/5] Initializing system directories...")

        # Ensure all directories exist
        (self.base_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "status").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "communication").mkdir(parents=True, exist_ok=True)

        print("   ✓ Directories created")

    def create_cfo(self):
        """Create and initialize CFO agent"""
        print("\n[2/5] Creating Agent 5.0 CFO...")

        self.cfo = AgentCFO()
        print(f"   ✓ CFO initialized: {self.cfo.agent_name}")

    def create_all_agents(self):
        """Create all 176 agents"""
        print("\n[3/5] Creating all 176 agents...")

        self.factory = AgentFactory()
        self.agents = self.factory.create_all_agents()

        print(f"   ✓ Created {len(self.agents)} agents")

        # Print agent summary by pillar
        pillars = {}
        for agent in self.agents:
            pillar = agent.master_prompt.split('in the ')[-1].split(' pillar')[0]
            pillars[pillar] = pillars.get(pillar, 0) + 1

        print("\n   Agent Distribution:")
        for pillar, count in sorted(pillars.items()):
            print(f"     - {pillar.title()}: {count} agents")

    def start_cfo(self):
        """Start CFO agent"""
        print("\n[4/5] Starting Agent 5.0 CFO...")

        # Start CFO in background
        cfo_thread = self.cfo.start_background(mode="continuous")
        self.threads.append(cfo_thread)

        time.sleep(1)  # Give CFO time to initialize

        print(f"   ✓ CFO started in continuous mode (72 hours)")

    def start_all_agents(self):
        """Start all agents"""
        print("\n[5/5] Starting all 176 agents...")

        # Start all agents in loop mode (10x protocol)
        agent_threads = self.factory.start_all_agents(mode="loop")
        self.threads.extend(agent_threads)

        print(f"   ✓ All {len(self.agents)} agents started")

    def display_activation_summary(self):
        """Display activation summary"""
        print("\n" + "="*60)
        print("AGENT 5.0 SYSTEM ACTIVATED")
        print("="*60)
        print(f"\nActivation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nSystem Status:")
        print(f"  • CFO Agent: RUNNING (continuous mode)")
        print(f"  • Total Agents: {len(self.agents)} RUNNING (10x loop mode)")
        print(f"  • Total Threads: {len(self.threads)}")
        print(f"\nOperational Pillars:")
        print(f"  • Financial Operations: ACTIVE")
        print(f"  • Legal Operations: ACTIVE")
        print(f"  • Trading Operations: ACTIVE")
        print(f"  • Business Intelligence: ACTIVE")
        print(f"\nCommunication:")
        print(f"  • File-based messaging: ENABLED")
        print(f"  • Status reporting: Every 4 hours")
        print(f"  • Logs directory: {self.base_dir / 'logs'}")
        print(f"  • Status directory: {self.base_dir / 'status'}")
        print(f"\nExecution Protocol:")
        print(f"  • CFO: Continuous for 72 hours")
        print(f"  • Agents: 10x loop protocol")
        print(f"  • Enhancement mode: ENABLED")
        print(f"  • Auto-reporting: ENABLED")
        print("\n" + "="*60)
        print("\nMonitoring:")
        print(f"  • View executive reports: cat {self.base_dir}/EXECUTIVE_REPORT.md")
        print(f"  • View system health: cat {self.base_dir}/SYSTEM_HEALTH.json")
        print(f"  • View agent logs: ls {self.base_dir}/logs/")
        print(f"  • View agent status: ls {self.base_dir}/status/")
        print("\n" + "="*60)

    def monitor_system(self):
        """Monitor system and keep running"""
        print("\n[MONITORING] System is now running...")
        print("Press Ctrl+C to stop the system\n")

        self.running = True

        try:
            while self.running:
                # Check if threads are alive
                alive_threads = sum(1 for t in self.threads if t.is_alive())

                # Display status every 60 seconds
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Active threads: {alive_threads}/{len(self.threads)}")

                # Check for executive report
                report_file = self.base_dir / "EXECUTIVE_REPORT.md"
                if report_file.exists():
                    mod_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                    print(f"               Last executive report: {mod_time.strftime('%H:%M:%S')}")

                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            print("\n\n[SHUTDOWN] Stopping all agents...")
            self.running = False

    def activate(self):
        """Main activation sequence"""
        try:
            self.initialize_system()
            self.create_cfo()
            self.create_all_agents()
            self.start_cfo()
            self.start_all_agents()
            self.display_activation_summary()
            self.monitor_system()

        except Exception as e:
            print(f"\n[ERROR] Activation failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def status_check(self):
        """Quick status check without starting agents"""
        print("\n" + "="*60)
        print("AGENT 5.0 STATUS CHECK")
        print("="*60)

        # Check for status files
        status_dir = self.base_dir / "status"
        if status_dir.exists():
            status_files = list(status_dir.glob("*.json"))
            print(f"\nActive agents: {len(status_files)}")

            # Categorize by status
            running = 0
            completed = 0
            errors = 0

            for status_file in status_files:
                try:
                    with open(status_file, 'r') as f:
                        data = json.load(f)
                        status = data.get('status', 'unknown')

                        if 'running' in status:
                            running += 1
                        elif 'completed' in status:
                            completed += 1
                        elif 'error' in status:
                            errors += 1
                except:
                    pass

            print(f"  • Running: {running}")
            print(f"  • Completed: {completed}")
            print(f"  • Errors: {errors}")

        # Check for reports
        report_file = self.base_dir / "EXECUTIVE_REPORT.md"
        if report_file.exists():
            mod_time = datetime.fromtimestamp(report_file.stat().st_mtime)
            print(f"\nLast executive report: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Check health
        health_file = self.base_dir / "SYSTEM_HEALTH.json"
        if health_file.exists():
            with open(health_file, 'r') as f:
                health = json.load(f)
                print(f"System health: {health.get('system_status', 'unknown')}")

        print("\n" + "="*60)


def main():
    """Main entry point"""
    orchestrator = MasterOrchestrator()

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        orchestrator.status_check()
    else:
        orchestrator.activate()


if __name__ == "__main__":
    main()
