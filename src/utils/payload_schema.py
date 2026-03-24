"""
Canonical JSON Schema for Compliance Payloads.

This schema defines the standard format for all compliance findings,
enabling consistency between local runners and GitLab pipeline integration.

Can be used with:
- Local runners (manual or automated)
- GitLab CI pipeline (when credentials added)
- Dashboard ingestion
- API imports
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import json


# ============================================================================
# ENUMS (Controlled Vocabularies)
# ============================================================================

class FindingSeverity(str, Enum):
    """Standard severity levels across all frameworks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingStatus(str, Enum):
    """Standard finding status values across all systems."""
    OPEN = "open"
    REMEDIATED = "remediated"
    ACCEPTED = "accepted"  # Risk accepted (waivers)
    FALSE_POSITIVE = "false_positive"  # Not actually a finding


class Framework(str, Enum):
    """Supported compliance frameworks."""
    SOC2 = "SOC 2"
    ISO27001 = "ISO 27001"
    PCIDSS = "PCI-DSS"
    HIPAA = "HIPAA"
    CUSTOM = "Custom"


class FindingType(str, Enum):
    """Categories of findings detected by Scanner agent."""
    SECRET_HARDCODED = "secret_hardcoded"
    ENCRYPTION_WEAK = "encryption_weak"
    AUTH_VULNERABILITY = "auth_vulnerability"
    DEPENDENCY_VULNERABLE = "dependency_vulnerable"
    CONFIG_INSECURE = "config_insecure"
    PROCESS_VIOLATION = "process_violation"
    DATA_EXPOSURE = "data_exposure"
    COMPLIANCE_VIOLATION = "compliance_violation"


class EvidenceType(str, Enum):
    """Types of evidence collected by Evidence Collector agent."""
    MR_METADATA = "mr_metadata"  # Author, reviewers, timestamps
    COMMIT_HISTORY = "commit_history"  # Commits and diffs
    REVIEW_COMMENTS = "review_comments"  # Discussion threads
    PIPELINE_RESULTS = "pipeline_results"  # Scan results
    APPROVAL_CHAIN = "approval_chain"  # Sign-off history
    ACCESS_AUDIT = "access_audit"  # Who accessed what


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Control:
    """Single compliance control (SOC 2, ISO 27001, PCI-DSS, HIPAA)."""
    id: str  # e.g., "SOC2-CC6.1", "ISO27001-A.8.1.1", "PCI-DSS-6.5.1"
    framework: Framework
    description: str  # Human-readable control description
    remediation_url: Optional[str] = None  # Link to remediation guide


@dataclass
class Evidence:
    """Audit trail evidence for non-repudiation."""
    type: EvidenceType
    data: Dict[str, Any]  # Raw evidence data
    collected_at: str  # ISO 8601 timestamp
    collected_by: str = "compliancebot-local"  # Source of evidence
    hash_sha256: Optional[str] = None  # Integrity check


@dataclass
class ComplianceFinding:
    """
    Single compliance finding detected by Scanner agent.
    
    Local representation that can be:
    - Logged to BigQuery locally
    - Sent to GitLab as a work item
    - Reported in compliance dashboard
    - Integrated into pipeline execution
    """
    # Identification
    id: str  # Unique: {project_id}-{mr_id}-{timestamp}-{uuid}
    title: str  # Brief title: "Hardcoded API key in auth.py"
    description: str  # Detailed description
    
    # Scope
    project_id: str  # GitLab project ID or local identifier
    mr_id: int  # Merge request IID (or 0 for non-MR scans)
    
    # Classification
    finding_type: FindingType
    severity: FindingSeverity
    
    # Compliance Mapping
    controls: List[Control] = field(default_factory=list)  # Mapped controls
    frameworks: List[Framework] = field(default_factory=list)  # Derived from controls
    
    # Optional scope
    mr_url: Optional[str] = None  # Full GitLab MR URL
    
    # Status
    status: FindingStatus = FindingStatus.OPEN
    
    # Remediation
    remediation_steps: List[str] = field(default_factory=list)
    remediation_deadline: Optional[str] = None  # ISO 8601
    assigned_to: Optional[str] = None  # Assignee username/email
    
    # Location
    file_path: Optional[str] = None  # e.g., "src/auth.py"
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None  # For context
    
    # Evidence
    evidence: List[Evidence] = field(default_factory=list)
    evidence_hash: Optional[str] = None  # SHA-256 of all evidence
    
    # Scoring
    compliance_score_impact: int = 0  # Points deducted from 100
    
    # Metadata
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    detected_by: str = "scanner-agent"  # Agent name
    tags: List[str] = field(default_factory=list)  # e.g., ["secrets", "pci-dss-required"]


