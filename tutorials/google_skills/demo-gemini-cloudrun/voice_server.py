"""
Live Voice Claims Demo — combined HTTP + WebSocket server.

Run:
    python voice_server.py

Requires: aiohttp>=3.9, google-genai, python-dotenv
Install: pip install aiohttp
"""

import asyncio
import base64
import json
import os
import sys
from pathlib import Path

import aiohttp
from aiohttp import web
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

PORT = 8765


# ---------------------------------------------------------------------------
# HTML dashboard
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Live Voice Claims — Gemini</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d1117;--sf:#161b22;--bd:#30363d;--bl:#58a6ff;--gr:#3fb950;--yl:#d29922;--rd:#f85149;--tx:#c9d1d9;--mt:#8b949e}
body{background:var(--bg);color:var(--tx);font-family:-apple-system,sans-serif;min-height:100vh;display:flex;flex-direction:column}
header{background:var(--sf);border-bottom:1px solid var(--bd);padding:1rem 1.5rem;display:flex;align-items:center;gap:1rem}
h1{font-size:1.1rem;font-weight:600;color:var(--bl)}
.dot{width:10px;height:10px;border-radius:50%;background:var(--mt);flex-shrink:0}
.dot.connected{background:var(--gr)}
.dot.in-call{background:var(--rd);animation:pulse 1s infinite}
.dot.extracting{background:var(--yl);animation:pulse .5s infinite}
.dot.ended{background:var(--gr)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
main{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:1rem;padding:1rem;max-width:1200px;margin:0 auto;width:100%}
.panel{background:var(--sf);border:1px solid var(--bd);border-radius:8px;padding:1rem;display:flex;flex-direction:column;gap:.75rem}
.ph{font-size:.7rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--mt);border-bottom:1px solid var(--bd);padding-bottom:.5rem;margin-bottom:.25rem}
#controls{display:flex;align-items:center;justify-content:center;gap:1rem;padding:1.5rem}
.mic{width:72px;height:72px;border-radius:50%;border:3px solid var(--bl);background:transparent;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0}
.mic:hover{background:rgba(88,166,255,.1)}
.mic.recording{background:var(--rd);border-color:var(--rd);animation:pulse 1s infinite}
.mic svg{width:28px;height:28px;fill:var(--bl);pointer-events:none}
.mic.recording svg{fill:#fff}
#end{background:var(--rd);color:#fff;border:none;padding:.75rem 2rem;border-radius:6px;font-size:.9rem;font-weight:600;cursor:pointer;display:none}
#end:hover{filter:brightness(1.1)}
.log{font-size:.75rem;color:var(--mt);max-height:60px;overflow-y:auto;background:var(--bg);border:1px solid var(--bd);border-radius:4px;padding:.5rem}
.ta{flex:1;overflow-y:auto;max-height:260px;font-size:.9rem;line-height:1.5}
.tl{padding:.2rem 0;border-bottom:1px solid var(--bd)}
.tl.gemini{color:var(--bl)}
.tl.user{color:var(--gr)}
.tl.system{color:var(--yl)}
.cg{display:grid;grid-template-columns:1fr 1fr;gap:.5rem}
.cf{background:var(--bg);border:1px solid var(--bd);border-radius:4px;padding:.5rem .75rem}
.cf label{font-size:.65rem;text-transform:uppercase;letter-spacing:.05em;color:var(--mt);display:block}
.cf .v{font-size:.9rem;font-weight:500;margin-top:.15rem}
.cf.empty .v{color:var(--mt);font-style:italic}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:4px;font-size:.75rem;font-weight:600;background:var(--bl);color:#fff}
.badge.rd{background:var(--rd)}.badge.yl{background:var(--yl);color:#000}.badge.mt{background:var(--mt)}
#routing-badge{background:var(--bl)}.badge.emergency{background:var(--rd)}.badge.siu{background:var(--yl);color:#000}.badge.needs-docs{background:var(--mt)}.badge.ready{background:var(--gr)}
</style>
</head>
<body>
<header><div class="dot" id="dot"></div><h1>Live Voice Claims Intake</h1></header>
<main>
  <div class="panel">
    <div class="ph">Call Controls</div>
    <div id="controls">
      <button class="mic" id="mic-btn" title="Hold to speak">
        <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15A.997.997 0 0 0 6.09 11H4c0 3.04 2.07 5.54 4.82 6.09.41.08.77-.23.87-.62.11-.44-.16-.87-.6-.94A6.003 6.003 0 0 1 4 11c0-3.31 2.69-6 6-6s6 2.69 6 6c0 1.98-.96 3.73-2.42 4.84-.23.18-.31.48-.2.74.12.26.41.41.7.35A8.001 8.001 0 0 0 18.91 11h-2.02z"/></svg>
      </button>
      <button id="end">End Call</button>
    </div>
    <div class="log" id="log">Connecting to server...</div>
  </div>
  <div class="panel">
    <div class="ph">Live Transcript</div>
    <div class="ta" id="ta"></div>
  </div>
  <div class="panel" style="grid-column:1/-1">
    <div class="ph">Claim State</div>
    <div class="cg">
      <div class="cf" id="f-claimant"><label>Claimant</label><div class="v">—</div></div>
      <div class="cf" id="f-policy"><label>Policy #</label><div class="v">—</div></div>
      <div class="cf" id="f-date"><label>Incident Date</label><div class="v">—</div></div>
      <div class="cf" id="f-loc"><label>Location</label><div class="v">—</div></div>
      <div class="cf" id="f-type"><label>Claim Type</label><div class="v">—</div></div>
      <div class="cf" id="f-sev"><label>Severity</label><div class="v">—</div></div>
      <div class="cf" id="f-rout" style="grid-column:1/-1"><label>Routing Decision</label><div class="v">—</div></div>
      <div class="cf" id="f-dmg" style="grid-column:1/-1"><label>Damage Items</label><div class="v">—</div></div>
    </div>
  </div>
</main>
<script>
const WS = `ws://${location.host}/live-voice`;
let ws, ac, proc, str, rec = false, state = {};
const log = document.getElementById('log');
const mic = document.getElementById('mic-btn');
const end = document.getElementById('end');
const ta = document.getElementById('ta');

function $(id) { return document.getElementById(id); }
function addLog(m) { log.textContent = m + '\n' + log.textContent; }
function addTl(role, text) {
  const d = document.createElement('div'); d.className = 'tl ' + role;
  d.textContent = (role === 'system' ? '⚡ ' : role + ': ') + text; ta.appendChild(d); ta.scrollTop = ta.scrollHeight;
}
function fld(id, val, badge) {
  const el = $(id); el.querySelector('.v').textContent = val || '—'; el.classList.toggle('empty', !val);
  if (badge && val) { const v = el.querySelector('.v'); if (!v.querySelector('.badge')) { const b = document.createElement('span'); b.className = 'badge ' + badge; b.textContent = val; v.innerHTML = ''; v.appendChild(b); } else { v.querySelector('.badge').textContent = val; } }
}
function ui() {
  $('dot').className = 'dot ' + (state.phase || 'idle');
  const p = state.phase || '';
  if (p === 'in_call') { end.style.display = 'block'; }
  else if (p === 'extracting') { addLog('Extracting claim data...'); }
  else if (p === 'ended') { addLog('Call ended — claim extracted.'); end.style.display = 'none'; }
  else if (p === 'connected' && !state.transcript?.length) addLog('Ready — hold mic button to speak');
  fld('f-claimant', state.claimant_name);
  fld('f-policy', state.policy_number);
  fld('f-date', state.incident_date);
  fld('f-loc', state.incident_location);
  fld('f-type', state.claim_type);
  fld('f-sev', state.severity);
  if (state.decision) {
    const d = state.decision;
    const cls = d === 'emergency_escalation' ? 'emergency' : d === 'special_investigation' ? 'siu' : d === 'needs_documents' ? 'needs-docs' : 'ready';
    const el = $('f-rout'); el.querySelector('.v').innerHTML = '<span class="badge ' + cls + '">' + state.decision + '</span> by ' + (state.team || '') + ' (p' + state.priority + ')';
    el.classList.remove('empty');
  }
  fld('f-dmg', (state.damage_items || []).join(', '));
}
function connect() {
  ws = new WebSocket(WS);
  ws.onopen = () => addLog('Connected to server');
  ws.onclose = () => { addLog('Disconnected'); mic.classList.remove('recording'); rec = false; };
  ws.onerror = () => addLog('WebSocket error');
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.type === 'state') { state = m; ui(); }
    else if (m.type === 'transcript') addTl(m.role, m.text);
    else if (m.type === 'audio' && m.data) play(m.data);
    else if (m.type === 'turn_complete') addLog('Gemini finished');
    else if (m.type === 'error') addLog('ERROR: ' + m.message);
  };
}
function play(b64) {
  if (!ac) ac = new AudioContext();
  const buf = Uint8Array.from(atob(b64), c => c.charCodeAt(0)).buffer;
  ac.decodeAudioData(buf, ab => {
    const src = ac.createBufferSource(); src.buffer = ab;
    src.connect(ac.destination); src.start();
  }, () => {});
}
async function start() {
  try {
    str = await navigator.mediaDevices.getUserMedia({ audio: true });
    ac = new AudioContext();
    proc = ac.createScriptProcessor(4096, 1, 1);
    proc.onaudioprocess = e => {
      if (!rec || !ws || ws.readyState !== 1) return;
      const mono = e.inputBuffer.getChannelData(0);
      const pcm = new Int16Array(mono.length);
      for (let i = 0; i < mono.length; i++) pcm[i] = Math.max(-1, Math.min(1, mono[i])) * 32767;
      ws.send(pcm.buffer);
    };
    ac.createMediaStreamSource(str).connect(proc);
    ws.send(JSON.stringify({ type: 'start' }));
    mic.classList.add('recording'); rec = true; addLog('Recording...');
  } catch(e) { addLog('Mic error: ' + e.message); }
}
function stop() {
  if (!rec) return; rec = false;
  proc && proc.disconnect();
  str && str.getTracks().forEach(t => t.stop());
  mic.classList.remove('recording');
  ws.send(JSON.stringify({ type: 'end' }));
  addLog('Stopping recording...');
}
mic.addEventListener('mousedown', () => !rec && start());
mic.addEventListener('mouseup', () => rec && stop());
mic.addEventListener('mouseleave', () => rec && stop());
mic.addEventListener('touchstart', e => { e.preventDefault(); !rec && start(); });
mic.addEventListener('touchend', e => { e.preventDefault(); rec && stop(); });
end.addEventListener('click', stop);
connect();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Claim state
# ---------------------------------------------------------------------------

