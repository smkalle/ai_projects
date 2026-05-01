---
name: cloud-run-basics
description: Deploy and manage services on Google Cloud Run. Use when asked to deploy a Docker image to Cloud Run, configure revisions, set concurrency, manage environment variables, set up custom domains, or configure auto-scaling.
when_to_use: Deploying containerized services to Cloud Run, configuring traffic splitting, setting up ingress controls, Cloud Run serverless VPC connector
---

# Cloud Run Basics Skill

Use this skill when deploying or managing Cloud Run services.

## Deploy a Service

```bash
gcloud run deploy my-service \
  --image=gcr.io/my-project/my-image:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=1 \
  --max-instances=20 \
  --concurrency=80 \
  --cpu=1 \
  --memory=512Mi \
  --timeout=60s
```

## Key Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--concurrency` | 80 | Requests per instance |
| `--max-instances` | 100 | Cap scale-out |
| `--min-instances` | 0 | Always-on instances (avoids cold start) |
| `--cpu` | 1 | CPU allocation (1, 2, 4) |
| `--memory` | 512Mi | Memory allocation |
| `--timeout` | 300s | Max request duration |
| `--no-allow-unauthenticated` | — | Require IAM auth |

## Environment Variables

```bash
# At deploy time
gcloud run deploy my-service \
  --set-env-vars="ENV=prod,DATABASE_URL=..." \
  --update-secrets=API_KEY=api-key:latest
```

## Traffic & Revisions

```bash
# Rollout to new revision
gcloud run services update-traffic my-service \
  --to-latest \
  --region=us-central1

# Canary / gradual rollout
gcloud run services update-traffic my-service \
  --to-revisions=my-service-00001-gen=10,my-service-00002-gen=90 \
  --region=us-central1
```

## Ingress Control

```bash
# Internal only (VPC)
gcloud run services update my-service \
  --ingress=internal \
  --vpc-connector=my-vpc-connector \
  --region=us-central1

# Cloud Load Balancer (default for managed)
gcloud run services update my-service \
  --ingress=all
```

## Service Accounts

```bash
gcloud run services update my-service \
  --service-account=my-sa@my-project.iam.gserviceaccount.com \
  --region=us-central1
```

## Common Patterns

### Cloud Run + Cloud SQL
```bash
gcloud run services update my-service \
  --add-cloudsql-instances=my-project:us-central1:my-sql
```

### Serverless VPC Access
```bash
gcloud compute networks vpc-access connectors create my-connector \
  --region=us-central1 \
  --network=my-vpc

gcloud run services update my-service \
  --vpc-connector=my-connector \
  --region=usxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-central1
```

### Custom Domain (Managed)
```bash
gcloud run domain-mappings create \
  --service=my-service \
  --domain=api.example.com \
  --region=us-central1
```
