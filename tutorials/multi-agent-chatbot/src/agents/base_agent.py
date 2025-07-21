from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import uuid

class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system"""
    
    def __init__(self, name: str, description: str, capabilities: List[str]):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and return updated state"""
        pass
    
    @abstractmethod
    async def can_handle(self, task: str) -> float:
        """Return confidence score (0-1) for handling this task"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "created_at": self.created_at.isoformat()
        }
    
    async def log_action(self, action: str, details: Dict[str, Any]):
        """Log agent actions for debugging and monitoring"""
        log_entry = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        # In production, send to logging service
        print(f"[{self.name}] {action}: {details.get('message', '')[:100]}...")
        return log_entry