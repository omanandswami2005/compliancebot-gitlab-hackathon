#!/bin/bash
# =============================================================================
# ComplianceBot GCP Setup Script
# =============================================================================
# This script automates the complete GCP setup for ComplianceBot integration.
# 
# Prerequisites:
#   - Google Cloud SDK (gcloud) installed: https://cloud.google.com/sdk/install
#   - Authenticated with gcloud: gcloud auth login
#   - Billing account linked to a project (or will create new project)
#
# Usage:
#   ./scripts/gcp_setup.sh [PROJECT_ID]
#
# If PROJECT_ID is not provided, a new project will be created.
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_ACCOUNT_NAME="compliancebot"
BIGQUERY_DATASET="compliance"
REGION="us-central1"
BUCKET_RETENTION_DAYS=365  # 1 year for SOC 2

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

# =============================================================================
# Pre-flight Checks
# =============================================================================

echo ""
echo "=============================================="
echo "   ComplianceBot GCP Setup Script"
echo "=============================================="
echo ""

log_info "Running pre-flight checks..."

# Check required commands
check_command "gcloud"
check_command "bq"
check_command "gsutil"
check_command "base64"

# Check gcloud authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null 2>&1; then
    log_error "Not authenticated with gcloud. Run: gcloud auth login"
    exit 1
fi

CURRENT_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1)
log_success "Authenticated as: $CURRENT_ACCOUNT"

# =============================================================================
# Project Setup
# =============================================================================

PROJECT_ID="${1:-}"

if [ -z "$PROJECT_ID" ]; then
    # Generate a unique project ID
    RANDOM_SUFFIX=$(date +%s | tail -c 6)
    PROJECT_ID="compliancebot-${RANDOM_SUFFIX}"
    
    log_info "No project ID provided. Creating new project: $PROJECT_ID"
    
    # Check if user wants to create new project
    read -p "Create new GCP project '$PROJECT_ID'? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Please provide an existing project ID:"
        read -p "Project ID: " PROJECT_ID
    else
        # Create new project
        log_info "Creating GCP project: $PROJECT_ID"
        gcloud projects create "$PROJECT_ID" --name="ComplianceBot" 2>/dev/null || {
            log_warning "Project may already exist or creation failed. Continuing..."
        }
    fi
fi

# Set the project
log_info "Setting active project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# Verify project exists
if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
    log_error "Project $PROJECT_ID does not exist or you don't have access."
    exit 1
fi

log_success "Using project: $PROJECT_ID"

# =============================================================================
# Check Billing
# =============================================================================

log_info "Checking billing status..."

BILLING_ACCOUNT=$(gcloud billing projects describe "$PROJECT_ID" --format="value(billingAccountName)" 2>/dev/null || echo "")

if [ -z "$BILLING_ACCOUNT" ] || [ "$BILLING_ACCOUNT" == "billingAccountName: ''" ]; then
    log_warning "No billing account linked to project."
    
    # List available billing accounts
    echo ""
    log_info "Available billing accounts:"
    gcloud billing accounts list --format="table(name, displayName, open)"
    echo ""
    
    read -p "Enter billing account ID (e.g., 01XXXX-XXXXXX-XXXXXX): " BILLING_ID
    
    if [ -n "$BILLING_ID" ]; then
        log_info "Linking billing account..."
        gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING_ID"
        log_success "Billing account linked."
    else
        log_warning "Skipping billing setup. Some services may not work."
    fi
else
    log_success "Billing account already linked."
fi

# =============================================================================
# Enable APIs
# =============================================================================

log_info "Enabling required GCP APIs..."

APIS=(
    "bigquery.googleapis.com"
    "storage.googleapis.com"
    "aiplatform.googleapis.com"
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "iam.googleapis.com"
)

for api in "${APIS[@]}"; do
    log_info "  Enabling $api..."
    gcloud services enable "$api" --quiet 2>/dev/null || log_warning "  Could not enable $api"
done

log_success "APIs enabled."

# =============================================================================
# Create Service Account
# =============================================================================

SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

log_info "Setting up service account: $SA_EMAIL"

