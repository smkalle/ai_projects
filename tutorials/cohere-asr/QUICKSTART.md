# Quick Start

Get the Medical Researcher Workbench running in under 5 minutes.

---

## Prerequisites

- Python 3.10 or 3.11
- Git
- (Recommended) GPU with 8GB+ VRAM — works on CPU too

---

## Step 1 — Clone and Enter the Project

```bash
git clone <repo-url>
cd medical-workbench
```

---

## Step 2 — Install Dependencies

```bash
./setup.sh
```

This runs `uv sync` to install all Python packages and creates a `.env` file from the template.

---

## Step 3 — Configure (Optional)

The workbench works out-of-the-box in **local mode** (no API key needed).

If you want to use a different transcription backend, edit `.env`:

```env
# Default: local transformers (no API key)
TRANSCRIPTION_MODE=local

# Optional: Cohere API (zero GPU required)
# TRANSCRIPTION_MODE=api
# COHERE_API_KEY=your-key-here

# Optional: vLLM self-hosted (high throughput)
# TRANSCRIPTION_MODE=vllm
# VLLM_BASE_URL=http://localhost:8000
```

---

## Step 4 — Launch

```bash
./run.sh
```

Open your browser at [http://localhost:8501](http://localhost:8501).

---

## Step 5 — Your First Transcription

### Single File

1. Click **Transcription** in the sidebar
2. Drag a `.wav`, `.mp3`, or `.m4a` file onto the uploader
3. Select the **language** from the dropdown (default: English)
4. Toggle **punctuation** on or off
5. Click **Transcribe** — wait for the result
6. Click **Save to Library** to persist it

### Live Microphone

1. Click **Live Stream** in the sidebar
2. Select your **language**
3. Click **Start Recording** — speak into your microphone
4. Watch the transcript appear in real time
5. Click **Stop Recording** when done
6. Save or export the result

### Batch (Multiple Files)

1. Click **Transcription** in the sidebar
2. Switch to the **Batch** tab
3. Drag multiple audio files onto the queue
4. Set the language for each file
5. Click **Run All** — progress shows per-file status
6. Click **Download All (ZIP)** when done

---

## Step 6 — Benchmark Your Audio

1. Click **Benchmarking** in the sidebar
2. Upload an **audio file** (the file under test)
3. Upload a **reference transcript** (the ground-truth .txt)
4. Select the **language**
5. Click **Run Benchmark** — WER and RTFx are displayed

---

## Step 7 — Library & Export

1. Click **Library** to see all saved transcripts
2. Search by keyword or filter by tag
3. Click a transcript to edit, retag, or export
4. **Export as .txt** for raw transcript
5. **Export as PDF** to include metadata and formatting

---

## Common Issues

| Problem | Solution |
|---------|----------|
| `CUDA out of memory` | Set `DEVICE=cpu` in `.env` or use half-precision (`torch_dtype=torch.float16`) |
| `ModuleNotFoundError` | Run `./setup.sh` again to ensure all packages are installed |
| No audio input detected | Check that your microphone is set as the default input device |
| Transcripts are empty | Verify the audio file is not encoded with a unsupported codec — re-encode as 16kHz mono wav |
| API mode fails | Confirm your `COHERE_API_KEY` is correct and has available credits |
