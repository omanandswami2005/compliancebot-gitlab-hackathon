# ComplianceBot Flow — Master Development Checklist
> Cross-referenced with `compliancebot-research-guide.md`
> **Hackathon Deadline: March 25, 2026 @ 2:00 PM EDT**

Track progress: Replace `[ ]` with `[x]` as you complete each item.

---

## 🏁 PHASE 0 — Hackathon Setup
*Reference: [Research Guide §1 — Hackathon Overview](#)*

- [ ] Register on [gitlab.devpost.com](https://gitlab.devpost.com)
- [ ] Request access to GitLab AI Hackathon group → [forms.gle/EeCH2WWUewK3eGmVA](https://forms.gle/EeCH2WWUewK3eGmVA)
- [ ] Join Discord → [discord.com/invite/gitlab](https://discord.com/invite/gitlab) → channel `#ai-hackathon`
- [ ] Create public repo in [gitlab.com/gitlab-ai-hackathon](https://gitlab.com/gitlab-ai-hackathon)
- [ ] Add MIT `LICENSE` file at repo root (must be visible/detectable)
- [ ] Enable GitLab Duo Agent Platform in project settings (requires 18.8+)
- [ ] Enable Flows in GitLab Duo settings
- [ ] Configure push rules to allow service account (required for flows that commit code)
- [ ] Verify GitLab hosted runners are enabled in the project

---

## 🏗 PHASE 1 — Repository & Project Structure
*Reference: [Research Guide §9 — Project Structure](#)*

- [x] Create directory structure as defined in §9
- [x] Add `README.md` with project description, installation steps, and architecture diagram
- [x] Add `AGENTS.md` at repo root → see §10 for template
- [x] Create `skills/compliance-scan/SKILL.md` → see §10 for template
- [x] Create `skills/report-generator/SKILL.md`
- [x] Add `requirements.txt`:
  ```
  python-gitlab>=4.0.0
  anthropic>=0.25.0
  google-cloud-bigquery>=3.0.0
  google-cloud-storage>=2.0.0
  reportlab>=4.0.0
  jinja2>=3.0.0
  pytest>=7.0.0
  ```
- [x] Add `.gitignore` (exclude `.env`, `*.pyc`, `__pycache__`, `/reports`)

---

## 🤖 PHASE 2 — Agent Development
*Reference: [Research Guide §5 — Agent Design](#)*

### Agent 1: ComplianceScanner
- [x] Create `.gitlab/duo/compliance-scanner.yaml` with GitLab format
  - [x] Set `visibility: public` for AI Catalog publication
  - [x] Define `system_prompt` with scanner behavior
  - [x] List tools: `read_file`, `read_files`, `analyze_file_diff`
- [x] Implement `src/agents/scanner.py` → full code in §9
- [x] Implement `_analyze_auth_change()` method
- [x] Implement `_analyze_dependency_change()` method
- [x] Implement `_analyze_encryption_change()` method
- [x] Implement `_pull_sast_findings()` method
- [x] Write unit tests `tests/test_scanner.py`
- [x] Create fixture `tests/fixtures/sample_mr_diff.json`
- [ ] Publish agent to AI Catalog as **Public** (via GitLab Web UI)

### Agent 2: ComplianceMapper
- [x] Create `.gitlab/duo/compliance-mapper.yaml` with GitLab format
  - [x] Set `visibility: public` for AI Catalog publication
  - [x] Define `system_prompt` with mapper behavior
  - [x] List tools: `read_file`, `execute_query`, `log_analysis`
- [x] Implement `src/agents/mapper.py`
- [x] Create `src/frameworks/soc2_controls.json` with all CC controls
- [x] Create `src/frameworks/iso27001_controls.json` with Annex A controls
- [x] Create `src/frameworks/pci_dss_controls.json` with Requirements 6,7,8,10,12
- [x] Create `src/frameworks/hipaa_controls.json` with Technical Safeguards
- [x] Implement `CONTROL_MAPPINGS` dict → see §5 for mappings
- [x] Implement compliance score calculation (0–100)
- [x] Write unit tests `tests/test_mapper.py`
- [ ] Publish agent to AI Catalog as **Public** (via GitLab Web UI)

### Agent 3: EvidenceCollector
- [x] Create `.gitlab/duo/evidence-collector.yaml` with GitLab format
  - [x] Set `visibility: public` for AI Catalog publication
  - [x] Define `system_prompt` with evidence behavior
  - [x] List tools: `read_file`, `execute_query`, `archive_data`, `generate_hash`
- [x] Implement `src/utils/evidence_builder.py` → full code in §9
- [x] Implement `collect_mr_approvals()` method
- [x] Implement `collect_pipeline_security_scans()` method
- [x] Implement `collect_access_control_records()` method (GitLab audit events)
- [x] Implement `_hash_evidence()` SHA-256 method → ensures non-repudiation
- [x] Implement `build_package()` to generate final JSON evidence package
- [x] Write unit tests `tests/test_evidence.py`
- [ ] Publish agent to AI Catalog as **Public**

### Agent 4: ComplianceReporter
- [x] Create `.gitlab/duo/compliance-reporter.yaml` with GitLab format
  - [x] Set `visibility: public` for AI Catalog publication
  - [x] Define `system_prompt` with reporter behavior (Vertex AI integration)
  - [x] List tools: `read_file`, `create_issue`, `post_comment`, `generate_pdf`, `archive_file`
- [x] Implement `src/agents/reporter.py`
- [x] Implement `cloud/cloud_run/report_generator.py` (Flask service)
- [x] Implement `generate_narrative()` → uses Vertex AI (Gemini-2.5-flash)
- [x] Implement `post_mr_comment()` method (only if score < 85)
- [x] Implement `create_gitlab_issue()` method (for each finding, severity >= medium)
- [x] Implement `generate_pdf()` using ReportLab
- [x] Implement `log_to_bigquery()` method (evidence archival)
- [x] Implement `upload_to_gcs()` method with 1-year retention tag (SOC 2)
- [x] Write unit tests `tests/test_reporter.py`
- [ ] Publish agent to AI Catalog as **Public** (via GitLab Web UI)

---

## � PHASE 3 — Flow Orchestration
*Reference: [Research Guide §6 — Flow Design](#)*

- [x] Create `.gitlab/flows/compliance-flow.yaml` with GitLab format
  - [x] Set `public: true` for AI Catalog publication
  - [x] Define YAML `definition.version: v1` with components
  - [x] Define: 3 triggers (MR events, pipeline events, schedule)
  - [x] Define: 4 sequential components (scanner → mapper → evidence_collector → reporter)
  - [x] Define: 3 output types (gitlab_issue, mr_comment, ci_artifact)
  - [x] Set conditional outputs (mr_comment only if score < 85)
- [ ] Create test MR → verify flow executes end-to-end
- [ ] Verify **Automate → Sessions** shows all 4 agents executed
- [ ] Verify **Automate → Flows** shows `ComplianceBot Flow` listed
- [ ] Publish flow to AI Catalog as **Public** (via GitLab Web UI)

---

## 🔧 PHASE 4 — Anthropic Integration (SKIPPED ✅)
*Reference: [Research Guide §7 — Anthropic API](#)*

- [x] **Reason**: No Anthropic API key available, GCP credits prioritized
- [x] **Decision**: Use Vertex AI (Gemini-2.5-flash) instead
- [x] **Advantage**: Zero additional API cost (uses existing GCP service account)
- [x] **Status**: ✅ Completed (integrated into reporter agent)

---

## 🚀 PHASE 5 — Google Cloud Integration
*Reference: [Research Guide §8 — Google Cloud Platform](#)*

### BigQuery
- [x] Schema defined: `cloud/bigquery_schema.sql` (ready to deploy)
- [x] Table structure: evidence_items with hash, timestamp, source, control_id columns
- [x] Retention policy: 1 year (SOC 2 compliance)
- [ ] **TODO**: Create dataset and table in GCP (requires GCP project setup)
- [ ] **TODO**: Set environment variable: `BIGQUERY_DATASET=compliance`

### Cloud Storage (GCS)
- [x] Bucket schema defined with lifecycle policy (365-day deletion)
- [x] PDF archival with 7-day signed URLs implemented in `report_generator.py`
- [x] Metadata tagging for compliance control reference
- [ ] **TODO**: Create GCS bucket in GCP (requires GCP project setup)
- [ ] **TODO**: Set environment variable: `GCS_BUCKET=compliance-evidence-${GCP_PROJECT_ID}`

### Cloud Run Service
- [x] Service code: `cloud/cloud_run/report_generator.py` (uses Vertex AI Gemini-2.5-flash)
- [x] Dockerfile: Uses Python 3.11 slim + Gunicorn
- [x] Deployment script: `cloud/cloud_run/deploy.sh` (uses Cloud Build, ❌ no Docker needed)
- [ ] **TODO**: Run `bash cloud/cloud_run/deploy.sh $GCP_PROJECT_ID` in GCP-enabled environment
- [ ] **TODO**: Set service environment variables:
  - `GCP_PROJECT_ID` (from GCP Console)
  - `GCP_SERVICE_ACCOUNT_KEY` (base64 encoded)
  - `BIGQUERY_DATASET=compliance`
  - `GCS_BUCKET=compliance-evidence-${GCP_PROJECT_ID}`

### Vertex AI Integration
- [x] Service code updated to use `vertexai.generative_models.GenerativeModel`
- [x] Model: Gemini-2.5-flash for narrative generation
- [x] Cost: ~$0.001 per report (free tier quota included)
- [x] No separate API key needed (uses GCP service account)

### Terraform (Optional)
- [x] Infrastructure as Code: `cloud/terraform/main.tf` (ready for deployment)
- [ ] **TODO**: Run `terraform init && terraform plan && terraform apply` (if desired)
- [ ] **TODO**: Alternatively: Use GCP Console or Cloud Build deployment script
- [ ] Set `GCP_PROJECT_ID` and `GCP_SERVICE_ACCOUNT_KEY` as CI/CD variables
- [x] Document GCP setup in `docs/configuration.md` ✓
- [ ] Add "Google Cloud" tag/label in Devpost submission

---

## 🧪 PHASE 6 — Testing & Quality
*Reference: [Research Guide §9 — Code Examples](#)*

- [ ] All unit tests pass: `pytest tests/ -v`
- [ ] Test coverage ≥ 70%
- [ ] Test with a real GitLab project (use hackathon group project)
- [ ] Test MR trigger end-to-end: create MR → badge appears in comment
- [ ] Test pipeline trigger end-to-end: pipeline runs → issue created
- [ ] Test scheduled trigger: manual trigger → PDF artifact generated
- [ ] Test AGENTS.md customization: add org-specific control → verify in report
- [ ] Test `/compliance-scan` slash command in GitLab Duo Chat
- [ ] Test Claude Code external agent on repository
- [ ] Verify evidence package JSON is valid and hashes are consistent
- [ ] Verify PDF evidence package opens correctly
- [ ] Test on project with ZERO compliance issues (score 100 expected)
- [ ] Test on project with known issues (score < 85, MR comment posted)

---

## 📝 PHASE 7 — Documentation
*Reference: [Research Guide — All Sections](#)*

- [ ] `README.md` includes:
  - [ ] What it does (2–3 sentence description)
  - [ ] Architecture diagram (ASCII or image)
  - [ ] Prerequisites (GitLab version, Duo tier, etc.)
  - [ ] Quick start / installation steps
  - [ ] Configuration options (AGENTS.md, env vars)
  - [ ] All 4 agents described with inputs/outputs
  - [ ] How to run a manual scan
  - [ ] Example compliance report screenshot
  - [ ] License section (MIT)
- [ ] `docs/installation.md` — Full setup guide
- [ ] `docs/configuration.md` — All env vars documented, GCP setup
- [ ] `docs/compliance-frameworks.md` — All controls covered per framework
- [ ] Code inline comments on all major functions
- [ ] AGENTS.md fully filled out → see §10

---

## 🎬 PHASE 8 — Demo Video
*Reference: [Research Guide §14 — Demo Video Strategy](#)*

- [ ] Script written and timed (must be ≤ 3 minutes)
- [ ] Recording environment prepared (GitLab dark theme, 1920×1080)
- [ ] Test project set up in hackathon group with sample compliance findings
- [ ] **Scene 1 [0:00–0:30]:** Record the pain — manual evidence spreadsheet, audit chaos
- [ ] **Scene 2 [0:30–1:15]:** Record MR trigger → badge appearing → finding details
- [ ] **Scene 3 [1:15–2:00]:** Record scheduled report → GitLab Issue created → PDF artifact
- [ ] **Scene 4 [2:00–2:30]:** Record AI Catalog with 4 agents published
- [ ] **Scene 5 [2:30–3:00]:** Record BigQuery dashboard / impact statement
- [ ] Add captions/text overlays for key moments
- [ ] Add background music (royalty-free)
- [ ] Edit to exactly ≤ 3:00
- [ ] Upload to YouTube as **Public** (not Unlisted — judges need access)
- [ ] Copy YouTube URL for Devpost submission

---

## 📦 PHASE 9 — Devpost Submission
*Reference: [Research Guide §1 — Hard Requirements](#)*

### Before Submitting
- [ ] All source code is in the GitLab AI Hackathon group (public repo)
- [ ] Primary license is MIT and visible at top of repo page
- [ ] Demo video is ≤ 3 minutes and publicly accessible on YouTube/Vimeo
- [ ] The flow is published as **Public** in AI Catalog
- [ ] At least one agent is published as **Public** in AI Catalog
- [ ] Project runs end-to-end without errors

### Devpost Submission Form
- [ ] **Project URL** → GitLab AI Hackathon group repo URL
- [ ] **Text description** — Copy from README intro (features + functionality)
- [ ] **Demo video URL** — YouTube link
- [ ] **Prizes opted in:**
  - [ ] Grand Prize
  - [ ] Most Impactful
  - [ ] Most Technically Impressive  
  - [ ] GitLab + Anthropic Grand Prize ✅
  - [ ] GitLab + Google Cloud Grand Prize ✅
- [ ] **Team members** added (if applicable)
- [ ] Submit before **March 25, 2026 @ 2:00 PM EDT** ⏰

---

## 🏆 JUDGING ALIGNMENT REVIEW

Before final submission, verify against each judging criterion:

| Criterion | How We Score | Check |
|---|---|---|
| **Technological Implementation** | Uses Flows + 4 custom agents + Claude + GCP + triggers | [ ] |
| **Design & Usability** | Zero-config install, AGENTS.md customization, slash command | [ ] |
| **Potential Impact** | Solves 200–400hr audit problem; addresses AI Paradox in compliance | [ ] |
| **Quality of the Idea** | No existing GitLab-native compliance flow agent exists | [ ] |

---

## 🔗 Quick Reference Links

| Resource | URL |
|---|---|
| Hackathon page | https://gitlab.devpost.com |
| Hackathon GitLab group | https://gitlab.com/gitlab-ai-hackathon |
| Access request form | https://forms.gle/EeCH2WWUewK3eGmVA |
| Discord | https://discord.com/invite/gitlab |
| Flows docs | https://docs.gitlab.com/user/duo_agent_platform/flows/ |
| Agent Platform docs | https://docs.gitlab.com/user/duo_agent_platform/ |
| External agents examples | https://docs.gitlab.com/user/duo_agent_platform/agents/external_examples/ |
| AI Catalog blog | https://about.gitlab.com/blog/ai-catalog-discover-and-share-agents/ |
| Getting started guide | https://about.gitlab.com/blog/gitlab-duo-agent-platform-complete-getting-started-guide/ |
| Prompt library | https://about.gitlab.com/gitlab-duo/prompt-library/ |
| Research guide | `compliancebot-research-guide.md` (this repo) |

---

*Checklist version: 1.0 | Last updated: March 18, 2026*
