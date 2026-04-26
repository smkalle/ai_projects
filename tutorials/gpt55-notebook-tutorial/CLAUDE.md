# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a uv-native Jupyter notebook tutorial project for learning GPT-5.5 improvements, enterprise agent architecture implications, and deployment-safety controls. The entire project centers on a single documented notebook.

## Key Commands

```bash
# Install dependencies into $HOME/.venvs/gpt55-notebook-tutorial
bash setup.sh

# Execute the notebook in-place
bash run.sh

# Export notebook to HTML
OUTPUT_FORMAT=html bash run.sh

# Install optional papermill pipeline dependencies
uv sync --locked --extra pipeline

# Run with papermill for parameterized execution
uv run papermill gpt55_improvements_documented_python_notebook_tutorial.ipynb executed_gpt55_tutorial.ipynb
```

## Environment Setup

This project uses `uv` for Python package management. The virtual environment is created outside the project directory at `$HOME/.venvs/gpt55-notebook-tutorial` by default. This is intentional — it avoids symlink permission issues on mounted filesystems (e.g., `/mnt/dev`).

To override the environment location:
```bash
UV_PROJECT_ENVIRONMENT=/custom/path bash setup.sh
```

## Architecture

Single-notebook project with no complex architecture:
- Main artifact: `gpt55_improvements_documented_python_notebook_tutorial.ipynb`
- Dependencies defined in `pyproject.toml` (uv-native format with pip strict mode)
- Shell scripts (`setup.sh`, `run.sh`) orchestrate uv and nbconvert