class ClaimState:
    def __init__(self):
        self.claimant_name = self.policy_number = self.incident_date = None
        self.incident_location = self.incident_description = None
        self.damage_items = []
        self.claim_type = self.severity = None
        self.decision = self.team = None
        self.priority = None
        self.transcript = []
        self.phase = "idle"

    def to_dict(self):
        return {
            "claimant_name": self.claimant_name,
            "policy_number": self.policy_number,
            "incident_date": self.incident_date,
            "incident_location": self.incident_location,
            "incident_description": self.incident_description,
            "damage_items": self.damage_items,
            "claim_type": self.claim_type,
            "severity": self.severity,
            "decision": self.decision,
            "team": self.team,
            "priority": self.priority,
            "transcript": self.transcript,
            "phase": self.phase,
        }

    def add(self, role, text):
        self.transcript.append({"role": role, "text": text})

    async def finalise(self, client):
        self.phase = "extracting"
        text = "\n".join(f"{t['role']}: {t['text']}" for t in self.transcript)
        if not text.strip():
            self.phase = "ended"
            return
        try:
            from pydantic import BaseModel
            class CN(BaseModel):
                claimant_name: str; policy_number: str
                incident_date: str | None = None; incident_location: str | None = None
                incident_description: str; damage_items: list[str]
            class CC(BaseModel):
                claim_type: str; severity: str; policy_line: str | None = None
            class FS(BaseModel):
                fraud_risk: bool; siu_referral_required: bool
                safety_concerns: bool; escalation_type: str | None

            def sp(resp):
                p = getattr(resp, "parsed", None)
                return p if isinstance(p, dict) else json.loads(resp.text)

            r1 = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"Extract from this insurance claim. Return ONLY valid JSON: claimant_name, policy_number, incident_date, incident_location, incident_description, damage_items (list).\n{text}",
                config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=CN.model_json_schema()),
            )
            d = sp(r1)
            for k in d:
                if hasattr(self, k):
                    setattr(self, k, d[k])

            r2 = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"Classify: claim_type, severity, policy_line. JSON only.\n{text}",
                config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=CC.model_json_schema()),
            )
            d2 = sp(r2)
            self.claim_type = d2.get("claim_type"); self.severity = d2.get("severity")

            r3 = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"Fraud risk: fraud_risk, siu_referral_required, safety_concerns, escalation_type. JSON only.\n{text}",
                config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=FS.model_json_schema()),
            )
            d3 = sp(r3)

            if d3.get("safety_concerns"):
                self.decision, self.team, self.priority = "emergency_escalation", "Emergency Response", 100
            elif d3.get("siu_referral_required"):
                self.decision, self.team, self.priority = "special_investigation", "SIU", 90
            elif not all([self.policy_number, self.incident_date, self.incident_location, self.incident_description]):
                self.decision, self.team, self.priority = "needs_documents", "Customer Service", 30
            else:
                self.decision, self.team, self.priority = "ready_for_adjuster", "Claims Processing", 50
        except Exception as exc:
            print(f"[voice_server] extraction error: {exc}", file=sys.stderr)
        finally:
            self.phase = "ended"