# Check if service account exists
if gcloud iam service-accounts describe "$SA_EMAIL" &> /dev/null; then
    log_info "Service account already exists."
else
    log_info "Creating service account..."
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="ComplianceBot Service Account" \
        --description="Service account for ComplianceBot GCP integration"
    log_success "Service account created."
fi

# Grant IAM roles
log_info "Granting IAM roles to service account..."

ROLES=(
    "roles/bigquery.dataEditor"
    "roles/bigquery.jobUser"
    "roles/storage.objectAdmin"
    "roles/aiplatform.user"
)

for role in "${ROLES[@]}"; do
    log_info "  Granting $role..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --condition=None \
        --quiet 2>/dev/null || log_warning "  Could not grant $role"
done

log_success "IAM roles granted."

# =============================================================================
# Create Service Account Key
# =============================================================================

KEY_FILE="/tmp/compliancebot-sa-key.json"
KEY_FILE_B64="/tmp/compliancebot-sa-key-b64.txt"

log_info "Creating service account key..."

# Delete existing keys (optional - keep only one)
# gcloud iam service-accounts keys list --iam-account="$SA_EMAIL" --format="value(name)" | while read key; do
#     gcloud iam service-accounts keys delete "$key" --iam-account="$SA_EMAIL" --quiet 2>/dev/null
# done

# Create new key
gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SA_EMAIL" \
    --quiet

# Base64 encode for GitLab CI/CD
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    base64 -i "$KEY_FILE" -o "$KEY_FILE_B64"
else
    # Linux
    base64 -w 0 "$KEY_FILE" > "$KEY_FILE_B64"
fi

log_success "Service account key created: $KEY_FILE"
log_success "Base64 encoded key: $KEY_FILE_B64"

# =============================================================================
# Create BigQuery Dataset
# =============================================================================

log_info "Setting up BigQuery dataset: $BIGQUERY_DATASET"

# Check if dataset exists
if bq show "${PROJECT_ID}:${BIGQUERY_DATASET}" &> /dev/null; then
    log_info "Dataset already exists."
else
    log_info "Creating BigQuery dataset..."
    bq mk --dataset \
        --location=US \
        --description="ComplianceBot compliance findings and analytics" \
        "${PROJECT_ID}:${BIGQUERY_DATASET}"
    log_success "Dataset created."
fi

# Create tables
log_info "Creating BigQuery tables..."

# Compliance findings table
bq query --use_legacy_sql=false --quiet << 'EOF'
CREATE TABLE IF NOT EXISTS compliance.compliance_findings (
  project_id STRING NOT NULL,
  mr_id INT64 NOT NULL,
  mr_url STRING,
  pipeline_id INT64,
  control_id STRING NOT NULL,
  framework STRING NOT NULL,
  severity STRING NOT NULL,
  status STRING DEFAULT 'NEEDS_REVIEW',
  title STRING,
  description STRING,
  file_path STRING,
  remediation_steps STRING,
  compliance_score INT64,
  evidence_hash STRING,
  finding_date TIMESTAMP NOT NULL,
  remediated_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(finding_date)
CLUSTER BY project_id, framework, severity;
EOF

log_success "BigQuery tables created."

# =============================================================================
# Create Cloud Storage Bucket
# =============================================================================

BUCKET_NAME="compliance-evidence-${PROJECT_ID}"

log_info "Setting up Cloud Storage bucket: $BUCKET_NAME"

# Check if bucket exists
if gsutil ls -b "gs://${BUCKET_NAME}" &> /dev/null; then
    log_info "Bucket already exists."
else
    log_info "Creating Cloud Storage bucket..."
    gsutil mb -l US "gs://${BUCKET_NAME}"
    log_success "Bucket created."
fi

# Set retention policy (1 year for SOC 2)
log_info "Setting retention policy (${BUCKET_RETENTION_DAYS} days)..."
gsutil retention set "${BUCKET_RETENTION_DAYS}d" "gs://${BUCKET_NAME}" 2>/dev/null || \
    log_warning "Could not set retention policy. May require bucket lock."

# Enable versioning
log_info "Enabling versioning..."
gsutil versioning set on "gs://${BUCKET_NAME}"

# Set lifecycle rule (move to NEARLINE after 90 days)
log_info "Setting lifecycle rules..."
cat > /tmp/lifecycle.json << EOF
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 90}
    }
  ]
}
EOF
gsutil lifecycle set /tmp/lifecycle.json "gs://${BUCKET_NAME}"

