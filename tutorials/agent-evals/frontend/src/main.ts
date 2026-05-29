import "./styles.css";

type Meta = {
  models: string[];
  scenarios: Record<string, string>;
  rubrics: Record<string, string>;
  default_profile: Record<string, unknown>;
  default_config: Record<string, unknown>;
};

type Run = {
  run_id: string;
  created_at: string;
  status: string;
  dataset_id: string;
  metrics_summary: Record<string, number>;
  agent_profile?: Record<string, unknown>;
};

type CaseResult = {
  case_id: string;
  status: string;
  score: number;
  latency_ms: number;
  answer: string;
};

type RunDetail = {
  run: Run;
  cases: CaseResult[];
  events: Array<Record<string, unknown>>;
  active: boolean;
};

type Analytics = {
  summary: {
    total_runs: number;
    finished_runs: number;
    running_runs: number;
    failed_runs: number;
    total_cases: number;
    case_failures: number;
    weighted_pass_rate: number;
    avg_latency_ms: number;
  };
  by_model: Rollup[];
  by_scenario: Rollup[];
  recent_runs: Run[];
};

type Rollup = {
  name: string;
  runs: number;
  cases: number;
  failures: number;
  avg_pass_rate: number;
};

type Readout = {
  coverage: {
    models: number;
    scenarios: number;
    total_cases: number;
    weighted_pass_rate: number;
    avg_latency_ms: number;
    failures: number;
  };
  readiness: "demo_ready" | "promising" | "not_ready";
  narrative: string;
  leaderboard: Array<{
    model: string;
    scenarios: number;
    pass_rate: number;
    avg_score: number;
    avg_latency_ms: number;
    failed: number;
  }>;
  matrix: Array<{
    run_id: string;
    model: string;
    scenario: string;
    status: string;
    pass_rate: number;
    avg_score: number;
    avg_latency_ms: number;
    passed: number;
    failed: number;
    total_cases: number;
  }>;
};

type AuditEvent = {
  run_id: string;
  model: string;
  scenario: string;
  event_type: string;
  case_id: string;
  status: string;
  timestamp: string;
};

type SupportResponse = {
  answer: string;
  model: string;
  steps: Array<{
    step_idx: number;
    summary: string;
    tool_name: string | null;
    tool_output: string | null;
    duration_ms: number;
  }>;
};

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "";

const state: {
  meta: Meta | null;
  analytics: Analytics | null;
  audit: AuditEvent[];
  runs: Run[];
  selectedRunId: string | null;
  compareRunIds: string[];
  selectedModels: string[];
  selectedScenarios: string[];
  selectedRubric: string;
  selectedModel: string;
  selectedScenario: string;
  detail: RunDetail | null;
  readout: Readout | null;
  supportPrompt: string;
  supportResponse: SupportResponse | null;
  busy: boolean;
} = {
  meta: null,
  analytics: null,
  audit: [],
  runs: [],
  selectedRunId: null,
  compareRunIds: [],
  selectedModels: [],
  selectedScenarios: [],
  selectedRubric: "balanced",
  selectedModel: "rule-based-v1",
  selectedScenario: "tutorial_basics_v1",
  detail: null,
  readout: null,
  supportPrompt: "From tutorial facts, what framework powers the console?",
  supportResponse: null,
  busy: false
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}

function pct(value = 0): string {
  return `${(value * 100).toFixed(1)}%`;
}

function readinessLabel(value?: string): string {
  if (value === "demo_ready") return "Operational";
  if (value === "promising") return "Watch";
  if (value === "not_ready") return "Incident";
  return "No batch";
}

function profilePayload(model: string): Record<string, unknown> {
  return {
    ...(state.meta?.default_profile ?? {}),
    model,
    enabled_tools: ["calculator", "lookup", "format_json"]
  };
}

function configPayload(scenario: string): Record<string, unknown> {
  return {
    ...(state.meta?.default_config ?? {}),
    dataset_id: scenario,
    rubric_variant: state.selectedRubric,
    fail_fast: false
  };
}

