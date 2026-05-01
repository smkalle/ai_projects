---
name: cloud-sql-basics
description: Provision and manage Cloud SQL for MySQL, PostgreSQL, or SQL Server on Google Cloud. Use when asked to create a Cloud SQL instance, enable high availability, configure failover replicas, manage users and databases, or set up private IP connectivity.
when_to_use: Creating Cloud SQL instances, enabling HA/DR, configuring read replicas, Cloud SQL Auth Proxy, connecting from Cloud Run or GKE, managing backups
---

# Cloud SQL Basics Skill

Use this skill when provisioning or managing Cloud SQL instances.

## Create an Instance

### PostgreSQL

```bash
gcloud sql instances create my-pg-instance \
  --database-version=POSTGRES_16 \
  --tier=db-n1-standard-2 \
  --region=us-central1 \
  --storage-size=50GB \
  --storage-auto-increase
```

### MySQL

```bash
gcloud sql instances create my-mysql-instance \
  --database-version=MYSQL_8_0 \
  --tier=db-n1-standard-2 \
  --region=us-central1
```

## Enable High Availability (Regional)

```bash
gcloud sql instances create my-pg-instance \
  --availability-type=REGIONAL \
  --enable-bin-log \
  # (for PostgreSQL HA, also set backup start window and HA)
```

Or update existing:

```bash
gcloud sql instances patch my-pg-instance \
  --availability-type=REGIONAL
```

## Create a Database

```bash
gcloud sql databases create mydb --instance=my-pg-instance
```

## Manage Users

```bash
# PostgreSQL user
gcloud sql users create app_user \
  --instance=my-pg-instance \
  --password=SECURE_PASSWORD

# MySQL user with host
gcloud sql users create app_user \
  --instance=my-mysql-instance \
  --host=% \
  --password=SECURE_PASSWORD
```

## Private IP (Recommended)

```bash
# Enable private IP
gcloud sql instances patch my-pg-instance \
  --network=projects/my-project/global/networks/my-vpc \
  --no-assign-ip

# Private IP is then auto-assigned from your VPC range
```

## Cloud SQL Auth Proxy (for local dev / Cloud Run)

```bash
# Download proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/latest/linux.amd64
chmod +x cloud-sql-proxy

# Run proxy
./cloud-sql-proxy my-project:us-central1:my-pg-instance

# Connect
psql "host=127.0.0.1 port=5432 dbname=mydb user=app_user"
```

## Backups

```bash
# On-demand backup
gcloud sql backups create --instance=my-pg-instance

# Scheduled (enabled by default with 7-day retention)
gcloud sql instances patch my-pg-instance \
  --backup-start-time=02:00
```

## Read Replica

```bash
gcloud sql instances create my-pg-replica \
  --master-instance-name=my-pg-instance \
  --tier=db-n1-standard-1 \
  --region=us-east1
```

## Connect from Cloud Run

```bash
gcloud run services update my-service \
  --add-cloudsql-instances=my-project:us-central1:my-pg-instance \
  --region=us-central1
```
