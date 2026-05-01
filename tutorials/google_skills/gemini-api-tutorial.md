# Gemini API Tutorial for Claude Code

A complete, hands-on guide to using the Gemini API via the Gen AI SDK on Agent Platform (formerly Vertex AI). Covers all capabilities — from simple text generation to live realtime streaming, video generation, and model fine-tuning.

> **Note:** Agent Platform was previously named "Vertex AI." Many docs still use the old branding — the API and SDK are identical.

---

## Prerequisites

### 1. Install the SDK

```bash
pip install google-genai
```

Or for other languages:
```bash
# JavaScript / TypeScript
npm install @google/genai

# Go
go get google.golang.org/genai

# C# / .NET
dotnet add package Google.GenAI

# Java (check Maven Central for latest version)
# build.gradle: implementation("com.google.genai:google-genai:VERSION")
```

### 2. Set Authentication

**Option A — Application Default Credentials (ADC):**
```bash
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='global'
export GOOGLE_GENAI_USE_VERTEXAI=true
```

**Option B — API Key (Express Mode):**
```bash
export GOOGLE_API_KEY='your-api-key'
export GOOGLE_GENAI_USE_VERTEXAI=true
```

### 3. Initialize the Client

```python
from google import genai
client = genai.Client()  # picks up env vars automatically
```

---

## Models Quick Reference

| Model | Best For |
|-------|---------|
| `gemini-3.1-pro-preview` | Complex reasoning, coding, research (1M token context) |
| `gemini-3-flash-preview` | Fast, balanced, multimodal (1M token context) |
| `gemini-3-pro-image-preview` | High-quality image generation and editing |
| `gemini-3.1-flash-image-preview` | Fast image generation and editing |
| `gemini-live-2.5-flash-native-audio` | Live Realtime API with native audio |

> Models like `gemini-2.0-*`, `gemini-1.5-*`, and `gemini-pro` are **legacy and deprecated**. Always use the new model IDs above.

---

## Table of Contents

