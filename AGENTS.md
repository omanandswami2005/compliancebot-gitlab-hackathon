# ComplianceBot Flow - Agent Instructions

## Overview

ComplianceBot is a multi-agent compliance flow that automatically analyzes merge requests for security and compliance issues. It maps findings to SOC 2, ISO 27001, PCI-DSS, and HIPAA controls, then generates audit-ready reports.

## How It Works

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Scanner    │───▶│    Mapper    │───▶│   Evidence   │───▶│   Reporter   │
│    Agent     │    │    Agent     │    │  Collector   │    │    Agent     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
      │                   │                   │                   │
 Read MR diffs      Map to SOC2         Gather audit        Post comment
 Find issues        ISO27001            evidence            Create issues
                    PCI-DSS
                    HIPAA
```

## Triggering the Flow

On any merge request, use one of these methods:

1. **Mention**: `@ai-compliance-bot-flow-gitlab-ai-hackathon analyze this MR`
2. **Assign**: Assign the flow as a reviewer
3. **Assign reviewer**: Add the flow as a reviewer

## Agent Definitions

All agents are in the `agents/` directory:

### 1. Scanner Agent (`compliance-scanner.yml`)

**Purpose**: Scans MR diffs for compliance-relevant code changes

**Detects**:
- Hardcoded secrets (API keys, passwords, private keys)
- Weak encryption (MD5, SHA1, disabled SSL)
- Authentication issues (SQL injection, weak sessions)
- Dependency vulnerabilities (known CVEs)
- Configuration problems (debug mode, permissive CORS)
- Process violations (missing change tickets)

**Output**: JSON findings with severity and control IDs

### 2. Mapper Agent (`compliance-mapper.yml`)

**Purpose**: Maps findings to compliance framework controls

**Frameworks**:
- SOC 2 (CC6.1-CC8.1)
- ISO 27001 (A.8-A.12)
- PCI-DSS (Req 6, 8, 10)
- HIPAA (§164.312)
- Custom (ORG-001, ORG-002, ORG-003)

**Scoring**:
- Start at 100 points
- Critical: -25 points
- High: -15 points
- Medium: -10 points
- Low: -5 points

### 3. Evidence Collector Agent (`evidence-collector.yml`)

**Purpose**: Gathers audit trail evidence

**Collects**:
- MR metadata (author, reviewers, approvers)
- Commit history with timestamps
- Review comments and discussions
- Pipeline execution results

**Security**: SHA-256 hashing for non-repudiation

### 4. Reporter Agent (`compliance-reporter.yml`)

**Purpose**: Generates reports and creates issues

**Actions**:
- Posts compliance comment on MR (if score < 85)
- Creates GitLab issues for findings (severity >= medium)
- Includes remediation steps and timelines

## Custom Controls

| Control | Description | Trigger |
|---------|-------------|---------|
| ORG-001 | Change ticket required | MR description missing ticket reference |
| ORG-002 | DBA approval required | Database migration without `db-migration` label |
| ORG-003 | CVE patching SLA | Dependencies not updated within 30 days of CVE |

## Behavior Guidelines

### Scanner
- Always include file paths in findings
- Map every finding to at least one control ID
- Ignore boilerplate files (README, CHANGELOG)
- Treat lock file changes as informational unless CVEs detected

### Mapper
- Always include SOC 2 and ISO 27001
- Add PCI-DSS only if payment code detected
- Add HIPAA only if health data detected
- Score 0-100 where 100 = audit-ready

### Evidence Collector
- Default collection: Last 14 days
- Scheduled audits: Last 30 days
- Maximum 500 MRs per collection
- Always include evidence hash

### Reporter
- Professional, auditor-friendly tone
- Executive summary: Max 3 sentences
- Post MR comment only if score < 85
- Create issues for severity >= medium

## GCP Integration (Optional)

When GCP credentials are configured:

| Service | Purpose |
|---------|---------|
| **Vertex AI** | AI-powered compliance narratives |
| **BigQuery** | Historical analytics and trends |
| **Cloud Storage** | PDF reports with 1-year retention |

Without GCP, the flow still works but skips archival features.

## Environment Variables

```bash
# Required for GCP (optional)
GCP_PROJECT_ID=your-project-id
GCP_SERVICE_ACCOUNT_KEY=base64-encoded-key

# Optional
BIGQUERY_DATASET=compliance
GCS_BUCKET=compliance-evidence-{project}
```

## Flow Configuration

The flow is defined in `flows/compliance-flow.yml`:

```yaml
name: "ComplianceBot Flow"
description: "Multi-agent compliance analysis flow"

definition:
  version: "v1"
  environment: ambient
  
  components:
    - name: "scanner"
      type: AgentComponent
      # ... scans MR for issues
      
    - name: "mapper"  
      type: AgentComponent
      # ... maps to compliance controls
      
    - name: "evidence_collector"
      type: AgentComponent
      # ... gathers audit evidence
      
    - name: "reporter"
      type: AgentComponent
      # ... posts reports and creates issues
```

## Testing

Test the flow on MR !10 which contains intentional violations:
- Hardcoded secrets
- Weak encryption
- SQL injection
- Outdated dependencies

Expected result: Score ~0/100, 20+ issues created.
