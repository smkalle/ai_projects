# Quickstart

## 1. Install uv

```bash
curl -Ls https://astral.sh/uv/install.sh | bash
source ~/.bashrc
uv --version
```

## 2. Setup environment

```bash
bash setup.sh
```

## 3. Run notebook

```bash
bash run.sh
```

## 4. Export to HTML

```bash
OUTPUT_FORMAT=html bash run.sh
```

## 5. Mounted filesystem fix

If your repo is under `/mnt/dev` or another mount that blocks symlinks:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/gpt55-notebook-tutorial
bash setup.sh
bash run.sh
```

## 6. Manual one-liner

```bash
UV_PROJECT_ENVIRONMENT=$HOME/.venvs/gpt55-notebook-tutorial \
uv run --locked jupyter nbconvert --execute --to notebook --inplace \
  gpt55_improvements_documented_python_notebook_tutorial.ipynb
```
