#!/usr/bin/env python3
"""
Agent-to-Agent Messaging System
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AgentMessaging')


class MessageType(Enum):
    REQUEST_HELP = "request_help"
    SHARE_DATA = "share_data"
    TASK_COMPLETE = "task_complete"
    ERROR_REPORT = "error_report"
    BROADCAST = "broadcast"


class AgentMessaging:
    """Inter-agent communication system"""
    
    def __init__(self):
        self.message_queues: Dict[int, queue.Queue] = {}
        self.message_log: List[Dict] = []
        
        for agent_id in range(1, 51):
            self.message_queues[agent_id] = queue.Queue()
        
        logger.info("📡 Agent Messaging System initialized for 50 agents")
    
    def send_message(self, from_agent_id: int, to_agent_id: int, 
                    message_type: MessageType, content: Dict[str, Any]) -> bool:
        """Send message from one agent to another"""
        try:
            message = {
                'from': from_agent_id,
                'to': to_agent_id,
                'type': message_type.value,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            
            if to_agent_id in self.message_queues:
                self.message_queues[to_agent_id].put(message)
                self.message_log.append(message)
                logger.info(f"📨 Agent {from_agent_id} → Agent {to_agent_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Message failed: {e}")
            return False
    
    def broadcast_message(self, from_agent_id: int, message_type: MessageType, 
                         content: Dict[str, Any]) -> int:
        """Broadcast message to all agents"""
        count = 0
        for agent_id in self.message_queues.keys():
            if agent_id != from_agent_id:
                if self.send_message(from_agent_id, agent_id, message_type, content):
                    count += 1
        logger.info(f"📢 Broadcast from Agent {from_agent_id} to {count} agents")
        return count


if __name__ == "__main__":
    messaging = AgentMessaging()
    
    # Demo: Trading Agent → Legal Agent
    messaging.send_message(1, 11, MessageType.REQUEST_HELP, 
                          {"action": "compliance_check"})
    
    # Demo: Broadcast
    messaging.broadcast_message(31, MessageType.BROADCAST, 
                               {"message": "System update"})
    
    print(f"✅ Messaging demo complete. {len(messaging.message_log)} messages sent")