async function loadMeta(): Promise<void> {
  state.meta = await request<Meta>("/api/meta");
  state.selectedModels = state.meta.models.slice(0, 2);
  state.selectedScenarios = Object.keys(state.meta.scenarios);
  state.selectedModel = state.meta.models[0];
  state.selectedScenario = Object.keys(state.meta.scenarios)[0];
  state.selectedRubric = Object.keys(state.meta.rubrics)[0];
}

async function refreshRuns(): Promise<void> {
  const data = await request<{ runs: Run[] }>("/api/runs?limit=100");
  state.runs = data.runs;
  if (!state.selectedRunId && state.runs.length) state.selectedRunId = state.runs[0].run_id;
}

async function loadOpsData(): Promise<void> {
  state.analytics = await request<Analytics>("/api/analytics?limit=100");
  state.audit = (await request<{ events: AuditEvent[] }>("/api/audit?limit=60")).events;
}

async function loadDetail(): Promise<void> {
  state.detail = state.selectedRunId ? await request<RunDetail>(`/api/runs/${state.selectedRunId}`) : null;
}

async function loadReadout(): Promise<void> {
  state.readout = state.compareRunIds.length
    ? await request<Readout>("/api/vc-readout", { method: "POST", body: JSON.stringify(state.compareRunIds) })
    : null;
}

async function hydrate(): Promise<void> {
  await refreshRuns();
  await loadOpsData();
  await loadDetail();
  await loadReadout();
  state.busy = false;
  render();
}

async function startSingleRun(): Promise<void> {
  state.busy = true;
  render();
  const data = await request<{ run_id: string }>("/api/runs", {
    method: "POST",
    body: JSON.stringify({ profile: profilePayload(state.selectedModel), config: configPayload(state.selectedScenario) })
  });
  state.selectedRunId = data.run_id;
  state.compareRunIds = [data.run_id];
  await hydrate();
}

async function startMatrixRun(): Promise<void> {
  state.busy = true;
  render();
  const data = await request<{ run_ids: string[] }>("/api/matrix-runs", {
    method: "POST",
    body: JSON.stringify({
      profile: profilePayload(state.selectedModel),
      config: configPayload(state.selectedScenario),
      models: state.selectedModels,
      scenarios: state.selectedScenarios
    })
  });
  state.compareRunIds = data.run_ids;
  state.selectedRunId = data.run_ids[0] ?? null;
  await hydrate();
}

async function askSupport(): Promise<void> {
  state.busy = true;
  render();
  state.supportResponse = await request<SupportResponse>("/api/support", {
    method: "POST",
    body: JSON.stringify({ prompt: state.supportPrompt, profile: profilePayload(state.selectedModel) })
  });
  state.busy = false;
  render();
}

function updateMultiSelect(select: HTMLSelectElement): string[] {
  return Array.from(select.selectedOptions).map((option) => option.value);
}

function metric(label: string, value: string, sub = ""): string {
  return `<div class="metric"><span>${label}</span><strong>${value}</strong><small>${sub}</small></div>`;
}

function renderShell(): string {
  return `
    <header class="topbar">
      <div>
        <strong>EvalOps Console</strong>
        <span>AI engineering, AIOps, and admin monitoring</span>
      </div>
      <nav>
        <a href="#analytics">Analytics</a>
        <a href="#batch">Batch</a>
        <a href="#observability">Observability</a>
        <a href="#audit">Audit</a>
        <a href="#support">Support</a>
      </nav>
    </header>
  `;
}

