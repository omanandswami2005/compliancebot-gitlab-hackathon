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
