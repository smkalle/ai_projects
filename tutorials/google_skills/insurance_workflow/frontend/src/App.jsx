import { useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8897";

const DEFAULT_NARRATIVE =
  "On April 12 my vehicle was rear-ended at the intersection of Main and 5th. Policy #AU-88271. I was stopped at a red light when the other driver hit me from behind. No injuries, but rear bumper and trunk are damaged.";

const SCENARIOS = [
  {
    key: "default",
    label: "Default collision",
    prompt: DEFAULT_NARRATIVE,
  },
  {
    key: "safety",
    label: "Safety emergency",
    prompt:
      "Policy AU-33333. Incident date 2026-05-02. Multi-car crash with fuel leak and reported injuries at Main and 7th. Immediate medical response required.",
  },
  {
    key: "siu",
    label: "Potential SIU",
    prompt:
      "Policy AU-22222. Incident date 2026-05-01. Car fire claim reported with conflicting witness statements and suspected staged loss indicators. Location: warehouse lot.",
  },
  {
    key: "missing",
    label: "Missing details",
    prompt: "My car crashed yesterday.",
  },
  {
    key: "racing",
    label: "Racing exclusion",
    prompt:
      "Policy AU-66666. Incident date 2026-05-05. Vehicle damaged during organized street race.",
  },
];

function field(value) {
  if (value === null || value === undefined || String(value).trim() === "") {
    return "Not provided";
  }
  return String(value);
}

function priorityClass(priority) {
  if (priority >= 100) return "chip danger";
  if (priority >= 90) return "chip warn";
  return "chip success";
}

export default function App() {
  const [scenario, setScenario] = useState("default");
  const [narrative, setNarrative] = useState(DEFAULT_NARRATIVE);
  const [sourceText, setSourceText] = useState("");
  const [sourceFile, setSourceFile] = useState(null);
  const [sourcePreview, setSourcePreview] = useState("");
  const [latestVision, setLatestVision] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [error, setError] = useState("");
  const [ingestMsg, setIngestMsg] = useState("");
  const [result, setResult] = useState(null);
  const [copyMsg, setCopyMsg] = useState("");
  const [debugState, setDebugState] = useState({
    phase: "idle",
    startedAt: null,
    endedAt: null,
    durationMs: null,
    httpStatus: null,
    httpStatusText: "",
    errorMessage: "",
    errorBody: "",
    trace: null,
  });

  const missingFields = useMemo(() => result?.validation?.missing_fields || [], [result]);

  async function submitClaim(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!narrative.trim()) {
      setError("Please enter a claim narrative.");
      return;
    }

    setLoading(true);
    const startedAt = new Date();
    setDebugState({
      phase: "submitting",
      startedAt: startedAt.toISOString(),
      endedAt: null,
      durationMs: null,
      httpStatus: null,
      httpStatusText: "",
      errorMessage: "",
      errorBody: "",
      trace: null,
    });
    try {
      const response = await fetch(`${API_URL}/claims`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: narrative }),
      });
      const rawText = await response.text();
      let body = null;
      try {
        body = rawText ? JSON.parse(rawText) : null;
      } catch {
        body = null;
      }

      const endedAt = new Date();
      const durationMs = endedAt.getTime() - startedAt.getTime();

      if (!response.ok) {
        const errorBody = body ? JSON.stringify(body, null, 2) : rawText;
        setDebugState({
          phase: "error",
          startedAt: startedAt.toISOString(),
          endedAt: endedAt.toISOString(),
          durationMs,
          httpStatus: response.status,
          httpStatusText: response.statusText,
          errorMessage: `HTTP ${response.status}`,
          errorBody: (errorBody || "").slice(0, 4000),
          trace: body?.detail?.trace || body?.trace || null,
        });
        throw new Error(`HTTP ${response.status}: ${errorBody}`);
      }

      const data = body || {};
      setResult(data);
      setDebugState({
        phase: "success",
        startedAt: startedAt.toISOString(),
        endedAt: endedAt.toISOString(),
        durationMs,
        httpStatus: response.status,
        httpStatusText: response.statusText,
        errorMessage: "",
        errorBody: "",
        trace: data.trace || null,
      });
    } catch (err) {
      setError(err.message || "Request failed");
      setDebugState((prev) => {
        if (prev.phase === "error") return prev;
        const endedAt = new Date();
        const started = prev.startedAt ? new Date(prev.startedAt) : endedAt;
        return {
          ...prev,
          phase: "error",
          endedAt: endedAt.toISOString(),
          durationMs: endedAt.getTime() - started.getTime(),
          errorMessage: err.message || "Request failed",
        };
      });
    } finally {
      setLoading(false);
    }
  }

  function debugBadgeClass(phase) {
    if (phase === "success") return "badge success";
    if (phase === "error") return "badge danger";
    if (phase === "submitting") return "badge warn";
    return "badge";
  }

  async function copyDebugPayload() {
    const payload = {
      phase: debugState.phase,
      endpoint: `${API_URL}/claims`,
      startedAt: debugState.startedAt,
      endedAt: debugState.endedAt,
      durationMs: debugState.durationMs,
      httpStatus: debugState.httpStatus,
      httpStatusText: debugState.httpStatusText,
      errorMessage: debugState.errorMessage,
      errorBody: debugState.errorBody,
      trace: debugState.trace,
      resultSummary: result
        ? {
            routing: result.routing,
            validation: result.validation,
            fraud_signals: result.fraud_signals,
            citations_count: result.citations?.length || 0,
          }
        : null,
    };
    try {
      await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
      setCopyMsg("Copied debug payload.");
    } catch {
      setCopyMsg("Copy failed. Clipboard permission denied.");
    }
  }

  async function ingestSource(event) {
    event.preventDefault();
    setIngestMsg("");
    if (!sourceText.trim() && !sourceFile) {
      setIngestMsg("Enter source text or select a file.");
      return;
    }
    setIngesting(true);
    try {
      let response;
      if (sourceFile) {
        const formData = new FormData();
        formData.append("file", sourceFile);
        formData.append("title", sourceFile.name);
        formData.append("kind", "claim_photo");
        response = await fetch(`${API_URL}/sources`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${API_URL}/sources`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: sourceText, title: "Manual Policy Source" }),
        });
      }
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.detail || `HTTP ${response.status}`);
      }
      setIngestMsg(`Ingested ${body.source_id}. Total sources: ${body.total_sources}`);
      setLatestVision(body.vision_findings || null);
      setSourceText("");
      setSourceFile(null);
      setSourcePreview("");
    } catch (err) {
      setIngestMsg(err.message || "Ingestion failed");
    } finally {
      setIngesting(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <p className="eyebrow">AInsurance Ops Console</p>
        <h1>AI-Native Claims Triage for Modern Carriers</h1>
        <p>Submit a narrative, ground decisions with policy sources, and route claims in under 30 seconds.</p>
      </header>

      <section className="kpis">
        <div className="kpi"><span>Status</span><strong>{debugState.phase.toUpperCase()}</strong></div>
        <div className="kpi"><span>Latency</span><strong>{field(debugState.durationMs)} ms</strong></div>
        <div className="kpi"><span>Sources</span><strong>{field(result?.citations?.length || 0)} cited</strong></div>
      </section>

      <section className="layout">
        <form className="card panel" onSubmit={submitClaim}>
          <h2>Claim Form</h2>
          <label htmlFor="scenario">Sample scenarios</label>
          <select
            id="scenario"
            value={scenario}
            onChange={(e) => {
              const picked = SCENARIOS.find((s) => s.key === e.target.value);
              setScenario(e.target.value);
              if (picked) {
                setNarrative(picked.prompt);
              }
            }}
          >
            {SCENARIOS.map((item) => (
              <option key={item.key} value={item.key}>
                {item.label}
              </option>
            ))}
          </select>
          <label htmlFor="narrative">Claim narrative</label>
          <textarea
            id="narrative"
            value={narrative}
            onChange={(e) => setNarrative(e.target.value)}
            rows={12}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Processing..." : "Submit Claim"}
          </button>
          {error ? <p className="error">{error}</p> : null}
        </form>

        <form className="card panel" onSubmit={ingestSource}>
          <h2>Source Ingestion</h2>
          <label htmlFor="sourceText">Policy/source text</label>
          <textarea
            id="sourceText"
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            rows={8}
          />
          <label htmlFor="sourceFile">Or attach a file (single)</label>
          <input
            id="sourceFile"
            type="file"
            accept=".jpg,.jpeg,.png,.webp,.pdf,.txt,.md"
            onChange={(e) => {
              const file = e.target.files?.[0] || null;
              setSourceFile(file);
              setLatestVision(null);
              if (file && file.type.startsWith("image/")) {
                setSourcePreview(URL.createObjectURL(file));
              } else {
                setSourcePreview("");
              }
            }}
          />
          <p className="empty">Accepted: JPG, PNG, WEBP, PDF, TXT, MD (max 15MB)</p>
          {sourcePreview ? <img src={sourcePreview} alt="Upload preview" className="img-preview" /> : null}
          <button type="submit" disabled={ingesting}>
            {ingesting ? "Analyzing..." : "Upload & Analyze"}
          </button>
          {ingestMsg ? <p className="empty">{ingestMsg}</p> : null}
          {latestVision ? (
            <div className="section">
              <h3>Instant Image Analysis</h3>
              <p><strong>Drivable risk:</strong> {field(latestVision.drivable_risk)}</p>
              {(latestVision.damage_findings || []).map((f, idx) => (
                <p key={`${f.part}-${idx}`}>- {field(f.part)} ({field(f.severity)}): {field(f.confidence_note)}</p>
              ))}
            </div>
          ) : null}
        </form>

        <section className="card panel intake">
          <h2>Intake Card</h2>
          {!result ? <p className="empty">Submit a claim to view structured results.</p> : null}

          {result ? (
            <>
              {missingFields.length > 0 ? (
                <div className="alert">
                  Missing fields: {missingFields.join(", ")}
                </div>
              ) : null}

              <div className="section">
                <h3>Claim Facts</h3>
                <p><strong>Policy:</strong> {field(result.claim?.policy_number)}</p>
                <p><strong>Date:</strong> {field(result.claim?.incident_date)}</p>
                <p><strong>Location:</strong> {field(result.claim?.incident_location)}</p>
                <p><strong>Description:</strong> {field(result.claim?.incident_description)}</p>
              </div>

              <div className="section">
                <h3>Classification</h3>
                <p><strong>Claim type:</strong> {field(result.classification?.claim_type)}</p>
                <p><strong>Severity:</strong> {field(result.classification?.severity)}</p>
                <p><strong>Line:</strong> {field(result.classification?.line_of_business)}</p>
              </div>

              <div className="section">
                <h3>Coverage</h3>
                <p><strong>Covered:</strong> {field(result.coverage?.is_covered)}</p>
                <p><strong>Rationale:</strong> {field(result.coverage?.coverage_rationale)}</p>
                <p><strong>Deductible:</strong> {field(result.coverage?.deductible_applicable)}</p>
              </div>

              <div className="section">
                <h3>Routing</h3>
                <p>
                  <span className={priorityClass(result.routing?.priority || 0)}>
                    {field(result.routing?.decision)}
                  </span>
                </p>
                <p><strong>Team:</strong> {field(result.routing?.team)}</p>
                <p><strong>Priority:</strong> {field(result.routing?.priority)}</p>
              </div>

              <div className="section">
                <h3>Fraud Signals</h3>
                <p><strong>Safety concerns:</strong> {field(result.fraud_signals?.safety_concerns)}</p>
                <p><strong>SIU referral:</strong> {field(result.fraud_signals?.siu_referral_required)}</p>
                <p><strong>Rationale:</strong> {field(result.fraud_signals?.fraud_rationale)}</p>
              </div>

              <div className="section">
                <h3>Citations</h3>
                {result.citations?.length ? result.citations.map((c) => (
                  <div key={c.source_id} className="citation">
                    <p><strong>{field(c.title)}</strong> ({field(c.source_id)})</p>
                    <p>{field(c.snippet)}</p>
                  </div>
                )) : <p>No sources retrieved.</p>}
              </div>

              <div className="section">
                <h3>Attachment Insights</h3>
                <p><strong>Drivable risk:</strong> {field(result.attachment_insights?.drivable_risk)}</p>
                <p><strong>Damage findings:</strong></p>
                {(result.attachment_insights?.damage_findings || []).length ? (
                  result.attachment_insights.damage_findings.map((f, idx) => (
                    <p key={`${f.part}-${idx}`}>- {field(f.part)} ({field(f.severity)}): {field(f.confidence_note)}</p>
                  ))
                ) : (
                  <p>No visual findings yet.</p>
                )}
                <p><strong>Recommended evidence:</strong> {(result.attachment_insights?.recommended_next_evidence || []).join(", ") || "None"}</p>
              </div>

              {result.trace ? (
                <details className="trace">
                  <summary>Debug trace</summary>
                  <pre>{JSON.stringify(result.trace, null, 2)}</pre>
                </details>
              ) : null}
            </>
          ) : null}

          <div className="section debug-card">
            <h3>Debug &amp; Progress</h3>
            <p>
              <span className={debugBadgeClass(debugState.phase)}>{debugState.phase.toUpperCase()}</span>
            </p>
            <p>
              <button type="button" className="mini-btn" onClick={copyDebugPayload}>Copy debug payload</button>
              {copyMsg ? <span className="copy-msg"> {copyMsg}</span> : null}
            </p>
            <p><strong>Endpoint:</strong> {API_URL}/claims</p>
            <p><strong>Started:</strong> {field(debugState.startedAt)}</p>
            <p><strong>Duration (ms):</strong> {field(debugState.durationMs)}</p>
            <p><strong>HTTP:</strong> {field(debugState.httpStatus)} {field(debugState.httpStatusText)}</p>
            {debugState.errorMessage ? <p><strong>Error:</strong> {debugState.errorMessage}</p> : null}

            {debugState.errorBody ? (
              <details className="trace" open>
                <summary>Error response body</summary>
                <pre>{debugState.errorBody}</pre>
              </details>
            ) : null}

            {debugState.trace ? (
              <details className="trace">
                <summary>Trace payload</summary>
                <pre>{JSON.stringify(debugState.trace, null, 2)}</pre>
              </details>
            ) : (
              <p className="empty">No trace returned yet. Backend debug is on by default; check request status/errors above.</p>
            )}
          </div>
        </section>
      </section>
    </main>
  );
}
