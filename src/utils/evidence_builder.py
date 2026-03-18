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
