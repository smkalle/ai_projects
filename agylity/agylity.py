"""
agylity.py — Minimalist agent workspace for Gemini Managed Agents
==================================================================
Layout: persistent sidebar (session + controls) · clean main panel (work).
Workflow: run → review → iterate, with full step inspection,
multi-turn memory, sandbox persistence, and streaming.

Run:
    pip install streamlit requests
    export GEMINI_API_KEY="<your Gemini API key>"
    streamlit run agylity.py
"""

import json
import html
import os
import time
import requests
import streamlit as st
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="agylity", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

URL          = "https://generativelanguage.googleapis.com/v1beta/interactions"
AGENT_ID     = "antigravity-preview-05-2026"
API_REVISION = "2026-05-20"
TIMEOUT      = 300
LOG_DIR      = Path("agylity_runs"); LOG_DIR.mkdir(exist_ok=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink:#0f172a; --paper:#f7fffd; --line:#b7e4dc; --soft:#475569;
    --faint:#94a3b8; --side:#ecfdf5; --teal:#0f766e; --teal2:#14b8a6;
    --mint:#ccfbf1; --panel:#ffffff;
}
.stApp { background: var(--paper); }
* { font-family: 'Inter', sans-serif; color: var(--ink); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 760px; padding: 2rem 2rem 6rem; }

