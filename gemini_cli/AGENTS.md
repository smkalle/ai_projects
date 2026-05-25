# Repository Guidelines

## Project Structure & Module Organization

- `infographic_agent/agent.py` defines the Google ADK agent and the top-level workflow tool.
- `infographic_agent/tools.py` contains scraping, image generation, evaluation, and logging helpers.
- `infographic_agent/.env` is for local secrets; do not commit real API keys.
- `skills/` and `.gemini/skills/` contain local skill documentation. Use these as built-in guidance for ADK and image-generation changes.
- `execution_log.txt` is generated runtime output.

Keep generated assets, logs, caches, and virtual environments out of source control.

## Build, Test, and Development Commands

Create and activate a virtual environment, then install runtime dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install google-adk google-genai requests beautifulsoup4 pillow python-dotenv
```

Run locally:

```bash
adk web                  # local ADK web UI
adk run infographic_agent # direct agent debugging
```

Check syntax:

```bash
python -m compileall infographic_agent
```

## Local Skill Guidance

Build changes from local `skills/*.md` guidance:

- `adk-agent-creator`: keep this as a Python 3.10+ Google ADK project. Define agents with `google.adk.agents.llm_agent.Agent`, document tools clearly, and prefer `gemini-3-flash-preview` for reasoning/evaluation.
- `nano-banana-image-gen`: use the `google-genai` SDK for image generation. The current generation model is `gemini-3.1-flash-image-preview`; request image output with `types.GenerateContentConfig(response_modalities=["IMAGE"])` and save image bytes from `part.inline_data`.

If skill files conflict with code, update both in the same change.

## Coding Style & Naming Conventions

Use standard Python 3 style with 4-space indentation, clear function names, and uppercase module constants such as `LOG_FILE`. Keep orchestration in `agent.py` and implementation details in `tools.py`. Use docstrings for public workflow/tool functions because ADK surfaces tool descriptions.

## Testing Guidelines

No formal test suite is present yet. When adding tests, create `tests/` and use `pytest`. Name files `test_<module>.py` and functions `test_<behavior>()`. Mock network calls, Gemini API calls, and file writes. Cover scraping errors, evaluation JSON cleanup, and workflow regeneration paths.

## Commit & Pull Request Guidelines

Recent commits use short imperative summaries such as `Add ...`, `Update ...`, and `Delete ...`. Keep that pattern: one concise subject line, with a body only when context is needed.

Pull requests should include a brief description, verification commands, required environment variables, and screenshots or generated sample output when image behavior changes. Link related issues when available.

## Security & Configuration Tips

Set `GEMINI_API_KEY` in the environment or a local `.env` file. Never hard-code secrets. Avoid committing generated logs, `.venv/`, `__pycache__/`, or generated image files.
