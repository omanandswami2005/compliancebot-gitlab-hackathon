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

    def _analyze_dependency_change(self, change: dict) -> List[ComplianceFinding]:
        """Analyze dependency-related code changes."""
        return [ComplianceFinding(
            control_id="SOC2-CC7.1",
            severity="medium",
            description=f"Dependency file modified: {change.get('new_path')}",
            evidence_type="dependency",
            file_path=change.get("new_path", ""),
            remediation="Ensure dependency updates are reviewed for known vulnerabilities.",
            framework="SOC2"
        )]

    def _analyze_encryption_change(self, change: dict) -> List[ComplianceFinding]:
        """Analyze encryption-related code changes."""
        return [ComplianceFinding(
            control_id="SOC2-CC6.7",
            severity="high",
            description=f"Encryption logic modified in {change.get('new_path')}",
            evidence_type="code_change",
            file_path=change.get("new_path", ""),
            remediation="Review with security team. Ensure encryption meets standards.",
            framework="SOC2"
        )]

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
