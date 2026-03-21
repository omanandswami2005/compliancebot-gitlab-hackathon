# 🛡️ ComplianceBot Flow

> **Your compliance auditor lives in GitLab now.**

An AI-powered multi-agent compliance flow built on the GitLab Duo Agent Platform. Automatically scans merge requests for compliance violations, maps findings to SOC 2/ISO 27001/PCI-DSS controls, and generates audit-ready reports.

[![GitLab AI Hackathon 2026](https://img.shields.io/badge/GitLab%20AI%20Hackathon-2026-orange)](https://gitlab.devpost.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Latest Release](https://img.shields.io/badge/release-v1.2.0-green)](https://gitlab.com/gitlab-ai-hackathon/participants/35481656/-/tags)

## 🎯 What It Does

| Before ComplianceBot | After ComplianceBot |
|---------------------|---------------------|
| Manual code review for security issues | Automatic scanning on every MR |
| Spreadsheets tracking compliance controls | Real-time control mapping |
| Weeks of audit evidence gathering | Instant evidence packages |
| 200-400 hours per SOC 2 audit | Minutes per compliance check |

## ✅ Live Demo Results

**Test MR [!10](https://gitlab.com/gitlab-ai-hackathon/participants/35481656/-/merge_requests/10)** with intentional violations:

- **20+ Issues Created** automatically ([#5](https://gitlab.com/gitlab-ai-hackathon/participants/35481656/-/work_items/5) - [#24](https://gitlab.com/gitlab-ai-hackathon/participants/35481656/-/work_items/24))
- **Compliance Score**: 0/100 (intentionally failing)
- **Findings**: 4 Critical, 10 High, 10 Medium severity
- **Controls Mapped**: SOC2-CC6.1, ISO27001-A.10.1.1, PCI-DSS-3.5.3, etc.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   GitLab Duo Agent Platform                      │
│                                                                  │
│  Trigger: @mention, assign, or assign reviewer on MR            │
│                         │                                        │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                 ComplianceBot Flow                          ││
│  │                                                             ││
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ ││
│  │  │ Scanner  │──▶│  Mapper  │──▶│ Evidence │──▶│ Reporter │ ││
│  │  │  Agent   │   │  Agent   │   │ Collector│   │  Agent   │ ││
│  │  └──────────┘   └──────────┘   └──────────┘   └──────────┘ ││
│  │       │              │              │              │        ││
│  │  Read MR diffs  Map to SOC2   Gather audit    Post MR      ││
│  │  Find issues    ISO27001      evidence        comment      ││
│  │                 PCI-DSS                       Create       ││
│  │                 HIPAA                         issues       ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼ (Optional GCP Integration)
              ┌────────────────────────────────────┐
              │         Google Cloud Platform       │
              │                                     │
              │  BigQuery ─── Compliance Analytics  │
              │  Cloud Storage ─── PDF Reports      │
              │  Vertex AI ─── AI Narratives        │
              └────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Trigger the Flow

On any merge request, mention the flow:
```
@ai-compliance-bot-flow-gitlab-ai-hackathon Please analyze this MR for compliance issues.
```

Or assign the flow as a reviewer.

### 2. View Results

- **MR Comment**: Compliance score badge with findings table
- **Issues**: Auto-created for each finding (severity >= medium)
- **Session Log**: Automate → Sessions → View agent reasoning

## 📊 What Gets Detected

| Category | Examples | Severity |
|----------|----------|----------|
| **Secrets** | API keys, passwords, private keys in code | Critical |
| **Encryption** | MD5/SHA1 hashing, disabled SSL, weak ciphers | Critical/High |
| **Authentication** | SQL injection, weak sessions, no MFA | High |
| **Dependencies** | Known CVEs in packages | High |
| **Configuration** | Debug mode, permissive CORS, weak passwords | Medium |
| **Process** | Missing change tickets, no DBA approval | Medium |

## 🎯 Compliance Frameworks

| Framework | Controls Covered |
|-----------|-----------------|
| **SOC 2** | CC6.1-CC6.8 (Access), CC7.1-CC7.5 (Operations), CC8.1 (Change Mgmt) |
| **ISO 27001** | A.8 (Asset Mgmt), A.9 (Access), A.10 (Crypto), A.12 (Operations) |
| **PCI-DSS** | Req 6 (Secure Dev), Req 8 (Auth), Req 10 (Logging) |
| **HIPAA** | §164.312 Technical Safeguards |
| **Custom** | ORG-001 (Change Tickets), ORG-002 (DBA Approval), ORG-003 (CVE Patching) |

## 📁 Project Structure

```
compliancebot/
├── agents/                     # Agent YAML definitions
│   ├── compliance-scanner.yml  # Scans MRs for issues
│   ├── compliance-mapper.yml   # Maps to compliance controls
│   ├── evidence-collector.yml  # Gathers audit evidence
│   └── compliance-reporter.yml # Posts reports & creates issues
│
├── flows/
│   └── compliance-flow.yml     # Multi-agent orchestration
│
├── src/
│   ├── agents/                 # Python implementations
│   ├── frameworks/             # Control definitions (JSON)
│   ├── gcp/                    # GCP integration module
│   │   ├── client.py           # Authentication & config
│   │   ├── bigquery.py         # Findings analytics
│   │   ├── storage.py          # PDF/evidence archival
│   │   ├── vertex_ai.py        # AI narrative generation
│   │   └── integration.py      # Main orchestrator
│   ├── templates/              # Report templates
│   └── utils/                  # Helpers
│
├── cloud/
│   ├── cloud_run/              # Report generator service
│   ├── terraform/              # GCP infrastructure
│   └── bigquery_schema.sql     # Analytics tables
│
├── scripts/
│   ├── gcp_setup.sh            # Automated GCP setup
│   └── diagnostic.sh           # Troubleshooting
│
├── tests/                      # Unit tests
├── docs/                       # Documentation
└── skills/                     # Duo skills (slash commands)
```

## ☁️ GCP Integration (Optional)

GCP integration provides additional features but is **not required** for the main flow to work.

| Service | Purpose | Required? |
|---------|---------|-----------|
| **Vertex AI** | AI-powered compliance narratives | Optional |
| **BigQuery** | Historical analytics & trends | Optional |
| **Cloud Storage** | PDF reports with 1-year retention | Optional |

### Setup GCP (One Command)

```bash
# Requires: gcloud CLI installed and authenticated
./scripts/gcp_setup.sh

# Or with existing project
./scripts/gcp_setup.sh your-project-id
```

The script will:
1. Create/configure GCP project
2. Enable required APIs
3. Create service account with permissions
4. Set up BigQuery dataset and tables
5. Create GCS bucket with retention policy
6. Output credentials for GitLab CI/CD

### Add to GitLab CI/CD Variables

**Location**: Settings → CI/CD → Variables

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `GCP_PROJECT_ID` | Your GCP project ID | No | No |
| `GCP_SERVICE_ACCOUNT_KEY` | Base64-encoded key | Yes | Yes |
| `BIGQUERY_DATASET` | `compliance` | No | No |
| `GCS_BUCKET` | `compliance-evidence-{project}` | No | No |

### Graceful Degradation

If GCP is not configured:
- ✅ Flow still scans MRs
- ✅ Issues still created
- ✅ MR comments still posted
- ⚠️ BigQuery logging skipped (with warning)
- ⚠️ PDF archival skipped (with warning)
- ⚠️ Fallback narrative (no AI enhancement)

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [GCP Setup Guide](docs/GCP_SETUP.md) | Complete GCP configuration |
| [Configuration](docs/configuration.md) | Environment variables |
| [Publishing Guide](docs/PUBLISHING_GUIDE.md) | How to publish to AI Catalog |
| [Official Tools](docs/OFFICIAL_TOOLS_REFERENCE.md) | Available GitLab tools |
| [AGENTS.md](AGENTS.md) | Agent behavior guidelines |

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Test GCP integration (requires credentials)
python -m src.gcp.cli status
```

## 🏆 Hackathon Submission

**GitLab AI Hackathon 2026** - Deadline: March 25, 2026 @ 2:00 PM EDT

### Checklist

- [x] Public GitLab repo in hackathon group
- [x] 4 custom agents published to AI Catalog
- [x] 1 multi-agent flow published
- [x] MIT License
- [x] Working demo (MR !10)
- [ ] 3-minute demo video
- [ ] Submit to [gitlab.devpost.com](https://gitlab.devpost.com)

### Prize Targets

| Prize | Amount | Status |
|-------|--------|--------|
| Grand Prize | $15,000 | 🎯 Target |
| Most Impactful | $5,000 | 🎯 Target |
| Google Cloud Bonus | $10,000 | ✅ GCP integrated |
| Anthropic Bonus | $10,000 | ✅ Claude via Duo |

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- GitLab Duo Agent Platform team
- Google Cloud for Vertex AI
- Anthropic Claude (via GitLab)

---

**Built for GitLab AI Hackathon 2026** | [View on GitLab](https://gitlab.com/gitlab-ai-hackathon/participants/35481656)
