"""
Inter-Agent Communication and Coordination System
Enables seamless communication between Agent versions 1.0 - 5.0
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class AgentStatus(Enum):
    """Agent status"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class Message:
    """Inter-agent message"""
    
    def __init__(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        payload: Dict,
        priority: MessagePriority = MessagePriority.NORMAL
    ):
        self.id = f"msg_{int(time.time() * 1000)}"
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.payload = payload
        self.priority = priority
        self.timestamp = datetime.now().isoformat()
        self.delivered = False
        self.response = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type,
            'payload': self.payload,
            'priority': self.priority.value,
            'timestamp': self.timestamp,
            'delivered': self.delivered
        }


class AgentRegistry:
    """Registry of all active agents"""
    
    def __init__(self):
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agent registry with all versions"""
        agent_versions = {
            '1.0': {'name': 'Agent 1.0 - Foundation', 'capabilities': ['basic_trading', 'basic_legal']},
            '2.0': {'name': 'Agent 2.0 - Enhanced Automation', 'capabilities': ['multi_account', '24_7_automation']},
            '2.0_advanced': {'name': 'Agent 2.0 Advanced', 'capabilities': ['multi_asset', 'mt5_integration']},
            '3.0': {'name': 'Agent 3.0 - Quantum Intelligence', 'capabilities': ['quantum_ai', 'probate']},
            '4.0': {'name': 'Agent 4.0 - Multi-Agent Orchestrator', 'capabilities': ['50_agents', 'orchestration']},
            '4.0_advanced': {'name': 'Agent 4.0 Advanced', 'capabilities': ['specialized_roles', 'adaptive_interface']},
            '5.0': {'name': 'Agent X5.0 - Enterprise', 'capabilities': ['219_agents', 'full_orchestration']}
        }
        
        for version, info in agent_versions.items():
            self.register_agent(version, info)
    
    def register_agent(self, agent_id: str, info: Dict):
        """Register an agent"""
        self.agents[agent_id] = {
            'id': agent_id,
            'name': info.get('name', agent_id),
            'capabilities': info.get('capabilities', []),
            'status': AgentStatus.IDLE,
            'last_seen': datetime.now().isoformat(),
            'message_queue': []
        }
        logger.info(f"Registered agent: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent information"""
        return self.agents.get(agent_id)
    
    def update_status(self, agent_id: str, status: AgentStatus):
        """Update agent status"""
        if agent_id in self.agents:
            self.agents[agent_id]['status'] = status
            self.agents[agent_id]['last_seen'] = datetime.now().isoformat()
    
    def find_capable_agent(self, required_capability: str) -> Optional[str]:
        """Find an agent with specific capability"""
        for agent_id, info in self.agents.items():
            if required_capability in info['capabilities']:
                if info['status'] == AgentStatus.IDLE:
                    return agent_id
        return None
    
    def get_all_agents(self) -> Dict:
        """Get all registered agents"""
        return self.agents


class MessageBroker:
    """Message broker for inter-agent communication"""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.message_queue = []
        self.message_history = []
    
    def send_message(self, message: Message) -> bool:
        """Send a message to an agent"""
        recipient = self.registry.get_agent(message.recipient)
        
        if not recipient:
            logger.error(f"Recipient not found: {message.recipient}")
            return False
        
        # Add to queue
        self.message_queue.append(message)
        recipient['message_queue'].append(message)
        
        logger.info(f"Message sent from {message.sender} to {message.recipient}")
        return True
    
    def receive_message(self, agent_id: str) -> Optional[Message]:
        """Receive a message for an agent"""
        agent = self.registry.get_agent(agent_id)
        
        if not agent or not agent['message_queue']:
            return None
        
        # Get highest priority message
        messages = sorted(
            agent['message_queue'],
            key=lambda m: m.priority.value,
            reverse=True
        )
        
        message = messages[0]
        agent['message_queue'].remove(message)
        message.delivered = True
        
        self.message_history.append(message)
        
        logger.info(f"Message delivered to {agent_id}")
        return message
    
    def broadcast_message(self, sender: str, message_type: str, payload: Dict) -> int:
        """Broadcast message to all agents"""
        count = 0
        for agent_id in self.registry.get_all_agents():
            if agent_id != sender:
                message = Message(sender, agent_id, message_type, payload)
                if self.send_message(message):
                    count += 1
        
        logger.info(f"Broadcast message sent to {count} agents")
        return count


