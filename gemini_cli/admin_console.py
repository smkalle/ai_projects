import os
from pathlib import Path

import streamlit as st

from infographic_agent.agent import create_infographic_workflow
from infographic_agent.tools import LOG_FILE, OUTPUT_DIR


def read_log() -> str:
    log_path = Path(LOG_FILE)
    if not log_path.exists():
        return "No log entries yet."
    return log_path.read_text(encoding="utf-8")


def latest_images() -> list[Path]:
    if not OUTPUT_DIR.exists():
        return []
    return sorted(OUTPUT_DIR.glob("*.png"), key=lambda path: path.stat().st_mtime, reverse=True)


def apply_runtime_config(api_key: str, use_vertex: bool, cloud_project: str, cloud_location: str) -> None:
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    if use_vertex:
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
        os.environ["GOOGLE_CLOUD_PROJECT"] = cloud_project
        os.environ["GOOGLE_CLOUD_LOCATION"] = cloud_location or "global"
    else:
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"


def main() -> None:
    st.set_page_config(page_title="Infographic Agent Admin", layout="wide")

    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Gemini API key", type="password")
        use_vertex = st.checkbox("Use Vertex AI")
        cloud_project = ""
        cloud_location = "global"

        if use_vertex:
            cloud_project = st.text_input("Google Cloud project")
            cloud_location = st.text_input("Google Cloud location", value="global")

        st.divider()
        if st.button("Clear log", width="stretch"):
            Path(LOG_FILE).write_text("", encoding="utf-8")
            st.rerun()

    st.title("Infographic Agent Admin")

    run_col, view_col = st.columns([0.9, 1.1], gap="large")

    with run_col:
        st.subheader("Run Workflow")
        url = st.text_input("Blog post URL", placeholder="https://example.com/blog/post")
        run_clicked = st.button("Generate Infographic", type="primary", width="stretch")

        if run_clicked:
            if not url.strip():
                st.error("Enter a blog post URL before running.")
            else:
                apply_runtime_config(api_key, use_vertex, cloud_project, cloud_location)
                with st.spinner("Running scrape, generation, evaluation, and optional regeneration..."):
                    result = create_infographic_workflow(url.strip())
                st.session_state["last_result"] = result
                if result.startswith("Error"):
                    st.error(result)
                else:
                    st.success("Workflow completed.")

        if st.session_state.get("last_result"):
            st.text_area("Last result", st.session_state["last_result"], height=160)

    with view_col:
        st.subheader("Generated Images")
        images = latest_images()
        if not images:
            st.info("No generated images yet.")
        else:
            selected_image = st.selectbox("Image", images, format_func=lambda path: path.name)
            st.image(str(selected_image), caption=str(selected_image), width="stretch")

    st.divider()
    st.subheader("Execution Log")
    st.code(read_log(), language="text")


if __name__ == "__main__":
    main()
