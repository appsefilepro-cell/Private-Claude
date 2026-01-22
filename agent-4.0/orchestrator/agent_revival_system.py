#!/usr/bin/env python3
"""
AGENT 4.0 - AGENT REVIVAL SYSTEM
Activates all 50 agents and assigns tasks from queue

This system:
1. Loads all 50 agents from multi_agent_system.py
2. Activates agents based on skill level
3. Assigns tasks from task queue
4. Monitors agent status (idle → working → completed)
5. Handles errors and retry logic
6. Updates agent_state.json in real-time
"""

import json
import logging
import os
import queue
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from multi_agent_system import Agent, AgentStatus, MultiAgentSystem, SkillLevel

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AgentRevival")


@dataclass
class Task:
    """Task definition"""

    id: str
    description: str
    category: str
    pillar: str
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    assigned_agent_id: Optional[int] = None
    created_at: str = None
    completed_at: str = None
    error: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class AgentRevivalSystem:
    """
    Agent Revival System - Brings all 50 agents to life

    Manages:
    - Agent activation and deactivation
    - Task queue management
    - Task assignment based on agent capabilities
    - Real-time status monitoring
    - Error handling and retry logic
    - Agent state persistence
    """

    def __init__(self, skill_level: SkillLevel = SkillLevel.EXPERT):
        self.base_path = Path(__file__).parent.parent.parent
        self.multi_agent_system = MultiAgentSystem()
        self.skill_level = skill_level

        # Task management
        self.task_queue = queue.Queue()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []

        # System status
        self.is_running = False
        self.workers: List[threading.Thread] = []

        logger.info("=" * 70)
        logger.info("✨ AGENT REVIVAL SYSTEM INITIALIZING")
        logger.info("=" * 70)
        logger.info(f"   Skill Level: {skill_level.value}")
        logger.info(f"   Total Agents: {len(self.multi_agent_system.agents)}")

    def add_task(self, task: Task) -> bool:
        """Add task to queue"""
        try:
            self.task_queue.put(task)
            logger.info(f"📋 Task added: {task.description} (ID: {task.id})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add task: {e}")
            return False

    def add_tasks_batch(self, tasks: List[Task]) -> int:
        """Add multiple tasks to queue"""
        added = 0
        for task in tasks:
            if self.add_task(task):
                added += 1
        logger.info(f"📦 Added {added}/{len(tasks)} tasks to queue")
        return added

    def select_agent_for_task(self, task: Task) -> Optional[int]:
        """
        Select best agent for task based on category and capabilities

        Uses intelligent matching:
        - Category-based selection
        - Agent availability
        - Skill requirements
        - Load balancing
        """
        category_map = {
            "TRADING": list(range(1, 11)),
            "LEGAL": list(range(11, 21)),
            "FEDERAL": list(range(21, 26)),
            "NONPROFIT": list(range(26, 31)),
            "SYSTEM": list(range(31, 41)),
            "INTEGRATION": list(range(41, 46)),
            "AI_ML": list(range(46, 51)),
        }

        # Get candidate agents for this category
        candidate_ids = category_map.get(task.category, [])

        if not candidate_ids:
            logger.warning(f"⚠️  No agents found for category: {task.category}")
            return None

        # Find idle agents in this category
        for agent_id in candidate_ids:
            agent = self.multi_agent_system.agents.get(agent_id)
            if agent and agent.status == AgentStatus.IDLE:
                return agent_id

        # If no idle agents, return first agent in category (will queue)
        return candidate_ids[0] if candidate_ids else None

    def assign_task_to_agent(self, task: Task, agent_id: int) -> bool:
        """Assign task to specific agent"""
        if agent_id not in self.multi_agent_system.agents:
            logger.error(f"❌ Agent {agent_id} not found")
            return False

        agent = self.multi_agent_system.agents[agent_id]

        # Update agent status
        agent.status = AgentStatus.WORKING
        agent.current_task = task.description

        # Update task status
        task.assigned_agent_id = agent_id
        task.status = "in_progress"
        self.active_tasks[task.id] = task

        logger.info(f"✅ Task '{task.description[:50]}...' assigned to {agent.name}")

        # Save state
        self.save_agent_state()

        return True

    def execute_task(self, task: Task, agent: Agent) -> bool:
        """
        Execute task with agent

        In production, this would:
        - Actually run the task logic
        - Monitor execution
        - Handle timeouts

        For now, simulates execution
        """
        try:
            logger.info(f"🔄 {agent.name} executing: {task.description}")

            # Simulate task execution (in real system, this would be actual
            # work)
            time.sleep(0.1)  # Simulated work

            # Mark as completed
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()

            # Update agent
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.tasks_completed += 1

            # Move to completed
            self.completed_tasks.append(task)
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]

            logger.info(f"✅ {agent.name} completed task: {task.description}")

            # Save state
            self.save_agent_state()

            return True

        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")

            # Handle error
            task.error = str(e)
            task.retry_count += 1

            agent.status = AgentStatus.ERROR
            agent.errors_encountered += 1

            # Retry if possible
            if task.retry_count < task.max_retries:
                task.status = "retry"
                logger.info(
                    f"🔄 Retrying task (attempt {task.retry_count}/{task.max_retries})"
                )
                self.task_queue.put(task)
            else:
                task.status = "failed"
                self.failed_tasks.append(task)
                logger.error(f"❌ Task failed after {task.max_retries} attempts")

            # Reset agent
            agent.status = AgentStatus.IDLE
            agent.current_task = None

            if task.id in self.active_tasks:
                del self.active_tasks[task.id]

            # Save state
            self.save_agent_state()

            return False

    def worker_thread(self):
        """Worker thread that processes tasks from queue"""
        logger.info("🔧 Worker thread started")

        while self.is_running:
            try:
                # Get task from queue (with timeout to allow checking
                # is_running)
                task = self.task_queue.get(timeout=1.0)

                # Select agent
                agent_id = self.select_agent_for_task(task)

                if agent_id is None:
                    logger.warning(
                        f"⚠️  No agent available for task: {task.description}"
                    )
                    self.task_queue.put(task)  # Re-queue
                    time.sleep(1)
                    continue

                # Assign task
                if not self.assign_task_to_agent(task, agent_id):
                    self.task_queue.put(task)  # Re-queue on failure
                    continue

                # Execute task
                agent = self.multi_agent_system.agents[agent_id]
                self.execute_task(task, agent)

                # Mark task as done in queue
                self.task_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Worker thread error: {e}")
                time.sleep(1)

        logger.info("🔧 Worker thread stopped")

    def start(self, num_workers: int = 5):
        """Start the agent revival system with worker threads"""
        if self.is_running:
            logger.warning("⚠️  System already running")
            return

        logger.info("=" * 70)
        logger.info("🚀 STARTING AGENT REVIVAL SYSTEM")
        logger.info("=" * 70)
        logger.info(f"   Workers: {num_workers}")
        logger.info(f"   Agents: {len(self.multi_agent_system.agents)}")

        self.is_running = True

        # Start worker threads
        for i in range(num_workers):
            worker = threading.Thread(target=self.worker_thread, daemon=True)
            worker.start()
            self.workers.append(worker)
            logger.info(f"   Worker {i+1}/{num_workers} started")

        logger.info("✅ Agent Revival System is now OPERATIONAL")
        logger.info("   All agents standing by for task assignment")

    def stop(self):
        """Stop the agent revival system"""
        logger.info("🛑 Stopping Agent Revival System...")

        self.is_running = False

        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5.0)

        self.workers.clear()

        # Save final state
        self.save_agent_state()

        logger.info("✅ Agent Revival System stopped")

    def save_agent_state(self):
        """Save current agent state to JSON file"""
        try:
            state_path = self.base_path / "agent-4.0" / "state" / "agent_state.json"
            state_path.parent.mkdir(parents=True, exist_ok=True)

            # Get status report from multi-agent system
            state = self.multi_agent_system.get_status_report()

            # Add revival system stats
            state["revival_system"] = {
                "is_running": self.is_running,
                "tasks_in_queue": self.task_queue.qsize(),
                "active_tasks": len(self.active_tasks),
                "completed_tasks": len(self.completed_tasks),
                "failed_tasks": len(self.failed_tasks),
                "worker_threads": len(self.workers),
            }

            with open(state_path, "w") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            logger.error(f"❌ Failed to save agent state: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_status = self.multi_agent_system.get_status_report()

        return {
            "timestamp": datetime.now().isoformat(),
            "is_running": self.is_running,
            "skill_level": self.skill_level.value,
            "agents": {
                "total": agent_status["total_agents"],
                "idle": agent_status["idle"],
                "working": agent_status["working"],
                "tasks_completed": agent_status["total_tasks_completed"],
                "errors": agent_status["total_errors"],
            },
            "tasks": {
                "in_queue": self.task_queue.qsize(),
                "active": len(self.active_tasks),
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks),
            },
            "workers": len(self.workers),
        }

    def print_status(self):
        """Print formatted status report"""
        status = self.get_status()

        print("\n" + "=" * 70)
        print("📊 AGENT REVIVAL SYSTEM STATUS")
        print("=" * 70)
        print(f"Status: {'🟢 RUNNING' if status['is_running'] else '🔴 STOPPED'}")
        print(f"Time: {status['timestamp']}")
        print()
        print(f"AGENTS:")
        print(f"  Total: {status['agents']['total']}")
        print(f"  Idle: {status['agents']['idle']}")
        print(f"  Working: {status['agents']['working']}")
        print(f"  Tasks Completed: {status['agents']['tasks_completed']}")
        print(f"  Errors: {status['agents']['errors']}")
        print()
        print(f"TASKS:")
        print(f"  In Queue: {status['tasks']['in_queue']}")
        print(f"  Active: {status['tasks']['active']}")
        print(f"  Completed: {status['tasks']['completed']}")
        print(f"  Failed: {status['tasks']['failed']}")
        print()
        print(f"WORKERS: {status['workers']}")
        print("=" * 70)


