# Cloud Build Setup Guide (No Docker Needed!)

## Overview

Since you don't have Docker installed, we use **Google Cloud Build** to automatically build and deploy your Cloud Run service. Cloud Build handles everything in the cloud—no local Docker daemon needed.

---

## How Cloud Build Works

```
Your repository (with Dockerfile)
        ↓
git commit & push
        ↓
Cloud Build (GCP) automatically:
  1. Detects Dockerfile in source
  2. Builds image in cloud
  3. Pushes to Container Registry (gcr.io)
  4. Cloud Run deploys latest image
        ↓
Service runs on Cloud Run
```

**Key Benefit**: Everything happens in GCP. Your laptop never needs Docker!

---

## One-Command Deployment

You don't need Docker installed. Just run:

```bash
cd c:\Users\omana\Projects\compliancebot-gitlab-hackathon

# Export GCP project ID
export GCP_PROJECT_ID="your-gcp-project-id"

# Run deployment script (uses Cloud Build)
bash cloud/cloud_run/deploy.sh $GCP_PROJECT_ID
```

The script will:
1. ✅ Enable Cloud Build API
2. ✅ Build your Dockerfile with Cloud Build
3. ✅ Push image to Google Container Registry
4. ✅ Deploy to Cloud Run automatically
5. ✅ Give you the service URL

---

## Prerequisites

### Required GCP Permissions
You need these roles in GCP:
- `Compute Admin` (for Cloud Run)
- `Storage Admin` (for GCS buckets)
- `BigQuery Admin` (for BigQuery)
- `Cloud Build Service Account` (automatic)

### Required CLI
```bash
# Install Google Cloud CLI if not already done
# Download from: https://cloud.google.com/sdk/docs/install

# Verify installation
gcloud --version

# Authenticate
gcloud auth login

# Set default project
gcloud config set project YOUR-GCP-PROJECT-ID
```

---

## Step-by-Step Deployment (Cloud Build)

### Step 1: Create GCP Project (First Time Only)
```bash
# Create new project
gcloud projects create compliancebot-2026 --name="ComplianceBot Hackathon"

# Get project ID
export GCP_PROJECT_ID=$(gcloud projects list --filter="name:compliancebot-2026" --format="value(projectId)")

# Set as default
gcloud config set project $GCP_PROJECT_ID
```

### Step 2: Enable Required APIs
```bash
# Cloud Build will do this automatically, but you can do it manually:
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    bigquery.googleapis.com \
    storage-api.googleapis.com \
    aiplatform.googleapis.com
```

### Step 3: Deploy with Cloud Build
```bash
# From your project root
bash cloud/cloud_run/deploy.sh $GCP_PROJECT_ID

# Output:
# ✅ Deployment complete!
#    Service URL: https://compliance-reporter-xxxxx.run.app
```

**What the script does**:
- ✅ Enables Cloud Build API
- ✅ Creates service account with proper permissions
- ✅ Runs `gcloud builds submit` which:
  - Uploads your code to GCS temporary bucket
  - Cloud Build reads Dockerfile
  - Builds image (you don't need Docker locally!)
  - Pushes to gcr.io/$PROJECT_ID/compliance-reporter
- ✅ Deploys to Cloud Run
- ✅ Returns service URL

### Step 4: Verify Deployment
```bash
# Check Cloud Run service status
gcloud run services describe compliance-reporter --region=us-central1

# View deployment logs
gcloud run logs read compliance-reporter --region=us-central1 --limit=20

# Test the service (requires authentication)
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://compliance-reporter-xxxxx.run.app/generate-report \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"project_id": "test", "evidence_package": {}}'
```

---

## How the Dockerfile Works

Your `cloud/cloud_run/Dockerfile`:

```dockerfile
# Multi-stage build for Cloud Build execution
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY report_generator.py .

# Environment setup
ENV PYTHONUNBUFFERED=True \
    PORT=8080

# Run with gunicorn
CMD exec gunicorn --bind 0.0.0.0:${PORT} report_generator:app
```

**Cloud Build Process**:
1. Pulls `python:3.11-slim` base image
2. Installs dependencies from requirements.txt
3. Copies your code
4. Sets environment variables
5. Runs gunicorn to start Flask app
6. Container is deployed to Cloud Run

---

## Cost Note

Cloud Build pricing:
- **First 120 minutes/day**: FREE (great for hackathon!)
- Additional: $0.003 per minute
- Each deployment typically takes 3-5 minutes
- You can deploy many times during hackathon for free

---

## Troubleshooting Cloud Build

### Build Fails: "Cannot find Dockerfile"
```
Solution:
1. Ensure Dockerfile is in cloud/cloud_run/ directory
2. Check filename: must be exactly "Dockerfile" (capital D)
3. Verify file exists:
   ls -la cloud/cloud_run/Dockerfile
```

### Build Fails: "Docker build error"
```
Solution:
1. Validate Dockerfile syntax:
   # Windows
   type cloud/cloud_run/Dockerfile
   
2. Check requirements.txt has all correct packages:
   cat cloud/cloud_run/requirements.txt

3. View full build log:
   gcloud builds log [BUILD_ID] --stream
```

### Cloud Run Service Won't Start
```
Solution:
1. Check service account permissions:
   gcloud projects get-iam-policy $GCP_PROJECT_ID
   
2. View startup logs:
   gcloud run logs read compliance-reporter --limit=50

3. Verify environment variables are set:
   gcloud run services describe compliance-reporter \
     --region=us-central1 --format='value(spec.template.spec.containers[0].env)'
```

### "Project not found" Error
```
Solution:
export GCP_PROJECT_ID="correct-project-id"
gcloud config set project $GCP_PROJECT_ID
```

---

## Advanced: View Build Progress

While deployment is happening:

```bash
# List recent builds
gcloud builds list --limit=10

# Watch a specific build
gcloud builds log BUILD_ID --stream

# Get build details
gcloud builds describe BUILD_ID
```

---

## Alternative: Manual Cloud Build Submit

If the script doesn't work, try manually:

```bash
# Navigate to Cloud Run directory
cd cloud/cloud_run

# Submit build manually
gcloud builds submit \
    --tag gcr.io/$GCP_PROJECT_ID/compliance-reporter:latest \
    --timeout=1800 \
    .

# Deploy to Cloud Run
gcloud run deploy compliance-reporter \
    --image gcr.io/$GCP_PROJECT_ID/compliance-reporter:latest \
    --region=us-central1 \
    --set-env-vars GCP_PROJECT_ID=$GCP_PROJECT_ID \
    --memory=512Mi
```

---

## Key Differences: Docker vs Cloud Build

| Task | Docker | Cloud Build (No Docker) |
|------|--------|------------------------|
| Build locally | Requires Docker Desktop | ❌ Not needed |
| Dependencies | Installs on your machine | Installs in cloud |
| Artifacts | .exe/.app files | Cloud Registry image |
| Deploy | Manual or shell script | Automatic |
| Cost | Free | Free (120 min/day) |
| Speed | Slower (your laptop) | Faster (GCP servers) |

---

## Summary

**You don't need Docker!** Just run:

```bash
bash cloud/cloud_run/deploy.sh $GCP_PROJECT_ID
```

Everything else happens automatically in Google Cloud. This is the recommended approach for hackathon projects because:

1. ✅ No local Docker installation needed
2. ✅ Builds faster (GCP servers are powerful)
3. ✅ Uses free Cloud Build tier
4. ✅ Automatically deploys to Cloud Run
5. ✅ Integrates seamlessly with GitLab CI/CD

Ready? Run the deployment script! 🚀
