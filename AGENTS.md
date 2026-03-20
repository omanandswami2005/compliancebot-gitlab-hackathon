# ComplianceBot Flow — Agent Instructions

## Context
This project uses ComplianceBot Flow to automatically analyze merge requests
and CI/CD pipelines for compliance with SOC 2, ISO 27001, PCI-DSS, and HIPAA.

## Architecture
ComplianceBot integrates with:
- **GitLab AI Catalog** — Agent publishing and flow management per official schema
- **Google Cloud Vertex AI** — AI model for compliance narrative generation (Gemini-2.5-flash)
- **Google Cloud BigQuery** — Evidence archival and compliance analytics
- **Google Cloud Storage** — Long-term evidence retention with 1-year SOC 2 compliance

## Agent Structure & Format

All agents are defined in `agents/` directory at repository root, following the official GitLab AI Catalog YAML schema:

```yaml
name: agent-name                    # Required: 3-255 characters
description: "What this agent does" # Required: max 1024 characters
public: true                        # Optional: boolean (default true)
system_prompt: |                    # Required
  Detailed system instructions for agent behavior
tools:                              # Optional
  - tool1
  - tool2
```

## Agent Behavior Guidelines

### ComplianceBot Scanner (`agents/compliance-scanner.yaml`)
- **Purpose**: Analyze MRs and pipelines for compliance signals
- **Input**: Merge request diffs, pipeline results, vulnerability reports
- **Output**: JSON findings with severity, control IDs, remediation steps
- **Behavior**:
  - Always include file paths in findings
  - Map every finding to at least one control ID (SOC2-CC6.1, ISO27001-A.8.2.3, etc.)
  - Never report informational findings for boilerplate files (README, CHANGELOG)
  - Treat dependency lock file changes as informational only unless CVEs are detected
  - Detect: Auth changes, encryption configs, dependency vulnerabilities, SAST findings

### ComplianceBot Mapper (`agents/compliance-mapper.yaml`)
- **Purpose**: Map findings to compliance framework controls
- **Input**: Finding list, compliance frameworks
- **Output**: Control mappings, risk assessment, compliance score (0-100)
- **Behavior**:
  - Primary framework: SOC 2 (always include)
  - Secondary frameworks: ISO 27001 (always), PCI-DSS (if payment-related code detected), HIPAA (if health data detected)
  - Use NIST SP 800-53 as supplemental reference
  - Score 0-100 where 100 = fully audit-ready
  - Assess business risk and remediation priority

### ComplianceBot Evidence Collector (`agents/evidence-collector.yaml`)
- **Purpose**: Gather audit trail evidence from GitLab activity
- **Input**: Project context, mapped controls
- **Output**: Evidence package with SHA-256 hashes, archived to BigQuery
- **Behavior**:
  - Evidence collection period: Last 14 days (default), 30 days for scheduled audits
  - Collect: MR metadata, pipeline results, access logs, code reviews
  - Always include SHA-256 hash of evidence for non-repudiation
  - Maximum 500 MR records per collection run
  - Archive to BigQuery with 1-year SOC 2 retention policy

### ComplianceBot Reporter (`agents/compliance-reporter.yaml`)
- **Purpose**: Generate audit-ready compliance reports
- **Input**: Evidence package, control mappings
- **Output**: Executive summary, PDF report, GitLab issues, MR comments
- **Behavior**:
  - Tone: Professional, auditor-friendly
  - Executive summary: Max 3 sentences, always includes compliance score (0-100)
  - Include remediation timeline estimates (days to compliance)
  - Post MR comment only if score < 85 (avoid alert fatigue)
  - Generate audit-ready PDFs with evidence hashes and timestamps
  - Use Vertex AI (Gemini-2.5-flash) for narrative generation

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