# ---------------------------------------------------------------------------
# WebSocket handler
# ---------------------------------------------------------------------------

async def handle_ws_aiohttp(ws):
    """Variant of handle_ws using aiohttp's WebSocketResponse API."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        await ws.send_str(json.dumps({"type": "error", "message": "No API key — set GOOGLE_API_KEY in .env"}))
        await ws.close()
        return

    client = genai.Client(api_key=api_key)
    state = ClaimState()
    state.phase = "connected"
    await ws.send_str(json.dumps({"type": "state", **state.to_dict()}))

    audio_q: asyncio.Queue = asyncio.Queue()

    async def send_audio(session):
        while True:
            d = await audio_q.get()
            if d is None:
                break
            try:
                await session.send_realtime_input(audio=d)
            except Exception:
                break

    async def recv_audio(session):
        try:
            async for resp in session.receive():
                if resp.data:
                    await ws.send_str(json.dumps({"type": "audio", "data": base64.b64encode(resp.data).decode()}))
                if resp.text:
                    state.add("gemini", resp.text)
                    await ws.send_str(json.dumps({"type": "transcript", "role": "gemini", "text": resp.text, **state.to_dict()}))
        except Exception as exc:
            print(f"[voice_server] recv: {exc}", file=sys.stderr)

    try:
        async with client.aio.live.connect(model="gemini-3.1-flash-live-preview") as sess:
            t1 = asyncio.create_task(send_audio(sess))
            t2 = asyncio.create_task(recv_audio(sess))
            while True:
                msg = await ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    d = json.loads(msg.data)
                    t = d.get("type")
                    if t == "start":
                        state.phase = "in_call"
                        await ws.send_str(json.dumps({"type": "state", **state.to_dict()}))
                    elif t == "audio":
                        await audio_q.put(base64.b64decode(d["data"]))
                        if d.get("text"):
                            state.add("user", d["text"])
                            await ws.send_str(json.dumps({"type": "transcript", "role": "user", "text": d["text"], **state.to_dict()}))
                    elif t == "text":
                        await sess.send_realtime_input(text=d["text"])
                        state.add("user", d["text"])
                        await ws.send_str(json.dumps({"type": "transcript", "role": "user", "text": d["text"], **state.to_dict()}))
                    elif t == "end":
                        await audio_q.put(None)
                        t1.cancel(); t2.cancel()
                        await ws.send_str(json.dumps({"type": "turn_complete"}))
                        await state.finalise(client)
                        await ws.send_str(json.dumps({"type": "state", **state.to_dict()}))
                        break
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    await audio_q.put(msg.data)
                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR):
                    t1.cancel(); t2.cancel()
                    break
    except Exception as exc:
        await ws.send_str(json.dumps({"type": "error", "message": str(exc)}))
    finally:
        try:
            await ws.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# aiohttp HTTP server (serves HTML, upgrades WebSocket)
# ---------------------------------------------------------------------------

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await handle_ws_aiohttp(ws)
    return ws

async def index_handler(request):
    return web.Response(text=HTML, content_type="text/html", charset="utf-8")

def create_app():
    app = web.Application()
    app.router.add_get("/", index_handler)
    app.router.add_get("/live-voice", websocket_handler)
    app.router.add_post("/live-voice", websocket_handler)
    return app


# ---------------------------------------------------------------------------
# Entry point — run both servers on the same event loop
# ---------------------------------------------------------------------------

async def main():
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    api_ok = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    print(f"  Live Voice Claims UI    : http://localhost:{PORT}/")
    print(f"  WebSocket endpoint     : ws://localhost:{PORT}/live-voice")
    print(f"  API key                : {'OK' if api_ok else 'MISSING — set GOOGLE_API_KEY in .env'}")
    print()
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[voice_server] Shutdown.")