# Notebook Summary Analysis

## Executive Summary

The `notebooks/` folder contains a six-part progression from direct prompt engineering for generated media to agentic workflows that plan, generate, evaluate, and retry outputs. The sequence starts with Gemini image generation in `L_2.ipynb`, extends the pattern to Veo video generation in `L_3.ipynb`, then introduces evaluation techniques in `L_4.ipynb`. The later notebooks package those capabilities as Google ADK agents: `L_5.ipynb` builds a brand-aware image agent, `L_6.ipynb` builds a multi-scene video agent, and `L_8.ipynb` shows a prior infographic workflow that closely resembles the current repository's `infographic_agent` project.

The notebooks appear to be cleared or unexecuted: every notebook has zero stored output cells and zero executed code cells. This analysis therefore describes static notebook content only. It does not claim that any generated images, videos, scores, or agent runs were successfully produced.

## Per-Notebook Overview

| Notebook | Purpose | Key models | Notable techniques and tools | Artifacts referenced |
| --- | --- | --- | --- | --- |
| `L_2.ipynb` | Prompt engineering for image generation | `gemini-3-flash-preview`, `gemini-3.1-flash-image-preview` | Keyword-to-prompt expansion, reference-image conditioning, `types.GenerateContentConfig(response_modalities=["IMAGE"])` | `slide-template.png`, `slide-image.png` |
| `L_3.ipynb` | Prompt engineering for video generation | `gemini-3-flash-preview`, `gemini-3.1-flash-image-preview`, `veo-3.1-fast-generate-001` | Text-to-video, image-to-video, video prompt expansion, polling long-running operations | `original.mp4`, `video-image.png`, `enhanced.mp4` |
| `L_4.ipynb` | Evaluation methods for generated images | `gemini-3-flash-preview`, `gemini-3.1-flash-image-preview` | SigLIP image-text score, Gemini-as-judge JSON evaluation, Gecko rubric evaluation through Vertex AI evals | `misaligned_image.png` |
| `L_5.ipynb` | ADK image-generation agent | `gemini-3-flash-preview`, `gemini-3.1-flash-image-preview` | Tool-based brand analysis, concept generation, image generation, rubric-like evaluation, retry guidance | `guide.png`, `{id}_idea.png` |
| `L_6.ipynb` | ADK video agent | `gemini-3.1-pro-preview`, `gemini-3.1-flash-image-preview`, `veo-3.1-fast-generate-001` | Scene planning, reference-frame generation, image-to-video, video evaluation, ffmpeg concatenation | `scene_{n}_ref.png`, `scene_{n}.mp4`, `scenes.txt`, `rag_explainer.mp4` |
| `L_8.ipynb` | Prior infographic/media agent | `gemini-3-flash-preview`, `gemini-3.1-flash-image-preview` | Blog fetching, infographic generation, evaluation and regeneration loop, ADK `LlmAgent` | `infographic_*.png`, `infographic_agent.log` |

## Detailed Notebook Summaries

### `L_2.ipynb`: Image Prompt Engineering

`L_2.ipynb` introduces direct use of the `google-genai` client for image generation. It defines `IMAGE_MODEL_ID = "gemini-3.1-flash-image-preview"` and `TEXT_MODEL_ID = "gemini-3-flash-preview"`. The first generation uses a simple Pythagorean theorem prompt with a 16:9 aspect ratio. The notebook then shows prompt enhancement: keywords such as subject, action, location, camera control, lighting, and style are expanded by Gemini into a richer image prompt.

The most relevant pattern for this repository is the reference-image workflow. The notebook reads `slide-template.png`, passes it as `types.Part.from_bytes(...)`, and asks the image model to use it as a general style guide while generating `slide-image.png`. This is the same class of pattern used by brand-guided and infographic image generation: a text brief is strengthened by visual context, and image bytes are saved from `part.inline_data`.

### `L_3.ipynb`: Video Prompt Engineering

`L_3.ipynb` extends prompt engineering from still images to generated videos. It defines `VIDEO_MODEL_ID = "veo-3.1-fast-generate-001"` alongside the Gemini text and image models. The notebook first calls `client.models.generate_videos(...)`, polls the operation until completion, and writes `original.mp4` through `show_video`.

It then creates `video-image.png`, using the slide image from the previous lesson as visual reference. A second keyword-expansion flow asks `gemini-3-flash-preview` to synthesize subject, scene, style, camera angle, camera movement, sound effects, and dialogue into one video prompt. The final generation uses Veo's image-to-video path with `types.Image.from_file(location="video-image.png")`, producing `enhanced.mp4`.

### `L_4.ipynb`: Evaluation Techniques

`L_4.ipynb` focuses on evaluation rather than generation alone. It generates an aligned image from a reference prompt, loads a separate `misaligned_image.png`, and compares multiple scoring strategies.

The first evaluator is SigLIP. The notebook loads `google/siglip-base-patch16-224` through `transformers` and defines `compute_siglip_score(image, prompt)` to produce an image-text alignment score. The second evaluator is Gemini-as-judge: `gemini_evaluate(image, prompt)` sends image bytes plus an evaluation prompt to `gemini-3-flash-preview`, strips possible Markdown fencing, and parses JSON. The third evaluator uses Vertex AI evaluation APIs with Gecko text-to-image rubrics, building rows through helper functions such as `make_gecko_row` and calling `vtx_client.evals.generate_rubrics(...)` and `vtx_client.evals.evaluate(...)`.

For the current project, the important lesson is the combination of automated metrics and model-judged feedback. The notebook also teaches JSON cleanup, which matters when an agent decides whether to regenerate an infographic.

