# ComplianceBot GitLab AI Catalog Sync - Debugging Context for Grok AI

## ERROR
```
❌ Error: No item files found in 1 of the sources
```
Occurs during: `ACTION=validate node /tmp/ai-catalog-sync/index.js`

---

## REPOSITORY STRUCTURE

```
compliancebot-gitlab-hackathon/
├── .gitlab-ci.yml                          # CI/CD Configuration
├── .gitignore
├── README.md
├── AGENTS.md
├── CHECKLIST.md
├── LICENSE
├── requirements.txt
│
├── agents/                                 # ← Official agent location (ROOT level)
│   ├── compliance-scanner.yaml
│   ├── compliance-mapper.yaml
│   ├── evidence-collector.yaml
│   ├── compliance-reporter.yaml
│   └── test-agent.yaml
│
├── flows/                                  # ← Official flow location (ROOT level)
│   └── compliance-flow.yaml
│
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
│       ├── evidence_builder.py
│       └── gitlab_api.py
│
├── tests/
│   ├── test_scanner.py
│   ├── test_mapper.py
│   ├── test_reporter.py
│   ├── test_evidence.py
│   └── fixtures/
│       └── sample_mr_diff.json
│
├── docs/
│   ├── configuration.md
│   ├── installation.md
│   ├── compliance-frameworks.md
│   ├── PUBLISHING_GUIDE.md
│   └── CLOUD_BUILD_GUIDE.md
│
├── cloud/
│   ├── bigquery_schema.sql
│   ├── cloud_run/
│   │   ├── Dockerfile
│   │   ├── deploy.sh
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   └── report_generator.py
│   └── terraform/
│       └── main.tf
│
├── scripts/
│   └── diagnostic.sh
│
└── skills/
    ├── compliance-scan/SKILL.md
    └── report-generator/SKILL.md
```

---

## .gitlab-ci.yml (Full)

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

# ── AI Catalog Sync Component ───────────────────────────────
# Validates and syncs agents/flows to AI Catalog on tag push
# Official docs: https://gitlab.com/components/ai-catalog
include:
  - component: $CI_SERVER_HOST/components/ai-catalog/catalog-sync@0.0.1
    inputs:
      agent_directory: "agents" # Where agent YAML files are located
      flow_directory: "flows" # Where flow YAML files are located
      enable_in_project: "false" # Don't require group_id (simpler setup)

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
  extends: Security/SAST.gitlab-ci.yml

dependency-scanning:
  stage: security
  extends: Security/Dependency-Scanning.gitlab-ci.yml

secret-detection:
  stage: security
  extends: Security/Secret-Detection.gitlab-ci.yml

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
    expire_in: 365 days # Keep for audit purposes

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

---

## AGENT YAML FILES

### agents/compliance-scanner.yaml

```yaml
name: ai_compliance-scanner
description: "Scans merge requests and pipelines for compliance signals. Detects auth changes, encryption configs, dependency vulnerabilities, and SAST findings."
public: true
system_prompt: |
  You are a compliance scanning agent for the GitLab Duo Agent Platform.
  Your role is to analyze merge request diffs and pipeline scan results to identify compliance risks.

  For each merge request:
  1. Check for authentication/authorization changes
  2. Detect encryption configuration changes
  3. Identify dependency version updates (especially security patches)
  4. Report SAST/DAST findings
  5. Map each finding to a specific control ID (e.g., SOC2-CC6.1, ISO27001-A.8.2.3)

  Return findings as a structured JSON list with:
  - finding_type (auth_change, encryption_change, dependency_update, sast_finding)
  - severity (critical, high, medium, low)
  - control_ids (array of mapped controls)
  - remediation_steps
  - file_paths affected
tools:
  - read_file
  - read_files
  - analyze_file_diff
```

### agents/compliance-mapper.yaml

```yaml
name: ai_compliance-mapper
description: "Maps security findings to compliance framework controls (SOC 2, ISO 27001, PCI-DSS, HIPAA). Scores compliance readiness on 0-100 scale."
public: true
system_prompt: |
  You are a compliance mapping agent for the GitLab Duo Agent Platform.
  Your role is to map raw security findings to specific compliance control IDs.

  Supported frameworks:
  - SOC 2 Trust Services Criteria (CC, OE, PO, PT)
  - ISO 27001 Information Security Controls (A.5-A.18)
  - PCI-DSS Requirements (when payment-related code detected)
  - HIPAA Security Rule (when health data detected)

  For each finding:
  1. Identify primary framework (always SOC 2)
  2. Map to specific control ID
  3. Assess business risk
  4. Calculate compliance score impact

  Return JSON with:
  - control_mappings: [{ framework, control_id, title, requirement }]
  - risk_assessment: { business_impact, auditability, remediation_priority }
  - overall_compliance_score: 0-100
tools:
  - read_file
  - get_vulnerability_details
  - list_vulnerabilities
  - get_issue
  - get_repository_file
  - gitlab_blob_search
```

