"""Streamlit app demonstrating Gemini 3.1 Flash-Lite capabilities."""

import json
import sys
import time
from pathlib import Path

# Ensure package is importable when run directly by streamlit
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from google.genai import types
from PIL import Image
from pydantic import BaseModel

from gemini_explorer.client import (
    EMBED_MODEL,
    MODEL,
    THINKING_LEVELS,
    extract_response_parts,
    get_client,
    get_usage,
    make_config,
    trace_log,
    traced_embed,
    traced_generate,
    traced_generate_stream,
)


def render_trace_log():
    """Render the API trace log panel in the sidebar."""
    st.sidebar.divider()
    st.sidebar.subheader("📡 API Trace Log")
    if st.sidebar.button("Clear log", key="clear_trace"):
        trace_log.clear()
        st.rerun()

    if not trace_log.entries:
        st.sidebar.caption("No API calls yet.")
        return

    for i, entry in enumerate(reversed(trace_log.entries)):
        status_icon = {"ok": "✅", "pending": "⏳", "error": "❌"}.get(entry["status"], "✅")
        if "streamed" in str(entry.get("status", "")):
            status_icon = "🌊"

        header = f'{status_icon} `{entry["method"]}` — {entry["duration_ms"]}ms' if entry["duration_ms"] else f'{status_icon} `{entry["method"]}` — pending'

        with st.sidebar.expander(header, expanded=(i == 0)):
            st.caption(f'⏰ {entry["timestamp"]}')
            st.code(f'model: {entry["model"]}', language=None)

            if entry["config"]:
                st.markdown("**Config:**")
                st.json(entry["config"])

            st.markdown("**Contents:**")
            st.code(entry["contents"], language=None)

            if entry["usage"]:
                st.markdown("**Usage:**")
                u = entry["usage"]
                st.code(
                    f'input: {u.get("input_tokens", "?")}  '
                    f'output: {u.get("output_tokens", "?")}  '
                    f'think: {u.get("thoughts_tokens", "?")}  '
                    f'total: {u.get("total_tokens", "?")}',
                    language=None,
                )

            if entry["response_summary"]:
                st.markdown("**Response preview:**")
                st.text(entry["response_summary"][:300])

            if entry["error"]:
                st.error(entry["error"])

st.set_page_config(page_title="Gemini 3.1 Flash-Lite Explorer", page_icon="⚡", layout="wide")


@st.cache_resource
def init_client():
    return get_client()


# ── Sidebar Navigation ──────────────────────────────────────────────────────

st.sidebar.title("⚡ Gemini Explorer")
st.sidebar.caption(f"Model: `{MODEL}`")

page = st.sidebar.radio(
    "Navigate",
    [
        "Chat",
        "Vision",
        "Audio",
        "Structured Output",
        "Function Calling",
        "Thinking Levels",
        "Embeddings",
        "Benchmarks",
    ],
)

# ── Chat Page ────────────────────────────────────────────────────────────────

if page == "Chat":
    st.header("💬 Chat")

    col1, col2 = st.columns([3, 1])
    with col2:
        level = st.selectbox("Thinking level", list(THINKING_LEVELS), index=2)
        system_msg = st.text_input("System instruction", "You are a helpful assistant.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client = init_client()
        contents = []
        for msg in st.session_state.chat_history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

        config = make_config(thinking_level=level, system_instruction=system_msg)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_text = ""
            for chunk in traced_generate_stream(client, MODEL, contents, config):
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)

        st.session_state.chat_history.append({"role": "assistant", "content": full_text})

# ── Vision Page ──────────────────────────────────────────────────────────────

elif page == "Vision":
    st.header("🖼️ Vision")

    col1, col2 = st.columns([2, 1])
    with col2:
        level = st.selectbox("Thinking level", list(THINKING_LEVELS), index=2, key="vision_level")
        prompt = st.text_area("Prompt", "Describe this image in detail. What do you observe?")

    with col1:
        upload = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp", "gif"])
        camera = st.camera_input("Or take a photo")

    image_source = upload or camera
    if image_source:
        img = Image.open(image_source)
        st.image(img, caption="Input image", use_container_width=True)

        if st.button("Analyze Image", type="primary"):
            client = init_client()
            config = make_config(thinking_level=level)

            with st.spinner("Analyzing..."):
                response = traced_generate(client, MODEL, [img, prompt], config)

            thoughts, answer = extract_response_parts(response)
            if thoughts:
                with st.expander("💭 Model thoughts"):
                    st.text(thoughts)
            st.markdown(answer)
            usage = get_usage(response)
            st.caption(f"Tokens: {usage['total_tokens']} (thoughts: {usage['thoughts_tokens']})")