function renderControls(): string {
  if (!state.meta) return "";
  const scenarioOptions = Object.entries(state.meta.scenarios)
    .map(([id, label]) => `<option value="${id}" ${id === state.selectedScenario ? "selected" : ""}>${label}</option>`)
    .join("");
  const rubricOptions = Object.entries(state.meta.rubrics)
    .map(([id, label]) => `<option value="${id}" ${id === state.selectedRubric ? "selected" : ""}>${label}</option>`)
    .join("");
  const modelOptions = state.meta.models
    .map((model) => `<option value="${model}" ${model === state.selectedModel ? "selected" : ""}>${model}</option>`)
    .join("");
  const matrixModelOptions = state.meta.models
    .map((model) => `<option value="${model}" ${state.selectedModels.includes(model) ? "selected" : ""}>${model}</option>`)
    .join("");
  const matrixScenarioOptions = Object.entries(state.meta.scenarios)
    .map(([id, label]) => `<option value="${id}" ${state.selectedScenarios.includes(id) ? "selected" : ""}>${label}</option>`)
    .join("");

  return `
    <section class="panel" id="batch" data-testid="batch-control-panel">
      <div class="panel-title"><span>Batch Control</span><strong>${state.busy ? "running" : "ready"}</strong></div>
      <div class="form-grid">
        <label>Primary model<select id="selected-model">${modelOptions}</select></label>
        <label>Primary scenario<select id="selected-scenario">${scenarioOptions}</select></label>
        <label>Rubric<select id="selected-rubric">${rubricOptions}</select></label>
        <label>Matrix models<select id="matrix-models" multiple size="3">${matrixModelOptions}</select></label>
        <label>Matrix scenarios<select id="matrix-scenarios" multiple size="3">${matrixScenarioOptions}</select></label>
      </div>
      <div class="button-row">
        <button id="run-single" ${state.busy ? "disabled" : ""}>Run Interactive Eval</button>
        <button id="run-matrix" class="primary" ${state.busy ? "disabled" : ""}>Run Batch Matrix</button>
      </div>
    </section>
  `;
}

function renderAnalytics(): string {
  const summary = state.analytics?.summary;
  return `
    <section class="hero-panel" id="analytics">
      <div>
        <p class="eyebrow">Production readiness</p>
        <h1>Operate model quality like infrastructure.</h1>
        <p>Batch evaluation, observability, audit evidence, and interactive support for AI engineering and AIOps teams.</p>
      </div>
      <div class="status-card ${state.readout?.readiness ?? "empty"}">
        <span>${readinessLabel(state.readout?.readiness)}</span>
        <strong>${state.readout ? pct(state.readout.coverage.weighted_pass_rate) : pct(summary?.weighted_pass_rate ?? 0)}</strong>
        <small>${state.readout?.narrative ?? "Run a batch matrix to generate release readiness evidence."}</small>
      </div>
    </section>
    <section class="metrics-grid">
      ${metric("Runs", String(summary?.total_runs ?? 0), `${summary?.running_runs ?? 0} running`)}
      ${metric("Cases", String(summary?.total_cases ?? 0), `${summary?.case_failures ?? 0} failures`)}
      ${metric("Pass Rate", pct(summary?.weighted_pass_rate ?? 0), "weighted")}
      ${metric("Latency", `${summary?.avg_latency_ms ?? 0} ms`, "fleet avg")}
    </section>
  `;
}

function renderRollups(): string {
  const models = state.analytics?.by_model ?? [];
  const scenarios = state.analytics?.by_scenario ?? [];
  const rows = (items: Rollup[]) =>
    items
      .map(
        (row) => `
          <tr>
            <td>${row.name}</td>
            <td>${row.runs}</td>
            <td>${row.cases}</td>
            <td>${pct(row.avg_pass_rate)}</td>
            <td>${row.failures}</td>
          </tr>`
      )
      .join("");
  return `
    <div class="split">
      <section class="panel" data-testid="model-analytics-panel">
        <div class="panel-title"><span>Model Analytics</span><strong>${models.length}</strong></div>
        <table><thead><tr><th>Model</th><th>Runs</th><th>Cases</th><th>Pass</th><th>Fail</th></tr></thead><tbody>${rows(models) || `<tr><td colspan="5">No data.</td></tr>`}</tbody></table>
      </section>
      <section class="panel" data-testid="scenario-analytics-panel">
        <div class="panel-title"><span>Scenario Analytics</span><strong>${scenarios.length}</strong></div>
        <table><thead><tr><th>Scenario</th><th>Runs</th><th>Cases</th><th>Pass</th><th>Fail</th></tr></thead><tbody>${rows(scenarios) || `<tr><td colspan="5">No data.</td></tr>`}</tbody></table>
      </section>
    </div>
  `;
}

