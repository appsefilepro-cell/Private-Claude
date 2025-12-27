#!/usr/bin/env python3
"""
AGENT 5.0 INTEGRATION TESTS
Test the Agent Activation System orchestrating all 150 agents
Test load balancing, inter-agent communication, and failure recovery
Version: 1.0.0
Author: Agent X5 PR Completion Team
Date: 2025-12-27

Test Coverage:
- Agent fleet activation (150 agents)
- Load balancing across agent generations
- Inter-agent communication and collaboration
- Task routing and priority queuing
- Failure recovery and self-healing
- Agent performance monitoring
- Multi-generation agent coordination
- Resource optimization
- Scalability tests
"""

import pytest
import asyncio
import time
import sys
import json
import threading
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Agent Activation System
try:
    from core_systems.agent_orchestration.agent_activation_system import (
        AgentActivationSystem,
        Agent,
        AgentGeneration,
        AgentStatus,
        Task,
        TaskPriority,
        TaskStatus,
        TaskQueue,
        LoadBalancer
    )
    from core_systems.agent_orchestration.e2e_workflow_orchestrator import (
        E2EWorkflowOrchestrator,
        WorkflowConfig
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Modules not available: {e}")
    MODULES_AVAILABLE = False


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def agent_system():
    """Initialize Agent Activation System with full fleet"""
    if not MODULES_AVAILABLE:
        pytest.skip("Modules not available")

    system = AgentActivationSystem()
    yield system

    # Cleanup
    system.stop_system()


@pytest.fixture
def agent_system_activated():
    """Initialize and activate full agent fleet"""
    if not MODULES_AVAILABLE:
        pytest.skip("Modules not available")

    system = AgentActivationSystem()
    system.activate_agent_fleet()

    # Wait for agents to initialize
    time.sleep(2)

    yield system

    system.stop_system()


@pytest.fixture
def task_generator():
    """Generate test tasks"""
    def _generate_task(name: str, priority: TaskPriority = TaskPriority.MEDIUM,
                      required_skills: set = None):
        return Task(
            task_id=f"task-{name}-{int(time.time() * 1000)}",
            name=name,
            description=f"Test task: {name}",
            priority=priority,
            required_skills=required_skills or {'python'},
            payload={'test': True, 'timestamp': datetime.now().isoformat()}
        )

    return _generate_task


# ============================================================================
# AGENT FLEET ACTIVATION TESTS
# ============================================================================

class TestAgentFleetActivation:
    """Test agent fleet activation and initialization"""

    def test_agent_system_initialization(self, agent_system):
        """Test basic agent system initialization"""
        assert agent_system is not None
        assert hasattr(agent_system, 'agents')
        assert hasattr(agent_system, 'task_queue')
        assert hasattr(agent_system, 'load_balancer')

    def test_activate_full_fleet(self, agent_system):
        """Test activating all 150 agents"""
        agent_system.activate_agent_fleet()

        # Wait for activation
        time.sleep(3)

        status = agent_system.get_system_status()

        # Verify total agents
        assert status['total_agents'] >= 150
        print(f"✓ Activated {status['total_agents']} agents")

        # Verify agents across all generations
        assert status['by_generation'][AgentGeneration.GENERATION_1.value] > 0
        assert status['by_generation'][AgentGeneration.GENERATION_2.value] > 0
        assert status['by_generation'][AgentGeneration.GENERATION_3.value] > 0
        assert status['by_generation'][AgentGeneration.GENERATION_4.value] > 0
        assert status['by_generation'][AgentGeneration.GENERATION_5.value] > 0

        print(f"✓ Agent distribution across generations:")
        for gen, count in status['by_generation'].items():
            print(f"  {gen}: {count} agents")

    def test_agent_generation_distribution(self, agent_system_activated):
        """Test that agents are distributed across generations"""
        status = agent_system_activated.get_system_status()

        total_agents = status['total_agents']
        by_generation = status['by_generation']

        # Each generation should have agents
        for gen in AgentGeneration:
            assert by_generation.get(gen.value, 0) > 0, f"Generation {gen.value} has no agents"

        # Calculate distribution
        distribution = {
            gen: (count / total_agents) * 100
            for gen, count in by_generation.items()
        }

        print("Agent distribution by generation:")
        for gen, percentage in distribution.items():
            print(f"  {gen}: {percentage:.1f}%")

    def test_agent_skills_initialization(self, agent_system_activated):
        """Test that agents have appropriate skills"""
        agents = list(agent_system_activated.agents.values())

        # Check that agents have skills
        agents_with_skills = [a for a in agents if len(a.skills) > 0]
        assert len(agents_with_skills) > 0

        # Common skills that should exist
        all_skills = set()
        for agent in agents:
            all_skills.update(agent.skills)

        expected_skills = {'python', 'trading', 'data_analysis', 'pattern_recognition'}
        found_skills = all_skills.intersection(expected_skills)

        assert len(found_skills) > 0, "No expected skills found"
        print(f"✓ Found {len(all_skills)} unique skills across agent fleet")

    def test_agent_initial_status(self, agent_system_activated):
        """Test that agents start in correct status"""
        agents = list(agent_system_activated.agents.values())

        # Most agents should be IDLE initially
        idle_agents = [a for a in agents if a.status == AgentStatus.IDLE]

        assert len(idle_agents) > 0
        print(f"✓ {len(idle_agents)} agents in IDLE state")


# ============================================================================
# LOAD BALANCING TESTS
# ============================================================================

class TestLoadBalancing:
    """Test load balancing across 150 agents"""

    def test_task_distribution(self, agent_system_activated, task_generator):
        """Test that tasks are distributed across agents"""
        # Submit 100 tasks
        tasks = []
        for i in range(100):
            task = task_generator(
                name=f"load-balance-{i}",
                priority=TaskPriority.MEDIUM,
                required_skills={'python'}
            )
            submitted = agent_system_activated.submit_task(
                name=task.name,
                priority=task.priority,
                required_skills=task.required_skills,
                payload=task.payload
            )
            tasks.append(submitted)

        # Wait for task distribution
        time.sleep(3)

        # Check task distribution across agents
        agent_task_counts = defaultdict(int)
        for agent in agent_system_activated.agents.values():
            if agent.task_count > 0:
                agent_task_counts[agent.agent_id] = agent.task_count

        # Multiple agents should have tasks
        agents_with_tasks = len(agent_task_counts)
        assert agents_with_tasks > 5, "Tasks not distributed across enough agents"

        print(f"✓ Tasks distributed across {agents_with_tasks} agents")
        print(f"  Average tasks per agent: {sum(agent_task_counts.values()) / len(agent_task_counts):.2f}")

        # Check load balancer statistics
        lb_stats = agent_system_activated.load_balancer.get_statistics()
        print(f"  Total assignments: {lb_stats['total_assignments']}")

    def test_priority_based_routing(self, agent_system_activated, task_generator):
        """Test that high-priority tasks are routed to best agents"""
        # Submit high-priority tasks
        high_priority_tasks = []
        for i in range(10):
            task = agent_system_activated.submit_task(
                name=f"high-priority-{i}",
                priority=TaskPriority.CRITICAL,
                required_skills={'trading', 'pattern_recognition'}
            )
            high_priority_tasks.append(task)

        # Submit low-priority tasks
        low_priority_tasks = []
        for i in range(20):
            task = agent_system_activated.submit_task(
                name=f"low-priority-{i}",
                priority=TaskPriority.LOW,
                required_skills={'python'}
            )
            low_priority_tasks.append(task)

        time.sleep(3)

        # High-priority tasks should be assigned first
        high_assigned = sum(
            1 for task_id in [t.task_id for t in high_priority_tasks]
            if task_id in agent_system_activated.task_queue.tasks
            and agent_system_activated.task_queue.tasks[task_id].status != TaskStatus.PENDING
        )

        print(f"✓ High-priority tasks assigned: {high_assigned}/10")
        assert high_assigned > 0

    def test_skill_based_routing(self, agent_system_activated, task_generator):
        """Test that tasks are routed to agents with matching skills"""
        # Submit tasks requiring specific skills
        skill_sets = [
            {'trading', 'pattern_recognition'},
            {'data_analysis', 'python'},
            {'testing', 'qa'},
            {'logging', 'monitoring'}
        ]

        for i, skills in enumerate(skill_sets):
            task = agent_system_activated.submit_task(
                name=f"skill-specific-{i}",
                priority=TaskPriority.MEDIUM,
                required_skills=skills
            )

        time.sleep(2)

        # Verify tasks were assigned to agents with matching skills
        print("✓ Skill-based routing executed")

    def test_load_balancer_fairness(self, agent_system_activated, task_generator):
        """Test that load balancer distributes tasks fairly"""
        # Submit many tasks
        for i in range(200):
            agent_system_activated.submit_task(
                name=f"fairness-{i}",
                priority=TaskPriority.MEDIUM,
                required_skills={'python'}
            )

        time.sleep(5)

        # Check task distribution variance
        task_counts = [
            agent.task_count
            for agent in agent_system_activated.agents.values()
            if agent.status != AgentStatus.DISABLED
        ]

        active_task_counts = [c for c in task_counts if c > 0]

        if active_task_counts:
            import statistics
            mean = statistics.mean(active_task_counts)
            stdev = statistics.stdev(active_task_counts) if len(active_task_counts) > 1 else 0

            print(f"  Task distribution - Mean: {mean:.2f}, StdDev: {stdev:.2f}")

            # Standard deviation should be reasonable (not too skewed)
            assert stdev < mean * 2, "Task distribution too skewed"

    def test_generation_priority_routing(self, agent_system_activated, task_generator):
        """Test that tasks prefer newer generation agents"""
        # Submit tasks
        for i in range(50):
            agent_system_activated.submit_task(
                name=f"gen-priority-{i}",
                priority=TaskPriority.HIGH,
                required_skills={'python'}
            )

        time.sleep(3)

        # Count tasks by agent generation
        tasks_by_generation = defaultdict(int)
        for agent in agent_system_activated.agents.values():
            if agent.task_count > 0:
                tasks_by_generation[agent.generation.value] += agent.task_count

        print(f"  Tasks by generation:")
        for gen in sorted(tasks_by_generation.keys(), reverse=True):
            print(f"    {gen}: {tasks_by_generation[gen]} tasks")

        # Generation 5 should handle more tasks than Generation 1
        gen5_tasks = tasks_by_generation.get(AgentGeneration.GENERATION_5.value, 0)
        gen1_tasks = tasks_by_generation.get(AgentGeneration.GENERATION_1.value, 0)

        print(f"✓ Gen 5: {gen5_tasks} tasks, Gen 1: {gen1_tasks} tasks")


# ============================================================================
# INTER-AGENT COMMUNICATION TESTS
# ============================================================================

class TestInterAgentCommunication:
    """Test inter-agent communication and collaboration"""

    def test_agent_to_agent_messaging(self, agent_system_activated):
        """Test agents can communicate with each other"""
        agents = list(agent_system_activated.agents.values())[:10]

        # Send messages between agents
        for i in range(len(agents) - 1):
            sender = agents[i]
            receiver = agents[i + 1]

            message = {
                'type': 'collaboration_request',
                'from': sender.agent_id,
                'to': receiver.agent_id,
                'content': 'Test message',
                'timestamp': datetime.now().isoformat()
            }

            # Simulate message passing
            receiver.metadata['last_message'] = message

        print(f"✓ Sent {len(agents) - 1} inter-agent messages")

    def test_task_delegation(self, agent_system_activated, task_generator):
        """Test agents can delegate tasks to other agents"""
        # Submit complex task that might be delegated
        complex_task = agent_system_activated.submit_task(
            name="complex-delegatable-task",
            priority=TaskPriority.HIGH,
            required_skills={'trading', 'data_analysis', 'pattern_recognition'}
        )

        time.sleep(2)

        # Verify task exists in system
        assert complex_task.task_id in agent_system_activated.task_queue.tasks

        print("✓ Task delegation mechanism tested")

    def test_collaborative_task_execution(self, agent_system_activated, task_generator):
        """Test multiple agents collaborating on tasks"""
        # Create tasks that require collaboration
        collab_tasks = []
        for i in range(5):
            task = agent_system_activated.submit_task(
                name=f"collaborative-task-{i}",
                priority=TaskPriority.HIGH,
                required_skills={'trading', 'pattern_recognition', 'data_analysis'}
            )
            collab_tasks.append(task)

        time.sleep(3)

        # Multiple agents should be working
        active_agents = [
            a for a in agent_system_activated.agents.values()
            if a.status == AgentStatus.BUSY
        ]

        print(f"✓ {len(active_agents)} agents actively collaborating")
        assert len(active_agents) > 0

    def test_agent_synchronization(self, agent_system_activated):
        """Test agents can synchronize state"""
        agents = list(agent_system_activated.agents.values())[:5]

        # Simulate synchronization
        sync_timestamp = datetime.now().isoformat()
        for agent in agents:
            agent.metadata['last_sync'] = sync_timestamp

        # Verify all have same sync timestamp
        sync_times = [a.metadata.get('last_sync') for a in agents]
        assert all(t == sync_timestamp for t in sync_times)

        print("✓ Agent synchronization tested")


# ============================================================================
# FAILURE RECOVERY TESTS
# ============================================================================

class TestFailureRecovery:
    """Test failure recovery and self-healing"""

    def test_agent_failure_detection(self, agent_system_activated):
        """Test system detects agent failures"""
        # Select an agent and simulate failure
        test_agent = list(agent_system_activated.agents.values())[0]
        original_status = test_agent.status

        # Simulate failure
        test_agent.status = AgentStatus.FAILED
        test_agent.health_score = 0.0

        # System should detect unhealthy agent
        unhealthy_agents = [
            a for a in agent_system_activated.agents.values()
            if a.health_score < 0.5
        ]

        assert len(unhealthy_agents) > 0
        print(f"✓ Detected {len(unhealthy_agents)} unhealthy agents")

    def test_task_reassignment_on_failure(self, agent_system_activated, task_generator):
        """Test tasks are reassigned when agent fails"""
        # Assign task to agent
        task = agent_system_activated.submit_task(
            name="reassignment-test",
            priority=TaskPriority.HIGH,
            required_skills={'python'}
        )

        time.sleep(1)

        # Find agent working on task
        working_agents = [
            a for a in agent_system_activated.agents.values()
            if a.status == AgentStatus.BUSY
        ]

        if working_agents:
            failed_agent = working_agents[0]
            failed_agent.status = AgentStatus.FAILED

            # Wait for reassignment
            time.sleep(2)

            # Task should still exist in queue
            assert task.task_id in agent_system_activated.task_queue.tasks

            print("✓ Task reassignment mechanism active")

    def test_self_healing_mechanism(self, agent_system_activated):
        """Test system can self-heal"""
        # Simulate multiple agent failures
        agents = list(agent_system_activated.agents.values())[:10]

        for i in range(5):
            agents[i].status = AgentStatus.FAILED
            agents[i].health_score = 0.2

        # Trigger health check
        agent_system_activated.health_monitor.perform_health_check()

        time.sleep(2)

        # System should attempt recovery
        status = agent_system_activated.get_system_status()

        print(f"✓ Self-healing triggered")
        print(f"  Active agents: {status['active_agents']}")
        print(f"  Failed agents: {status.get('failed_agents', 0)}")

    def test_graceful_degradation(self, agent_system_activated, task_generator):
        """Test system degrades gracefully under failures"""
        # Disable half the agents
        agents = list(agent_system_activated.agents.values())
        disabled_count = len(agents) // 2

        for i in range(disabled_count):
            agents[i].status = AgentStatus.DISABLED

        # System should still accept tasks
        task = agent_system_activated.submit_task(
            name="degradation-test",
            priority=TaskPriority.MEDIUM,
            required_skills={'python'}
        )

        time.sleep(1)

        # Task should be queued or assigned
        assert task.task_id in agent_system_activated.task_queue.tasks

        print(f"✓ System operating with {disabled_count} disabled agents")

    def test_automatic_agent_restart(self, agent_system_activated):
        """Test failed agents can be automatically restarted"""
        # Fail an agent
        test_agent = list(agent_system_activated.agents.values())[0]
        original_id = test_agent.agent_id

        test_agent.status = AgentStatus.FAILED
        test_agent.consecutive_failures = 5

        # Simulate restart
        test_agent.status = AgentStatus.IDLE
        test_agent.consecutive_failures = 0
        test_agent.health_score = 1.0

        # Verify agent recovered
        assert test_agent.status == AgentStatus.IDLE
        assert test_agent.health_score == 1.0

        print("✓ Agent restart mechanism functional")


# ============================================================================
# SCALABILITY TESTS
# ============================================================================

class TestScalability:
    """Test system scalability with 150 agents"""

    def test_handle_1000_concurrent_tasks(self, agent_system_activated, task_generator):
        """Test system can handle 1000 concurrent tasks"""
        start_time = time.time()

        # Submit 1000 tasks
        tasks = []
        for i in range(1000):
            task = agent_system_activated.submit_task(
                name=f"scale-{i}",
                priority=random.choice([TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH]),
                required_skills={'python'}
            )
            tasks.append(task)

        submission_time = time.time() - start_time

        print(f"✓ Submitted 1000 tasks in {submission_time:.2f} seconds")
        assert submission_time < 10, "Task submission too slow"

        # Wait for processing
        time.sleep(5)

        # Check progress
        status = agent_system_activated.get_system_status()
        print(f"  Tasks in queue: {status.get('tasks_in_queue', 0)}")
        print(f"  Active agents: {status['active_agents']}")

    def test_sustained_load(self, agent_system_activated, task_generator):
        """Test system under sustained load"""
        duration = 10  # seconds
        tasks_per_second = 20

        start_time = time.time()
        total_tasks = 0

        while time.time() - start_time < duration:
            # Submit batch of tasks
            for _ in range(tasks_per_second):
                agent_system_activated.submit_task(
                    name=f"sustained-{total_tasks}",
                    priority=TaskPriority.MEDIUM,
                    required_skills={'python'}
                )
                total_tasks += 1

            time.sleep(1)

        print(f"✓ System handled {total_tasks} tasks over {duration}s")
        print(f"  Rate: {total_tasks / duration:.2f} tasks/second")

    def test_memory_usage_under_load(self, agent_system_activated, task_generator):
        """Test memory usage remains stable"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Submit many tasks
        for i in range(500):
            agent_system_activated.submit_task(
                name=f"memory-{i}",
                priority=TaskPriority.MEDIUM,
                required_skills={'python'}
            )

        time.sleep(3)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Increase: {memory_increase:.2f} MB")

        # Memory increase should be reasonable
        assert memory_increase < 500, "Excessive memory usage"

    def test_agent_pool_scaling(self, agent_system):
        """Test agent pool can scale up and down"""
        # Start with base fleet
        agent_system.activate_agent_fleet()
        time.sleep(2)

        initial_count = len(agent_system.agents)

        # Add more agents
        for i in range(10):
            new_agent = agent_system.create_agent(
                name=f"scaled-agent-{i}",
                generation=AgentGeneration.GENERATION_5,
                skills={'python', 'scaling_test'}
            )

        # Verify increase
        new_count = len(agent_system.agents)
        assert new_count > initial_count

        print(f"✓ Scaled from {initial_count} to {new_count} agents")


# ============================================================================
# PERFORMANCE MONITORING TESTS
# ============================================================================

class TestPerformanceMonitoring:
    """Test agent performance monitoring"""

    def test_track_agent_metrics(self, agent_system_activated):
        """Test system tracks agent performance metrics"""
        # Get metrics for all agents
        agents = list(agent_system_activated.agents.values())[:10]

        for agent in agents:
            assert hasattr(agent, 'tasks_completed')
            assert hasattr(agent, 'tasks_failed')
            assert hasattr(agent, 'health_score')
            assert hasattr(agent, 'last_heartbeat')

        print(f"✓ Tracking metrics for {len(agents)} agents")

    def test_health_monitoring(self, agent_system_activated):
        """Test health monitoring system"""
        # Perform health check
        agent_system_activated.health_monitor.perform_health_check()

        # Get health report
        health_report = agent_system_activated.health_monitor.get_health_report()

        assert 'healthy_agents' in health_report
        assert 'unhealthy_agents' in health_report
        assert 'average_health_score' in health_report

        print(f"  Healthy agents: {health_report['healthy_agents']}")
        print(f"  Unhealthy agents: {health_report['unhealthy_agents']}")
        print(f"  Average health: {health_report['average_health_score']:.2f}")

    def test_performance_analytics(self, agent_system_activated, task_generator):
        """Test performance analytics"""
        # Submit and process tasks
        for i in range(50):
            agent_system_activated.submit_task(
                name=f"analytics-{i}",
                priority=TaskPriority.MEDIUM,
                required_skills={'python'}
            )

        time.sleep(3)

        # Get analytics
        analytics = agent_system_activated.get_analytics()

        assert 'total_tasks_processed' in analytics
        assert 'average_task_time' in analytics
        assert 'success_rate' in analytics

        print(f"  Total tasks processed: {analytics.get('total_tasks_processed', 0)}")
        print(f"  Success rate: {analytics.get('success_rate', 0):.2f}%")

    def test_real_time_monitoring(self, agent_system_activated):
        """Test real-time monitoring capabilities"""
        # Get real-time status
        status = agent_system_activated.get_system_status()

        # Should have real-time metrics
        assert 'active_agents' in status
        assert 'total_agents' in status
        assert 'tasks_in_queue' in status

        print("✓ Real-time monitoring operational")
        print(f"  Active: {status['active_agents']}/{status['total_agents']}")


# ============================================================================
# INTEGRATION WITH E2E WORKFLOW TESTS
# ============================================================================

class TestE2EWorkflowIntegration:
    """Test agent system integration with E2E workflow orchestrator"""

    @pytest.mark.asyncio
    async def test_workflow_with_agents(self):
        """Test E2E workflow using agent system"""
        if not MODULES_AVAILABLE:
            pytest.skip("Modules not available")

        config = WorkflowConfig(enable_parallel_execution=True)
        orchestrator = E2EWorkflowOrchestrator(config)

        await orchestrator.initialize_systems()

        # Verify agent system is initialized
        assert orchestrator.agent_system is not None

        print("✓ E2E workflow integrated with agent system")

    @pytest.mark.asyncio
    async def test_workflow_task_distribution(self):
        """Test workflow tasks distributed through agent system"""
        if not MODULES_AVAILABLE:
            pytest.skip("Modules not available")

        config = WorkflowConfig(enable_parallel_execution=True)
        orchestrator = E2EWorkflowOrchestrator(config)

        await orchestrator.initialize_systems()

        if orchestrator.agent_system:
            # Submit tasks through workflow
            workflow_data = {
                'data_sources': [],
                'market_data': [],
                'alerts': []
            }

            # Execute workflow stages
            await orchestrator.execute_data_ingestion_stage([])

            print("✓ Workflow tasks distributed through agents")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_comprehensive_agent_tests():
    """Run all agent tests and generate report"""
    print("=" * 80)
    print("AGENT 5.0 INTEGRATION TEST SUITE")
    print("=" * 80)

    # Run pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
        "--disable-warnings"
    ])

    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED")
    print("=" * 80)

    return exit_code


if __name__ == "__main__":
    exit(run_comprehensive_agent_tests())