# ── Audio Page ───────────────────────────────────────────────────────────────

elif page == "Audio":
    st.header("🎵 Audio")

    col1, col2 = st.columns([2, 1])
    with col2:
        level = st.selectbox("Thinking level", list(THINKING_LEVELS), index=2, key="audio_level")
        prompt = st.text_area("Prompt", "Transcribe this audio. Then provide a summary.", key="audio_prompt")

    with col1:
        upload = st.file_uploader("Upload audio", type=["mp3", "wav", "ogg", "flac"])

    if upload:
        st.audio(upload)
        if st.button("Process Audio", type="primary"):
            client = init_client()
            config = make_config(thinking_level=level)

            mime_map = {"mp3": "audio/mp3", "wav": "audio/wav", "ogg": "audio/ogg", "flac": "audio/flac"}
            ext = upload.name.rsplit(".", 1)[-1].lower()
            mime = mime_map.get(ext, "audio/mp3")

            audio_bytes = upload.read()
            with st.spinner("Processing audio..."):
                response = traced_generate(client, MODEL, [types.Part.from_bytes(data=audio_bytes, mime_type=mime), prompt], config)

            thoughts, answer = extract_response_parts(response)
            if thoughts:
                with st.expander("💭 Model thoughts"):
                    st.text(thoughts)
            st.markdown(answer)

# ── Structured Output Page ───────────────────────────────────────────────────

elif page == "Structured Output":
    st.header("📋 Structured Output")

    class Recipe(BaseModel):
        name: str
        cuisine: str
        prep_time_minutes: int
        ingredients: list[str]
        steps: list[str]
        difficulty: str

    class MovieReview(BaseModel):
        title: str
        year: int
        rating: float
        genre: str
        summary: str
        pros: list[str]
        cons: list[str]

    class CodeAnalysis(BaseModel):
        language: str
        purpose: str
        complexity: str
        functions: list[str]
        suggestions: list[str]

    schemas = {
        "Recipe": Recipe,
        "Movie Review": MovieReview,
        "Code Analysis": CodeAnalysis,
    }

    col1, col2 = st.columns([2, 1])
    with col2:
        level = st.selectbox("Thinking level", list(THINKING_LEVELS), index=2, key="json_level")
        schema_name = st.selectbox("Schema", list(schemas))

    selected_schema = schemas[schema_name]
    st.code(json.dumps(selected_schema.model_json_schema(), indent=2), language="json")

    default_prompts = {
        "Recipe": "Create a creative fusion recipe combining Thai and Italian cuisine.",
        "Movie Review": "Write a review for a fictional sci-fi movie set in 2150.",
        "Code Analysis": "Analyze this code:\ndef fib(n): return n if n<2 else fib(n-1)+fib(n-2)",
    }

    prompt = st.text_area("Prompt", default_prompts[schema_name], key="json_prompt")

    if st.button("Generate", type="primary"):
        client = init_client()
        config = make_config(thinking_level=level, json_schema=selected_schema.model_json_schema())

        with st.spinner("Generating structured output..."):
            response = traced_generate(client, MODEL, prompt, config)

        result = selected_schema.model_validate_json(response.text)
        st.json(result.model_dump())

# ── Function Calling Page ────────────────────────────────────────────────────

elif page == "Function Calling":
    st.header("🔧 Function Calling")

    st.info("The model can call Python functions as tools. Try queries that need weather or math.")

    def get_weather(city: str) -> str:
        """Get the current weather for a city."""
        data = {
            "tokyo": "22°C, partly cloudy, humidity 65%",
            "new york": "18°C, sunny, humidity 45%",
            "london": "14°C, rainy, humidity 80%",
            "paris": "16°C, overcast, humidity 70%",
            "sydney": "26°C, clear skies, humidity 55%",
        }
        return data.get(city.lower(), f"No weather data for {city}. Available: {', '.join(data)}")

    def calculate(expression: str) -> str:
        """Evaluate a math expression. Supports basic arithmetic (+, -, *, /, %)."""
        allowed = set("0123456789+-*/.() %")
        if not all(c in allowed for c in expression):
            return "Error: invalid characters"
        try:
            return str(eval(expression))  # noqa: S307
        except Exception as e:
            return f"Error: {e}"

    col1, col2 = st.columns([3, 1])
    with col2:
        level = st.selectbox("Thinking level", list(THINKING_LEVELS), index=2, key="tools_level")

    with col1:
        st.markdown("**Available tools:** `get_weather(city)`, `calculate(expression)`")
        query = st.text_input(
            "Query",
            "What's the weather in Tokyo and Paris? Also, what's 18% tip on a $127.50 bill?",
        )

    if st.button("Run", type="primary"):
        client = init_client()
        config = make_config(thinking_level=level, tools=[get_weather, calculate])

        with st.spinner("Calling tools..."):
            response = traced_generate(client, MODEL, query, config)

        st.markdown(response.text)
        usage = get_usage(response)
        st.caption(f"Tokens: {usage['total_tokens']}")

