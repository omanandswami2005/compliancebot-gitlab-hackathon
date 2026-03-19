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

All agents are ready for publication to the GitLab AI Catalog:

1. **ComplianceBot Scanner** ([.gitlab/agents/compliance-scanner.yaml](.gitlab/agents/compliance-scanner.yaml))
   - Analyzes MRs and CI/CD pipelines
   - Detects: auth changes, encryption configs, dependency vulnerabilities, SAST findings
   - Maps findings to control IDs

2. **ComplianceBot Mapper** ([.gitlab/agents/compliance-mapper.yaml](.gitlab/agents/compliance-mapper.yaml))
   - Maps security findings to compliance controls
   - Supports: SOC 2, ISO 27001, PCI-DSS, HIPAA
   - Scores compliance readiness (0-100)

3. **ComplianceBot Evidence Collector** ([.gitlab/agents/evidence-collector.yaml](.gitlab/agents/evidence-collector.yaml))
   - Collects audit trails and evidence
   - Features: MR approvals, pipeline results, access logs, SHA-256 hashing
   - Archives to BigQuery with non-repudiation

4. **ComplianceBot Reporter** ([.gitlab/agents/compliance-reporter.yaml](.gitlab/agents/compliance-reporter.yaml))
   - Generates compliance reports using Vertex AI
   - Creates GitLab issues for findings
   - Posts MR comments with compliance badges
   - Generates audit-ready PDFs

## Flow

The **compliance-flow** ([.gitlab/flows/compliance-flow.yaml](.gitlab/flows/compliance-flow.yaml)) orchestrates all 4 agents:

**Triggers:**
- On MR created/updated
- On pipeline success/failure (for main/production branches)
- Weekly schedule (Monday 2 AM)
- Manual trigger via Automate menu

**Output:**
- GitLab issues for each finding
- MR comments with compliance score (only for score < 85)
- CI/CD artifacts with full PDF reports

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
