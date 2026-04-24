# Google Cloud Skills for AI Agents

Installable knowledge packs for Google Cloud products and workflows, consumed by AI agents via the [`skills.sh`](https://github.com/skills-sh/ecosystem) runtime.

## Installation

```bash
npx skills add google/skills
```

This installs all available skills. To install a specific category only:

```bash
npx skills add google/skills/cloud/products
npx skills add google/skills/cloud/recipes
npx skills add google/skills/cloud/well-architected-framework
```

## Quick Start

Once installed, reference the skill by name in your agent's request. For example:

> "Deploy a Cloud Run service with a Docker image" → the agent loads `cloud-run-basics`

> "Help me authenticate to Google Cloud locally" → the agent loads `google-cloud-recipe-auth`

> "Review my infrastructure for cost savings" → the agent loads `google-cloud-waf-cost-optimization`

## Usage Examples

### Products — Per-service skill packs

Each product skill covers provisioning, configuration, and common `gcloud` CLI patterns.

| Skill | Use when you need to... |
|-------|------------------------|
| `gemini-api-basics` | Call the Gemini API, set up API keys, configure model parameters |
| `alloydb-basics` | Provision an AlloyDB cluster, configure backups, connect from a VM |
| `bigquery-basics` | Create datasets, load data, run queries, configure access |
| `cloud-run-basics` | Deploy a service from a Docker image, set concurrency, configure revisions |
| `cloud-sql-basics` | Create a Cloud SQL instance, enable high availability, manage users |
| `firebase-basics` | Initialize a Firebase project, configure Authentication and Firestore |
| `gke-basics` | Create a GKE cluster, deploy workloads, configure node pools |

**Example prompt:**
> "Create a BigQuery dataset called `analytics_prod` and give the `data-eng@my-project.iam` service account `WRITER` access."

### Recipes — Multi-step workflows

Recipes chain `gcloud` commands and GCP console steps into repeatable workflows.

**`google-cloud-recipe-onboarding`** — New GCP project setup end-to-end: enable APIs, set up billing, create service accounts, assign roles.

> "Walk me through setting up a new GCP project from scratch with billing, APIs, and a dev service account."

**`google-cloud-recipe-auth`** — Local authentication via `gcloud auth login`, Application Default Credentials, and service account key management.

> "My local gcloud CLI isn't authenticated. Help me authenticate and verify it works."

**`google-cloud-networking-observability`** — VPC design, firewall rules, Cloud NAT, and set up Cloud Monitoring dashboards and alerting.

> "Set up a VPC with a private subnet for my GKE cluster and add a Cloud NAT gateway."

### Well-Architected Framework — Guided reviews

Each WAF skill applies the corresponding Google Cloud pillar review to your infrastructure.

| Skill | Review scope |
|-------|-------------|
| `google-cloud-waf-security` | IAM least-privilege, VPC Service Controls, Secret Manager, Binary Authorization |
| `google-cloud-waf-reliability` | SLO definition, Cloud Monitoring alerting, failover with Cloud Load Balancing |
| `google-cloud-waf-cost-optimization` | Committed use discounts, right-sizing Compute Engine, Cloud Storage lifecycle policies |

**Example prompt:**
> "Review my current GKE cluster setup for cost optimization. I'm running 20 n2-standard-4 nodes and bills are higher than expected."

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines. To add a new skill:

1. Choose the correct category: `cloud/products/`, `cloud/recipes/`, or `cloud/well-architected-framework/`
2. Create a directory `<category>/<your-skill-name>/`
3. Add an `skill.md` entry point file
4. Open a pull request against `google/skills`

## License

Apache 2.0 — see [LICENSE](./LICENSE)
