# ComplianceBot Local Runner Guide

> **Run compliance scans locally without GitLab pipeline access.** Archive findings to GCP (optional) and generate audit reports.

## 🎯 What This Enables

✅ **No Pipeline Access Required** - Scan MRs locally, on your machine  
✅ **GCP Optional** - Works with or without Google Cloud credentials  
✅ **Structured Payloads** - Canonical JSON format for consistency  
✅ **Future-Proof** - Code structure supports direct pipeline integration later  
✅ **Audit-Ready** - Generates evidence packages and compliance reports  

## 📋 Quick Start

### Installation

```bash
# Clone and setup
cd compliancebot-gitlab-hackathon
pip install -r requirements.txt

# (Optional) Configure GCP
export GCP_PROJECT_ID="your-project-id"
export GCP_SERVICE_ACCOUNT_KEY="base64-encoded-key"
```

### Run Your First Scan

```bash
# Scan with demo data
python -m src.local_runner scan --mode demo

# Scan your MR (export from GitLab as JSON first)
python -m src.local_runner scan --json /path/to/mr.json --project my-project

# Save report to file
python -m src.local_runner scan --mode demo --output report.json

# Archive to GCP (if configured)
python -m src.local_runner scan --mode demo --archive
```

## 🏗️ Architecture: Local-First Flow

```
┌────────────────────────────────────────────────┐
│         Your Machine (Local)                    │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  ComplianceBot Local Runner              │  │
│  │                                           │  │
│  │  Input: MR JSON  ──────┐                 │  │
│  │                        ▼                 │  │
│  │  [1] Scanner Agent    ✓ Detect issues   │  │
│  │  [2] Mapper Agent     ✓ Map controls    │  │
│  │  [3] Evidence Collector ✓ Gather audit  │  │
│  │  [4] Reporter Agent   ✓ Format results  │  │
│  │                        │                 │  │
│  │                        ▼                 │  │
│  │  Output: ComplianceFinding[]             │  │
│  │          + ComplianceReport JSON         │  │
│  │                                           │  │
│  │  Optional: Archive to GCP ────────────┐  │  │
│  └──────────────────────────────────────┼──┘  │
│                                         │       │
└─────────────────────────────────────────┼─────┘
                                          │
                    ┌─────────────────────▼───────────┐
                    │    Google Cloud Platform        │
                    │                                  │
                    │  BigQuery: Findings analytics   │
                    │  Cloud Storage: Reports & PDF   │
                    │                                  │
                    └──────────────────────────────────┘
```

## 📝 Input Formats

### Option A: Demo Data (Quickest)

```bash
python -m src.local_runner scan --mode demo
```

Uses fixture data with intentional compliance issues for testing.

### Option B: Export from GitLab UI

1. Open MR in GitLab
2. Click **"..."** → **Download as JSON** (if available) or
3. Use GitLab API to export:

```bash
# Get MR data from GitLab
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/YOUR_PROJECT_ID/merge_requests/MR_IID" \
  > mr.json

# Scan locally
python -m src.local_runner scan --json mr.json --project YOUR_PROJECT_ID
```

### Option C: Manual JSON File

Create `mr.json` with structure:

```json
{
  "id": 12345,
  "iid": 42,
  "title": "Add authentication",
  "project_name": "my-service",
  "source_branch": "feat/auth",
  "target_branch": "main",
  "diffs": [
    {
      "new_path": "src/auth.py",
      "diff": "...unified diff content..."
    }
  ]
}
```

Then scan:

```bash
python -m src.local_runner scan --json mr.json
```

## 📊 Output Formats

### Human-Readable Report

```bash
python -m src.local_runner scan --mode demo
```

Outputs formatted findings to terminal:

```
[src.local_runner] INFO: Starting compliance scan for project local
[src.local_runner] INFO: Running Scanner agent...
[src.local_runner] INFO: Scanner found 5 issues
...
✅ Scan complete: 45/100 score, 5 findings
```

### JSON Report

Save structured output:

```bash
python -m src.local_runner scan --mode demo --output report.json
```

Outputs canonical `ComplianceReport` with:

