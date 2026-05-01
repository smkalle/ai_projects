---
name: google-cloud-waf-reliability
description: Apply Google Cloud Well-Architected Reliability pillar to infrastructure. Use when asked to define SLOs, configure Cloud Monitoring alerting, set up failover with Cloud Load Balancing, design for high availability, or create disaster recovery plans.
when_to_use: SLO definition and tracking, Cloud Monitoring alerting policies, Cloud Load Balancer failover setup, multi-region deployment, disaster recovery runbook
---

# Google Cloud WAF — Reliability Pillar

Use this skill when designing or reviewing GCP infrastructure for reliability.

## SLO Definition

```bash
# Define SLO via SLI registry (Cloud Monitoring)
gcloud monitoring slo create \
  --service=run.googleapis.com \
  --display-name="API Availability SLO" \
  --method=GET \
  --good-total-ratio=0.99 \
  --period=86400
```

### Common SLO Targets

| Service Type | Availability SLO | Latency SLO |
|-------------|-------------------|-------------|
| Critical API | 99.9% | p99 < 500ms |
| Standard API | 99.5% | p95 < 1s |
| Batch/Background | 99.0% | N/A |

## Cloud Load Balancing (Multi-region HA)

```bash
# Global HTTP(S) Load Balancer with backend services
gcloud compute backend-services create api-backend \
  --global \
  --health-checks=http-health-check \
  --enable-cdn \
  --protocol=HTTPS

gcloud compute backend-services add-backend api-backend \
  --global \
  --instance-group=us-central1-ig \
  --instance-group-region=us-central1

gcloud compute backend-services add-backend api-backend \
  --global \
  --instance-group=europe-west1-ig \
  --instance-group-region=europe-west1

# URL map for traffic splitting
gcloud compute url-maps import api-lb --source=url-map.yaml --global
```

## Cloud Monitoring Alerting

```bash
# Alert on high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High 5xx Error Rate" \
  --condition-display-name="5xx > 1%" \
  --condition-filter='metric.type="loadbalancing.googleapis.com/https/request_count" AND metric.labels.response_code_class="5xx"' \
  --condition-threshold-value=0.01 \
  --condition-threshold-comparison=COMPARISON_GT \
  --condition-threshold-duration=300s

# Alert on latency regression
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Latency" \
  --condition-filter='metric.type="run.googleapis.com/container/request_latencies"' \
  --condition-threshold-value=1000 \
  --condition-threshold-comparison=COMPARISON_GT \
  --condition-threshold-duration=120s
```

## High Availability Patterns

### Cloud Run (Multi-region)
```bash
# Deploy to primary and secondary regions
gcloud run deploy my-service --region=us-central1 --allow-unauthenticated
gcloud run deploy my-service --region=europe-west1 --allow-unauthenticated

# Use global HTTPS Load Balancer to route between them
```

### GKE (Regional Clusters)
```bash
gcloud container clusters create my-cluster \
  --region=us-central1 \
  --enable-regional  # creates nodes across 3 zones automatically
```

### Cloud SQL HA
```bash
gcloud sql instances patch my-instance \
  --availability-type=REGIONAL  # enables automatic failover
```

## Disaster Recovery Checklist

- [ ] SLOs defined and tracked in Cloud Monitoring
- [ ] Alerting policies notify on-call (not just email)
- [ ] Multi-region or multi-zone deployment for critical services
- [ ] Cloud SQL HA with automatic failover enabled
- [ ] GKE regional cluster (not zonal)
- [ ] Data backed up (Cloud SQL auto-backups + cross-region GCS)
- [ ] Chaos testing: intentionally fail instances to verify recovery
- [ ] Runbook exists for MTTR < 1 hour
