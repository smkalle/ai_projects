---
name: bigquery-basics
description: Work with Google BigQuery for data warehousing and analytics. Use when asked to create datasets, load data, run SQL queries, configure access controls, set up streaming inserts, or optimize query performance.
when_to_use: Creating BigQuery datasets, loading data from GCS, running analytical SQL queries, configuring dataset IAM, BigQuery ML, export to Cloud Storage
---

# BigQuery Basics Skill

Use this skill when working with BigQuery datasets, tables, queries, or data loading.

## Setup

```bash
gcloud auth application-default login
gcloud config set project my-project
```

## Common Workflows

### Create a Dataset

```bash
gcloud bigquery datasets create analytics_prod \
  --location=US \
  --description="Production analytics data"
```

### Create a Table (Schema)

```bash
gcloud bigquery mk \
  --table=my-project:analytics_prod.events \
  --schema=event_id:STRING,user_id:STRING,timestamp:TIMESTAMP,event_type:STRING
```

### Load Data from Cloud Storage

```bash
gcloud bigquery load \
  --source_format=CSV \
  --autodetect \
  my-project:analytics_prod.events \
  gs://my-bucket/events/*.csv
```

### Run a Query

```bash
# Interactive
gcloud bigquery query \
  --use_legacy_sql=false \
  "SELECT user_id, COUNT(*) as events
   FROM analytics_prod.events
   WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
   GROUP BY user_id"

# Save results to table
gcloud bigquery query \
  --destination_table=analytics_prod.user_weekly \
  --use_legacy_sql=false \
  "SELECT ..."
```

### Configure Dataset IAM

```bash
# Grant user access
gcloud bigquery add-iam-policy-binding \
  --member="user:data-eng@my-project.iam" \
  --role="roles/bigquery.dataEditor" \
  my-project:analytics_prod

# Service account for pipeline
gcloud bigquery add-iam-policy-binding \
  --member="serviceAccount:etl@my-project.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser" \
  --member="serviceAccount:etl@my-project.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor" \
  my-project:analytics_prod
```

### Streaming Insert

```bash
gcloud bigquery rows insert \
  --dataset=analytics_prod \
  --table=events \
  --json-rows='[{"event_id": "e1", "user_id": "u1"}]'
```

## SQL Tips

- Use partitioned tables on timestamp columns: `PARTITION BY DATE(timestamp)`
- Cluster on high-cardinality keys: `CLUSTER BY user_id, event_type`
- Preview: `SELECT * FROM table LIMIT 10`
- Dry-run query cost: add `--dry_run` flag or use `EXPLAIN`

## Pricing

| Query type | Cost |
|-----------|------|
| On-demand | $5 per TB scanned |
| Flat-rate (slot) | Reserved capacity |
| Interactive | Billed per second |
|结果缓存 | Free |