log_success "Cloud Storage bucket configured."

# =============================================================================
# Test Vertex AI Access
# =============================================================================

log_info "Testing Vertex AI access..."

# Simple test to verify API is accessible
if gcloud ai models list --region="$REGION" --limit=1 &> /dev/null; then
    log_success "Vertex AI is accessible."
else
    log_warning "Could not verify Vertex AI access. It may still work."
fi

# =============================================================================
# Generate Output
# =============================================================================

echo ""
echo "=============================================="
echo "   GCP Setup Complete!"
echo "=============================================="
echo ""

log_success "All GCP resources have been configured."
echo ""

echo -e "${BLUE}Project ID:${NC}        $PROJECT_ID"
echo -e "${BLUE}Service Account:${NC}   $SA_EMAIL"
echo -e "${BLUE}BigQuery Dataset:${NC}  $BIGQUERY_DATASET"
echo -e "${BLUE}GCS Bucket:${NC}        $BUCKET_NAME"
echo -e "${BLUE}Region:${NC}            $REGION"
echo ""

echo "=============================================="
echo "   GitLab CI/CD Variables"
echo "=============================================="
echo ""
echo "Add these variables to your GitLab project:"
echo "Settings > CI/CD > Variables"
echo ""

echo -e "${GREEN}GCP_PROJECT_ID${NC}"
echo "  Value: $PROJECT_ID"
echo "  Protected: No"
echo "  Masked: No"
echo ""

echo -e "${GREEN}GCP_SERVICE_ACCOUNT_KEY${NC}"
echo "  Value: (contents of $KEY_FILE_B64)"
echo "  Protected: Yes"
echo "  Masked: Yes"
echo ""

echo -e "${GREEN}BIGQUERY_DATASET${NC}"
echo "  Value: $BIGQUERY_DATASET"
echo "  Protected: No"
echo "  Masked: No"
echo ""

echo -e "${GREEN}GCS_BUCKET${NC}"
echo "  Value: $BUCKET_NAME"
echo "  Protected: No"
echo "  Masked: No"
echo ""

# Copy to clipboard if possible
if command -v pbcopy &> /dev/null; then
    cat "$KEY_FILE_B64" | pbcopy
    log_success "Base64 key copied to clipboard (macOS)."
elif command -v xclip &> /dev/null; then
    cat "$KEY_FILE_B64" | xclip -selection clipboard
    log_success "Base64 key copied to clipboard (Linux)."
fi

echo "=============================================="
echo "   Quick Copy Commands"
echo "=============================================="
echo ""
echo "# View the base64-encoded service account key:"
echo "cat $KEY_FILE_B64"
echo ""
echo "# Test GCP integration locally:"
echo "export GCP_PROJECT_ID=\"$PROJECT_ID\""
echo "export GCP_SERVICE_ACCOUNT_KEY=\"\$(cat $KEY_FILE_B64)\""
echo "python -m src.gcp.cli status"
echo ""

echo "=============================================="
echo "   Security Reminders"
echo "=============================================="
echo ""
log_warning "1. Delete the key files after adding to GitLab:"
echo "   rm $KEY_FILE $KEY_FILE_B64"
echo ""
log_warning "2. Rotate service account keys every 90 days"
echo ""
log_warning "3. Never commit service account keys to git"
echo ""

echo "=============================================="
echo "   Next Steps"
echo "=============================================="
echo ""
echo "1. Copy the base64 key to GitLab CI/CD variables"
echo "2. Trigger the ComplianceBot flow on a merge request"
echo "3. Check BigQuery for logged findings"
echo "4. Check GCS bucket for PDF reports"
echo ""

log_success "Setup complete! 🎉"