# ── Thinking Levels Page ─────────────────────────────────────────────────────

elif page == "Thinking Levels":
    st.header("🧠 Thinking Levels Comparison")

    prompt = st.text_area(
        "Prompt",
        "A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left?",
    )
    selected_levels = st.multiselect(
        "Levels to compare",
        list(THINKING_LEVELS),
        default=["minimal", "low", "medium", "high"],
    )

    if st.button("Compare", type="primary") and selected_levels:
        client = init_client()
        cols = st.columns(len(selected_levels))

        for i, level in enumerate(selected_levels):
            with cols[i]:
                st.subheader(f"**{level.upper()}**")
                config = make_config(thinking_level=level)

                start = time.time()
                with st.spinner(f"{level}..."):
                    response = traced_generate(client, MODEL, prompt, config)
                elapsed = time.time() - start

                thoughts, answer = extract_response_parts(response)
                usage = get_usage(response)

                st.markdown(answer)
                if thoughts:
                    with st.expander("💭 Thoughts"):
                        st.text(thoughts)
                st.caption(
                    f"⏱ {elapsed:.1f}s | 🧠 {usage['thoughts_tokens']} think tokens | "
                    f"📊 {usage['total_tokens']} total"
                )

# ── Embeddings Page ──────────────────────────────────────────────────────────

elif page == "Embeddings":
    st.header("📐 Embeddings & Similarity")

    col1, col2 = st.columns(2)
    with col1:
        text1 = st.text_area("Text A", "The cat sat on the mat.", key="emb1")
    with col2:
        text2 = st.text_area("Text B", "A kitten was sitting on a rug.", key="emb2")

    if st.button("Compute Similarity", type="primary"):
        client = init_client()

        with st.spinner("Computing embeddings..."):
            result = traced_embed(
                client, EMBED_MODEL, [text1, text2],
                config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
            )

        vec1 = result.embeddings[0].values
        vec2 = result.embeddings[1].values
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        similarity = dot / (norm1 * norm2) if norm1 and norm2 else 0.0

        st.metric("Cosine Similarity", f"{similarity:.4f}")
        st.progress(max(0.0, min(1.0, similarity)))
        st.caption(f"Embedding dimensions: {len(vec1)}")

        with st.expander("Raw vectors (first 20 dims)"):
            st.json({"text_a": vec1[:20], "text_b": vec2[:20]})

# ── Benchmarks Page ──────────────────────────────────────────────────────────

elif page == "Benchmarks":
    st.header("📊 Benchmarks")

    prompt = st.text_area("Test prompt", "Explain the concept of entropy in information theory.", key="bench_prompt")
    rounds = st.slider("Rounds per level", 1, 5, 1)

    if st.button("Run Benchmark", type="primary"):
        client = init_client()
        results = []

        progress = st.progress(0)
        total = len(THINKING_LEVELS) * rounds

        step = 0
        for level_name in THINKING_LEVELS:
            config = make_config(thinking_level=level_name)
            times = []
            last_usage = {}

            for r in range(rounds):
                start = time.time()
                response = traced_generate(client, MODEL, prompt, config)
                times.append(time.time() - start)
                last_usage = get_usage(response)
                step += 1
                progress.progress(step / total)

            results.append({
                "Level": level_name,
                "Avg Time (s)": round(sum(times) / len(times), 2),
                "Input Tokens": last_usage.get("input_tokens", 0),
                "Output Tokens": last_usage.get("output_tokens", 0),
                "Think Tokens": last_usage.get("thoughts_tokens", 0),
                "Total Tokens": last_usage.get("total_tokens", 0),
            })

        progress.empty()
        st.dataframe(results, use_container_width=True)

        # Chart
        import pandas as pd

        df = pd.DataFrame(results)
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df.set_index("Level")["Avg Time (s)"])
        with col2:
            st.bar_chart(df.set_index("Level")["Think Tokens"])

# ── Trace Log Panel (always rendered) ────────────────────────────────────────

render_trace_log()
