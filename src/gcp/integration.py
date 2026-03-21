# src/gcp/integration.py
"""
GCP Integration Orchestrator - Main entry point for GCP operations.
Coordinates BigQuery logging, Cloud Storage uploads, and Vertex AI narratives.
"""

import logging
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from io import BytesIO

from .client import get_gcp_client, GCPClient
from .bigquery import BigQueryLogger, log_compliance_findings
from .storage import CloudStorageUploader, upload_compliance_pdf, upload_evidence
from .vertex_ai import VertexAINarrative, generate_compliance_narrative

logger = logging.getLogger(__name__)


class GCPIntegration:
    """
    Main orchestrator for GCP integration.
    
    Provides a single interface for all GCP operations with:
    - Graceful degradation when GCP is not configured
    - Comprehensive status reporting
    - PDF report generation and upload
    - Evidence archival
    - Compliance analytics
    """
    
    def __init__(self):
        self._gcp_client = get_gcp_client()
        self._bq_logger = BigQueryLogger()
        self._storage = CloudStorageUploader()
        self._vertex = VertexAINarrative()
    
    @property
    def is_available(self) -> bool:
        """Check if GCP integration is fully available."""
        return self._gcp_client.is_available
    
    @property
    def is_configured(self) -> bool:
        """Check if GCP is configured (may not have credentials)."""
        return self._gcp_client.is_configured
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive GCP integration status."""
        return self._gcp_client.get_status()
    
    def process_compliance_results(
        self,
        findings: List[Dict[str, Any]],
        compliance_score: int,
        frameworks: List[str],
        project_id: str,
        project_name: str,
        mr_id: int,
        mr_url: str,
        mr_title: str = None,
        evidence_package: Dict[str, Any] = None,
        generate_pdf: bool = True
    ) -> Dict[str, Any]:
        """
        Process compliance results and archive to GCP.
        
        This is the main entry point for GCP integration. It:
        1. Generates an AI narrative (if Vertex AI available)
        2. Logs findings to BigQuery (if available)
        3. Uploads evidence to Cloud Storage (if available)
        4. Generates and uploads PDF report (if requested and available)
        
        All operations are optional and fail gracefully.
        
        Args:
            findings: List of compliance findings
            compliance_score: Overall compliance score (0-100)
            frameworks: List of frameworks assessed
            project_id: GitLab project ID or path
            project_name: Human-readable project name
            mr_id: Merge request IID
            mr_url: Full URL to the merge request
            mr_title: Optional merge request title
            evidence_package: Optional evidence package dict
            generate_pdf: Whether to generate and upload PDF
            
        Returns:
            dict: Comprehensive results from all operations
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gcp_available": self.is_available,
            "gcp_configured": self.is_configured,
            "operations": {}
        }
        
        # Calculate evidence hash
        evidence_hash = None
        if evidence_package:
            evidence_json = json.dumps(evidence_package, sort_keys=True, default=str)
            evidence_hash = hashlib.sha256(evidence_json.encode()).hexdigest()
        
        # 1. Generate AI narrative
        logger.info("Generating compliance narrative...")
        narrative_result = self._vertex.generate_executive_summary(
            findings=findings,
            compliance_score=compliance_score,
            frameworks=frameworks,
            project_name=project_name,
            mr_title=mr_title
        )
        results["operations"]["narrative"] = narrative_result
        
        # 2. Log to BigQuery
        logger.info("Logging findings to BigQuery...")
        bq_result = self._bq_logger.log_findings(
            findings=findings,
            project_id=project_id,
            mr_id=mr_id,
            mr_url=mr_url,
            compliance_score=compliance_score,
            evidence_hash=evidence_hash
        )
        results["operations"]["bigquery"] = bq_result
        
        # 3. Upload evidence to Cloud Storage
        if evidence_package:
            logger.info("Uploading evidence package to Cloud Storage...")
            evidence_result = self._storage.upload_evidence_package(
                evidence=evidence_package,
                project_id=project_id,
                mr_id=mr_id
            )
            results["operations"]["evidence_upload"] = evidence_result
        
        # 4. Generate and upload PDF
        if generate_pdf:
            logger.info("Generating PDF report...")
            pdf_result = self._generate_and_upload_pdf(
                findings=findings,
                compliance_score=compliance_score,
                frameworks=frameworks,
                project_id=project_id,
                project_name=project_name,
                mr_id=mr_id,
                mr_url=mr_url,
                mr_title=mr_title,
                narrative=narrative_result.get("narrative", ""),
                evidence_hash=evidence_hash
            )
            results["operations"]["pdf_report"] = pdf_result
        
        # Summarize results
        results["summary"] = self._summarize_results(results["operations"])
        
        return results
    
    def _generate_and_upload_pdf(
        self,
        findings: List[Dict[str, Any]],
        compliance_score: int,
        frameworks: List[str],
        project_id: str,
        project_name: str,
        mr_id: int,
        mr_url: str,
        mr_title: str,
        narrative: str,
        evidence_hash: str
    ) -> Dict[str, Any]:
        """Generate PDF report and upload to GCS."""
        try:
            pdf_content = self._generate_pdf(
                findings=findings,
                compliance_score=compliance_score,
                frameworks=frameworks,
                project_name=project_name,
                mr_id=mr_id,
                mr_url=mr_url,
                mr_title=mr_title,
                narrative=narrative,
                evidence_hash=evidence_hash
            )
            
            if pdf_content:
                return self._storage.upload_report_pdf(
                    pdf_content=pdf_content,
                    project_id=project_id,
                    mr_id=mr_id,
                    compliance_score=compliance_score,
                    frameworks=frameworks
                )
            else:
                return {
                    "success": False,
                    "error": "PDF generation failed - reportlab may not be installed"
                }
                
        except Exception as e:
            logger.error(f"PDF generation/upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_pdf(
        self,
        findings: List[Dict[str, Any]],
        compliance_score: int,
        frameworks: List[str],
        project_name: str,
        mr_id: int,
        mr_url: str,
        mr_title: str,
        narrative: str,
        evidence_hash: str
    ) -> Optional[bytes]:
        """Generate PDF report content."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, 
                TableStyle, PageBreak
            )
            from reportlab.lib import colors
        except ImportError:
            logger.warning("reportlab not installed - PDF generation skipped")
            return None
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1f4788'),
            spaceAfter=20,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            spaceBefore=15,
            spaceAfter=10
        )
        
        # Title
        story.append(Paragraph("🛡️ Compliance Assessment Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata table
        score_color = '#27ae60' if compliance_score >= 85 else '#f39c12' if compliance_score >= 70 else '#e74c3c'
        meta_data = [
            ["Project", project_name],
            ["Merge Request", f"!{mr_id}" + (f" - {mr_title}" if mr_title else "")],
            ["Compliance Score", f"{compliance_score}/100"],
            ["Frameworks", ", ".join(frameworks)],
            ["Generated", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")],
            ["Evidence Hash", evidence_hash[:16] + "..." if evidence_hash else "N/A"]
        ]
        
        meta_table = Table(meta_data, colWidths=[1.5*inch, 5*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 2), (1, 2), HexColor(score_color)),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        # Clean narrative for PDF
        clean_narrative = narrative.replace('##', '').replace('**', '').replace('*', '')
        for para in clean_narrative.split('\n\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Findings Summary
        story.append(Paragraph("Findings Summary", heading_style))
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for f in findings:
            sev = f.get('severity', 'low').lower()
            if sev in severity_counts:
                severity_counts[sev] += 1
        
        findings_data = [
            ["Severity", "Count"],
            ["Critical", str(severity_counts['critical'])],
            ["High", str(severity_counts['high'])],
            ["Medium", str(severity_counts['medium'])],
            ["Low", str(severity_counts['low'])],
            ["Total", str(len(findings))]
        ]
        
        findings_table = Table(findings_data, colWidths=[2*inch, 1*inch])
        findings_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, 1), HexColor('#ffebee')),  # Critical - red bg
            ('BACKGROUND', (0, 2), (-1, 2), HexColor('#fff3e0')),  # High - orange bg
            ('BACKGROUND', (0, 3), (-1, 3), HexColor('#fffde7')),  # Medium - yellow bg
            ('BACKGROUND', (0, 4), (-1, 4), HexColor('#e8f5e9')),  # Low - green bg
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(findings_table)
        
        # Top Findings Detail
        if findings:
            story.append(PageBreak())
            story.append(Paragraph("Top Findings Detail", heading_style))
            
            for i, finding in enumerate(findings[:10], 1):
                severity = finding.get('severity', 'unknown').upper()
                title = finding.get('title', finding.get('description', 'Finding'))[:80]
                control = finding.get('control_id', 
                    finding.get('control_ids', ['N/A'])[0] if isinstance(finding.get('control_ids'), list) else 'N/A'
                )
                
                story.append(Paragraph(
                    f"<b>{i}. [{severity}] {title}</b>",
                    styles['BodyText']
                ))
                story.append(Paragraph(
                    f"Control: {control}",
                    styles['BodyText']
                ))
                story.append(Spacer(1, 0.1*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            "<i>Generated by ComplianceBot Flow | GitLab Duo Agent Platform</i>",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
        ))
        
        # Build PDF
        doc.build(story)
        return buffer.getvalue()
    
    def _summarize_results(self, operations: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize operation results."""
        successful = []
        failed = []
        skipped = []
        
        for op_name, result in operations.items():
            if result.get("success"):
                successful.append(op_name)
            elif "not available" in str(result.get("error", "")).lower():
                skipped.append(op_name)
            else:
                failed.append(op_name)
        
        return {
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "total_operations": len(operations),
            "success_rate": len(successful) / max(len(operations), 1)
        }


