---
name: gke-basics
description: Create and manage Google Kubernetes Engine clusters and workloads. Use when asked to create a GKE cluster, deploy an application to GKE, configure node pools, set up ingress, manage Kubernetes resources (Deployments, Services, ConfigMaps, Secrets), or configure autoscaling.
when_to_use: Creating GKE clusters, deploying container workloads, Kubernetes Ingress for GCP, GKE node pool management, Vertical Pod Autoscaler, GKE Config Connector
---

# GKE Basics Skill

Use this skill when provisioning or deploying workloads on Google Kubernetes Engine.

## Create a Cluster

### Standard (self-managed nodes)

```bash
gcloud container clusters create my-cluster \
  --region=us-central1 \
  --num-nodes=3 \
  --machine-type=n2-standard-4 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10
```

### Autopilot

```bash
gcloud container clusters create-auto my-cluster \
  --region=us-central1
```

## kubectl Setup

```bash
gcloud container clusters get-credentials my-cluster --region=us-central1
kubectl get nodes
```

## Deploy an Application

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: gcr.io/my-project/my-image:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: my-app-svc
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
```

```bash
kubectl apply -f deployment.yaml
kubectl get svc
# Note external IP from LoadBalancer
```

## GKE Ingress (Cloud Load Balancer)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    kubernetes.io/ingress.class: "gce"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - app.example.com
    secretName: app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /*
        pathType: Prefix
        backend:
          service:
            name: my-app-svc
            port:
              number: 80
```

## Horizontal Pod Autoscaler

```bash
kubectl autoscale deployment my-app \
  --cpu-percent=70 \
  --min=2 \
  --max=20
```

## Node Pool Management

```bash
# Add a node pool
gcloud container node-pools create memory-opt \
  --cluster=my-cluster \
  --region=us-central1 \
  --machine-type=arm64-optimized-m1 \
  --num-nodes=2

# Upgrade node pool version
gcloud container clusters upgrade my-cluster \
  --region=us-central1 \
  --master
```

## GKE Workload Identity (Recommended — instead of service account keys)

```bash
# Bind KSA to GSA
gcloud iam service-accounts add-iam-policy-binding \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:my-project.svc.id.goog[default/my-app-k8s]" \
  my-sa@my-project.iam.gserviceaccount.com

# Annotate KSA
kubectl annotate serviceaccount my-app-k8s \
  --namespace=default \
  iam.gke.io/gcp-service-account=my-sa@my-project.iam.gserviceaccount.com
```
