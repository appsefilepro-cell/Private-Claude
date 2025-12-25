#!/usr/bin/env python3
"""
Base Agent Class for Agent 5.0 System
Each agent inherits from this base class and implements specific tasks
"""

import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import threading


class BaseAgent:
    """Base class for all AI agents in the system"""

    def __init__(self, agent_id: str, agent_name: str, role: str, master_prompt: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.role = role
        self.master_prompt = master_prompt
        self.base_dir = Path("/home/user/Private-Claude/agent-orchestrator")
        self.log_dir = self.base_dir / "logs"
        self.status_dir = self.base_dir / "status"
        self.comm_dir = self.base_dir / "communication"

        # Ensure directories exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.status_dir.mkdir(parents=True, exist_ok=True)
        self.comm_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Agent state
        self.status = "initialized"
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.start_time = None
        self.last_report_time = None
        self.loop_count = 0
        self.max_loops = 10  # 10x loop protocol

        self.log(f"Agent {self.agent_name} initialized with role: {self.role}")

    def setup_logging(self):
        """Setup logging for this agent"""
        log_file = self.log_dir / f"{self.agent_id}.log"

        # Create logger
        self.logger = logging.getLogger(self.agent_id)
        self.logger.setLevel(logging.INFO)

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def log(self, message: str, level: str = "info"):
        """Log a message"""
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "critical":
            self.logger.critical(message)

    def update_status(self, status: str, details: Dict[str, Any] = None):
        """Update agent status to file system"""
        self.status = status

        status_data = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "role": self.role,
            "status": status,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "loop_count": self.loop_count,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_update": datetime.now().isoformat(),
            "details": details or {}
        }

        status_file = self.status_dir / f"{self.agent_id}.json"
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)

        self.log(f"Status updated: {status}")

    def send_message(self, recipient: str, message: str, message_type: str = "info"):
        """Send message to another agent or system via file system"""
        message_data = {
            "from": self.agent_id,
            "to": recipient,
            "type": message_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        # Create message file
        timestamp = int(time.time() * 1000)
        message_file = self.comm_dir / f"{recipient}_{timestamp}.json"

        with open(message_file, 'w') as f:
            json.dump(message_data, f, indent=2)

        self.log(f"Message sent to {recipient}: {message}")

    def read_messages(self) -> List[Dict[str, Any]]:
        """Read messages addressed to this agent"""
        messages = []

        # Find all message files for this agent
        pattern = f"{self.agent_id}_*.json"
        for msg_file in self.comm_dir.glob(pattern):
            try:
                with open(msg_file, 'r') as f:
                    message = json.load(f)
                messages.append(message)
                # Delete message after reading
                msg_file.unlink()
            except Exception as e:
                self.log(f"Error reading message {msg_file}: {e}", "error")

        return messages

    def report_status(self):
        """Send status report to CFO and user"""
        report = {
            "agent": self.agent_name,
            "role": self.role,
            "status": self.status,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "loop_count": self.loop_count,
            "uptime": self.get_uptime()
        }

        # Send to CFO
        self.send_message("agent_cfo", json.dumps(report), "status_report")

        # Update last report time
        self.last_report_time = datetime.now()

        self.log(f"Status report sent: {json.dumps(report)}")

    def get_uptime(self) -> str:
        """Get agent uptime"""
        if not self.start_time:
            return "0s"

        uptime = datetime.now() - self.start_time
        return str(uptime)

    def should_report(self) -> bool:
        """Check if it's time to send status report (every 4 hours)"""
        if not self.last_report_time:
            return True

        time_since_report = datetime.now() - self.last_report_time
        return time_since_report.total_seconds() >= (4 * 3600)  # 4 hours

    def execute_task(self, task: Dict[str, Any]) -> bool:
        """
        Execute a specific task - to be overridden by subclasses
        Returns True if task completed successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement execute_task()")

    def get_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of tasks for this agent - to be overridden by subclasses
        Returns list of task dictionaries
        """
        raise NotImplementedError("Subclasses must implement get_tasks()")

    def run_loop(self):
        """Main execution loop - 10x protocol"""
        self.log(f"Starting 10x loop execution for {self.agent_name}")
        self.start_time = datetime.now()
        self.update_status("running")

        try:
            for loop_iteration in range(1, self.max_loops + 1):
                self.loop_count = loop_iteration
                self.log(f"Starting loop iteration {loop_iteration}/{self.max_loops}")

                # Get tasks
                tasks = self.get_tasks()

                # Execute each task
                for task in tasks:
                    task_name = task.get('name', 'unnamed_task')
                    self.log(f"Executing task: {task_name}")

                    try:
                        success = self.execute_task(task)

                        if success:
                            self.tasks_completed += 1
                            self.log(f"Task completed successfully: {task_name}")
                        else:
                            self.tasks_failed += 1
                            self.log(f"Task failed: {task_name}", "warning")

                    except Exception as e:
                        self.tasks_failed += 1
                        self.log(f"Task error {task_name}: {e}\n{traceback.format_exc()}", "error")

                # Check for messages
                messages = self.read_messages()
                if messages:
                    self.log(f"Received {len(messages)} messages")
                    for msg in messages:
                        self.process_message(msg)

                # Send status report if needed
                if self.should_report():
                    self.report_status()

                self.update_status(f"running_loop_{loop_iteration}")

                # Small delay between loops
                time.sleep(1)

            # All loops complete
            self.update_status("completed")
            self.report_status()
            self.log(f"Completed all {self.max_loops} loops. Tasks completed: {self.tasks_completed}, Tasks failed: {self.tasks_failed}")

        except Exception as e:
            self.update_status("error")
            self.log(f"Critical error in run_loop: {e}\n{traceback.format_exc()}", "critical")
            self.report_status()

    def process_message(self, message: Dict[str, Any]):
        """Process incoming message - can be overridden by subclasses"""
        msg_type = message.get('type', 'info')
        msg_content = message.get('message', '')
        sender = message.get('from', 'unknown')

        self.log(f"Message from {sender} ({msg_type}): {msg_content}")

    def run_continuous(self, duration_hours: int = 72):
        """Run continuously for specified duration (default 72 hours)"""
        self.log(f"Starting continuous execution for {duration_hours} hours")
        self.start_time = datetime.now()
        self.update_status("running_continuous")

        end_time = datetime.now().timestamp() + (duration_hours * 3600)

        try:
            while datetime.now().timestamp() < end_time:
                # Get and execute tasks
                tasks = self.get_tasks()

                for task in tasks:
                    task_name = task.get('name', 'unnamed_task')

                    try:
                        success = self.execute_task(task)

                        if success:
                            self.tasks_completed += 1
                        else:
                            self.tasks_failed += 1

                    except Exception as e:
                        self.tasks_failed += 1
                        self.log(f"Task error {task_name}: {e}", "error")

                # Check messages
                messages = self.read_messages()
                for msg in messages:
                    self.process_message(msg)

                # Report status every 4 hours
                if self.should_report():
                    self.report_status()

                # Sleep between task cycles
                time.sleep(60)  # 1 minute between cycles

            self.update_status("completed_continuous")
            self.report_status()

        except Exception as e:
            self.update_status("error")
            self.log(f"Critical error in run_continuous: {e}\n{traceback.format_exc()}", "critical")
            self.report_status()

    def start_background(self, mode: str = "loop"):
        """Start agent in background thread"""
        if mode == "loop":
            thread = threading.Thread(target=self.run_loop, daemon=True)
        else:
            thread = threading.Thread(target=self.run_continuous, daemon=True)

        thread.start()
        self.log(f"Agent started in background mode: {mode}")
        return thread


if __name__ == "__main__":
    print("BaseAgent class - not meant to be run directly")
    print("Create agent subclasses that inherit from BaseAgent")
