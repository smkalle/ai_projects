# Talk to My Agent — Conversation‑Driven APIs (with MCP)

> **For**: AI/Platform engineers building APIs that LLM agents can use autonomously.  
> **What you’ll build**: An *agent‑friendly* REST API and an **MCP server** that wraps it as tools, including *reverse prompts*, HATEOAS‑style next steps, and observability with OpenTelemetry.  
> **Why**: When agents get `[]`, they often stop. Treat responses as **reverse prompts** that keep the conversation going.

---

## Table of Contents

- [Concepts](#concepts)  
- [Architecture](#architecture)  
- [Prerequisites](#prerequisites)  
- [Step 1 — Scaffold the API](#step-1--scaffold-the-api)  
- [Step 2 — Reverse‑Prompt Responses](#step-2--reverse-prompt-responses)  
- [Step 3 — HATEOAS Next Actions](#step-3--hateoas-next-actions)  
- [Step 4 — Observability (OpenTelemetry)](#step-4--observability-opentelemetry)  
- [Step 5 — MCP Server Wrapper](#step-5--mcp-server-wrapper)  
- [Step 6 — Try It from an MCP Client](#step-6--try-it-from-an-mcp-client)  
- [Step 7 — Hardening & Safety](#step-7--hardening--safety)  
- [Step 8 — Evaluation & Iteration](#step-8--evaluation--iteration)  
- [Appendix — Checklists & Patterns](#appendix--checklists--patterns)  
- [References](#references)

---

## Concepts

**Conversation‑driven API**: Design responses to *advance a dialog*. Instead of a silent `[]`, return:  
- **what happened** (diagnostic),  
- **why it might happen** (context),  
- **what to try next** (concrete suggestions + ready‑to‑call links).

**Reverse prompt**: Structured hints that guide the agent’s *next* call. Treat every response like a mini‑prompt and include actionable next‑steps.

**MCP (Model Context Protocol)**: An open protocol for exposing **tools**, **resources**, and **prompts** to LLMs. We’ll build a Node/TS MCP server that wraps our API so any MCP‑capable client can use it.

---

## Architecture

```
apps/
  api/                       # Express (TypeScript) API designed for agents
    src/
      routes/usage.ts        # Domain: code-usage insights from traces
      lib/otel.ts            # OpenTelemetry setup
      server.ts
    package.json
servers/
  mcp-usage/                 # MCP server that exposes API as tools
    src/
      index.ts
      schema.ts              # Zod/JSON Schema for tool inputs/outputs
    package.json
```

**Flow**: Agent → MCP client → MCP server → our API → back with reverse‑prompt response (diagnostics + next actions).

---

## Prerequisites

- Node.js 18+ and pnpm or npm
- Basic TypeScript
- Docker (optional for running OTEL Collector)
- An MCP‑capable client (e.g., Claude Desktop, Cursor, or MCP Inspector)

```bash
mkdir -p talk-to-my-agent/{apps/api,servers/mcp-usage}
cd talk-to-my-agent
```

---

## Step 1 — Scaffold the API

Install dependencies:

```bash
cd apps/api
pnpm init -y
pnpm add express zod cors pino pino-pretty
pnpm add -D typescript ts-node @types/node @types/express nodemon
pnpm add @opentelemetry/api @opentelemetry/sdk-node \
        @opentelemetry/auto-instrumentations-node \
        @opentelemetry/exporter-trace-otlp-http
```

`tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "CommonJS",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true
  }
}
```

`package.json` scripts:

```json
{
  "scripts": {
    "dev": "nodemon --watch src --exec ts-node src/server.ts",
    "build": "tsc -p .",
    "start": "node dist/server.js"
  }
}
```

`src/server.ts`:

```ts
import express from "express";
import cors from "cors";
import pino from "pino";
import usageRouter from "./routes/usage";

const app = express();
const log = pino();
app.use(cors());
app.use(express.json());

app.use("/usage", usageRouter);

app.get("/health", (_req, res) => res.json({ ok: true }));

const port = process.env.PORT || 4001;
app.listen(port, () => log.info({ port }, "API listening"));
```

`src/routes/usage.ts` (domain example: function usage from traces):

```ts
import { Router } from "express";
import { z } from "zod";

const router = Router();

// --- Request/Response Schemas ---------------------------------------------
const QuerySchema = z.object({
  functionName: z.string().min(1),
  className: z.string().optional(),
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional()
});

const LinkSchema = z.object({
  rel: z.string(),                 // e.g., "retry", "alternate", "inspect-endpoint"
  href: z.string(),                // URL to call
  method: z.enum(["GET", "POST"]), // HTTP method
  title: z.string().optional()     // human/agent hint
});

const ReversePromptSchema = z.object({
  message: z.string(),             // diagnostic message
  why: z.string().optional(),      // context / likely cause
  suggestedNextSteps: z.array(z.string()).optional(),
  links: z.array(LinkSchema).optional()
});

const UsagePointSchema = z.object({
  timestamp: z.string(),
  count: z.number()
});

const UsageResponseSchema = z.object({
  ok: z.literal(true),
  query: QuerySchema,
  series: z.array(UsagePointSchema),
  reversePrompt: ReversePromptSchema.optional()
});

const NoDataResponseSchema = z.object({
  ok: z.literal(false),
  query: QuerySchema,
  code: z.literal("NO_DATA"),
  reversePrompt: ReversePromptSchema
});

// --- Fake store for tutorial ----------------------------------------------
const FAKE = {
  "OrderService.placeOrder": [
    { timestamp: "2025-07-27T10:00:00Z", count: 51 },
    { timestamp: "2025-07-28T10:00:00Z", count: 62 }
  ]
};

// --- Helpers ---------------------------------------------------------------
function buildLink(rel: string, href: string, method: "GET"|"POST", title?: string) {
  return { rel, href, method, title };
}

// --- Routes ----------------------------------------------------------------
router.post("/function-usage", (req, res) => {
  const parse = QuerySchema.safeParse(req.body);
  if (!parse.success) {
    return res.status(400).json({
      ok: false,
      code: "BAD_REQUEST",
      reversePrompt: {
        message: "Invalid input for /usage/function-usage",
        suggestedNextSteps: [
          "Provide 'functionName' (e.g., 'OrderService.placeOrder')",
          "Optionally include 'className' to disambiguate",
          "Provide ISO8601 'from'/'to' timestamps"
        ],
        links: [
          buildLink("schema", "/usage/schema", "GET", "Retrieve JSON Schemas"),
        ]
      }
    });
  }

  const q = parse.data;
  const key = q.className ? `${q.className}.${q.functionName}` : q.functionName;
  const series = FAKE[key] || [];

  if (series.length === 0) {
    return res.status(200).json({
      ok: false,
      code: "NO_DATA",
      query: q,
      reversePrompt: {
        message: "No trace data found for the given function.",
        why: "Function may not be called, or not instrumented with OTEL spans.",
        suggestedNextSteps: [
          "Search for endpoints that call this function (HTTP handlers, jobs, consumers).",
          "Try /usage/endpoint-trace with a candidate route (e.g., POST /orders).",
          "Suggest manual instrumentation using OTEL annotations or code, per language."
        ],
        links: [
          buildLink(
            "alternate",
            "/usage/search-endpoints?functionName=" + encodeURIComponent(q.functionName),
            "GET",
            "Find endpoints that might call this function"
          ),
          buildLink("related", "/usage/endpoint-trace", "POST", "Get a sample trace for an endpoint")
        ]
      }
    } satisfies z.infer<typeof NoDataResponseSchema>);
  }

  return res.status(200).json({
    ok: true,
    query: q,
    series,
    reversePrompt: {
      message: "Usage series returned. Consider exploring endpoint traces for hotspots.",
      suggestedNextSteps: [
        "Call /usage/endpoint-trace on the most active route for code-level context.",
        "If investigating regressions, compare 'from'/'to' windows with a baseline."
      ],
      links: [
        buildLink("related", "/usage/endpoint-trace", "POST", "Trace an endpoint")
      ]
    }
  } satisfies z.infer<typeof UsageResponseSchema>);
});

router.get("/schema", (_req, res) => {
  res.json({
    QuerySchema: QuerySchema.toJSON(),
    UsageResponseSchema: UsageResponseSchema.toJSON(),
    NoDataResponseSchema: NoDataResponseSchema.toJSON()
  });
});

router.get("/search-endpoints", (req, res) => {
  const { functionName } = req.query as { functionName?: string };
  if (!functionName) return res.status(400).json({ error: "functionName is required" });
  // Fake match for tutorial
  res.json({
    matches: [
      { route: "POST /orders", method: "POST", handler: "OrderController.create" }
    ],
    reversePrompt: {
      message: "Candidate endpoints that might call the function.",
      suggestedNextSteps: [
        "Use /usage/endpoint-trace with the route to fetch a representative trace."
      ],
      links: [
        buildLink("related", "/usage/endpoint-trace", "POST", "Trace the 'POST /orders' endpoint")
      ]
    }
  });
});

router.post("/endpoint-trace", (req, res) => {
  const { route } = req.body || {};
  if (!route) {
    return res.status(400).json({
      error: "route is required",
      reversePrompt: {
        message: "Provide an HTTP route (e.g., 'POST /orders') to fetch a sample trace.",
        suggestedNextSteps: [
          "If unsure, call /usage/search-endpoints to discover routes."
        ],
        links: [
          buildLink("alternate", "/usage/search-endpoints?functionName=OrderService.placeOrder", "GET")
        ]
      }
    });
  }
  res.json({
    traceId: "trace-123",
    spans: [
      { name: "POST /orders", start: "2025-07-28T10:00:00Z", durationMs: 45 },
      { name: "OrderService.placeOrder", start: "2025-07-28T10:00:20Z", durationMs: 10 }
    ],
    reversePrompt: {
      message: "Sample trace ready.",
      suggestedNextSteps: [
        "If the function is missing, recommend manual OTEL instrumentation.",
        "Correlate this trace with usage spikes in /usage/function-usage."
      ]
    }
  });
});

export default router;
```

---

## Step 2 — Reverse‑Prompt Responses

**Goal**: Never dead‑end the agent. For each non‑terminal outcome, return a `reversePrompt` object:

```ts
type ReversePrompt = {
  message: string;
  why?: string;
  suggestedNextSteps?: string[];
  links?: { rel: string; href: string; method: "GET"|"POST"; title?: string }[];
};
```

- Use **diagnostics** (`message`, `why`) to explain outcomes.  
- Provide **Next Steps** + **Links** that are *safe* to call immediately (HATEOAS: see below).  
- Keep it **short** and **deterministic**—agents prefer explicit structure over prose.

---

## Step 3 — HATEOAS Next Actions

Return **actionable links** (`rel`, `href`, `method`) with stable meanings:

- `retry`: Same call with tweaked params.
- `alternate`: A related call that could help (e.g., search endpoints).
- `related`: Optional explorations (e.g., trace an endpoint).
- `schema`: Where to fetch JSON Schema to self‑calibrate.

This helps agents plan sequences without guessing URLs or shapes.

---

## Step 4 — Observability (OpenTelemetry)

`src/lib/otel.ts`:

```ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";

export function initOtel() {
  const exporter = new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT || "http://localhost:4318/v1/traces"
  });
  const sdk = new NodeSDK({
    traceExporter: exporter,
    instrumentations: [getNodeAutoInstrumentations()]
  });
  sdk.start();
  process.on("SIGTERM", () => sdk.shutdown());
}
```

Call `initOtel()` from `server.ts` (top of file) to emit spans. Use traces to **teach** the agent (e.g., link from a response to a specific trace or error event).

---

## Step 5 — MCP Server Wrapper

Create server:

```bash
cd ../../servers/mcp-usage
pnpm init -y
pnpm add zod node-fetch @modelcontextprotocol/sdk
pnpm add -D typescript ts-node @types/node
```

`tsconfig.json` (similar to API).

`src/schema.ts`:

```ts
import { z } from "zod";

export const FunctionUsageInput = z.object({
  functionName: z.string().min(1),
  className: z.string().optional(),
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional()
});

export type FunctionUsageInput = z.infer<typeof FunctionUsageInput>;
```

`src/index.ts`:

```ts
import { Server } from "@modelcontextprotocol/sdk/server/index";
import { z } from "zod";
import fetch from "node-fetch";
import { FunctionUsageInput } from "./schema";

const API_URL = process.env.API_URL || "http://localhost:4001";

const server = new Server(
  {
    name: "mcp-usage",
    version: "0.1.0"
  },
  {
    capabilities: {
      tools: {},
      prompts: {},
      resources: {}
    }
  }
);

server.tool(
  "getFunctionUsage",
  "Return usage series and reverse-prompt guidance for a function",
  FunctionUsageInput,
  async (args) => {
    const res = await fetch(`${API_URL}/usage/function-usage`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(args)
    });
    const json = await res.json();
    return {
      content: [
        {
          type: "json",
          json
        }
      ]
    };
  }
);

// Optional: expose a helper tool to search endpoints
server.tool(
  "searchEndpoints",
  "Find endpoints that might call a function",
  z.object({ functionName: z.string().min(1) }),
  async (args) => {
    const u = new URL(`${API_URL}/usage/search-endpoints`);
    u.searchParams.set("functionName", args.functionName);
    const res = await fetch(u.toString());
    const json = await res.json();
    return { content: [{ type: "json", json }] };
  }
);

server.start();
```

**Run**:

```bash
# Terminal 1
cd apps/api && pnpm dev

# Terminal 2
cd servers/mcp-usage && ts-node src/index.ts
```

---

## Step 6 — Try It from an MCP Client

- If you use **MCP Inspector**:  
  ```bash
  npx @modelcontextprotocol/inspector ts-node servers/mcp-usage/src/index.ts
  ```
  Call `getFunctionUsage` with `{"functionName":"OrderService.placeOrder"}`.  
  Then try a missing function to see the **NO_DATA** reverse prompt with next steps.

- If you use a desktop client that supports MCP, register this server per client docs and invoke tools from the UI.

---

## Step 7 — Hardening & Safety

- **Pagination & Windows**: Enforce limits (`from`/`to`, `limit`, `nextToken`) and include links to fetch next pages.  
- **Ambiguity Handling**: When multiple matches are found, return a `DISAMBIGUATE` response with options + links.  
- **Rate Limits**: Return `429` with `Retry-After` and a `retry` HATEOAS link.  
- **Idempotency**: Encourage idempotent GETs; for POSTs, accept an `idempotencyKey`.  
- **Schema Contracts**: Expose `/usage/schema` and keep it authoritative for agents.  
- **Safety**: Validate all inputs with Zod; never return secrets; scrub PII in traces.  
- **Observability for Agents**: Emit structured events (e.g., `agent.hint.provided=true`) and include `traceId` in responses so agents can correlate.

---

## Step 8 — Evaluation & Iteration

Track **agent success rate** over sessions:  
- % of calls that end with *useful* outcomes (non-dead-end).  
- # of *follow‑on* calls taken via HATEOAS links.  
- Time‑to‑task and attempts‑to‑success.  
Run A/B on different `reversePrompt` wordings and link sets.

---

## Appendix — Checklists & Patterns

**Reverse Prompt Checklist**  
- [ ] Clear message (<= 1 sentence).  
- [ ] Optional “why” with 1–2 common causes.  
- [ ] 2–3 next steps, ordered from most likely to help.  
- [ ] Links: `retry`, `alternate`, `related`, `schema`.  
- [ ] Deterministic shape (no freeform HTML).

**Common Patterns**  
- `NO_DATA` → suggest discovery tools (search endpoints) or instrumentation.  
- `DISAMBIGUATE` → return choices with stable IDs + links.  
- `RETRYABLE_ERROR` → include backoff guidance (`Retry-After`, jitter).  
- `SECURITY_DENIED` → explain the policy and link to a least‑privilege path.

---

## References

- Model Context Protocol: https://modelcontextprotocol.io/  
- MCP Spec: https://modelcontextprotocol.io/specification/2025-06-18  
- Anthropic MCP docs: https://docs.anthropic.com/en/docs/mcp  
- NPM SDK: https://www.npmjs.com/package/@modelcontextprotocol/sdk  
- MCP Inspector: https://www.npmjs.com/package/@modelcontextprotocol/inspector

> This tutorial demonstrates the *conversation‑driven API* principle: **don’t dead‑end**— respond with diagnostics, causes, and next actions, plus links agents can follow immediately.

ts`:

```ts
import express from "express";
import cors from "cors";
import pino from "pino";
import { usageRouter } from "./routes/usage";

const app = express();
const logger = pino({ level: process.env.LOG_LEVEL || "info" });

app.use(cors());
app.use(express.json());

app.use("/usage", usageRouter);

// Healthz for agents to probe
app.get("/healthz", (_req, res) => res.json({ ok: true }));

const port = process.env.PORT || 3000;
app.listen(port, () => logger.info({ port }, "API listening"));
```

### Domain route: usage insights
We’ll simulate a tracing-backed service that answers, “How is function **X** used?”

`src/routes/usage.ts`:

```ts
import { Router } from "express";
import { z } from "zod";

export const usageRouter = Router();

// --- Schema for reverse-prompt response
const nextActionSchema = z.object({
  rel: z.enum(["related-endpoints", "trace-for-endpoint", "instrumentation-guide"]),
  title: z.string(),
  href: z.string(),           // absolute URL to call next (or MCP tool name if you prefer tool links)
  method: z.enum(["GET", "POST"]).default("GET"),
  params: z.record(z.any()).optional(),   // default params for agent
});

const diagnosticSchema = z.object({
  code: z.string(),     // e.g., NO_DATA
  message: z.string(),
  details: z.record(z.any()).optional(),
});

const usageResponseSchema = z.object({
  ok: z.boolean(),
  data: z.any(),
  diagnostics: z.array(diagnosticSchema).default([]),
  nextActions: z.array(nextActionSchema).default([]),
  meta: z.object({
    requestId: z.string().optional(),
    hint: z.string().optional(),          // a one-liner reverse prompt
    schemaVersion: z.string().default("1.0")
  }).default({ schemaVersion: "1.0" })
});

type UsageResponse = z.infer<typeof usageResponseSchema>;

// --- Fake store
const callsByFunction = new Map<string, number>([
  ["AuthController.login", 156],
  ["OrderService.placeOrder", 91],
]);

const endpointsByFunction = new Map<string, string[]>([
  ["OrderService.placeOrder", ["/api/orders POST", "/api/users/:id/orders GET"]]
]);

// Helpers
function ok(data: any, nextActions = [], hint?: string): UsageResponse {
  return { ok: true, data, diagnostics: [], nextActions, meta: { hint, schemaVersion: "1.0" } };
}

function noData(functionName: string): UsageResponse {
  const suggestions = [
    {
      rel: "related-endpoints",
      title: "Search endpoints that call this function",
      href: `/usage/related-endpoints?function=${encodeURIComponent(functionName)}`,
      method: "GET",
      params: { function: functionName }
    },
    {
      rel: "trace-for-endpoint",
      title: "Get traces for a specific endpoint",
      href: `/usage/trace-for-endpoint`,
      method: "POST",
      params: { route: "/api/orders" }
    },
    {
      rel: "instrumentation-guide",
      title: "Suggest manual instrumentation",
      href: `/usage/instrumentation-guide?lang=java`,
      method: "GET"
    }
  ] as const;

  return {
    ok: false,
    data: [],
    diagnostics: [{
      code: "NO_DATA",
      message: `No usage found for "${functionName}". It may not be called or lacks OTEL instrumentation.`,
      details: { functionName }
    }],
    nextActions: suggestions as any,
    meta: {
      hint: "Try related endpoints, fetch traces by route, or add manual instrumentation.",
      schemaVersion: "1.0"
    }
  };
}

// --- Routes
usageRouter.get("/", (req, res) => {
  const q = String(req.query.function ?? "").trim();

  if (!q) {
    return res.status(400).json({
      ok: false,
      data: null,
      diagnostics: [{ code: "BAD_INPUT", message: "Missing ?function= query parameter" }],
      nextActions: [{
        rel: "related-endpoints",
        title: "List known functions",
        href: "/usage/known-functions",
        method: "GET"
      }],
      meta: { hint: "Provide ?function=Fully.Qualified.Name" }
    } as UsageResponse);
  }

  const calls = callsByFunction.get(q);
  if (!calls) {
    return res.json(noData(q));
  }

  const next = endpointsByFunction.get(q)?.[0];
  return res.json(ok(
    { function: q, callsLast30d: calls },
    next ? [{
      rel: "trace-for-endpoint",
      title: `Fetch trace for likely endpoint using ${q}`,
      href: "/usage/trace-for-endpoint",
      method: "POST",
      params: { route: next.split(" ")[0] }
    }] : [],
    "You can also fetch traces for the top endpoint."
  ));
});

usageRouter.get("/known-functions", (_req, res) => {
  const list = Array.from(callsByFunction.keys());
  res.json(ok(list));
});

usageRouter.get("/related-endpoints", (req, res) => {
  const fn = String(req.query.function ?? "");
  const eps = endpointsByFunction.get(fn) ?? [];
  res.json(ok(eps, eps.length ? [{
    rel: "trace-for-endpoint",
    title: "Fetch trace for this endpoint",
    href: "/usage/trace-for-endpoint",
    method: "POST",
    params: { route: eps[0]?.split(" ")[0] }
  }] : [], eps.length ? "Choose an endpoint to trace." : "No related endpoints found."));
});

usageRouter.post("/trace-for-endpoint", (req, res) => {
  const route = String(req.body?.route ?? "");
  if (!route) {
    return res.status(400).json({
      ok: false,
      data: null,
      diagnostics: [{ code: "BAD_INPUT", message: "Missing body.route" }],
      nextActions: [{
        rel: "trace-for-endpoint",
        title: "Example request body",
        href: "/usage/trace-for-endpoint",
        method: "POST",
        params: { route: "/api/orders" }
      }],
      meta: { hint: "Provide the endpoint route to fetch traces." }
    } as UsageResponse);
  }

  // Fake trace
  res.json(ok({ route, spans: [{ id: "abc123", service: "orders", latencyMs: 123 }] }));
});

usageRouter.get("/instrumentation-guide", (_req, res) => {
  res.json(ok({
    java: "Use @WithSpan on methods and ensure OTEL exporter is configured.",
    python: "Use OpenTelemetry SDK; wrap functions with tracer.start_as_current_span."
  }));
});
```

Run the API:

```bash
pnpm dev
# GET http://localhost:3000/usage?function=OrderService.placeOrder
# GET http://localhost:3000/usage?function=Unknown.method   -> returns NO_DATA with nextActions
```

---

## Step 2 — Reverse‑Prompt Responses

**Design goal:** never dead‑end the agent. Every error/empty state returns:
- `diagnostics[]` (machine‑readable + natural language),
- `nextActions[]` (ready‑to‑call links with default params),
- a short `meta.hint` one‑liner.

**Error taxonomy (example):**
- `BAD_INPUT` → include example
- `NO_DATA` → offer alternative discovery path
- `AMBIGUOUS` → propose disambiguation keys
- `RATE_LIMIT` → include `retryAfterMs`

Tip: **keep fields stable** (schemaVersion) but content adaptive.

---

## Step 3 — HATEOAS Next Actions

Expose affordances as links with a `rel` that encodes intent. Agents don’t always know the map—give them the roads.

**Pattern:**
```json
{
  "nextActions": [
    { "rel": "related-endpoints", "title": "Search endpoints...", "href": "/usage/related-endpoints?function=Foo.bar", "method": "GET" },
    { "rel": "trace-for-endpoint", "title": "Get traces", "href": "/usage/trace-for-endpoint", "method": "POST", "params": { "route": "/api/orders" } }
  ]
}
```

---

## Step 4 — Observability (OpenTelemetry)

**Why**: Learn how agents struggle. Record inputs, status codes, which `rel` they pick next, and whether goals are met.

`src/lib/otel.ts` (minimal tracer setup):

```ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";

export function startTelemetry() {
  const exporter = new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || "http://localhost:4318/v1/traces"
  });
  const sdk = new NodeSDK({
    traceExporter: exporter,
    instrumentations: [getNodeAutoInstrumentations()]
  });
  sdk.start();
  return sdk;
}
```

Wire it in `server.ts`:

```ts
// at the top
import { startTelemetry } from "./lib/otel";
const otel = startTelemetry();
process.on("SIGTERM", () => otel.shutdown());
```

**Capture reverse‑prompt fields** in spans: add attributes like `diagnostics.count`, `nextActions.count`, `rel.first`, etc.

---

## Step 5 — MCP Server Wrapper

Create the MCP server:

```bash
cd ../../servers/mcp-usage
pnpm init -y
pnpm add @modelcontextprotocol/sdk zod undici
pnpm add -D typescript ts-node @types/node
```

`tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "CommonJS",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true
  }
}
```

`src/schema.ts`:

```ts
import { z } from "zod";

export const getUsageInput = z.object({
  function: z.string().describe("Fully qualified method, e.g., OrderService.placeOrder")
});
export type GetUsageInput = z.infer<typeof getUsageInput>;

export const usageResponse = z.object({
  ok: z.boolean(),
  data: z.any(),
  diagnostics: z.array(z.object({ code: z.string(), message: z.string() })),
  nextActions: z.array(z.object({
    rel: z.string(),
    title: z.string(),
    href: z.string(),
    method: z.string(),
    params: z.record(z.any()).optional()
  })),
  meta: z.object({ hint: z.string().optional(), schemaVersion: z.string().optional() })
});
export type UsageResponse = z.infer<typeof usageResponse>;
```

`src/index.ts`:

```ts
import { StdioServerTransport, Server } from "@modelcontextprotocol/sdk/server";
import { z } from "zod";
import { getUsageInput, usageResponse } from "./schema";
import { request } from "undici";

const API = process.env.API_BASE ?? "http://localhost:3000";

async function callApi(path: string, init?: RequestInit) {
  const url = `${API}${path}`;
  const res = await request(url, init as any);
  const body = await res.body.json();
  return body;
}

async function main() {
  const transport = new StdioServerTransport();
  const server = new Server(
    {
      name: "mcp-usage",
      version: "1.0.0"
    },
    { capabilities: { tools: {} } }
  );

  server.tool("getFunctionUsage", {
    description: "Get usage stats for a function and suggested next actions",
    inputSchema: getUsageInput,
    async invoke({ input }) {
      const q = input as z.infer<typeof getUsageInput>;
      const body = await callApi(`/usage?function=${encodeURIComponent(q.function)}`);
      const parsed = usageResponse.parse(body);
      return {
        content: [
          { type: "text", text: JSON.stringify(parsed, null, 2) }
        ]
      };
    }
  });

  server.tool("followNextAction", {
    description: "Follow a nextAction from a previous response (href+method+params)",
    inputSchema: z.object({
      href: z.string(),
      method: z.enum(["GET", "POST"]).default("GET"),
      params: z.record(z.any()).optional()
    }),
    async invoke({ input }) {
      const { href, method, params } = input as any;
      const init = method === "POST"
        ? { method: "POST", body: JSON.stringify(params ?? {}), headers: { "content-type": "application/json" } }
        : undefined;
      const path = href.startsWith("http") ? href.replace(API, "") : href;
      const body = await callApi(path, init);
      return { content: [{ type: "text", text: JSON.stringify(body, null, 2) }] };
    }
  });

  await server.connect(transport);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
```

Run the MCP server:

```bash
pnpm ts-node src/index.ts
```

---

## Step 6 — Try It from an MCP Client

- **MCP Inspector (CLI/UI)**

```bash
npx @modelcontextprotocol/inspector node ./dist/index.js
# or
npx @modelcontextprotocol/inspector pnpm ts-node src/index.ts
```

- **Ask the model**: “Use the `getFunctionUsage` tool for `OrderService.placeOrder` and, if `nextActions` exist, call `followNextAction`.”  
- On a `NO_DATA`, the agent will see `diagnostics` and actionable `nextActions` to continue.

---

## Step 7 — Hardening & Safety

- **Pagination**: include `page`, `pageSize`, `nextPageHref` in responses; surface as next actions.  
- **Ambiguity**: respond with `AMBIGUOUS` + `disambiguationKeys` (e.g., `service`, `env`) and include example calls.  
- **Rate limits**: return `429` with `retryAfterMs` and a next action to retry later.  
- **Input validation**: Zod on both API and MCP sides; echo normalized inputs.  
- **Idempotency**: accept an `Idempotency-Key` header for POSTs when side effects exist.  
- **Security**: sign `nextActions.href` or restrict to same-origin relative paths; verify auth per agent identity.  
- **Docs for agents**: keep `/openapi.json` minimal and add a short **“How to Use”** endpoint with examples.  

---

## Step 8 — Evaluation & Iteration

Track **agent success rate**:
- % of sessions that reach a terminal *goal* (e.g., retrieved trace for target endpoint).  
- Average **steps to success** (should go down).  
- **Drop-off points** where agents stop; add targeted reverse prompts there.  
- Telemetry dimensions: input shape, error code, first `rel` chosen, time to next call.

Run A/B on reverse‑prompt copy; optimize for fewer steps and higher success.

---

## Appendix — Checklists & Patterns

**Response Skeleton**

```json
{
  "ok": false,
  "data": [],
  "diagnostics": [{ "code": "NO_DATA", "message": "…reason…" }],
  "nextActions": [
    { "rel": "related-endpoints", "title": "…", "href": "/usage/related-endpoints?function=Foo.bar", "method": "GET" },
    { "rel": "trace-for-endpoint", "title": "…", "href": "/usage/trace-for-endpoint", "method": "POST", "params": { "route": "/api/orders" } }
  ],
  "meta": { "hint": "Try related endpoints or fetch traces for a likely route.", "schemaVersion": "1.0" }
}
```

**Agent‑Friendly Tips**
- Keep `title` imperative: “Fetch…”, “List…”, “Suggest…”.  
- Provide **ready‑to‑call** examples in `params`.  
- Include a short `hint` for quick summarization in the model’s chain of thought.  
- Use stable error codes; don’t overload `message`.  
- Prefer relative `href` to avoid exfiltration and simplify routing through MCP.

---

## References

- **MCP Introduction** — https://modelcontextprotocol.io/introduction  
- **MCP Specification** — https://modelcontextprotocol.io/specification/2025-06-18  
- **Anthropic docs: MCP** — https://docs.anthropic.com/en/docs/mcp  
- **TypeScript SDK (NPM)** — https://www.npmjs.com/package/@modelcontextprotocol/sdk  

> This tutorial demonstrates the “reverse prompt” idea for conversation‑driven APIs and shows an end‑to‑end path from API → MCP → Agent.

    }
  });
  }

  const count = callsByFunction.get(q);
  if (!count) {
    return res.status(200).json(noData(q));
  }

  const next = [];
  const eps = endpointsByFunction.get(q);
  if (eps?.length) {
    next.push({
      rel: "related-endpoints",
      title: "Endpoints that use this function",
      href: `/usage/related-endpoints?function=${encodeURIComponent(q)}`,
      method: "GET"
    });
  } else {
    next.push({
      rel: "instrumentation-guide",
      title: "Add manual instrumentation",
      href: `/usage/instrumentation-guide?lang=java`,
      method: "GET"
    });
  }

  return res.json({
    ok: true,
    data: { function: q, callsLast30d: count },
    diagnostics: [],
    nextActions: next,
    meta: { hint: "Inspect related endpoints or add instrumentation.", schemaVersion: "1.0" }
  });
});

usageRouter.get("/known-functions", (_req, res) => {
  res.json({ ok: true, data: Array.from(callsByFunction.keys()), diagnostics: [], nextActions: [] });
});

usageRouter.get("/related-endpoints", (req, res) => {
  const fn = String(req.query.function ?? "");
  res.json({
    ok: true,
    data: { function: fn, endpoints: endpointsByFunction.get(fn) ?? [] },
    diagnostics: [],
    nextActions: [{
      rel: "trace-for-endpoint",
      title: "Get traces for an endpoint",
      href: `/usage/trace-for-endpoint`,
      method: "POST",
      params: { route: "/api/orders" }
    }]
  });
});

usageRouter.post("/trace-for-endpoint", (req, res) => {
  const route = String(req.body?.route ?? "");
  if (!route) {
    return res.status(400).json({
      ok: false,
      data: null,
      diagnostics: [{ code: "BAD_INPUT", message: "Missing body.route" }],
      nextActions: [],
      meta: { hint: "Provide body: { route: \"/api/...\" }", schemaVersion: "1.0" }
    });
  }
  // Fake trace result
  res.json({
    ok: true,
    data: { route, spans: [{ id: "abc123", durationMs: 51 }] },
    diagnostics: [],
    nextActions: []
  });
});

usageRouter.get("/instrumentation-guide", (req, res) => {
  const lang = String(req.query.lang ?? "java");
  res.json({
    ok: true,
    data: {
      lang,
      steps: [
        "Add OTEL SDK and exporter",
        "Annotate the function with @WithSpan",
        "Propagate context across async boundaries"
      ]
    },
    diagnostics: [],
    nextActions: []
  });
});
```

Run it:

```bash
pnpm dev
# GET http://localhost:3000/usage?function=Foo.bar  -> returns NO_DATA with next actions
```

---

## Step 2 — Reverse‑Prompt Responses

**Design goals**:
- Always include `diagnostics[]` when something non‑ideal happens, even `200 OK` with empty results.
- Offer *executable* `nextActions[]` (HATEOAS) with `href`, `method`, and example `params`.
- Add a single‑line `meta.hint` that an agent can paste into its own chain of thought.

**TypeScript type** (already shown) enforces structure and keeps responses consistent across endpoints.

---

## Step 3 — HATEOAS Next Actions

Provide **self‑documenting continuations** the agent can call immediately. Consider these relations:

- `related-endpoints` — find HTTP routes that use a function
- `trace-for-endpoint` — fetch OTEL spans for a route
- `instrumentation-guide` — present language‑specific steps to add spans

When feasible, set `params` defaults so an agent can *copy‑execute* with minimal planning.

---

## Step 4 — Observability (OpenTelemetry)

Wire up OTEL early—agents benefit from clear error signals and latencies to choose retries.

`src/lib/otel.ts`:

```ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";

export function startOtel() {
  const exporter = new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || "http://localhost:4318/v1/traces"
  });

  const sdk = new NodeSDK({
    traceExporter: exporter,
    instrumentations: [getNodeAutoInstrumentations()],
  });

  sdk.start();
  return sdk;
}
```

Call it from `server.ts` *(top of file)*:

```ts
import { startOtel } from "./lib/otel";
startOtel();
```

Optional: run an **OTEL Collector** with an OTLP HTTP receiver -> Jaeger/Tempo.

---

## Step 5 — MCP Server Wrapper

We’ll expose two tools via MCP: `getFunctionUsage` and `getTraceForEndpoint`.

```bash
cd ../../servers/mcp-usage
pnpm init -y
pnpm add @modelcontextprotocol/sdk zod undici
pnpm add -D typescript ts-node @types/node
```

`tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "CommonJS",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true
  }
}
```

`src/schema.ts`:

```ts
import { z } from "zod";

export const GetFunctionUsageInput = z.object({
  function: z.string().describe("Fully qualified method name, e.g., OrderService.placeOrder")
});

export const GetTraceForEndpointInput = z.object({
  route: z.string().describe("HTTP route to fetch traces for, e.g., /api/orders")
});

export type ReversePromptResponse = {
  ok: boolean;
  data: any;
  diagnostics?: Array<{ code: string; message: string; details?: any }>;
  nextActions?: Array<{ rel: string; title: string; href: string; method?: "GET"|"POST"; params?: Record<string, any> }>;
  meta?: { hint?: string; schemaVersion?: string };
};
```

`src/index.ts`:

```ts
import { createServer, Tool } from "@modelcontextprotocol/sdk/server";
import { z } from "zod";
import { GetFunctionUsageInput, GetTraceForEndpointInput, ReversePromptResponse } from "./schema";
import { request } from "undici";

const API_BASE = process.env.AGENT_API_BASE || "http://localhost:3000";

const getFunctionUsage: Tool = {
  name: "getFunctionUsage",
  description: "Return usage stats for a function and suggest next actions if empty",
  inputSchema: GetFunctionUsageInput,
  async *call({ input }) {
    const url = new URL("/usage", API_BASE);
    url.searchParams.set("function", input.function);
    const { body } = await request(url, { method: "GET" });
    const json = (await body.json()) as ReversePromptResponse;

    // Hint surfacing: convert API's meta.hint into MCP text content
    const hint = json.meta?.hint ? `Hint: ${json.meta.hint}` : "";
    yield { content: [{ type: "text", text: JSON.stringify(json, null, 2) + (hint ? `\n\n${hint}` : "") }] };
  }
};

const getTraceForEndpoint: Tool = {
  name: "getTraceForEndpoint",
  description: "Fetch traces for an HTTP route",
  inputSchema: GetTraceForEndpointInput,
  async *call({ input }) {
    const { body } = await request(`${API_BASE}/usage/trace-for-endpoint`, {
      method: "POST",
      body: JSON.stringify({ route: input.route }),
      headers: { "content-type": "application/json" }
    });
    const json = (await body.json()) as ReversePromptResponse;
    yield { content: [{ type: "text", text: JSON.stringify(json, null, 2) }] };
  }
};

const server = createServer({
  name: "usage-mcp",
  version: "1.0.0",
  tools: [getFunctionUsage, getTraceForEndpoint]
});

server.start();
```

Run it:

```bash
pnpm ts-node src/index.ts
# Server listens on stdio by default (MCP). Use your client to connect.
```

---

## Step 6 — Try It from an MCP Client

- **MCP Inspector** (CLI):  
  ```bash
  npx @modelcontextprotocol/inspector node servers/mcp-usage/dist/index.js
  ```
  Call `getFunctionUsage` with `{ "function": "Foo.bar" }` and observe `diagnostics` + `nextActions`.

- **Claude Desktop / Cursor / other MCP clients**: add the server config to your client per its docs and invoke the tools interactively.

---

## Step 7 — Hardening & Safety

- **Pagination**: Return `page`, `pageSize`, `nextPageHref` in `meta`.
- **Ambiguity resolution**: When multiple candidates exist, return `diagnostics[{ code: "AMBIGUOUS", ... }]` and a `nextActions` list of disambiguation calls.
- **Idempotency & retries**: Use idempotency keys for POSTs; return `Retry-After` when rate‑limited.
- **Rate limits**: Include `diagnostics[{ code: "RATE_LIMIT", ... }]` and a `nextActions` retry link with backoff guidance.
- **Safety**: Validate and clamp inputs; return safe errors; prefer allow‑lists for any filesystem or network tools exposed via MCP.
- **Versioning**: Put `meta.schemaVersion` and support evolution via minor bumps.
- **Docs for agents**: Provide succinct per‑tool docs; agents read short docs better than long prose.

---

## Step 8 — Evaluation & Iteration

Track **Agent Success Rate (ASR)**: % of sessions where the agent reaches the intended outcome. Instrument:
- Count of `NO_DATA` followed by a *successful* follow‑up call.
- How often `meta.hint` appears before success.
- Latency percentiles by endpoint to identify agent‑unfriendly hotspots.

Roll out A/B of different `nextActions` copy and ordering; keep what yields higher ASR.

---

## Appendix — Checklists & Patterns

**Response checklist**  
- [ ] `ok` boolean, `data` payload  
- [ ] `diagnostics[]` (code, message, details)  
- [ ] `nextActions[]` with executable `href` and default `params`  
- [ ] `meta.hint` one‑liner

**Common diagnostics codes**: `NO_DATA`, `BAD_INPUT`, `AMBIGUOUS`, `RATE_LIMIT`, `RETRY_SUGGESTED`, `NOT_READY`.

**Disambiguation pattern**  
Return a small candidate list and `nextActions` that select one candidate by ID—let the agent loop.

**Teaching pattern**  
Include `instrumentation-guide` style actions with language‑aware steps.

---

## References

- Model Context Protocol (overview & spec):  
  - https://modelcontextprotocol.io/  
  - https://modelcontextprotocol.io/specification/2025-06-18  
- TypeScript SDK: https://www.npmjs.com/package/@modelcontextprotocol/sdk  
- Anthropic MCP docs: https://docs.anthropic.com/en/docs/mcp  
- Inspector: https://dev.to/shadid12/how-to-build-mcp-servers-with-typescript-sdk-1c28

---

## License

MIT

const exporter = new OTLPTraceExporter({
  // point to collector or vendor endpoint
  url: process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT || "http://localhost:4318/v1/traces"
});

export const sdk = new NodeSDK({
  traceExporter: exporter,
  instrumentations: [getNodeAutoInstrumentations()]
});

export async function startTelemetry() {
  await sdk.start();
  console.log("OpenTelemetry started");
}

export async function shutdownTelemetry() {
  await sdk.shutdown();
  console.log("OpenTelemetry shutdown");
}
```

Use it in `src/server.ts`:

```ts
import { startTelemetry } from "./lib/otel";
startTelemetry().catch(err => console.error("OTEL start error", err));
```

> Tip: Add attributes like `agent.hint`, `next.action.count`, and `diagnostic.code` to spans so you can quantify “agent‑success” beyond HTTP status codes.

---

## Step 5 — MCP Server Wrapper

Now expose your API as **MCP tools**.

```bash
cd ../../../servers/mcp-usage
pnpm init -y
pnpm add @modelcontextprotocol/sdk zod undici
pnpm add -D typescript ts-node @types/node
```

`tsconfig.json` similar to the API’s.

`src/schema.ts`:

```ts
import { z } from "zod";

export const GetUsageInput = z.object({
  function: z.string().describe("Fully-qualified name, e.g., OrderService.placeOrder")
});

export const GetUsageOutput = z.object({
  ok: z.boolean(),
  data: z.any(),
  diagnostics: z.array(z.object({
    code: z.string(),
    message: z.string(),
    details: z.record(z.any()).optional()
  })),
  nextActions: z.array(z.object({
    rel: z.string(),
    title: z.string(),
    href: z.string(),
    method: z.string(),
    params: z.record(z.any()).optional()
  })),
  meta: z.record(z.any()).optional()
});
```

`src/index.ts`:

```ts
import { MCPServer } from "@modelcontextprotocol/sdk/server";
import { z } from "zod";
import { GetUsageInput, GetUsageOutput } from "./schema";
import { request } from "undici";

const server = new MCPServer({
  name: "mcp-usage",
  version: "1.0.0"
});

server.tool(
  "get_function_usage",
  "Get usage stats for a function (reverse-prompt enriched).",
  GetUsageInput,
  async (input) => {
    const url = `http://localhost:3000/usage?function=${encodeURIComponent(input.function)}`;
    const res = await request(url, { method: "GET" });
    const body = await res.body.text();
    const json = JSON.parse(body);
    const parsed = GetUsageOutput.parse(json);
    return parsed;
  }
);

// Optional: a tool that executes a nextAction href automatically
server.tool(
  "follow_next_action",
  "Follow an API-provided nextAction href (GET/POST).",
  z.object({
    href: z.string(),
    method: z.enum(["GET", "POST"]).default("GET"),
    params: z.record(z.any()).optional()
  }),
  async ({ href, method, params }) => {
    const url = new URL(href, "http://localhost:3000").toString();
    const init: any = { method };
    if (method === "POST") init.body = JSON.stringify(params || {}), init.headers = { "content-type": "application/json" };
    const res = await request(url, init);
    return JSON.parse(await res.body.text());
  }
);

server.start();
```

Run:

```bash
pnpm ts-node src/index.ts
```

---

## Step 6 — Try It from an MCP Client

- **MCP Inspector** (handy for debugging):  
  ```bash
  npx @modelcontextprotocol/inspector node servers/mcp-usage/dist/index.js
  ```
- **Claude Desktop / Cursor / other MCP clients**: register `mcp-usage` as a server, then call tools:
  - `get_function_usage { "function": "OrderService.placeOrder" }`
  - If `NO_DATA`, call `follow_next_action` with the first `nextActions[]` entry.

Observe how the response **teaches** the model what to do next.

---

## Step 7 — Hardening & Safety

**Pagination**: Return `paging` + a `nextAction` with the next cursor.  
**Ambiguity**: Provide a `diagnostics` entry like `AMBIGUOUS_INPUT` plus a `disambiguate` nextAction.  
**Rate limits**: Use `429` with `retryAfterSeconds` and a `nextAction` that waits/backs off.  
**Idempotency**: For POST tools, support idempotency keys.  
**Auth**: Prefer OAuth device/PKCE for human-mediated consent; for agents running in CI, scope keys narrowly.  
**Safety**: Validate tool input with Zod/JSON Schema; return explicit error codes and *safe* suggestions.  
**Docs for models**: co-locate **tool descriptions** with copy-sized examples. Models learn from concise examples more than long prose.

---

## Step 8 — Evaluation & Iteration

Track *agent‑centric* KPIs:
- **Dead‑end rate**: responses with `ok=false` *and* `nextActions.length==0` (aim for zero)
- **Follow‑through rate**: how often the next action is called within N seconds
- **Resolution rate**: sequences ending with `ok=true` and goal satisfied
- **Average steps to resolution**: shorter is better, but not at the expense of accuracy

Use OTEL spans + logs to reconstruct sequences and measure these KPIs. Iterate on reverse prompts and next actions where agents drop off.

---

## Appendix — Checklists & Patterns

**API Response Checklist**  
- [ ] `diagnostics[]` with `code` and `message`  
- [ ] `meta.hint` one‑liner (“Try related endpoints…”)  
- [ ] `nextActions[]` with executable `href`, `method`, and default `params`  
- [ ] Concrete examples in 200–300 chars

**Patterns**  
- *No‑data but useful next step* → suggest discovery endpoints or traces  
- *Ambiguous input* → return candidates and a disambiguation action  
- *Expired/unauthorized* → return `REAUTH_NEEDED` with an OAuth device‑code URL  
- *Long‑running* → return `202 ACCEPTED` + poll‑link next action

---

## References

- Model Context Protocol — Introduction: https://modelcontextprotocol.io/introduction  
- MCP Specification (2025‑06‑18): https://modelcontextprotocol.io/specification/2025-06-18  
- TypeScript SDK (npm): https://www.npmjs.com/package/@modelcontextprotocol/sdk  
- Inspector: `npx @modelcontextprotocol/inspector`  
- OpenTelemetry JS: https://opentelemetry.io/docs/languages/js/

---

## License

MIT

**Ambiguity**: If input is ambiguous, return `diagnostics: [{ code: "AMBIGUOUS", message, details: { choices: [...] } }]` and a `nextAction` to disambiguate.  
**Rate Limits**: Return `429` *and* a `nextAction` with `retryAfter` guidance and lighter alternative queries.  
**Idempotency**: Prefer GET for reads; for writes, adopt idempotency keys and surface them in `diagnostics`.  
**Safety**: Validate inputs with Zod; disallow dangerous operations unless explicitly whitelisted; include `policy` URLs in responses.

---

## Step 8 — Evaluation & Iteration

Instrument and track *agent success rate*:
- % of calls that result in **useful next action** vs. dead end
- time‑to‑task and number of calls per successful task
- prevalence of `diagnostic.code`s (e.g., `NO_DATA`, `AMBIGUOUS`)
- retries following `429` with success

Continuously update `nextActions` with the **shortest, safest** path you see in traces.

---

## Appendix — Checklists & Patterns

**Response Contract**

```ts
type ReversePromptResponse<T> = {
  ok: boolean;
  data: T;
  diagnostics: Array<{ code: string; message: string; details?: Record<string, any> }>;
  nextActions: Array<{
    rel: string;
    title: string;
    href: string;
    method: "GET" | "POST";
    params?: Record<string, any>;
  }>;
  meta?: { hint?: string; schemaVersion: string };
};
```

**Patterns**

- **Explain & Suggest** on 2xx empties.  
- **Disambiguate** instead of erroring: offer choices with links.  
- **Decompose** long tasks into `nextActions` chain.  
- **Teach Limits**: when you can’t do X, offer what you *can* do next.  
- **Make Links Executable**: agents should be able to call your `href` as‑is.

---

## References

- Model Context Protocol — Introduction: https://modelcontextprotocol.io/introduction  
- MCP Specification (2025‑06‑18): https://modelcontextprotocol.io/specification/2025-06-18  
- MCP TypeScript SDK: https://www.npmjs.com/package/@modelcontextprotocol/sdk  
- Cloudflare Agents + MCP: https://developers.cloudflare.com/agents/model-context-protocol/  
- Inspector (debugger): `npx @modelcontextprotocol/inspector`

> Acknowledgement: The central “reverse prompt” insight—*keep the conversation going on empty responses*—is inspired by recent practitioner write‑ups on conversation‑driven APIs.

---

## License

MIT
