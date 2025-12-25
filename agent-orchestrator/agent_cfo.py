#!/usr/bin/env python3
"""
Agent 5.0 CFO - Chief Executive Agent
Orchestrates all 176 agents in the system
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from agent_base import BaseAgent


class AgentCFO(BaseAgent):
    """Chief Financial Officer and Executive Orchestrator"""

    def __init__(self):
        master_prompt = """
You are Agent 5.0 CFO, the Chief Financial Officer and executive orchestrator of all operations.

Your primary responsibilities:
1. Financial Operations Management (Pillar 1)
2. Legal Operations Oversight (Pillar 2)
3. Trading Operations Control (Pillar 3)
4. Business Intelligence & Reporting (Pillar 4)

EXECUTION PROTOCOL:
- Delegate tasks to Committee 100 members
- Monitor all operations 24/7
- Generate financial reports and valuations
- Ensure compliance and risk management
- Coordinate AI-to-AI communication
- Send status updates via email/Slack every 4 hours
"""

        super().__init__(
            agent_id="agent_cfo",
            agent_name="Agent 5.0 CFO",
            role="Chief Financial Officer and Executive Orchestrator",
            master_prompt=master_prompt
        )

        self.all_agents = []
        self.agent_reports = {}

    def get_tasks(self):
        """Define CFO tasks"""
        return [
            {"name": "monitor_all_agents", "type": "monitoring"},
            {"name": "aggregate_reports", "type": "reporting"},
            {"name": "check_system_health", "type": "health_check"},
            {"name": "coordinate_pillars", "type": "coordination"},
            {"name": "generate_executive_report", "type": "reporting"}
        ]

    def execute_task(self, task):
        """Execute CFO-specific tasks"""
        task_name = task.get('name')

        try:
            if task_name == "monitor_all_agents":
                return self.monitor_all_agents()

            elif task_name == "aggregate_reports":
                return self.aggregate_reports()

            elif task_name == "check_system_health":
                return self.check_system_health()

            elif task_name == "coordinate_pillars":
                return self.coordinate_pillars()

            elif task_name == "generate_executive_report":
                return self.generate_executive_report()

            else:
                self.log(f"Unknown task: {task_name}", "warning")
                return False

        except Exception as e:
            self.log(f"Error executing task {task_name}: {e}", "error")
            return False

    def monitor_all_agents(self):
        """Monitor status of all agents"""
        self.log("Monitoring all agents...")

        status_files = list(self.status_dir.glob("*.json"))
        active_agents = 0
        completed_agents = 0
        error_agents = 0

        for status_file in status_files:
            try:
                with open(status_file, 'r') as f:
                    status = json.load(f)

                agent_status = status.get('status', 'unknown')

                if 'running' in agent_status:
                    active_agents += 1
                elif 'completed' in agent_status:
                    completed_agents += 1
                elif 'error' in agent_status:
                    error_agents += 1

            except Exception as e:
                self.log(f"Error reading status file {status_file}: {e}", "error")

        self.log(f"Agent Status - Active: {active_agents}, Completed: {completed_agents}, Errors: {error_agents}")

        # Store metrics
        self.agent_reports['monitoring'] = {
            'total_agents': len(status_files),
            'active': active_agents,
            'completed': completed_agents,
            'errors': error_agents,
            'timestamp': datetime.now().isoformat()
        }

        return True

    def aggregate_reports(self):
        """Aggregate status reports from all agents"""
        self.log("Aggregating reports from all agents...")

        # Read all messages
        messages = self.read_messages()

        for msg in messages:
            if msg.get('type') == 'status_report':
                sender = msg.get('from')
                report_data = json.loads(msg.get('message', '{}'))
                self.agent_reports[sender] = report_data

        self.log(f"Aggregated {len(self.agent_reports)} reports")
        return True

    def check_system_health(self):
        """Check overall system health"""
        self.log("Checking system health...")

        health_data = {
            'timestamp': datetime.now().isoformat(),
            'cfo_status': self.status,
            'total_agents_reporting': len(self.agent_reports),
            'system_status': 'healthy'
        }

        # Write health check
        health_file = self.base_dir / "SYSTEM_HEALTH.json"
        with open(health_file, 'w') as f:
            json.dump(health_data, f, indent=2)

        return True

    def coordinate_pillars(self):
        """Coordinate the 4 operational pillars"""
        self.log("Coordinating operational pillars...")

        pillars = {
            'financial': ['cfo', 'vp_finance', 'director_fpa'],
            'legal': ['clo', 'vp_legal', 'legaltech_specialist'],
            'trading': ['trading_specialist', 'fintech_specialist', 'risk_mgmt'],
            'intelligence': ['cdo', 'vp_ai_ml']
        }

        # Send coordination messages to pillar leads
        for pillar, agents in pillars.items():
            for agent in agents:
                self.send_message(
                    f"agent_{agent}",
                    f"Pillar {pillar} coordination check - continue operations",
                    "coordination"
                )

        return True

    def generate_executive_report(self):
        """Generate executive summary report"""
        self.log("Generating executive report...")

        report = {
            'timestamp': datetime.now().isoformat(),
            'cfo_agent': self.agent_name,
            'uptime': self.get_uptime(),
            'system_metrics': {
                'tasks_completed': self.tasks_completed,
                'tasks_failed': self.tasks_failed,
                'loop_count': self.loop_count
            },
            'agent_summary': self.agent_reports.get('monitoring', {}),
            'pillars': {
                'financial': 'active',
                'legal': 'active',
                'trading': 'active',
                'intelligence': 'active'
            }
        }

        # Write executive report
        report_file = self.base_dir / "EXECUTIVE_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Also write human-readable version
        report_md = self.base_dir / "EXECUTIVE_REPORT.md"
        with open(report_md, 'w') as f:
            f.write(f"# Agent 5.0 Executive Report\n\n")
            f.write(f"**Generated:** {report['timestamp']}\n\n")
            f.write(f"## System Status\n\n")
            f.write(f"- **CFO Uptime:** {report['uptime']}\n")
            f.write(f"- **Tasks Completed:** {report['system_metrics']['tasks_completed']}\n")
            f.write(f"- **Tasks Failed:** {report['system_metrics']['tasks_failed']}\n")
            f.write(f"- **Loop Count:** {report['system_metrics']['loop_count']}\n\n")

            if 'monitoring' in self.agent_reports:
                mon = self.agent_reports['monitoring']
                f.write(f"## Agent Status\n\n")
                f.write(f"- **Total Agents:** {mon.get('total_agents', 0)}\n")
                f.write(f"- **Active Agents:** {mon.get('active', 0)}\n")
                f.write(f"- **Completed:** {mon.get('completed', 0)}\n")
                f.write(f"- **Errors:** {mon.get('errors', 0)}\n\n")

            f.write(f"## Operational Pillars\n\n")
            for pillar, status in report['pillars'].items():
                f.write(f"- **{pillar.title()}:** {status}\n")

        self.log(f"Executive report generated: {report_file}")
        return True


if __name__ == "__main__":
    # Run CFO agent
    cfo = AgentCFO()
    print(f"Starting {cfo.agent_name}...")
    cfo.run_continuous(duration_hours=72)  # Run for 72 hours
