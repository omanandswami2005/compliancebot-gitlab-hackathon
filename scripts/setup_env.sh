#!/bin/bash
# =============================================================================
# ComplianceBot Environment Setup
# =============================================================================
# Source this file to export all required env vars for local development.
#
# Usage:
#   source scripts/setup_env.sh
# =============================================================================

if ! (return 0 2>/dev/null); then
	echo "This script must be sourced so the exported variables persist in your current shell."
	echo "Use: source ./scripts/setup_env.sh"
	echo "Or run: ./scripts/run_dashboard.sh"
	exit 1
fi

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
