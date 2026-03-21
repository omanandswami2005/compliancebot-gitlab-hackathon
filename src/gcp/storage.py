# src/gcp/storage.py
"""
Cloud Storage Uploader - Uploads compliance reports to GCS.
Provides graceful degradation when GCS is not available.
"""

import logging
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Union
from io import BytesIO

from .client import get_gcp_client

logger = logging.getLogger(__name__)


class CloudStorageUploader:
    """
    Uploads compliance reports and evidence to Google Cloud Storage.
    
    Features:
    - PDF report upload with signed URLs
    - JSON evidence package upload
    - Automatic metadata tagging
    - Graceful degradation when GCS is not available
    """
    
    def __init__(self):
        self._client = None
        self._bucket = None
        
    def _ensure_client(self) -> bool:
        """Ensure GCS client is initialized."""
        if self._client is not None:
            return True
            
        gcp = get_gcp_client()
        
        if not gcp.is_available:
            logger.warning(f"Cloud Storage not available: {gcp.error_message}")
            return False
        
        try:
            from google.cloud import storage
            
            self._client = storage.Client(project=gcp.config.project_id)
            self._bucket = self._client.bucket(gcp.config.gcs_bucket)
            
            # Check if bucket exists
            if not self._bucket.exists():
                logger.warning(f"GCS bucket does not exist: {gcp.config.gcs_bucket}")
                logger.info("Creating bucket...")
                self._bucket = self._client.create_bucket(
                    gcp.config.gcs_bucket,
                    location="US"
                )
            
            logger.info(f"Cloud Storage client initialized for bucket: {gcp.config.gcs_bucket}")
            return True
            
        except ImportError:
            logger.error("google-cloud-storage package not installed. Run: pip install google-cloud-storage")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Storage client: {e}")
            return False
    
    def upload_report_pdf(
        self,
        pdf_content: bytes,
        project_id: str,
        mr_id: int,
        compliance_score: int,
        frameworks: list
    ) -> Dict[str, Any]:
        """
        Upload PDF compliance report to GCS.
        
        Args:
            pdf_content: PDF file content as bytes
            project_id: GitLab project ID or path
            mr_id: Merge request IID
            compliance_score: Overall compliance score
            frameworks: List of frameworks assessed
            
        Returns:
            dict: Result with signed URL or error information
        """
        if not self._ensure_client():
            return {
                "success": False,
                "error": "Cloud Storage not available - PDF not uploaded",
                "gcp_status": get_gcp_client().get_status()
            }
        
        try:
            # Generate unique filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            safe_project_id = project_id.replace('/', '_')
            blob_name = f"reports/{safe_project_id}/compliance-report_MR{mr_id}_{timestamp}.pdf"
            
            blob = self._bucket.blob(blob_name)
            
            # Set metadata
            blob.metadata = {
                "project_id": project_id,
                "mr_id": str(mr_id),
                "compliance_score": str(compliance_score),
                "frameworks": ",".join(frameworks),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "content_hash": hashlib.sha256(pdf_content).hexdigest()
            }
            
            # Upload
            blob.upload_from_string(pdf_content, content_type='application/pdf')
            
            # Generate signed URL (valid for 7 days)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET"
            )
            
            logger.info(f"PDF report uploaded to GCS: {blob_name}")
            
            return {
                "success": True,
                "blob_name": blob_name,
                "signed_url": signed_url,
                "expires_in_days": 7,
                "content_hash": blob.metadata["content_hash"]
            }
            
        except Exception as e:
            logger.error(f"Failed to upload PDF to GCS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_evidence_package(
        self,
        evidence: Dict[str, Any],
        project_id: str,
        mr_id: int
    ) -> Dict[str, Any]:
        """
        Upload JSON evidence package to GCS.
        
        Args:
            evidence: Evidence package dictionary
            project_id: GitLab project ID or path
            mr_id: Merge request IID
            
        Returns:
            dict: Result with blob info or error
        """
        if not self._ensure_client():
            return {
                "success": False,
                "error": "Cloud Storage not available - evidence not uploaded",
                "gcp_status": get_gcp_client().get_status()
            }
        
        try:
            # Generate unique filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            safe_project_id = project_id.replace('/', '_')
            blob_name = f"evidence/{safe_project_id}/evidence-package_MR{mr_id}_{timestamp}.json"
            
            blob = self._bucket.blob(blob_name)
            
            # Serialize evidence
            evidence_json = json.dumps(evidence, indent=2, default=str)
            evidence_bytes = evidence_json.encode('utf-8')
            
            # Set metadata
            blob.metadata = {
                "project_id": project_id,
                "mr_id": str(mr_id),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "content_hash": hashlib.sha256(evidence_bytes).hexdigest(),
                "finding_count": str(len(evidence.get('findings', [])))
            }
            
            # Upload
            blob.upload_from_string(evidence_bytes, content_type='application/json')
            
            # Generate signed URL (valid for 7 days)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET"
            )
            
            logger.info(f"Evidence package uploaded to GCS: {blob_name}")
            
            return {
                "success": True,
                "blob_name": blob_name,
                "signed_url": signed_url,
                "expires_in_days": 7,
                "content_hash": blob.metadata["content_hash"]
            }
            
        except Exception as e:
            logger.error(f"Failed to upload evidence to GCS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_reports(
        self,
        project_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        List recent compliance reports for a project.
        
        Args:
            project_id: GitLab project ID or path
            limit: Maximum number of reports to return
            
        Returns:
            dict: List of reports or error
        """
        if not self._ensure_client():
            return {
                "success": False,
                "error": "Cloud Storage not available",
                "reports": []
            }
        
        try:
            safe_project_id = project_id.replace('/', '_')
            prefix = f"reports/{safe_project_id}/"
            
            blobs = list(self._bucket.list_blobs(prefix=prefix, max_results=limit))
            
            reports = []
            for blob in blobs:
                reports.append({
                    "name": blob.name,
                    "size": blob.size,
                    "created": blob.time_created.isoformat() if blob.time_created else None,
                    "metadata": blob.metadata or {}
                })
            
            return {
                "success": True,
                "reports": reports,
                "count": len(reports)
            }
            
        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return {
                "success": False,
                "error": str(e),
                "reports": []
            }


# Convenience functions
def upload_compliance_pdf(
    pdf_content: bytes,
    project_id: str,
    mr_id: int,
    compliance_score: int,
    frameworks: list
) -> Dict[str, Any]:
    """
    Convenience function to upload PDF report.
    Safe to call even if GCP is not configured.
    """
    uploader = CloudStorageUploader()
    return uploader.upload_report_pdf(
        pdf_content=pdf_content,
        project_id=project_id,
        mr_id=mr_id,
        compliance_score=compliance_score,
        frameworks=frameworks
    )


def upload_evidence(
    evidence: Dict[str, Any],
    project_id: str,
    mr_id: int
) -> Dict[str, Any]:
    """
    Convenience function to upload evidence package.
    Safe to call even if GCP is not configured.
    """
    uploader = CloudStorageUploader()
    return uploader.upload_evidence_package(
        evidence=evidence,
        project_id=project_id,
        mr_id=mr_id
    )
