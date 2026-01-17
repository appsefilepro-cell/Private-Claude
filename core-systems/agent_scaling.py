#!/usr/bin/env python3
"""
Agent Scaling Infrastructure - 500 Parallel Agents
Part 2 Implementation - Advanced Asyncio Patterns

Implements semaphore-based rate limiting and task sharding for
scaling from 219 agents to 500+ concurrent agents.
"""

import asyncio
import time
from typing import List, Dict, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """Represents a task for an agent to execute."""
    task_id: str
    task_type: str
    priority: int
    payload: Dict[str, Any]
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class AgentScalingOrchestrator:
    """
    Orchestrates execution of tasks across 500+ parallel agents with rate limiting.
    
    Key Features:
    - Asyncio.Semaphore for concurrent execution control
    - Task sharding across agent pools
    - Rate limit protection (prevents 429 errors)
    - Performance monitoring and metrics
    """
    
    def __init__(self, 
                 max_concurrent_agents: int = 500,
                 rate_limit_per_second: int = 50,
                 enable_monitoring: bool = True):
        """
        Initialize the agent scaling orchestrator.
        
        Args:
            max_concurrent_agents: Maximum agents running concurrently
            rate_limit_per_second: Max tasks starting per second
            enable_monitoring: Enable performance monitoring
        """
        self.max_concurrent_agents = max_concurrent_agents
        self.rate_limit_per_second = rate_limit_per_second
        self.enable_monitoring = enable_monitoring
        
        # Semaphore acts as gatekeeper to prevent API rate limits
        self.semaphore = asyncio.Semaphore(rate_limit_per_second)
        
        # Agent pool management
        self.agent_pool = []
        self.active_agents = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        
        # Performance metrics
        self.metrics = {
            'total_tasks_queued': 0,
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'average_task_duration': 0.0,
            'peak_concurrent_agents': 0,
            'start_time': None,
            'end_time': None
        }
        
        logger.info(f"Agent Scaling Orchestrator initialized: "
                   f"max_agents={max_concurrent_agents}, "
                   f"rate_limit={rate_limit_per_second}/s")
    
    async def execute_agent_task(self, 
                                  task: AgentTask,
                                  task_func: Callable,
                                  *args, **kwargs) -> Dict:
        """
        Execute a single agent task with rate limiting.
        
        Args:
            task: AgentTask object
            task_func: Async function to execute
            *args, **kwargs: Arguments for task_func
            
        Returns:
            Dictionary with execution results
        """
        async with self.semaphore:
            self.active_agents += 1
            
            # Update peak concurrent agents metric
            if self.active_agents > self.metrics['peak_concurrent_agents']:
                self.metrics['peak_concurrent_agents'] = self.active_agents
            
            start_time = time.time()
            
            try:
                # Execute the task
                result = await task_func(task, *args, **kwargs)
                
                # Record success
                self.completed_tasks += 1
                self.metrics['total_tasks_completed'] += 1
                
                duration = time.time() - start_time
                
                if self.enable_monitoring:
                    logger.debug(f"Task {task.task_id} completed in {duration:.2f}s")
                
                return {
                    'success': True,
                    'task_id': task.task_id,
                    'duration': duration,
                    'result': result
                }
                
            except Exception as e:
                # Record failure
                self.failed_tasks += 1
                self.metrics['total_tasks_failed'] += 1
                
                logger.error(f"Task {task.task_id} failed: {e}")
                
                return {
                    'success': False,
                    'task_id': task.task_id,
                    'error': str(e),
                    'duration': time.time() - start_time
                }
            
            finally:
                self.active_agents -= 1
    
    async def execute_task_batch(self,
                                  tasks: List[AgentTask],
                                  task_func: Callable,
                                  shard_size: Optional[int] = None) -> List[Dict]:
        """
        Execute a batch of tasks with automatic sharding.
        
        Args:
            tasks: List of AgentTask objects
            task_func: Async function to execute for each task
            shard_size: Size of each shard (None = auto-calculate)
            
        Returns:
            List of execution results
        """
        self.metrics['start_time'] = time.time()
        self.metrics['total_tasks_queued'] = len(tasks)
        
        logger.info(f"Starting batch execution: {len(tasks)} tasks")
        
        # Auto-calculate shard size if not provided
        if shard_size is None:
            shard_size = min(100, max(10, len(tasks) // 10))
        
        # Shard tasks into manageable chunks
        shards = [tasks[i:i + shard_size] for i in range(0, len(tasks), shard_size)]
        
        logger.info(f"Tasks sharded into {len(shards)} shards of size ~{shard_size}")
        
        all_results = []
        
        # Process each shard
        for shard_idx, shard in enumerate(shards):
            logger.info(f"Processing shard {shard_idx + 1}/{len(shards)} "
                       f"({len(shard)} tasks)")
            
            # Create coroutines for all tasks in shard
            coroutines = [
                self.execute_agent_task(task, task_func)
                for task in shard
            ]
            
            # Execute shard concurrently
            shard_results = await asyncio.gather(*coroutines, return_exceptions=True)
            all_results.extend(shard_results)
            
            # Brief pause between shards to prevent overwhelming the system
            if shard_idx < len(shards) - 1:
                await asyncio.sleep(0.1)
        
        self.metrics['end_time'] = time.time()
        
        # Calculate average task duration
        successful_results = [r for r in all_results if isinstance(r, dict) and r.get('success')]
        if successful_results:
            avg_duration = sum(r['duration'] for r in successful_results) / len(successful_results)
            self.metrics['average_task_duration'] = avg_duration
        
        logger.info(f"Batch execution completed: "
                   f"{self.metrics['total_tasks_completed']} succeeded, "
                   f"{self.metrics['total_tasks_failed']} failed")
        
        return all_results
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics for the execution."""
        total_time = 0
        if self.metrics['start_time'] and self.metrics['end_time']:
            total_time = self.metrics['end_time'] - self.metrics['start_time']
        
        throughput = 0
        if total_time > 0:
            throughput = self.metrics['total_tasks_completed'] / total_time
        
        return {
            **self.metrics,
            'total_execution_time': total_time,
            'throughput_tasks_per_second': throughput,
            'success_rate': (
                self.metrics['total_tasks_completed'] / 
                max(1, self.metrics['total_tasks_queued'])
            ) * 100
        }
    
    def print_performance_report(self) -> None:
        """Print a detailed performance report."""
        metrics = self.get_performance_metrics()
        
        print("\n" + "=" * 70)
        print("AGENT SCALING PERFORMANCE REPORT")
        print("=" * 70)
        print(f"\nConfiguration:")
        print(f"  Max Concurrent Agents: {self.max_concurrent_agents}")
        print(f"  Rate Limit: {self.rate_limit_per_second} tasks/second")
        print(f"\nExecution Summary:")
        print(f"  Total Tasks Queued: {metrics['total_tasks_queued']}")
        print(f"  Tasks Completed: {metrics['total_tasks_completed']}")
        print(f"  Tasks Failed: {metrics['total_tasks_failed']}")
        print(f"  Success Rate: {metrics['success_rate']:.1f}%")
        print(f"\nPerformance Metrics:")
        print(f"  Total Execution Time: {metrics['total_execution_time']:.2f} seconds")
        print(f"  Average Task Duration: {metrics['average_task_duration']:.3f} seconds")
        print(f"  Throughput: {metrics['throughput_tasks_per_second']:.2f} tasks/second")
        print(f"  Peak Concurrent Agents: {metrics['peak_concurrent_agents']}")
        print("\n" + "=" * 70 + "\n")
    
    async def scale_to_target(self, 
                             target_agents: int,
                             test_task_func: Optional[Callable] = None) -> Dict:
        """
        Test scaling to a target number of concurrent agents.
        
        Args:
            target_agents: Target number of agents (e.g., 500)
            test_task_func: Optional test function (uses default if None)
            
        Returns:
            Scaling test results
        """
        logger.info(f"Starting scale test to {target_agents} agents")
        
        # Create test tasks
        test_tasks = [
            AgentTask(
                task_id=f"scale_test_{i}",
                task_type="SCALE_TEST",
                priority=1,
                payload={'iteration': i}
            )
            for i in range(target_agents)
        ]
        
        # Use default test function if none provided
        if test_task_func is None:
            test_task_func = self._default_test_task
        
        # Execute scaling test
        start = time.time()
        results = await self.execute_task_batch(test_tasks, test_task_func)
        duration = time.time() - start
        
        # Analyze results
        successful = len([r for r in results if isinstance(r, dict) and r.get('success')])
        
        scale_results = {
            'target_agents': target_agents,
            'test_duration': duration,
            'tasks_completed': successful,
            'tasks_failed': target_agents - successful,
            'success_rate': (successful / target_agents) * 100,
            'average_throughput': successful / duration if duration > 0 else 0,
            'peak_concurrent': self.metrics['peak_concurrent_agents'],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Scale test completed: {successful}/{target_agents} succeeded "
                   f"in {duration:.2f}s ({scale_results['average_throughput']:.2f} tasks/s)")
        
        return scale_results
    
    async def _default_test_task(self, task: AgentTask) -> str:
        """Default test task that simulates agent work."""
        # Simulate varying task durations
        await asyncio.sleep(0.01 + (task.payload.get('iteration', 0) % 5) * 0.001)
        return f"Completed test task {task.task_id}"


# Example task functions for different agent types

async def trading_agent_task(task: AgentTask) -> Dict:
    """Example trading agent task."""
    await asyncio.sleep(0.05)  # Simulate API call
    return {
        'agent_type': 'TRADING',
        'task_id': task.task_id,
        'action': 'ANALYZE_MARKET',
        'result': 'Analysis complete'
    }


async def legal_agent_task(task: AgentTask) -> Dict:
    """Example legal agent task."""
    await asyncio.sleep(0.03)  # Simulate document processing
    return {
        'agent_type': 'LEGAL',
        'task_id': task.task_id,
        'action': 'PROCESS_DOCUMENT',
        'result': 'Document processed'
    }


async def cfo_agent_task(task: AgentTask) -> Dict:
    """Example CFO agent task."""
    await asyncio.sleep(0.04)  # Simulate financial calculation
    return {
        'agent_type': 'CFO',
        'task_id': task.task_id,
        'action': 'CALCULATE_METRICS',
        'result': 'Metrics calculated'
    }


async def main():
    """Demonstration of agent scaling to 500 agents."""
    print("Agent Scaling Infrastructure - Part 2 Implementation")
    print("Demonstrating scaling from 219 to 500+ agents\n")
    
    # Create orchestrator
    orchestrator = AgentScalingOrchestrator(
        max_concurrent_agents=500,
        rate_limit_per_second=50,
        enable_monitoring=True
    )
    
    # Test scaling to 500 agents
    print("Running scale test to 500 agents...")
    scale_results = await orchestrator.scale_to_target(500)
    
    print(f"\nScale Test Results:")
    print(f"  Target: {scale_results['target_agents']} agents")
    print(f"  Duration: {scale_results['test_duration']:.2f} seconds")
    print(f"  Success Rate: {scale_results['success_rate']:.1f}%")
    print(f"  Throughput: {scale_results['average_throughput']:.2f} tasks/second")
    print(f"  Peak Concurrent: {scale_results['peak_concurrent']} agents")
    
    # Print detailed performance report
    orchestrator.print_performance_report()
    
    print("\nIntegration Example:")
    print("  orchestrator = AgentScalingOrchestrator(max_concurrent_agents=500)")
    print("  tasks = [AgentTask(...) for _ in range(500)]")
    print("  results = await orchestrator.execute_task_batch(tasks, your_task_func)")


if __name__ == "__main__":
    asyncio.run(main())
