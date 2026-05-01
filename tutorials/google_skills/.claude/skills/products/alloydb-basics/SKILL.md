---
name: alloydb-basics
description: Provision and manage AlloyDB for PostgreSQL-compatible databases on Google Cloud. Use when asked to create an AlloyDB cluster, configure backups, set up read pools, connect from a VM, or migrate from Cloud SQL PostgreSQL.
when_to_use: Creating AlloyDB clusters, configuring automated backups, connecting to AlloyDB from Compute Engine or GKE, PostgreSQL workload scaling
---

# AlloyDB Basics Skill

Use this skill when provisioning or managing AlloyDB clusters on Google Cloud.

## Key Concepts

- **AlloyDB** — Fully managed PostgreSQL-compatible database with automatic storage scaling
- **Primary instance** — Read-write node; supports regional high availability
- **Read pool** — Read-scaleout nodes; distribute read traffic
- **Cluster** — Contains primary + optional read pools + regional storage
- **VPC** — AlloyDB requires Private Service Access (private IP only)

## Common Workflows

### Create a Cluster

```bash
gcloud alloydb clusters create my-cluster \
  --region=us-central1 \
  --network=projects/my-project/global/networks/my-vpc \
  --password=MY_SECURE_PASSWORD \
  --cluster-type=REGIONAL
```

### Create an Instance

```bash
gcloud alloydb instances create my-instance \
  --cluster=my-cluster \
  --instance-type=PRIMARY \
  --cpu-count=8 \
  --region=us-central1
```

### Create a Read Pool

```bash
gcloud alloydb instances create my-read-pool \
  --cluster=my-cluster \
  --instance-type=READPOOL \
  --node-count=2 \
  --region=us-central1
```

### Enable Automated Backups

```bash
gcloud alloydb clusters update my-cluster \
  --region=us-central1 \
  --enable-automated-backup \
  --backup-window=01:00-05:00 \
  --retention-count=14
```

### Connect from a VM

```bash
# On the client VM
psql -h $ALLOYDB_PRIVATE_IP -U postgres
```

## Connection Parameters

| Parameter | Where to find |
|-----------|---------------|
| Host | `gcloud alloydb instances describe my-instance --region=us-central1 --format="get(ipAddress)"` |
| Port | 5432 (default) |
| Database | postgres |
| User | postgres |

## Migration from Cloud SQL

```bash
# Dump from Cloud SQL
pg_dump -h CLOUD_SQL_IP -U postgres -d mydb > dump.sql

# Restore to AlloyDB
psql -h ALLOYDB_IP -U postgres -d mydb < dump.sql
```
