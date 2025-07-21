from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import time

from .agents.simple_agent import SimpleAgent
from .utils.context_manager import ContextManager

class MultiAgentSystem:
    """Simplified Multi-Agent System for demonstration"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.context_manager = ContextManager()
        
        # System metrics
        self.metrics = {
            "requests_processed": 0,
            "average_response_time": 0,
            "agent_usage": {},
            "errors": 0
        }
        
        # Initialize agents
        self.agents = {}
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all agents"""
        agent_types = ["research", "task", "memory", "qa", "general"]
        
        for agent_type in agent_types:
            self.agents[agent_type] = SimpleAgent(agent_type)
            self.metrics["agent_usage"][agent_type] = 0
    
    async def initialize(self):
        """Async initialization (placeholder for future async setup)"""
        print("Multi-Agent System initialized successfully!")
        return True
    
    async def process_message(self, 
                            message: str, 
                            user_id: str = "default_user",
                            session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a user message through the multi-agent system"""
        
        start_time = time.time()
        
        try:
            # Initialize state
            initial_state = {
                "messages": [{"role": "user", "content": message}],
                "current_agent": None,
                "context": {},
                "task_queue": [],
                "memory": {},
                "metadata": {
                    "user_id": user_id,
                    "session_id": session_id or f"session_{int(time.time())}",
                    "timestamp": datetime.utcnow().isoformat()
                },
                "user_id": user_id,
                "should_end": False
            }
            
            # Select best agent for the task
            best_agent = await self._select_best_agent(message)
            
            # Process with selected agent
            final_state = await best_agent.process(initial_state)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update metrics
            self._update_metrics(best_agent.agent_type, processing_time)
            
            # Extract response
            response = {
                "response": final_state["messages"][-1]["content"],
                "metadata": {
                    **final_state.get("metadata", {}),
                    "agent_used": best_agent.name,
                    "agent_type": best_agent.agent_type,
                    "processing_time": processing_time,
                    "confidence": await best_agent.can_handle(message)
                },
                "agent_used": best_agent.name,
                "processing_time": processing_time
            }
            
            return response
            
        except Exception as e:
            self.metrics["errors"] += 1
            processing_time = time.time() - start_time
            
            return {
                "response": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "metadata": {
                    "error": str(e),
                    "processing_time": processing_time,
                    "agent_used": "error_handler"
                },
                "agent_used": "error_handler",
                "processing_time": processing_time
            }
    
    async def _select_best_agent(self, message: str) -> SimpleAgent:
        """Select the best agent for handling the message"""
        
        # Get confidence scores from all agents
        agent_scores = {}
        
        for agent_type, agent in self.agents.items():
            confidence = await agent.can_handle(message)
            agent_scores[agent_type] = confidence
        
        # Select agent with highest confidence
        best_agent_type = max(agent_scores, key=agent_scores.get)
        
        # If no agent has good confidence, use general agent
        if agent_scores[best_agent_type] < 0.3:
            best_agent_type = "general"
        
        return self.agents[best_agent_type]
    
    def _update_metrics(self, agent_type: str, processing_time: float):
        """Update system metrics"""
        self.metrics["requests_processed"] += 1
        self.metrics["agent_usage"][agent_type] += 1
        
        # Update average response time
        current_avg = self.metrics["average_response_time"]
        total_requests = self.metrics["requests_processed"]
        
        self.metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        return {
            "status": "online",
            "agents_available": len(self.agents),
            "metrics": self.metrics,
            "agent_info": {
                name: agent.get_info() 
                for name, agent in self.agents.items()
            }
        }
    
    async def process_conversation(self,
                                 messages: List[Dict[str, str]],
                                 user_id: str = "default_user") -> List[Dict[str, Any]]:
        """Process a full conversation"""
        responses = []
        session_id = f"session_{int(time.time())}"
        
        for message in messages:
            if message["role"] == "user":
                response = await self.process_message(
                    message["content"],
                    user_id,
                    session_id
                )
                responses.append(response)
        
        return responses