[data-testid="stSidebar"] { background: linear-gradient(180deg, #ecfdf5 0%, #f0fdfa 100%) !important; border-right: 1px solid var(--line); min-width: 270px !important; }
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
/* Make the collapse/expand control always visible and obvious */
[data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] {
    display: block !important; visibility: visible !important;
    color: var(--teal) !important; opacity: 1 !important; }
[data-testid="collapsedControl"] {
    background: var(--side) !important; border: 1px solid var(--line) !important;
    border-radius: 5px !important; padding: 4px !important; }

.brand { font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em; color: var(--teal); }
.brand .dot { color: var(--teal2); }
.brand-sub { font-size: 0.66rem; color: var(--soft); letter-spacing: 0.05em; margin: -2px 0 1.2rem; font-weight:500; }

.side-label {
    font-family:'JetBrains Mono',monospace; font-size:0.58rem;
    letter-spacing:0.18em; text-transform:uppercase; color:var(--teal);
    margin: 1.3rem 0 0.4rem; }

.fact { display:flex; justify-content:space-between; font-size:0.72rem; color:var(--soft); padding:0.2rem 0; }
.fact b { color:var(--teal); font-weight:600; font-family:'JetBrains Mono',monospace; }
.fact-id { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:var(--soft); word-break:break-all; line-height:1.5; margin-top:2px; }

.dot-i { display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--faint); margin-right:6px; }
.dot-i.on { background:var(--teal2); box-shadow:0 0 0 3px var(--mint); }

.step-label {
    font-family:'JetBrains Mono',monospace; font-size:0.6rem;
    letter-spacing:0.18em; text-transform:uppercase; color:var(--teal);
    margin: 1.6rem 0 0.5rem; display:flex; align-items:center; gap:0.6rem; }
.step-label::before { content:''; width:14px; height:2px; background:var(--teal2); }

.echo {
    font-size:0.82rem; color:var(--soft); white-space:pre-wrap;
    border-left:3px solid var(--teal2); padding:0.15rem 0 0.15rem 0.8rem; margin-bottom:0.5rem; }
.output {
    background:var(--panel); border:1px solid var(--line); border-radius:8px;
    padding:1.1rem 1.3rem; font-size:0.9rem; line-height:1.65;
    color:var(--ink); white-space:pre-wrap; word-break:break-word; box-shadow:0 8px 24px rgba(15,118,110,0.07); }
.output.err { border-color:#e2bcbc; color:#9c3d3d; background:#fdf7f7; }

.steps-strip { display:flex; gap:5px; flex-wrap:wrap; margin:0.6rem 0; }
.pill {
    font-family:'JetBrains Mono',monospace; font-size:0.6rem;
    padding:2px 9px; border-radius:11px; letter-spacing:0.04em;
    border:1px solid var(--line); color:var(--teal); background:#f0fdfa; font-weight:600; }
.pill.thought { border-color:#99f6e4; color:#0f766e; }
.pill.code    { border-color:#7dd3fc; color:#0369a1; }
.pill.result  { border-color:#86efac; color:#15803d; }

.status {
    font-family:'JetBrains Mono',monospace; font-size:0.66rem; color:var(--soft);
    padding:0.6rem 0; letter-spacing:0.02em; border-top:1px solid var(--line);
    margin-top:0.8rem; display:flex; gap:1.4rem; flex-wrap:wrap; }
.status b { color:var(--teal); font-weight:600; }

.empty { text-align:center; color:var(--soft); font-size:0.85rem; padding:4rem 1rem; line-height:1.9; }
.empty .big { font-size:1.8rem; color:var(--teal2); margin-bottom:0.6rem; }

.hist { font-size:0.76rem; color:var(--soft); padding:0.45rem 0; border-bottom:1px solid var(--line); }
.hist b { color:var(--teal); font-weight:600; }

.topnav {
    border:1px solid var(--line); border-radius:8px; background:linear-gradient(135deg, #ffffff 0%, #f0fdfa 100%);
    padding:0.9rem 1rem; margin-bottom:1rem; box-shadow:0 10px 30px rgba(15,118,110,0.08);
    display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.topnav-title { font-size:0.74rem; color:var(--soft); font-family:'JetBrains Mono',monospace; }
.topnav-title b { color:var(--teal); font-weight:600; }
.topnav-facts { display:flex; gap:1rem; flex-wrap:wrap; font-size:0.7rem; color:var(--soft); }
.topnav-facts b { color:var(--teal); font-family:'JetBrains Mono',monospace; font-weight:600; }

.stTextArea textarea, .stTextInput input {
    background:#ffffff !important; border:1px solid var(--line) !important;
    border-radius:8px !important; color:var(--ink) !important; caret-color:var(--teal) !important; }
.stTextArea textarea { font-size:0.9rem !important; padding:0.8rem !important; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color:var(--teal) !important; box-shadow:0 0 0 3px var(--mint) !important; }
[data-testid="stSidebar"] .stTextInput input { font-family:'JetBrains Mono',monospace !important; font-size:0.78rem !important; }

.stButton button {
    background:var(--teal) !important; color:#fff !important;
    border:1px solid var(--teal) !important; border-radius:8px !important;
    font-size:0.8rem !important; font-weight:500 !important;
    padding:0.45rem 1rem !important; transition:opacity 0.15s !important; }
.stButton button:hover { opacity:0.9 !important; background:#115e59 !important; border-color:#115e59 !important; }
.stButton button:disabled { background:var(--line) !important; color:var(--faint) !important; border-color:var(--line) !important; }
[data-testid="stSidebar"] .stButton button {
    background:#ffffff !important; color:var(--teal) !important;
    border:1px solid var(--line) !important; font-size:0.75rem !important; }
[data-testid="stSidebar"] .stButton button:hover { border-color:var(--teal) !important; background:#f0fdfa !important; }

[data-testid="stExpander"] { border:1px solid var(--line) !important; border-radius:8px !important; background:#ffffff !important; }
[data-testid="stExpander"] summary { font-size:0.76rem !important; color:var(--teal) !important; font-weight:600 !important; }

.stToggle label, .stCheckbox label, .stRadio label, .stMarkdown, p, label {
    color:var(--ink) !important; }
.stToggle label, .stCheckbox label, .stRadio label { font-size:0.78rem !important; color:var(--ink) !important; font-weight:500 !important; }
.stDownloadButton button {
    background:#ffffff !important; color:var(--teal) !important;
    border:1px solid var(--line) !important; border-radius:8px !important; font-size:0.78rem !important; }
code { font-family:'JetBrains Mono',monospace !important; }
[data-testid="stCodeBlock"], [data-testid="stCodeBlock"] pre {
    background:#f8fffd !important; color:var(--ink) !important;
    border:1px solid var(--line) !important; border-radius:8px !important; }
[data-testid="stCodeBlock"] code, [data-testid="stCodeBlock"] span {
    color:var(--ink) !important; background:transparent !important; }
.step-code {
    display:block; background:#f8fffd; color:#0f172a !important;
    border:1px solid var(--line); border-radius:8px; padding:0.85rem;
    font-family:'JetBrains Mono',monospace; font-size:0.78rem; line-height:1.55;
    white-space:pre-wrap; word-break:break-word; overflow-x:auto;
}
hr { border-color:var(--line) !important; }

[data-testid="stSidebar"] .stRadio > div { gap:2px !important; }
[data-testid="stSidebar"] .stRadio label {
    font-family:'JetBrains Mono',monospace !important; font-size:0.74rem !important;
    letter-spacing:0.03em !important; padding:0.15rem 0 !important; }
[data-testid="stHorizontalBlock"] [role="radiogroup"] {
    gap: 0.35rem !important; flex-wrap: wrap !important; }
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
    color:var(--ink) !important; }
</style>
""", unsafe_allow_html=True)

def init():
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    d = {"key":env_key, "key_source":"env" if env_key else "", "iid":None, "eid":None, "history":[], "current":None,
         "turns":0, "sys":"", "stream":False, "total":0.0, "nav":"Workspace"}
    for k,v in d.items(): st.session_state.setdefault(k,v)
init()

def ts(): return datetime.now().strftime("%H:%M:%S")

def esc(value):
    return html.escape(str(value), quote=True)

def log_run(data):
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    (LOG_DIR / f"run_{stamp}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

def call(prompt, sys_inst="", stream=False, fresh=False):
    headers = {"Content-Type":"application/json",
               "x-goog-api-key": st.session_state.key,
               "Api-Revision": API_REVISION}
    body = {"agent": AGENT_ID,
            "input":[{"type":"text","text":prompt}],
            "environment": st.session_state.eid if (not fresh and st.session_state.eid) else {"type":"remote"}}
    if not fresh and st.session_state.iid:
        body["previous_interaction_id"] = st.session_state.iid
    if sys_inst.strip(): body["system_instruction"] = sys_inst.strip()
    if stream: body["stream"] = True

    t0 = time.time()
    try:
        r = requests.post(URL, headers=headers, json=body, timeout=TIMEOUT, stream=stream)
    except Exception as e:
        return {"error": str(e)}
    elapsed = round(time.time()-t0, 2)

    if r.status_code != 200:
        try: msg = r.json().get("error",{}).get("message", r.text)
        except: msg = r.text
        return {"error": f"HTTP {r.status_code}: {msg}", "elapsed": elapsed}

    if stream:
        full=""; chunks=0; data={}; buf=""
        parse_errors = 0
        for raw in r.iter_content(chunk_size=None):
            buf += raw.decode("utf-8","replace")
            parts = buf.split("\n\n"); buf = parts.pop()
            for p in parts:
                dl = next((l[5:].strip() for l in p.splitlines() if l.startswith("data:")), None)
                if not dl or dl=="[DONE]": continue
                try:
                    c=json.loads(dl); chunks+=1
                    if c.get("output_text"): full=c["output_text"]
                    if c.get("delta",{}).get("text"): full+=c["delta"]["text"]
                    data.update({k:c[k] for k in ("id","environment_id","steps") if k in c})
                except json.JSONDecodeError:
                    parse_errors += 1
        data.update({"output_text":full,"chunks":chunks,"elapsed":elapsed})
        if parse_errors:
            data["stream_parse_errors"] = parse_errors
    else:
        data = r.json(); data["elapsed"]=elapsed

    if data.get("id"): st.session_state.iid = data["id"]
    if data.get("environment_id"): st.session_state.eid = data["environment_id"]
    st.session_state.turns += 1
    st.session_state.total += elapsed

    log_run(data)
    return data

def run_prompt(text, fresh=False):
    with st.spinner("agent working…"):
        result = call(text, st.session_state.sys, stream=st.session_state.stream, fresh=fresh)
    result["_prompt"]=text; result["_ts"]=ts()
    st.session_state.current = result
    if not result.get("error"):
        st.session_state.history.append(result)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<div class="brand">agylity<span class="dot">.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">gemini managed agent</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-label">api key</div>', unsafe_allow_html=True)
    if st.session_state.key:
        source = "env" if st.session_state.key_source == "env" else "manual"
        st.markdown(f'<div class="fact"><span><span class="dot-i on"></span>connected</span><b>{source}</b></div>',
                    unsafe_allow_html=True)
        if st.button("change key", use_container_width=True):
            st.session_state.key=""; st.session_state.key_source="manual"; st.rerun()
    else:
        k = st.text_input("key", type="password", placeholder="Gemini API key", label_visibility="collapsed")
        if k:
            st.session_state.key=k.strip(); st.session_state.key_source="manual"; st.rerun()

    if st.session_state.iid:
        st.markdown('<div class="side-label">ids</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="fact" style="display:block"><span>interaction</span>'
                    f'<div class="fact-id">{esc(st.session_state.iid)}</div></div>', unsafe_allow_html=True)
        if st.session_state.eid:
            st.markdown(f'<div class="fact" style="display:block"><span>environment</span>'
                        f'<div class="fact-id">{esc(st.session_state.eid)}</div></div>', unsafe_allow_html=True)

# ── KEY GATE ──
if not st.session_state.key:
    st.markdown('<div class="empty"><div class="big">◆</div>'
                'Paste your Gemini API key in the sidebar to begin.<br>'
                '<span style="font-size:0.72rem">aistudio.google.com/apikey</span></div>',
                unsafe_allow_html=True)
    st.stop()

cur = st.session_state.current

# ── TOP NAV ──
on = "on" if st.session_state.iid else ""
st.markdown(f"""
<div class="topnav">
  <div class="topnav-title"><span class="dot-i {on}"></span><b>{'active' if st.session_state.iid else 'idle'}</b> session</div>
  <div class="topnav-facts">
    <span><b>{st.session_state.turns}</b> turns</span>
    <span><b>{st.session_state.total:.1f}s</b> time</span>
    <span><b>{len(st.session_state.history)}</b> runs</span>
  </div>
</div>
""", unsafe_allow_html=True)

nav_col, stream_col, reset_col = st.columns([4, 1.2, 1.2], vertical_alignment="bottom")
with nav_col:
    st.session_state.nav = st.radio("view", ["Workspace","Steps","History","Sandbox"],
        label_visibility="collapsed",
        index=["Workspace","Steps","History","Sandbox"].index(st.session_state.nav),
        horizontal=True)
with stream_col:
    st.session_state.stream = st.toggle("stream", value=st.session_state.stream)
with reset_col:
    if st.button("reset", use_container_width=True, disabled=not bool(st.session_state.iid)):
        for k in ["iid","eid","history","current","turns","total"]:
            st.session_state[k] = (None if k in ["iid","eid","current"]
                                   else (0 if k=="turns" else (0.0 if k=="total" else [])))
        st.rerun()

with st.expander("system instruction"):
    st.session_state.sys = st.text_area("sys", value=st.session_state.sys, height=80,
        placeholder="You are a terse analytics agent…", label_visibility="collapsed")

st.markdown('<div class="step-label">prompt</div>', unsafe_allow_html=True)
prompt = st.text_area("prompt", height=110, label_visibility="collapsed",
                      placeholder="Describe a task for the agent…")
c1, c2 = st.columns([3,1])
with c1:
    fresh = st.toggle("fresh sandbox", value=False,
                      help="Ignore prior context, provision a new environment")
with c2:
    run = st.button("▶ run", use_container_width=True,
                    disabled=not (prompt and prompt.strip()))
if run and prompt.strip():
    run_prompt(prompt.strip(), fresh=fresh); st.rerun()

# ── WORKSPACE ──
if st.session_state.nav == "Workspace":
    if cur:
        st.markdown('<div class="step-label">review</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="echo">{esc(cur.get("_prompt",""))}</div>', unsafe_allow_html=True)
        if cur.get("error"):
            st.markdown(f'<div class="output err">{esc(cur["error"])}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="output">{esc(cur.get("output_text","(no output)"))}</div>',
                        unsafe_allow_html=True)
            steps = cur.get("steps",[])
            if steps:
                pills = "".join(
                    f'<span class="pill {({"thought":"thought","tool_code":"code","tool_code_result":"result"}.get(s.get("type",""),""))}">{esc(s.get("type","step"))}</span>'
                    for s in steps)
                st.markdown(f'<div class="steps-strip">{pills}</div>', unsafe_allow_html=True)
                st.caption("→ full step inspection in the **Steps** view")
        st.markdown(f"""
        <div class="status">
          <span><b>{esc(cur.get('elapsed','—'))}s</b> elapsed</span>
          <span><b>{len(cur.get('steps',[]))}</b> steps</span>
          <span><b>{st.session_state.turns}</b> turns</span>
          {"<span><b>"+esc(cur.get('chunks'))+"</b> chunks</span>" if cur.get('chunks') else ""}
        </div>""", unsafe_allow_html=True)

        if not cur.get("error"):
            st.markdown('<div class="step-label">iterate</div>', unsafe_allow_html=True)
            fu = st.text_input("fu", label_visibility="collapsed",
                               placeholder="Refine, continue, or follow up…")
            i1, i2 = st.columns([1,1])
            with i1:
                cont = st.button("→ continue", use_container_width=True,
                                 disabled=not (fu and fu.strip()))
            with i2:
                st.download_button("⬇ export run",
                    data=json.dumps(cur, indent=2, ensure_ascii=False),
                    file_name=f"agylity_{datetime.now().strftime('%H%M%S')}.json",
                    mime="application/json", use_container_width=True)
            if cont and fu.strip():
                run_prompt(fu.strip(), fresh=False); st.rerun()
    else:
        st.markdown('<div class="empty"><div class="big">◆</div>'
                    'Write a prompt and run the agent.<br>'
                    '<span style="font-size:0.72rem">Runs share a sandbox you can iterate on.</span>'
                    '</div>', unsafe_allow_html=True)

# ── STEPS ──
elif st.session_state.nav == "Steps":
    st.markdown('<div class="step-label">step inspection · latest run</div>', unsafe_allow_html=True)
    if not cur or not cur.get("steps"):
        st.markdown('<div class="empty"><div class="big">⚙</div>'
                    'No steps yet. Run a prompt above to inspect agent activity here.</div>', unsafe_allow_html=True)
    else:
        steps = cur["steps"]
        counts = {}
        for s in steps: counts[s.get("type","?")] = counts.get(s.get("type","?"),0)+1
        st.markdown(f'<div class="echo">{esc(cur.get("_prompt",""))}</div>', unsafe_allow_html=True)
        st.markdown('<div class="steps-strip">' + "".join(
            f'<span class="pill {({"thought":"thought","tool_code":"code","tool_code_result":"result"}.get(k,""))}">{esc(k)} ×{v}</span>'
            for k,v in counts.items()) + '</div>', unsafe_allow_html=True)
        for i, s in enumerate(steps):
            t = s.get("type","step")
            icon = {"thought":"💭","tool_code":"⚙","tool_code_result":"✓"}.get(t,"→")
            detail = s.get("thought") or s.get("code") or str(s.get("result","")) or json.dumps(s)
            with st.expander(f"{icon}  [{i}]  {t}", expanded=(i<2)):
                st.markdown(f'<pre class="step-code">{esc(detail[:4000])}</pre>', unsafe_allow_html=True)

# ── HISTORY ──
elif st.session_state.nav == "History":
    st.markdown('<div class="step-label">session history</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown('<div class="empty"><div class="big">↻</div>No runs yet.</div>',
                    unsafe_allow_html=True)
    else:
        for i, h in enumerate(reversed(st.session_state.history)):
            n = len(st.session_state.history)-i
            st.markdown(
                f'<div class="hist"><b>{n}.</b> <span style="font-family:JetBrains Mono;'
                f'color:#c0c0c0">{esc(h.get("_ts",""))}</span> · {esc(h.get("_prompt","")[:70])} '
                f'<span style="color:#c8c8c8">({esc(h.get("elapsed","—"))}s · '
                f'{len(h.get("steps",[]))} steps)</span></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("⬇ export full session",
            data=json.dumps(st.session_state.history, indent=2, ensure_ascii=False),
            file_name=f"agylity_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json")

# ── SANDBOX ──
elif st.session_state.nav == "Sandbox":
    st.markdown('<div class="step-label">sandbox environment</div>', unsafe_allow_html=True)
    if not st.session_state.eid:
        st.markdown('<div class="empty"><div class="big">▢</div>'
                    'No sandbox yet. The first run provisions one.<br>'
                    '<span style="font-size:0.72rem">Files persist across runs in this session.</span>'
                    '</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="output"><b>environment_id</b><br>'
                    f'<span style="font-family:JetBrains Mono;font-size:0.78rem;color:#666">'
                    f'{esc(st.session_state.eid)}</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="step-label">probe the sandbox</div>', unsafe_allow_html=True)
        st.caption("Run a shell command in the persistent environment.")
        probe = st.text_input("probe", label_visibility="collapsed", placeholder="e.g. ls -la /workspace")
        if st.button("▶ run in sandbox", disabled=not (probe and probe.strip())):
            run_prompt(f"Run this shell command and show the raw output: {probe.strip()}", fresh=False)
            st.rerun()
        if cur and not cur.get("error"):
            st.markdown('<div class="step-label">last output</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="output">{esc(cur.get("output_text",""))}</div>', unsafe_allow_html=True)