### `L_5.ipynb`: Image Generation Agent

`L_5.ipynb` turns image-generation steps into an ADK tool workflow. It defines four central tools: `brand_analysis`, `generate_design_concepts`, `generate_idea_image`, and `evaluate_image`.

`brand_analysis` reads a brand guideline image and asks `gemini-3-flash-preview` for structured JSON describing colors, typography, icon style, brand voice, and UI elements. `generate_design_concepts` combines a user description, the brand image, and extracted guidelines to produce structured UI concepts. `generate_idea_image` uses `gemini-3.1-flash-image-preview` to generate a branded UI mockup and save it as `{id}_idea.png`. `evaluate_image` compares the generated UI image against `guide.png`, scoring visual aesthetic, contrast, repetition, alignment, and proximity with a pass threshold.

The notebook then wires these tools into an ADK `Agent` with a prompt requiring brand analysis, concept generation, image generation, evaluation, and at most one retry. This is a direct precursor to the current repository's ADK structure: public tool functions with docstrings, a custom Gemini model wrapper, and a top-level agent.

### `L_6.ipynb`: Video Agent

`L_6.ipynb` applies the same agentic pattern to multi-scene video. It uses `MODEL = "gemini-3.1-pro-preview"` for planning, `IMAGE_MODEL = "gemini-3.1-flash-image-preview"` for reference frames, and `VIDEO_MODEL = "veo-3.1-fast-generate-001"`.

The key tools are `plan_scenes`, `generate_scene_image`, `generate_scene_video`, and `evaluate_scene`. `plan_scenes` converts a brief into a JSON array of scene plans, including visual description, narration script, and camera motion. `generate_scene_image` creates `scene_{scene_num}_ref.png` reference frames. `generate_scene_video` animates each frame into an 8-second clip with narration and a voice profile. `evaluate_scene` scores temporal consistency, motion coherence, prompt adherence, visual quality, narration alignment, voice profile, and continuity, returning structured JSON with failure type.

The final step writes a concat list and invokes ffmpeg to create `rag_explainer.mp4`, broadening the image-agent loop into planning, per-scene generation, quality control, and assembly.

### `L_8.ipynb`: Prior Infographic Agent

`L_8.ipynb` is the closest notebook to the current project. It defines `fetch_blog_content`, `generate_infographic`, `evaluate_infographic`, `infographic_workflow`, and `log_step`, then exposes `infographic_workflow` as the tool for an ADK `LlmAgent` named `InfographicAgent`.

The workflow fetches a blog URL with `requests`, truncates raw HTML/text to 5,000 characters, generates an infographic with `gemini-3.1-flash-image-preview`, evaluates it with `gemini-3-flash-preview` for factual accuracy, spelling, and aesthetics, and retries up to three times. It logs progress to `infographic_agent.log` and saves timestamped `infographic_*.png` files.

This notebook appears to be an earlier single-notebook version of the current repository's agent design. The repository has since separated orchestration into `infographic_agent/agent.py` and implementation details into `infographic_agent/tools.py`, which is a cleaner maintainable structure than the notebook's monolithic code cell.

## Cross-Notebook Themes and Progression

The sequence repeatedly uses a generate-evaluate-improve pattern. `L_2` and `L_3` show how prompt quality and reference media affect output quality. `L_4` introduces evaluators that can convert subjective quality into structured scores or feedback. `L_5`, `L_6`, and `L_8` package those ideas as tools available to ADK agents.

Another theme is increasingly structured output. Early notebooks display generated media directly, while later notebooks request JSON schemas, parse model responses, and use pass/fail thresholds. This shift is important because agents need machine-readable tool outputs to make retry decisions.

The notebooks also show a consistent model split: Gemini Flash text models are used for prompt expansion and judging, Gemini image models are used for image bytes, Gemini Pro appears for more complex scene planning in `L_6`, and Veo is used only for video generation.

## Relevance to the Current ADK Infographic Agent

The current project should be understood as a productionized version of the `L_8` concept, informed by the evaluation and media-generation lessons in the earlier notebooks. The named tools in the repository, including `fetch_blog_content`, `generate_infographic`, `evaluate_infographic`, and `infographic_workflow`, align with the notebook's workflow. The local project guidance also matches notebook practice: keep ADK orchestration in `agent.py`, place implementation details in `tools.py`, use `gemini-3-flash-preview` for reasoning/evaluation, and use `gemini-3.1-flash-image-preview` for image generation with `response_modalities=["IMAGE"]`.

The strongest improvement path suggested by the notebooks is to make evaluation more structured. `L_8` returns `"PASS"` or free-form feedback, while `L_4` and `L_5` demonstrate JSON scoring and threshold-based decisions. Moving the infographic evaluator toward a schema with factuality, spelling, visual hierarchy, source coverage, and overall pass/fail would make regeneration more reliable.

## Risks, Gaps, and Opportunities

Because the notebooks have no stored outputs, there is no evidence of successful execution, generated asset quality, or actual evaluation scores. Future validation should run representative examples with real credentials.

Several notebook techniques are intentionally simple for teaching. `L_8` fetches raw response text rather than parsing article content with BeautifulSoup, which can include navigation, scripts, and unrelated page text. The current project can improve this with stronger extraction and length controls. The evaluation loops also depend on model judgment, so they should clean JSON responses defensively, handle API failures, and log enough context for diagnosis without storing secrets.

Finally, generated artifacts and logs should remain outside source control. The notebooks reference many runtime files, including PNGs, MP4s, concat text files, and logs. The repository guidance already calls this out, and the current agent should keep that boundary clear.
