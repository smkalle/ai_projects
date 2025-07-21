from typing import Dict, Any, List
import asyncio
from datetime import datetime
from .base_agent import BaseAgent
from ..utils.kimi_client import KimiK2Client
import os

class SimpleAgent(BaseAgent):
    """Simplified agent that can handle various tasks with basic reasoning"""
    
    def __init__(self, agent_type: str = "general"):
        capabilities = {
            "research": ["information_gathering", "fact_checking", "web_search"],
            "task": ["action_execution", "workflow_automation", "api_integration"],
            "memory": ["context_management", "conversation_history", "user_profiling"],
            "qa": ["question_answering", "explanation", "clarification"],
            "general": ["conversation", "general_assistance", "routing"]
        }
        
        descriptions = {
            "research": "Conducts research, fact-checking, and information gathering",
            "task": "Executes specific tasks and workflows",
            "memory": "Manages conversation history and context",
            "qa": "Handles questions with deep understanding",
            "general": "Provides general assistance and conversation"
        }
        
        super().__init__(
            name=agent_type.title(),
            description=descriptions.get(agent_type, "General purpose agent"),
            capabilities=capabilities.get(agent_type, ["general_assistance"])
        )
        
        self.agent_type = agent_type
        self.kimi_client = KimiK2Client()
        
    async def can_handle(self, task: str) -> float:
        """Determine if this agent can handle the task"""
        task_lower = task.lower()
        
        # Agent-specific keyword matching
        keywords = {
            "research": ["research", "find", "search", "look up", "fact check", "verify", "investigate"],
            "task": ["do", "execute", "perform", "create", "generate", "send", "schedule"],
            "memory": ["remember", "recall", "previous", "history", "mentioned", "discussed"],
            "qa": ["what", "why", "how", "explain", "describe", "tell me", "clarify"],
            "general": ["hello", "hi", "help", "chat", "talk"]
        }
        
        agent_keywords = keywords.get(self.agent_type, [])
        matches = sum(1 for keyword in agent_keywords if keyword in task_lower)
        
        # Return confidence score based on matches
        if matches > 0:
            return min(matches / 3, 0.9)  # Cap at 0.9
        
        # General agent can handle anything at low confidence
        return 0.3 if self.agent_type == "general" else 0.1
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and generate response"""
        current_message = state["messages"][-1]["content"] if state["messages"] else ""
        
        await self.log_action("processing_request", {"message": current_message})
        
        try:
            # Generate response based on agent type
            response = await self._generate_response(current_message, state)
            
            # Add response to messages
            state["messages"].append({
                "role": "assistant",
                "content": response
            })
            
            # Update metadata
            state["metadata"].update({
                "last_agent": self.name,
                "agent_type": self.agent_type,
                "processing_timestamp": datetime.utcnow().isoformat()
            })
            
            await self.log_action("response_generated", {"response_length": len(response)})
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            state["messages"].append({
                "role": "assistant", 
                "content": error_response
            })
            
        return state
    
    async def _generate_response(self, message: str, state: Dict[str, Any]) -> str:
        """Generate response using Kimi K2 client"""
        
        # Create context-aware prompt based on agent type
        system_prompt = self._get_system_prompt()
        
        # Get recent conversation context
        recent_messages = state["messages"][-5:] if len(state["messages"]) > 1 else []
        context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in recent_messages[:-1]  # Exclude current message
        ])
        
        # Prepare messages for API
        messages = [{
            "role": "user",
            "content": f"Context: {context}\n\nCurrent message: {message}"
        }]
        
        try:
            async with self.kimi_client as client:
                response = await client.complete(
                    messages=messages,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                return response["choices"][0]["message"]["content"]
                
        except Exception as e:
            return self._fallback_response(message)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt based on agent type"""
        prompts = {
            "research": """You are a Research Agent specialized in information gathering and fact-checking. 
            Provide accurate, well-researched responses with citations when possible. 
            Focus on finding and verifying information.""",
            
            "task": """You are a Task Agent specialized in executing actions and workflows.
            Help users accomplish specific tasks by breaking them down into actionable steps.
            Focus on practical, executable solutions.""",
            
            "memory": """You are a Memory Agent specialized in managing conversation context.
            Help users recall previous discussions and maintain conversational continuity.
            Focus on contextual awareness and relationship building.""",
            
            "qa": """You are a QA Agent specialized in answering questions with deep understanding.
            Provide comprehensive, well-explained answers that address the core of user questions.
            Focus on clarity and educational value.""",
            
            "general": """You are a helpful AI assistant providing general conversation and assistance.
            Be friendly, helpful, and engaging while maintaining professionalism.
            Adapt your responses to the user's needs and context."""
        }
        
        return prompts.get(self.agent_type, prompts["general"])
    
    def _fallback_response(self, message: str) -> str:
        """Generate fallback response when API is unavailable"""
        responses = {
            "research": f"I'd help you research information about '{message[:50]}...' but I'm currently in demo mode. In production, I would search reliable sources and provide fact-checked information.",
            
            "task": f"I'd help you execute the task '{message[:50]}...' but I'm currently in demo mode. In production, I would break this down into actionable steps and help you complete it.",
            
            "memory": f"I'd help you recall relevant information about '{message[:50]}...' but I'm currently in demo mode. In production, I would maintain context and conversation history.",
            
            "qa": f"I'd provide a detailed answer about '{message[:50]}...' but I'm currently in demo mode. In production, I would give comprehensive explanations with examples.",
            
            "general": f"Thanks for your message about '{message[:50]}...' I'm currently running in demo mode, but I'm here to help! This multi-agent system demonstrates how different specialized agents can work together."
        }
        
        return responses.get(self.agent_type, responses["general"])