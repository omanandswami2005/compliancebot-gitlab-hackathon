# GCP Integration Setup Guide

This guide explains how to set up Google Cloud Platform integration for ComplianceBot.

## Overview

ComplianceBot's GCP integration provides:
- **BigQuery** - Store compliance findings for trend analysis
- **Cloud Storage** - Archive PDF reports and evidence packages (1-year retention)
- **Vertex AI** - Generate AI-powered compliance narratives using Gemini

**Important:** GCP integration is **optional**. The main ComplianceBot flow works without GCP credentials. When GCP is not configured, the flow will:
- ✅ Continue to scan MRs for compliance issues
- ✅ Create GitLab issues for findings
- ✅ Post compliance comments on MRs
- ⚠️ Skip BigQuery logging (with warning)
- ⚠️ Skip Cloud Storage archival (with warning)
- ⚠️ Use fallback narrative generation (without AI enhancement)

## Two Activation Paths

### Path 1: Local-First (No Permission Required) ⭐ Recommended for Hackathon

Run ComplianceBot locally on your machine, then archive to GCP:

```bash
# 1. Scan locally (no pipeline needed)
python -m src.local_runner scan --json mr.json --project my-project

# 2. Archive results to GCP (with local credentials)
python -m src.local_runner scan --mode demo --archive
```

**Benefits:**
- Works immediately without pipeline access
- Full control over when/what to scan
- Supports batch processing
- Non-blocking - GCP failures don't affect scans

**Then, if you get Maintainer permission later:**
- Update GitLab CI/CD variables
- Add `.gitlab-ci.yml` step
- Same code works in pipeline (no migration needed)

See [docs/LOCAL_RUNNER.md](LOCAL_RUNNER.md) for detailed guide.

### Path 2: Pipeline-Integrated (Maintainer Access Required)

Skip this section unless you have pipeline trigger permission.

## Quick Start (Local-First)

### 1. Set Environment Variables

For local archival to GCP:

```bash
# Required for archival
export GCP_PROJECT_ID="your-gcp-project-id"
export GCP_SERVICE_ACCOUNT_KEY="<base64-encoded-service-account-json>"

# Optional (have defaults)
export GCP_REGION="us-central1"
export BIGQUERY_DATASET="compliance"
export GCS_BUCKET="compliance-evidence-${GCP_PROJECT_ID}"
```

### 2. Check GCP Status

```bash
# Check if GCP is properly configured
python -m src.local_runner status
```

Expected output when configured:
```
🔧 GCP Integration Status
==================================================
  available: True
  project_id: your-project-id
  services:
    bigquery: True
    gcs: True
==================================================

✅ GCP is configured and ready for archival
```

### 3. Test Local Scan + Archive

```bash
# Demo scan with archival
python -m src.local_runner scan --mode demo --archive

# With your MR
python -m src.local_runner scan --json mr.json --project my-project --archive
```

## Detailed Setup

### Step 1: Create GCP Project

```bash
# Create new project (or use existing)
gcloud projects create compliancebot-$RANDOM --name="ComplianceBot"
gcloud config set project <PROJECT_ID>

# Enable billing (required for most services)
gcloud billing accounts list
gcloud billing projects link <PROJECT_ID> --billing-account=<BILLING_ACCOUNT_ID>
```

### Step 2: Enable Required APIs

```bash
gcloud services enable \
  bigquery.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com
```

### Step 3: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create compliancebot \
  --display-name="ComplianceBot Service Account"

# Get service account email
SA_EMAIL="compliancebot@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant required permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/compliancebot-key.json \
  --iam-account=$SA_EMAIL

# Base64 encode for GitLab CI/CD
cat ~/compliancebot-key.json | base64 -w 0 > ~/compliancebot-key-b64.txt
```

### Step 4: Create BigQuery Dataset

```bash
# Create dataset
bq mk --dataset \
  --location=US \
  --description="ComplianceBot compliance findings" \
  ${PROJECT_ID}:compliance

# Create table from schema
bq query --use_legacy_sql=false < cloud/bigquery_schema.sql
```

### Step 5: Create Cloud Storage Bucket

```bash
# Create bucket
gsutil mb -l US gs://compliance-evidence-${PROJECT_ID}

# Set 1-year retention policy (SOC 2 requirement)
gsutil retention set 365d gs://compliance-evidence-${PROJECT_ID}

# Enable versioning for audit trail
gsutil versioning set on gs://compliance-evidence-${PROJECT_ID}
```

### Step 6: Configure GitLab CI/CD Variables

Go to **Settings > CI/CD > Variables** and add:

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `GCP_PROJECT_ID` | Your GCP project ID | No | No |
| `GCP_SERVICE_ACCOUNT_KEY` | Contents of `compliancebot-key-b64.txt` | Yes | Yes |
| `BIGQUERY_DATASET` | `compliance` | No | No |
| `GCS_BUCKET` | `compliance-evidence-<project-id>` | No | No |

## Usage

### From Python Code

```python
from src.gcp.integration import archive_compliance_results, get_gcp_status

# Check status
status = get_gcp_status()
print(f"GCP Available: {status['gcp_available']}")

