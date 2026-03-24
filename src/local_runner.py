#!/usr/bin/env python3
"""
ComplianceBot Local Runner - Run compliance agents locally.

This tool allows you to:
1. Scan a merge request locally (no GitLab pipeline required)
2. Produce structured compliance reports
3. Archive to GCP (optional, local credentials supported)
4. Generate compliance dashboards and evidence

Usage:
  python -m src.local_runner scan --mr-diff <json-file> --project <id>
  python -m src.local_runner scan --mode demo
  python -m src.local_runner archive --report <json-file> --to bigquery,gcs
  python -m src.local_runner status
"""

import json
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
import uuid

from src.utils.payload_schema import (
    ComplianceReport,
    ComplianceFinding,
    FindingSeverity,
    FindingStatus,
    FindingType,
    Framework,
    Control,
    Evidence,
    EvidenceType,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Agent Implementations (Simplified Local Versions)
# ============================================================================

class MockScanner:
    """Mock scanner for demo/local execution."""
    
    def scan(self, mr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan MR data and return raw findings."""
        diffs = mr_data.get("diffs", [])
        findings = []
        
        # Simple pattern matching for demo
        for diff in diffs:
            diff_text = diff.get("diff", "")
            file_path = diff.get("new_path", "")
            
            # Detect hardcoded secrets
            if any(keyword in diff_text for keyword in ["password", "api_key", "secret", "token"]):
                findings.append({
                    "title": "Potential hardcoded secret detected",
                    "description": f"Found potential secret in {file_path}",
                    "finding_type": FindingType.SECRET_HARDCODED.value,
                    "severity": "critical",
                    "control_ids": ["ISO27001-A.10.1.1", "SOC2-CC6.1"],
                    "remediation_steps": [
                        "Use environment variables instead",
                        "Rotate the exposed secret"
                    ],
                    "file_path": file_path,
                    "tags": ["secrets", "critical"],
                })
            
            # Detect weak encryption
            if any(keyword in diff_text for keyword in ["MD5", "SHA1", "ssl: false"]):
                findings.append({
                    "title": "Weak encryption detected",
                    "description": f"Found weak encryption in {file_path}",
                    "finding_type": FindingType.ENCRYPTION_WEAK.value,
                    "severity": "high",
                    "control_ids": ["ISO27001-A.10.1.1", "PCI-DSS-3.4"],
                    "remediation_steps": ["Use SHA256 or better", "Enable SSL/TLS"],
                    "file_path": file_path,
                    "tags": ["encryption"],
                })
        
        return findings


class MockMapper:
    """Mock mapper for demo/local execution."""
    
    def map_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map findings to compliance controls."""
        # Findings already have controls from scanner
        return findings


class MockEvidenceCollector:
    """Mock evidence collector for demo/local execution."""
    
    def collect(self, mr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect audit evidence."""
        return [
            {
                "type": "mr_metadata",
                "data": {
                    "mr_id": mr_data.get("iid"),
                    "author": mr_data.get("author", {}).get("name", "Unknown"),
                    "created_at": mr_data.get("created_at"),
                    "updated_at": mr_data.get("updated_at"),
                },
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }
        ]


# ============================================================================
# Local Runner Implementation
# ============================================================================

class LocalRunner:
    """Orchestrates local compliance scanning without GitLab integration."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._setup_logging()
        self.scanner = MockScanner()
        self.mapper = MockMapper()
        self.evidence_collector = MockEvidenceCollector()
    
    def _setup_logging(self):
        """Configure logging based on verbosity."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="[%(name)s] %(levelname)s: %(message)s"
        )
    
    def scan_mr(self, mr_data: Dict[str, Any], project_id: str) -> ComplianceReport:
        """
        Scan a merge request and produce a compliance report.
        
        Args:
            mr_data: MR data (can be from API, fixture, or manual JSON)
            project_id: GitLab project ID or local identifier
        
        Returns:
            ComplianceReport with findings
        """
        logger.info(f"Starting compliance scan for project {project_id}")
        
        # Create report container
        report = ComplianceReport(
            report_id=f"{project_id}-{datetime.now(timezone.utc).isoformat()}-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            project_name=mr_data.get("project_name", f"project-{project_id}"),
            scan_type="mr",
            merge_requests=[mr_data.get("iid", 0)],
            branch=mr_data.get("source_branch"),
            commit_sha=mr_data.get("head_commit_sha"),
        )
        
        try:
            # Step 1: Scanner Agent - Detect issues
            logger.info("Running Scanner agent...")
            raw_findings = self.scanner.scan(mr_data)
            logger.info(f"Scanner found {len(raw_findings)} issues")
            
            # Step 2: Mapper Agent - Map to controls
            logger.info("Running Mapper agent...")
            mapped_findings = self.mapper.map_findings(raw_findings)
            logger.info(f"Mapper mapped {len(mapped_findings)} findings to controls")
            
            # Step 3: Evidence Collector - Gather audit trail
            logger.info("Running Evidence Collector agent...")
            evidence_items = self.evidence_collector.collect(mr_data)
            logger.info(f"Evidence Collector gathered {len(evidence_items)} evidence items")
            
            # Step 4: Convert to canonical format
            logger.info("Normalizing findings to canonical format...")
            for mapped_finding in mapped_findings:
                finding = self._normalize_finding(
                    mapped_finding,
                    project_id=project_id,
                    mr_id=mr_data.get("iid", 0),
                    mr_url=mr_data.get("web_url"),
                    evidence=evidence_items,
                )
                report.findings.append(finding)
            
            # Step 5: Compute statistics
            report.compute_stats()
            report.finished_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"✅ Scan complete: {report.compliance_score}/100 score, {report.stats['total_findings']} findings")
            return report
        
        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            raise
    
    def _normalize_finding(
        self,
        raw_finding: Dict[str, Any],
        project_id: str,
        mr_id: int,
        mr_url: Optional[str],
        evidence: List[Dict[str, Any]],
    ) -> ComplianceFinding:
        """Convert raw agent output to ComplianceFinding."""
        
        # Extract control mappings
        controls = []
        frameworks = set()
        for control_id in raw_finding.get("control_ids", []):
            framework = self._infer_framework(control_id)
            frameworks.add(framework)
            controls.append(Control(
                id=control_id,
                framework=framework,
                description=f"Control {control_id}",
            ))
        
        # Determine severity
        severity = FindingSeverity(raw_finding.get("severity", "medium").lower())
        
        # Calculate score impact
        impact_map = {
            FindingSeverity.CRITICAL: 25,
            FindingSeverity.HIGH: 15,
            FindingSeverity.MEDIUM: 10,
            FindingSeverity.LOW: 5,
        }
        compliance_score_impact = impact_map.get(severity, 10)
        
        # Build evidence objects
        evidence_objects = [
            Evidence(
                type=EvidenceType(ev.get("type", "mr_metadata")),
                data=ev.get("data", {}),
                collected_at=ev.get("collected_at", datetime.now(timezone.utc).isoformat()),
                collected_by=ev.get("collected_by", "evidence-collector"),
            )
            for ev in evidence
        ]
        
        return ComplianceFinding(
            id=f"{project_id}-{mr_id}-{uuid.uuid4().hex[:12]}",
            title=raw_finding.get("title", "Unnamed finding"),
            description=raw_finding.get("description", ""),
            project_id=project_id,
            mr_id=mr_id,
            finding_type=FindingType(raw_finding.get("finding_type", "compliance_violation")),
            severity=severity,
            controls=controls,
            frameworks=list(frameworks),
            remediation_steps=raw_finding.get("remediation_steps", []),
            file_path=raw_finding.get("file_path"),
            line_number=raw_finding.get("line_number"),
            code_snippet=raw_finding.get("code_snippet"),
            evidence=evidence_objects,
            compliance_score_impact=compliance_score_impact,
            detected_by="scanner-agent",
            tags=raw_finding.get("tags", []),
            mr_url=mr_url,
        )
    
    @staticmethod
    def _infer_framework(control_id: str) -> Framework:
        """Infer framework from control ID prefix."""
        prefix = control_id.split("-")[0].upper()
        if prefix in ("SOC2", "CC"):
            return Framework.SOC2
        elif prefix in ("ISO27001", "A"):
            return Framework.ISO27001
        elif prefix == "PCI":
            return Framework.PCIDSS
        elif prefix == "HIPAA":
            return Framework.HIPAA
        else:
            return Framework.CUSTOM
    
    def archive_report(
        self,
        report: ComplianceReport,
        destinations: List[str] = ["bigquery"],
    ) -> bool:
        """
        Archive a compliance report (stub for local-only).
        
        Note: Full GCP integration requires GCP credentials to be set
        """
        logger.info(f"Archiving report {report.report_id} to {destinations}")
        
        # For now, just save locally
        report.archived_to = ["local-json"]
        return True
    
    def check_gcp_status(self) -> Dict[str, Any]:
        """Check GCP configuration status."""
        import os
        gcp_project = os.getenv("GCP_PROJECT_ID")
        gcp_key = os.getenv("GCP_SERVICE_ACCOUNT_KEY")
        
        if gcp_project and gcp_key:
            return {
                "available": True,
                "project_id": gcp_project,
                "message": "GCP credentials configured"
            }
        else:
            return {
                "available": False,
                "message": "GCP not configured. Set GCP_PROJECT_ID and GCP_SERVICE_ACCOUNT_KEY env vars.",
                "guide": "See docs/GCP_SETUP.md for instructions"
            }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ComplianceBot Local Runner",
        epilog="See docs/LOCAL_RUNNER.md for detailed guide"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a merge request")
    scan_parser.add_argument("--mr-diff", type=str, help="Path to MR diff JSON file")
    scan_parser.add_argument("--json", type=str, help="Path to MR JSON file")
    scan_parser.add_argument("--project", type=str, default="local", help="Project ID")
    scan_parser.add_argument("--mode", choices=["demo"], help="Use demo/fixture data")
    scan_parser.add_argument("--output", type=str, help="Output JSON file path")
    scan_parser.add_argument("--archive", action="store_true", help="Archive to GCP after scan")
    
    # archive command
    archive_parser = subparsers.add_parser("archive", help="Archive a report to GCP")
    archive_parser.add_argument("--report", type=str, required=True, help="Path to report JSON")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Check GCP status")
    
    args = parser.parse_args()
    
    runner = LocalRunner(verbose=args.verbose)
    
    try:
        if args.command == "scan":
            # Load MR data
            if args.mode == "demo":
                fixture_path = Path(__file__).parent.parent / "tests" / "fixtures" / "sample_mr_diff.json"
                if not fixture_path.exists():
                    logger.error(f"Demo fixture not found: {fixture_path}")
                    return 1
                with open(fixture_path) as f:
                    mr_data = json.load(f)
                logger.info(f"Loaded demo MR from {fixture_path}")
            elif args.mr_diff:
                with open(args.mr_diff) as f:
                    mr_data = json.load(f)
                logger.info(f"Loaded MR diff from {args.mr_diff}")
            elif args.json:
                with open(args.json) as f:
                    mr_data = json.load(f)
                logger.info(f"Loaded MR JSON from {args.json}")
            else:
                parser.error("Must specify --mr-diff, --json, or --mode demo")
            
            # Scan
            report = runner.scan_mr(mr_data, args.project)
            
            # Output
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(report.to_json())
                logger.info(f"Report saved to {output_path}")
            else:
                print("\n" + "="*80)
                print(report.to_json())
                print("="*80 + "\n")
            
            # Archive if requested
            if args.archive:
                runner.archive_report(report)
            
            return 0
        
        elif args.command == "archive":
            # Load and archive existing report
            with open(args.report) as f:
                report_data = json.load(f)
            report = ComplianceReport.from_dict(report_data)
            
            success = runner.archive_report(report)
            
            return 0 if success else 1
        
        elif args.command == "status":
            status = runner.check_gcp_status()
            print("\n🔧 GCP Integration Status")
            print("="*50)
            for key, value in status.items():
                print(f"  {key}: {value}")
            print("="*50 + "\n")
            
            if status.get("available"):
                print("✅ GCP is configured and ready for archival")
            else:
                print("ℹ️  GCP is not configured (optional for demo)")
                print(f"    {status.get('message')}")
            
            return 0
        
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())



class LocalRunner:
    """Orchestrates local compliance scanning without GitLab integration."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._setup_logging()
        self.scanner = ComplianceScanner()
        self.mapper = ComplianceMapper()
        self.evidence_collector = EvidenceCollector()
        self.bq_logger = BigQueryLogger()
        self.gcs_logger = CloudStorageLogger()
    
    def _setup_logging(self):
        """Configure logging based on verbosity."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="[%(name)s] %(levelname)s: %(message)s"
        )
    
    def scan_mr(self, mr_data: Dict[str, Any], project_id: str) -> ComplianceReport:
        """
        Scan a merge request and produce a compliance report.
        
        Args:
            mr_data: MR data (can be from API, fixture, or manual JSON)
            project_id: GitLab project ID or local identifier
        
        Returns:
            ComplianceReport with findings
        """
        logger.info(f"Starting compliance scan for project {project_id}")
        
        # Create report container
        report = ComplianceReport(
            report_id=f"{project_id}-{datetime.now(timezone.utc).isoformat()}-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            project_name=mr_data.get("project_name", f"project-{project_id}"),
            scan_type="mr",
            merge_requests=[mr_data.get("iid", 0)],
            branch=mr_data.get("source_branch"),
            commit_sha=mr_data.get("head_commit_sha"),
        )
        
        try:
            # Step 1: Scanner Agent - Detect issues
            logger.info("Running Scanner agent...")
            raw_findings = self.scanner.scan(mr_data)
            logger.info(f"Scanner found {len(raw_findings)} issues")
            
            # Step 2: Mapper Agent - Map to controls
            logger.info("Running Mapper agent...")
            mapped_findings = self.mapper.map_findings(raw_findings)
            logger.info(f"Mapper mapped {len(mapped_findings)} findings to controls")
            
            # Step 3: Evidence Collector - Gather audit trail
            logger.info("Running Evidence Collector agent...")
            evidence_items = self.evidence_collector.collect(mr_data)
            logger.info(f"Evidence Collector gathered {len(evidence_items)} evidence items")
            
            # Step 4: Convert to canonical format
            logger.info("Normalizing findings to canonical format...")
            for mapped_finding in mapped_findings:
                finding = self._normalize_finding(
                    mapped_finding,
                    project_id=project_id,
                    mr_id=mr_data.get("iid", 0),
                    mr_url=mr_data.get("web_url"),
                    evidence=evidence_items,
                )
                report.findings.append(finding)
            
            # Step 5: Compute statistics
            report.compute_stats()
            report.finished_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"✅ Scan complete: {report.compliance_score}/100 score, {report.stats['total_findings']} findings")
            return report
        
        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            raise
    
    def _normalize_finding(
        self,
        raw_finding: Dict[str, Any],
        project_id: str,
        mr_id: int,
        mr_url: Optional[str],
        evidence: List[Dict[str, Any]],
    ) -> ComplianceFinding:
        """Convert raw agent output to ComplianceFinding."""
        
        # Extract control mappings
        controls = []
        frameworks = set()
        for control_id in raw_finding.get("control_ids", []):
            framework = self._infer_framework(control_id)
            frameworks.add(framework)
            controls.append(Control(
                id=control_id,
                framework=framework,
                description=f"Control {control_id}",  # Could load from JSON files
            ))
        
        # Determine severity
        severity = FindingSeverity(raw_finding.get("severity", "medium").lower())
        
        # Calculate score impact
        impact_map = {
            FindingSeverity.CRITICAL: 25,
            FindingSeverity.HIGH: 15,
            FindingSeverity.MEDIUM: 10,
            FindingSeverity.LOW: 5,
        }
        compliance_score_impact = impact_map.get(severity, 10)
        
        # Build evidence objects
        evidence_objects = [
            Evidence(
                type=EvidenceType(ev.get("type", "mr_metadata")),
                data=ev.get("data", {}),
                collected_at=ev.get("collected_at", datetime.now(timezone.utc).isoformat()),
                collected_by=ev.get("collected_by", "evidence-collector"),
            )
            for ev in evidence
        ]
        
        return ComplianceFinding(
            id=f"{project_id}-{mr_id}-{uuid.uuid4().hex[:12]}",
            title=raw_finding.get("title", "Unnamed finding"),
            description=raw_finding.get("description", ""),
            project_id=project_id,
            mr_id=mr_id,
            mr_url=mr_url,
            finding_type=FindingType(raw_finding.get("finding_type", "compliance_violation")),
            severity=severity,
            status=FindingStatus.OPEN,
            controls=controls,
            frameworks=list(frameworks),
            remediation_steps=raw_finding.get("remediation_steps", []),
            file_path=raw_finding.get("file_path"),
            line_number=raw_finding.get("line_number"),
            code_snippet=raw_finding.get("code_snippet"),
            evidence=evidence_objects,
            compliance_score_impact=compliance_score_impact,
            detected_by="scanner-agent",
            tags=raw_finding.get("tags", []),
        )
    
    @staticmethod
    def _infer_framework(control_id: str) -> Framework:
        """Infer framework from control ID prefix."""
        prefix = control_id.split("-")[0].upper()
        if prefix in ("SOC2", "CC"):
            return Framework.SOC2
        elif prefix in ("ISO27001", "A"):
            return Framework.ISO27001
        elif prefix == "PCI":
            return Framework.PCIDSS
        elif prefix == "HIPAA":
            return Framework.HIPAA
        else:
            return Framework.CUSTOM
    
    def archive_report(
        self,
        report: ComplianceReport,
        destinations: List[str] = ["bigquery", "gcs"],
    ) -> bool:
        """
        Archive a compliance report to GCP.
        
        Args:
            report: ComplianceReport to archive
            destinations: List of ["bigquery", "gcs"] to archive to
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Archiving report {report.report_id} to {destinations}")
        
        archived = []
        
        if "bigquery" in destinations:
            logger.info("Uploading findings to BigQuery...")
            try:
                for finding in report.findings:
                    # Convert ComplianceFinding to BigQuery format
                    self.bq_logger.log_findings({
                        "project_id": finding.project_id,
                        "mr_id": finding.mr_id,
                        "mr_url": finding.mr_url,
                        "title": finding.title,
                        "description": finding.description,
                        "severity": finding.severity.value,
                        "status": finding.status.value,
                        "control_ids": [c.id for c in finding.controls],
                        "file_path": finding.file_path,
                        "remediation_steps": finding.remediation_steps,
                    })
                archived.append("bigquery")
                logger.info("✅ BigQuery upload complete")
            except Exception as e:
                logger.error(f"BigQuery archival failed: {e}")
        
        if "gcs" in destinations:
            logger.info("Uploading report to Cloud Storage...")
            try:
                report_json = report.to_json()
                report_path = f"reports/{report.report_id}.json"
                self.gcs_logger.upload_report(report_path, report_json)
                archived.append("gcs")
                logger.info(f"✅ Cloud Storage upload complete: {report_path}")
            except Exception as e:
                logger.error(f"Cloud Storage archival failed: {e}")
        
        report.archived_to = archived
        return len(archived) > 0
    
    def check_gcp_status(self) -> Dict[str, Any]:
        """Check GCP configuration and connectivity."""
        try:
            client = get_gcp_client()
            return {
                "available": True,
                "project_id": client.project_id if client else "unknown",
                "services": {
                    "bigquery": self.bq_logger._ensure_client(),
                    "gcs": self.gcs_logger._ensure_client() is not None,
                }
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "message": "GCP not configured. Set GCP_PROJECT_ID and GCP_SERVICE_ACCOUNT_KEY env vars."
            }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ComplianceBot Local Runner",
        epilog="For detailed docs: https://github.com/compliancebot/local-runner"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a merge request")
    scan_parser.add_argument("--mr-diff", type=str, help="Path to MR diff JSON file")
    scan_parser.add_argument("--json", type=str, help="Path to MR JSON file")
    scan_parser.add_argument("--project", type=str, default="local", help="Project ID")
    scan_parser.add_argument("--mode", choices=["demo"], help="Use demo/fixture data")
    scan_parser.add_argument("--output", type=str, help="Output JSON file path")
    scan_parser.add_argument("--archive", action="store_true", help="Archive to GCP after scan")
    
    # archive command
    archive_parser = subparsers.add_parser("archive", help="Archive a report to GCP")
    archive_parser.add_argument("--report", type=str, required=True, help="Path to report JSON")
    archive_parser.add_argument("--to", type=str, default="bigquery,gcs", help="Destinations")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Check GCP status")
    
    args = parser.parse_args()
    
    runner = LocalRunner(verbose=args.verbose)
    
    try:
        if args.command == "scan":
            # Load MR data
            if args.mode == "demo":
                fixture_path = Path(__file__).parent / "fixtures" / "sample_mr_diff.json"
                with open(fixture_path) as f:
                    mr_data = json.load(f)
                logger.info(f"Loaded demo MR from {fixture_path}")
            elif args.mr_diff:
                with open(args.mr_diff) as f:
                    mr_data = json.load(f)
                logger.info(f"Loaded MR diff from {args.mr_diff}")
            elif args.json:
                with open(args.json) as f:
                    mr_data = json.load(f)
                logger.info(f"Loaded MR JSON from {args.json}")
            else:
                parser.error("Must specify --mr-diff, --json, or --mode demo")
            
            # Scan
            report = runner.scan_mr(mr_data, args.project)
            
            # Output
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(report.to_json())
                logger.info(f"Report saved to {output_path}")
            else:
                print("\n" + "="*80)
                print(report.to_json())
                print("="*80 + "\n")
            
            # Archive if requested
            if args.archive:
                runner.archive_report(report)
            
            return 0 if report.compliance_score >= 0 else 1
        
        elif args.command == "archive":
            # Load and archive existing report
            with open(args.report) as f:
                report_data = json.load(f)
            report = ComplianceReport.from_dict(report_data)
            
            destinations = args.to.split(",")
            success = runner.archive_report(report, destinations)
            
            return 0 if success else 1
        
        elif args.command == "status":
            status = runner.check_gcp_status()
            print("\n🔧 GCP Integration Status")
            print("="*50)
            for key, value in status.items():
                print(f"  {key}: {value}")
            print("="*50 + "\n")
            
            if status.get("available"):
                print("✅ GCP is configured and ready for archival")
            else:
                print("⚠️  GCP is not configured")
                print(f"Error: {status.get('error')}")
                print("\nTo enable GCP integration:")
                print("  1. Create a GCP project and service account")
                print("  2. Enable BigQuery, Cloud Storage, and Vertex AI APIs")
                print("  3. Set environment variables:")
                print("     export GCP_PROJECT_ID=<project-id>")
                print("     export GCP_SERVICE_ACCOUNT_KEY=<base64-encoded-key>")
            
            return 0 if status.get("available") else 1
        
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
