
# Google Agents with Vertex AI â€“ Tutorial (June 21, 2025)

A step-by-step guide for AI engineers to build, test, and deploy powerful AI agents using **Google Cloud's Agent Development Kit (ADK)** and **Vertex AI Agent Engine**.

---

## Part 1: Environment Setup

### 1.1 Create a Google Cloud Project
```bash
gcloud projects create ai-agent-dev
gcloud config set project ai-agent-dev
gcloud billing projects link ai-agent-dev --billing-account=XXXX
```

### 1.2 Enable Required APIs
```bash
gcloud services enable vertexai.googleapis.com iamcredentials.googleapis.com
```

### 1.3 Local Setup
```bash
gcloud auth application-default login
python3 -m venv venv && source venv/bin/activate
pip install google-adk
```

---

## Part 2: Clone Agent Garden Examples
```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python
```

Explore agents like:
- `academic-research`
- `customer-service`
- `multi-agent-weather`

---

## Part 3: Build a Simple Agent Locally

### 3.1 Code Example (`my_agent.py`)
```python
from adk import Agent, tool
import datetime, random

@tool
def get_weather(location: str) -> str:
    return f"{location}: {random.choice(['â˜€ï¸','ðŸŒ§ï¸','â›…'])}"

@tool
def now() -> str:
    return datetime.datetime.utcnow().isoformat()

my_agent = Agent(
    name="utility-bot",
    description="Time & weather helper",
    tools=[get_weather, now],
    model="gemini-1.5-flash"
)
```

### 3.2 Launch the Web UI
```bash
adk web --agent-file=my_agent.py
```

---

## Part 4: Orchestrate Multi-Agent Workflows

- Use a master agent to coordinate subtasks.
- Mix Gemini, GPT-4o, Claude via LiteLLM.
- Add Memory and Safety Callbacks.

ðŸ‘‰ See: `multi-agent-weather` in ADK samples.

---

## Part 5: Deploy to Vertex AI

### 5.1 CLI Deployment
```bash
gcloud ai agent-engines deploy   --agent-file=my_agent.py   --display-name="utility-bot-prod"   --location=us-central1
```

### 5.2 Python Deployment
```python
from vertexai import agent_engines
from my_agent import my_agent

deployed = agent_engines.deploy(
  agent=my_agent,
  project="ai-agent-dev",
  location="us-central1",
  display_name="utility-bot-prod"
)
print(deployed.endpoint)
```

---

## Part 6: IAM Permissions
```bash
gcloud projects add-iam-policy-binding ai-agent-dev   --member="serviceAccount:AGENT_SA_EMAIL"   --role="roles/secretmanager.secretAccessor"
```

---

## Part 7: Cost & Monitoring

| Resource | Rate (USD/hr) |
|----------|---------------|
| vCPU     | $0.0994       |
| RAM      | $0.0105/GiB   |

- Logs go to Cloud Logging.
- Metrics to Cloud Monitoring.
- Agents auto-scale to 0.

---

## Next Steps

- Browse Agent Garden templates
- Integrate LiteLLM for multi-model
- Use Gemini Code Assist to scaffold new tools
- Try `Agent2Agent` protocol for multi-agent collab

---

## Summary

Build scalable AI agents in days with Google Cloudâ€™s ADK + Vertex AI. Start local, grow to global.

> _Fork this guide, share improvements, and join the community building the future of intelligent agents!_