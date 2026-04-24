#!/bin/bash
# Deploy gemini-demo to Google Cloud Run.
# Prerequisites:
#   - gcloud CLI authenticated: gcloud auth login
#   - Project set: gcloud config set project YOUR_PROJECT_ID
#   - APIs enabled: gcloud services enable run.googleapis.com
#
# Usage: ./deploy.sh [--region us-central1]

set -e

REGION="${1:-us-central1}"
SERVICE_NAME="gemini-demo"

echo "Deploying ${SERVICE_NAME} to region ${REGION}..."

gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region="${REGION}" \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=5 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=60s \
  --concurrency=80

echo "Done. Get the service URL with:"
echo "  gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'"