function renderObservability(): string {
  const matrix = state.readout?.matrix ?? [];
  return `
    <section class="panel" id="observability" data-testid="observability-panel">
      <div class="panel-title"><span>Observability Matrix</span><strong>${matrix.length}</strong></div>
      <table>
        <thead><tr><th>Model</th><th>Scenario</th><th>Status</th><th>Pass</th><th>Score</th><th>Latency</th><th>Failures</th></tr></thead>
        <tbody>
          ${matrix
            .map(
              (row) => `
            <tr>
              <td>${row.model}</td>
              <td>${state.meta?.scenarios[row.scenario] ?? row.scenario}</td>
              <td><span class="pill ${row.status}">${row.status}</span></td>
              <td>${pct(row.pass_rate)}</td>
              <td>${row.avg_score.toFixed(3)}</td>
              <td>${row.avg_latency_ms} ms</td>
              <td>${row.failed}</td>
            </tr>`
            )
            .join("") || `<tr><td colspan="7">Run a batch matrix to populate live observability.</td></tr>`}
        </tbody>
      </table>
    </section>
  `;
}

function renderEvidence(): string {
  const cases = state.detail?.cases ?? [];
  return `
    <div class="split">
      <section class="panel" data-testid="run-history-panel">
        <div class="panel-title"><span>Run History</span><strong>${state.runs.length}</strong></div>
        <div class="run-list">
          ${state.runs
            .slice(0, 12)
            .map(
              (run) => `
              <button class="run-row ${run.run_id === state.selectedRunId ? "active" : ""}" data-run-id="${run.run_id}">
                <span>${run.dataset_id}</span><strong>${pct(run.metrics_summary?.pass_rate ?? 0)}</strong><small>${run.status}</small>
              </button>`
            )
            .join("") || `<p class="muted">No runs yet.</p>`}
        </div>
      </section>
      <section class="panel" data-testid="case-evidence-panel">
        <div class="panel-title"><span>Case Evidence</span><strong>${state.detail?.run.run_id ?? "none"}</strong></div>
        <table><thead><tr><th>Case</th><th>Status</th><th>Score</th><th>Latency</th><th>Answer</th></tr></thead>
        <tbody>${cases
          .map(
            (row) => `<tr><td>${row.case_id}</td><td><span class="pill ${row.status}">${row.status}</span></td><td>${row.score.toFixed(3)}</td><td>${row.latency_ms} ms</td><td>${row.answer}</td></tr>`
          )
          .join("") || `<tr><td colspan="5">Select a run to inspect case evidence.</td></tr>`}</tbody></table>
      </section>
    </div>
  `;
}

function renderAudit(): string {
  return `
    <section class="panel" id="audit" data-testid="audit-panel">
      <div class="panel-title"><span>Audit Trail</span><strong>${state.audit.length}</strong></div>
      <table><thead><tr><th>Timestamp</th><th>Event</th><th>Run</th><th>Model</th><th>Scenario</th><th>Status</th></tr></thead>
      <tbody>${state.audit
        .slice(0, 18)
        .map(
          (event) => `<tr><td>${event.timestamp}</td><td>${event.event_type}</td><td>${event.run_id}</td><td>${event.model}</td><td>${event.scenario}</td><td>${event.status}</td></tr>`
        )
        .join("") || `<tr><td colspan="6">No audit events yet.</td></tr>`}</tbody></table>
    </section>
  `;
}

