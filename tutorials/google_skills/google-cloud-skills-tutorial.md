# Google Cloud Skills Tutorial for Claude Code

A comprehensive guide to all Google Cloud skills available in Claude Code, organized by category. These skills enable Claude to assist with everything from initial onboarding to advanced production workloads.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Compute & Serverless](#2-compute--serverless)
3. [Databases](#3-databases)
4. [AI & Machine Learning](#4-ai--machine-learning)
5. [Container Orchestration](#5-container-orchestration)
6. [Networking & Observability](#6-networking--observability)
7. [Well-Architected Framework](#7-well-architected-framework)

---

## 1. Getting Started

### `google-cloud-recipe-onboarding`

**Use when:** A developer is new to Google Cloud and needs help setting up their first project, billing, and deploying their first resource.

**What it covers:**
- Creating a Google Cloud project
- Setting up billing (linking a billing account)
- Installing and initializing the `gcloud` CLI
- Enabling APIs
- Deploying a first resource (Cloud Run, Compute Engine, or Cloud Storage)

**Trigger phrases:** "I'm new to Google Cloud", "get started with GCP", "set up a Google Cloud project", "first steps with Google Cloud"

**Quick start:**
```bash
gcloud init
gcloud run deploy hello-world \
  --image=gcr.io/cloudrun/hello \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated
```

---

### `google-cloud-recipe-auth`

**Use when:** You need to understand how to authenticate to Google Cloud — for human users, service accounts, or cross-cloud workloads.

**What it covers:**
- Human authentication (Console, gcloud CLI, ADC)
- Service-to-service authentication (Service Accounts, Workload Identity)
- IAM authorization (roles, policies, least privilege)
- Special cases: GKE Workload Identity, external workloads, API keys, OIDC tokens

**Key best practices it teaches:**
- Avoid downloading Service Account keys locally — use impersonation instead
- Attach service accounts to resources rather than using static keys
- Use Workload Identity Federation for workloads running outside GCP

**Trigger phrases:** "authenticate to Google Cloud", "service account", "how do I connect", "ADC", "OIDC", "API key"

---

## 2. Compute & Serverless

### `cloud-run-basics`

**Use when:** Deploying containerized applications, scheduled jobs, or always-on worker workloads on Google Cloud's serverless platform.

**What it covers:**
- **Services** — HTTP services that autoscale based on traffic
- **Jobs** — Parallelizable tasks executed on a schedule or on-demand
- **Worker pools** — Always-on pull-based background workloads (Kafka, Pub/Sub consumers)

**Important rules:**
- Deployed code must listen on `0.0.0.0` (not `127.0.0.1`)
- Must use the `$PORT` environment variable (defaults to `8080`)

**Deployment:**
```bash
# From a container image
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL \
  --region us-central1 \
  --allow-unauthenticated

# From source code (uses Cloud Build)
gcloud run deploy SERVICE_NAME --source .

# Create and execute a job
gcloud run jobs create JOB_NAME --image IMAGE_URL
gcloud run jobs execute JOB_NAME
```

**Trigger phrases:** "deploy to Cloud Run", "Cloud Run job", "serverless container", "worker pool"

**Troubleshooting:**
- Crash on boot → fetch logs: `gcloud logging read "resource.labels.service_name=SERVICE_NAME" --limit=20`
- IAM errors → check [iam-security.md](cloud-run-basics/references/iam-security.md)

---

## 3. Databases

### `cloud-sql-basics`

**Use when:** Creating or managing Cloud SQL instances for MySQL, PostgreSQL, or SQL Server.

**What it covers:**
- Instance creation and configuration
- Database and user management
- High availability (HA) setup
- Secure connectivity via Cloud SQL Auth Proxy
- SSL/TLS certificate management

**Quick start (PostgreSQL):**
```bash
gcloud services enable sqladmin.googleapis.com

gcloud sql instances create INSTANCE_NAME \
  --database-version=POSTGRES_18 \
  --cpu=2 --memory=7680MiB \
  --region=REGION

gcloud sql users set-password postgres \
  --instance=INSTANCE_NAME --password=PASSWORD

gcloud sql databases create DATABASE_NAME --instance=INSTANCE_NAME
```

**Connecting via Auth Proxy:**
```bash
./cloud-sql-proxy INSTANCE_CONNECTION_NAME
psql "host=127.0.0.1 port=5432 user=postgres dbname=DATABASE_NAME"
```

**Trigger phrases:** "create a database", "Cloud SQL", "PostgreSQL instance", "MySQL instance", "SQL Server"

---

### `alloydb-basics`

**Use when:** Managing AlloyDB for PostgreSQL clusters — an enterprise-grade, disaggregated compute-and-storage database with built-in AI features.

**What it distinguishes from Cloud SQL:**
- Disaggregated architecture (compute and storage scale independently)
- Built-in **AlloyDB AI** features: vector search, hybrid search, natural language queries, forecasting
- Designed for enterprise-grade performance and availability

**Quick start:**
```bash
gcloud services enable alloydb.googleapis.com

gcloud alloydb clusters create my-cluster \
  --region=us-central1 --password=my-password --network=my-vpc

gcloud alloydb instances create my-primary \
  --cluster=my-cluster --region=us-central1 \
  --instance-type=PRIMARY --cpu-count=2
```

> **Security note:** For production, prefer IAM database authentication over passwords. If passwords are required, use Secret Manager.

**Trigger phrases:** "AlloyDB", "vector search", "enterprise database", "PostgreSQL cluster"

---

### `bigquery-basics`

**Use when:** Running SQL queries, managing datasets and tables, performing data analytics, or leveraging BigQuery ML for AI workloads.

**What it covers:**
- Dataset and table creation
- SQL queries using the `bq` CLI
- BigQuery ML integration with Gemini
- Client libraries (Python, Java, Node.js, Go)
- Terraform IaC for BigQuery resources
- IAM and data governance

**Quick start:**
```bash
gcloud services enable bigquery.googleapis.com

bq mk --dataset --location=US my_dataset

bq query --use_legacy_sql=false \
  'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` \
  WHERE state = "TX" LIMIT 10'
```

**Trigger phrases:** "BigQuery", "run a SQL query", "data warehouse", "analytics", "BigQuery ML"

---

## 4. AI & Machine Learning

### `gemini-api`

**Use when:** Building enterprise AI applications using Gemini models via the Gen AI SDK on Agent Platform (formerly Vertex AI).

**What it covers:**
- Text and multimodal generation (images, audio, video)
- Function calling and structured output
- Context caching
- Embeddings for semantic search
- Live Realtime API (bidirectional streaming)
- Batch prediction
- Model fine-tuning

**Core directive:** Always use the **Gen AI SDK** (`google-genai` for Python, `@google/genai` for JS/TS) — not legacy SDKs like `google-cloud-aiplatform`.

**Quick start (Python):**
```python
from google import genai
client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain quantum computing"
)
print(response.text)
```

**Authentication:**
```bash
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='global'
export GOOGLE_GENAI_USE_VERTEXAI=true
```

**Key models:**
| Model | Use Case |
|-------|---------|
| `gemini-3.1-pro-preview` | Complex reasoning, coding, research (1M tokens) |
| `gemini-3-flash-preview` | Fast, balanced, multimodal (1M tokens) |
| `gemini-3-pro-image-preview` | Image generation and editing |
| `gemini-live-2.5-flash-native-audio` | Live Realtime API with native audio |

**Trigger phrases:** "Gemini", "Agent Platform", "Vertex AI", "generate text", "multimodal AI", "LLM", "function calling"

---

### `firebase-basics`

**Use when:** Working on mobile or web apps that use Firebase products (Firestore, Authentication, Hosting, Functions, etc.).

**CRITICAL prerequisites (mandatory):**
1. Ensure NPM is installed
2. Install the Firebase Agent Skills:
   ```bash
   npx -y skills add firebase/agent-skills -y
   ```
3. Log in via `npx -y firebase-tools@latest login`
4. Set an active project with `npx -y firebase-tools@latest use`

**Trigger phrases:** "Firebase", "Firestore", "Firebase Auth", "mobile app backend", "deploy Firebase"

---

## 5. Container Orchestration

### `gke-basics`

**Use when:** Creating, configuring, or managing Google Kubernetes Engine (GKE) clusters — from day-0 setup to production-grade workloads.

**What it covers (20+ reference topics):**

| Topic | Trigger Keywords |
|-------|-----------------|
| [Core Concepts](gke-basics/references/core-concepts.md) | Autopilot vs Standard, architecture, pricing |
| [Golden Path](gke-basics/references/gke-golden-path.md) | Day-0 checklist, production defaults |
| [Cluster Creation](gke-basics/references/gke-cluster-creation.md) | create cluster, new cluster |
| [Networking](gke-basics/references/gke-networking.md) | private cluster, VPC, Gateway API, ingress |
| [Security](gke-basics/references/gke-security.md) | Workload Identity, RBAC, hardening |
| [Scaling](gke-basics/references/gke-scaling.md) | HPA, VPA, autoscaling, NAP |
| [Cost](gke-basics/references/gke-cost.md) | Spot VMs, CUDs, rightsizing |
| [AI/ML Inference](gke-basics/references/gke-inference.md) | GPU, TPU, vLLM, model serving |
| [Upgrades](gke-basics/references/gke-upgrades.md) | maintenance, release channels, patching |
| [Observability](gke-basics/references/gke-observability.md) | Prometheus, Grafana, dashboards |
| [Storage](gke-basics/references/gke-storage.md) | PVC, persistent volume, Filestore |
| [Backup & DR](gke-basics/references/gke-backup-dr.md) | backup, disaster recovery, CMEK |

**Quick start (Autopilot):**
```bash
gcloud services enable container.googleapis.com
gcloud container clusters create-auto my-cluster --region=us-central1
gcloud container clusters get-credentials my-cluster --region=us-central1
kubectl create deployment hello-server \
  --image=us-docker.pkg.dev/google-samples/containers/gke/hello-app:1.0
```

**Default style:** This skill defaults to the **Autopilot "golden path"** configuration — a production-ready cluster with sensible guardrails built in. Use Standard mode only when Autopilot limits are a constraint.

**Trigger phrases:** "GKE", "Kubernetes cluster", "create a cluster", "Autopilot", "K8s", "container orchestration"

---

## 6. Networking & Observability

### `google-cloud-networking-observability`

**Use when:** Investigating networking issues — VPC Flow Logs, firewall rules, NAT gateways, threat logs, latency metrics, or connectivity problems.

**What it covers:**
- **Threat logs** — Cloud Firewall Plus / Cloud IDS malicious traffic patterns
- **VPC Flow Logs** — IP traffic analysis, top talkers, volume trends
- **Firewall logs** — DENY/ALLOW connection events
- **Cloud NAT logs** — NAT translation auditing, port exhaustion
- **Networking metrics** — RTT, throughput, packet loss trends
- **Connectivity Tests** — Path diagnostics for firewall/routing misconfigs

**Core rules (enforced strictly):**
- Always check BigQuery linked datasets before Cloud Logging for high-volume analysis
- Present the direct answer as soon as it is identified — do NOT run additional exploratory queries
- Treat "no data found" as a conclusive finding and report it
- For volume analysis, BigQuery aggregation is the **primary source of truth**

**Quick query pattern:**
```bash
# VPC Flow log query in BigQuery
bq query --use_legacy_sql=false \
  'SELECT src_ip, SUM(bytes_sent) as total_bytes \
   FROM \`project.dataset.vpc_flows\` \
   WHERE log_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR) \
   GROUP BY src_ip ORDER BY total_bytes DESC LIMIT 10'
```

**Trigger phrases:** "VPC Flow logs", "firewall issue", "network latency", "NAT gateway", "connectivity test", "threat logs", "port exhaustion"

---

## 7. Well-Architected Framework

The WAF skills apply Google's [Well-Architected Framework](https://cloud.google.com/architecture/framework) to evaluate and improve cloud workloads across three pillars:

---

### `google-cloud-waf-security`

**Use when:** Evaluating a workload's security posture across IAM, network security, data protection, and operational security.

**Core principles:**
- **Security by design** — Integrate security from the initial design phase
- **Zero trust** — Never trust, always verify; least-privilege access
- **Shift-left security** — Security testing early in the CI/CD pipeline
- **Preemptive cyber defense** — Proactive threat intelligence and defense
- **AI security** — Secure AI model pipelines, prevent data poisoning
- **Compliance** — Meet regulatory and privacy requirements

**Key products covered:** IAM, IAP, Cloud Armor, VPC Service Controls, Cloud KMS, Sensitive Data Protection, Binary Authorization, Security Command Center

**Trigger phrases:** "security review", "harden my deployment", "IAM permissions", "zero trust", "compliance"

---

### `google-cloud-waf-reliability`

**Use when:** Designing or evaluating a workload for resilience, high availability, and graceful failure recovery.

**Core principles:**
- Define reliability based on **user-experience goals**, not infrastructure metrics
- Set realistic SLOs and use error budgets
- Build highly available systems through **resource redundancy** (multi-zone)
- Design for **horizontal scalability**
- Implement **observability** (monitoring, logging, alerting)
- Plan for **graceful degradation** (circuit breakers, retries, rate limiting)
- Test recovery regularly (**game days** / chaos engineering)
- Conduct blameless **postmortems** after incidents

**Key products covered:** Cloud Load Balancing, Cloud CDN, Cloud SQL HA, Spanner, Managed Service for Prometheus, Backup and DR Service

**Trigger phrases:** "high availability", "SLO", "reliability review", "failover", "disaster recovery", "observability"

---

### `google-cloud-waf-cost-optimization`

**Use when:** Analyzing, planning, or executing cloud cost optimization for a workload or organization.

**Core principles:**
- **Align spending with business value** — IT spending tied to revenue/customer outcomes
- **Foster cost awareness** — Give teams visibility into spend
- **Optimize resource usage** — Provision only what you need, pay-per-use
- **Optimize continuously** — Ongoing monitoring and iteration

**Key products covered:** Cloud Billing reports, BigQuery billing export, Active Assist Recommender, FinOps Hub, Committed Use Discounts (CUDs), Spot VMs, Cloud Storage lifecycle policies, Resource Labels

**Key checklist items:**
- 100% of resources labeled with `env`, `team`, `app`
- BigQuery billing export enabled for regular cost reviews
- Budgets and spending alerts configured per project
- Resources regularly rightsized using Active Assist
- Monthly review of CUD coverage
- Unused resources identified and removed monthly
- Serverless preferred unless there is a specific technical constraint

**Trigger phrases:** "reduce costs", "optimize spending", "FinOps", "Committed Use Discounts", "rightsizing", "budget alert"

---

## Skill Invocation Quick Reference

| Skill | Trigger When User Says... |
|-------|--------------------------|
| `google-cloud-recipe-onboarding` | "I'm new to GCP", "first Google Cloud project" |
| `google-cloud-recipe-auth` | "authenticate", "service account", "ADC", "OIDC" |
| `cloud-run-basics` | "deploy to Cloud Run", "serverless container", "Cloud Run job" |
| `cloud-sql-basics` | "create database", "Cloud SQL", "PostgreSQL instance" |
| `alloydb-basics` | "AlloyDB", "vector search", "enterprise database" |
| `bigquery-basics` | "BigQuery", "run SQL query", "data warehouse", "analytics" |
| `gemini-api` | "Gemini", "Agent Platform", "Vertex AI", "LLM", "generate text" |
| `firebase-basics` | "Firebase", "Firestore", "Firebase Auth", "mobile app" |
| `gke-basics` | "GKE", "Kubernetes", "create cluster", "Autopilot" |
| `google-cloud-networking-observability` | "VPC Flow logs", "firewall issue", "network latency" |
| `google-cloud-waf-security` | "security review", "IAM", "zero trust", "harden deployment" |
| `google-cloud-waf-reliability` | "SLO", "high availability", "failover", "reliability" |
| `google-cloud-waf-cost-optimization` | "reduce costs", "FinOps", "CUDs", "rightsizing" |

---

## Common Reference File Types

Each skill includes a set of reference files in its `references/` directory:

| Reference File | Purpose |
|---------------|---------|
| `core-concepts.md` | Architecture, key concepts, product overview |
| `cli-usage.md` | Essential `gcloud` / `bq` / `kubectl` commands |
| `client-library-usage.md` | SDK usage for Python, Java, Node.js, Go |
| `mcp-usage.md` | MCP server tools for automated operations |
| `iac-usage.md` | Terraform / IaC configuration examples |
| `iam-security.md` | IAM roles, permissions, security best practices |

---

## Quick Decision Guide

**"Which skill do I need?"**

```
Need to get started?
  → google-cloud-recipe-onboarding

Need to authenticate?
  → google-cloud-recipe-auth

Deploying a web service or job?
  → cloud-run-basics

Need a relational database?
  → cloud-sql-basics (standard workloads)
  → alloydb-basics (enterprise + AI features)

Running analytics / SQL?
  → bigquery-basics

Building AI applications?
  → gemini-api

Building a mobile/web app?
  → firebase-basics

Running containers / Kubernetes?
  → gke-basics

Debugging network issues?
  → google-cloud-networking-observability

Evaluating architecture?
  → google-cloud-waf-security (security)
  → google-cloud-waf-reliability (reliability)
  → google-cloud-waf-cost-optimization (cost)
```
