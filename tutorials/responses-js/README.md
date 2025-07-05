# responses.js Tutorial

A hands‑on guide for AI engineers to spin up and extend **[responses.js](https://github.com/huggingface/responses.js)** – a lightweight Express.js server that implements the OpenAI Responses API on top of **Hugging Face Inference Providers**.

---

## ✨ Why use responses.js?

* **Vendor‑neutral**: call 100+ OSS & commercial models from one endpoint.  
* **Stateless & lightweight**: drop‑in replacement for OpenAI chat endpoints without DB baggage.  
* **Multi‑modal**: text, images, and JSON tools in one pipeline.  
* **Streaming & function calling**: perfect for real‑time UX and agent tooling.

---

## 🗂 Project Layout

```
responses-js-tutorial/
├── README.md                ← this guide
├── examples/
│   ├── getting-started.js   ← single‑prompt text generation
│   └── weather-tool.js      ← demo of function‑calling
├── .env.example             ← copy ➜ `.env` and add your HF_TOKEN
└── package.json
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/huggingface/responses.js.git
cd responses.js      # upstream repo
pnpm install         # or npm install
pnpm dev             # launches http://localhost:3000
```

1. **Copy env**  
   `cp ../responses-js-tutorial/.env.example demo/.env` and paste your Hugging Face token.

2. **Run a sample**  
   ```bash
   cd ../responses-js-tutorial/examples
   node getting-started.js
   ```

---

## 🧑‍💻 Example 1 – Hello LLM

```js
// examples/getting-started.js
import { HfInference } from "@huggingface/inference";
import "dotenv/config";

const hf = new HfInference(process.env.HF_TOKEN);

const main = async () => {
  const res = await hf.textGeneration({
    model: "HuggingFaceH4/zephyr-7b-beta",
    inputs: "Tell me a fun fact about space elevators.",
  });
  console.log(res.generated_text);
};

main();
```

---

## 🔌 Example 2 – Function Calling (Weather Bot)

```js
// examples/weather-tool.js
import { HfInference } from "@huggingface/inference";
import fetch from "node-fetch";
import "dotenv/config";

const hf = new HfInference(process.env.HF_TOKEN);

async function getWeather(city) {
  const resp = await fetch(`https://wttr.in/${city}?format=j1`);
  const data = await resp.json();
  return `The temperature in ${city} is ${data.current_condition[0].temp_C}°C`;
}

(async () => {
  const completion = await hf.chatCompletion({
    model: "mistralai/Mixtral-8x7B-Instruct-v0.1",
    messages: [
      { role: "user", content: "What's the weather in Tokyo?" }
    ],
    functions: [
      {
        name: "getWeather",
        description: "Return current weather for a city",
        parameters: {
          type: "object",
          properties: { city: { type: "string" } },
          required: ["city"]
        }
      }
    ]
  });

  const fc = completion.choices[0].message.function_call;
  if (fc) {
    const result = await getWeather(JSON.parse(fc.arguments).city);
    console.log("⛅", result);
  }
})();
```

---

## 🏗 Next Steps

* **Multi‑modal**: try `pnpm run example image` for VQA with `vilt-b32-finetuned-vqa`.
* **Structured output**: `pnpm run example structured_output`.
* **Deploy**: `docker build . && docker run -p 3000:3000 responses.js`.
* **Scale**: point to Hugging Face Inference Endpoints or your own GPU pods.

---

## 📝 License

This tutorial is MIT like the upstream project. Pull requests welcome!