```json
{
  "report_id": "local-2026-03-24T...-a1b2c3d4",
  "project_id": "local",
  "project_name": "demo-project",
  "compliance_score": 45,
  "findings": [
    {
      "id": "local-42-...",
      "title": "Hardcoded API key in auth.py",
      "severity": "critical",
      "frameworks": ["ISO 27001", "SOC 2"],
      "controls": [
        {
          "id": "ISO27001-A.10.1.1",
          "framework": "ISO 27001",
          "description": "Encryption of sensitive data"
        }
      ],
      "remediation_steps": [
        "Move API key to environment variable",
        "Rotate the exposed key in production"
      ],
      "file_path": "src/auth.py",
      "line_number": 42,
      "status": "open",
      "detected_at": "2026-03-24T..."
    }
  ],
  "stats": {
    "total_findings": 5,
    "critical": 2,
    "high": 1,
    "medium": 2,
    "frameworks_covered": 4
  }
}
```

## 🔐 GCP Integration (Optional)

### Check GCP Status

```bash
python -m src.local_runner status
```

Output:

```
🔧 GCP Integration Status
==================================================
  available: True
  project_id: my-gcp-project
  services:
    bigquery: True
    gcs: True
==================================================

✅ GCP is configured and ready for archival
```

### Scan + Archive to GCP

```bash
# One command: scan + archive to BigQuery + Cloud Storage
python -m src.local_runner scan --mode demo --archive

# Or archive separately
python -m src.local_runner scan --mode demo --output report.json
python -m src.local_runner archive --report report.json --to bigquery,gcs
```

### What Gets Archived

**BigQuery Table: `compliance.compliance_findings`**

- One row per finding
- Enables trend analysis and dashboards
- Queryable for audits

```sql
SELECT
  control_id,
  severity,
  COUNT(*) as count
FROM compliance.compliance_findings
WHERE finding_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY control_id, severity
ORDER BY count DESC;
```

**Cloud Storage: `gs://{bucket}/reports/{report_id}.json`**

- Full report with findings, evidence, stats
- 1-year retention (configurable)
- Queryable via BigQuery external tables

## 🔧 Configuration

### Environment Variables

```bash
# Required for GCP archival
export GCP_PROJECT_ID="my-gcp-project"
export GCP_SERVICE_ACCOUNT_KEY="base64-encoded-service-account-json"

# Optional (have defaults)
export GCP_REGION="us-central1"
export BIGQUERY_DATASET="compliance"
export GCS_BUCKET="compliance-evidence-${GCP_PROJECT_ID}"
```

### Get GCP Credentials

```bash
# Download service account key from GCP Console
# Then encode it
cat service-account-key.json | base64 -w 0 > key.b64

# Use in environment
export GCP_SERVICE_ACCOUNT_KEY=$(cat key.b64)
```

### Local-Only Mode (No GCP)

The runner works perfectly without GCP:

```bash
# Scan locally, save JSON report (no archival)
python -m src.local_runner scan --mode demo --output report.json

# Later, if you get GCP access:
python -m src.local_runner archive --report report.json --to bigquery,gcs
```

## 🚀 Advanced Usage

### Batch Scan Multiple MRs

```bash
#!/bin/bash
# scan_all_mrs.sh

for mr_file in /path/to/mrs/*.json; do
  project=$(basename "$mr_file" .json)
  echo "Scanning $project..."
  python -m src.local_runner scan \
    --json "$mr_file" \
    --project "$project" \
    --output "reports/${project}.json" \
    --archive
done
```

### Integrate with CI/CD (Non-GitLab)

Your CI pipeline can call the local runner:

```bash
# In your CI (Jenkins, CircleCI, GitHub Actions, etc.)
pip install -r requirements.txt
python -m src.local_runner scan \
  --json "$CI_MERGE_REQUEST_JSON" \
  --project "$CI_PROJECT_ID" \
  --archive
```

### Generate Dashboard Data

```bash
# Scan all saved reports and generate dashboard data
python -c "
from src.dashboard.data_loader import get_findings
from src.utils.payload_schema import ComplianceReport
import json

with open('report.json') as f:
    report = ComplianceReport.from_dict(json.load(f))

# Dashboard can query findings directly
for finding in report.findings:
    print(f'{finding.title}: {finding.severity.value}')
"
```

## 🔄 Migration to Pipeline (Future)

When you get GitLab Maintainer permission, here's what changes:

### Current (Local-First)

```bash
python -m src.local_runner scan --json mr.json --archive
```

### Future (Pipeline-Integrated)

1. Update `.gitlab-ci.yml` to run the agent flow
2. Pipeline produces same `ComplianceReport` JSON
3. Pipeline archives using same GCP credentials
4. **Your code doesn't change** - pipeline just orchestrates local runner

