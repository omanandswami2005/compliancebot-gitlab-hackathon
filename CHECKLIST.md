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
- [x] Create `.gitlab/agents/compliance-scanner.yaml` → see §5 for YAML skeleton
- [x] Implement `src/agents/scanner.py` → full code in §9
- [x] Implement `_analyze_auth_change()` method
- [x] Implement `_analyze_dependency_change()` method
- [x] Implement `_analyze_encryption_change()` method
- [x] Implement `_pull_sast_findings()` method
- [x] Write unit tests `tests/test_scanner.py`
- [x] Create fixture `tests/fixtures/sample_mr_diff.json`
- [ ] Publish agent to AI Catalog as **Public**

### Agent 2: ComplianceMapper
- [x] Create `.gitlab/agents/compliance-mapper.yaml`
- [x] Implement `src/agents/mapper.py`
- [x] Create `src/frameworks/soc2_controls.json` with all CC controls
- [x] Create `src/frameworks/iso27001_controls.json` with Annex A controls
- [x] Create `src/frameworks/pci_dss_controls.json` with Requirements 6,7,8,10,12
- [x] Create `src/frameworks/hipaa_controls.json` with Technical Safeguards
- [x] Implement `CONTROL_MAPPINGS` dict → see §5 for mappings
- [x] Implement compliance score calculation (0–100)
- [x] Write unit tests `tests/test_mapper.py`
- [ ] Publish agent to AI Catalog as **Public**

### Agent 3: EvidenceCollector
- [x] Create `.gitlab/agents/evidence-collector.yaml`
- [x] Implement `src/utils/evidence_builder.py` → full code in §9
- [x] Implement `collect_mr_approvals()` method
- [x] Implement `collect_pipeline_security_scans()` method
- [x] Implement `collect_access_control_records()` method (GitLab audit events)
- [x] Implement `_hash_evidence()` SHA-256 method → ensures non-repudiation
- [x] Implement `build_package()` to generate final JSON evidence package
- [x] Write unit tests `tests/test_evidence.py`
- [ ] Publish agent to AI Catalog as **Public**

### Agent 4: ComplianceReporter
- [x] Create `.gitlab/agents/compliance-reporter.yaml`
- [x] Implement `src/agents/reporter.py`
- [x] Create `src/templates/compliance_report.md.j2` (Jinja2 Markdown template)
- [x] Create `src/templates/mr_comment_badge.md.j2` (MR badge comment template)
- [x] Implement `src/utils/gitlab_api.py` → `post_compliance_comment()` → see §9
- [x] Implement `src/utils/gitlab_api.py` → `create_compliance_issue()`
- [x] Implement PDF generation via `reportlab` → `src/utils/pdf_generator.py`
- [x] Write unit tests `tests/test_reporter.py`
- [ ] Publish agent to AI Catalog as **Public**

---

## 🔗 PHASE 3 — Flow Orchestration
*Reference: [Research Guide §6 — Flow Design](#)*

- [x] Create `.gitlab/flows/compliance-flow.yaml` → full YAML in §6
- [x] Define `triggers` section: `merge_request`, `pipeline`, `schedule`
- [x] Define `components` section with all 4 agents in dependency order
- [x] Define `outputs` section: `gitlab_issue`, `mr_comment`, `ci_artifact`
- [x] Configure `schedule` trigger (weekly cron: `0 2 * * 1`)
- [ ] Test MR trigger → open a test MR and verify flow starts
- [ ] Test pipeline trigger → run pipeline on main and verify flow starts
- [ ] Test scheduled trigger → manually trigger the schedule
- [ ] Verify flow appears in Automate > Sessions with proper logs
- [ ] Publish flow to AI Catalog as **Public** (required for hackathon)

---

## 🤖 PHASE 4 — Anthropic Integration ($10K Bonus Prize)
*Reference: [Research Guide §7 — Anthropic Integration](#)*
**⚠️ SKIPPED — No Anthropic API key available. Using Google Cloud Vertex AI instead.**

- [x] ~~Confirm flows use Claude Sonnet 4 through GitLab gateway~~ → Using Vertex AI Gemini instead
- [x] ~~Implement Claude risk scoring prompt~~ → Vertex AI handles narrative generation
- [x] ~~Implement semantic auth change analysis using Claude~~ → Vertex AI provides similar capability
- [x] ~~Implement Claude-powered evidence narrative generation~~ → Implemented with Vertex AI
- [x] ~~Configure External Agent using Claude Code~~ → Not needed with Vertex AI

---

## ☁️ PHASE 5 — Google Cloud Integration ($10K Bonus Prize)
*Reference: [Research Guide §8 — Google Cloud Integration](#)*
**🔥 PRIMARY FOCUS — Using GCP credits for Vertex AI + BigQuery + Cloud Run**

- [ ] Create GCP project for ComplianceBot
- [ ] Enable APIs: BigQuery, Cloud Run, Cloud Storage, Vertex AI
- [ ] Create BigQuery dataset and `compliance_findings` table → schema in §8
- [x] Implement BigQuery logging in `cloud/cloud_run/report_generator.py` ✓
- [x] Implement Cloud Run report generator with Vertex AI Gemini ✓
  - [x] Updated `cloud/cloud_run/report_generator.py` to use Vertex AI
  - [x] Implements `generate_narrative()` with Gemini-2.5-flash
  - [x] Implements `log_to_bigquery()` for evidence archival
  - [x] Implements `upload_to_gcs()` with signed URLs
- [x] Containerize Cloud Run service: `Dockerfile` ✓
- [ ] Deploy Cloud Run service: `gcloud run deploy compliance-reporter`
- [x] Create GCS bucket for evidence archive → Terraform in §8 ✓
- [x] Apply 1-year retention policy to GCS bucket (SOC 2 requirement) ✓
- [ ] Implement `upload-to-gcs` CI/CD job → see §11
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
