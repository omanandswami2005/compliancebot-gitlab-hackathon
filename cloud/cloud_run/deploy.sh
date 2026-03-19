#!/bin/bash

# ComplianceBot Cloud Run Deployment Script
# Deploys the report generator to Google Cloud Run

set -e

PROJECT_ID="${1:-}"
SERVICE_ACCOUNT="${2:-compliance-runner}"
REGION="${3:-us-central1}"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./deploy.sh <GCP_PROJECT_ID> [SERVICE_ACCOUNT] [REGION]"
    echo "Example: ./deploy.sh my-gcp-project compliance-runner us-central1"
    exit 1
fi

echo "🚀 Deploying ComplianceBot to Cloud Run..."
echo "   Project ID: $PROJECT_ID"
echo "   Service Account: $SERVICE_ACCOUNT"
echo "   Region: $REGION"

# Set GCP project
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable \
    bigquery.googleapis.com \
    storage-api.googleapis.com \
    run.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com

# Create service account if doesn't exist
echo "🔐 Setting up service account..."
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" &>/dev/null; then
    gcloud iam service-accounts create "$SERVICE_ACCOUNT" \
        --display-name="ComplianceBot Cloud Run Service Account"
else
    echo "   Service account $SERVICE_ACCOUNT already exists"
fi

SA_EMAIL="$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"

# Grant permissions
echo "🔒 Granting IAM permissions..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/bigquery.dataEditor" \
    --condition=None 2>/dev/null || true

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.objectCreator" \
    --condition=None 2>/dev/null || true

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/aiplatform.user" \
    --condition=None 2>/dev/null || true

# Build and push with Cloud Build (no Docker needed!)
echo "🐳 Building with Cloud Build (using Dockerfile from repo)..."
# Cloud Build automatically uses Dockerfile in the source directory
gcloud builds submit \
    --tag "gcr.io/$PROJECT_ID/compliance-reporter:latest" \
    --source cloud/cloud_run/ \
    --timeout=1800

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy compliance-reporter \
    --image "gcr.io/$PROJECT_ID/compliance-reporter:latest" \
    --platform managed \
    --region "$REGION" \
    --service-account "$SA_EMAIL" \
    --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID" \
    --memory 512Mi \
    --timeout 3600 \
    --no-allow-unauthenticated

# Get service URL
SERVICE_URL=$(gcloud run services describe compliance-reporter \
    --platform managed \
    --region "$REGION" \
    --format "value(status.url)")

echo ""
echo "✅ Deployment complete!"
echo "   Service URL: $SERVICE_URL"
echo ""
echo "📝 Next steps:"
echo "   1. Add $GCP_PROJECT_ID to GitLab CI/CD variables"
echo "   2. Add service account key to CI/CD variables"
echo "   3. Update .gitlab-ci.yml with Cloud Run endpoint"
echo ""
echo "For more details, see: docs/configuration.md"
