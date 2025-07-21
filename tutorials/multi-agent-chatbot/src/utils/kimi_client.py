import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import os

class KimiK2Client:
    """Client for interacting with Kimi K2 API with advanced reasoning capabilities"""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        self.api_url = api_url or os.getenv("KIMI_API_URL", "https://api.kimi.ai/v1")
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def complete(self, 
                      messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: int = 2000,
                      system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Get completion from Kimi K2 - fallback to mock response if API not available"""
        
        try:
            if not self.api_key:
                return self._mock_response(messages[-1]["content"])
            
            # Prepare messages
            formatted_messages = []
            if system_prompt:
                formatted_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            formatted_messages.extend(messages)
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "kimi-k2",
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                f"{self.api_url}/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    # Fallback to mock response on error
                    return self._mock_response(messages[-1]["content"])
                
                result = await response.json()
                return result
                
        except Exception:
            # Fallback to mock response on any error
            return self._mock_response(messages[-1]["content"])
    
    def _mock_response(self, user_message: str) -> Dict[str, Any]:
        """Generate a mock response when Kimi API is not available"""
        response_content = f"""I understand you're asking about: "{user_message[:100]}..."

I'm currently running in demonstration mode. In a production environment with proper API keys, I would:

1. Analyze your request using advanced reasoning
2. Consider multiple approaches to address your needs
3. Provide detailed, context-aware responses
4. Leverage my specialized capabilities for this type of query

For now, I can still help you with general questions and demonstrate the multi-agent system architecture. Each agent in this system has specific capabilities:

- Research Agent: Information gathering and fact-checking
- Task Agent: Action execution and workflow automation  
- Memory Agent: Context management and conversation history
- QA Agent: Question answering with deep understanding

What would you like to explore about the multi-agent system?"""

        return {
            "choices": [{
                "message": {
                    "content": response_content,
                    "role": "assistant"
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": len(response_content.split()),
                "total_tokens": 100 + len(response_content.split())
            }
        }
    
    async def complete_with_reasoning(self,
                                    task: str,
                                    context: str,
                                    temperature: float = 0.7) -> Dict[str, Any]:
        """Use Kimi K2's advanced reasoning capabilities"""
        
        reasoning_prompt = f"""You are an advanced AI assistant with strong reasoning capabilities.

Task: {task}

Context:
{context}

Please approach this task step by step:
1. Analyze the requirements
2. Consider multiple approaches  
3. Choose the best approach with justification
4. Provide a detailed response

Think through this carefully and show your reasoning process."""

        messages = [{
            "role": "user",
            "content": reasoning_prompt
        }]
        
        response = await self.complete(
            messages=messages,
            temperature=temperature,
            max_tokens=3000
        )
        
        # Extract reasoning and final answer
        content = response["choices"][0]["message"]["content"]
        
        # Parse reasoning steps (simplified for demo)
        lines = content.split("\n")
        reasoning_steps = []
        final_answer = content
        
        # Look for structured reasoning
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ["step", "approach", "analysis"]):
                reasoning_steps.append(line.strip())
        
        # If no structured reasoning found, create basic steps
        if not reasoning_steps:
            reasoning_steps = [
                f"Analyzed the task: {task[:50]}...",
                "Considered available information and context",
                "Formulated appropriate response strategy"
            ]
        
        return {
            "reasoning_steps": reasoning_steps,
            "final_answer": final_answer,
            "raw_response": content,
            "metadata": {
                "model": "kimi-k2",
                "timestamp": datetime.utcnow().isoformat(),
                "temperature": temperature
            }
        }