function renderSupport(): string {
  const steps = state.supportResponse?.steps ?? [];
  return `
    <section class="panel" id="support" data-testid="support-panel">
      <div class="panel-title"><span>Interactive Support</span><strong>${state.supportResponse?.model ?? state.selectedModel}</strong></div>
      <div class="support-grid">
        <textarea id="support-prompt" rows="5">${state.supportPrompt}</textarea>
        <div>
          <button id="ask-support" class="primary" ${state.busy ? "disabled" : ""}>Ask Agent</button>
          <div class="answer-box" data-testid="support-answer"><span>Answer</span><strong>${state.supportResponse?.answer ?? "No support response yet."}</strong></div>
        </div>
      </div>
      <table><thead><tr><th>Step</th><th>Summary</th><th>Tool</th><th>Output</th><th>Latency</th></tr></thead>
      <tbody>${steps
        .map(
          (step) => `<tr><td>${step.step_idx}</td><td>${step.summary}</td><td>${step.tool_name ?? "direct"}</td><td>${step.tool_output ?? ""}</td><td>${step.duration_ms} ms</td></tr>`
        )
        .join("") || `<tr><td colspan="5">Ask the agent to inspect tool use and response behavior.</td></tr>`}</tbody></table>
    </section>
  `;
}

function render(): void {
  const app = document.querySelector<HTMLDivElement>("#app");
  if (!app) return;
  app.innerHTML = `
    ${renderShell()}
    <main>
      ${renderAnalytics()}
      ${renderControls()}
      ${renderRollups()}
      ${renderObservability()}
      ${renderEvidence()}
      ${renderAudit()}
      ${renderSupport()}
    </main>
  `;
  bindEvents();
}

function bindEvents(): void {
  document.querySelector<HTMLSelectElement>("#selected-model")?.addEventListener("change", (event) => {
    state.selectedModel = (event.target as HTMLSelectElement).value;
  });
  document.querySelector<HTMLSelectElement>("#selected-scenario")?.addEventListener("change", (event) => {
    state.selectedScenario = (event.target as HTMLSelectElement).value;
  });
  document.querySelector<HTMLSelectElement>("#selected-rubric")?.addEventListener("change", (event) => {
    state.selectedRubric = (event.target as HTMLSelectElement).value;
  });
  document.querySelector<HTMLSelectElement>("#matrix-models")?.addEventListener("change", (event) => {
    state.selectedModels = updateMultiSelect(event.target as HTMLSelectElement);
  });
  document.querySelector<HTMLSelectElement>("#matrix-scenarios")?.addEventListener("change", (event) => {
    state.selectedScenarios = updateMultiSelect(event.target as HTMLSelectElement);
  });
  document.querySelector<HTMLTextAreaElement>("#support-prompt")?.addEventListener("input", (event) => {
    state.supportPrompt = (event.target as HTMLTextAreaElement).value;
  });
  document.querySelector("#run-single")?.addEventListener("click", () => void startSingleRun());
  document.querySelector("#run-matrix")?.addEventListener("click", () => void startMatrixRun());
  document.querySelector("#ask-support")?.addEventListener("click", () => void askSupport());
  document.querySelectorAll<HTMLButtonElement>(".run-row").forEach((button) => {
    button.addEventListener("click", async () => {
      state.selectedRunId = button.dataset.runId ?? null;
      await loadDetail();
      render();
    });
  });
}

async function boot(): Promise<void> {
  await loadMeta();
  await hydrate();
  window.setInterval(async () => {
    const active = state.runs.some((run) => run.status === "running");
    if (active || state.busy) await hydrate();
  }, 2500);
}

boot().catch((error) => {
  const app = document.querySelector<HTMLDivElement>("#app");
  if (app) app.innerHTML = `<main class="fatal"><h1>Unable to load console</h1><pre>${String(error)}</pre></main>`;
});
