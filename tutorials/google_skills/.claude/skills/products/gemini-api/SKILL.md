---
name: gemini-api
description: Use the Google Gemini API for generative AI tasks. Use when asked to call the Gemini API, generate text or images with Gemini, set up API keys for Gemini, configure model parameters (temperature, max tokens, safety settings), or use the Vertex AI Gemini endpoint.
when_to_use: Calls to Gemini API, generating content with Gemini models, setting up Gemini authentication, Vertex AI Gemini endpoints
---

# Gemini API Skill

Use this skill when working with the Google Gemini API (via `generativelanguage.googleapis.com` or Vertex AI).

## Setup

### API Key (Direct API)

```bash
export GEMINI_API_KEY="your-api-key"
```

### Vertex AI (Recommended for production)

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT
```

## API Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/MODEL:generateContent?key=${GEMINI_API_KEY}
```

Available models: `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.5-pro-preview`

## Request Format

```json
{
  "contents": [{
    "role": "user",
    "parts": [{ "text": "Your prompt here" }]
  }],
  "generationConfig": {
    "temperature": 0.9,
    "maxOutputTokens": 2048,
    "topP": 0.95,
    "topK": 40
  },
  "safetySettings": [
    { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE" }
  ]
}
```

## cURL Example

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Explain Google Cloud Run in one sentence"}]}],
    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 256}
  }'
```

## Safety Categories

| Category | Description |
|----------|-------------|
| `HARM_CATEGORY_HATE_SPEECH` | Hate speech and slurs |
| `HARM_CATEGORY_DANGEROUS_CONTENT` | Dangerous or violent content |
| `HARM_CATEGORY_SEXUALLY_EXPLICIT` | Sexually explicit content |
| `HARM_CATEGORY_HARASSMENT` | Harassment |

## Common Tasks

- **Text generation**: `generateContent` with text parts
- **Multi-turn chat**: `chat` endpoint with conversation history
- **Vision**: Pass base64-encoded images in `inlineData` parts
- **Streaming**: Use `streamGenerateContent` for lower latency
