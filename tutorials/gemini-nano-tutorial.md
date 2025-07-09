
# 🚀 Comprehensive Tutorial: Using Gemini Nano in Chrome 138+ 
> Based on insights by [@swyx](https://x.com/swyx) and others  
> 📅 July 2025 | 🧠 On-device LLM | 🔒 Privacy-first

---

## 🧩 Introduction

**Gemini Nano**, a lightweight large language model (LLM), is now integrated into Chrome 138. It enables *on-device AI processing* for Chrome’s 3.7B monthly users — no server, no cloud, just local inference.

This hands-on tutorial guides you through:

- ✅ Enabling Gemini Nano in Chrome
- 🛠️ Setting up a dev environment
- 💬 Prompting Gemini via JavaScript
- 🧾 Generating structured JSON output
- 🔁 Creating stateless sessions
- 🖼️ (Optional) Using multimodal inputs (image/audio)
- 🔐 Addressing privacy & reliability concerns

---

## 📦 Prerequisites

- ✅ Chrome 138 or later (`chrome://version`)
- 🧠 Basic JavaScript
- 💻 Dev environment (e.g., VS Code)
- 🌐 Local server (`live-server`, `python -m http.server`, etc.)

---

## 🛠️ Step 1: Enable Gemini Nano in Chrome

1. Open `chrome://flags`
2. Search: `#prompt-api-for-gemini-nano`
3. Enable the flag → **Restart Chrome**
4. Visit `chrome://components`  
   If the model isn’t downloaded, it will auto-download (~1.5–2.4 GB).

> 💡 The model is quantized for ~4 GB VRAM and supports ~6k tokens.

---

## 📁 Step 2: Set Up Your Project

```bash
mkdir gemini-nano-demo
cd gemini-nano-demo
```

### `index.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gemini Nano Demo</title>
</head>
<body>
  <h1>Gemini Nano Demo</h1>
  <script type="module" src="script.js"></script>
</body>
</html>
```

### Start a Local Server

```bash
npm install -g live-server
live-server
```

---

## 🤖 Step 3: Basic Prompt to Gemini Nano

### `script.js`
```javascript
(async () => {
  try {
    const session = await LanguageModel.create({
      monitor(m) {
        m.addEventListener("downloadprogress", (e) => {
          console.log(`Download Progress: ${e.loaded * 100}%`);
        });
      }
    });

    const response = await session.prompt("Hello, what can you do?");
    console.log("Response:", response);
    document.body.innerHTML += `<p>Response: ${response}</p>`;
  } catch (error) {
    console.error("Error:", error);
  }
})();
```

> 🧪 Test in Chrome DevTools (F12). First run triggers model download.

---

## 🧾 Step 4: Generate Structured JSON Output

### Define a Schema
```javascript
const JSONSchema = `
<schema>
{
  "description": "Correctly extracted UserDetail",
  "name": "UserDetail",
  "parameters": {
    "properties": {
      "age": { "title": "Age", "type": "integer" },
      "name": { "title": "Name", "type": "string" }
    },
    "required": ["age", "name"],
    "type": "object"
  }
}
</schema>
`;
```

### Prompt with Schema
```javascript
const JSONSession = await LanguageModel.create({
  initialPrompts: [
    { role: 'system', content: `You are a helpful LLM that only responds in valid JSON: ${JSONSchema}` },
    { role: 'user', content: "Extract Jason is 35 years old" },
    { role: 'assistant', content: '{"age": 35, "name": "Jason"}' }
  ]
});

const result = await JSONSession.prompt("Extract Sarah is 22 years old");
console.log("Structured Output:", JSON.parse(result));
```

> ⚠️ Gemini Nano may sometimes omit required fields — validate output!

---

## 🔁 Step 5: Stateless Session Pattern

```javascript
const baseSession = await LanguageModel.create({
  initialPrompts: [
    { role: 'system', content: `You are a helpful LLM that only responds in valid JSON: ${JSONSchema}` }
  ]
});

const statelessSession = {
  async prompt(str) {
    const clone = await baseSession.clone();
    return clone.prompt(str);
  }
};

const result1 = await statelessSession.prompt("Extract Sarah is 22 years old");
const result2 = await statelessSession.prompt("Extract Tanisha is 30 years old");

console.log("Result 1:", JSON.parse(result1));
console.log("Result 2:", JSON.parse(result2));
```

> ✅ Avoids hidden context issues across prompts.

---

## 🖼️ Step 6: Multimodal Input (Experimental)

```javascript
const multimodalSession = await LanguageModel.create({
  monitor(m) {
    m.addEventListener("downloadprogress", (e) => {
      console.log(`Download Progress: ${e.loaded * 100}%`);
    });
  },
  expectedInputs: [{ type: "audio" }, { type: "image" }]
});

const imageBase64 = "data:image/png;base64,..."; // Replace this
const response = await multimodalSession.prompt(`Describe this image: ${imageBase64}`);
console.log("Image Description:", response);
```

> 🔬 Refer to [Chrome’s Prompt API docs](https://developer.chrome.com/docs/ai/prompt-api) for updates.

---

## 🔒 Step 7: Privacy & Reliability

### 🔐 Privacy
- No clear evidence of cloud transmission.
- Assume **local-only inference**.
- Use sandboxed browser profiles for sensitive tasks.

### ✅ Reliability
```javascript
function validateJSON(result, schema) {
  const parsed = JSON.parse(result);
  schema.required.forEach(field => {
    if (!(field in parsed)) console.warn(`Missing field: ${field}`);
  });
  return parsed;
}

const validated = validateJSON(result, { required: ["age", "name"] });
```

---

## ⚙️ Step 8: Testing & Optimization

- 🔄 Test ambiguous prompts (e.g., “Vibhu was 28 last year”)
- ⚡ Optimize prompt length — stay within 6k tokens
- 📦 Use wrappers like:
  ```html
  <script type="module" src="https://unpkg.com/simple-chromium-ai@0.1.1/dist/simple-chromium-ai.mjs"></script>
  ```

---

## ✅ Conclusion

This tutorial helps you leverage **Gemini Nano** in Chrome 138 for:

- Lightweight local inference
- JSON schema generation
- Stateless prompting
- Multimodal inputs (experimental)

---

## 📍 Next Steps

- Try multimodal experiments with audio or image
- Contribute wrappers or schema validators
- Follow `chrome://flags` for new AI feature releases

---

🧑‍💻 *Tutorial by a Google SDE3 AI Engineer*  
🔗 Feedback? PRs welcome!  
📬 [your-email@example.com]
