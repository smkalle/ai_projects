---
name: nano-banana-image-gen
description: Use Nano Banana (Gemini 3.1 Flash Image) with the Google Gen AI SDK on Google Cloud. Use this for high-speed image generation and conversational image editing tasks.
---

# Nano Banana with Gen AI SDK on Google Cloud

This skill provides the essential workflow for using **Nano Banana** (Gemini 3.1 Flash Image) and its successors via the `google-genai` SDK on Google Cloud.

## 1. Installation

```bash
pip install -U google-genai
```

## 2. Initialization (Google Cloud)

To use Nano Banana on Google Cloud, initialize the client with `vertexai=True`.

```python
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True, 
    project="YOUR_PROJECT_ID", 
    location="global"
)
```

## 3. Image Generation (Text-to-Image)

Use `gemini-3.1-flash-image-preview` for high-speed generation.

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="A futuristic neon city at night, synthwave style",
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
    )
)

# Extract and save the image
for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("output.png", "wb") as f:
            f.write(part.inline_data.data)
```

## 4. Conversational Image Editing

Nano Banana allows modifying existing images by providing the image and a text instruction.

```python
import PIL.Image

ref_image = PIL.Image.open("input_photo.jpg")

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=[
        ref_image,
        "Change the sky to a dramatic lightning storm"
    ],
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
    )
)
```

## Model Reference
- **Nano Banana:** `gemini-2.5-flash-image` (Speed-optimized)
- **Nano Banana 2:** `gemini-3.1-flash-image-preview` (Fidelity-optimized)
- **Nano Banana Pro:** `gemini-3-pro-image-preview` (Complex reasoning)
- **Gemini:** `gemini-3-flash-preview` (Image analysis)
