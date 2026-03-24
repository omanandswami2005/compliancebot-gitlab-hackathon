"""
Payload builders and converters for compliance findings.

Adapts between:
- Canonical schema (src/utils/payload_schema.py)
- BigQuery rows (src/gcp/bigquery.py)
- GitLab work items/issues
- Dashboard analytics format
"""

from typing import Dict, List, Any, Optional
from dataclasses import asdict
from datetime import datetime, timezone

from src.utils.payload_schema import (
    ComplianceReport,
    ComplianceFinding,
    FindingSeverity,
    FindingStatus,
    Framework,
)


class PayloadConverter:
    """Converts between canonical schema and various destinations."""
    
    @staticmethod
    def to_bigquery_row(finding: ComplianceFinding) -> Dict[str, Any]:
        """
        Convert ComplianceFinding to BigQuery row format.
        
        Returns format compatible with BigQueryLogger.log_findings()
        """
        return {
            "project_id": finding.project_id,
            "mr_id": finding.mr_id,
            "mr_url": finding.mr_url or "",
            "control_ids": [c.id for c in finding.controls],
            "frameworks": [f.value for f in finding.frameworks],
            "severity": finding.severity.value,
            "status": finding.status.value,
            "title": finding.title,
            "description": finding.description,
            "file_path": finding.file_path or "unknown",
            "remediation_steps": "\n".join(finding.remediation_steps) if finding.remediation_steps else "",
            "compliance_score": finding.compliance_score_impact,  # Impact, not overall score
            "evidence_hash": finding.evidence_hash or "",
            "finding_date": finding.detected_at,
            "tags": ",".join(finding.tags) if finding.tags else "",
        }
    
    @staticmethod
    def to_gitlab_issue(finding: ComplianceFinding) -> Dict[str, Any]:
        """
        Convert ComplianceFinding to GitLab issue creation format.
        
        Suitable for POST /projects/:id/issues
        """
        severity_emoji = {
            FindingSeverity.CRITICAL: "🔴",
            FindingSeverity.HIGH: "🟠",
            FindingSeverity.MEDIUM: "🟡",
            FindingSeverity.LOW: "🟢",
        }
        
        # Build description with evidence
        description = f"""
{finding.description}

### Details
- **Type:** {finding.finding_type.value}
- **Detected:** {finding.detected_at}
- **File:** {finding.file_path or 'N/A'}
- **Line:** {finding.line_number or 'N/A'}

### Compliance Controls
"""
        for control in finding.controls:
            description += f"- **{control.framework.value}:** {control.id} - {control.description}\n"
        
        description += "\n### Remediation\n"
        for step in finding.remediation_steps:
            description += f"- {step}\n"
        
        if finding.code_snippet:
            description += f"\n### Code\n```\n{finding.code_snippet}\n```\n"
        
        return {
            "title": f"{severity_emoji[finding.severity]} {finding.title}",
            "description": description,
            "labels": [
                f"severity-{finding.severity.value}",
                "compliance-finding",
            ] + [f"{fw.value.lower()}-finding" for fw in finding.frameworks],
            "assigned_to_id": None,  # Would need username → ID mapping
            "milestone_id": None,
            "weight": {
                FindingSeverity.CRITICAL: 13,
                FindingSeverity.HIGH: 8,
                FindingSeverity.MEDIUM: 5,
                FindingSeverity.LOW: 3,
            }[finding.severity],
        }
    
    @staticmethod
    def to_dashboard_row(finding: ComplianceFinding, report_id: str) -> Dict[str, Any]:
        """
        Convert ComplianceFinding to dashboard analytics row.
        
        Compatible with dashboard/data_loader.py expectations
        """
        return {
            "report_id": report_id,
            "finding_id": finding.id,
            "project_id": finding.project_id,
            "mr_id": finding.mr_id,
            "date": datetime.fromisoformat(finding.detected_at).strftime("%Y-%m-%d"),
            "framework": finding.frameworks[0].value if finding.frameworks else "Unknown",
            "control_id": finding.controls[0].id if finding.controls else "UNKNOWN",
            "severity": finding.severity.value,
            "status": finding.status.value,
            "title": finding.title,
            "description": finding.description,
            "file_path": finding.file_path or "unknown",
            "compliance_score": finding.compliance_score_impact,
            "compliance_score_impact": finding.compliance_score_impact,
        }
    
    @staticmethod
    def from_agent_output(
        agent_finding: Dict[str, Any],
        project_id: str,
        mr_id: int,
        mr_url: Optional[str] = None,
    ) -> ComplianceFinding:
        """
        Convert raw agent output to ComplianceFinding.
        
        Agent output should have:
        {
            "title": "...",
            "description": "...",
            "finding_type": "...",
            "severity": "critical|high|medium|low",
            "control_ids": ["SOC2-CC6.1", ...],
            "remediation_steps": ["...", ...],
            "file_path": "src/auth.py",
            "line_number": 123,
            "code_snippet": "...",
            "tags": ["secret", "auth"],
        }
        """
        from src.utils.payload_schema import (
            ComplianceFinding,
            FindingType,
            Control,
            Evidence,
        )
        
        # Infer frameworks from control IDs
        frameworks = set()
        controls = []
        
        for control_id in agent_finding.get("control_ids", []):
            framework = _infer_framework(control_id)
            frameworks.add(framework)
            controls.append(Control(
                id=control_id,
                framework=framework,
                description="",  # Could load from frameworks/*.json
            ))
        
        # Map severity
        severity = FindingSeverity(
            agent_finding.get("severity", "medium").lower()
        )
        
        # Calculate score impact
        impact_map = {
            FindingSeverity.CRITICAL: 25,
            FindingSeverity.HIGH: 15,
            FindingSeverity.MEDIUM: 10,
            FindingSeverity.LOW: 5,
        }
        
        return ComplianceFinding(
            id=f"{project_id}-{mr_id}-{datetime.now(timezone.utc).timestamp():.0f}",
            title=agent_finding.get("title", "Unnamed finding"),
            description=agent_finding.get("description", ""),
            project_id=project_id,
            mr_id=mr_id,
            mr_url=mr_url,
            finding_type=FindingType(
                agent_finding.get("finding_type", "compliance_violation")
            ),
            severity=severity,
            status=FindingStatus.OPEN,
            controls=controls,
            frameworks=list(frameworks),
            remediation_steps=agent_finding.get("remediation_steps", []),
            file_path=agent_finding.get("file_path"),
            line_number=agent_finding.get("line_number"),
            code_snippet=agent_finding.get("code_snippet"),
            evidence=[],  # Populated separately
            compliance_score_impact=impact_map.get(severity, 10),
            detected_by="scanner-agent",
            tags=agent_finding.get("tags", []),
        )


