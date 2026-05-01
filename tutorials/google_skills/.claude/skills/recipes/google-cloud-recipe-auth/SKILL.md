---
name: google-cloud-recipe-auth
description: Authenticate to Google Cloud via CLI and application code. Use when asked to authenticate the gcloud CLI, set up Application Default Credentials, configure service account keys, rotate credentials, or troubleshoot "Permission denied" errors in GCP tools.
when_to_use: gcloud auth login, Application Default Credentials, service account key management, troubleshooting GCP auth errors, workload identity setup
---

# Google Cloud Authentication Recipe

Use this recipe to authenticate to Google Cloud from local workstations, CI/CD, or production services.

## Local CLI Authentication (User Account)

```bash
# Interactive login
gcloud auth login

# Verify active account
gcloud auth list

# Set default project and region
gcloud config set project my-project-id
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

## Application Default Credentials (ADC)

ADC is the recommended way to authenticate SDKs and tools automatically.

```bash
# For local dev — authenticate as your user
gcloud auth application-default login

# Verify ADC
gcloud auth application-default print-access-token
```

Your code then picks up credentials automatically:
```python
from google.cloud import bigquery
client = bigquery.Client()  # reads ADC
```

```javascript
const { Storage } = require('@google-cloud/storage');
const storage = new Storage(); // reads ADC
```

## Service Account Authentication

### Option 1 — Key file (development only)

```bash
# Download key
gcloud iam service-accounts keys create key.json \
  --iam-account=my-sa@my-project.iam.gserviceaccount.com

# Activate
gcloud auth activate-service-account \
  --key-file=key.json

# Set as ADC for SDKs
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### Option 2 — Workload Identity (GKE/production — preferred)

```bash
# 1. Allow KSA to impersonate GSA
gcloud iam service-accounts add-iam-policy-binding \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:my-project.svc.id.goog[namespace/kSA-name]" \
  my-sa@my-project.iam.gserviceaccount.com

# 2. Annotate Kubernetes ServiceAccount
kubectl annotate serviceaccount kSA-name \
  --namespace=namespace \
  iam.gke.io/gcp-service-account=my-sa@my-project.iam.gserviceaccount.com
```

### Option 3 — Workload Identity Federation (CI/CD — no service account keys)

```bash
# For GitHub Actions or other OIDC providers
gcloud iam workload-identity-pools create my-pool \
  --location=global

gcloud iam workload-identity-pools providers create-github my-provider \
  --workload-identity-pool=my-pool \
  --location=global \
  --attribute-mapping="google.subject=assertion.sub"

# Get the principal set for GitHub
gcloud iam workload-identity-pools describe my-pool \
  --location=global
```

GitHub Actions sample:
```yaml
- id: 'auth'
  uses: google-github-actions/auth@v1
  with:
    workload_identity_provider: 'projects/xxx/locations/global/workloadIdentityPools/my-pool/providers/my-provider'
    service_account: 'my-sa@my-project.iam.gserviceaccount.com'
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Application Default Credentials not found` | Run `gcloud auth application-default login` |
| `Permission 'iam.serviceAccounts.actAs' denied` | Grant `roles/iam.serviceAccountUser` to the caller |
| `Invalid grant: account not found` | Service account deleted or ADC pointing to wrong project |
| Token expired | Run `gcloud auth application-default revoke` then re-authenticate |

## Key Rotation

```bash
# List active keys
gcloud iam service-accounts keys list \
  --iam-account=my-sa@my-project.iam.gserviceaccount.com

# Delete old key
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=my-sa@my-project.iam.gserviceaccount.com
```