1. [Text Generation](#1-text-generation)
2. [Chat (Multi-turn Conversations)](#2-chat-multi-turn-conversations)
3. [Streaming](#3-streaming)
4. [Multimodal Inputs](#4-multimodal-inputs)
5. [Structured Output (JSON)](#5-structured-output-json)
6. [Function Calling](#6-function-calling)
7. [Search Grounding](#7-search-grounding)
8. [Code Execution](#8-code-execution)
9. [Text Embeddings](#9-text-embeddings)
10. [Image Generation](#10-image-generation)
11. [Image Editing](#11-image-editing)
12. [Video Generation](#12-video-generation)
13. [Bounding Box Detection](#13-bounding-box-detection)
14. [Live Realtime API](#14-live-realtime-api)
15. [Content Caching](#15-content-caching)
16. [Batch Prediction](#16-batch-prediction)
17. [Thinking / Reasoning](#17-thinking--reasoning)
18. [Safety Settings](#18-safety-settings)
19. [Model Tuning (Fine-tuning)](#19-model-tuning-fine-tuning)
20. [MCP Integration](#20-mcp-integration)

---

## 1. Text Generation

The simplest use case — send a text prompt and get a text response.

**Python:**
```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain quantum computing in simple terms"
)
print(response.text)
```

**JavaScript / TypeScript:**
```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ vertexai: { project: "your-project-id", location: "global" } });
const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "Explain quantum computing in simple terms"
});
console.log(response.text);
```

**Go:**
```go
client, err := genai.NewClient(ctx, &genai.ClientConfig{
    Backend:  genai.BackendVertexAI,
    Project:  "your-project-id",
    Location: "global",
})
resp, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", genai.Text("Explain quantum computing"), nil)
fmt.Println(resp.Text)
```

---

## 2. Chat (Multi-turn Conversations)

Maintain conversation history across multiple turns.

```python
from google import genai
from google.genai import types

client = genai.Client()

chat_session = client.chats.create(
    model="gemini-3-flash-preview",
    history=[
        types.UserContent(parts=[types.Part.from_text(text="Hello")]),
        types.ModelContent(parts=[types.Part.from_text(text="Great to meet you. What would you like to know?")]),
    ],
)

response = chat_session.send_message("Tell me a story.")
print(response.text)

# Continue the conversation
response = chat_session.send_message("Make it a horror story.")
print(response.text)
```

---

## 3. Streaming

Get responses streamed token-by-token for faster perceived latency.

```python
from google import genai

client = genai.Client()
for chunk in client.models.generate_content_stream(
    model="gemini-3-flash-preview",
    contents="Tell me a 300-word story about a robot.",
):
    print(chunk.text, end="")
```

---

## 4. Multimodal Inputs

Process images, audio, and video alongside text. Supports both Google Cloud Storage URIs and local files.

**Image input:**
```python
from google import genai
from google.genai import types

client = genai.Client()

# From Cloud Storage
gcs_image = types.Part.from_uri(
    file_uri="gs://cloud-samples-data/generative-ai/image/scones.jpg",
    mime_type="image/jpeg"
)

# From a local file
with open("local_image.jpg", "rb") as f:
    local_image = types.Part.from_bytes(data=f.read(), mime_type="image/jpeg")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        "Describe what you see in both images.",
        gcs_image,
        local_image,
    ],
)
print(response.text)
```

**YouTube video input:**
```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        types.Part.from_uri(
            file_uri="https://www.youtube.com/watch?v=3KtWfp0UopM",
            mime_type="video/mp4",
        ),
        "Write a short blog post based on this video.",
    ],
)
print(response.text)
```

---

## 5. Structured Output (JSON)

Generate responses that conform to a specific JSON schema using Pydantic models or Python type hints.

```python
from google import genai
from google.genai import types
from pydantic import BaseModel

class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[str]

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="List 3 popular cookie recipes.",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=list[Recipe],
    ),
)

# Two ways to access the result:
print(response.text)         # raw JSON string
print(response.parsed)      # parsed Pydantic objects
for recipe in response.parsed:
    print(f"{recipe.recipe_name}: {recipe.ingredients}")
```

---

## 6. Function Calling

Let the model decide when to call external functions — ideal for building agents, RAG pipelines, and tool-augmented AI.

```python
from google import genai
from google.genai import types

def get_current_weather(location: str) -> str:
    """Get the current weather for a city."""
    if 'boston' in location.lower():
        return "Snowing, 28°F"
    return "Sunny, 72°F"

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What's the weather like in Boston?",
    config=types.GenerateContentConfig(tools=[get_current_weather]),
)

if response.function_calls:
    for function_call in response.function_calls:
        print(f"Calling: {function_call.name}")
        print(f"Args: {dict(function_call.args)}")
        # Execute the function
        result = get_current_weather(**function_call.args)
        print(f"Result: {result}")
else:
    print(response.text)
```

---

## 7. Search Grounding

Ground responses in live Google Search results or enterprise data to reduce hallucinations.

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="When is the next total solar eclipse in the US?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
    ),
)
print(response.text)

# Inspect grounding metadata
print(f"Search queries: {response.candidates[0].grounding_metadata.web_search_queries}")
print(f"Sources: {[site.web.title for site in response.candidates[0].grounding_metadata.grounding_chunks]}")
```

---

## 8. Code Execution

Let the model run Python code to compute precise answers.

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Calculate the 20th Fibonacci number.",
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())],
    ),
)

print(response.executable_code)           # the code the model wrote
print(response.code_execution_result)    # the computed result
```

---

## 9. Text Embeddings

Generate vector embeddings for semantic search, clustering, or similarity matching.

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=[
        "How do I get a driver's license?",
        "How long is my driver's license valid for?",
    ],
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",
        output_dimensionality=768
    ),
)
for embedding in response.embeddings:
    print(embedding.values[:5], "...")  # first 5 dimensions
```

---

## 10. Image Generation

Generate images from text prompts using the image generation models.

**Standard quality:**
```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A golden retriever reading a book on a rooftop at sunset",
)

for part in response.parts:
    if part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")
    elif part.text is not None:
        print(part.text)
```

**High resolution (with aspect ratio and size control):**
```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="A golden retriever reading a book on a rooftop at sunset",
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        )
    )
)
```

---

## 11. Image Editing

Use chat mode to iteratively edit an image — more natural than single-shot prompts.

```python
from google import genai
from PIL import Image

client = genai.Client()

# Step 1: Send the original image
chat = client.chats.create(model="gemini-2.5-flash-image")
image = Image.open("fruit.png")
response = chat.send_message([
    "Edit this image: make the bowl ceramic and blue",
    image
])

# Step 2: Iterate with more edits
response = chat.send_message("Make the bowl red")

# Step 3: Save the result
for part in response.candidates[0].content.parts:
    if part.inline_data is not None:
        part.as_image().save("edited_image.png")
```

---

## 12. Video Generation

Generate video from a text prompt (or starting image) using the Veo model.

> **Cost warning:** Veo can be expensive. Start with the fast model (`veo-3.1-fast-generate-001`) and upgrade to the larger model only if needed.

```python
import time
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()
image = Image.open("start_image.png")  # optional starting frame

# Video generation is async — returns an operation
operation = client.models.generate_videos(
    model="veo-3.1-fast-generate-001",
    prompt="a cat reading a book, cozy library setting",
    image=image,
    config=types.GenerateVideosConfig(
        person_generation="dont_allow",
        aspect_ratio="16:9",
        number_of_videos=1,
        duration_seconds=5,
        output_gcs_uri="gs://your-bucket/videos/",  # optional output bucket
    ),
)

# Poll until complete
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

if operation.response:
    print(operation.result.generated_videos[0].video.uri)
```

---

## 13. Bounding Box Detection

Detect and localize objects in images, returning normalized `[y_min, x_min, y_max, x_max]` coordinates.

```python
from google import genai
from google.genai.types import GenerateContentConfig, Part
from pydantic import BaseModel

class BoundingBox(BaseModel):
    box_2d: list[int]
    label: str

client = genai.Client()
config = GenerateContentConfig(
    system_instruction="Return bounding boxes as an array with labels. Limit to 25 objects.",
    response_mime_type="application/json",
    response_schema=list[BoundingBox],
)

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        Part.from_uri(file_uri="gs://cloud-samples-data/generative-ai/image/socks.jpg", mime_type="image/jpeg"),
        "Detect all objects and provide bounding boxes.",
    ],
    config=config,
)

for bbox in response.parsed:
    print(f"{bbox.label}: {bbox.box_2d}")

# Scale coordinates back to pixel space
def scale_box(box_2d, width, height):
    y_min, x_min, y_max, x_max = box_2d
    return [
        int(y_min / 1000 * height),
        int(x_min / 1000 * width),
        int(y_max / 1000 * height),
        int(x_max / 1000 * width),
    ]
```

**Coordinate system:**
- Format: `[y_min, x_min, y_max, x_max]`
- Range: integers `0` to `1000` (normalized)
- Origin: top-left corner

---

## 14. Live Realtime API

Bidirectional, low-latency streaming via WebSockets — ideal for voice and video assistants.

```python
import asyncio
from google import genai
from google.genai import types

async def generate_content():
    client = genai.Client()
    model_id = "gemini-live-2.5-flash-native-audio"

    config = types.LiveConnectConfig(
        response_modalities=[types.LiveModality.TEXT],  # or AUDIO for voice
    )

    async with client.aio.live.connect(model=model_id, config=config) as session:
        # Send a text message
        await session.send_client_content(
            turns=types.Content(
                role="user",
                parts=[types.Part.from_text(text="Hello, are you there?")]
        )

        # Receive streamed responses
        async for message in session.receive():
            if message.text:
                print(message.text, end="")

        # Send audio (16kHz PCM)
        # await session.send_realtime_input(
        #     media=Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
        # )

asyncio.run(generate_content())
```

---

## 15. Content Caching

Cache large documents (PDFs, codebases, transcripts) to dramatically reduce cost and latency on repeated queries.

```python
from google import genai
from google.genai import types

client = genai.Client()

# Create a cache from a large document
content_cache = client.caches.create(
    model="gemini-3-flash-preview",
    config=types.CreateCachedContentConfig(
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri="gs://your-bucket/large-document.pdf",
                        mime_type="application/pdf"
                    )
                ]
            )
        ],
        system_instruction="You are an expert researcher.",
        display_name="research-cache",
        ttl="86400s",  # 24 hours
    ),
)

# Use the cache — much cheaper for repeated queries
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Summarize the key findings in the document.",
    config=types.GenerateContentConfig(
        cached_content=content_cache.name
    ),
)
print(response.text)
```

---

## 16. Batch Prediction

Process large datasets asynchronously — submit a JSONL file of prompts and get results written to Cloud Storage.

**Input file format** (`gs://your-bucket/prompts.jsonl`):
```jsonl
{"contents": "Translate this to Spanish: Hello"}
{"contents": "Translate this to Spanish: Goodbye"}
{"contents": "Translate this to Spanish: Thank you"}
```

**Submit and monitor the job:**
```python
import time
from google import genai
from google.genai import types

client = genai.Client()

job = client.batches.create(
    model="gemini-3-flash-preview",
    src="gs://your-bucket/prompts.jsonl",
    config=types.CreateBatchJobConfig(dest="gs://your-bucket/outputs"),
)

completed_states = {
    types.JobState.JOB_STATE_SUCCEEDED,
    types.JobState.JOB_STATE_FAILED,
    types.JobState.JOB_STATE_CANCELLED,
}

while job.state not in completed_states:
    time.sleep(30)
    job = client.batches.get(name=job.name)

print(f"Batch job state: {job.state}")
if job.state == types.JobState.JOB_STATE_SUCCEEDED:
    print(f"Results: {job.metadata}")
```

---

## 17. Thinking / Reasoning

Control how deeply the model reasons before responding. Higher reasoning takes longer but produces more thoroughly vetted answers. On by default for `gemini-3.1-pro-preview`.

| Level | Use Case |
|-------|---------|
| `MINIMAL` | Low-complexity tasks, fast responses needed |
| `LOW` | Simple tasks, minimal reasoning benefit |
| `MEDIUM` | Moderate complexity, balanced reasoning |
| `HIGH` (default) | Complex research, coding, multi-step planning |

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="Design a distributed database that handles network partitions gracefully.",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.HIGH
        )
    )
)

# Access the model's reasoning steps
for part in response.candidates[0].content.parts:
    if part.thought:
        print(f"Reasoning: {part.text}")
    else:
        print(f"Final Answer: {part.text}")
```

---

## 18. Safety Settings

Adjust thresholds to block or allow certain content categories.

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Write a joke about a programmer.",
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
        ]
    ),
)

if response.text is None:
    print(f"Blocked. Reason: {response.candidates[0].finish_reason}")
else:
    print(response.text)

# Inspect per-category safety ratings
for rating in response.candidates[0].safety_ratings:
    print(f"  {rating.category}: blocked={rating.blocked}, prob={rating.probability}")
```

**Harm categories:** `HARM_CATEGORY_DANGEROUS_CONTENT`, `HARM_CATEGORY_HARASSMENT`, `HARM_CATEGORY_HATE_SPEECH`, `HARM_CATEGORY_SEXUALLY_EXPLICIT`

**Block thresholds:** `BLOCK_NONE`, `BLOCK_LOW_AND_ABOVE`, `BLOCK_MEDIUM_AND_ABOVE`, `BLOCK_ONLY_HIGH`, `BLOCK_HIGH_AND_ABOVE`

---

## 19. Model Tuning (Fine-tuning)

Fine-tune a base model on your own data using either Supervised Fine-Tuning (SFT) or Preference Tuning.

**Training data** (`gs://your-bucket/sft_train_data.jsonl`):
```jsonl
{"contents": "What is Python?", "answer": "Python is a high-level programming language."}
{"contents": "What is Go?", "answer": "Go is a statically typed compiled language by Google."}
```

**Submit and monitor a tuning job:**
```python
import time
from google import genai
from google.genai import types

client = genai.Client()

tuning_job = client.tunings.tune(
    base_model="gemini-3-flash-preview",
    training_dataset=types.TuningDataset(
        gcs_uri="gs://your-bucket/sft_train_data.jsonl"
    ),
    config=types.CreateTuningJobConfig(
        tuned_model_display_name="my-custom-model",
    ),
)

running_states = {"JOB_STATE_PENDING", "JOB_STATE_RUNNING"}
while tuning_job.state in running_states:
    time.sleep(60)
    tuning_job = client.tunings.get(name=tuning_job.name)

print("Tuned model endpoint:", tuning_job.tuned_model.endpoint)

# Use the tuned model
response = client.models.generate_content(
    model=tuning_job.tuned_model.endpoint,
    contents="What is Rust?",
)
print(response.text)
```

---

## 20. MCP Integration

Connect Gemini to local or remote Model Context Protocol (MCP) servers to extend capabilities with external tools.

```python
import asyncio
from datetime import datetime
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types

client = genai.Client()

async def run():
    # Connect to a local MCP server
    server_params = dict(command="npx", args=["-y", "@philschmid/weather-mcp"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            prompt = f"What is the weather in London on {datetime.now().strftime('%Y-%m-%d')}?"

            response = await client.aio.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[session],  # MCP session as a tool
                ),
            )
            print(response.text)

asyncio.run(run())
```

---

## Quick Reference: Common Patterns

| Task | Code Pattern |
|------|-------------|
| Simple text generation | `client.models.generate_content(model, contents)` |
| Multi-turn chat | `client.chats.create()` → `send_message()` |
| Streaming output | `client.models.generate_content_stream()` |
| Image input | `types.Part.from_uri()` or `types.Part.from_bytes()` |
| JSON output | `response_mime_type="application/json"`, `response_json_schema=` |
| Function calling | `tools=[my_function]` + check `response.function_calls` |
| Image generation | `model="gemini-2.5-flash-image"` |
| Video generation | `client.models.generate_videos()` |
| Text embeddings | `client.models.embed_content()` |
| Content caching | `client.caches.create()` + `cached_content=` |
| Code execution | `tools=[types.Tool(code_execution=...)]` |
| Live API | `client.aio.live.connect()` |
| Fine-tuning | `client.tunings.tune()` |

---

## Resources

- **Official docs:** https://docs.cloud.google.com/gemini-enterprise-agent-platform/overview
- **REST API reference:** https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest
- **Python samples:** https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/genai
