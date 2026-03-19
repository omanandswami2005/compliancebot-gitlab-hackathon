# ComplianceBot Flow — Agent Instructions

## Context
This project uses ComplianceBot Flow to automatically analyze merge requests
and CI/CD pipelines for compliance with SOC 2, ISO 27001, PCI-DSS, and HIPAA.

## Architecture
ComplianceBot integrates with:
- **GitLab Duo Agent Platform** — Agent orchestration and GitLab integration
- **Google Cloud Vertex AI** — AI model for compliance narrative generation (Gemini-2.5-flash)
- **Google Cloud BigQuery** — Evidence archival and compliance analytics
- **Google Cloud Storage** — Long-term evidence retention with 1-year SOC 2 compliance

## Agent Behavior Guidelines

### ComplianceScanner
- Always include file paths in findings
- Map every finding to at least one control ID
- Never report informational findings for boilerplate files (README, CHANGELOG)
- Treat dependency lock file changes as informational only unless CVEs are detected

### ComplianceMapper
- Primary framework: SOC 2 (always include)
- Secondary frameworks: ISO 27001 (always), PCI-DSS (if payment-related code detected)
- Use NIST SP 800-53 mapping as supplemental reference
- Score 0-100 where 100 = fully audit-ready

### EvidenceCollector
- Evidence collection period: current sprint (last 14 days) by default
- For scheduled runs: collect last 30 days
- Always include SHA-256 hash of evidence for non-repudiation
- Maximum 500 MR records per collection run

### ComplianceReporter
- Tone: professional, auditor-friendly
- Executive summary: max 3 sentences
- Include remediation timeline estimates
- Post MR comment only for score < 85 (avoid noise for passing MRs)

## Custom Compliance Controls
This project adds these org-specific controls:
- ORG-001: All production deployments require change ticket reference in MR description
- ORG-002: Database migrations require DBA approval (label: 'db-migration')
- ORG-003: Dependencies upgraded within 30 days of critical CVE disclosure

## Google Cloud Integration

### Evidence Flow
1. **ComplianceScanner** → Detects findings from MR/pipeline
2. **ComplianceMapper** → Maps findings to control IDs
3. **EvidenceCollector** → Gathers audit trail and approvals
4. **ComplianceReporter** → Uses Vertex AI to generate narrative, logs to BigQuery, uploads PDF to GCS

### GCP Services Used
- **Vertex AI (Gemini-2.5-flash)** — Generates compliance narratives (no separate API key needed)
- **BigQuery** — Stores compliance findings for historical analysis
- **Cloud Storage** — Archives evidence PDFs with 1-year retention (SOC 2)
- **Cloud Run** — Hosts report generator microservice

### Configuration
Set these environment variables for GCP integration:
- `GCP_PROJECT_ID` — Your Google Cloud project ID
- `GCP_SERVICE_ACCOUNT_KEY` — Service account JSON key (base64 encoded)
- `BIGQUERY_DATASET` — BigQuery dataset name (default: `compliance`)
- `GCS_BUCKET` — GCS bucket name (default: `compliance-evidence-${GCP_PROJECT_ID}`)

See `docs/configuration.md` for detailed GCP setup instructions.
