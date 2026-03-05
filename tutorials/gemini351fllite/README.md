# Gemini 3.1 Flash-Lite Explorer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A CLI and Streamlit app to explore the full capabilities of Google's **Gemini 3.1 Flash-Lite** — their most cost-efficient model with thinking levels, multimodal support, and strong benchmarks.

Includes a **Medical Diagnostic Workbench** — an agentic workflow demo using [Google ADK](https://google.github.io/adk-docs/) that showcases SequentialAgent, ParallelAgent, LoopAgent, and LLM-based routing in a 5-stage diagnostic pipeline.

## Features

- **Interactive Chat** — Multi-turn streaming conversations
- **Thinking Levels** — Compare MINIMAL / LOW / MEDIUM / HIGH reasoning depth side-by-side
- **Vision** — Image analysis and description
- **Audio** — Transcription and summarization
- **Structured Output** — JSON generation with Pydantic schemas
- **Function Calling** — Tool use with automatic execution
- **Embeddings** — Text similarity via cosine distance
- **Benchmarks** — Latency and token usage across thinking levels
- **API Trace Log** — Full request/response logging to console
- **Medical Diagnostic Workbench** — Agentic multi-step reasoning with Google ADK (see below)

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/smkalle/gemini351fllite.git
cd gemini351fllite
./setup.sh

# 2. Add your API key
# Edit .env and set GEMINI_API_KEY
# Get a key at: https://aistudio.google.com/apikey

# 3. Run
./run_cli.sh chat              # Interactive CLI chat
./run_cli.sh --help            # See all commands
./run_app.sh                   # Launch Streamlit web app
./run_medical.sh               # Launch Medical Workbench (port 8502)
```

## CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `chat` | Interactive streaming chat | `./run_cli.sh chat --level high` |
| `think` | Compare thinking levels | `./run_cli.sh think "Explain entropy"` |
| `vision` | Analyze an image | `./run_cli.sh vision photo.jpg` |
| `audio` | Transcribe/summarize audio | `./run_cli.sh audio recording.mp3` |
| `json` | Structured JSON output | `./run_cli.sh json --prompt "A pasta recipe"` |
| `tools` | Function calling demo | `./run_cli.sh tools "Weather in Tokyo?"` |
| `embed` | Text similarity | `./run_cli.sh embed "cats" "kittens"` |
| `bench` | Benchmark thinking levels | `./run_cli.sh bench --rounds 3` |
| `medical diagnose` | Full diagnostic pipeline | `./run_cli.sh medical diagnose --case chest_pain` |
| `medical triage` | Quick triage classification | `./run_cli.sh medical triage "chest pain" --age 58 --sex male` |
| `medical analyze-image` | Medical image analysis | `./run_cli.sh medical analyze-image lesion.jpg` |
| `medical drug-check` | Drug interaction lookup | `./run_cli.sh medical drug-check warfarin aspirin` |

## Streamlit Apps

**Explorer** — Launch with `./run_app.sh` → http://localhost:8501

The sidebar provides navigation to all 8 capability pages. Each page includes configurable thinking levels and displays results with token usage.

**Medical Workbench** — Launch with `./run_medical.sh` → http://localhost:8502

A 3-page app demonstrating agentic AI diagnostics with live pipeline progress, sample patient cases, and stage-by-stage output visualization.

## Medical Diagnostic Workbench

> **EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE.**
> All outputs are AI-generated simulations using mock data.

An agentic diagnostic pipeline built with [Google ADK](https://google.github.io/adk-docs/) (`google-adk`) demonstrating how multi-agent orchestration composes with Gemini's multimodal reasoning.

### Architecture — 5-Stage Pipeline

```
MedicalPipeline (SequentialAgent)
├── Stage 1: TriageAgent (LlmAgent) — fast urgency classification
├── Stage 2: ConcurrentAnalysis (ParallelAgent)
│   ├── SymptomAnalysisAgent — symptom extraction + lab interpretation
│   └── ImagingAnalysisAgent — medical image analysis (vision)
├── Stage 3: DiagnosisRefinementLoop (LoopAgent, max 3 iterations)
│   ├── DiagnosisGeneratorAgent — ranked differential with ICD-10 codes
│   └── DiagnosisCriticAgent — confidence evaluation, loop exit control
├── Stage 4: SpecialistRouter (LlmAgent coordinator)
│   ├── CardiologyAgent
│   ├── DermatologyAgent
│   ├── PediatricsAgent
│   └── GeneralMedicineAgent
└── Stage 5: CaseSummaryAgent — SOAP-format case summary
```

### ADK Patterns Demonstrated

| Pattern | Agent | What It Shows |
|---------|-------|---------------|
| `SequentialAgent` | Outer pipeline | Ordered multi-step reasoning |
| `ParallelAgent` | Stage 2 | Concurrent independent analysis |
| `LoopAgent` | Stage 3 | Iterative refinement with exit condition |
| LLM-based routing | Stage 4 | Dynamic specialist selection |
| `output_key` + `{var}` | All stages | State propagation between agents |
| `ToolContext.actions.escalate` | Diagnosis critic | Programmatic loop exit |

### Gemini Capabilities Exercised

| Capability | Where |
|---|---|
| Vision | Stage 2: skin lesion / wound image analysis |
| Audio | Pre-pipeline: patient symptom transcription |
| Structured output | Pydantic schemas: TriageResult, DifferentialDiagnosis, CaseSummary |
| Function calling | Drug interactions, BMI, eGFR, ICD-10 lookup, risk scores |
| Thinking levels | LOW (triage) → MEDIUM (analysis) → HIGH (differential diagnosis) |
| Streaming | Stage 5: real-time case summary generation |

### Sample Cases

| Case | Triage | Specialist | Key Demo |
|------|--------|------------|----------|
| Chest Pain (58M) | EMERGENT | Cardiology | Red flags, TIMI score, drug interactions |
| Skin Lesion (42F) | SEMI-URGENT | Dermatology | Vision capability, ABCDE criteria |
| Pediatric Fever (4F) | URGENT | Pediatrics | Broad differential, 2+ loop iterations |
| Chronic Fatigue (35F) | NON-URGENT | General Medicine | HIGH thinking, 3 loop iterations |

### Mock Tools

All tools return synthetic data — no external APIs or databases.

- `lookup_drug_interaction(drug_a, drug_b)` — interaction severity and description
- `calculate_bmi(weight_kg, height_cm)` — BMI with category
- `calculate_egfr(creatinine, age, sex)` — kidney function estimate
- `lookup_icd_code(condition)` — ICD-10 code lookup
- `check_contraindication(medication, condition)` — safety check
- `calculate_risk_score(score_type, parameters)` — Wells PE, CHA2DS2-VASc, CURB-65, TIMI

## Project Structure

```
gemini_explorer/
  client.py          # Shared client, config helpers, API tracing
  examples.py        # Shared schemas, prompts, tools for explorer
  cli.py             # Click CLI with 8 commands + medical subgroup
  app.py             # Streamlit explorer app (8 pages)
  app_medical.py     # Streamlit medical workbench (3 pages)
  medical/
    __init__.py      # Package init + API key bridge
    schemas.py       # 5 Pydantic medical schemas
    tools.py         # 7 mock medical tools + red flag detection
    prompts.py       # 11 agent system prompts
    agents.py        # ADK pipeline: Sequential → Parallel → Loop → Router
    cases.py         # 4 sample patient cases
    cli_commands.py  # 4 Click medical subcommands
samples/             # Place test images/audio here
setup.sh             # Install dependencies
run_cli.sh           # Launch CLI
run_app.sh           # Launch Streamlit explorer
run_medical.sh       # Launch Medical Workbench
```

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (auto-installed by setup.sh)
- A [Gemini API key](https://aistudio.google.com/apikey)

### Dependencies

- `google-genai>=1.65.0` — Gemini API client
- `google-adk>=1.26.0` — Agent Development Kit
- `streamlit>=1.30.0` — Web UI framework
- `click>=8.1.0` — CLI framework
- `rich>=13.0.0` — Terminal formatting
- `pydantic>=2.0.0` — Data validation
- `pillow>=10.0.0` — Image handling

## License

[MIT](LICENSE)