def _infer_framework(control_id: str) -> Framework:
    """Infer compliance framework from control ID prefix."""
    prefix = control_id.split("-")[0].upper()
    
    if prefix in ("SOC2", "CC"):
        return Framework.SOC2
    elif prefix in ("ISO27001", "A"):
        return Framework.ISO27001
    elif prefix.startswith("PCI"):
        return Framework.PCIDSS
    elif prefix.startswith("HIPAA"):
        return Framework.HIPAA
    else:
        return Framework.CUSTOM


class ReportBuilder:
    """Builder pattern for creating ComplianceReport documents."""
    
    def __init__(self, project_id: str, project_name: str):
        self.project_id = project_id
        self.project_name = project_name
        self.findings: List[ComplianceFinding] = []
        self.mr_ids: List[int] = []
        self.start_time = datetime.now(timezone.utc).isoformat()
        self.scan_type = "manual"
    
    def add_finding(self, finding: ComplianceFinding) -> "ReportBuilder":
        """Add a finding to the report."""
        self.findings.append(finding)
        if finding.mr_id not in self.mr_ids:
            self.mr_ids.append(finding.mr_id)
        return self
    
    def add_findings(self, findings: List[ComplianceFinding]) -> "ReportBuilder":
        """Add multiple findings."""
        for finding in findings:
            self.add_finding(finding)
        return self
    
    def set_scan_type(self, scan_type: str) -> "ReportBuilder":
        """Set scan type (mr, scheduled, manual)."""
        self.scan_type = scan_type
        return self
    
    def build(self) -> ComplianceReport:
        """Build and return the final report."""
        import uuid
        
        report = ComplianceReport(
            report_id=f"{self.project_id}-{datetime.now(timezone.utc).isoformat()}-{uuid.uuid4().hex[:8]}",
            project_id=self.project_id,
            project_name=self.project_name,
            scan_type=self.scan_type,
            merge_requests=self.mr_ids,
            started_at=self.start_time,
            findings=self.findings,
        )
        
        # Compute statistics and score
        report.compute_stats()
        report.finished_at = datetime.now(timezone.utc).isoformat()
        
        return report


class PayloadValidator:
    """Validates compliance payloads against schema."""
    
    @staticmethod
    def validate_finding(finding: ComplianceFinding) -> List[str]:
        """
        Validate a finding object.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not finding.title:
            errors.append("Finding must have a title")
        
        if not finding.description:
            errors.append("Finding must have a description")
        
        if not finding.project_id:
            errors.append("Finding must have a project_id")
        
        if not finding.controls:
            errors.append("Finding must have at least one control mapping")
        
        if not finding.severity:
            errors.append("Finding must have severity")
        
        return errors
    
    @staticmethod
    def validate_report(report: ComplianceReport) -> List[str]:
        """
        Validate a report object.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not report.project_id:
            errors.append("Report must have a project_id")
        
        if not report.project_name:
            errors.append("Report must have a project_name")
        
        if not report.findings:
            errors.append("Warning: Report has no findings")
        
        # Validate each finding
        for i, finding in enumerate(report.findings):
            finding_errors = PayloadValidator.validate_finding(finding)
            for error in finding_errors:
                errors.append(f"Finding #{i}: {error}")
        
        return errors