```yaml
# .gitlab-ci.yml (future)
compliance-scan:
  stage: compliance
  script:
    - python -m src.local_runner archive --report $CI_ARTIFACTS/report.json --to bigquery,gcs
```

The architecture supports both paths because:
- ✅ Canonical schema is version-stable
- ✅ Converters handle both local and pipeline inputs
- ✅ GCP client works with or without pipeline context
- ✅ Agents are independent of GitLab integration

## 📚 Schema & API Reference

### ComplianceReport Schema

See [ComplianceReport](src/utils/payload_schema.py) for full schema.

Key sections:

```python
# Metadata
report_id: str  # Unique identifier
project_id: str
project_name: str

# Results
findings: List[ComplianceFinding]  # One per issue
compliance_score: int  # 0-100

# Execution
started_at: str  # ISO 8601
finished_at: str
agents_executed: List[str]  # ["scanner", "mapper", ...]

# Archival
archived_to: List[str]  # ["bigquery", "gcs"]
```

### ComplianceFinding Schema

```python
# Identification
id: str
title: str
description: str

# Classification
finding_type: FindingType  # e.g., "secret_hardcoded"
severity: FindingSeverity  # "critical" | "high" | "medium" | "low"
status: FindingStatus  # "open" | "remediated" | "accepted"

# Compliance Mapping
controls: List[Control]  # SOC2-CC6.1, ISO27001-A.8.1.1, etc.
frameworks: List[Framework]  # Derived from controls

# Location & Context
file_path: Optional[str]
line_number: Optional[int]
code_snippet: Optional[str]

# Remediation
remediation_steps: List[str]
assigned_to: Optional[str]

# Scoring
compliance_score_impact: int  # Points deducted from 100
```

See [payload_schema.py](src/utils/payload_schema.py) for complete type definitions.

## 🛠️ Troubleshooting

### "GCP is not configured"

**Problem:** Getting "GCP is not configured" when trying to archive

**Solution:**

```bash
1. Check env vars:
   echo $GCP_PROJECT_ID
   echo $GCP_SERVICE_ACCOUNT_KEY

2. Set them:
   export GCP_PROJECT_ID="my-project"
   export GCP_SERVICE_ACCOUNT_KEY="$(cat key.b64)"

3. Verify:
   python -m src.local_runner status
```

### "Failed to read MR JSON"

**Problem:** File not found or invalid JSON

**Solution:**

```bash
# Validate JSON
python -m json.tool mr.json

# Try with full path
python -m src.local_runner scan --json "$(pwd)/mr.json"
```

### "BigQuery table not found"

**Problem:** Table `compliance.compliance_findings` doesn't exist

**Solution:**

```bash
# Create schema (one-time setup)
bq mk --dataset --location=US compliance
bq mk --table compliance.compliance_findings \
  cloud/bigquery_schema.sql
```

### Scanner finds no issues

**Problem:** Scanner returns empty findings list

**Solution:**

```bash
# Run in verbose mode
python -m src.local_runner scan --mode demo --verbose 2>&1 | head -50

# Check scanner logs
grep -i "scanner\|security\|issue" /tmp/compliancebot.log
```

## 📖 Next Steps

- **Dashboard:** See [dashboard/README.md](../dashboard/README.md) for analytics
- **Agents:** See [AGENTS.md](../AGENTS.md) for agent internals
- **GCP Setup:** See [docs/GCP_SETUP.md](../docs/GCP_SETUP.md) for detailed setup
- **Testing:** See [TESTING_QUICK_REFERENCE.md](../TESTING_QUICK_REFERENCE.md) for running tests

## 💡 Design Principles

The local runner implements these core principles:

1. **Local-First** - Works without any external service
2. **Schema-Driven** - Canonical schema ensures consistency
3. **Composable** - Find → Map → Evidence → Report
4. **Extensible** - New agents/frameworks plug in easily
5. **Future-Proof** - Pipeline integration doesn't require refactoring
6. **Audit-Ready** - Evidence hashing and integrity checks built-in

## 🤝 Contributing

Want to add a new analyzer or archival destination?

1. Implement agent in `src/agents/`
2. Add tests in `tests/`
3. Update `local_runner.py` to invoke it
4. Payload schema stays stable - converters handle translation

Example: [Adding a new agent](docs/EXTENDING.md)

---

**Last Updated:** March 24, 2026  
**Version:** 1.0.0
