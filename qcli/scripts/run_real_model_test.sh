#!/usr/bin/env bash
set -euo pipefail

MODEL_ID="${1:-Qwen/Qwen3.5-2B}"
DEVICE="${DEVICE:-auto}"
DTYPE="${DTYPE:-auto}"
QUANTIZED="${QUANTIZED:-none}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-48}"
INSTALL_DEPS="${INSTALL_DEPS:-0}"
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"
export MODEL_ID DEVICE DTYPE QUANTIZED MAX_NEW_TOKENS

if [[ "$INSTALL_DEPS" == "1" ]]; then
  uv venv --allow-existing
  uv sync --no-install-project
fi

uv run python - <<'PY'
import os
import time

from qcli.engine import EngineOptions, LocalHFEngine

model_id = os.environ.get("MODEL_ID", "Qwen/Qwen3.5-2B")
device = os.environ.get("DEVICE", "auto")
dtype = os.environ.get("DTYPE", "auto")
quantized = os.environ.get("QUANTIZED", "none")
max_new_tokens = int(os.environ.get("MAX_NEW_TOKENS", "48"))

messages = [
    {"role": "system", "content": "You are concise."},
    {"role": "user", "content": "In one short sentence, what is Linux?"},
]

start = time.time()
engine = LocalHFEngine(
    EngineOptions(
        model_id=model_id,
        device=device,
        dtype=dtype,
        quantized=quantized,
        trust_remote_code=False,
    )
)
loaded_s = time.time() - start

start = time.time()
out = engine.generate_text(
    messages,
    temperature=0.2,
    top_p=0.9,
    max_new_tokens=max_new_tokens,
)
gen_s = time.time() - start

clean = out.strip()
if not clean:
    raise SystemExit("FAIL: model returned empty output")

print("PASS: real model inference succeeded")
print(f"MODEL: {model_id}")
print(f"DEVICE: {engine.device}")
print(f"LOAD_SECONDS: {loaded_s:.2f}")
print(f"GEN_SECONDS: {gen_s:.2f}")
print("OUTPUT:", clean.replace("\n", " ")[:400])
PY
