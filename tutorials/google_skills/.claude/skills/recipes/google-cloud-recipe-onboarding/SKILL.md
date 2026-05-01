---
name: google-cloud-recipe-onboarding
description: Onboard to Google Cloud from scratch. Use when asked to set up a new GCP project, enable APIs, configure billing, create service accounts, assign IAM roles, or walk through first-time GCP project initialization.
when_to_use: New GCP project setup, enabling billing and APIs, creating first service account, initial project IAM configuration, GCP organization structure
---

# Google Cloud Onboarding Recipe

Use this recipe to set up a new Google Cloud project end-to-end — billing, APIs, service accounts, and IAM.

## Step 1 — Create or Select a Project

```bash
# Create new project
gcloud projects create my-project-id --name="My Project"

# Or set active project
gcloud config set project my-project-id

# Link billing
gcloud billing projects link my-project-id \
  --billing-account=XXXXXX-XXXXXX-XXXXXX
```

## Step 2 — Enable APIs

```bash
# Core APIs for most workloads
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com
```

## Step 3 — Create a Service Account

```bash
gcloud iam service-accounts create app-sa \
  --display-name="Application Service Account"

# Get the full email
gcloud iam service-accounts list \
  --filter="displayName:Application Service Account"
```

## Step 4 — Assign IAM Roles

```bash
# Grant roles to the service account
gcloud projects add-iam-policy-binding my-project-id \
  --member="serviceAccount:app-sa@my-project-id.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding my-project-id \
  --member="serviceAccount:app-sa@my-project-id.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding my-project-id \
  --member="serviceAccount:app-sa@my-project-id.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

## Step 5 — Create a Key (if needed for local/dev)

```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=app-sa@my-project-id.iam.gserviceaccount.com

# Set as ADC
gcloud auth application-default login
gcloud auth activate-service-account app-sa@my-project-id.iam.gserviceaccount.com \
  --key-file=key.json
```

## Step 6 — Set Up Organization (if applicable)

```bash
# List organization
gcloud organizations list

# Add folder-level admin
gcloud resource-manager folders create \
  --display-name="Engineering" \
  --organization=YOUR_ORG_ID
```

## Checklist

- [ ] Billing account linked
- [ ] Core APIs enabled (`compute`, `iam`, `cloudresourcemanager`)
- [ ] Service account created with least-privilege roles
- [ ] Local auth verified (`gcloud auth list`)
- [ ] ADC configured (`gcloud auth application-default print-access-token`)
- [ ] Budget alert set (Cloud Billing → Budgets)
