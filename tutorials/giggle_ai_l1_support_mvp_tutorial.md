
# AI L1 Support
*Updated: 2025-06-17*

---

## 1 🔍 What You’ll Build
This guided **Markdown notebook** shows how to stand‑up an **ADK‑powered multi‑agent L1 support pipeline** that glues together **PagerDuty → FastAPI (webhook) → Celery task queue → ADK agents**.  
It mirrors the repository layout but adds _why_ behind each step so you can follow along like an executable tutorial.

---

## 2 📁 Repository Anatomy

```text
giggle-ai-l1-support/
├── app/                    # All runtime code
│   ├── main.py             # FastAPI entrypoint
│   ├── webhooks.py         # PagerDuty listener → Celery task
│   ├── tasks.py            # Celery orchestration
│   ├── agents/             # ADK agents
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   ├── triage.py
│   │   ├── diagnostics.py
│   │   ├── resolution.py
│   │   └── escalation.py
│   └── utils/              # Logging + secrets
├── tests/                  # pytest unit/e2e
├── pyproject.toml          # Poetry deps & tooling
├── Dockerfile              # Prod container
└── README.md               # Quick reference
```

> **Tip:** Keep the *app* folder import‑root so you can `python -m app.main` locally without path hacks.

---

## 3 ⚙️ Prerequisites

| Tool            | Version tested |
|-----------------|----------------|
| Python          | `3.12`         |
| Poetry          | `1.8+`         |
| Redis (broker)  | `7.x`          |
| Docker / Podman | optional       |

Install deps:

```bash
poetry install
```

---

## 4 🚀 Run It Locally (Dev‑Mode)

### 4.1 Start API

```bash
uvicorn app.main:app --reload
```

Browse docs at [`http://localhost:8000/docs`](http://localhost:8000/docs).

### 4.2 Start Worker

```bash
celery -A app.tasks.celery_app worker -l info
```

The **FastAPI webhook** drops incidents onto Redis; **Celery** picks them up and kicks off the **OrchestratorAgent** chain.

---

## 5 🛰️ PagerDuty Webhook Setup

1. In PagerDuty → *Services* → *Integrations* → **Add v3 Webhook**  
2. Point to `https://YOUR_DOMAIN/webhook/pagerduty`  
3. Select _Trigger on Incident Created_ events.

The payload hits `/webhook/pagerduty`, where we extract:

```python
incident_id = payload["incident"]["id"]
summary      = payload["incident"]["trigger_summary_data"]["subject"]
service      = payload["incident"]["service"]["summary"]
```

…and enqueue `orchestrate_incident.delay(...)`.

---

## 6 🤖 Inside the Agents

Below is a minimal *triage* implementation to get you moving:

```python
# app/agents/triage.py
from transformers import pipeline
from .base import BaseAgent

class TriageAgent(BaseAgent):
    def __init__(self):
        super().__init__("triage")
        self.classifier = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )

    def classify(self, summary: str):
        result = self.classifier(summary, truncation=True)[0]
        return result["label"], result["score"]
```

> **Why sentiment?** It’s a placeholder—swap in a domain‑fine‑tuned classifier later.

The **Orchestrator** composes agents:

```python
resolved, meta = orchestrator.run()
```

If unresolved (`resolved == False`), the **EscalationAgent** uses `requests` to annotate the PagerDuty incident and post to Slack.

---

## 7 🧪 Test First

```bash
pytest -q
```

A starter test ensures the triage output shape:

```python
def test_classify():
    label, score = TriageAgent().classify("Database connection timeout")
    assert 0.0 < score <= 1.0
```

Add more e2e tests by **mocking** PagerDuty JSON and asserting Celery task completion.

---

## 8 🌐 Containerising

```dockerfile
FROM python:3.12-slim
WORKDIR /code
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && poetry install --no-dev
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Then:

```bash
docker build -t giggle-ai:mvp .
docker run -p 8000:8000 giggle-ai:mvp
```

Worker can live in a **second container** using the same image and command `celery -A app.tasks.celery_app worker -l info`.

---

## 9 📊 Observability Hooks (Stretch)

* **Structured logs** via `structlog`.
* **Prometheus FastAPI middleware** for request metrics.
* **OpenTelemetry** exporter from Celery to trace agent spans.

---

## 10 🔄 Next Steps

* Fine‑tune the classifier on historical incident tags.  
* Add **playbook registry** for the ResolutionAgent.  
* Terraform modules for Redis, ECS/Kubernetes, and PagerDuty resources.  
* Load‑test with [k6](https://k6.io) and autoscale workers.

---

Happy hacking – may your MTTR curve bend downwards 📉!
