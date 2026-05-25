# Infographic Agent

The Infographic Agent is a Python-based project that leverages Google's Agent Development Kit (ADK) and Gemini models to automate the creation of infographics from blog posts.

## Project Overview

This application provides an end-to-end workflow to:
1.  **Scrape** content from a provided blog post URL.
2.  **Generate** an infographic based on the scraped content using **Nano Banana** (`gemini-3.1-flash-image-preview`).
3.  **Evaluate** the generated image for factual accuracy, spelling, and professional layout using **Gemini 1.5** (`gemini-3-flash-preview`).
4.  **Regenerate** the infographic once if the evaluation fails, incorporating specific feedback.

### Key Technologies
- **Google ADK**: Agent and workflow orchestration.
- **Google GenAI SDK**: Interface for Gemini 1.5 and Nano Banana models.
- **Streamlit**: Web-based admin console for configuration and execution.
- **BeautifulSoup4**: HTML parsing for blog scraping.

## Project Structure

- `admin_console.py`: A Streamlit interface to configure API keys, run workflows, view logs, and see generated images.
- `infographic_agent/agent.py`: Defines the `infographic_agent` using ADK's `Agent` class and the core `create_infographic_workflow`.
- `infographic_agent/tools.py`: Contains the low-level implementations for `scrape_blog`, `generate_infographic`, and `evaluate_infographic`.
- `skills/`: Local instructional context for specific tasks (e.g., image generation details).
- `generated_infographics/`: Directory where output images are stored.
- `execution_log.txt`: Runtime logs for workflow steps.

## Building and Running

### Environment Setup

1.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure API Keys:
    Set `GEMINI_API_KEY` in a `.env` file or exported in your shell.

### Execution Commands

- **Run Admin Console (Recommended)**:
  ```bash
  streamlit run admin_console.py
  ```
- **Run Agent via ADK CLI**:
  ```bash
  adk run infographic_agent
  ```
- **Run ADK Web UI**:
  ```bash
  adk web
  ```

## Development Conventions

- **Orchestration vs. Implementation**: Keep high-level workflow logic in `agent.py` and detailed tool implementations in `tools.py`.
- **Image Generation**: Always use the `google-genai` SDK with `response_modalities=["IMAGE"]` for Nano Banana.
- **Error Handling**: Tools should return "Error: [message]" strings or raise descriptive exceptions for the workflow to handle.
- **Logging**: Use `log_step` in `tools.py` to ensure consistency in `execution_log.txt`.
- **Testing**: While no formal test suite exists yet, use `pytest` for new tests and mock all external API calls.
- **Commit Style**: Use short imperative summaries (e.g., "Add scraping logic", "Fix evaluation parser").