# Convenience function for simple usage
def archive_compliance_results(
    findings: List[Dict[str, Any]],
    compliance_score: int,
    frameworks: List[str],
    project_id: str,
    project_name: str,
    mr_id: int,
    mr_url: str,
    mr_title: str = None,
    evidence_package: Dict[str, Any] = None,
    generate_pdf: bool = True
) -> Dict[str, Any]:
    """
    Archive compliance results to GCP.
    
    This is the main convenience function for GCP integration.
    Safe to call even if GCP is not configured - will return
    status information about what was skipped.
    
    Args:
        findings: List of compliance findings
        compliance_score: Overall compliance score (0-100)
        frameworks: List of frameworks assessed
        project_id: GitLab project ID or path
        project_name: Human-readable project name
        mr_id: Merge request IID
        mr_url: Full URL to the merge request
        mr_title: Optional merge request title
        evidence_package: Optional evidence package dict
        generate_pdf: Whether to generate and upload PDF
        
    Returns:
        dict: Results from all GCP operations
    """
    integration = GCPIntegration()
    return integration.process_compliance_results(
        findings=findings,
        compliance_score=compliance_score,
        frameworks=frameworks,
        project_id=project_id,
        project_name=project_name,
        mr_id=mr_id,
        mr_url=mr_url,
        mr_title=mr_title,
        evidence_package=evidence_package,
        generate_pdf=generate_pdf
    )


def get_gcp_status() -> Dict[str, Any]:
    """
    Get GCP integration status.
    
    Returns:
        dict: Status information about GCP configuration
    """
    return get_gcp_client().get_status()
