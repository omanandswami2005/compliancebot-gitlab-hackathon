# ComplianceBot Cloud Run Service

This directory contains the Cloud Run microservice that generates compliance reports and archives evidence to Google Cloud Storage.

## Components

- **report_generator.py** — Flask application that:
  - Uses Vertex AI (Gemini-2.5-flash) to generate narrative summaries
  - Logs findings to BigQuery for compliance analytics
  - Generates PDF reports via ReportLab
  - Uploads PDFs to Cloud Storage with signed URLs

- **Dockerfile** — Container image for Cloud Run deployment

- **requirements.txt** — Python dependencies for the service

- **deploy.sh** — Automated deployment script

## Quick Start

### 1. Set up GCP Prerequisites
```bash
export GCP_PROJECT_ID="your-project-id"
export REGION="us-central1"

# Run the deployment script
bash deploy.sh $GCP_PROJECT_ID
```

### 2. Test Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app locally (requires GCP auth)
export FLASK_APP=report_generator.py
export GCP_PROJECT_ID="your-project-id"
gcloud auth application-default login
python -m flask run --port 8080
```

### 3. Call the Service
```bash
# Request signature
curl -X POST http://localhost:8080/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-project",
    "evidence_package": {
      "findings": [...],
      "compliance_score": 85,
      "frameworks": ["SOC2", "ISO27001"]
    }
  }'
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GCP_PROJECT_ID` | Yes | Google Cloud Project ID |
| `BIGQUERY_DATASET` | No | BigQuery dataset (default: `compliance`) |
| `PORT` | No | Service port (default: `8080`) |

## API Reference

### POST /generate-report

**Request:**
```json
{
  "project_id": "string (required)",
  "evidence_package": {
    "findings": [
      {
        "control_id": "SOC2-CC6.1",
        "severity": "high|medium|low|critical",
        "framework": "SOC2|ISO27001|PCI-DSS|HIPAA"
      }
    ],
    "compliance_score": 0-100,
    "frameworks": ["SOC2", "ISO27001"],
    "generated_at": "string (ISO 8601)",
    "summary": {}
  }
}
```

**Response:**
```json
{
  "report_url": "https://storage.googleapis.com/...",
  "narrative": "Executive summary text...",
  "timestamp": "2026-03-19T10:00:00Z"
}
```

## Costs & Optimization

### Expected Monthly Costs
- **Vertex AI Gemini-2.5-flash**: ~$0.001 per request (very cheap)
- **BigQuery**: Free tier covers most usage; ~$0.07 per GB scanned
- **Cloud Run**: ~$5/month for typical hackathon load
- **Cloud Storage**: ~$0.10/month for evidence PDFs

### Cost Optimization Tips
1. Use `gemini-2.5-flash` instead of `gemini-1.5-pro`
2. Set Cloud Run memory to 512Mi (sufficient for document generation)
3. Enable Cloud Run autoscaling (min=0, max=10)
4. Use Cloud Storage lifecycle policies to move old reports to NEARLINE

## Security

- ✅ Service account with minimal IAM permissions
- ✅ No public access (requires IAM authentication)
- ✅ GCS buckets have 1-year retention (SOC 2 compliance)
- ✅ BigQuery dataset is private

## Monitoring

```bash
# View service logs
gcloud run logs read compliance-reporter --region=us-central1 --limit=50

# Get service metrics
gcloud run services describe compliance-reporter --region=us-central1
```

## Troubleshooting

### Vertex AI API Errors
```bash
# Ensure Vertex AI is enabled
gcloud services enable aiplatform.googleapis.com

# Check service account permissions
gcloud projects get-iam-policy $GCP_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:compliance-runner@*"
```

### BigQuery Insert Errors
```bash
# Verify dataset exists
bq ls -d compliance

# Check table schema
bq show compliance.compliance_findings

# Check permissions
bq show --project_id=$GCP_PROJECT_ID compliance
```

## References

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Generative AI](https://cloud.google.com/vertex-ai/docs/generative-ai)
- [BigQuery Streaming Inserts](https://cloud.google.com/bigquery/docs/streaming-data-types)
