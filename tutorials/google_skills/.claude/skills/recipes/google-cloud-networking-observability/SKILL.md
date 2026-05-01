---
name: google-cloud-networking-observability
description: Set up Google Cloud networking and observability. Use when asked to design a VPC, configure firewall rules, set up Cloud NAT, create a Serverless VPC Access connector, or configure Cloud Monitoring dashboards and alerting policies.
when_to_use: VPC subnet design, firewall rule management, Cloud NAT for private instances, Cloud Monitoring dashboards, alerting on error rate or latency, Cloud Logging filters
---

# Networking & Observability Recipe

Use this recipe to set up a production-ready VPC and monitoring stack on Google Cloud.

## Part 1 — Networking

### Create a VPC (Custom Mode — recommended)

```bash
gcloud compute networks create my-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=regional
```

### Create Subnets

```bash
# Private subnet with private Google Access
gcloud compute networks subnets create private-subnet \
  --network=my-vpc \
  --range=10.0.1.0/24 \
  --region=us-central1 \
  --enable-private-ip-google-access \
  --secondary-range=pods=10.1.0.0/16,services=10.2.0.0/16  # for GKE
```

### Firewall Rules

```bash
# Allow internal traffic
gcloud compute firewall-rules create allow-internal \
  --network=my-vpc \
  --allow=tcp,udp,icmp \
  --source-ranges=10.0.0.0/8

# Allow health checks (for load balancer backends)
gcloud compute firewall-rules create allow-health-checks \
  --network=my-vpc \
  --allow=tcp:80,tcp:443 \
  --source-ranges=35.191.0.0/16,130.211.0.0/22

# Allow SSH via IAP (Identity-Aware Proxy — no public SSH)
gcloud compute firewall-rules create allow-iap-ssh \
  --network=my-vpc \
  --allow=tcp:22 \
  --source-ranges=35.235.240.0/20
  # Then connect via: gcloud compute ssh --zone=us-central1-a my-instance --tunnel-through-iap
```

### Cloud NAT (for private instances with no external IP)

```bash
# Create Cloud Router
gcloud compute routers create my-router \
  --network=my-vpc \
  --region=us-central1

# Create NAT
gcloud compute routers nats create my-nat \
  --router=my-router \
  --region=us-central1 \
  --auto-allocate-nat-external-ips \
  --nat-all-subnet-ip-ranges
```

### Serverless VPC Access (for Cloud Run / Cloud Functions)

```bash
gcloud compute networks vpc-access connectors create my-connector \
  --region=us-central1 \
  --network=my-vpc \
  --range=10.8.0.0/28

gcloud run services update my-service \
  --vpc-connector=my-connector \
  --region=us-central1
```

## Part 2 — Observability

### Cloud Monitoring — Create a Dashboard

```bash
# Create alerting policy for error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-filter='metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"' \
  --condition-threshold-value=10 \
  --condition-threshold-duration=300s
```

### Cloud Logging — Log Sinks

```bash
# Sink errors to Cloud Storage for archival
gcloud logging sinks create error-sink \
  storage.googleapis.com/my-error-bucket \
  --log-filter='resource.type="cloud_run_revision" severity>=ERROR'

# Sink to BigQuery for analysis
gcloud logging sinks create bq-sink \
  bigquery.googleapis.com/projects/my-project/datasets/logs \
  --log-filter='resource.type="k8s_container"'
```

### Cloud Logging — Query Logs

```bash
# Recent Cloud Run errors
gcloud logging read \
  'resource.type="cloud_run_revision" severity>=ERROR' \
  --limit=20 \
  --format=table

# GKE pod errors
gcloud logging read \
  'resource.type="k8s_container" kubernetes.pod_name="my-pod"' \
  --limit=10

# Export specific fields
gcloud logging read 'severity>=WARNING' \
  --format="value(timestamp,severity,textPayload)"
```

### Uptime Checks

```bash
gcloud monitoring uptime create \
  --display-name="My Service Uptime" \
  --resource-type=uptime-url \
  --hostname=my-service.run.app \
  --path=/healthz \
  --check-interval=60s
```

## VPC Design Checklist

- [ ] Custom VPC (not default)
- [ ] Private subnets with `private-ip-google-access`
- [ ] Firewall: allow-internal + allow-health-checks + allow-IAP
- [ ] Cloud NAT for private instances egress
- [ ] Serverless VPC Access connector for Cloud Run/Functions
- [ ] VPC Flow Logs enabled on subnets
