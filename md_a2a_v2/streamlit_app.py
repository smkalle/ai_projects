import os
import requests
import streamlit as st

st.set_page_config(page_title="Multiagent A2A Search", layout="centered")
st.title("🔎 Multiagent A2A Content Search (LangGraph)")

backend_url = st.sidebar.text_input("Backend URL", os.getenv("BACKEND_URL", "http://localhost:8000")).rstrip("/")

q = st.text_input("Your query", "What documentaries exist on renewable energy?")
if st.button("Search"):
    try:
        resp = requests.post(f"{backend_url}/query", json={"query": q}, timeout=60)
        if resp.ok:
            st.subheader("Response")
            st.json(resp.json())
        else:
            st.error(f"Request failed: {resp.status_code} {resp.text}")
    except Exception as e:
        st.exception(e)

st.caption("Tip: Start the API with `uvicorn server.main:app --reload --port 8000`, then run this UI with `streamlit run streamlit_app.py`.")
