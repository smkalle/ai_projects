# GenAI Processors: A Practical Hands‑On Tutorial
> Build modular, asynchronous AI pipelines with Google DeepMind’s **GenAI Processors** (released **10 Jul 2025**).

---

## Why GenAI Processors?
GenAI Processors wraps *Python `asyncio`* around a unified **Processor ↔ ProcessorPart** abstraction.  
It lets you:

| Goal | How GenAI Processors Helps |
|------|---------------------------|
| Reduce latency / TTFT | Concurrent execution of pipeline stages |
| Handle multimodal data | A single stream of `ProcessorPart` objects |
| Re‑use & test components | Chain (`+`) or branch (`//`) processors |
| Go from idea to live agent fast | Ready‑made `GenaiModel` & `LiveProcessor` for Gemini API |

---

## 1 · Prerequisites
* Python ≥ 3.10
* A Google Cloud project with **Gemini API** enabled (for live examples)
* A *virtualenv* (recommended):

```bash
python -m venv .venv && source .venv/bin/activate
```

---

## 2 · Installation

```bash
pip install --upgrade pip
pip install genai-processors   # v1.0.3 at the time of writing
```

---

## 3 · Quickstart: “Hello Gemini”

```python
from genai_processors.core import genai_model
from genai_processors import content_api, streams

pipeline = genai_model.GenaiModel(model_name="gemini-2.0-flash")

inp = content_api.from_text("Hello, Gemini Processors!")
out_stream = await pipeline(inp)

async for part in out_stream:
    print(part.text)
```

Save as **quickstart.py** and run:

```bash
python -m asyncio quickstart.py
```

---

## 4 · Core Concepts

### 4.1 Processor / PartProcessor
```python
from genai_processors import processor

@processor.PartProcessor
async def uppercase(part):
    if part.text:
        part.text = part.text.upper()
    return part
```
* A **Processor** accepts / returns **async streams** of `ProcessorPart`.
* Chain processors with **`+`** (serial) or **`//`** (parallel).

### 4.2 ProcessorPart
```python
from genai_processors import content_api
img_part  = content_api.from_image("cat.png", mime_type="image/png")
text_part = content_api.from_text("meow")
```
Metadata (MIME type, role, custom attrs) travels with every part.

### 4.3 Streams & Concurrency
```python
from genai_processors import streams
parts = streams.stream_content(["Hello", "world"])
```
The library schedules downstream processors *concurrently* whenever their
dependencies are ready, minimising **Time‑To‑First‑Token**.

---

## 5 · Building Pipelines Step‑by‑Step

### 5.1 Example 1 – Uppercase → Gemini

```python
text_pipeline = uppercase + genai_model.GenaiModel("gemini-2.0-pro")

inp = content_api.from_text("Synchronous code is so 2024.")
async for part in text_pipeline(inp):
    print(part.text)          # => Synchronous code is so 2024. (Gemini reply)
```

### 5.2 Example 2 – Live Audio + Video Agent

```python
from genai_processors.core import audio_io, video, live_model

cam_mic   = video.VideoIn() + audio_io.PyAudioIn()
speaker   = audio_io.PyAudioOut()
live_llm  = live_model.LiveProcessor(model_name="gemini-2.0-pro")

live_agent = cam_mic + live_llm + speaker

async for part in live_agent(streams.endless_stream()):
    # e.g. print live transcription tokens
    if part.text:
        print(part.text)
```

### 5.3 Example 3 – Custom JSON ProcessorPart

```python
@processor.PartProcessor
async def sentiment_json(part):
    if part.text:
        score = 1 if "🙂" in part.text else -1
        yield content_api.from_json({"sentiment": score})
```

---

## 6 · Testing & Debugging

```python
import pytest, asyncio, types

@pytest.mark.asyncio
async def test_uppercase():
    from genai_processors import content_api, streams
    from tutorial.upper import uppercase
    s = streams.stream_content(["abc"])
    out = [p async for p in uppercase(s)]
    assert out[0].text == "ABC"
```

* Use **`pytest-asyncio`** for coroutine tests.
* Use the **`streams.preview()`** helper to peek at parts without consuming them.

---

## 7 · Performance Tips

| Tip | Explanation |
|-----|-------------|
| Keep processors *pure* | Avoid global state; easier to parallelise |
| Chunk large inputs | Emit smaller `ProcessorPart`s to start downstream work sooner |
| Prefer `LiveProcessor` | Streams tokens as they’re produced |
| Profile with `asyncio.run(debug=True, …)` | Enables built‑in slow‑task detector |

---

## 8 · Deployment (Docker + Cloud Run)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir genai-processors
CMD ["python", "-m", "uvicorn", "app:router", "--host=0.0.0.0", "--port=8080"]
```

> Deploy with  
> `gcloud run deploy genai-pipeline --source=. --region=us-central1`

---

## 9 · Contributing

1. Fork <https://github.com/google-gemini/genai-processors>.
2. Add your processor under **`contrib/`**.
3. Run `make test && make lint`.
4. Open a PR – follow the **CLA** and style guide in `CONTRIBUTING.md`.

---

## 10 · Further Reading
* Official blog – *“Announcing GenAI Processors”*  
*Colab notebooks* (Content API, Processor Intro, Live API)  
*Examples directory* (Real‑Time Live, Research Agent, Live Commentary)

---

© 2025 The GenAI Processors authors · Apache‑2.0  
Pull requests welcome!