@dataclass
class ComplianceReport:
    """
    Complete compliance scan report.
    
    This is the canonical payload format that moves between:
    - Local runners → GCP archival
    - GitLab artifacts → Dashboard
    - Pipeline execution → Local storage
    """
    # Metadata
    report_id: str  # Unique: {project_id}-{timestamp}-{uuid}
    project_id: str
    project_name: str  # Human-readable name
    scan_type: Literal["mr", "scheduled", "manual"] = "manual"
    
    # Scope
    merge_requests: List[int] = field(default_factory=list)  # MR IIDs scanned
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
    
    # Execution
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_seconds: int = 0
    
    # Results
    findings: List[ComplianceFinding] = field(default_factory=list)
    compliance_score: int = 100  # Start at 100, deduct per finding
    stats: Dict[str, int] = field(default_factory=dict)  # See below
    
    # Frameworks evaluated
    frameworks: List[Framework] = field(default_factory=list)
    
    # Generated by
    generated_by: str = "compliancebot-local"
    agents_executed: List[str] = field(
        default_factory=lambda: ["scanner", "mapper", "evidence-collector", "reporter"]
    )
    
    # Archive destinations
    archived_to: List[str] = field(default_factory=list)  # ["bigquery", "gcs"]
    
    def compute_stats(self) -> None:
        """Recalculate statistics from findings."""
        self.stats = {
            "total_findings": len(self.findings),
            "critical": sum(1 for f in self.findings if f.severity == FindingSeverity.CRITICAL),
            "high": sum(1 for f in self.findings if f.severity == FindingSeverity.HIGH),
            "medium": sum(1 for f in self.findings if f.severity == FindingSeverity.MEDIUM),
            "low": sum(1 for f in self.findings if f.severity == FindingSeverity.LOW),
            "frameworks_covered": len(set(f for finding in self.findings for f in finding.frameworks)),
            "unique_controls": len(set(c.id for finding in self.findings for c in finding.controls)),
        }
        
        # Compute compliance score (100 - sum of impacts)
        self.compliance_score = max(0, 100 - sum(f.compliance_score_impact for f in self.findings))
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self._to_dict(), indent=indent, default=str)
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enum serialization."""
        data = asdict(self)
        
        # Serialize enums
        if data.get("frameworks"):
            data["frameworks"] = [f.value if isinstance(f, Enum) else f for f in data["frameworks"]]
        if data.get("findings"):
            for finding in data["findings"]:
                finding["finding_type"] = finding["finding_type"].value
                finding["severity"] = finding["severity"].value
                finding["status"] = finding["status"].value
                # Controls are already dicts after asdict(), just ensure enums are converted
                if finding.get("controls"):
                    for control in finding["controls"]:
                        if isinstance(control.get("framework"), Enum):
                            control["framework"] = control["framework"].value
                finding["frameworks"] = [f.value if isinstance(f, Enum) else f for f in finding["frameworks"]]
                # Evidence is also already dicts after asdict()
                if finding.get("evidence"):
                    for ev in finding["evidence"]:
                        if isinstance(ev.get("type"), Enum):
                            ev["type"] = ev["type"].value
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComplianceReport":
        """Deserialize from dictionary with enum reconstruction."""
        # Reconstruct enums
        if data.get("frameworks"):
            data["frameworks"] = [Framework(f) if isinstance(f, str) else f for f in data["frameworks"]]
        
        if data.get("findings"):
            findings = []
            for f in data["findings"]:
                f["finding_type"] = FindingType(f["finding_type"]) if isinstance(f["finding_type"], str) else f["finding_type"]
                f["severity"] = FindingSeverity(f["severity"]) if isinstance(f["severity"], str) else f["severity"]
                f["status"] = FindingStatus(f["status"]) if isinstance(f["status"], str) else f["status"]
                f["frameworks"] = [Framework(fw) if isinstance(fw, str) else fw for fw in f.get("frameworks", [])]
                
                # Reconstruct controls and evidence
                controls = [Control(**c) for c in f.get("controls", [])]
                evidence = [Evidence(type=EvidenceType(e["type"]), **{k: v for k, v in e.items() if k != "type"}) for e in f.get("evidence", [])]
                
                f["controls"] = controls
                f["evidence"] = evidence
                
                findings.append(ComplianceFinding(**f))
            
            data["findings"] = findings
        
        return cls(**data)


# ============================================================================
# JSON SCHEMA Export (for documentation and external tools)
# ============================================================================

def get_json_schema() -> Dict[str, Any]:
    """
    Export JSON schema for ComplianceReport.
    Useful for:
    - API documentation
    - External tool integration
    - Dashboard validation
    """
    return {
        "title": "ComplianceReport",
        "description": "Canonical compliance scan report",
        "type": "object",
        "properties": {
            "report_id": {"type": "string", "description": "Unique report identifier"},
            "project_id": {"type": "string", "description": "GitLab project ID or identifier"},
            "project_name": {"type": "string"},
            "scan_type": {"enum": ["mr", "scheduled", "manual"]},
            "merge_requests": {"type": "array", "items": {"type": "integer"}},
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "finding_type": {"enum": [ft.value for ft in FindingType]},
                        "severity": {"enum": [s.value for s in FindingSeverity]},
                        "status": {"enum": [st.value for st in FindingStatus]},
                        "controls": {"type": "array", "items": {"type": "object"}},
                        "frameworks": {"type": "array", "items": {"enum": [f.value for f in Framework]}},
                        "compliance_score_impact": {"type": "integer"},
                    }
                }
            },
            "compliance_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "stats": {"type": "object"},
        },
        "required": [
            "report_id", "project_id", "project_name", "findings",
            "compliance_score", "started_at", "finished_at"
        ]
    }
