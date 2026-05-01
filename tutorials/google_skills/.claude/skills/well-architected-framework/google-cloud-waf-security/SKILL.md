---
name: google-cloud-waf-security
description: Apply Google Cloud Well-Architected Security pillar review to infrastructure. Use when asked to review GCP security posture, configure IAM least-privilege, set up VPC Service Controls, configure Secret Manager, enable Binary Authorization, or apply org policies.
when_to_use: IAM audit, VPC Service Controls perimeter, Secret Manager usage, Binary Authorization for GKE, organization policy enforcement, security health analytics
---

# Google Cloud WAF — Security Pillar

Use this skill when reviewing or hardening GCP infrastructure for security.

## IAM Least Privilege

```bash
# List all IAM members with broad roles
gcloud organizations get-iam-policy YOUR_ORG_ID \
  --format=flattened | grep -E "role:|member:"

# Find service accounts with admin roles
gcloud projects get-iam-policy my-project \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/.*admin" \
  --format="table(bindings.role,bindings.members)"

# Audit service account usage
gcloud iam service-accounts list
gcloud iam service-accounts keys list \
  --iam-account=my-sa@my-project.iam.gserviceaccount.com
```

## VPC Service Controls

```bash
# Create a service perimeter
gcloud access-context-manager perimeters create my-perimeter \
  --title="My Perimeter" \
  --resources=projects/my-project-number \
  --access-levels=MY_ACCESS_LEVEL \
  --ingress-policies='[
    {
      "source": {"identities": ["serviceAccount:data-ingest@my-project.iam.gserviceaccount.com"]},
      "ingressFrom": {"sources": [{"accessLevel": "IngressFromSources"}]}
    }
  ]'
```

## Secret Manager

```bash
# Create a secret
gcloud secrets create my-api-key --data-file=- <<< "my-secret-value"

# Grant access
gcloud secrets add-iam-policy-binding my-api-key \
  --member="serviceAccount:my-app@my-project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Access in code
# Use Secret Manager client library; do NOT embed secrets in code or env vars checked into source control
```

## Binary Authorization (GKE)

```bash
# Enable Binary Authorization
gcloud container clusters update my-cluster \
  --region=us-central1 \
  --enable-binauthz

# Require attestation for production
gcloud container binauthz policy import policy.yaml
```

```yaml
# policy.yaml
defaultAdmissionRule:
  enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
  evaluationMode: REQUIRE_ATTESTATION
attestors:
  - name: my-attestor
    userOwnedGrafeasNote:
      noteNames:
        - projects/my-project/notes/my-attestor
```

## Organization Policies

```bash
# Disable serial port access
gcloud org-policies set-policy my-project-id <<EOF
{"policy": {"booleanPolicy": {"enabled": true}, "constraint": "compute.disableSerialPortAccess"}}
EOF

# Enforce uniform bucket-level access
gcloud org-policies set-policy my-project-id <<EOF
{"policy": {"booleanPolicy": {"enabled": true}, "constraint": "storage.uniformBucketLevelAccess"}}
EOF

# Restrict OS login
gcloud org-policies set-policy my-project-id <<EOF
{"policy": {"booleanPolicy": {"enabled": true}, "constraint": "compute.requireOsLogin"}}
EOF
```

## Security Health Analytics

```bash
# Enable Security Health Analytics
gcloud securityposture list  # check current posture
gcloud securityposture posture scan  # trigger on-demand scan
```

## Checklist

- [ ] All service accounts have specific (non-admin) roles
- [ ] No long-lived service account keys in source control
- [ ] Secret Manager used for all secrets
- [ ] VPC Service Controls perimeter around sensitive data
- [ ] Binary Authorization enforced on GKE production clusters
- [ ] Org policies restrict serial port, OS login, public IP assignment
- [ ] VPC Flow Logs enabled on production subnets
- [ ] Cloud Armor enabled on public-facing Cloud Load Balancers
