import { useState, useRef, useEffect, useCallback } from "react";

// ─── Constants ───────────────────────────────────────────────────────────────
const INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions";
const AGENT_ID = "antigravity-preview-05-2026";
const API_REVISION = "2026-05-20";

// ─── Styles ──────────────────────────────────────────────────────────────────
const css = `
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Syne:wght@600;700;800&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #080810;
    --surface:  #0f0f1a;
    --s2:       #14141f;
    --border:   #1c1c2e;
    --b2:       #252538;
    --text:     #dde0f0;
    --muted:    #5a5a7a;
    --dim:      #383850;
    --green:    #3dffa0;
    --blue:     #5ab4ff;
    --yellow:   #ffd06a;
    --red:      #ff6a8a;
    --purple:   #b06aff;
    --glow-g:   rgba(61,255,160,0.12);
    --glow-b:   rgba(90,180,255,0.10);
  }

  html, body, #root { height: 100%; background: var(--bg); color: var(--text); font-family: 'JetBrains Mono', monospace; font-size: 13px; overflow: hidden; }

  /* ── Layout ── */
  .app { display: grid; grid-template-rows: 44px 1fr; height: 100vh; }

  /* ── Topbar ── */
  .topbar {
    display: flex; align-items: center; gap: 12px;
    padding: 0 16px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    flex-shrink: 0;
  }
  .topbar-logo { font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 800; letter-spacing: -0.03em; color: var(--green); }
  .topbar-logo span { color: var(--muted); }
  .topbar-status { display: flex; align-items: center; gap: 6px; font-size: 10px; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; margin-left: 4px; }
  .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--dim); flex-shrink: 0; transition: background 0.3s, box-shadow 0.3s; }
  .dot.active { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .dot.working { background: var(--yellow); box-shadow: 0 0 6px var(--yellow); animation: pulse 1s ease-in-out infinite; }
  .dot.error { background: var(--red); box-shadow: 0 0 6px var(--red); }
  @keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:0.4 } }

  .topbar-model { margin-left: auto; font-size: 10px; color: var(--blue); border: 1px solid var(--b2); padding: 3px 8px; letter-spacing: 0.05em; }
  .topbar-env { font-size: 10px; color: var(--muted); border: 1px solid var(--border); padding: 3px 8px; letter-spacing: 0.05em; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .topbar-btn { font-family: inherit; font-size: 10px; padding: 3px 10px; background: transparent; border: 1px solid var(--b2); color: var(--muted); cursor: pointer; letter-spacing: 0.05em; transition: all 0.15s; }
  .topbar-btn:hover { border-color: var(--red); color: var(--red); }
  .topbar-btn.new { border-color: var(--b2); color: var(--dim); }
  .topbar-btn.new:hover { border-color: var(--green); color: var(--green); }

  /* ── Main panes ── */
  .main { display: grid; grid-template-columns: 1fr 280px; overflow: hidden; }

  /* ── Chat pane ── */
  .chat-pane { display: flex; flex-direction: column; border-right: 1px solid var(--border); overflow: hidden; }

  .messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
  .messages::-webkit-scrollbar { width: 4px; }
  .messages::-webkit-scrollbar-track { background: transparent; }
  .messages::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 2px; }

  /* ── Message ── */
  .msg { display: flex; flex-direction: column; gap: 4px; animation: fadeIn 0.2s ease; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; } }

  .msg-header { display: flex; align-items: center; gap: 8px; }
  .msg-role { font-size: 9px; letter-spacing: 0.15em; text-transform: uppercase; font-weight: 600; }
  .msg-role.user { color: var(--blue); }
  .msg-role.agent { color: var(--green); }
  .msg-role.system { color: var(--muted); }
  .msg-ts { font-size: 9px; color: var(--dim); }

  .msg-body { padding: 10px 12px; line-height: 1.7; font-size: 12px; border-left: 2px solid; white-space: pre-wrap; word-break: break-word; }
  .msg-body.user { border-color: var(--blue); background: rgba(90,180,255,0.04); color: var(--text); }
  .msg-body.agent { border-color: var(--green); background: rgba(61,255,160,0.03); color: var(--text); }
  .msg-body.system { border-color: var(--dim); background: transparent; color: var(--muted); font-size: 11px; }
  .msg-body.streaming { border-color: var(--yellow); background: rgba(255,208,106,0.03); }
  .msg-body.error { border-color: var(--red); background: rgba(255,106,138,0.04); color: var(--red); }

  .cursor { display: inline-block; width: 7px; height: 13px; background: var(--yellow); animation: blink 0.8s step-end infinite; margin-left: 2px; vertical-align: middle; }
  @keyframes blink { 0%,100% { opacity:1 } 50% { opacity:0 } }

  /* ── Steps ── */
  .steps { display: flex; flex-direction: column; gap: 2px; margin-top: 6px; }
  .step { display: flex; align-items: flex-start; gap: 8px; font-size: 10px; color: var(--muted); padding: 4px 8px; border: 1px solid var(--border); background: var(--s2); }
  .step-icon { flex-shrink: 0; width: 14px; text-align: center; }
  .step-type { color: var(--yellow); font-weight: 500; min-width: 70px; flex-shrink: 0; }
  .step-detail { color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
  .step.tool .step-type { color: var(--purple); }
  .step.code .step-type { color: var(--blue); }
  .step.result .step-type { color: var(--green); }

  /* ── Input ── */
  .input-area { padding: 12px 16px; border-top: 1px solid var(--border); background: var(--surface); }
  .input-row { display: flex; gap: 8px; align-items: flex-end; }
  .input-wrap { flex: 1; position: relative; }
  .input-prefix { position: absolute; left: 10px; top: 10px; color: var(--green); font-size: 13px; pointer-events: none; }
  textarea {
    width: 100%; resize: none; background: var(--bg);
    border: 1px solid var(--b2); color: var(--text);
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
    padding: 8px 10px 8px 26px; line-height: 1.6;
    min-height: 38px; max-height: 120px;
    outline: none; transition: border-color 0.15s;
  }
  textarea:focus { border-color: var(--green); }
  textarea::placeholder { color: var(--dim); }
  textarea:disabled { opacity: 0.5; cursor: not-allowed; }

  .send-btn {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600;
    padding: 0 16px; height: 38px; cursor: pointer;
    background: var(--green); color: var(--bg); border: none;
    letter-spacing: 0.05em; transition: opacity 0.15s;
    flex-shrink: 0;
  }
  .send-btn:hover { opacity: 0.85; }
  .send-btn:disabled { background: var(--dim); color: var(--muted); cursor: not-allowed; opacity: 1; }

  .input-meta { display: flex; justify-content: space-between; margin-top: 6px; font-size: 10px; color: var(--dim); }
  .slash-hint { color: var(--muted); }
  .slash-hint span { color: var(--yellow); }

  /* ── Right panel ── */
  .right-panel { display: flex; flex-direction: column; overflow: hidden; }

  .panel-tab-bar { display: flex; border-bottom: 1px solid var(--border); background: var(--surface); flex-shrink: 0; }
  .panel-tab { flex: 1; padding: 8px 4px; font-size: 10px; text-align: center; color: var(--muted); cursor: pointer; border-bottom: 2px solid transparent; letter-spacing: 0.08em; text-transform: uppercase; transition: all 0.15s; }
  .panel-tab.active { color: var(--green); border-bottom-color: var(--green); }
  .panel-tab:hover:not(.active) { color: var(--text); }

  .panel-body { flex: 1; overflow-y: auto; padding: 12px; }
  .panel-body::-webkit-scrollbar { width: 3px; }
  .panel-body::-webkit-scrollbar-thumb { background: var(--dim); }

  /* ── API key panel ── */
  .apikey-panel { padding: 16px; display: flex; flex-direction: column; gap: 10px; }
  .apikey-panel label { font-size: 10px; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
  .apikey-panel input {
    width: 100%; background: var(--bg); border: 1px solid var(--b2);
    color: var(--text); font-family: inherit; font-size: 11px;
    padding: 7px 10px; outline: none;
  }
  .apikey-panel input:focus { border-color: var(--green); }
  .apikey-save { font-family: inherit; font-size: 10px; padding: 6px 12px; background: transparent; border: 1px solid var(--green); color: var(--green); cursor: pointer; letter-spacing: 0.1em; }
  .apikey-save:hover { background: var(--glow-g); }
  .apikey-note { font-size: 10px; color: var(--muted); line-height: 1.6; }
  .apikey-note a { color: var(--blue); text-decoration: none; }
  .apikey-note a:hover { text-decoration: underline; }

  /* ── Session info ── */
  .info-row { display: flex; flex-direction: column; gap: 2px; margin-bottom: 10px; }
  .info-label { font-size: 9px; color: var(--dim); letter-spacing: 0.12em; text-transform: uppercase; }
  .info-value { font-size: 10px; color: var(--text); word-break: break-all; line-height: 1.5; }
  .info-value.mono { color: var(--blue); }
  .divider { height: 1px; background: var(--border); margin: 10px 0; }

  /* ── Hook config ── */
  .hook-editor { display: flex; flex-direction: column; gap: 8px; }
  .hook-editor label { font-size: 10px; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; }
  .hook-editor textarea {
    width: 100%; height: 180px; background: var(--bg); border: 1px solid var(--b2);
    color: var(--green); font-family: inherit; font-size: 10px;
    padding: 8px; resize: vertical; min-height: 80px;
    padding-left: 8px;
  }
  .hook-editor textarea:focus { border-color: var(--green); }
  .hook-apply { font-family: inherit; font-size: 10px; padding: 5px 10px; background: transparent; border: 1px solid var(--yellow); color: var(--yellow); cursor: pointer; letter-spacing: 0.08em; }
  .hook-apply:hover { background: rgba(255,208,106,0.06); }
  .hook-status { font-size: 10px; padding: 4px 8px; border: 1px solid; }
  .hook-status.ok { border-color: var(--green); color: var(--green); background: var(--glow-g); }
  .hook-status.err { border-color: var(--red); color: var(--red); }

  /* ── Steps log (right panel) ── */
  .step-log-item { padding: 6px 8px; border: 1px solid var(--border); margin-bottom: 4px; font-size: 10px; line-height: 1.6; }
  .step-log-item .sl-type { font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 2px; }
  .step-log-item .sl-detail { color: var(--muted); white-space: pre-wrap; word-break: break-word; }
  .step-log-item.thought .sl-type { color: var(--yellow); }
  .step-log-item.tool_code .sl-type { color: var(--blue); }
  .step-log-item.tool_code_result .sl-type { color: var(--green); }
  .step-log-item.default .sl-type { color: var(--muted); }

  /* ── Empty state ── */
  .empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 8px; }
  .empty-title { font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800; color: var(--b2); letter-spacing: -0.02em; }
  .empty-sub { font-size: 10px; color: var(--dim); text-align: center; line-height: 1.8; }
  .empty-sub span { color: var(--muted); }

  /* ── Confirm hook overlay ── */
  .overlay { position: fixed; inset: 0; background: rgba(8,8,16,0.85); display: flex; align-items: center; justify-content: center; z-index: 100; }
  .confirm-box { background: var(--surface); border: 1px solid var(--yellow); padding: 20px; width: 380px; display: flex; flex-direction: column; gap: 12px; }
  .confirm-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 14px; color: var(--yellow); }
  .confirm-detail { font-size: 11px; color: var(--muted); line-height: 1.7; }
  .confirm-code { font-size: 10px; background: var(--bg); padding: 8px; color: var(--text); border: 1px solid var(--border); white-space: pre-wrap; word-break: break-word; max-height: 100px; overflow-y: auto; }
  .confirm-btns { display: flex; gap: 8px; }
  .confirm-btn { flex: 1; font-family: inherit; font-size: 11px; padding: 7px; cursor: pointer; border: 1px solid; background: transparent; letter-spacing: 0.05em; }
  .confirm-btn.approve { border-color: var(--green); color: var(--green); }
  .confirm-btn.approve:hover { background: var(--glow-g); }
  .confirm-btn.block { border-color: var(--red); color: var(--red); }
  .confirm-btn.block:hover { background: rgba(255,106,138,0.06); }
`;

