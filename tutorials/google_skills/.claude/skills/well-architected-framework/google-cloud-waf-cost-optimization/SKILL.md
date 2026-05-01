---
name: google-cloud-waf-cost-optimization
description: Optimize Google Cloud costs. Use when asked to reduce GCP spending, apply committed use discounts, right-size Compute Engine, configure Cloud Storage lifecycle policies, set up billing budgets and alerts, or analyze cost breakdowns by service.
when_to_use: Analyzing GCP billing, committing to CUDs, right-sizing VMs, Cloud Storage cost reduction, budget alerts, idle resource cleanup
---

# Google Cloud WAF — Cost Optimization Pillar

Use this skill when analyzing and reducing Google Cloud spending.

## Cost Analysis

```bash
# View current spend by service
gcloud billing accounts list  # get billing account ID
gcloud beta billing accounts get-iam-policy ACCOUNT_ID

# Use Billing Export to BigQuery for detailed analysis
# Enable: Cloud Billing → Budgets & alerts → Export to BigQuery

# Query cost breakdown
bq query --use_legacy_sql=false \
  "SELECT service.description, SUM(cost) as total_cost
   FROM billing_export.gcp_billing_export_v1_
   WHERE usage_start_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
   GROUP BY 1 ORDER BY 2 DESC"

# Find idle resources
bq query --use_legacy_sql=false \
  "SELECT resource.type, COUNT(*) as idle_count
   FROM ...
   WHERE sku.description LIKE '%Compute Engine%'
   GROUP BY 1"
```

## Committed Use Discounts (CUDs)

```bash
# Purchase committed CPU+RAM for a project
gcloud compute commitments create my-commitment \
  --region=us-central1 \
  --resources=vcpu=32,ram=131072 \
  --plan=12-month

# Purchase for a folder (reservations shared)
gcloud compute commitments create my-commitment \
  --region=us-central1 \
  --resources=vcpu=64,ram=262144 \
  --plan=36-month \
  --folder=FOLDER_ID
```

### CUD Scope Recommendations

| Resource | CUD Coverage | Notes |
|----------|-------------|-------|
| Compute Engine | 70-80% of base CPU+RAM | Locked to region/zone |
| GKE node pools | Use node auto-provisioning with CUDs | |
| Cloud SQL | CUDs available on db-custom | 3-year plans save ~57% |

## Right-sizing Compute Engine

```bash
# List recommendations
gcloud recommender recommendations list \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1-a \
  --project=my-project

# Apply a recommendation
gcloud recommender recommendations apply \
  --recommendation=RECOMMENDATION_ID \
  --location=us-central1-a
```

### Right-sizing GKE

```bash
# Enable autoscaler with appropriate thresholds
gcloud container clusters update my-cluster \
  --region=us-central1 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --node-pool-name=default-pool

# Use GKE Autopilot (pay per pod, no idle nodes)
gcloud container clusters create-auto my-cluster --region=us-central1
```

## Cloud Storage Lifecycle Policies

```bash
# Set lifecycle policy via .xml or JSON
# lifecycle.json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 90}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365}
    }
  ]
}

gsutil lifecycle set lifecycle.json gs://my-bucket/
```

## Billing Budgets & Alerts

```bash
# Create budget alert (100% of $5,000/month = alert at $5,000)
gcloud billing budgets create \
  --billing-account=XXXXXX-XXXXXX-XXXXXX \
  --display-name="Monthly Spend Budget" \
  --budget-amount=5000 \
  --filter-projects=my-project \
  --threshold-rule=percent=0.5 \
  --threshold-rule=percent=0.9 \
  --threshold-rule=percent=1.0 \
  --notification-account-email=billing-team@example.com
```

## Quick Wins Checklist

- [ ] Identify and delete unattached external IP addresses
- [ ] Enable Cloud Storage lifecycle policies (delete old data)
- [ ] Enable GKE autoscaling (Horizontal + Vertical Pod Autoscaler)
- [ ] Convert persistent disks to SSDs only where needed
- [ ] Purchase CUDs for steady-state workloads (>70% utilization)
- [ ] Use Cloud Run or Cloud Functions for event-driven workloads (pay per invocation)
- [ ] Use preemptible/spot VMs for batch workloads
- [ ] Set up billing budgets with alerts at 50%, 90%, 100%
