# ComplianceBot Configuration Guide

## Overview
ComplianceBot Flow runs on GitLab Duo Agent Platform with Google Cloud integration for evidence archival and report generation.

## Environment Variables

### Required (All Environments)
```bash
# GitLab Configuration
GITLAB_INSTANCE_URL=https://gitlab.com
GITLAB_PROJECT_ID=<your-project-id>
GITLAB_PERSONAL_TOKEN=<gitlab-token>

# Google Cloud (GCP) Configuration
GCP_PROJECT_ID=<gcp-project-id>
GCP_SERVICE_ACCOUNT_KEY=<path-to-service-account-json>
```

### Optional (Cloud Run Integration)
```bash
# BigQuery Configuration
BIGQUERY_DATASET=compliance
BIGQUERY_TABLE=compliance_findings

# Cloud Storage Configuration
GCS_BUCKET=compliance-evidence-${GCP_PROJECT_ID}
GCS_RETENTION_DAYS=365
```

---

## Google Cloud Setup (GCP Integration)

### 1. Create GCP Project
```bash
gcloud projects create compliance-bot-$RANDOM --name="ComplianceBot"
gcloud config set project <PROJECT_ID>
```

### 2. Enable Required APIs
```bash
gcloud services enable \
  bigquery.googleapis.com \
  storage-api.googleapis.com \
  run.googleapis.com \
  aiplatform.googleapis.com \
  cloudscheduler.googleapis.com
```

### 3. Create BigQuery Dataset & Table
```bash
bq mk --dataset compliance

# Create findings table
bq mk --table \
  compliance.compliance_findings \
  cloud/bigquery_schema.sql
```

### 4. Create GCS Bucket with Retention Policy
```bash
# Create bucket
gsutil mb gs://compliance-evidence-$PROJECT_ID

# Apply 1-year retention policy (SOC 2 requirement)
gsutil retention set 31536000 gs://compliance-evidence-$PROJECT_ID

# Enable versioning for immutable audit trail
gsutil versioning set on gs://compliance-evidence-$PROJECT_ID
```

### 5. Create Service Account for Cloud Run
```bash
# Create service account
gcloud iam service-accounts create compliance-runner \
  --display-name="ComplianceBot Cloud Run Service Account"

# Get service account email
SA_EMAIL=$(gcloud iam service-accounts list --filter="displayName:ComplianceBot" --format='value(email)')

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/bigquery.dataEditor"

# Grant Storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectCreator"

# Grant Vertex AI permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create /tmp/key.json \
  --iam-account=$SA_EMAIL
```

### 6. Deploy Cloud Run Service
```bash
# Build and push Docker image
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/compliance-reporter \
  cloud/cloud_run/

# Deploy to Cloud Run
gcloud run deploy compliance-reporter \
  --image gcr.io/$PROJECT_ID/compliance-reporter:latest \
  --platform managed \
  --region us-central1 \
  --service-account $SA_EMAIL \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID \
  --no-allow-unauthenticated
```

### 7. Configure Terraform for Infrastructure
```bash
cd cloud/terraform

# Initialize Terraform
terraform init \
  -backend-config="bucket=$PROJECT_ID-tf-state" \
  -backend-config="prefix=compliance-bot"

# Plan and apply
terraform plan -out=tfplan
terraform apply tfplan
```

---

## GitLab CI/CD Integration

### Set CI/CD Variables in GitLab
Add these to your GitLab project under **Settings > CI/CD > Variables**:

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `GCP_PROJECT_ID` | Your GCP project ID | No | No |
| `GCP_SERVICE_ACCOUNT_KEY` | Service account JSON (base64 encoded) | Yes | Yes |
| `BIGQUERY_DATASET` | `compliance` | No | No |
| `GCS_BUCKET` | `compliance-evidence-${GCP_PROJECT_ID}` | No | No |

### Upload Evidence to GCS (CI/CD Job)
Add to `.gitlab-ci.yml`:

```yaml
upload_compliance_evidence:
  stage: report
  image: google/cloud-sdk:alpine
  only:
    - merge_requests
    - main
    - production
  script:
    # Authenticate with GCP
    - echo $GCP_SERVICE_ACCOUNT_KEY | base64 -d > /tmp/gcp-key.json
    - gcloud auth activate-service-account --key-file=/tmp/gcp-key.json
    - gsutil cp compliance-report.json gs://${GCS_BUCKET}/reports/
    - gsutil cp compliance-report.pdf gs://${GCS_BUCKET}/reports/
  artifacts:
    paths:
      - compliance-report.*
    expire_in: 90 days
```

---

## Vertex AI Configuration

ComplianceBot uses **Vertex AI Gemini** for report narrative generation (no separate API key needed - uses GCP credentials).

### Enable Vertex AI
```bash
gcloud services enable aiplatform.googleapis.com

# Test Vertex AI access
gcloud ai-platform models list --region=us-central1
```

### Supported Models
- `gemini-2.5-flash` - Fast text generation (recommended for compliance narratives)
- `gemini-1.5-pro` - Advanced reasoning (for complex compliance analysis)

---

## Monitoring & Logging

### Cloud Run Logs
```bash
gcloud run logs read compliance-reporter \
  --region=us-central1 \
  --limit=50
```

### BigQuery Analytics
```sql
-- Query 30-day compliance trends
SELECT
  DATE(finding_date) as date,
  framework,
  AVG(score) as avg_score,
  COUNTIF(status = 'FAIL') as failures
FROM compliance.compliance_findings
WHERE finding_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY date, framework
ORDER BY date DESC;
```

### Cost Monitoring
```bash
gcloud billing budgets create \
  --billing-account=<BILLING_ACCOUNT_ID> \
  --display-name="ComplianceBot GCP Budget" \
  --budget-amount=100 \
  --threshold-rule=percent=80
```

---

## Troubleshooting

### Cloud Run Service Not Starting
```bash
# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format='table(bindings.role)' \
  --filter="bindings.members:$SA_EMAIL"

# View service logs
gcloud run logs read compliance-reporter --limit=100
```

### BigQuery Insert Errors
```bash
# Verify table schema
bq show compliance.compliance_findings

# Check dataset permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format='table(bindings.role)' \
  --filter="bindings.members:$SA_EMAIL"
```

### GCS Upload Failures
```bash
# Verify bucket exists and has proper permissions
gsutil ls gs://compliance-evidence-$PROJECT_ID/

# Check bucket metadata
gsutil stat gs://compliance-evidence-$PROJECT_ID/
```

---

## Cost Optimization Tips

1. **BigQuery**: Use partitioning by date to optimize queries
2. **Cloud Run**: Enabled autoscaling (recommended: min=0, max=10)
3. **Cloud Storage**: Move old reports to NEARLINE storage (90+ days)
4. **Vertex AI**: Use `gemini-2.5-flash` instead of `gemini-1.5-pro` for lower cost

---

## Security Best Practices

1. ✅ Service accounts have minimal permissions (principle of least privilege)
2. ✅ GCS bucket has 1-year retention policy (compliance requirement)
3. ✅ BigQuery dataset has no public access
4. ✅ Cloud Run service requires IAM authentication
5. ✅ Service account keys rotated every 90 days

---

## References

- [Google Cloud BigQuery Setup](https://cloud.google.com/bigquery/docs/quickstart-quickstart)
- [Cloud Run Deployment Guide](https://cloud.google.com/run/docs/quickstarts/deploy-container)
- [Vertex AI Generative AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Cloud Storage Retention Policies](https://cloud.google.com/storage/docs/managing-data-retention)
