# ComplianceBot Flow

An AI-powered multi-agent compliance flow built on the GitLab Duo Agent Platform that monitors merge requests, maps findings to compliance controls, and generates audit-ready evidence packages.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              GitLab Duo Agent Platform               │
│                                                     │
│  ┌──────────────┐    ┌──────────────────────────┐   │
│  │   Triggers   │───▶│     ComplianceBot Flow   │   │
│  │              │    │                          │   │
│  │ • MR Created │    │  ┌────────────────────┐  │   │
│  │ • Pipeline   │    │  │ 1. Scanner Agent   │  │   │
│  │   Completed  │    │  │   (MR Analysis)    │  │   │
│  │ • Schedule   │    │  └────────┬───────────┘  │   │
│  │   (Nightly)  │    │           │              │   │
│  │ • Manual     │    │  ┌────────▼───────────┐  │   │
│  │   Trigger    │    │  │ 2. Mapper Agent    │  │   │
│  └──────────────┘    │  │ (Control Mapping)  │  │   │
│                      │  └────────┬───────────┘  │   │
│                      │           │              │   │
│                      │  ┌────────▼───────────┐  │   │
│                      │  │ 3. Evidence Agent  │  │   │
│                      │  │ (Evidence Collect) │  │   │
│                      │  └────────┬───────────┘  │   │
│                      │           │              │   │
│                      │  ┌────────▼───────────┐  │   │
│                      │  │ 4. Reporter Agent  │  │   │
│                      │  │  (Report Generate) │  │   │
│                      │  └────────────────────┘  │   │
│                      └──────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- GitLab account with Duo Agent Platform access
- Google Cloud project with billing enabled
- GitLab PAT token (with `api`, `read_api`, `write_repository` scopes)
- VS Code with [GitLab PAT extension](https://marketplace.visualstudio.com/items?itemName=GitLab.gitlab-workflow)

### 1. Configure Google Cloud

Set these environment variables or in your GitLab CI/CD settings:
```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_SERVICE_ACCOUNT_KEY="your-service-account-key-base64"
export BIGQUERY_DATASET="compliance"  # default
export GCS_BUCKET="compliance-evidence-${GCP_PROJECT_ID}"
```

See [GCP Configuration Guide](docs/configuration.md) for detailed setup.

### 2. Deploy Cloud Run Service

No Docker required! Uses Google Cloud Build:
```bash
bash cloud/cloud_run/deploy.sh $GCP_PROJECT_ID
```

See [Cloud Build Deployment Guide](docs/CLOUD_BUILD_GUIDE.md) for details.

### 3. Publish to AI Catalog

See [Agent Publishing Guide](docs/PUBLISHING_GUIDE.md) for step-by-step instructions on:
- Setting up GitLab PAT in VS Code
- Publishing 4 agents to AI Catalog
- Publishing the compliance flow
- Hackathon submission checklist

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Agent Platform** | GitLab Duo | Agent orchestration and flow management |
| **AI Model** | Google Vertex AI (Gemini-2.5-flash) | Compliance narrative generation |
| **Compliance Analytics** | Google BigQuery | Evidence archival and trend analysis |
| **Evidence Storage** | Google Cloud Storage | 1-year SOC 2 compliant retention |
| **Reporting** | ReportLab + Flask | PDF generation and MR comments |

## Agents

All agents are ready for publication to the GitLab AI Catalog. They are defined in `.gitlab/agents/` and use GitLab's agent YAML format.

### 1. ComplianceBot Scanner
**File**: [.gitlab/agents/compliance-scanner.yaml](.gitlab/agents/compliance-scanner.yaml)

- **Role**: Scans merge requests and pipelines for compliance signals
- **Input**: MR diffs, pipeline results, vulnerability reports
- **Detects**: Auth changes, encryption configs, dependency vulnerabilities, SAST findings
- **Output**: JSON findings with severity, control IDs, remediation steps
- **Tools**: `read_file`, `read_files`, `analyze_file_diff`

### 2. ComplianceBot Mapper
**File**: [.gitlab/agents/compliance-mapper.yaml](.gitlab/agents/compliance-mapper.yaml)

- **Role**: Maps security findings to compliance framework controls
- **Frameworks**: SOC 2, ISO 27001, PCI-DSS, HIPAA
- **Output**: Control mappings, risk assessment, compliance score (0-100)
- **Scoring**: 0-100 scale where 100 = fully audit-ready
- **Tools**: `read_file`, `execute_query`, `log_analysis`

### 3. ComplianceBot Evidence Collector
**File**: [.gitlab/agents/evidence-collector.yaml](.gitlab/agents/evidence-collector.yaml)

- **Role**: Collects and archives audit trail evidence from GitLab activity
- **Collection Window**: Last 14 days (30 days for scheduled audits), max 500 MRs
- **Evidence Type**: MR metadata, approvals, pipeline results, access logs
- **Security**: SHA-256 hashing for non-repudiation
- **Archive**: BigQuery with 1-year SOC 2 compliance retention
- **Tools**: `read_file`, `execute_query`, `archive_data`, `generate_hash`

### 4. ComplianceBot Reporter
**File**: [.gitlab/agents/compliance-reporter.yaml](.gitlab/agents/compliance-reporter.yaml)

- **Role**: Generates audit-ready compliance reports using Vertex AI
- **Narrative**: Uses Gemini-2.5-flash for executive summaries
- **Outputs**: 
  - GitLab issues (for findings with severity >= medium)
  - MR comments (only if score < 85)
  - PDF reports (audit-ready, archived to GCS with 7-day signed URLs)
- **Timeline**: Includes remediation timeline estimates (days to compliance)
- **Tools**: `read_file`, `create_issue`, `post_comment`, `generate_pdf`, `archive_file`

## Flow

The **ComplianceBot Flow** ([.gitlab/flows/compliance-flow.yaml](.gitlab/flows/compliance-flow.yaml)) orchestrates all 4 agents in sequence:

**Architecture**:
```
Scanner → Mapper → Evidence Collector → Reporter
```

**Triggers:**
- ✅ Merge Request (opened or updated)
- ✅ Pipeline (success or failure on main/production branches)
- ✅ Schedule (Every Monday at 2 AM UTC)
- ✅ Manual trigger via Automate → Flows menu

**Flow Components**:
1. **Scanner**: Analyzes MR/pipeline for compliance signals
2. **Mapper**: Maps findings to control IDs (SOC2, ISO27001, PCI-DSS, HIPAA)
3. **Evidence Collector**: Gathers audit evidence (MR approvals, pipeline logs, access records)
4. **Reporter**: Generates compliance report and posts findings

**Outputs**:
- **GitLab Issues**: One per finding (with control ID reference)
- **MR Comments**: Compliance score badge (only if score < 85)
- **CI/CD Artifacts**: PDF reports stored for 90 days
- **BigQuery**: Evidence logged for historical trend analysis

## Documentation

| Guide | Purpose |
|-------|---------|
| [Installation](docs/installation.md) | Project setup and dependencies |
| [Configuration](docs/configuration.md) | Environment variables and GCP setup |
| [Compliance Frameworks](docs/compliance-frameworks.md) | SOC 2, ISO 27001, PCI-DSS, HIPAA details |
| [Publishing Guide](docs/PUBLISHING_GUIDE.md) | **How to publish agents and flows** |
| [Cloud Build Guide](docs/CLOUD_BUILD_GUIDE.md) | **Serverless deployment without Docker** |
| [Agent Behavior](AGENTS.md) | Agent guidelines and custom controls |

## Testing

Run unit tests:
```bash
python -m pytest tests/ -v
```

Test coverage includes:
- MR analysis and finding detection (17 tests)
- Compliance control mapping (23 tests)
- Report generation and PDF formatting (18 tests)
- Evidence collection and BigQuery integration (27+ tests)

## Hackathon Submission

For GitLab AI Hackathon 2026:

1. ✅ Create public agents (all 4 ready)
2. ✅ Create public flow (ready)
3. 📋 Follow [Publishing Guide](docs/PUBLISHING_GUIDE.md) Section 4-5
4. 📹 Record 3-minute demo video
5. 📤 Submit to [gitlab.devpost.com](https://gitlab.devpost.com) before **March 25, 2026 @ 2 PM EDT**

See [Publishing Guide Section 7](docs/PUBLISHING_GUIDE.md#7-hackathon-submission-checklist) for complete submission requirements.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Project Structure

```
.gitlab/
├── agents/                    # 4 custom agents
│   ├── compliance-scanner.yaml
│   ├── compliance-mapper.yaml
│   ├── evidence-collector.yaml
│   └── compliance-reporter.yaml
└── flows/
    └── compliance-flow.yaml   # Multi-agent orchestration

src/
├── agents/                    # Python implementations
│   ├── scanner.py
│   ├── mapper.py
│   ├── evidence_collector.py
│   └── reporter.py
├── frameworks/                # Control definitions
│   ├── soc2_controls.json
│   ├── iso27001_controls.json
│   ├── pci_dss_controls.json
│   └── hipaa_controls.json
├── templates/                 # Report templates
│   ├── compliance_report.md.j2
│   └── mr_comment_badge.md.j2
└── utils/
    ├── gitlab_api.py
    └── evidence_builder.py

cloud/
├── cloud_run/
│   ├── report_generator.py    # Flask service (uses Vertex AI)
│   ├── Dockerfile
│   └── deploy.sh              # Cloud Build deployment
├── terraform/
│   └── main.tf                # GCP infrastructure
└── bigquery_schema.sql        # Evidence table schema

docs/
├── installation.md
├── configuration.md
├── compliance-frameworks.md
├── PUBLISHING_GUIDE.md         # ⭐ START HERE for hackathon
├── CLOUD_BUILD_GUIDE.md        # ⭐ For deployment
└── ...

tests/                         # 67+ unit tests
├── test_scanner.py
├── test_mapper.py
├── test_reporter.py
├── test_evidence.py
└── fixtures/
    └── sample_mr_diff.json
```

## Support

For issues or questions:
1. Check [AGENTS.md](AGENTS.md) for agent behavior guidelines
2. Review [configuration.md](docs/configuration.md) for GCP setup errors
3. See [CLOUD_BUILD_GUIDE.md](docs/CLOUD_BUILD_GUIDE.md) for deployment issues
4. Check test fixtures in `tests/fixtures/` for example MR payloads
