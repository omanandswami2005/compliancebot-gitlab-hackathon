#!/bin/bash
# =============================================================================
# ComplianceBot Environment Setup
# =============================================================================
# Source this file to export all required env vars for local development.
#
# Usage:
#   source scripts/setup_env.sh
# =============================================================================

export GCP_PROJECT_ID="compliancebot-gitlab-hackathon"
export GCP_CREDENTIALS_PATH="$HOME/.config/compliancebot/compliancebot-sa-key.json"
export GOOGLE_APPLICATION_CREDENTIALS="$GCP_CREDENTIALS_PATH"
export CLOUDSDK_PYTHON="C:/Program Files (x86)/Google/Cloud SDK/google-cloud-sdk/platform/bundledpython/python.exe"
export GCP_REGION="us-central1"
export BIGQUERY_DATASET="compliance"
export GCS_BUCKET="compliance-evidence-compliancebot-gitlab-hackathon"

echo "ComplianceBot environment configured:"
echo "  GCP_PROJECT_ID=$GCP_PROJECT_ID"
echo "  GCP_CREDENTIALS_PATH=$GCP_CREDENTIALS_PATH"
echo "  GCP_REGION=$GCP_REGION"
echo "  BIGQUERY_DATASET=$BIGQUERY_DATASET"
echo "  GCS_BUCKET=$GCS_BUCKET"