### agents/evidence-collector.yaml

```yaml
name: ai_evidence-collector
description: "Collects and archives audit trail evidence from GitLab. Generates SHA-256 hashes for non-repudiation. Archives to BigQuery with 1-year SOC 2 retention."
public: true
system_prompt: |
  You are an evidence collection agent for the GitLab Duo Agent Platform.
  Your role is to gather audit trails and evidence for compliance audits.

  Evidence collection period: Last 14 days (or 30 days for scheduled audits)
  Maximum MR records per run: 500

  Collect:
  1. Merge request metadata (author, approvers, timestamps)
  2. Pipeline execution results and logs
  3. Access control records (project membership changes)
  4. Deployment records (branch, user, timestamp)
  5. Code reviewer audit trail

  For each evidence item:
  1. Generate SHA-256 hash for non-repudiation
  2. Record collection timestamp (UTC)
  3. Include source system metadata
  4. Tag with compliance control reference
  5. Archive to BigQuery evidence table

  Return JSON with:
  - evidence_items: [{ hash, timestamp, source, control_id }]
  - collection_summary: { total_items, date_range, archive_status }
tools:
  - read_file
  - get_repository_file
  - list_project_audit_events
  - list_group_audit_events
  - gitlab_api_get
  - gitlab_graphql
```

### agents/compliance-reporter.yaml

```yaml
name: ai_compliance-reporter
description: "Generates audit-ready compliance reports using AI. Uses Vertex AI (Gemini-2.5-flash) to create executive summaries. Posts MR comments and creates GitLab issues for findings."
public: true
system_prompt: |
  You are a compliance reporting agent for the GitLab Duo Agent Platform.
  Your role is to generate compliance reports and communicate findings to the development team.

  Report types:
  1. Executive Summary (2-3 sentences, 0-100 compliance score)
  2. Detailed Findings (per-control analysis)
  3. Audit-Ready PDF (with evidence hashes, timestamps, signatures)
  4. MR Comment Badge (compliance score indicator)

  Report generation:
  1. Use Vertex AI (Gemini-2.5-flash) for narrative generation
  2. Include remediation timeline estimates
  3. Reference control IDs for auditor traceability
  4. Calculate days-to-compliance

  Delivery:
  - MR Comment: Only if score < 85 (avoid alert fatigue)
  - GitLab Issue: For each finding with severity >= medium
  - PDF Archive: To Google Cloud Storage with 1-year retention
  - BigQuery: Log all metrics for trend analysis

  Return JSON with:
  - report_summary: { score, recommendations, timeline_days }
  - mr_comment_posted: boolean
  - issue_creation_status: { created_count, issue_links }
  - pdf_archive_url: signed_7day_url
tools:
  - read_file
  - create_issue
  - create_issue_note
  - get_issue
  - list_issues
  - upload_artifact
```

### agents/test-agent.yaml

```yaml
name: test-agent
description: "Test agent for validation pipeline"
public: true
system_prompt: |
  Test agent for debugging and validation.
tools: []
```

---

## FLOW YAML FILE

### flows/compliance-flow.yaml

```yaml
# ComplianceBot Flow
# Official location: flows/compliance-flow.yaml (GitLab AI Catalog)
name: "ComplianceBot Flow"
description: "Multi-agent compliance automation flow that scans MRs, maps findings to controls, collects evidence, and generates audit-ready reports"
public: true
definition:
  version: v1
  environment: ambient

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
      cron: "0 2 * * 1"

  components:
    - name: scanner
      type: AgentComponent
      prompt_id: "compliance_scanner_prompt"
      inputs:
        - "context:merge_request_diff"
        - "context:pipeline_results"
      toolset:
        - read_file
        - read_files
        - analyze_file_diff
      ui_log_events:
        - on_agent_final_answer

    - name: mapper
      type: AgentComponent
      prompt_id: "compliance_mapper_prompt"
      inputs:
        - "from:scanner"
      toolset:
        - read_file
        - execute_query
        - log_analysis
      ui_log_events:
        - on_agent_final_answer

    - name: evidence_collector
      type: AgentComponent
      prompt_id: "evidence_collector_prompt"
      inputs:
        - "from:mapper"
        - "context:project"
      toolset:
        - read_file
        - execute_query
        - archive_data
        - generate_hash
      ui_log_events:
        - on_agent_final_answer

    - name: reporter
      type: AgentComponent
      prompt_id: "compliance_reporter_prompt"
      inputs:
        - "from:evidence_collector"
      toolset:
        - read_file
        - create_issue
        - post_comment
        - generate_pdf
        - archive_file
      ui_log_events:
        - on_agent_final_answer

  prompts:
    - prompt_id: "compliance_scanner_prompt"
      name: "ComplianceBot Scanner"
      prompt_template:
        system: |
          You are a compliance scanning agent.
          Analyze merge request diffs for compliance risks.
        user: |
          Analyze the following MR diff:
          {{context}}
        placeholder: history
      params:
        timeout: 180

    - prompt_id: "compliance_mapper_prompt"
      name: "ComplianceBot Mapper"
      prompt_template:
        system: |
          Map findings to compliance frameworks.
        user: |
          {{context}}
        placeholder: history
      params:
        timeout: 180

    - prompt_id: "evidence_collector_prompt"
      name: "ComplianceBot Evidence Collector"
      prompt_template:
        system: |
          Collect audit trail evidence.
        user: |
          {{context}}
        placeholder: history
      params:
        timeout: 180

    - prompt_id: "compliance_reporter_prompt"
      name: "ComplianceBot Reporter"
      prompt_template:
        system: |
          Generate compliance reports.
        user: |
          {{context}}
        placeholder: history
      params:
        timeout: 180

  routers:
    - from: scanner
      to: mapper
    - from: mapper
      to: evidence_collector
    - from: evidence_collector
      to: reporter
    - from: reporter
      to: end

  flow:
    entry_point: scanner
```