# Archive compliance results
results = archive_compliance_results(
    findings=[...],
    compliance_score=75,
    frameworks=['SOC2', 'ISO27001'],
    project_id='my-org/my-project',
    project_name='My Project',
    mr_id=10,
    mr_url='https://gitlab.com/my-org/my-project/-/merge_requests/10',
    mr_title='Feature: Add authentication',
    evidence_package={...},
    generate_pdf=True
)

# Check results
print(f"BigQuery: {results['operations']['bigquery']['success']}")
print(f"PDF Upload: {results['operations']['pdf_report']['success']}")
```

### From CLI

```bash
# Archive from JSON file
python -m src.gcp.cli archive \
  --input compliance-results.json \
  --output archive-results.json

# Archive with parameters
python -m src.gcp.cli archive \
  --project-id "my-org/my-project" \
  --project-name "My Project" \
  --mr-id 10 \
  --mr-url "https://gitlab.com/my-org/my-project/-/merge_requests/10" \
  --score 75 \
  --frameworks "SOC2,ISO27001" \
  --findings findings.json
```

### From CI/CD Pipeline

Add to `.gitlab-ci.yml`:

```yaml
archive-compliance:
  stage: report
  image: python:3.11-slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  before_script:
    - pip install -r requirements.txt
  script:
    - python -m src.gcp.cli archive \
        --project-id "$CI_PROJECT_PATH" \
        --project-name "$CI_PROJECT_NAME" \
        --mr-id "$CI_MERGE_REQUEST_IID" \
        --mr-url "$CI_MERGE_REQUEST_PROJECT_URL/-/merge_requests/$CI_MERGE_REQUEST_IID" \
        --input compliance-results.json \
        --output archive-results.json
  artifacts:
    paths:
      - archive-results.json
    expire_in: 90 days
```

## Troubleshooting

### "GCP_PROJECT_ID environment variable not set"

Set the environment variable:
```bash
export GCP_PROJECT_ID="your-project-id"
```

### "GCP credentials not configured"

Ensure one of these is set:
- `GCP_SERVICE_ACCOUNT_KEY` - Base64-encoded service account JSON
- `GCP_CREDENTIALS_PATH` - Path to service account JSON file
- `GOOGLE_APPLICATION_CREDENTIALS` - Standard GCP credentials path

### "BigQuery insert errors"

1. Check table exists: `bq show compliance.compliance_findings`
2. Verify permissions: Service account needs `roles/bigquery.dataEditor`
3. Check schema matches: Run `cloud/bigquery_schema.sql`

### "GCS bucket does not exist"

Create the bucket:
```bash
gsutil mb -l US gs://compliance-evidence-${GCP_PROJECT_ID}
```

### "Vertex AI not available"

1. Enable API: `gcloud services enable aiplatform.googleapis.com`
2. Check permissions: Service account needs `roles/aiplatform.user`
3. Verify region supports Gemini: Use `us-central1`

## Cost Optimization

| Service | Estimated Cost | Optimization |
|---------|---------------|--------------|
| BigQuery | ~$5/TB queried | Use partitioning, limit date ranges |
| Cloud Storage | ~$0.02/GB/month | Use NEARLINE for old reports |
| Vertex AI | ~$0.00025/1K chars | Use gemini-2.0-flash (faster, cheaper) |

**Estimated monthly cost for typical usage:** $5-20/month

## Security Best Practices

1. ✅ Use dedicated service account with minimal permissions
2. ✅ Store credentials in GitLab CI/CD variables (masked)
3. ✅ Enable GCS bucket versioning for audit trail
4. ✅ Set retention policy for compliance (1 year for SOC 2)
5. ✅ Rotate service account keys every 90 days
6. ✅ Use VPC Service Controls for sensitive projects

## Pipeline Integration (Future - When You Get Maintainer Access)

Once you have GitLab Maintainer permission, upgrading from local-first to pipeline integration is simple:

### Step 1: Add CI/CD Variables

Go to **Settings > CI/CD > Variables**:

| Variable | Value |
|----------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_SERVICE_ACCOUNT_KEY` | Base64-encoded key |
| `BIGQUERY_DATASET` | `compliance` |
| `GCS_BUCKET` | `compliance-evidence-{project}` |

### Step 2: Create `.gitlab-ci.yml` Step

Add to your pipeline:

```yaml
compliance-scan:
  stage: quality
  image: python:3.11-slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  before_script:
    - pip install -r requirements.txt
  script:
    # Same command you used locally!
    - python -m src.local_runner scan \
        --json $CI_MERGE_REQUEST_JSON \
        --project "$CI_PROJECT_ID" \
        --archive
  artifacts:
    paths:
      - compliance-report-*.json
    expire_in: 30 days
```

### Why This Works (Zero Code Changes)

The local runner was designed to work everywhere because:

✅ **Canonical Schema** - Same `ComplianceReport` format locally and in pipeline  
✅ **Portable Agents** - Agents are independent of execution context  
✅ **GCP Client Agnostic** - Uses environment variables, works anywhere  
✅ **No Git Dependency** - Doesn't require pipeline-specific context  

**Result:** Your local development code IS the pipeline code. No migration, no refactoring.

## References

- [Google Cloud BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Vertex AI Generative AI Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/quickstart-multimodal)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [ComplianceBot Local Runner Guide](LOCAL_RUNNER.md)