def create_demo_tasks() -> List[Task]:
    """Create demo tasks for testing"""
    tasks = []

    # Trading tasks (Pillar A)
    for i in range(10):
        tasks.append(
            Task(
                id=f"TRADING-{i+1}",
                description=f"Execute paper trading strategy #{i+1}",
                category="TRADING",
                pillar="PILLAR_A",
                priority=1,
            )
        )

    # Legal tasks (Pillar B)
    for i in range(10):
        tasks.append(
            Task(
                id=f"LEGAL-{i+1}",
                description=f"Generate legal document #{i+1}",
                category="LEGAL",
                pillar="PILLAR_B",
                priority=1,
            )
        )

    # Federal tasks (Pillar C)
    for i in range(10):
        tasks.append(
            Task(
                id=f"FEDERAL-{i+1}",
                description=f"Process federal contract opportunity #{i+1}",
                category="FEDERAL",
                pillar="PILLAR_C",
                priority=1,
            )
        )

    # Nonprofit tasks (Pillar D)
    for i in range(10):
        tasks.append(
            Task(
                id=f"NONPROFIT-{i+1}",
                description=f"Manage donor campaign #{i+1}",
                category="NONPROFIT",
                pillar="PILLAR_D",
                priority=1,
            )
        )

    return tasks


def main():
    """Demo of Agent Revival System"""
    print(
        """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                 AGENT REVIVAL SYSTEM                              ║
    ║              Activating All 50 Agents                             ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    )

    # Initialize revival system
    revival = AgentRevivalSystem(skill_level=SkillLevel.EXPERT)

    # Create demo tasks
    demo_tasks = create_demo_tasks()
    logger.info(f"📦 Created {len(demo_tasks)} demo tasks")

    # Add tasks to queue
    revival.add_tasks_batch(demo_tasks)

    # Start system
    revival.start(num_workers=5)

    # Monitor for a bit
    try:
        for _ in range(10):
            time.sleep(2)
            revival.print_status()

        # Wait for all tasks to complete
        revival.task_queue.join()

        # Final status
        revival.print_status()

    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
    finally:
        revival.stop()

    print("\n✅ Demo complete")
    print(f"   Completed: {len(revival.completed_tasks)}")
    print(f"   Failed: {len(revival.failed_tasks)}")


if __name__ == "__main__":
    main()
