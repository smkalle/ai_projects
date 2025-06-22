# MCP‑Powered Audio Analysis Toolkit ☕️

> **TL;DR** – Spin up your own Model Context Protocol (MCP) server that wraps AssemblyAI’s speech‑to‑text + audio‑intelligence APIs and plug it straight into Claude Desktop (or any MCP‑capable host). Optional Streamlit UI included. Tested on Python 3.10.

---

## Table of Contents
1. [Features](#features)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Step‑by‑Step Guide](#step-by-step-guide)
    * [1 · Create the Audio Analyzer](#1-create-the-audio-analyzer)
    * [2 · Build the MCP Server](#2-build-the-mcp-server)
    * [3 · Connect from Claude Desktop](#3-connect-from-claude-desktop)
    * [4 · (Opt) Streamlit UI](#4-opt-streamlit-ui)
8. [Testing & Debugging](#testing--debugging)
9. [Production Deployment](#production-deployment)
10. [FAQ](#faq)
11. [Contributing](#contributing)
12. [License](#license)
13. [References](#references)

---

## Features<a id="features"></a>

* **Transcription** – High‑accuracy speech‑to‑text via AssemblyAI  
* **Audio Intelligence** – Sentiment, topics, summarization, speaker labels  
* **RAG‑over‑Audio** – Query transcripts with your favourite LLM  
* **MCP first‑class** – Exposes a single `analyze_audio` tool over MCP  
* **CLI / Claude / Streamlit** – Choose your interface  
* **Batteries‑included** – `.env`, Dockerfile, Gunicorn/Nginx recipe  

_Pour yourself a coffee and let’s build._ ☕️

---

## Architecture<a id="architecture"></a>

```text
┌──────────┐    HTTP+JSON     ┌──────────────┐
│Streamlit │ ───────────────▶ │  MCP Server  │
│   UI     │                  │  (FastMCP)   │
└──────────┘                  │  analyze_audio
        ▲                     └─────┬────────┘
        │           HTTPS REST       │
        │                            ▼
  User  │                     ┌─────────────┐
        ├────────────────────▶│ AssemblyAI  │
        │     audio file      │  API        │
        ▼                     └─────────────┘
┌────────────────────────────────────────────┐
│              Claude Desktop                │
│   (MCP client → analyze_audio tool)        │
└────────────────────────────────────────────┘
```

---

## Quick Start<a id="quick-start"></a>

```bash
# 1. clone & install
git clone https://github.com/your‑org/mcp-audio-toolkit.git
cd mcp-audio-toolkit
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. configure
cp .env.example .env            # paste your AssemblyAI key inside

# 3. run the server (stdio transport)
python audio_analysis_mcp.py

# 4. hook it up in Claude Desktop → Settings → Developer → Edit Config
#    mcp_servers = ["http://localhost:3333"]   # example

# 5. ask Claude:
#    “Use analyze_audio on <public‑audio‑url> and summarise.” ✅
```

---

## Prerequisites<a id="prerequisites"></a>

* Python ≥ 3.10  
* AssemblyAI account – get a free API key [here](https://www.assemblyai.com)  
* (Optional) Claude Desktop or any MCP‑compliant host  
* (Optional) Streamlit if you want the web UI  
* Unix‑like shell (commands use Bash)

---

## Installation<a id="installation"></a>

```bash
pip install fastmcp assemblyai streamlit python-dotenv rich
```

Add _extras_ for dev:

```bash
pip install black isort pre-commit
```

---

## Configuration<a id="configuration"></a>

Create `.env`:

```dotenv
ASSEMBLYAI_API_KEY=✨your_secret_key✨
```

Never commit secrets – `.gitignore` already excludes `.env`.

---

## Step‑by‑Step Guide<a id="step-by-step-guide"></a>

### 1 · Create the Audio Analyzer<a id="1-create-the-audio-analyzer"></a>

`audio_analysis_tools.py`

```python
import os
import assemblyai as aai

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def transcribe_and_analyze(audio_url: str) -> dict:
    \"\"\"Return transcript + insights for a remote or local audio file.\"\"\"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(
        audio_url,
        sentiment_analysis=True,
        summarize=True,
        topics=True,
        speaker_labels=True,
    )
    return {
        "transcript": transcript.text,
        "sentiment": transcript.sentiment_analysis,
        "summary": transcript.summary,
        "topics": transcript.topics,
        "speaker_labels": transcript.speaker_labels,
    }
```

### 2 · Build the MCP Server<a id="2-build-the-mcp-server"></a>

`audio_analysis_mcp.py`

```python
from fastmcp import FastMCP
from audio_analysis_tools import transcribe_and_analyze

mcp = FastMCP("audio_analysis")

@mcp.tool
def analyze_audio(audio_url: str) -> dict:
    \"\"\"Transcribe + analyse an audio file via AssemblyAI.\"\"\"
    return transcribe_and_analyze(audio_url)

if __name__ == "__main__":
    # stdio transport works great for Claude Desktop
    mcp.run(transport="stdio")
```

Run it:

```bash
python audio_analysis_mcp.py
```

### 3 · Connect from Claude Desktop<a id="3-connect-from-claude-desktop"></a>

1. **Settings → Developer → Edit Config**  
2. Append your server:

```toml
[mcp_servers]
audio_analysis = "http://localhost:3333"
```

3. Save & restart Claude.  
4. Look for the 🛠️ icon → choose **analyze_audio**.

### 4 · (Opt) Streamlit UI<a id="4-opt-streamlit-ui"></a>

`audio_analysis_ui.py`

```python
import streamlit as st
from audio_analysis_tools import transcribe_and_analyze

st.title("☕️ Audio Analysis Toolkit")

file = st.file_uploader("Upload audio", type=("wav", "mp3", "m4a"))
if file:
    with open("temp_audio", "wb") as f:
        f.write(file.read())
    res = transcribe_and_analyze("temp_audio")
    st.json(res)
```

```bash
streamlit run audio_analysis_ui.py
```

---

## Testing & Debugging<a id="testing--debugging"></a>

* **Unit tests** – `pytest tests/`
* **Server health** – `curl -X POST localhost:3333 -d '{"audio_url": "..."}'`
* **Common gotchas**  
  * 401? Check `ASSEMBLYAI_API_KEY`  
  * Large files? Use AssemblyAI’s async upload helper  

---

## Production Deployment<a id="production-deployment"></a>

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "audio_analysis_mcp.py"]
```

```bash
docker build -t mcp-audio .
docker run -p 3333:3333 --env-file .env mcp-audio
```

### Gunicorn + Nginx (Bare‑Metal)

See `docs/deploy_nginx.md` for a step‑by‑step recipe.

### Scaling on AWS

* Put the container behind an **Application Load Balancer**  
* Use an **Auto Scaling Group** with health checks  
* Store secrets in **AWS Secrets Manager**

---

## FAQ<a id="faq"></a>

| Question | Answer |
|----------|--------|
| Does it support local files? | Yes — pass the file path instead of a URL. |
| How much does AssemblyAI cost? | Free tier → 5 hrs/mo; then pay‑as‑you‑go. |
| Can I add language detection? | Enable `language_detection=True` in the config. |

---

## Contributing<a id="contributing"></a>

1. Fork ➜ create feature branch ➜ PR  
2. Run **pre‑commit** & unit tests  
3. ☕️ Describe your change clearly

---

## License<a id="license"></a>

MIT © 2025

---

## References<a id="references"></a>

| Resource | Link |
|----------|------|
| AssemblyAI Speech‑to‑Text API | https://www.assemblyai.com/docs |
| FastMCP | https://github.com/jlowin/fastmcp |
| MCP Specification | https://modelcontextprotocol.io/spec |
| AssemblyAI Python SDK | https://github.com/AssemblyAI/assemblyai-python-sdk |
| Streamlit | https://streamlit.io |
| Claude Desktop MCP Config | (see docs) |
