---
name: adk-agent-creator
description: Create and configure Python-based agents using the Agent Development Kit (ADK). Use this when the user wants to scaffold, install, or run an ADK agent project.
---

# ADK Agent Creator

This skill provides a workflow for creating, configuring, and running Python agents using the [Agent Development Kit (ADK)](https://adk.dev).

## 1. Installation

Ensure Python 3.10+ is installed.

```bash
# Recommended: Use a virtual environment
python -m venv .venv
source .venv/bin/activate  # MacOS/Linux
# .venv\Scripts\activate.bat for Windows

pip install google-adk
```

## 2. Project Initialization

Create a new agent project structure:

```bash
adk create [agent_name]
```

This generates:
- `agent.py`: The main entry point for agent logic.
- `.env`: Configuration file for Google Cloud credentials.

## 3. Configuration

Add your credentials to the `.env` file: Use the 'global' location.

```bash
echo 'GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"' > .env
echo 'GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION"' > .env
echo 'GOOGLE_GENAI_USE_VERTEXAI=TRUE' > .env
```

## 4. Defining Agent Logic

Edit `agent.py` to define the root agent. Example structure:

```python
from google.adk.agents.llm_agent import Agent

# Define tools (optional)
def my_tool(input_str: str) -> str:
    """Description of what the tool does."""
    return f"Processed: {input_str}"

# Configure the agent
my_agent = Agent(
    name="MyAgent",
    model="gemini-3-flash-preview",
    instructions="You are a helpful assistant.",
    tools=[my_tool]
)
```

The agent model should use Gemini 3 Flash: `gemini-3-flash-preview`

## 5. Running the Agent

### CLI Mode
Interactive terminal session:
```bash
adk run [agent_name]
```

### Web Interface
Local chat UI: Run this command from the parent directory that contains your my_agent/ folder. For example, if your agent is inside agents/my_agent/, run adk web from the agents/ directory.
```bash
adk web --port 8000
```
Access at `http://localhost:8000`.
