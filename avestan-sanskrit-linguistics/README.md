# Avestan–Vedic Sanskrit Comparative Linguistics

A data science pipeline for studying linguistic similarities and divergences between Avestan and Vedic Sanskrit using NLP, phonological modeling, and semantic analysis.

## Modules

| Module | Description |
|---|---|
| **Lexical** | Cognate detection via LexStat + multilingual embeddings |
| **Phonological** | Sound law mining (e.g., s→h shift) via ALINE alignment |
| **Semantic** | Drift analysis including the Asura/Daeva reversal |
| **Dashboard** | Streamlit interactive explorer |

## Quick Start

```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_data_exploration.ipynb
# or launch dashboard:
streamlit run app/dashboard.py
```

## Full Spec

See [SPEC.md](SPEC.md) for the complete project specification, methodology, data sources, and evaluation plan.