---

## PYTHON SOURCE CODE

### src/agents/scanner.py

```python
"""ComplianceBot Compliance Scanner Agent"""
import json
import argparse
from typing import Dict, List, Optional
import os

class ComplianceScanner:
    """Analyze MRs and pipelines for compliance signals"""
    
    def __init__(self):
        self.framework_list = ['soc2', 'iso27001', 'pci-dss', 'hipaa']
        
    def scan_mr(self, mr_iid: str) -> Dict:
        """Scan merge request for compliance issues"""
        findings = {
            'mr_iid': mr_iid,
            'findings': [],
            'summary': {
                'total_findings': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
        
        # Placeholder implementation
        try:
            # Scan authentication changes
            auth_findings = self._analyze_auth_changes(mr_iid)
            findings['findings'].extend(auth_findings)
            
            # Scan encryption configs
            encryption_findings = self._analyze_encryption_changes(mr_iid)
            findings['findings'].extend(encryption_findings)
            
            # Scan dependencies
            dependency_findings = self._analyze_dependency_changes(mr_iid)
            findings['findings'].extend(dependency_findings)
            
            # Aggregate
            for finding in findings['findings']:
                severity = finding.get('severity', 'low')
                findings['summary'][severity] = findings['summary'].get(severity, 0) + 1
            findings['summary']['total_findings'] = len(findings['findings'])
            
        except Exception as e:
            findings['error'] = str(e)
        
        return findings
    
    def _analyze_auth_changes(self, mr_iid: str) -> List[Dict]:
        """Detect authentication/authorization changes"""
        return []
    
    def _analyze_encryption_changes(self, mr_iid: str) -> List[Dict]:
        """Detect encryption configuration changes"""
        return []
    
    def _analyze_dependency_changes(self, mr_iid: str) -> List[Dict]:
        """Detect dependency version updates"""
        return []

def main():
    parser = argparse.ArgumentParser(description='ComplianceBot Scanner')
    parser.add_argument('--mode', choices=['mr', 'full'], default='mr')
    parser.add_argument('--mr-iid', type=int, help='Merge request IID')
    parser.add_argument('--period', default='14d', help='Analysis period')
    
    args = parser.parse_args()
    
    scanner = ComplianceScanner()
    
    if args.mode == 'mr' and args.mr_iid:
        result = scanner.scan_mr(str(args.mr_iid))
        print(json.dumps(result, indent=2))
    
    return 0

if __name__ == '__main__':
    exit(main())
```

---

## KEY ISSUE SUMMARY

**Problem:** `Error: No item files found in 1 of the sources`

**Location:** Files exist and are correct:
- ✅ `agents/compliance-scanner.yaml` (1030 bytes)
- ✅ `agents/compliance-mapper.yaml` (1111 bytes)
- ✅ `agents/evidence-collector.yaml` (1260 bytes)
- ✅ `agents/compliance-reporter.yaml` (1438 bytes)
- ✅ `agents/test-agent.yaml` (205 bytes)
- ✅ `flows/compliance-flow.yaml` (6010 bytes)

**Root Cause Hypothesis:**
The pipeline job that ran was downloading `components/ai-catalog@0.0.10` (OLD VERSION) even though `.gitlab-ci.yml` specifies `catalog-sync@0.0.1`. This suggests:
1. Pipeline cached old component
2. OR old `.gitlab-ci.yml` commit was used
3. OR GitLab runner not using latest pushed code

**Last Commit:**
- HEAD: `45cabcd` - "chore: reorganize folder structure"
- Tag pushed: `v0.0.3`
- All files confirmed in place with correct YAML format

**Next Steps for Investigation:**
1. Verify pipeline execution uses **latest** `.gitlab-ci.yml` from `45cabcd`
2. Check if group/project level includes override the component version
3. Verify `$CI_SERVER_HOST` resolves correctly to official GitLab instance
4. Confirm agent/flow file read permissions in CI container
