# ComplianceBot Flow — Complete Research & Development Guide
> GitLab AI Hackathon 2026 | You Orchestrate. AI Accelerates.
> **Deadline: March 25, 2026 @ 2:00 PM EDT**

---

## Table of Contents

1. [Hackathon Overview & Requirements](#1-hackathon-overview--requirements)
2. [Project Vision: ComplianceBot Flow](#2-project-vision-compliancebot-flow)
3. [Architecture & System Design](#3-architecture--system-design)
4. [GitLab Duo Agent Platform — Deep Dive](#4-gitlab-duo-agent-platform--deep-dive)
5. [Agent Design: Custom Agents](#5-agent-design-custom-agents)
6. [Flow Design: Multi-Agent Orchestration](#6-flow-design-multi-agent-orchestration)
7. [Anthropic Claude Integration (Bonus Prize)](#7-anthropic-claude-integration-bonus-prize)
8. [Google Cloud Integration (Bonus Prize)](#8-google-cloud-integration-bonus-prize)
9. [Code Examples & Implementation](#9-code-examples--implementation)
10. [AGENTS.md & SKILL.md Configuration](#10-agentsmd--skillmd-configuration)
11. [CI/CD Pipeline Setup](#11-cicd-pipeline-setup)
12. [Compliance Frameworks Covered](#12-compliance-frameworks-covered)
13. [Features & Innovations](#13-features--innovations)
14. [Demo Video Strategy](#14-demo-video-strategy)
15. [Submission Requirements Checklist](#15-submission-requirements-checklist)
16. [Resources & References](#16-resources--references)

---

## 1. Hackathon Overview & Requirements

### Key Facts
| Field | Detail |
|---|---|
| **Event** | GitLab AI Hackathon: You Orchestrate. AI Accelerates. |
| **Platform** | [gitlab.devpost.com](https://gitlab.devpost.com) |
| **Deadline** | March 25, 2026 @ 2:00 PM EDT |
| **Participants** | 4,913+ registered |
| **Prize Pool** | $65,000 total |
| **Our Target Prizes** | Grand Prize ($15K) + Anthropic Bonus ($10K) + Google Cloud Bonus ($10K) |

### Prize Breakdown Relevant to Us
| Prize | Amount | Requirement |
|---|---|---|
| Grand Prize | $15,000 | Best overall project |
| Most Impactful | $5,000 | Real-world SDLC impact |
| Most Technically Impressive | $5,000 | Platform depth |
| GitLab + Anthropic Grand Prize | $10,000 | Use Claude through GitLab |
| GitLab + Anthropic Runner Up | $3,500 | Use Claude through GitLab |
| GitLab + Google Grand Prize | $10,000 | Use Google Cloud + GitLab |
| Honorable Mention | $500 each | 6 winners |

### Hard Requirements
- ✅ **Public GitLab repo** in the [GitLab AI Hackathon group](https://gitlab.com/gitlab-ai-hackathon)
- ✅ **At least one custom public agent OR public flow** created using GitLab Duo Agent Platform
- ✅ **Open source license** visible at top of repo (MIT recommended)
- ✅ **Text description** of features and functionality
- ✅ **Demo video ≤ 3 minutes** on YouTube or Vimeo (public)
- ✅ **Functional source code** with all assets and instructions

### Judging Criteria (weighted equally)
1. **Technological Implementation** — Quality code + real use of GitLab Duo Agent Platform (Tools, Triggers, Context)
2. **Design & Usability** — Easy to install, configure, and interact with
3. **Potential Impact** — Solves a real "AI Paradox" bottleneck (planning, security, operations)
4. **Quality of the Idea** — Creative, unique, doesn't already exist or significantly improves on it

### What Disqualifies
- Pure chatbot — must be an agent that **reacts to triggers and takes action**
- Private repository
- Missing demo video
- No source code in GitLab AI Hackathon group

---

## 2. Project Vision: ComplianceBot Flow

### The Problem (The Pain)
Enterprise engineering teams face a crushing compliance burden:
- **SOC 2 Type II**, **ISO 27001**, **PCI-DSS**, **HIPAA**, **GDPR** audits require months of manual evidence collection
- Auditors demand proof from Git history, CI/CD pipelines, access logs, vulnerability scans, and more
- A typical SOC 2 audit takes **200–400 engineer-hours** just for evidence gathering
- After each sprint, developers merge code without knowing if it violates a compliance control
- Security findings go stale and unaddressed, creating audit gaps

### The Solution (ComplianceBot Flow)
An **AI-powered multi-agent compliance flow** built on the GitLab Duo Agent Platform that:
1. **Monitors** every merge request, pipeline run, and security scan in real-time
2. **Maps** findings to compliance controls (SOC 2 CC6, ISO 27001 A.12, PCI DSS 6.3, etc.)
3. **Generates** audit-ready evidence packages automatically
4. **Alerts** teams to compliance drift before audits
5. **Produces** human-readable compliance reports as GitLab issues + downloadable PDFs

### Tagline
> *"Your compliance auditor lives in GitLab now."*

### Value Proposition
- Cuts SOC 2 evidence gathering from **weeks to minutes**
- Zero new tooling — lives entirely inside GitLab
- Works retroactively on existing repositories
- Produces reports auditors actually accept

---

## 3. Architecture & System Design

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
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │              Outputs                        │    │
│  │  • GitLab Issue (compliance report)         │    │
│  │  • MR Comment (per-PR compliance score)     │    │
│  │  • Downloadable PDF evidence package        │    │
│  │  • GitLab Dashboard widget                  │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
  ┌─────────────┐          ┌────────────────┐
  │  Anthropic  │          │  Google Cloud  │
  │  Claude API │          │  (Storage/NLP) │
  │  (via GitLab│          │  BigQuery      │
  │   Gateway)  │          │  Cloud Run     │
  └─────────────┘          └────────────────┘
```

### Data Flow
1. **Trigger fires** → Flow starts in GitLab CI/CD
2. **Scanner Agent** reads MR diff, pipeline results, vulnerability scan data, commit history
3. **Mapper Agent** maps findings to specific compliance controls using AI
4. **Evidence Agent** collects supporting artifacts (logs, screenshots, audit trails)
5. **Reporter Agent** synthesizes everything into a structured report
6. Report is posted as a **GitLab Issue** and optionally as a **MR comment**

---

## 4. GitLab Duo Agent Platform — Deep Dive

### Platform Overview
The GitLab Duo Agent Platform (GA since January 15, 2026, GitLab 18.8+) is an AI-native solution embedding multiple agents throughout the software development lifecycle. It addresses the "AI Paradox" — AI speeds up coding, but planning, security, and compliance remain manual bottlenecks costing teams ~7 hours/person/week.

### Three Agent Types
| Type | Description | Our Usage |
|---|---|---|
| **Foundational** | Pre-built by GitLab (Planner, Security Analyst, Data Analyst) | Use Security Analyst as input |
| **Custom** | Built by your org via AI Catalog | Our 4 custom agents |
| **External** | Third-party AI (Claude Code, Codex CLI) | Claude Code for deep analysis |

### Key Platform Features
- **AI Catalog** — Central hub to publish, discover, and enable agents/flows
- **Flows** — Multi-agent orchestration running in GitLab CI/CD
- **Agentic Chat** — Natural language interface with full SDLC context
- **MCP Client** (GA) — Connect to external tools (Jira, Slack, Confluence)
- **AGENTS.md** — Customize flow behavior per-project
- **SKILL.md** — Define agent skills as slash commands
- **Sessions** — Full audit trail of agent actions (Automate > Sessions)
- **Knowledge Graph** — Structured code relationship understanding
- **GitLab Credits** — Usage-based billing (pooled org-wide)

### LLM Used by Flows
Flows use **Anthropic Claude Sonnet 4** as the underlying model — directly relevant to the Anthropic bonus prize.

### Platform Prerequisites
```
- GitLab version 18.8 or later (for GA)
- GitLab Duo Pro or Enterprise subscription (or Duo Core for free tier)
- Agent Platform turned on in GitLab Duo settings
- Developer, Maintainer, or Owner role
- Push rules configured for service account (for flows that create code)
- GitLab hosted runners OR self-configured runners
```

---

## 5. Agent Design: Custom Agents

### Agent 1: ComplianceScanner Agent

**Purpose:** Analyze a merge request or pipeline and extract compliance-relevant signals.

**Inputs:**
- MR diff and description
- Pipeline job results and logs
- GitLab vulnerability scan results (SAST, DAST, dependency scanning)
- Commit messages and author information

**System Prompt Design:**
```
You are a compliance scanner for software engineering teams.
Your job is to analyze a GitLab merge request and identify:
1. Code changes that affect security controls (authentication, encryption, data handling)
2. Dependency changes that introduce known CVEs
3. Infrastructure changes that affect network security
4. Missing or altered security tests
5. Access control changes (RBAC, permission scope changes)

For each finding, output structured JSON with:
- control_id: The compliance control this maps to (e.g., SOC2-CC6.1)
- severity: critical | high | medium | low | informational
- description: Plain English description
- evidence_type: code_change | config_change | test_coverage | dependency
- file_path: The affected file
- remediation: Suggested fix

Output only valid JSON. No preamble.
```

**Triggers:**
- Merge Request opened or updated
- Pipeline completion (on main/production branches)

**Agent YAML Skeleton:**
```yaml
name: compliance-scanner
description: >
  Scans GitLab merge requests and pipelines for compliance signals.
  Maps findings to SOC 2, ISO 27001, PCI-DSS, and HIPAA controls.
visibility: public
type: custom
model: claude-sonnet-4
context:
  - merge_request_diff
  - pipeline_results
  - vulnerability_report
  - commit_history
output_format: json
```

---

### Agent 2: ComplianceMapper Agent

**Purpose:** Map raw scanner findings to specific compliance framework controls.

**Compliance Frameworks Supported:**
- SOC 2 Type II (Trust Service Criteria)
- ISO 27001:2022 (Annex A controls)
- PCI-DSS v4.0 (Requirements 6, 8, 10, 12)
- HIPAA (Technical Safeguards §164.312)
- GDPR (Article 25, 32)

**Mapping Logic (simplified):**
```python
CONTROL_MAPPINGS = {
    "authentication_change": [
        "SOC2-CC6.1",    # Logical access controls
        "ISO27001-A.9.4.2",  # Secure log-on procedures
        "PCI-DSS-8.2",   # User identification and authentication
    ],
    "encryption_change": [
        "SOC2-CC6.7",    # Transmission of data encryption
        "ISO27001-A.10.1.1",  # Policy on use of cryptographic controls
        "PCI-DSS-4.1",   # Protect cardholder data during transmission
    ],
    "dependency_vulnerability": [
        "SOC2-CC7.1",    # Vulnerability detection
        "ISO27001-A.12.6.1",  # Management of technical vulnerabilities
        "PCI-DSS-6.3.3", # Patch management
    ],
    "access_control_change": [
        "SOC2-CC6.3",    # Access removal
        "ISO27001-A.9.2.6",  # Removal or adjustment of access rights
        "PCI-DSS-7.2",   # Access control systems
    ],
}
```

**Agent Prompt:**
```
You are a compliance control mapper. Given a list of security findings from a code review,
map each finding to the most relevant compliance controls across SOC 2, ISO 27001, PCI-DSS, and HIPAA.

For each mapping:
1. Identify the primary framework and control ID
2. Identify secondary applicable controls
3. Assign a compliance impact score (1-10)
4. Determine if this is a PASS, FAIL, or NEEDS_REVIEW status
5. Provide a one-line explanation suitable for an auditor

Return structured JSON matching the ComplianceMapping schema.
```

---

### Agent 3: EvidenceCollector Agent

**Purpose:** Gather and package audit evidence from GitLab activity.

**Evidence Sources:**
- Git commit history with author attribution
- CI/CD pipeline execution logs
- Merge request approval records
- Access control logs (who merged, who approved)
- Vulnerability scan results with timestamps
- Deployment records
- SAST/DAST scan reports

**Key Innovation:** Evidence is **timestamped, immutable, and cryptographically linked** to GitLab's internal audit trail — so it satisfies auditor requirements for non-repudiation.

**Evidence Package Structure:**
```json
{
  "evidence_package": {
    "generated_at": "2026-03-18T10:30:00Z",
    "project": "myorg/myapp",
    "period": "2026-01-01 to 2026-03-18",
    "controls": {
      "SOC2-CC6.1": {
        "status": "PASS",
        "evidence": [
          {
            "type": "mr_approval",
            "description": "All MRs required 2 approvals before merge",
            "source_url": "https://gitlab.com/myorg/myapp/-/merge_requests/142",
            "timestamp": "2026-03-10T14:22:00Z",
            "approvers": ["alice@company.com", "bob@company.com"]
          }
        ]
      }
    }
  }
}
```

---

### Agent 4: ComplianceReporter Agent

**Purpose:** Generate human-readable compliance reports from structured evidence.

**Output Formats:**
- GitLab Issue (primary — auto-created)
- Markdown report (in repo)
- PDF evidence package (via CI artifact)
- MR comment with compliance score badge

**Report Structure:**
```markdown
# 🔒 Compliance Report — Sprint 42
**Generated:** 2026-03-18 | **Project:** myorg/myapp | **Score:** 87/100

## Executive Summary
This sprint introduced 2 high-severity compliance findings and 1 critical item
requiring immediate attention before the next SOC 2 audit window.

## Control Status Overview
| Control | Framework | Status | Severity |
|---|---|---|---|
| CC6.1 - Logical Access | SOC 2 | ✅ PASS | — |
| CC7.1 - Vulnerability Mgmt | SOC 2 | ⚠️ NEEDS REVIEW | Medium |
| A.12.6.1 - Patch Mgmt | ISO 27001 | ❌ FAIL | High |

## Findings
### CRITICAL: Unpatched Dependency (lodash 4.17.20)
**Control:** SOC2-CC7.1, ISO27001-A.12.6.1
**MR:** !142 — Added lodash 4.17.20 (CVE-2021-23337)
**Remediation:** Upgrade to lodash 4.17.21 or later

## Evidence Package
All supporting artifacts are attached as CI artifacts.
Download: [compliance-evidence-sprint42.zip](...)
```

---

## 6. Flow Design: Multi-Agent Orchestration

### Flow YAML Configuration

```yaml
# .gitlab/flows/compliance-flow.yaml
name: compliance-bot-flow
description: >
  Multi-agent compliance analysis flow. Scans MRs and pipelines,
  maps findings to compliance controls, collects evidence, and
  generates audit-ready reports.
version: "1.0"
visibility: public

triggers:
  - type: merge_request
    events:
      - opened
      - updated
  - type: pipeline
    events:
      - success
      - failed
    branches:
      - main
      - production
  - type: schedule
    cron: "0 2 * * 1"  # Every Monday at 2 AM — weekly compliance digest

components:
  - name: scanner
    type: AgentComponent
    agent: compliance-scanner
    inputs:
      - from: "context:merge_request"
        as: "mr_context"
      - from: "context:pipeline"
        as: "pipeline_context"
      - from: "context:vulnerability_report"
        as: "vuln_report"

  - name: mapper
    type: AgentComponent
    agent: compliance-mapper
    depends_on: [scanner]
    inputs:
      - from: "steps.scanner.output"
        as: "findings"
      - from: "context:compliance_config"
        as: "frameworks"

  - name: evidence
    type: AgentComponent
    agent: evidence-collector
    depends_on: [mapper]
    inputs:
      - from: "steps.mapper.output"
        as: "mapped_controls"
      - from: "context:project"
        as: "project_info"

  - name: reporter
    type: AgentComponent
    agent: compliance-reporter
    depends_on: [evidence]
    inputs:
      - from: "steps.evidence.output"
        as: "evidence_package"
      - from: "context:workspace_agent_skills"
        as: "workspace_agent_skills"
        optional: true

outputs:
  - type: gitlab_issue
    title: "🔒 Compliance Report — {{ trigger.ref }}"
    labels: ["compliance", "automated"]
  - type: mr_comment
    condition: "trigger.type == 'merge_request'"
    template: "compliance_score_badge"
  - type: ci_artifact
    path: "compliance-report.pdf"
    expire_in: "90 days"
```

### Flow Execution in CI/CD

The flow runs as a GitLab CI/CD job, giving it access to:
- GitLab API (via `AI_FLOW_GITLAB_TOKEN`)
- Repository content
- Pipeline artifacts
- Vulnerability reports

```yaml
# .gitlab-ci.yml (auto-generated by platform, shown for reference)
compliance-bot:
  stage: compliance
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
  variables:
    COMPLIANCE_FRAMEWORKS: "soc2,iso27001,pci-dss"
    REPORT_FORMAT: "issue,pdf,mr-comment"
  trigger:
    include: .gitlab/flows/compliance-flow.yaml
```

---

## 7. Anthropic Claude Integration (Bonus Prize)

### Why This Wins the $10K Anthropic Prize
The Anthropic bonus specifically requires **running Anthropic through GitLab** (not direct API calls). Our flow uses Claude Sonnet 4 natively through the GitLab Duo Agent Platform gateway — exactly what the prize targets.

### Claude's Role in ComplianceBot

#### 1. Deep Semantic Analysis
Claude understands *why* code changes are compliance risks, not just pattern-matching keywords. Example:

```
Input: A code diff that changes JWT token expiry from 7 days to 30 days

Claude's Analysis:
"This change extends session lifetime from 7 to 30 days.
This conflicts with:
- SOC2 CC6.1: Session management controls
- PCI-DSS 8.1.8: Re-authenticate after 15-minute idle
- NIST SP 800-63B: Session time-bound requirements

Severity: HIGH
Remediation: Revert to ≤24h expiry or implement sliding window with activity-based extension"
```

#### 2. Natural Language Evidence Summaries
Claude converts raw log data into auditor-friendly prose:

```
Raw: pipeline_job{id: 5821, status: "success", duration: 142, stage: "security-scan", 
     artifacts: ["gl-sast-report.json"]}

Claude Output: "Security scanning pipeline ran successfully on March 10, 2026 at 14:22 UTC,
completing in 2 minutes 22 seconds. SAST analysis produced no new critical findings.
Full report attached as audit artifact #5821."
```

#### 3. Risk Scoring with Reasoning
```python
# How Claude is called via GitLab's AI Gateway
# (flows use Claude Sonnet 4 natively — no direct API key needed)

CLAUDE_RISK_PROMPT = """
You are a compliance risk analyst. Given the following evidence package,
produce a compliance risk score from 0-100 where:
- 90-100: Audit-ready, no significant gaps
- 70-89: Minor gaps, addressable within 30 days
- 50-69: Moderate gaps, requires sprint-level effort
- 0-49: Critical gaps, audit would fail

Provide:
1. Overall score
2. Score per framework
3. Top 3 risk items
4. 30-day remediation roadmap

Evidence: {evidence_json}
"""
```

#### 4. External Agent Configuration (Claude Code)
For deeper repository analysis, the Claude Code external agent can be triggered:

```yaml
# External agent config for Claude Code
name: compliance-deep-analyzer
type: external
injectGatewayToken: true
image: node:22-slim
commands:
  - npm install -g @anthropic-ai/claude-code
  - |
    claude --prompt "Analyze this repository for compliance gaps across
    SOC 2, ISO 27001, and PCI-DSS. Focus on:
    1. Authentication and session management patterns
    2. Data encryption at rest and in transit
    3. Logging and audit trail completeness
    4. Dependency vulnerability exposure
    
    Repository context: $AI_FLOW_CONTEXT
    
    Output a structured compliance gap report as JSON."
```

---

## 8. Google Cloud Integration (Bonus Prize)

### Why This Wins the $10K Google Cloud Prize

#### Integration Points

**1. BigQuery — Compliance Trend Analytics**
Store compliance scores over time for trend analysis:

```sql
-- Schema for compliance_findings table in BigQuery
CREATE TABLE compliance_findings (
  project_id STRING,
  pipeline_id INT64,
  mr_id INT64,
  control_id STRING,
  framework STRING,
  status STRING,  -- PASS | FAIL | NEEDS_REVIEW
  severity STRING,
  finding_date TIMESTAMP,
  remediated_date TIMESTAMP,
  score INT64
);

-- Query: Compliance trend over last 90 days
SELECT
  DATE(finding_date) as date,
  framework,
  AVG(score) as avg_score,
  COUNTIF(status = 'FAIL') as failures
FROM compliance_findings
WHERE project_id = @project_id
  AND finding_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY date, framework
ORDER BY date DESC;
```

**2. Cloud Run — Report Generation Service**
A serverless microservice that generates PDF evidence packages:

```python
# cloud_run/report_generator.py
from flask import Flask, request, jsonify
from google.cloud import storage
import anthropic
import json

app = Flask(__name__)

@app.route('/generate-report', methods=['POST'])
def generate_report():
    evidence = request.json['evidence_package']
    project_id = request.json['project_id']
    
    # Use Vertex AI / Anthropic to enhance report narrative
    client = anthropic.Anthropic()
    
    narrative = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"Generate an executive compliance narrative for auditors: {json.dumps(evidence)}"
        }]
    )
    
    # Generate PDF and upload to GCS
    pdf_bytes = generate_pdf(evidence, narrative.content[0].text)
    
    bucket = storage.Client().bucket('compliance-reports')
    blob = bucket.blob(f"{project_id}/report-{evidence['period']}.pdf")
    blob.upload_from_string(pdf_bytes, content_type='application/pdf')
    
    return jsonify({"report_url": blob.public_url})
```

**3. Cloud Storage — Evidence Archive**
```yaml
# Terraform config for GCS compliance evidence bucket
resource "google_storage_bucket" "compliance_evidence" {
  name     = "compliance-evidence-${var.project_id}"
  location = "US"
  
  retention_policy {
    retention_period = 31536000  # 1 year (SOC 2 requirement)
  }
  
  versioning {
    enabled = true  # Immutable evidence trail
  }
  
  lifecycle_rule {
    action { type = "SetStorageClass" storage_class = "NEARLINE" }
    condition { age = 90 }  # Move to cheaper storage after 90 days
  }
}
```

**4. Vertex AI — Enhanced NLP**
For organizations that prefer Google's models, route through Vertex AI:

```python
from vertexai.generative_models import GenerativeModel

model = GenerativeModel("gemini-1.5-pro")
response = model.generate_content(
    f"Map these security findings to compliance controls: {findings_json}",
    generation_config={"response_mime_type": "application/json"}
)
```

---

## 9. Code Examples & Implementation

### Project Structure
```
compliance-bot-flow/
├── README.md
├── LICENSE                    # MIT License
├── AGENTS.md                  # GitLab Duo agent instructions
├── .gitlab/
│   ├── flows/
│   │   └── compliance-flow.yaml     # Main flow definition
│   └── agents/
│       ├── compliance-scanner.yaml
│       ├── compliance-mapper.yaml
│       ├── evidence-collector.yaml
│       └── compliance-reporter.yaml
├── skills/
│   ├── compliance-scan/
│   │   └── SKILL.md
│   └── report-generator/
│       └── SKILL.md
├── src/
│   ├── agents/
│   │   ├── scanner.py
│   │   ├── mapper.py
│   │   ├── evidence_collector.py
│   │   └── reporter.py
│   ├── frameworks/
│   │   ├── soc2_controls.json
│   │   ├── iso27001_controls.json
│   │   ├── pci_dss_controls.json
│   │   └── hipaa_controls.json
│   ├── templates/
│   │   ├── compliance_report.md.j2
│   │   └── mr_comment_badge.md.j2
│   └── utils/
│       ├── gitlab_api.py
│       ├── evidence_builder.py
│       └── pdf_generator.py
├── cloud/
│   ├── bigquery_schema.sql
│   ├── cloud_run/
│   │   └── report_generator.py
│   └── terraform/
│       └── main.tf
├── tests/
│   ├── test_scanner.py
│   ├── test_mapper.py
│   └── fixtures/
│       └── sample_mr_diff.json
└── docs/
    ├── installation.md
    ├── configuration.md
    └── compliance-frameworks.md
```

### Core Scanner Implementation

```python
# src/agents/scanner.py
import os
import json
import gitlab
from dataclasses import dataclass
from typing import List

@dataclass
class ComplianceFinding:
    control_id: str
    severity: str  # critical | high | medium | low
    description: str
    evidence_type: str
    file_path: str
    remediation: str
    framework: str

class ComplianceScanner:
    def __init__(self, gitlab_token: str, project_id: str):
        self.gl = gitlab.Gitlab(
            os.environ.get('CI_SERVER_URL', 'https://gitlab.com'),
            private_token=gitlab_token
        )
        self.project = self.gl.projects.get(project_id)
    
    def scan_merge_request(self, mr_iid: int) -> List[ComplianceFinding]:
        mr = self.project.mergerequests.get(mr_iid)
        diff = mr.diffs.list()
        findings = []
        
        for change in diff:
            # Check for authentication changes
            if any(keyword in change.get('diff', '') for keyword in 
                   ['jwt', 'session', 'token_expiry', 'password', 'auth']):
                findings.extend(self._analyze_auth_change(change))
            
            # Check for dependency changes
            if change.get('new_path') in ['package.json', 'requirements.txt', 'Gemfile.lock']:
                findings.extend(self._analyze_dependency_change(change))
            
            # Check for encryption changes  
            if any(keyword in change.get('diff', '') for keyword in
                   ['encrypt', 'ssl', 'tls', 'certificate', 'cipher']):
                findings.extend(self._analyze_encryption_change(change))
        
        # Pull vulnerability scan results
        findings.extend(self._pull_sast_findings(mr))
        
        return findings
    
    def _analyze_auth_change(self, change: dict) -> List[ComplianceFinding]:
        """Analyze authentication-related code changes."""
        return [ComplianceFinding(
            control_id="SOC2-CC6.1",
            severity="high",
            description=f"Authentication logic modified in {change.get('new_path')}",
            evidence_type="code_change",
            file_path=change.get('new_path', ''),
            remediation="Review with security team. Ensure change complies with auth policy.",
            framework="SOC2"
        )]
    
    def _pull_sast_findings(self, mr) -> List[ComplianceFinding]:
        """Pull SAST/dependency scan findings from CI artifacts."""
        findings = []
        pipelines = mr.pipelines.list()
        
        for pipeline in pipelines[:1]:  # Latest pipeline
            try:
                jobs = self.project.pipelines.get(pipeline.id).jobs.list()
                for job in jobs:
                    if 'sast' in job.name.lower() or 'dependency' in job.name.lower():
                        # Parse GL security report artifact
                        artifacts = job.artifacts()
                        report = json.loads(artifacts.get('gl-sast-report.json', '{}'))
                        
                        for vuln in report.get('vulnerabilities', []):
                            if vuln.get('severity') in ['Critical', 'High']:
                                findings.append(ComplianceFinding(
                                    control_id="SOC2-CC7.1",
                                    severity=vuln['severity'].lower(),
                                    description=vuln.get('message', ''),
                                    evidence_type="sast_finding",
                                    file_path=vuln.get('location', {}).get('file', ''),
                                    remediation=vuln.get('solution', 'Remediate identified vulnerability'),
                                    framework="SOC2"
                                ))
            except Exception:
                pass
        
        return findings
```

### Evidence Builder

```python
# src/utils/evidence_builder.py
from datetime import datetime, timezone
import hashlib
import json

class EvidenceBuilder:
    def __init__(self, project, period_start: str, period_end: str):
        self.project = project
        self.period_start = period_start
        self.period_end = period_end
        self.evidence = {}
    
    def collect_mr_approvals(self) -> dict:
        """Collect evidence that MRs required proper approvals."""
        mrs = self.project.mergerequests.list(
            state='merged',
            updated_after=self.period_start,
            updated_before=self.period_end,
            all=True
        )
        
        approval_evidence = []
        for mr in mrs:
            approvals = mr.approvals.get()
            approval_evidence.append({
                "mr_id": mr.iid,
                "title": mr.title,
                "merged_by": mr.merged_by.get('name') if mr.merged_by else None,
                "merged_at": mr.merged_at,
                "approver_count": approvals.approvals_left == 0,
                "approvers": [a['user']['name'] for a in approvals.approved_by],
                "source_url": mr.web_url
            })
        
        return {
            "control": "SOC2-CC6.1",
            "description": "Merge request approval records",
            "count": len(approval_evidence),
            "records": approval_evidence,
            "hash": self._hash_evidence(approval_evidence)
        }
    
    def collect_pipeline_security_scans(self) -> dict:
        """Collect evidence that security scanning ran consistently."""
        pipelines = self.project.pipelines.list(
            ref='main',
            updated_after=self.period_start,
            all=True
        )
        
        scan_records = []
        for pipeline in pipelines:
            jobs = pipeline.jobs.list()
            security_jobs = [j for j in jobs if any(
                kw in j.name.lower() for kw in ['sast', 'dast', 'dependency', 'secret']
            )]
            
            scan_records.append({
                "pipeline_id": pipeline.id,
                "created_at": pipeline.created_at,
                "status": pipeline.status,
                "security_jobs": [{"name": j.name, "status": j.status} for j in security_jobs],
                "all_security_passed": all(j.status == 'success' for j in security_jobs)
            })
        
        pass_rate = sum(1 for r in scan_records if r['all_security_passed']) / max(len(scan_records), 1)
        
        return {
            "control": "SOC2-CC7.1",
            "description": "Security scanning pipeline execution records",
            "scan_pass_rate": f"{pass_rate:.0%}",
            "total_pipelines": len(scan_records),
            "records": scan_records,
            "hash": self._hash_evidence(scan_records)
        }
    
    def _hash_evidence(self, data) -> str:
        """Create a SHA-256 hash of evidence for non-repudiation."""
        return hashlib.sha256(
            json.dumps(data, sort_keys=True, default=str).encode()
        ).hexdigest()
    
    def build_package(self) -> dict:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project": self.project.path_with_namespace,
            "period": f"{self.period_start} to {self.period_end}",
            "generator": "ComplianceBot Flow v1.0",
            "evidence": {
                "mr_approvals": self.collect_mr_approvals(),
                "security_scans": self.collect_pipeline_security_scans(),
            }
        }
```

### GitLab API Helper

```python
# src/utils/gitlab_api.py
import os
import gitlab

def get_gitlab_client() -> gitlab.Gitlab:
    """Get authenticated GitLab client from CI environment."""
    return gitlab.Gitlab(
        os.environ['CI_SERVER_URL'],
        private_token=os.environ.get('AI_FLOW_GITLAB_TOKEN') or 
                      os.environ.get('GITLAB_TOKEN')
    )

def post_compliance_comment(project_id: str, mr_iid: int, score: int, findings_count: int):
    """Post a compliance score badge as an MR comment."""
    gl = get_gitlab_client()
    project = gl.projects.get(project_id)
    mr = project.mergerequests.get(mr_iid)
    
    color = "brightgreen" if score >= 85 else "yellow" if score >= 70 else "red"
    badge_url = f"https://img.shields.io/badge/compliance-{score}%25-{color}"
    
    comment = f"""## 🔒 ComplianceBot Scan Results

![Compliance Score]({badge_url})

**Score: {score}/100** | **Findings: {findings_count}**

{'✅ This MR meets compliance requirements.' if score >= 85 else '⚠️ Review compliance findings before merging.'}

[View Full Report](../issues?label_name=compliance)
"""
    
    mr.notes.create({'body': comment})

def create_compliance_issue(project_id: str, report_markdown: str, labels: list):
    """Create a GitLab issue with the compliance report."""
    gl = get_gitlab_client()
    project = gl.projects.get(project_id)
    
    project.issues.create({
        'title': f'🔒 Compliance Report — {os.environ.get("CI_COMMIT_REF_NAME", "main")}',
        'description': report_markdown,
        'labels': labels,
        'assignee_ids': []
    })
```

---

## 10. AGENTS.md & SKILL.md Configuration

### AGENTS.md (Root of Repository)

```markdown
# ComplianceBot Flow — Agent Instructions

## Context
This project uses ComplianceBot Flow to automatically analyze merge requests
and CI/CD pipelines for compliance with SOC 2, ISO 27001, PCI-DSS, and HIPAA.

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
```

### SKILL.md — Compliance Scan Skill

```markdown
---
name: compliance-scan
description: >
  Run a full compliance scan on the current project or a specific merge request.
  Maps findings to SOC 2, ISO 27001, and PCI-DSS controls. Generates an evidence
  package and compliance score.
metadata:
  slash-command: enabled
---

# Compliance Scan Skill

When invoked with `/compliance-scan`, perform the following:

1. Identify the current project context (project ID, branch, recent MRs)
2. Run the ComplianceScanner agent on the latest merge request or the last 7 days of changes
3. Map findings using the ComplianceMapper agent
4. Calculate a compliance score (0-100)
5. Return a summary with:
   - Overall score
   - Top 3 critical findings
   - Frameworks covered
   - Link to full report

## Usage Examples
- `/compliance-scan` — Scan current project
- `/compliance-scan mr=!142` — Scan specific MR
- `/compliance-scan framework=soc2` — Scan for SOC 2 only
- `/compliance-scan period=2026-01-01:2026-03-31` — Scan a date range
```

---

## 11. CI/CD Pipeline Setup

### Full `.gitlab-ci.yml`

```yaml
# .gitlab-ci.yml
stages:
  - test
  - security
  - compliance
  - report

variables:
  PYTHON_VERSION: "3.11"
  COMPLIANCE_FRAMEWORKS: "soc2,iso27001,pci-dss"

# ── Standard Pipeline ───────────────────────────────
unit-tests:
  stage: test
  image: python:3.11-slim
  script:
    - pip install -r requirements.txt
    - pytest tests/ -v --tb=short
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

sast:
  stage: security
  include:
    - template: Security/SAST.gitlab-ci.yml

dependency-scanning:
  stage: security
  include:
    - template: Security/Dependency-Scanning.gitlab-ci.yml

secret-detection:
  stage: security
  include:
    - template: Security/Secret-Detection.gitlab-ci.yml

# ── ComplianceBot Flow ──────────────────────────────
compliance-scan-mr:
  stage: compliance
  image: python:3.11-slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  before_script:
    - pip install -r requirements.txt python-gitlab
  script:
    - python src/agents/scanner.py --mode mr --mr-iid $CI_MERGE_REQUEST_IID
    - python src/agents/mapper.py
    - python src/agents/evidence_collector.py --mode sprint
    - python src/agents/reporter.py --output mr-comment
  artifacts:
    paths:
      - compliance-report.json
    expire_in: 30 days

compliance-weekly-report:
  stage: compliance
  image: python:3.11-slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
  before_script:
    - pip install -r requirements.txt python-gitlab
  script:
    - python src/agents/scanner.py --mode full --period 30d
    - python src/agents/mapper.py
    - python src/agents/evidence_collector.py --mode full --period 30d
    - python src/agents/reporter.py --output issue,pdf
  artifacts:
    paths:
      - compliance-report.pdf
      - evidence-package.json
    expire_in: 365 days  # Keep for audit purposes

upload-to-gcs:
  stage: report
  image: google/cloud-sdk:slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
  script:
    - echo $GCP_SERVICE_ACCOUNT_KEY | base64 -d > /tmp/sa-key.json
    - gcloud auth activate-service-account --key-file=/tmp/sa-key.json
    - gsutil cp compliance-report.pdf gs://compliance-evidence-${CI_PROJECT_ID}/
    - gsutil cp evidence-package.json gs://compliance-evidence-${CI_PROJECT_ID}/
  dependencies:
    - compliance-weekly-report
```

### Environment Variables Required
```
GITLAB_TOKEN          — GitLab API token (scope: api)
GCP_PROJECT_ID        — Google Cloud project ID
GCP_SERVICE_ACCOUNT_KEY — Base64-encoded GCP service account JSON
BIGQUERY_DATASET      — BigQuery dataset for trend data
GCS_BUCKET            — GCS bucket for evidence archive
COMPLIANCE_FRAMEWORKS — Comma-separated list: soc2,iso27001,pci-dss,hipaa
NOTIFICATION_SLACK_URL — (Optional) Slack webhook for alerts
```

---

## 12. Compliance Frameworks Covered

### SOC 2 Type II — Trust Service Criteria

| Control | ID | ComplianceBot Coverage |
|---|---|---|
| Logical access controls | CC6.1 | MR approvals, auth code changes |
| User authentication | CC6.2 | Password policy, MFA config checks |
| Access removal | CC6.3 | Offboarding via GitLab access log |
| Encryption in transit | CC6.7 | TLS config changes, cert expiry |
| Vulnerability management | CC7.1 | SAST/DAST findings, CVE tracking |
| Incident response | CC7.3 | Pipeline failures, security alerts |
| Change management | CC8.1 | MR approval workflow, deployment records |

### ISO 27001:2022

| Control | ID | ComplianceBot Coverage |
|---|---|---|
| Cryptographic controls | A.10.1 | Encryption algorithm changes |
| Secure development | A.8.25 | Code review enforcement |
| Vulnerability management | A.8.8 | Dependency scanning results |
| Logging | A.8.15 | Pipeline audit trail |
| Access rights | A.5.15 | GitLab role changes |

### PCI-DSS v4.0

| Requirement | ComplianceBot Coverage |
|---|---|
| 6.2 — Bespoke software security | SAST findings on payment code |
| 6.3.3 — Security patches | Dependency update tracking |
| 7.2 — Access control | RBAC change detection |
| 8.2 — Authentication | Auth code change analysis |
| 10.2 — Audit logs | Pipeline execution records |

---

## 13. Features & Innovations

### Core Features
- **Multi-framework support** — SOC 2, ISO 27001, PCI-DSS, HIPAA in one flow
- **Triggered automation** — Reacts to MR events, pipeline completions, and schedules
- **Evidence packages** — Cryptographically hashed, timestamped, auditor-ready
- **Compliance scoring** — 0-100 score with per-framework breakdown
- **MR comment badges** — Visual compliance indicator on every PR
- **GitLab Issues reports** — Auto-created issues with structured findings
- **PDF export** — Downloadable evidence packages via CI artifacts
- **Custom controls** — AGENTS.md for org-specific compliance rules

### Innovative Differentiators

1. **Compliance Drift Detection** — Compares current score to 90-day baseline; alerts on declining trend before an audit window

2. **Auditor Mode** — Generates reports in the exact format requested by Big 4 accounting firms (deloitte/pwc/ey/kpmg templates configurable)

3. **Evidence Chain of Custody** — SHA-256 hash of every evidence artifact, linked to GitLab's immutable commit history, creates a tamper-evident audit trail

4. **Sprint Compliance Dashboard** — Posted as a GitLab Pages site showing compliance posture over time (powered by BigQuery)

5. **Remediation Auto-Linking** — Automatically creates linked child issues with specific remediation steps, assigned to the relevant MR author

6. **Zero-Configuration Start** — Works out of the box on any GitLab project without custom setup; AGENTS.md provides progressive enhancement

7. **Retroactive Analysis** — Can scan the entire history of a repository, not just new activity, enabling compliance onboarding for existing projects

### AI Innovation: Contextual Understanding
Unlike rule-based compliance scanners (Checkov, Terrascan), ComplianceBot uses Claude's contextual reasoning to understand *intent*, not just patterns:

```
Rule-based: "Found 'password' in code → FAIL"

ComplianceBot: "This change adds a password strength validator
that ENFORCES the complexity requirements defined in SOC2-CC6.1.
This is a PASS — it improves compliance posture."
```

---

## 14. Demo Video Strategy

### 3-Minute Video Script

**[0:00 – 0:30] The Problem**
- Show a developer merging code that contains a compliance issue
- Show the chaos of evidence gathering before an audit (spreadsheet, manual emails)
- Text: "SOC 2 audits cost 200-400 engineering hours. What if it took 2 minutes?"

**[0:30 – 1:15] ComplianceBot in Action — MR Trigger**
- Open a merge request that changes authentication code
- Show ComplianceBot Flow auto-triggering
- Show the compliance score badge appearing in the MR comment
- Show the specific findings with control IDs and remediation steps

**[1:15 – 2:00] Weekly Compliance Digest**
- Show the nightly scheduled flow running
- Show the GitLab Issue auto-created with the full report
- Show the PDF evidence package as a CI artifact
- Show the compliance score trend (improving over time)

**[2:00 – 2:30] The Architecture**
- Quick diagram of the 4-agent flow
- Show the AI Catalog with all 4 agents published
- Show the flow YAML configuration

**[2:30 – 3:00] Impact & Close**
- "SOC 2 evidence: collected in 2 minutes, not 2 weeks"
- Show BigQuery dashboard with compliance trend
- "Built entirely inside GitLab. Zero new tools. Zero new workflows."
- Link to repository and setup instructions

### Recording Tips
- Use OBS Studio for screen recording
- Record in 1920x1080
- Use GitLab's dark theme for visual contrast
- Add captions for the compliance findings
- Upload to YouTube as Unlisted first, then set to Public after final review

---

## 15. Submission Requirements Checklist

See the companion file: **`CHECKLIST.md`**

---

## 16. Resources & References

### Official GitLab Documentation
- [GitLab Duo Agent Platform](https://docs.gitlab.com/user/duo_agent_platform/)
- [Flows Documentation](https://docs.gitlab.com/user/duo_agent_platform/flows/)
- [Custom Agents](https://docs.gitlab.com/user/duo_agent_platform/agents/external/)
- [External Agent Examples](https://docs.gitlab.com/user/duo_agent_platform/agents/external_examples/)
- [AGENTS.md Customization](https://docs.gitlab.com/user/gitlab_duo/customize_duo/agents_md/)
- [Agent Skills (SKILL.md)](https://docs.gitlab.com/user/duo_agent_platform/customize/agent_skills/)
- [AI Catalog](https://about.gitlab.com/blog/ai-catalog-discover-and-share-agents/)
- [Getting Started Guide (8-part)](https://about.gitlab.com/blog/gitlab-duo-agent-platform-complete-getting-started-guide/)

### Hackathon Resources
- [Hackathon Page](https://gitlab.devpost.com)
- [GitLab AI Hackathon Group](https://gitlab.com/gitlab-ai-hackathon)
- [Request Access Form](https://forms.gle/EeCH2WWUewK3eGmVA)
- [Discord #ai-hackathon](https://discord.com/invite/gitlab)
- [Custom Agents Tutorial](https://gitlab.navattic.com/custom-agents)
- [Custom Flows Tutorial](https://gitlab.navattic.com/custom-flows)
- [GitLab Duo Prompt Library](https://about.gitlab.com/gitlab-duo/prompt-library/)

### Libraries & Tools
- `python-gitlab` — GitLab API client: `pip install python-gitlab`
- `anthropic` — Anthropic SDK: `pip install anthropic`
- `google-cloud-bigquery` — BigQuery client: `pip install google-cloud-bigquery`
- `google-cloud-storage` — GCS client: `pip install google-cloud-storage`
- `reportlab` — PDF generation: `pip install reportlab`
- `jinja2` — Template rendering: `pip install jinja2`

### Compliance References
- [SOC 2 Trust Service Criteria](https://www.aicpa.org/resources/article/trust-services-criteria)
- [ISO 27001:2022 Controls](https://www.iso.org/standard/27001)
- [PCI-DSS v4.0](https://www.pcisecuritystandards.org/document_library/)
- [HIPAA Technical Safeguards](https://www.hhs.gov/hipaa/for-professionals/security/guidance/)
- [NIST SP 800-53 Rev 5](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)

---

*Document version: 1.0 | Generated: March 18, 2026 | ComplianceBot Flow Team*