class TaskDelegator:
    """Delegate tasks to appropriate agents"""
    
    def __init__(self, registry: AgentRegistry, broker: MessageBroker):
        self.registry = registry
        self.broker = broker
        self.active_tasks = {}
    
    def delegate_task(
        self,
        task_id: str,
        task_type: str,
        task_data: Dict,
        required_capability: Optional[str] = None
    ) -> Dict:
        """Delegate a task to an appropriate agent"""
        
        # Find capable agent
        if required_capability:
            agent_id = self.registry.find_capable_agent(required_capability)
        else:
            # Default to Agent 5.0 for complex tasks
            agent_id = '5.0'
        
        if not agent_id:
            logger.error(f"No agent found for capability: {required_capability}")
            return {
                'success': False,
                'error': 'No capable agent available'
            }
        
        # Update agent status
        self.registry.update_status(agent_id, AgentStatus.BUSY)
        
        # Send task message
        message = Message(
            sender='task_delegator',
            recipient=agent_id,
            message_type='task_assignment',
            payload={
                'task_id': task_id,
                'task_type': task_type,
                'task_data': task_data
            },
            priority=MessagePriority.HIGH
        )
        
        self.broker.send_message(message)
        
        # Track task
        self.active_tasks[task_id] = {
            'task_id': task_id,
            'agent_id': agent_id,
            'status': 'assigned',
            'created': datetime.now().isoformat()
        }
        
        logger.info(f"Task {task_id} delegated to agent {agent_id}")
        
        return {
            'success': True,
            'task_id': task_id,
            'assigned_to': agent_id,
            'agent_name': self.registry.get_agent(agent_id)['name']
        }
    
    def complete_task(self, task_id: str, result: Dict):
        """Mark task as complete"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task['status'] = 'completed'
            task['completed'] = datetime.now().isoformat()
            task['result'] = result
            
            # Update agent status
            agent_id = task['agent_id']
            self.registry.update_status(agent_id, AgentStatus.IDLE)
            
            logger.info(f"Task {task_id} completed by agent {agent_id}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        return self.active_tasks.get(task_id)
    
    def get_active_tasks(self) -> List[Dict]:
        """Get all active tasks"""
        return [
            task for task in self.active_tasks.values()
            if task['status'] != 'completed'
        ]


class AgentCoordinator:
    """Main coordination system for all agents"""
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.broker = MessageBroker(self.registry)
        self.delegator = TaskDelegator(self.registry, self.broker)
        self.running = False
    
    def start(self):
        """Start the coordination system"""
        self.running = True
        logger.info("Agent coordination system started")
    
    def stop(self):
        """Stop the coordination system"""
        self.running = False
        logger.info("Agent coordination system stopped")
    
    def create_workflow(
        self,
        workflow_name: str,
        tasks: List[Dict],
        parallel: bool = False
    ) -> Dict:
        """Create a workflow with multiple tasks"""
        workflow_id = f"workflow_{int(time.time() * 1000)}"
        
        results = []
        
        if parallel:
            # Execute tasks in parallel
            for idx, task in enumerate(tasks):
                task_id = f"{workflow_id}_task_{idx}"
                result = self.delegator.delegate_task(
                    task_id=task_id,
                    task_type=task.get('type'),
                    task_data=task.get('data', {}),
                    required_capability=task.get('capability')
                )
                results.append(result)
        else:
            # Execute tasks sequentially
            for idx, task in enumerate(tasks):
                task_id = f"{workflow_id}_task_{idx}"
                result = self.delegator.delegate_task(
                    task_id=task_id,
                    task_type=task.get('type'),
                    task_data=task.get('data', {}),
                    required_capability=task.get('capability')
                )
                results.append(result)
                
                # Wait for completion if sequential
                # (In real implementation, would use async/await)
                time.sleep(0.1)
        
        return {
            'workflow_id': workflow_id,
            'workflow_name': workflow_name,
            'total_tasks': len(tasks),
            'parallel': parallel,
            'tasks': results
        }
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        agents = self.registry.get_all_agents()
        
        status_counts = {
            'idle': 0,
            'busy': 0,
            'offline': 0,
            'error': 0
        }
        
        for agent in agents.values():
            status_counts[agent['status'].value] += 1
        
        return {
            'running': self.running,
            'total_agents': len(agents),
            'status_breakdown': status_counts,
            'active_tasks': len(self.delegator.get_active_tasks()),
            'message_queue_size': len(self.broker.message_queue)
        }


def main():
    """Example usage"""
    print("=== Agent Coordination System ===\n")
    
    # Initialize coordinator
    coordinator = AgentCoordinator()
    coordinator.start()
    
    # Show system status
    status = coordinator.get_system_status()
    print(f"System Status:")
    print(f"  Total Agents: {status['total_agents']}")
    print(f"  Active Tasks: {status['active_tasks']}")
    print(f"  Status Breakdown: {status['status_breakdown']}\n")
    
    # Create a workflow
    workflow = coordinator.create_workflow(
        workflow_name="Data Processing Pipeline",
        tasks=[
            {
                'type': 'parse_csv',
                'data': {'file': 'data.csv'},
                'capability': 'multi_asset'
            },
            {
                'type': 'analyze',
                'data': {'analysis_type': 'financial'},
                'capability': 'quantum_ai'
            },
            {
                'type': 'generate_report',
                'data': {'format': 'pdf'},
                'capability': 'basic_legal'
            }
        ],
        parallel=False
    )
    
    print(f"✓ Workflow Created: {workflow['workflow_name']}")
    print(f"  Workflow ID: {workflow['workflow_id']}")
    print(f"  Total Tasks: {workflow['total_tasks']}")
    print(f"  Execution Mode: {'Parallel' if workflow['parallel'] else 'Sequential'}\n")
    
    # Show task delegation
    for idx, task in enumerate(workflow['tasks'], 1):
        if task.get('success'):
            print(f"  Task {idx}: Assigned to {task['agent_name']}")
    
    print("\n✓ Agent coordination system demonstration complete!")


if __name__ == '__main__':
    main()
