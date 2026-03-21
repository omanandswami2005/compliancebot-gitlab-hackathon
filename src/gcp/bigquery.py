# src/gcp/bigquery.py
"""
BigQuery Logger - Logs compliance findings to BigQuery for analytics.
Provides graceful degradation when BigQuery is not available.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from .client import get_gcp_client

logger = logging.getLogger(__name__)


@dataclass
class ComplianceFindingRecord:
    """BigQuery record for a compliance finding."""
    project_id: str
    mr_id: int
    mr_url: str
    control_id: str
    framework: str
    severity: str
    status: str
    title: str
    description: str
    file_path: Optional[str]
    finding_date: str
    compliance_score: int
    evidence_hash: Optional[str] = None
    remediation_steps: Optional[str] = None
    pipeline_id: Optional[int] = None
    remediated_date: Optional[str] = None


class BigQueryLogger:
    """
    Logs compliance findings to BigQuery.
    
    Gracefully handles missing credentials by logging warnings
    and returning success=False without raising exceptions.
    """
    
    def __init__(self):
        self._client = None
        self._table_id = None
        
    def _ensure_client(self) -> bool:
        """Ensure BigQuery client is initialized."""
        if self._client is not None:
            return True
            
        gcp = get_gcp_client()
        
        if not gcp.is_available:
            logger.warning(f"BigQuery not available: {gcp.error_message}")
            return False
        
        try:
            from google.cloud import bigquery
            
            self._client = bigquery.Client(project=gcp.config.project_id)
            self._table_id = f"{gcp.config.project_id}.{gcp.config.bigquery_dataset}.{gcp.config.bigquery_table}"
            
            logger.info(f"BigQuery client initialized for table: {self._table_id}")
            return True
            
        except ImportError:
            logger.error("google-cloud-bigquery package not installed. Run: pip install google-cloud-bigquery")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            return False
    
    def log_findings(
        self,
        findings: List[Dict[str, Any]],
        project_id: str,
        mr_id: int,
        mr_url: str,
        compliance_score: int,
        evidence_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log compliance findings to BigQuery.
        
        Args:
            findings: List of finding dictionaries from the scanner
            project_id: GitLab project ID or path
            mr_id: Merge request IID
            mr_url: Full URL to the merge request
            compliance_score: Overall compliance score (0-100)
            evidence_hash: SHA-256 hash of evidence package
            
        Returns:
            dict: Result with success status and any errors
        """
        if not self._ensure_client():
            return {
                "success": False,
                "error": "BigQuery not available - findings not logged",
                "logged_count": 0,
                "gcp_status": get_gcp_client().get_status()
            }
        
        try:
            rows_to_insert = []
            finding_date = datetime.now(timezone.utc).isoformat()
            
            for finding in findings:
                record = ComplianceFindingRecord(
                    project_id=project_id,
                    mr_id=mr_id,
                    mr_url=mr_url,
                    control_id=finding.get('control_id', finding.get('control_ids', ['UNKNOWN'])[0] if isinstance(finding.get('control_ids'), list) else 'UNKNOWN'),
                    framework=finding.get('framework', self._extract_framework(finding)),
                    severity=finding.get('severity', 'unknown'),
                    status='NEEDS_REVIEW',
                    title=finding.get('title', finding.get('description', '')[:100]),
                    description=finding.get('description', ''),
                    file_path=finding.get('file_path', finding.get('file_paths', [None])[0] if isinstance(finding.get('file_paths'), list) else None),
                    finding_date=finding_date,
                    compliance_score=compliance_score,
                    evidence_hash=evidence_hash,
                    remediation_steps=finding.get('remediation_steps', finding.get('remediation')),
                    pipeline_id=finding.get('pipeline_id')
                )
                rows_to_insert.append(asdict(record))
            
            if not rows_to_insert:
                return {
                    "success": True,
                    "message": "No findings to log",
                    "logged_count": 0
                }
            
            # Insert rows
            errors = self._client.insert_rows_json(self._table_id, rows_to_insert)
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                return {
                    "success": False,
                    "error": f"BigQuery insert errors: {errors}",
                    "logged_count": 0
                }
            
            logger.info(f"Successfully logged {len(rows_to_insert)} findings to BigQuery")
            return {
                "success": True,
                "logged_count": len(rows_to_insert),
                "table_id": self._table_id
            }
            
        except Exception as e:
            logger.error(f"Failed to log findings to BigQuery: {e}")
            return {
                "success": False,
                "error": str(e),
                "logged_count": 0
            }
    
    def _extract_framework(self, finding: Dict[str, Any]) -> str:
        """Extract framework from control IDs."""
        control_ids = finding.get('control_ids', [])
        if not control_ids:
            control_id = finding.get('control_id', '')
            control_ids = [control_id] if control_id else []
        
        for cid in control_ids:
            cid_upper = str(cid).upper()
            if 'SOC2' in cid_upper or cid_upper.startswith('CC'):
                return 'SOC2'
            elif 'ISO' in cid_upper or cid_upper.startswith('A.'):
                return 'ISO27001'
            elif 'PCI' in cid_upper:
                return 'PCI-DSS'
            elif 'HIPAA' in cid_upper:
                return 'HIPAA'
            elif 'ORG' in cid_upper:
                return 'ORG-CUSTOM'
        
        return 'UNKNOWN'
    
    def query_compliance_trend(
        self,
        project_id: str,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Query compliance score trend for a project.
        
        Args:
            project_id: GitLab project ID or path
            days: Number of days to look back
            
        Returns:
            dict: Trend data or error information
        """
        if not self._ensure_client():
            return {
                "success": False,
                "error": "BigQuery not available",
                "data": []
            }
        
        try:
            query = f"""
            SELECT
                DATE(finding_date) as date,
                framework,
                AVG(compliance_score) as avg_score,
                COUNT(*) as finding_count,
                COUNTIF(severity = 'critical') as critical_count,
                COUNTIF(severity = 'high') as high_count
            FROM `{self._table_id}`
            WHERE project_id = @project_id
                AND finding_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            GROUP BY date, framework
            ORDER BY date DESC
            """
            
            job_config = self._client.QueryJobConfig(
                query_parameters=[
                    self._client.ScalarQueryParameter("project_id", "STRING", project_id),
                    self._client.ScalarQueryParameter("days", "INT64", days),
                ]
            )
            
            results = self._client.query(query, job_config=job_config)
            
            data = []
            for row in results:
                data.append({
                    "date": row.date.isoformat() if row.date else None,
                    "framework": row.framework,
                    "avg_score": float(row.avg_score) if row.avg_score else 0,
                    "finding_count": row.finding_count,
                    "critical_count": row.critical_count,
                    "high_count": row.high_count
                })
            
            return {
                "success": True,
                "data": data,
                "project_id": project_id,
                "days": days
            }
            
        except Exception as e:
            logger.error(f"Failed to query compliance trend: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }


# Convenience function
def log_compliance_findings(
    findings: List[Dict[str, Any]],
    project_id: str,
    mr_id: int,
    mr_url: str,
    compliance_score: int,
    evidence_hash: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to log findings to BigQuery.
    
    Creates a BigQueryLogger instance and logs the findings.
    Safe to call even if GCP is not configured.
    """
    bq_logger = BigQueryLogger()
    return bq_logger.log_findings(
        findings=findings,
        project_id=project_id,
        mr_id=mr_id,
        mr_url=mr_url,
        compliance_score=compliance_score,
        evidence_hash=evidence_hash
    )
