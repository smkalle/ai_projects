import os
import json
from datetime import datetime, timezone
from pathlib import Path

import PIL.Image
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
load_dotenv(Path(__file__).with_name(".env"))

LOG_FILE = "execution_log.txt"
OUTPUT_DIR = Path("generated_infographics")
IMAGE_MODEL = "gemini-3.1-flash-image-preview"
EVALUATION_MODEL = "gemini-3-flash-preview"
REQUEST_TIMEOUT_MS = 60_000


def log_step(message: str) -> None:
    """Append a timestamped workflow step to the local execution log."""
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)


def _create_client() -> genai.Client:
    """Create a Gemini client from local environment configuration."""
    http_options = types.HttpOptions(timeout=REQUEST_TIMEOUT_MS)
    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
    if use_vertex:
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
        if not project:
            raise RuntimeError("Set GOOGLE_CLOUD_PROJECT when GOOGLE_GENAI_USE_VERTEXAI=true.")
        return genai.Client(
            vertexai=True,
            project=project,
            location=location,
            http_options=http_options,
        )

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY before running the agent.")
    return genai.Client(api_key=api_key, http_options=http_options)


def scrape_blog(url: str) -> str:
    """Scrape a blog post URL and return extracted text for infographic generation."""
    log_step(f"Step: Scraping blog URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else "No Title"
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text(" ", strip=True) for p in paragraphs[:16])
        if not content.strip():
            log_step("Error: No paragraph content found in blog response.")
            return "Error scraping blog: no paragraph content found."

        extracted_text = f"Title: {title}\nContent: {content}"
        log_step(f"Success: Extracted content from {url}")
        return extracted_text
    except Exception as e:
        log_step(f"Error: Failed to scrape {url}: {str(e)}")
        return f"Error scraping blog: {str(e)}"


def generate_infographic(prompt_summary: str, feedback: str | None = None, attempt: int = 1) -> str:
    """Generate an infographic with Nano Banana, optionally applying evaluator feedback."""
    log_step(f"Step: Generating infographic using Nano Banana. Attempt {attempt}.")
    client = _create_client()

    full_prompt = f"""
Create a high-quality infographic from the blog content below.

Requirements:
- Preserve factual claims from the source content.
- Use concise, correctly spelled labels.
- Make the layout visually professional and suitable for a blog summary.
- Avoid inventing statistics, dates, names, or claims not present in the source.

Blog content:
---
{prompt_summary}
---
"""
    if feedback:
        log_step(f"Applying feedback for regeneration: {feedback}")
        full_prompt += f"\n\nPlease address this feedback from the previous attempt: {feedback}"

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
        )

        if not response.candidates or not response.candidates[0].content.parts:
            log_step(f"Error: No candidates or parts in response. Response: {response}")
            return "Error: No image generated (Empty response)."

        OUTPUT_DIR.mkdir(exist_ok=True)
        image_path = OUTPUT_DIR / f"infographic_attempt_{attempt}.png"
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with open(image_path, "wb") as f:
                    f.write(part.inline_data.data)
                log_step(f"Success: Infographic saved to {image_path}")
                return str(image_path)

        log_step("Error: No image data found in response.")
        return "Error: No image generated."
    except Exception as e:
        log_step(f"Error: Image generation failed: {str(e)}")
        return f"Error generating image: {str(e)}"


def evaluate_infographic(image_path: str, original_summary: str) -> str:
    """Evaluate the infographic for accuracy, spelling, and aesthetic alignment."""
    log_step(f"Step: Evaluating infographic at {image_path}")
    client = _create_client()

    try:
        img = PIL.Image.open(image_path)

        evaluation_prompt = f"""
        Evaluate this infographic based on the original content summary:
        ---
        {original_summary}
        ---
        Evaluate three criteria:
        1. Factual accuracy: does it preserve the source claims without invention?
        2. Spelling: are all visible words spelled correctly?
        3. Aesthetic alignment: is the layout professional and suitable for the blog content?
        
        Respond ONLY with a JSON object:
        {{
            "passed": true/false,
            "feedback": "detailed feedback if failed, or 'Excellent' if passed"
        }}
        """

        response = client.models.generate_content(
            model=EVALUATION_MODEL,
            contents=[img, evaluation_prompt]
        )

        eval_result = response.text.strip()
        if "```json" in eval_result:
            eval_result = eval_result.split("```json")[1].split("```")[0].strip()
        elif "```" in eval_result:
            eval_result = eval_result.split("```")[1].split("```")[0].strip()

        log_step(f"Evaluation complete: {eval_result}")
        return eval_result
    except Exception as e:
        log_step(f"Error: Evaluation failed: {str(e)}")
        return json.dumps({"passed": False, "feedback": f"Evaluation error: {str(e)}"})
