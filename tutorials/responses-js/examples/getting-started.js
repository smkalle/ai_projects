import { HfInference } from "@huggingface/inference";
import "dotenv/config";

const hf = new HfInference(process.env.HF_TOKEN);

(async () => {
  const res = await hf.textGeneration({
    model: "HuggingFaceH4/zephyr-7b-beta",
    inputs: "Hello from responses.js tutorial!"
  });
  console.log(res.generated_text);
})();