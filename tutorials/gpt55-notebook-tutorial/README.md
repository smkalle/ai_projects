# GPT-5.5 Improvements — Documented Notebook Tutorial

A GitHub-ready, **uv-native** Jupyter notebook project for learning and presenting GPT-5.5 improvements, enterprise agent architecture implications, and deployment-safety controls.

## What is included

- `gpt55_improvements_documented_python_notebook_tutorial.ipynb` — main documented notebook
- `pyproject.toml` — uv-native dependency definition
- `uv.lock` — pinned lockfile for reproducible installs
- `setup.sh` — creates/syncs a uv environment
- `run.sh` — executes the notebook from CLI
- `.env.example` — optional environment settings
- `QUICKSTART.md` — short command reference

## Prerequisites

Install `uv`:

```bash
curl -Ls https://astral.sh/uv/install.sh | bash
source ~/.bashrc
uv --version
```

## Setup

```bash
bash setup.sh
```

By default, `setup.sh` creates the environment outside the project at:

```bash
$HOME/.venvs/gpt55-notebook-tutorial
```

This avoids symlink permission issues on mounted folders such as `/mnt/dev`.

To override:

```bash
UV_PROJECT_ENVIRONMENT=/some/other/path bash setup.sh
```

## Run the notebook from CLI

```bash
bash run.sh
```

This executes the notebook in place using:

```bash
uv run jupyter nbconvert --execute --to notebook --inplace gpt55_improvements_documented_python_notebook_tutorial.ipynb
```

## Generate an HTML report

```bash
OUTPUT_FORMAT=html bash run.sh
```

## Run without setup

```bash
UV_PROJECT_ENVIRONMENT=$HOME/.venvs/gpt55-notebook-tutorial \
uv run --locked jupyter nbconvert --execute --to notebook --inplace \
  gpt55_improvements_documented_python_notebook_tutorial.ipynb
```

## Optional: Papermill pipeline mode

Install optional pipeline dependencies:

```bash
uv sync --locked --extra pipeline
```

Run with Papermill:

```bash
uv run papermill \
  gpt55_improvements_documented_python_notebook_tutorial.ipynb \
  executed_gpt55_tutorial.ipynb
```

## Recommended GitHub workflow

```bash
git init
git add .
git commit -m "Add uv-native GPT-5.5 notebook tutorial"
```

## Notes for Termux / proot / mounted filesystems

If you see errors like:

```text
Permission denied: 'lib' -> '.venv/lib64'
```

keep the uv environment outside the mounted project directory:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/gpt55-notebook-tutorial
bash setup.sh
bash run.sh
```
