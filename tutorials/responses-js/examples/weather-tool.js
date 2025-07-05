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