// ─── Helpers ─────────────────────────────────────────────────────────────────
const ts = () => new Date().toLocaleTimeString("en-GB", { hour12: false });
const shortId = (id) => id ? id.slice(0, 16) + "…" : "—";

function parseHooks(json) {
  try { return JSON.parse(json); }
  catch { return null; }
}

function matchHook(hooks, eventName, detail = {}) {
  if (!hooks?.hooks) return null;
  return hooks.hooks.find(h => {
    if (h.event !== eventName) return false;
    if (h.match) {
      return Object.entries(h.match).every(([k, v]) => detail[k] === v);
    }
    return true;
  }) || null;
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function Agylity() {
  const [apiKey, setApiKey] = useState("");
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("idle"); // idle | working | error
  const [interactionId, setInteractionId] = useState(null);
  const [environmentId, setEnvironmentId] = useState(null);
  const [allSteps, setAllSteps] = useState([]);
  const [hookJson, setHookJson] = useState(JSON.stringify({
    hooks: [
      { event: "before_interaction", action: "log" },
      { event: "after_interaction", action: "log" },
      { event: "on_error", action: "log" }
    ]
  }, null, 2));
  const [hooksParsed, setHooksParsed] = useState(null);
  const [hookStatus, setHookStatus] = useState(null);
  const [rightTab, setRightTab] = useState("session");
  const [confirmPending, setConfirmPending] = useState(null); // { resolve, detail }
  const [hookLog, setHookLog] = useState([]);
  const [model] = useState("gemini-3.5-flash");

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const hookLogRef = useRef([]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Hook engine ──────────────────────────────────────────────────────────
  const fireHook = useCallback(async (eventName, detail = {}) => {
    const hook = matchHook(hooksParsed, eventName, detail);
    if (!hook) return { proceed: true };

    const entry = { ts: ts(), event: eventName, action: hook.action, detail };
    hookLogRef.current = [...hookLogRef.current, entry];
    setHookLog([...hookLogRef.current]);

    if (hook.action === "log") {
      console.log("[agylity hook]", entry);
      return { proceed: true };
    }

    if (hook.action === "block") {
      addMessage("system", `🪝 Hook blocked: ${eventName}`);
      return { proceed: false };
    }

    if (hook.action === "confirm") {
      return new Promise((resolve) => {
        setConfirmPending({ resolve, detail, event: eventName });
      });
    }

    if (hook.action === "notify" && hook.webhook) {
      try {
        await fetch(hook.webhook, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(entry),
        });
      } catch { /* webhook errors are non-fatal */ }
      return { proceed: true };
    }

    return { proceed: true };
  }, [hooksParsed]);

  // ── Message helpers ──────────────────────────────────────────────────────
  const addMessage = (role, content, extra = {}) => {
    setMessages(prev => [...prev, { id: Date.now(), role, content, ts: ts(), ...extra }]);
  };

  // ── Streaming call ───────────────────────────────────────────────────────
  const runInteraction = useCallback(async (prompt) => {
    if (!apiKey) { addMessage("system", "⚠ Set your Gemini API key in the Config tab first."); return; }
    if (status === "working") return;

    setStatus("working");
    addMessage("user", prompt);

    const preHook = await fireHook("before_interaction", { prompt });
    if (!preHook.proceed) { setStatus("idle"); return; }

    // seed streaming message
    setMessages(prev => [...prev, { id: "stream", role: "agent", content: "", ts: ts(), streaming: true, steps: [] }]);

    const body = {
      agent: AGENT_ID,
      input: [{ type: "text", text: prompt }],
      environment: environmentId ? environmentId : { type: "remote" },
      ...(interactionId ? { previous_interaction_id: interactionId } : {}),
      stream: true,
    };

    let finalText = "";
    let finalInteractionId = null;
    let finalEnvId = null;
    let streamSteps = [];

    try {
      const resp = await fetch(INTERACTIONS_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": apiKey,
          "Api-Revision": API_REVISION,
        },
        body: JSON.stringify(body),
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: { message: resp.statusText } }));
        const msg = err?.error?.message || resp.statusText;
        throw new Error(`${resp.status}: ${msg}`);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // SSE: split on double newline
        const parts = buffer.split("\n\n");
        buffer = parts.pop();

        for (const part of parts) {
          const dataLine = part.split("\n").find(l => l.startsWith("data:"));
          if (!dataLine) continue;
          const raw = dataLine.slice(5).trim();
          if (raw === "[DONE]") continue;
          try {
            const chunk = JSON.parse(raw);

            // Accumulate text
            if (chunk.output_text) {
              finalText = chunk.output_text;
            }
            if (chunk.delta?.text) {
              finalText += chunk.delta.text;
            }

            // Steps
            if (chunk.steps) {
              streamSteps = chunk.steps;
              setAllSteps(chunk.steps);
            }

            // IDs
            if (chunk.id) finalInteractionId = chunk.id;
            if (chunk.environment_id) finalEnvId = chunk.environment_id;

            // Update streaming bubble
            setMessages(prev => prev.map(m =>
              m.id === "stream"
                ? { ...m, content: finalText, steps: streamSteps }
                : m
            ));
          } catch { /* partial JSON, skip */ }
        }
      }

      // Handle non-streaming JSON fallback (some environments)
      if (!finalText && buffer.trim()) {
        try {
          const full = JSON.parse(buffer.trim());
          finalText = full.output_text || "";
          finalInteractionId = full.id || null;
          finalEnvId = full.environment_id || null;
          if (full.steps) { streamSteps = full.steps; setAllSteps(full.steps); }
        } catch { finalText = buffer.trim(); }
      }

      setMessages(prev => prev.map(m =>
        m.id === "stream"
          ? { ...m, id: Date.now(), content: finalText || "(no output)", streaming: false, steps: streamSteps }
          : m
      ));

      if (finalInteractionId) setInteractionId(finalInteractionId);
      if (finalEnvId) setEnvironmentId(finalEnvId);

      await fireHook("after_interaction", { interaction_id: finalInteractionId });
      setStatus("active");

    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.id === "stream"
          ? { ...m, id: Date.now(), content: err.message, streaming: false, role: "agent", error: true }
          : m
      ));
      await fireHook("on_error", { error: err.message });
      setStatus("error");
    }
  }, [apiKey, status, interactionId, environmentId, fireHook]);

  // ── Slash commands ───────────────────────────────────────────────────────
  const handleSlash = (cmd) => {
    if (cmd === "/clear") {
      setMessages([]);
      addMessage("system", "Context cleared. Environment preserved — files persist.");
      setStatus("active");
      return true;
    }
    if (cmd === "/new") {
      setMessages([]);
      setInteractionId(null);
      setEnvironmentId(null);
      setAllSteps([]);
      setStatus("idle");
      addMessage("system", "New session started. Fresh sandbox will provision on next prompt.");
      return true;
    }
    if (cmd === "/resume") {
      addMessage("system", interactionId
        ? `Resuming session ${shortId(interactionId)}`
        : "No previous interaction to resume.");
      return true;
    }
    if (cmd.startsWith("/model")) {
      addMessage("system", `Model: ${model} (Gemini 3.5 Flash — fixed for managed agent)`);
      return true;
    }
    if (cmd === "/help") {
      addMessage("system", `Commands: /clear /new /resume /model /help\n\nManaged Agent: ${AGENT_ID}\nAPI: POST ${INTERACTIONS_URL}`);
      return true;
    }
    return false;
  };

  // ── Submit ───────────────────────────────────────────────────────────────
  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    setInput("");
    if (trimmed.startsWith("/")) {
      handleSlash(trimmed);
      return;
    }
    runInteraction(trimmed);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // ── Hook apply ───────────────────────────────────────────────────────────
  const applyHooks = () => {
    const parsed = parseHooks(hookJson);
    if (!parsed) {
      setHookStatus({ ok: false, msg: "Invalid JSON" });
      return;
    }
    setHooksParsed(parsed);
    setHookStatus({ ok: true, msg: `${parsed.hooks?.length || 0} hook(s) active` });
  };

  // ── New session ──────────────────────────────────────────────────────────
  const newSession = () => {
    setMessages([]);
    setInteractionId(null);
    setEnvironmentId(null);
    setAllSteps([]);
    hookLogRef.current = [];
    setHookLog([]);
    setStatus("idle");
  };

  // ── Confirm handler ──────────────────────────────────────────────────────
  const resolveConfirm = (proceed) => {
    if (confirmPending) {
      confirmPending.resolve({ proceed });
      setConfirmPending(null);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────
  const statusLabel = status === "idle" ? "ready" : status === "working" ? "working" : status === "active" ? "active" : "error";

  return (
    <>
      <style>{css}</style>

      {confirmPending && (
        <div className="overlay">
          <div className="confirm-box">
            <div className="confirm-title">🪝 Hook: confirm required</div>
            <div className="confirm-detail">Event: <strong>{confirmPending.event}</strong></div>
            <div className="confirm-code">{JSON.stringify(confirmPending.detail, null, 2)}</div>
            <div className="confirm-btns">
              <button className="confirm-btn approve" onClick={() => resolveConfirm(true)}>▶ Approve</button>
              <button className="confirm-btn block" onClick={() => resolveConfirm(false)}>✕ Block</button>
            </div>
          </div>
        </div>
      )}

      <div className="app">
        {/* Topbar */}
        <div className="topbar">
          <span className="topbar-logo">AGY<span>lity</span></span>
          <div className="topbar-status">
            <div className={`dot ${status === "working" ? "working" : status === "active" ? "active" : status === "error" ? "error" : ""}`} />
            {statusLabel}
          </div>
          <span className="topbar-model">{model}</span>
          {environmentId && (
            <span className="topbar-env" title={environmentId}>env: {environmentId.slice(0, 20)}…</span>
          )}
          <button className="topbar-btn new" onClick={newSession}>+ new</button>
          {interactionId && (
            <button className="topbar-btn" onClick={() => {
              setInteractionId(null);
              setEnvironmentId(prev => prev); // keep sandbox
              addMessage("system", "Conversation cleared. Sandbox preserved.");
              setStatus("active");
            }}>/ clear ctx</button>
          )}
        </div>

        {/* Main */}
        <div className="main">
          {/* Chat */}
          <div className="chat-pane">
            <div className="messages">
              {messages.length === 0 && (
                <div className="empty">
                  <div className="empty-title">AGYlity</div>
                  <div className="empty-sub">
                    Gemini Managed Agent bridge<br/>
                    <span>agent: {AGENT_ID}</span><br/>
                    <span>Set API key → Config tab → start prompting</span>
                  </div>
                </div>
              )}
              {messages.map(m => (
                <div className="msg" key={m.id}>
                  <div className="msg-header">
                    <span className={`msg-role ${m.role}`}>{m.role}</span>
                    <span className="msg-ts">{m.ts}</span>
                  </div>
                  <div className={`msg-body ${m.role} ${m.streaming ? "streaming" : ""} ${m.error ? "error" : ""}`}>
                    {m.content}
                    {m.streaming && <span className="cursor" />}
                  </div>
                  {m.steps?.length > 0 && (
                    <div className="steps">
                      {m.steps.slice(0, 4).map((s, i) => (
                        <div key={i} className={`step ${s.type || "default"}`}>
                          <span className="step-icon">
                            {s.type === "thought" ? "💭" : s.type === "tool_code" ? "⚙" : s.type === "tool_code_result" ? "✓" : "→"}
                          </span>
                          <span className="step-type">{s.type || "step"}</span>
                          <span className="step-detail">
                            {s.thought ? s.thought.slice(0, 80) :
                             s.code ? s.code.slice(0, 80) :
                             s.result ? String(s.result).slice(0, 80) :
                             JSON.stringify(s).slice(0, 80)}
                          </span>
                        </div>
                      ))}
                      {m.steps.length > 4 && (
                        <div className="step">
                          <span className="step-icon">…</span>
                          <span className="step-type">more</span>
                          <span className="step-detail">{m.steps.length - 4} additional steps</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
              <div className="input-row">
                <div className="input-wrap">
                  <span className="input-prefix">›</span>
                  <textarea
                    ref={textareaRef}
                    rows={1}
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="prompt the agent… or /help for commands"
                    disabled={status === "working"}
                  />
                </div>
                <button
                  className="send-btn"
                  onClick={handleSubmit}
                  disabled={status === "working" || !input.trim()}
                >
                  {status === "working" ? "…" : "RUN"}
                </button>
              </div>
              <div className="input-meta">
                <span className="slash-hint">
                  <span>/clear</span> · <span>/new</span> · <span>/resume</span> · <span>/help</span>
                </span>
                <span>{interactionId ? `session: ${shortId(interactionId)}` : "no session"}</span>
              </div>
            </div>
          </div>

          {/* Right panel */}
          <div className="right-panel">
            <div className="panel-tab-bar">
              {["session", "steps", "hooks", "config"].map(t => (
                <div
                  key={t}
                  className={`panel-tab ${rightTab === t ? "active" : ""}`}
                  onClick={() => setRightTab(t)}
                >{t}</div>
              ))}
            </div>

            <div className="panel-body">
              {/* Session tab */}
              {rightTab === "session" && (
                <div>
                  <div className="info-row">
                    <div className="info-label">Agent</div>
                    <div className="info-value">{AGENT_ID}</div>
                  </div>
                  <div className="info-row">
                    <div className="info-label">Model</div>
                    <div className="info-value mono">{model}</div>
                  </div>
                  <div className="info-row">
                    <div className="info-label">Status</div>
                    <div className={`info-value ${status === "active" ? "" : ""}`}>{statusLabel}</div>
                  </div>
                  <div className="divider" />
                  <div className="info-row">
                    <div className="info-label">Interaction ID</div>
                    <div className="info-value mono" style={{ fontSize: 9, wordBreak: "break-all" }}>
                      {interactionId || "—"}
                    </div>
                  </div>
                  <div className="info-row">
                    <div className="info-label">Environment ID</div>
                    <div className="info-value mono" style={{ fontSize: 9, wordBreak: "break-all" }}>
                      {environmentId || "—"}
                    </div>
                  </div>
                  <div className="divider" />
                  <div className="info-row">
                    <div className="info-label">Turns</div>
                    <div className="info-value">{messages.filter(m => m.role === "user").length}</div>
                  </div>
                  <div className="info-row">
                    <div className="info-label">Steps logged</div>
                    <div className="info-value">{allSteps.length}</div>
                  </div>
                  <div className="info-row">
                    <div className="info-label">Hook events</div>
                    <div className="info-value">{hookLog.length}</div>
                  </div>
                  <div className="divider" />
                  <div className="info-row">
                    <div className="info-label">API endpoint</div>
                    <div className="info-value" style={{ fontSize: 9, color: "var(--muted)", wordBreak: "break-all" }}>
                      {INTERACTIONS_URL}
                    </div>
                  </div>
                  <div className="info-row">
                    <div className="info-label">Api-Revision</div>
                    <div className="info-value mono">{API_REVISION}</div>
                  </div>
                </div>
              )}

              {/* Steps tab */}
              {rightTab === "steps" && (
                <div>
                  {allSteps.length === 0 && hookLog.length === 0 && (
                    <div style={{ color: "var(--dim)", fontSize: 10, padding: "8px 0" }}>
                      Steps appear here after agent runs.
                    </div>
                  )}
                  {allSteps.map((s, i) => (
                    <div key={i} className={`step-log-item ${s.type || "default"}`}>
                      <div className="sl-type">{s.type || "step"} #{i + 1}</div>
                      <div className="sl-detail">
                        {s.thought ? s.thought :
                         s.code ? s.code :
                         s.result ? String(s.result) :
                         JSON.stringify(s, null, 2)}
                      </div>
                    </div>
                  ))}
                  {hookLog.length > 0 && (
                    <>
                      <div className="divider" />
                      <div style={{ fontSize: 9, color: "var(--yellow)", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 6 }}>Hook Log</div>
                      {hookLog.map((h, i) => (
                        <div key={i} className="step-log-item default">
                          <div className="sl-type">{h.event} → {h.action}</div>
                          <div className="sl-detail">{h.ts}</div>
                        </div>
                      ))}
                    </>
                  )}
                </div>
              )}

              {/* Hooks tab */}
              {rightTab === "hooks" && (
                <div className="hook-editor">
                  <label>Hook Config (JSON)</label>
                  <textarea
                    value={hookJson}
                    onChange={e => setHookJson(e.target.value)}
                    spellCheck={false}
                  />
                  <button className="hook-apply" onClick={applyHooks}>Apply Hooks</button>
                  {hookStatus && (
                    <div className={`hook-status ${hookStatus.ok ? "ok" : "err"}`}>
                      {hookStatus.ok ? "✓" : "✕"} {hookStatus.msg}
                    </div>
                  )}
                  <div style={{ fontSize: 9, color: "var(--dim)", lineHeight: 1.7, marginTop: 4 }}>
                    Events: before_interaction · after_interaction · on_error<br/>
                    Actions: log · block · confirm · notify(+webhook)
                  </div>
                </div>
              )}

              {/* Config tab */}
              {rightTab === "config" && (
                <div className="apikey-panel">
                  <label>Gemini API Key</label>
                  <input
                    type="password"
                    placeholder="Gemini API key"
                    value={apiKeyInput || (apiKey ? "••••••••••••••••" : "")}
                    onChange={e => setApiKeyInput(e.target.value)}
                    autoComplete="off"
                  />
                  <button className="apikey-save" onClick={() => {
                    if (apiKeyInput) {
                      setApiKey(apiKeyInput);
                      setApiKeyInput("");
                      addMessage("system", "✓ API key loaded for this browser session.");
                      setStatus("active");
                    }
                  }}>
                    Save Key
                  </button>
                  {apiKey && (
                    <div style={{ fontSize: 10, color: "var(--green)" }}>✓ Key loaded in memory</div>
                  )}
                  <div className="divider" />
                  <div className="apikey-note">
                    Get a free key at{" "}
                    <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer">
                      aistudio.google.com/apikey
                    </a>
                    <br/><br/>
                    Enable <strong>Managed Agents</strong> under the Experimental section of your project.
                    <br/><br/>
                    Interactions API (beta) — requires{" "}
                    <code style={{ color: "var(--yellow)" }}>Api-Revision: {API_REVISION}</code>
                    <br/><br/>
                    Keys are kept in memory only. They are not written to localStorage.
                  </div>
                  <div className="divider" />
                  <div className="apikey-note">
                    <strong style={{ color: "var(--text)" }}>What this prototype tests</strong><br/>
                    • Real POST to /v1beta/interactions<br/>
                    • SSE streaming from Managed Agent<br/>
                    • Multi-turn via previous_interaction_id<br/>
                    • Sandbox persistence via environment_id<br/>
                    • JSON hook engine (log/block/confirm)<br/>
                    • Slash commands (/clear /new /resume)
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
