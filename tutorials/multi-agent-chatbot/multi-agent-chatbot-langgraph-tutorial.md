# Multi-Agent Chatbot with LangGraph, Context Engineering, and Kimi K2: A Hands-On Tutorial

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Project Setup](#project-setup)
4. [Understanding LangGraph](#understanding-langgraph)
5. [Context Engineering Fundamentals](#context-engineering-fundamentals)
6. [Integrating Kimi K2](#integrating-kimi-k2)
7. [Building the Multi-Agent System](#building-the-multi-agent-system)
8. [Advanced Features](#advanced-features)
9. [Deployment](#deployment)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

## Introduction

In this comprehensive tutorial, we'll build a sophisticated multi-agent chatbot system that leverages:
- **LangGraph**: For orchestrating complex agent workflows and state management
- **Context Engineering**: To optimize agent interactions and memory management
- **Kimi K2**: A powerful language model for enhanced reasoning capabilities

By the end of this tutorial, you'll have a production-ready multi-agent chatbot capable of handling complex business workflows, customer support scenarios, or personal assistant tasks.

### What We'll Build

A multi-agent system with:
- **Coordinator Agent**: Routes queries to specialized agents
- **Research Agent**: Handles information gathering and fact-checking
- **Task Agent**: Executes specific actions and workflows
- **Memory Agent**: Manages conversation history and context
- **QA Agent**: Handles question-answering with context awareness

## Prerequisites

### Required Knowledge
- Python 3.8+
- Basic understanding of async programming
- Familiarity with REST APIs
- Basic understanding of LLMs and prompting

### Required Tools
```bash
# System requirements
python --version  # Should be 3.8+
pip --version     # Latest pip recommended

# API Keys needed
# - OpenAI API key (for LangGraph)
# - Kimi K2 API access
```

## Project Setup

### 1. Create Project Structure

```bash
mkdir multi-agent-chatbot
cd multi-agent-chatbot

# Create directory structure
mkdir -p src/{agents,utils,config,memory}
mkdir -p tests
mkdir -p data/{contexts,templates}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

Create `requirements.txt`:

```txt
langgraph==0.0.20
langchain==0.1.0
langchain-openai==0.0.5
pydantic==2.5.0
python-dotenv==1.0.0
aiohttp==3.9.1
redis==5.0.1
fastapi==0.109.0
uvicorn==0.25.0
numpy==1.24.3
tiktoken==0.5.1
chromadb==0.4.22
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
KIMI_API_KEY=your_kimi_k2_api_key_here
KIMI_API_URL=https://api.kimi.ai/v1

# Redis Configuration (for memory)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
MAX_CONTEXT_LENGTH=4096
```

## Understanding LangGraph

### Core Concepts

LangGraph is a library for building stateful, multi-actor applications with LLMs. Key concepts:

1. **Nodes**: Individual agents or processing steps
2. **Edges**: Connections between nodes defining flow
3. **State**: Shared context passed between nodes
4. **Graphs**: Complete workflow definitions

### Basic LangGraph Setup

Create `src/config/graph_config.py`:

```python
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """State passed between agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str
    context: dict
    task_queue: list
    memory: dict
    metadata: dict

def create_base_graph():
    """Create the base graph structure"""
    workflow = StateGraph(AgentState)
    
    # We'll add nodes and edges here
    return workflow
```

## Context Engineering Fundamentals

Context engineering is crucial for optimizing agent performance. We'll implement:

1. **Dynamic Context Windows**: Adjust context based on task complexity
2. **Context Compression**: Reduce token usage while maintaining relevance
3. **Semantic Chunking**: Break down information intelligently

Create `src/utils/context_manager.py`:

```python
import tiktoken
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter

class ContextManager:
    def __init__(self, max_tokens: int = 4096, model: str = "gpt-4"):
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model(model)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def compress_context(self, messages: List[Dict[str, Any]], 
                        preserve_recent: int = 5) -> List[Dict[str, Any]]:
        """Compress conversation history while preserving important context"""
        if len(messages) <= preserve_recent:
            return messages
        
        # Keep system message and recent messages
        compressed = []
        if messages[0]["role"] == "system":
            compressed.append(messages[0])
            recent_start = -preserve_recent
        else:
            recent_start = -preserve_recent
        
        # Summarize middle messages
        middle_messages = messages[len(compressed):recent_start]
        if middle_messages:
            summary = self._summarize_messages(middle_messages)
            compressed.append({
                "role": "system",
                "content": f"Previous conversation summary: {summary}"
            })
        
        # Add recent messages
        compressed.extend(messages[recent_start:])
        return compressed
    
    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize a list of messages"""
        # In production, use an LLM to summarize
        # For now, simple extraction
        key_points = []
        for msg in messages:
            if msg["role"] == "user":
                key_points.append(f"User asked: {msg['content'][:100]}...")
            elif msg["role"] == "assistant":
                key_points.append(f"Assistant responded about: {msg['content'][:100]}...")
        
        return " ".join(key_points[-5:])  # Keep last 5 key points
    
    def chunk_document(self, document: str) -> List[str]:
        """Split document into semantic chunks"""
        chunks = self.splitter.split_text(document)
        return chunks
    
    def create_context_window(self, 
                            current_task: str,
                            history: List[Dict[str, Any]],
                            relevant_docs: List[str]) -> str:
        """Create optimized context window for current task"""
        context_parts = []
        remaining_tokens = self.max_tokens
        
        # Add current task (highest priority)
        task_tokens = self.count_tokens(current_task)
        if task_tokens < remaining_tokens:
            context_parts.append(f"Current Task: {current_task}")
            remaining_tokens -= task_tokens
        
        # Add compressed history
        compressed_history = self.compress_context(history)
        history_text = "\n".join([f"{m['role']}: {m['content']}" 
                                 for m in compressed_history])
        history_tokens = self.count_tokens(history_text)
        
        if history_tokens < remaining_tokens:
            context_parts.append(f"Conversation History:\n{history_text}")
            remaining_tokens -= history_tokens
        
        # Add relevant documents
        for doc in relevant_docs:
            doc_tokens = self.count_tokens(doc)
            if doc_tokens < remaining_tokens:
                context_parts.append(f"Relevant Information:\n{doc}")
                remaining_tokens -= doc_tokens
            else:
                # Truncate if needed
                truncated = self._truncate_to_tokens(doc, remaining_tokens - 100)
                context_parts.append(f"Relevant Information (truncated):\n{truncated}")
                break
        
        return "\n\n---\n\n".join(context_parts)
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit"""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens) + "..."
```

## Integrating Kimi K2

Kimi K2 is a powerful language model with enhanced reasoning capabilities. Let's create a wrapper for it.

Create `src/utils/kimi_client.py`:

```python
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import backoff

class KimiK2Client:
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @backoff.on_exception(
        backoff.expo,
        aiohttp.ClientError,
        max_tries=3,
        max_time=30
    )
    async def complete(self, 
                      messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: int = 2000,
                      system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Get completion from Kimi K2"""
        
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
        
        async with self.session.post(
            f"{self.api_url}/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Kimi API error: {response.status} - {error_text}")
            
            result = await response.json()
            return result
    
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
        
        # Parse reasoning steps (in production, use structured output)
        lines = content.split("\n")
        reasoning_steps = []
        final_answer = ""
        
        parsing_reasoning = False
        parsing_answer = False
        
        for line in lines:
            if "step" in line.lower() or "approach" in line.lower():
                parsing_reasoning = True
                parsing_answer = False
            elif "final answer" in line.lower() or "conclusion" in line.lower():
                parsing_reasoning = False
                parsing_answer = True
            elif parsing_reasoning:
                reasoning_steps.append(line.strip())
            elif parsing_answer:
                final_answer += line + "\n"
        
        return {
            "reasoning_steps": reasoning_steps,
            "final_answer": final_answer.strip(),
            "raw_response": content,
            "metadata": {
                "model": "kimi-k2",
                "timestamp": datetime.utcnow().isoformat(),
                "temperature": temperature
            }
        }
```

## Building the Multi-Agent System

Now let's build our specialized agents that work together.

### 1. Base Agent Class

Create `src/agents/base_agent.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class BaseAgent(ABC):
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
        print(f"[{self.name}] {action}: {details}")
        return log_entry
```

### 2. Coordinator Agent

Create `src/agents/coordinator_agent.py`:

```python
from typing import Dict, Any, List
import asyncio
from .base_agent import BaseAgent
from ..utils.kimi_client import KimiK2Client
import os

class CoordinatorAgent(BaseAgent):
    def __init__(self, agents_registry: Dict[str, BaseAgent]):
        super().__init__(
            name="Coordinator",
            description="Routes tasks to appropriate specialized agents",
            capabilities=["task_routing", "agent_orchestration", "workflow_management"]
        )
        self.agents_registry = agents_registry
        self.kimi_client = None
        
    async def initialize(self):
        """Initialize Kimi client"""
        self.kimi_client = KimiK2Client(
            api_key=os.getenv("KIMI_API_KEY"),
            api_url=os.getenv("KIMI_API_URL")
        )
    
    async def can_handle(self, task: str) -> float:
        """Coordinator can handle all tasks by routing them"""
        return 1.0
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to appropriate agent"""
        current_message = state["messages"][-1]["content"]
        
        # Analyze task and determine best agent
        best_agent = await self._select_best_agent(current_message, state)
        
        if best_agent:
            await self.log_action("routing_task", {
                "task": current_message,
                "selected_agent": best_agent.name
            })
            
            # Update state with selected agent
            state["current_agent"] = best_agent.name
            state["metadata"]["routing_decision"] = {
                "coordinator": self.agent_id,
                "selected_agent": best_agent.name,
                "reasoning": state.get("routing_reasoning", "")
            }
            
            # Process with selected agent
            state = await best_agent.process(state)
        else:
            # Handle with general response
            state = await self._handle_general_query(current_message, state)
        
        return state
    
    async def _select_best_agent(self, task: str, state: Dict[str, Any]) -> BaseAgent:
        """Select the best agent for the task using Kimi K2"""
        
        # Get agent capabilities
        agents_info = []
        for agent_name, agent in self.agents_registry.items():
            if agent_name != self.name:  # Don't include coordinator
                confidence = await agent.can_handle(task)
                agents_info.append({
                    "name": agent_name,
                    "description": agent.description,
                    "capabilities": agent.capabilities,
                    "confidence": confidence
                })
        
        # Use Kimi K2 to analyze and select best agent
        async with self.kimi_client as client:
            selection_prompt = f"""Analyze this task and select the best agent:

Task: {task}

Available Agents:
{json.dumps(agents_info, indent=2)}

Context from conversation:
{self._get_recent_context(state)}

Select the most appropriate agent and explain your reasoning."""

            result = await client.complete_with_reasoning(
                task="Select the best agent for this task",
                context=selection_prompt,
                temperature=0.3  # Lower temperature for more consistent routing
            )
        
        # Parse agent selection
        selected_agent_name = self._parse_agent_selection(result["final_answer"])
        state["routing_reasoning"] = " ".join(result["reasoning_steps"])
        
        return self.agents_registry.get(selected_agent_name)
    
    def _get_recent_context(self, state: Dict[str, Any], max_messages: int = 5) -> str:
        """Get recent conversation context"""
        recent_messages = state["messages"][-max_messages:]
        context = []
        for msg in recent_messages:
            context.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(context)
    
    def _parse_agent_selection(self, response: str) -> str:
        """Parse agent name from response"""
        # Simple parsing - in production use structured output
        response_lower = response.lower()
        for agent_name in self.agents_registry:
            if agent_name.lower() in response_lower:
                return agent_name
        return None
    
    async def _handle_general_query(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle queries that don't fit specific agents"""
        async with self.kimi_client as client:
            response = await client.complete(
                messages=[{"role": "user", "content": query}],
                system_prompt="You are a helpful AI assistant. Provide clear, concise responses."
            )
        
        state["messages"].append({
            "role": "assistant",
            "content": response["choices"][0]["message"]["content"]
        })
        
        return state
```

### 3. Research Agent

Create `src/agents/research_agent.py`:

```python
from typing import Dict, Any, List
import asyncio
import aiohttp
from .base_agent import BaseAgent
from ..utils.kimi_client import KimiK2Client
from ..utils.context_manager import ContextManager
import os

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research",
            description="Conducts research, fact-checking, and information gathering",
            capabilities=["web_search", "fact_checking", "data_analysis", "summarization"]
        )
        self.context_manager = ContextManager()
        self.kimi_client = None
        
    async def initialize(self):
        """Initialize Kimi client"""
        self.kimi_client = KimiK2Client(
            api_key=os.getenv("KIMI_API_KEY"),
            api_url=os.getenv("KIMI_API_URL")
        )
    
    async def can_handle(self, task: str) -> float:
        """Determine if this agent can handle the task"""
        research_keywords = [
            "research", "find", "search", "look up", "fact check",
            "verify", "investigate", "analyze", "data", "information",
            "what is", "how does", "explain", "tell me about"
        ]
        
        task_lower = task.lower()
        score = sum(1 for keyword in research_keywords if keyword in task_lower)
        return min(score / 3, 1.0)  # Normalize to 0-1
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process research request"""
        task = state["messages"][-1]["content"]
        
        await self.log_action("starting_research", {"task": task})
        
        # Extract research query
        research_query = await self._extract_research_query(task, state)
        
        # Conduct research
        research_results = await self._conduct_research(research_query)
        
        # Synthesize findings
        synthesis = await self._synthesize_findings(
            query=research_query,
            results=research_results,
            context=state
        )
        
        # Update state with response
        state["messages"].append({
            "role": "assistant",
            "content": synthesis["response"]
        })
        
        # Store research metadata
        state["metadata"]["research"] = {
            "query": research_query,
            "sources": research_results.get("sources", []),
            "confidence": synthesis.get("confidence", 0.8),
            "key_findings": synthesis.get("key_findings", [])
        }
        
        await self.log_action("research_completed", {
            "sources_used": len(research_results.get("sources", [])),
            "confidence": synthesis.get("confidence", 0.8)
        })
        
        return state
    
    async def _extract_research_query(self, task: str, state: Dict[str, Any]) -> str:
        """Extract the core research query from the task"""
        async with self.kimi_client as client:
            extraction_prompt = f"""Extract the main research query from this request:

Task: {task}

Context: {self.context_manager._get_recent_context(state)}

Provide only the core research query, nothing else."""

            response = await client.complete(
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=0.3,
                max_tokens=200
            )
        
        return response["choices"][0]["message"]["content"].strip()
    
    async def _conduct_research(self, query: str) -> Dict[str, Any]:
        """Conduct actual research (simplified for tutorial)"""
        # In production, integrate with:
        # - Web search APIs (Google, Bing, etc.)
        # - Knowledge bases
        # - Vector databases
        # - Academic databases
        
        # Simulated research results
        results = {
            "sources": [
                {
                    "type": "web",
                    "title": f"Information about {query}",
                    "content": f"Detailed information about {query}...",
                    "url": "https://example.com/info",
                    "reliability": 0.9
                },
                {
                    "type": "knowledge_base",
                    "title": f"Technical details on {query}",
                    "content": f"Technical specifications and details...",
                    "reliability": 0.95
                }
            ],
            "raw_data": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # In production, implement actual search
        await asyncio.sleep(0.5)  # Simulate API call
        
        return results
    
    async def _synthesize_findings(self, 
                                 query: str, 
                                 results: Dict[str, Any],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize research findings into coherent response"""
        
        # Prepare research summary
        sources_summary = []
        for source in results.get("sources", []):
            sources_summary.append(
                f"- {source['title']} (reliability: {source['reliability']}): "
                f"{source['content'][:200]}..."
            )
        
        synthesis_prompt = f"""Synthesize research findings into a comprehensive response.

Research Query: {query}

Sources Found:
{chr(10).join(sources_summary)}

Context from conversation:
{self.context_manager._get_recent_context(context)}

Provide:
1. A comprehensive answer to the research query
2. Key findings (list 3-5 main points)
3. Confidence level (0-1) in the findings
4. Any caveats or limitations

Format the response to be helpful and informative."""

        async with self.kimi_client as client:
            result = await client.complete_with_reasoning(
                task="Synthesize research findings",
                context=synthesis_prompt,
                temperature=0.5
            )
        
        # Parse synthesis (in production, use structured output)
        response_text = result["final_answer"]
        
        # Extract key findings
        key_findings = self._extract_key_findings(response_text)
        
        return {
            "response": response_text,
            "key_findings": key_findings,
            "confidence": 0.85,  # In production, calculate based on sources
            "reasoning": result["reasoning_steps"]
        }
    
    def _extract_key_findings(self, text: str) -> List[str]:
        """Extract key findings from synthesis"""
        # Simple extraction - in production use NLP
        findings = []
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith("-") or line.startswith("•") or 
                        line[0].isdigit() and "." in line[:3]):
                findings.append(line.lstrip("-•1234567890. "))
        
        return findings[:5]  # Top 5 findings
```

### 4. Task Agent

Create `src/agents/task_agent.py`:

```python
from typing import Dict, Any, List, Optional
import asyncio
import json
from .base_agent import BaseAgent
from ..utils.kimi_client import KimiK2Client
import os

class TaskAgent(BaseAgent):
    def __init__(self, task_registry: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Task",
            description="Executes specific tasks and workflows",
            capabilities=["task_execution", "workflow_automation", "action_planning", "api_integration"]
        )
        self.task_registry = task_registry or {}
        self.kimi_client = None
        self._register_default_tasks()
        
    async def initialize(self):
        """Initialize Kimi client"""
        self.kimi_client = KimiK2Client(
            api_key=os.getenv("KIMI_API_KEY"),
            api_url=os.getenv("KIMI_API_URL")
        )
    
    def _register_default_tasks(self):
        """Register default task handlers"""
        self.task_registry.update({
            "send_email": self._task_send_email,
            "schedule_meeting": self._task_schedule_meeting,
            "create_document": self._task_create_document,
            "analyze_data": self._task_analyze_data,
            "generate_report": self._task_generate_report
        })
    
    async def can_handle(self, task: str) -> float:
        """Determine if this agent can handle the task"""
        action_keywords = [
            "do", "execute", "perform", "create", "generate",
            "send", "schedule", "analyze", "process", "calculate",
            "build", "make", "write", "update", "delete"
        ]
        
        task_lower = task.lower()
        
        # Check for registered tasks
        for task_name in self.task_registry:
            if task_name.replace("_", " ") in task_lower:
                return 0.95
        
        # Check for action keywords
        score = sum(1 for keyword in action_keywords if keyword in task_lower)
        return min(score / 2, 0.8)
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process task execution request"""
        task_description = state["messages"][-1]["content"]
        
        await self.log_action("analyzing_task", {"task": task_description})
        
        # Analyze and plan task execution
        task_plan = await self._create_task_plan(task_description, state)
        
        # Execute task plan
        execution_results = await self._execute_task_plan(task_plan, state)
        
        # Generate response
        response = await self._generate_task_response(
            task_plan=task_plan,
            results=execution_results,
            original_task=task_description
        )
        
        # Update state
        state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        state["metadata"]["task_execution"] = {
            "plan": task_plan,
            "results": execution_results,
            "status": "completed" if execution_results["success"] else "failed"
        }
        
        return state
    
    async def _create_task_plan(self, task: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution plan for the task"""
        planning_prompt = f"""Create a detailed execution plan for this task:

Task: {task}

Available Actions:
{json.dumps(list(self.task_registry.keys()), indent=2)}

Context:
{self._get_context_summary(state)}

Provide:
1. Step-by-step execution plan
2. Required parameters for each step
3. Expected outcomes
4. Potential failure points

Be specific and actionable."""

        async with self.kimi_client as client:
            result = await client.complete_with_reasoning(
                task="Create task execution plan",
                context=planning_prompt,
                temperature=0.4
            )
        
        # Parse plan (in production, use structured output)
        plan = self._parse_task_plan(result["final_answer"])
        plan["reasoning"] = result["reasoning_steps"]
        
        return plan
    
    def _parse_task_plan(self, plan_text: str) -> Dict[str, Any]:
        """Parse task plan from text"""
        # Simplified parsing - in production use structured output
        lines = plan_text.split("\n")
        steps = []
        current_step = None
        
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and "." in line[:3]:
                if current_step:
                    steps.append(current_step)
                current_step = {
                    "description": line[line.index(".") + 1:].strip(),
                    "action": None,
                    "parameters": {},
                    "expected_outcome": ""
                }
            elif current_step and "action:" in line.lower():
                current_step["action"] = line.split(":", 1)[1].strip()
            elif current_step and "parameters:" in line.lower():
                # Parse parameters (simplified)
                params_text = line.split(":", 1)[1].strip()
                current_step["parameters"] = {"raw": params_text}
            elif current_step and "outcome:" in line.lower():
                current_step["expected_outcome"] = line.split(":", 1)[1].strip()
        
        if current_step:
            steps.append(current_step)
        
        return {
            "steps": steps,
            "total_steps": len(steps),
            "estimated_duration": len(steps) * 2  # seconds
        }
    
    async def _execute_task_plan(self, plan: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task plan"""
        results = {
            "success": True,
            "completed_steps": [],
            "failed_steps": [],
            "outputs": []
        }
        
        for i, step in enumerate(plan["steps"]):
            try:
                await self.log_action("executing_step", {
                    "step_number": i + 1,
                    "description": step["description"]
                })
                
                # Execute step based on action
                if step["action"] and step["action"] in self.task_registry:
                    handler = self.task_registry[step["action"]]
                    step_result = await handler(step["parameters"], state)
                else:
                    # Generic execution
                    step_result = await self._execute_generic_step(step, state)
                
                results["completed_steps"].append({
                    "step": i + 1,
                    "description": step["description"],
                    "result": step_result
                })
                results["outputs"].append(step_result.get("output", ""))
                
            except Exception as e:
                results["failed_steps"].append({
                    "step": i + 1,
                    "description": step["description"],
                    "error": str(e)
                })
                results["success"] = False
                
                # Decide whether to continue or abort
                if step.get("critical", True):
                    break
        
        return results
    
    async def _execute_generic_step(self, step: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a generic step"""
        # In production, integrate with actual services
        await asyncio.sleep(0.5)  # Simulate execution
        
        return {
            "status": "completed",
            "output": f"Executed: {step['description']}",
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "duration": 0.5
            }
        }
    
    async def _generate_task_response(self, 
                                    task_plan: Dict[str, Any],
                                    results: Dict[str, Any],
                                    original_task: str) -> str:
        """Generate user-friendly response about task execution"""
        
        response_prompt = f"""Generate a clear, concise response about the task execution.

Original Task: {original_task}

Execution Summary:
- Total Steps: {task_plan['total_steps']}
- Completed: {len(results['completed_steps'])}
- Failed: {len(results['failed_steps'])}
- Success: {results['success']}

Results:
{json.dumps(results['outputs'], indent=2)}

Create a user-friendly summary that:
1. Confirms what was done
2. Highlights key results
3. Mentions any issues (if any)
4. Provides next steps (if applicable)

Keep it concise and professional."""

        async with self.kimi_client as client:
            response = await client.complete(
                messages=[{"role": "user", "content": response_prompt}],
                temperature=0.6,
                max_tokens=500
            )
        
        return response["choices"][0]["message"]["content"]
    
    # Task handler examples
    async def _task_send_email(self, params: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Send email task handler"""
        # In production, integrate with email service
        return {
            "status": "completed",
            "output": f"Email sent successfully",
            "email_id": "mock_email_123",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _task_schedule_meeting(self, params: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule meeting task handler"""
        # In production, integrate with calendar service
        return {
            "status": "completed",
            "output": f"Meeting scheduled",
            "meeting_id": "mock_meeting_456",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _task_create_document(self, params: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Create document task handler"""
        # In production, integrate with document service
        return {
            "status": "completed",
            "output": f"Document created",
            "document_id": "mock_doc_789",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _task_analyze_data(self, params: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data task handler"""
        # In production, perform actual data analysis
        return {
            "status": "completed",
            "output": "Data analysis completed",
            "insights": ["Insight 1", "Insight 2", "Insight 3"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _task_generate_report(self, params: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report task handler"""
        # In production, generate actual report
        return {
            "status": "completed",
            "output": "Report generated successfully",
            "report_url": "https://example.com/reports/mock_report.pdf",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_context_summary(self, state: Dict[str, Any]) -> str:
        """Get context summary for planning"""
        context_items = []
        
        # Recent messages
        recent = state["messages"][-3:]
        for msg in recent:
            context_items.append(f"{msg['role']}: {msg['content'][:100]}...")
        
        # Any relevant metadata
        if "user_preferences" in state.get("metadata", {}):
            context_items.append(f"User preferences: {state['metadata']['user_preferences']}")
        
        return "\n".join(context_items)
```

### 5. Memory Agent

Create `src/agents/memory_agent.py`:

```python
from typing import Dict, Any, List, Optional
import json
import redis
from datetime import datetime, timedelta
import hashlib
from .base_agent import BaseAgent
from ..utils.kimi_client import KimiK2Client
import chromadb
from chromadb.utils import embedding_functions
import os

class MemoryAgent(BaseAgent):
    def __init__(self, redis_config: Dict[str, Any] = None):
        super().__init__(
            name="Memory",
            description="Manages conversation history, context, and long-term memory",
            capabilities=["context_retrieval", "memory_storage", "pattern_recognition", "user_profiling"]
        )
        
        # Redis for short-term memory
        redis_config = redis_config or {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
            "db": int(os.getenv("REDIS_DB", 0))
        }
        self.redis_client = redis.Redis(**redis_config)
        
        # ChromaDB for long-term semantic memory
        self.chroma_client = chromadb.Client()
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-ada-002"
        )
        
        # Create or get collection
        try:
            self.memory_collection = self.chroma_client.create_collection(
                name="agent_memory",
                embedding_function=self.embedding_function
            )
        except:
            self.memory_collection = self.chroma_client.get_collection(
                name="agent_memory",
                embedding_function=self.embedding_function
            )
        
        self.kimi_client = None
        
    async def initialize(self):
        """Initialize Kimi client"""
        self.kimi_client = KimiK2Client(
            api_key=os.getenv("KIMI_API_KEY"),
            api_url=os.getenv("KIMI_API_URL")
        )
    
    async def can_handle(self, task: str) -> float:
        """Determine if this agent can handle the task"""
        memory_keywords = [
            "remember", "recall", "forgot", "previous", "earlier",
            "history", "context", "mentioned", "said", "discussed",
            "last time", "before", "past conversation"
        ]
        
        task_lower = task.lower()
        score = sum(1 for keyword in memory_keywords if keyword in task_lower)
        return min(score / 2, 0.9)
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process memory-related requests"""
        current_message = state["messages"][-1]["content"]
        user_id = state.get("user_id", "default_user")
        
        await self.log_action("processing_memory_request", {
            "user_id": user_id,
            "message": current_message[:100]
        })
        
        # Store current interaction
        await self._store_interaction(user_id, state)
        
        # Determine memory operation type
        operation = await self._determine_memory_operation(current_message)
        
        if operation == "retrieve":
            response = await self._retrieve_relevant_memories(current_message, user_id, state)
        elif operation == "analyze_patterns":
            response = await self._analyze_conversation_patterns(user_id, state)
        elif operation == "summarize":
            response = await self._summarize_conversation_history(user_id, state)
        else:
            response = await self._provide_context_aware_response(current_message, user_id, state)
        
        # Update state with response
        state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        # Update memory metadata
        state["metadata"]["memory"] = {
            "operation": operation,
            "memories_retrieved": state.get("memories_retrieved", 0),
            "user_profile_updated": state.get("profile_updated", False)
        }
        
        return state
    
    async def _determine_memory_operation(self, message: str) -> str:
        """Determine what type of memory operation is needed"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["what did", "remember when", "recall"]):
            return "retrieve"
        elif any(word in message_lower for word in ["pattern", "usually", "tend to"]):
            return "analyze_patterns"
        elif any(word in message_lower for word in ["summarize", "summary", "recap"]):
            return "summarize"
        else:
            return "context_aware"
    
    async def _store_interaction(self, user_id: str, state: Dict[str, Any]):
        """Store current interaction in memory"""
        interaction = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "messages": state["messages"][-2:],  # Last user message and assistant response
            "metadata": state.get("metadata", {})
        }
        
        # Short-term memory (Redis)
        key = f"conversation:{user_id}:{datetime.utcnow().strftime('%Y%m%d')}"
        self.redis_client.lpush(key, json.dumps(interaction))
        self.redis_client.expire(key, 86400 * 7)  # Keep for 7 days
        
        # Long-term memory (ChromaDB)
        content = f"{interaction['messages'][0]['content']} | {interaction['messages'][-1]['content']}"
        doc_id = hashlib.md5(f"{user_id}:{content}:{interaction['timestamp']}".encode()).hexdigest()
        
        self.memory_collection.add(
            documents=[content],
            metadatas=[{
                "user_id": user_id,
                "timestamp": interaction["timestamp"],
                "type": "conversation"
            }],
            ids=[doc_id]
        )
        
        # Update user profile
        await self._update_user_profile(user_id, interaction)
    
    async def _update_user_profile(self, user_id: str, interaction: Dict[str, Any]):
        """Update user profile based on interactions"""
        profile_key = f"user_profile:{user_id}"
        
        # Get existing profile
        profile_data = self.redis_client.get(profile_key)
        if profile_data:
            profile = json.loads(profile_data)
        else:
            profile = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "interaction_count": 0,
                "topics_discussed": [],
                "preferences": {},
                "communication_style": {}
            }
        
        # Update profile
        profile["interaction_count"] += 1
        profile["last_interaction"] = interaction["timestamp"]
        
        # Extract topics (simplified - in production use NLP)
        message = interaction["messages"][0]["content"]
        topics = await self._extract_topics(message)
        profile["topics_discussed"].extend(topics)
        
        # Store updated profile
        self.redis_client.set(profile_key, json.dumps(profile))
        self.redis_client.expire(profile_key, 86400 * 30)  # Keep for 30 days
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # In production, use NLP models for topic extraction
        # For now, simple keyword extraction
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        words = text.lower().split()
        topics = [word for word in words if len(word) > 4 and word not in common_words]
        return topics[:5]  # Top 5 topics
    
    async def _retrieve_relevant_memories(self, 
                                        query: str, 
                                        user_id: str, 
                                        state: Dict[str, Any]) -> str:
        """Retrieve relevant memories for the query"""
        
        # Search in vector database
        results = self.memory_collection.query(
            query_texts=[query],
            n_results=5,
            where={"user_id": user_id}
        )
        
        # Format memories
        memories = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                memories.append({
                    "content": doc,
                    "timestamp": metadata.get("timestamp", ""),
                    "relevance": results["distances"][0][i] if results["distances"] else 1.0
                })
        
        # Generate response with memories
        memory_context = "\n".join([
            f"[{mem['timestamp']}] {mem['content']}" 
            for mem in memories
        ])
        
        response_prompt = f"""Based on the user's query and their conversation history, provide a helpful response.

User Query: {query}

Relevant Memories:
{memory_context}

Current Context:
{self._get_recent_context(state)}

Provide a response that:
1. Directly answers their query
2. References relevant past conversations
3. Maintains consistency with previous interactions"""

        async with self.kimi_client as client:
            response = await client.complete(
                messages=[{"role": "user", "content": response_prompt}],
                temperature=0.7,
                max_tokens=500
            )
        
        state["memories_retrieved"] = len(memories)
        return response["choices"][0]["message"]["content"]
    
    async def _analyze_conversation_patterns(self, user_id: str, state: Dict[str, Any]) -> str:
        """Analyze patterns in user's conversations"""
        # Get user profile
        profile_key = f"user_profile:{user_id}"
        profile_data = self.redis_client.get(profile_key)
        
        if not profile_data:
            return "I don't have enough conversation history to identify patterns yet."
        
        profile = json.loads(profile_data)
        
        # Get recent conversations
        pattern_key = f"conversation:{user_id}:*"
        conversations = []
        for key in self.redis_client.scan_iter(match=pattern_key):
            conv_data = self.redis_client.lrange(key, 0, -1)
            conversations.extend([json.loads(c) for c in conv_data])
        
        # Analyze patterns
        analysis_prompt = f"""Analyze the user's conversation patterns and preferences.

User Profile:
- Total Interactions: {profile['interaction_count']}
- Topics Discussed: {', '.join(profile['topics_discussed'][:10])}
- First Interaction: {profile['created_at']}
- Last Interaction: {profile.get('last_interaction', 'Unknown')}

Recent Conversations: {len(conversations)}

Provide insights about:
1. Common topics or interests
2. Communication preferences
3. Patterns in queries or requests
4. Any notable trends

Be specific and helpful."""

        async with self.kimi_client as client:
            response = await client.complete(
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.6
            )
        
        return response["choices"][0]["message"]["content"]
    
    async def _summarize_conversation_history(self, user_id: str, state: Dict[str, Any]) -> str:
        """Summarize recent conversation history"""
        # Get recent messages from state
        recent_messages = state["messages"][-10:]  # Last 10 messages
        
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in recent_messages
        ])
        
        summary_prompt = f"""Summarize this conversation concisely.

Conversation:
{conversation_text}

Provide:
1. Main topics discussed
2. Key decisions or outcomes
3. Any action items or next steps
4. Overall conversation flow

Keep it brief but comprehensive."""

        async with self.kimi_client as client:
            response = await client.complete(
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.5,
                max_tokens=400
            )
        
        return response["choices"][0]["message"]["content"]
    
    async def _provide_context_aware_response(self, 
                                            message: str, 
                                            user_id: str, 
                                            state: Dict[str, Any]) -> str:
        """Provide response with context awareness"""
        # Get user profile for personalization
        profile_key = f"user_profile:{user_id}"
        profile_data = self.redis_client.get(profile_key)
        profile = json.loads(profile_data) if profile_data else {}
        
        # Get recent relevant memories
        recent_memories = self.memory_collection.query(
            query_texts=[message],
            n_results=3,
            where={"user_id": user_id}
        )
        
        context_prompt = f"""Provide a helpful response considering the user's history and preferences.

Current Message: {message}

User Profile:
- Interaction Count: {profile.get('interaction_count', 0)}
- Common Topics: {', '.join(profile.get('topics_discussed', [])[:5])}

Recent Context:
{self._get_recent_context(state)}

Be helpful and maintain consistency with previous interactions."""

        async with self.kimi_client as client:
            response = await client.complete(
                messages=[{"role": "user", "content": context_prompt}],
                temperature=0.7
            )
        
        return response["choices"][0]["message"]["content"]
    
    def _get_recent_context(self, state: Dict[str, Any], max_messages: int = 5) -> str:
        """Get recent conversation context"""
        recent_messages = state["messages"][-max_messages:]
        context = []
        for msg in recent_messages:
            context.append(f"{msg['role']}: {msg['content'][:200]}...")
        return "\n".join(context)
```

### 6. QA Agent

Create `src/agents/qa_agent.py`:

```python
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from .base_agent import BaseAgent
from ..utils.kimi_client import KimiK2Client
from ..utils.context_manager import ContextManager
import os
import chromadb
from chromadb.utils import embedding_functions

class QAAgent(BaseAgent):
    def __init__(self, knowledge_base_path: Optional[str] = None):
        super().__init__(
            name="QA",
            description="Handles question-answering with deep understanding and context awareness",
            capabilities=["question_answering", "explanation", "clarification", "knowledge_retrieval"]
        )
        
        self.context_manager = ContextManager()
        self.kimi_client = None
        
        # Knowledge base setup
        self.chroma_client = chromadb.Client()
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-ada-002"
        )
        
        # Create or get knowledge collection
        try:
            self.knowledge_collection = self.chroma_client.create_collection(
                name="qa_knowledge_base",
                embedding_function=self.embedding_function
            )
        except:
            self.knowledge_collection = self.chroma_client.get_collection(
                name="qa_knowledge_base",
                embedding_function=self.embedding_function
            )
        
        # Load knowledge base if provided
        if knowledge_base_path:
            self._load_knowledge_base(knowledge_base_path)
    
    async def initialize(self):
        """Initialize Kimi client"""
        self.kimi_client = KimiK2Client(
            api_key=os.getenv("KIMI_API_KEY"),
            api_url=os.getenv("KIMI_API_URL")
        )
    
    def _load_knowledge_base(self, path: str):
        """Load knowledge base documents"""
        # In production, implement loading from various sources
        # (PDFs, docs, websites, databases, etc.)
        pass
    
    async def can_handle(self, task: str) -> float:
        """Determine if this agent can handle the task"""
        qa_keywords = [
            "what", "why", "how", "when", "where", "who",
            "explain", "describe", "tell me", "clarify",
            "meaning", "definition", "understand", "difference between"
        ]
        
        task_lower = task.lower()
        
        # Check if it's a question
        if "?" in task:
            return 0.9
        
        # Check for QA keywords
        score = sum(1 for keyword in qa_keywords if keyword in task_lower)
        return min(score / 2, 0.85)
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process question-answering request"""
        question = state["messages"][-1]["content"]
        
        await self.log_action("processing_question", {"question": question})
        
        # Analyze question type and complexity
        question_analysis = await self._analyze_question(question, state)
        
        # Retrieve relevant knowledge
        relevant_knowledge = await self._retrieve_knowledge(
            question=question,
            question_type=question_analysis["type"],
            context=state
        )
        
        # Generate comprehensive answer
        answer = await self._generate_answer(
            question=question,
            analysis=question_analysis,
            knowledge=relevant_knowledge,
            context=state
        )
        
        # Add follow-up suggestions
        follow_ups = await self._generate_follow_up_questions(
            question=question,
            answer=answer["response"],
            context=state
        )
        
        # Construct final response
        final_response = answer["response"]
        if follow_ups:
            final_response += f"\n\n**Related questions you might ask:**\n"
            for i, fq in enumerate(follow_ups[:3], 1):
                final_response += f"{i}. {fq}\n"
        
        # Update state
        state["messages"].append({
            "role": "assistant",
            "content": final_response
        })
        
        state["metadata"]["qa"] = {
            "question_type": question_analysis["type"],
            "complexity": question_analysis["complexity"],
            "confidence": answer["confidence"],
            "knowledge_sources": len(relevant_knowledge),
            "follow_up_questions": follow_ups
        }
        
        return state
    
    async def _analyze_question(self, question: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the question to understand its type and requirements"""
        
        analysis_prompt = f"""Analyze this question in detail:

Question: {question}

Context: {self.context_manager._get_recent_context(state)}

Provide:
1. Question type (factual, conceptual, procedural, analytical, hypothetical)
2. Complexity level (simple, moderate, complex)
3. Key concepts/entities mentioned
4. Information needed to answer
5. Potential ambiguities
6. Answer format preference (brief, detailed, step-by-step, etc.)"""

        async with self.kimi_client as client:
            result = await client.complete_with_reasoning(
                task="Analyze the question",
                context=analysis_prompt,
                temperature=0.3
            )
        
        # Parse analysis (in production, use structured output)
        analysis = self._parse_question_analysis(result["final_answer"])
        analysis["reasoning"] = result["reasoning_steps"]
        
        return analysis
    
    def _parse_question_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse question analysis from text"""
        # Simplified parsing
        analysis = {
            "type": "factual",  # default
            "complexity": "moderate",  # default
            "key_concepts": [],
            "information_needed": [],
            "ambiguities": [],
            "answer_format": "balanced"
        }
        
        lines = analysis_text.lower().split("\n")
        for line in lines:
            if "type:" in line:
                for qtype in ["factual", "conceptual", "procedural", "analytical", "hypothetical"]:
                    if qtype in line:
                        analysis["type"] = qtype
                        break
            elif "complexity:" in line:
                for level in ["simple", "moderate", "complex"]:
                    if level in line:
                        analysis["complexity"] = level
                        break
            elif "format:" in line:
                if "brief" in line:
                    analysis["answer_format"] = "brief"
                elif "detailed" in line:
                    analysis["answer_format"] = "detailed"
                elif "step" in line:
                    analysis["answer_format"] = "step-by-step"
        
        return analysis
    
    async def _retrieve_knowledge(self, 
                                question: str, 
                                question_type: str,
                                context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge for answering the question"""
        
        # Search in knowledge base
        results = self.knowledge_collection.query(
            query_texts=[question],
            n_results=5
        )
        
        knowledge_items = []
        
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                knowledge_items.append({
                    "content": doc,
                    "relevance": 1 - results["distances"][0][i] if results["distances"] else 0.5,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                })
        
        # For complex questions, search for related concepts
        if question_type in ["conceptual", "analytical"]:
            # Extract key concepts and search for each
            concepts = await self._extract_key_concepts(question)
            for concept in concepts[:3]:  # Top 3 concepts
                concept_results = self.knowledge_collection.query(
                    query_texts=[concept],
                    n_results=2
                )
                if concept_results["documents"] and concept_results["documents"][0]:
                    for i, doc in enumerate(concept_results["documents"][0]):
                        knowledge_items.append({
                            "content": doc,
                            "relevance": 0.7 * (1 - concept_results["distances"][0][i]),
                            "metadata": concept_results["metadatas"][0][i] if concept_results["metadatas"] else {},
                            "concept": concept
                        })
        
        # Sort by relevance
        knowledge_items.sort(key=lambda x: x["relevance"], reverse=True)
        
        return knowledge_items[:7]  # Top 7 most relevant
    
    async def _extract_key_concepts(self, question: str) -> List[str]:
        """Extract key concepts from question"""
        # In production, use NER and concept extraction models
        # Simplified implementation
        concept_prompt = f"""Extract the key concepts from this question:

Question: {question}

List only the main concepts, entities, or topics (max 5).
One concept per line."""

        async with self.kimi_client as client:
            response = await client.complete(
                messages=[{"role": "user", "content": concept_prompt}],
                temperature=0.3,
                max_tokens=100
            )
        
        concepts = [line.strip() for line in response["choices"][0]["message"]["content"].split("\n") if line.strip()]
        return concepts[:5]
    
    async def _generate_answer(self,
                             question: str,
                             analysis: Dict[str, Any],
                             knowledge: List[Dict[str, Any]],
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive answer using Kimi K2"""
        
        # Prepare knowledge context
        knowledge_context = "\n\n".join([
            f"[Relevance: {k['relevance']:.2f}] {k['content']}"
            for k in knowledge[:5]
        ])
        
        # Craft answer generation prompt based on question type
        answer_prompt = self._create_answer_prompt(
            question=question,
            question_type=analysis["type"],
            answer_format=analysis["answer_format"],
            knowledge=knowledge_context,
            context=self.context_manager._get_recent_context(context)
        )
        
        async with self.kimi_client as client:
            result = await client.complete_with_reasoning(
                task="Answer the question comprehensively",
                context=answer_prompt,
                temperature=0.6
            )
        
        # Evaluate answer confidence
        confidence = await self._evaluate_answer_confidence(
            question=question,
            answer=result["final_answer"],
            knowledge_available=len(knowledge) > 0
        )
        
        return {
            "response": result["final_answer"],
            "confidence": confidence,
            "reasoning": result["reasoning_steps"],
            "knowledge_used": len(knowledge)
        }
    
    def _create_answer_prompt(self,
                            question: str,
                            question_type: str,
                            answer_format: str,
                            knowledge: str,
                            context: str) -> str:
        """Create tailored prompt based on question type"""
        
        base_prompt = f"""Answer this question accurately and helpfully.

Question: {question}
Question Type: {question_type}
Preferred Format: {answer_format}

Available Knowledge:
{knowledge}

Conversation Context:
{context}

"""
        
        # Add type-specific instructions
        if question_type == "factual":
            base_prompt += """Provide accurate facts with sources when available.
Be direct and concise while ensuring accuracy."""
        
        elif question_type == "conceptual":
            base_prompt += """Explain the concept clearly with examples.
Break down complex ideas into understandable parts.
Show relationships between concepts."""
        
        elif question_type == "procedural":
            base_prompt += """Provide clear step-by-step instructions.
Include prerequisites and expected outcomes.
Mention common pitfalls to avoid."""
        
        elif question_type == "analytical":
            base_prompt += """Analyze different aspects systematically.
Consider multiple perspectives.
Provide evidence-based reasoning."""
        
        elif question_type == "hypothetical":
            base_prompt += """Explore the scenario thoughtfully.
Consider various possibilities and their implications.
Distinguish between speculation and known facts."""
        
        # Add format-specific instructions
        if answer_format == "brief":
            base_prompt += "\n\nKeep the answer concise (2-3 sentences max)."
        elif answer_format == "detailed":
            base_prompt += "\n\nProvide a comprehensive, detailed answer."
        elif answer_format == "step-by-step":
            base_prompt += "\n\nStructure the answer as numbered steps."
        
        return base_prompt
    
    async def _evaluate_answer_confidence(self,
                                        question: str,
                                        answer: str,
                                        knowledge_available: bool) -> float:
        """Evaluate confidence in the generated answer"""
        
        evaluation_prompt = f"""Evaluate the quality and confidence of this answer.

Question: {question}
Answer: {answer}
Knowledge Available: {knowledge_available}

Rate on these criteria (0-1 scale):
1. Accuracy: How accurate is the answer?
2. Completeness: Does it fully address the question?
3. Clarity: Is it clear and understandable?
4. Evidence: Is it well-supported?

Provide an overall confidence score (0-1)."""

        async with self.kimi_client as client:
            response = await client.complete(
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.3,
                max_tokens=200
            )
        
        # Parse confidence (in production, use structured output)
        try:
            response_text = response["choices"][0]["message"]["content"].lower()
            if "confidence:" in response_text:
                conf_text = response_text.split("confidence:")[1].strip()
                confidence = float(conf_text.split()[0].strip(",."))
                return min(max(confidence, 0.0), 1.0)
        except:
            pass
        
        # Default confidence based on knowledge availability
        return 0.8 if knowledge_available else 0.6
    
    async def _generate_follow_up_questions(self,
                                          question: str,
                                          answer: str,
                                          context: Dict[str, Any]) -> List[str]:
        """Generate relevant follow-up questions"""
        
        follow_up_prompt = f"""Based on this Q&A exchange, suggest relevant follow-up questions.

Original Question: {question}
Answer Provided: {answer[:500]}...

Generate 3-5 follow-up questions that:
1. Explore the topic deeper
2. Clarify specific aspects
3. Connect to related topics
4. Are likely to be helpful

One question per line."""

        async with self.kimi_client as client:
            response = await client.complete(
                messages=[{"role": "user", "content": follow_up_prompt}],
                temperature=0.8,
                max_tokens=200
            )
        
        questions = [
            line.strip().lstrip("123456789.- ")
            for line in response["choices"][0]["message"]["content"].split("\n")
            if line.strip() and "?" in line
        ]
        
        return questions[:5]
```

### 7. Multi-Agent Orchestration

Create `src/multi_agent_system.py`:

```python
from typing import Dict, Any, List, Optional
import asyncio
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .agents.coordinator_agent import CoordinatorAgent
from .agents.research_agent import ResearchAgent
from .agents.task_agent import TaskAgent
from .agents.memory_agent import MemoryAgent
from .agents.qa_agent import QAAgent
from .config.graph_config import AgentState

class MultiAgentSystem:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize agents
        self.agents = {}
        self._initialize_agents()
        
        # Create workflow graph
        self.workflow = self._create_workflow()
        self.app = None
    
    def _initialize_agents(self):
        """Initialize all agents"""
        # Create specialized agents
        self.agents["research"] = ResearchAgent()
        self.agents["task"] = TaskAgent()
        self.agents["memory"] = MemoryAgent()
        self.agents["qa"] = QAAgent()
        
        # Create coordinator with agent registry
        self.agents["coordinator"] = CoordinatorAgent(self.agents)
    
    async def initialize(self):
        """Async initialization for all agents"""
        init_tasks = []
        for agent in self.agents.values():
            if hasattr(agent, 'initialize'):
                init_tasks.append(agent.initialize())
        
        await asyncio.gather(*init_tasks)
        
        # Compile the workflow
        self.app = self.workflow.compile()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        for agent_name, agent in self.agents.items():
            workflow.add_node(agent_name, self._create_agent_node(agent))
        
        # Add entry point
        workflow.set_entry_point("coordinator")
        
        # Add conditional edges based on coordinator's decision
        workflow.add_conditional_edges(
            "coordinator",
            self._route_to_agent,
            {
                "research": "research",
                "task": "task",
                "memory": "memory",
                "qa": "qa",
                "end": END
            }
        )
        
        # Add edges back to coordinator after each agent
        for agent_name in ["research", "task", "memory", "qa"]:
            workflow.add_edge(agent_name, "coordinator")
        
        return workflow
    
    def _create_agent_node(self, agent):
        """Create a node function for an agent"""
        async def node_fn(state: AgentState) -> AgentState:
            # Process with the agent
            updated_state = await agent.process(state)
            return updated_state
        
        return node_fn
    
    def _route_to_agent(self, state: AgentState) -> str:
        """Determine which agent to route to next"""
        # Check if we should end
        if state.get("should_end", False):
            return "end"
        
        # Check if all tasks are complete
        if not state.get("task_queue", []):
            # Check if this is a follow-up or new query
            last_message = state["messages"][-1]
            if last_message["role"] == "assistant":
                return "end"
        
        # Route based on current agent selection
        current_agent = state.get("current_agent", "coordinator")
        
        # Map agent names to valid routes
        agent_mapping = {
            "Research": "research",
            "Task": "task",
            "Memory": "memory",
            "QA": "qa"
        }
        
        return agent_mapping.get(current_agent, "end")
    
    async def process_message(self, 
                            message: str, 
                            user_id: str = "default_user",
                            session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a user message through the multi-agent system"""
        
        # Initialize state
        initial_state = {
            "messages": [{"role": "user", "content": message}],
            "current_agent": "coordinator",
            "context": {},
            "task_queue": [],
            "memory": {},
            "metadata": {
                "user_id": user_id,
                "session_id": session_id or f"session_{datetime.utcnow().timestamp()}"
            }
        }
        
        # Run the workflow
        try:
            final_state = await self.app.ainvoke(initial_state)
            
            # Extract response
            response = {
                "response": final_state["messages"][-1]["content"],
                "metadata": final_state.get("metadata", {}),
                "agent_used": final_state.get("current_agent", "unknown")
            }
            
            return response
            
        except Exception as e:
            return {
                "response": f"I encountered an error processing your request: {str(e)}",
                "metadata": {"error": str(e)},
                "agent_used": "error_handler"
            }
    
    async def process_conversation(self,
                                 messages: List[Dict[str, str]],
                                 user_id: str = "default_user") -> List[Dict[str, Any]]:
        """Process a full conversation"""
        responses = []
        session_id = f"session_{datetime.utcnow().timestamp()}"
        
        for message in messages:
            if message["role"] == "user":
                response = await self.process_message(
                    message["content"],
                    user_id,
                    session_id
                )
                responses.append(response)
        
        return responses
```

## Advanced Features

### 1. Streaming Responses

Create `src/utils/streaming.py`:

```python
from typing import AsyncIterator, Dict, Any
import asyncio
import json

class StreamingHandler:
    def __init__(self, multi_agent_system):
        self.system = multi_agent_system
    
    async def stream_response(self, 
                            message: str,
                            user_id: str = "default_user") -> AsyncIterator[str]:
        """Stream response tokens as they're generated"""
        
        # In production, integrate with LLM streaming APIs
        # This is a simplified implementation
        
        # Get the full response first
        response = await self.system.process_message(message, user_id)
        
        # Simulate streaming by yielding chunks
        full_text = response["response"]
        words = full_text.split()
        
        buffer = []
        for i, word in enumerate(words):
            buffer.append(word)
            
            # Yield every 3 words or at the end
            if len(buffer) >= 3 or i == len(words) - 1:
                chunk = " ".join(buffer) + " "
                yield json.dumps({
                    "type": "content",
                    "content": chunk,
                    "metadata": {
                        "agent": response.get("agent_used", "unknown"),
                        "partial": i < len(words) - 1
                    }
                })
                buffer = []
                await asyncio.sleep(0.05)  # Simulate typing delay
        
        # Send completion marker
        yield json.dumps({
            "type": "complete",
            "metadata": response.get("metadata", {})
        })
```

### 2. Agent Plugins

Create `src/plugins/base_plugin.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BasePlugin(ABC):
    """Base class for agent plugins"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.enabled = True
    
    @abstractmethod
    async def execute(self, 
                     input_data: Dict[str, Any],
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin functionality"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this plugin provides"""
        pass
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate plugin input"""
        return True
```

### 3. Performance Monitoring

Create `src/utils/monitoring.py`:

```python
import time
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from collections import defaultdict

class PerformanceMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.active_timers = {}
    
    def start_timer(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Start timing an operation"""
        timer_id = f"{operation}_{time.time()}"
        self.active_timers[timer_id] = {
            "operation": operation,
            "start_time": time.time(),
            "metadata": metadata or {}
        }
        return timer_id
    
    def end_timer(self, timer_id: str):
        """End timing and record metrics"""
        if timer_id not in self.active_timers:
            return
        
        timer_data = self.active_timers.pop(timer_id)
        duration = time.time() - timer_data["start_time"]
        
        self.metrics[timer_data["operation"]].append({
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": timer_data["metadata"]
        })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        summary = {}
        
        for operation, measurements in self.metrics.items():
            if measurements:
                durations = [m["duration"] for m in measurements]
                summary[operation] = {
                    "count": len(measurements),
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "total_duration": sum(durations)
                }
        
        return summary
    
    async def monitor_async_operation(self, operation: str, coroutine):
        """Monitor an async operation"""
        timer_id = self.start_timer(operation)
        try:
            result = await coroutine
            return result
        finally:
            self.end_timer(timer_id)
```

## Deployment

### 1. FastAPI Application

Create `src/api/main.py`:

```python
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import os
from datetime import datetime

from ..multi_agent_system import MultiAgentSystem
from ..utils.streaming import StreamingHandler
from ..utils.monitoring import PerformanceMonitor

# Initialize FastAPI app
app = FastAPI(title="Multi-Agent Chatbot API", version="1.0.0")

# Global instances
multi_agent_system = None
streaming_handler = None
performance_monitor = PerformanceMonitor()

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    response: str
    metadata: Dict[str, Any]
    agent_used: str
    processing_time: float

class ConversationRequest(BaseModel):
    messages: List[Dict[str, str]]
    user_id: Optional[str] = "default_user"

@app.on_event("startup")
async def startup_event():
    """Initialize the multi-agent system on startup"""
    global multi_agent_system, streaming_handler
    
    print("Initializing Multi-Agent System...")
    multi_agent_system = MultiAgentSystem()
    await multi_agent_system.initialize()
    
    streaming_handler = StreamingHandler(multi_agent_system)
    print("Multi-Agent System initialized successfully!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi-Agent Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "stream": "/stream",
            "conversation": "/conversation",
            "health": "/health",
            "metrics": "/metrics"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a single message"""
    if not multi_agent_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Monitor performance
    timer_id = performance_monitor.start_timer("chat_request", {
        "user_id": request.user_id,
        "message_length": len(request.message)
    })
    
    try:
        # Process message
        result = await multi_agent_system.process_message(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Calculate processing time
        performance_monitor.end_timer(timer_id)
        metrics = performance_monitor.get_metrics_summary()
        processing_time = metrics.get("chat_request", {}).get("avg_duration", 0)
        
        return ChatResponse(
            response=result["response"],
            metadata=result["metadata"],
            agent_used=result["agent_used"],
            processing_time=processing_time
        )
        
    except Exception as e:
        performance_monitor.end_timer(timer_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream")
async def stream_chat(request: ChatRequest):
    """Stream response tokens"""
    if not streaming_handler:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    async def generate():
        try:
            async for chunk in streaming_handler.stream_response(
                message=request.message,
                user_id=request.user_id
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/conversation")
async def process_conversation(request: ConversationRequest):
    """Process a full conversation"""
    if not multi_agent_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        responses = await multi_agent_system.process_conversation(
            messages=request.messages,
            user_id=request.user_id
        )
        
        return {
            "responses": responses,
            "total_messages": len(request.messages),
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process message
            if data.get("type") == "chat":
                result = await multi_agent_system.process_message(
                    message=data["message"],
                    user_id=data.get("user_id", "websocket_user")
                )
                
                # Send response
                await websocket.send_json({
                    "type": "response",
                    "data": result
                })
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })
        await websocket.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    is_healthy = multi_agent_system is not None
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": list(multi_agent_system.agents.keys()) if is_healthy else []
    }

@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    return {
        "metrics": performance_monitor.get_metrics_summary(),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Docker Configuration

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY .env .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - chatbot
    restart: unless-stopped

volumes:
  redis_data:
```

### 3. Production Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream chatbot_backend {
        server chatbot:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # WebSocket support
        location /ws {
            proxy_pass http://chatbot_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }

        # SSE support for streaming
        location /stream {
            proxy_pass http://chatbot_backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_buffering off;
            proxy_cache off;
            proxy_read_timeout 86400;
        }

        # Regular API endpoints
        location / {
            proxy_pass http://chatbot_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Best Practices

### 1. Error Handling

Create `src/utils/error_handling.py`:

```python
from typing import Dict, Any, Optional, Callable
import logging
import traceback
from functools import wraps
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentError(Exception):
    """Base exception for agent errors"""
    def __init__(self, message: str, agent_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.agent_name = agent_name
        self.details = details or {}

class AgentTimeoutError(AgentError):
    """Raised when an agent operation times out"""
    pass

class AgentValidationError(AgentError):
    """Raised when agent input validation fails"""
    pass

def handle_agent_errors(agent_name: str):
    """Decorator for handling agent errors"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AgentError:
                # Re-raise agent errors
                raise
            except asyncio.TimeoutError:
                raise AgentTimeoutError(
                    f"Operation timed out in {agent_name}",
                    agent_name=agent_name
                )
            except Exception as e:
                logger.error(f"Error in {agent_name}: {str(e)}")
                logger.error(traceback.format_exc())
                raise AgentError(
                    f"Unexpected error in {agent_name}: {str(e)}",
                    agent_name=agent_name,
                    details={"original_error": str(e)}
                )
        return wrapper
    return decorator

class ErrorRecoveryStrategy:
    """Strategies for recovering from errors"""
    
    @staticmethod
    async def retry_with_backoff(
        coroutine_func: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        """Retry with exponential backoff"""
        delay = initial_delay
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await coroutine_func()
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
                    logger.warning(f"Retry attempt {attempt + 1} after error: {str(e)}")
        
        raise last_error
    
    @staticmethod
    async def fallback_response(error: Exception, context: Dict[str, Any]) -> str:
        """Generate a fallback response when an error occurs"""
        error_messages = {
            AgentTimeoutError: "I'm taking longer than expected to process this. Please try again.",
            AgentValidationError: "I couldn't understand that request. Could you rephrase it?",
        }
        
        message = error_messages.get(
            type(error),
            "I encountered an issue processing your request. Please try again."
        )
        
        # Log for debugging
        logger.error(f"Fallback response triggered: {error}")
        
        return message
```

### 2. Testing

Create `tests/test_agents.py`:

```python
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.agents.research_agent import ResearchAgent
from src.agents.task_agent import TaskAgent
from src.agents.memory_agent import MemoryAgent
from src.agents.qa_agent import QAAgent
from src.agents.coordinator_agent import CoordinatorAgent

@pytest.fixture
def mock_state():
    """Create mock state for testing"""
    return {
        "messages": [
            {"role": "user", "content": "Test message"}
        ],
        "current_agent": "test",
        "context": {},
        "task_queue": [],
        "memory": {},
        "metadata": {"user_id": "test_user"}
    }

@pytest.mark.asyncio
async def test_research_agent_initialization():
    """Test research agent initialization"""
    agent = ResearchAgent()
    
    assert agent.name == "Research"
    assert "web_search" in agent.capabilities
    assert "fact_checking" in agent.capabilities

@pytest.mark.asyncio
async def test_research_agent_can_handle():
    """Test research agent's ability to handle tasks"""
    agent = ResearchAgent()
    
    # Should handle research-related queries
    assert await agent.can_handle("research climate change") > 0.5
    assert await agent.can_handle("find information about Python") > 0.5
    assert await agent.can_handle("what is machine learning") > 0.5
    
    # Should not handle non-research queries
    assert await agent.can_handle("send an email") < 0.5
    assert await agent.can_handle("schedule a meeting") < 0.5

@pytest.mark.asyncio
async def test_task_agent_plan_creation(mock_state):
    """Test task agent's plan creation"""
    agent = TaskAgent()
    
    with patch.object(agent, 'kimi_client') as mock_client:
        mock_client.complete_with_reasoning = AsyncMock(return_value={
            "final_answer": "1. Send email\n2. Update calendar",
            "reasoning_steps": ["Step 1", "Step 2"]
        })
        
        plan = await agent._create_task_plan("Send email and update calendar", mock_state)
        
        assert "steps" in plan
        assert len(plan["steps"]) > 0
        assert "reasoning" in plan

@pytest.mark.asyncio
async def test_memory_agent_storage(mock_state):
    """Test memory agent's storage functionality"""
    agent = MemoryAgent()
    
    # Mock Redis client
    agent.redis_client = Mock()
    agent.memory_collection = Mock()
    
    await agent._store_interaction("test_user", mock_state)
    
    # Verify Redis storage was called
    agent.redis_client.lpush.assert_called()
    agent.redis_client.expire.assert_called()
    
    # Verify ChromaDB storage was called
    agent.memory_collection.add.assert_called()

@pytest.mark.asyncio
async def test_qa_agent_question_analysis():
    """Test QA agent's question analysis"""
    agent = QAAgent()
    
    with patch.object(agent, 'kimi_client') as mock_client:
        mock_client.complete_with_reasoning = AsyncMock(return_value={
            "final_answer": "Type: factual\nComplexity: simple",
            "reasoning_steps": ["Analyzing question type"]
        })
        
        analysis = await agent._analyze_question("What is the capital of France?", {})
        
        assert "type" in analysis
        assert "complexity" in analysis

@pytest.mark.asyncio
async def test_coordinator_agent_routing(mock_state):
    """Test coordinator agent's routing logic"""
    # Create mock agents
    mock_agents = {
        "research": Mock(can_handle=AsyncMock(return_value=0.8)),
        "task": Mock(can_handle=AsyncMock(return_value=0.3)),
        "qa": Mock(can_handle=AsyncMock(return_value=0.9))
    }
    
    agent = CoordinatorAgent(mock_agents)
    
    with patch.object(agent, 'kimi_client') as mock_client:
        mock_client.complete_with_reasoning = AsyncMock(return_value={
            "final_answer": "Select: qa agent for this question",
            "reasoning_steps": ["This is a question", "QA agent is best suited"]
        })
        
        best_agent = await agent._select_best_agent("What is Python?", mock_state)
        
        # Should select QA agent based on mock confidence scores
        assert best_agent is not None

@pytest.mark.asyncio
async def test_error_handling(mock_state):
    """Test error handling in agents"""
    agent = ResearchAgent()
    
    # Simulate an error in research
    with patch.object(agent, '_conduct_research', side_effect=Exception("API Error")):
        with patch.object(agent, 'kimi_client'):
            # Should handle error gracefully
            result = await agent.process(mock_state)
            
            assert "messages" in result
            # Should have added an error message or fallback response

@pytest.mark.asyncio
async def test_multi_agent_integration():
    """Test integration between multiple agents"""
    from src.multi_agent_system import MultiAgentSystem
    
    system = MultiAgentSystem()
    
    # Mock all agent initializations
    for agent in system.agents.values():
        if hasattr(agent, 'initialize'):
            agent.initialize = AsyncMock()
    
    await system.initialize()
    
    # Test message processing
    with patch.object(system.app, 'ainvoke') as mock_invoke:
        mock_invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Test"},
                {"role": "assistant", "content": "Response"}
            ],
            "metadata": {}
        }
        
        response = await system.process_message("Test message")
        
        assert "response" in response
        assert response["response"] == "Response"

# Performance tests
@pytest.mark.asyncio
async def test_concurrent_agent_processing():
    """Test concurrent processing by multiple agents"""
    agents = [
        ResearchAgent(),
        TaskAgent(),
        QAAgent()
    ]
    
    # Create tasks for concurrent processing
    tasks = []
    for agent in agents:
        task = agent.can_handle("process this query")
        tasks.append(task)
    
    # All agents should process concurrently
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(agents)
    assert all(isinstance(r, float) for r in results)

# Load tests
@pytest.mark.asyncio
async def test_high_volume_messages():
    """Test system under high message volume"""
    from src.multi_agent_system import MultiAgentSystem
    
    system = MultiAgentSystem()
    
    # Mock to avoid actual API calls
    for agent in system.agents.values():
        if hasattr(agent, 'initialize'):
            agent.initialize = AsyncMock()
    
    await system.initialize()
    
    # Simulate high volume
    messages = ["Test message " + str(i) for i in range(10)]
    
    with patch.object(system.app, 'ainvoke') as mock_invoke:
        mock_invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Test"},
                {"role": "assistant", "content": "Response"}
            ],
            "metadata": {}
        }
        
        # Process messages concurrently
        tasks = [system.process_message(msg) for msg in messages]
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == len(messages)
        assert all("response" in r for r in responses)
```

### 3. Security Best Practices

Create `src/utils/security.py`:

```python
import re
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet

class SecurityManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.fernet = Fernet(Fernet.generate_key())
        
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove potential script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove SQL injection attempts
        sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'UNION', 'SELECT']
        for keyword in sql_keywords:
            pattern = rf'\b{keyword}\b.*?(TABLE|FROM|WHERE|INTO)'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove special characters that could be used for injection
        text = re.sub(r'[;<>]', '', text)
        
        return text.strip()
    
    def validate_api_key(self, api_key: str, valid_keys: List[str]) -> bool:
        """Validate API key using constant-time comparison"""
        if not api_key or not valid_keys:
            return False
        
        # Use constant-time comparison to prevent timing attacks
        for valid_key in valid_keys:
            if secrets.compare_digest(api_key, valid_key):
                return True
        
        return False
    
    def generate_session_token(self, user_id: str, expiry_hours: int = 24) -> str:
        """Generate JWT session token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expiry_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def rate_limit_check(self, user_id: str, redis_client, max_requests: int = 100, window_seconds: int = 3600) -> bool:
        """Check if user has exceeded rate limit"""
        key = f"rate_limit:{user_id}"
        
        try:
            current_count = redis_client.incr(key)
            
            if current_count == 1:
                redis_client.expire(key, window_seconds)
            
            return current_count <= max_requests
        except:
            # If Redis fails, allow the request
            return True
    
    def detect_prompt_injection(self, text: str) -> bool:
        """Detect potential prompt injection attempts"""
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'disregard\s+all\s+prior',
            r'forget\s+everything',
            r'new\s+instructions:',
            r'system\s+prompt:',
            r'</?\s*prompt\s*>',
            r'###\s*INSTRUCTIONS?\s*###'
        ]
        
        text_lower = text.lower()
        for pattern in injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    def sanitize_output(self, text: str) -> str:
        """Sanitize output to prevent information leakage"""
        # Remove potential API keys or tokens
        text = re.sub(r'\b[A-Za-z0-9]{32,}\b', '[REDACTED]', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        # Remove credit card numbers
        text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', text)
        
        return text

# Middleware for FastAPI
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, security_manager: SecurityManager):
        super().__init__(app)
        self.security_manager = security_manager
    
    async def dispatch(self, request: Request, call_next):
        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        
        # Validate API key for protected endpoints
        if request.url.path.startswith("/api/") and not request.url.path.startswith("/api/public"):
            valid_keys = ["your-api-key-1", "your-api-key-2"]  # In production, load from secure storage
            if not self.security_manager.validate_api_key(api_key, valid_keys):
                raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
```

## Troubleshooting

### Common Issues and Solutions

1. **Memory Issues with Large Context**
   ```python
   # Solution: Implement context window management
   context_manager = ContextManager(max_tokens=2048)
   compressed_context = context_manager.compress_context(messages)
   ```

2. **Agent Response Timeouts**
   ```python
   # Solution: Add timeout handling
   async def with_timeout(coroutine, timeout_seconds=30):
       try:
           return await asyncio.wait_for(coroutine, timeout=timeout_seconds)
       except asyncio.TimeoutError:
           return {"error": "Operation timed out"}
   ```

3. **Rate Limiting Issues**
   ```python
   # Solution: Implement exponential backoff
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
   async def api_call_with_retry():
       # Your API call here
       pass
   ```

## Conclusion

You've now built a sophisticated multi-agent chatbot system using LangGraph, Context Engineering, and Kimi K2. This system features:

- **Modular Architecture**: Easy to extend with new agents
- **Context-Aware Processing**: Intelligent context management
- **Advanced Reasoning**: Powered by Kimi K2
- **Production-Ready**: Complete with API, monitoring, and security

### Next Steps

1. **Add More Agents**: Create specialized agents for your use case
2. **Enhance Memory**: Implement more sophisticated memory strategies
3. **Integrate Services**: Connect to external APIs and databases
4. **Scale Horizontally**: Deploy multiple instances with load balancing
5. **Add Analytics**: Track usage patterns and optimize performance

### Resources

- [LangGraph Documentation](https://github.com/langchain-ai/langgraph)
- [Kimi K2 API Reference](https://kimi.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)

Happy building! 🚀