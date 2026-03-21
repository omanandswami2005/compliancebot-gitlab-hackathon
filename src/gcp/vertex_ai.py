# src/gcp/vertex_ai.py
"""
Vertex AI Integration - Generates compliance narratives using Gemini.
Provides graceful degradation when Vertex AI is not available.
"""

import logging
import json
from typing import Dict, Any, Optional, List

from .client import get_gcp_client

logger = logging.getLogger(__name__)


class VertexAINarrative:
    """
    Generates compliance narratives using Google Vertex AI (Gemini).
    
    Features:
    - Executive summary generation
    - Auditor-friendly language
    - Graceful degradation when Vertex AI is not available
    """
    
    # Default model - Gemini 2.5 Flash for speed and cost efficiency
    DEFAULT_MODEL = "gemini-2.0-flash-001"
    
    def __init__(self, model: str = None):
        self._model_name = model or self.DEFAULT_MODEL
        self._model = None
        self._initialized = False
        
    def _ensure_model(self) -> bool:
        """Ensure Vertex AI model is initialized."""
        if self._initialized:
            return self._model is not None
            
        self._initialized = True
        gcp = get_gcp_client()
        
        if not gcp.is_available:
            logger.warning(f"Vertex AI not available: {gcp.error_message}")
            return False
        
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            # Initialize Vertex AI
            vertexai.init(
                project=gcp.config.project_id,
                location=gcp.config.region
            )
            
            self._model = GenerativeModel(self._model_name)
            logger.info(f"Vertex AI initialized with model: {self._model_name}")
            return True
            
        except ImportError:
            logger.error("vertexai package not installed. Run: pip install google-cloud-aiplatform vertexai")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            return False
    
    def generate_executive_summary(
        self,
        findings: List[Dict[str, Any]],
        compliance_score: int,
        frameworks: List[str],
        project_name: str,
        mr_title: str = None
    ) -> Dict[str, Any]:
        """
        Generate an executive summary for compliance findings.
        
        Args:
            findings: List of compliance findings
            compliance_score: Overall compliance score (0-100)
            frameworks: List of frameworks assessed
            project_name: Name of the project
            mr_title: Optional merge request title
            
        Returns:
            dict: Generated narrative or fallback text
        """
        if not self._ensure_model():
            # Return a fallback narrative when Vertex AI is not available
            return self._generate_fallback_summary(
                findings, compliance_score, frameworks, project_name, mr_title
            )
        
        try:
            # Prepare findings summary for the prompt
            severity_counts = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
            
            for finding in findings:
                severity = finding.get('severity', 'low').lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            prompt = f"""You are a compliance auditor writing an executive summary for a software compliance assessment.

Project: {project_name}
{f'Merge Request: {mr_title}' if mr_title else ''}
Compliance Score: {compliance_score}/100
Frameworks Assessed: {', '.join(frameworks)}

Findings Summary:
- Critical: {severity_counts['critical']}
- High: {severity_counts['high']}
- Medium: {severity_counts['medium']}
- Low: {severity_counts['low']}
- Total: {len(findings)}

Top Findings:
{self._format_top_findings(findings[:5])}

Write a professional executive summary (150-200 words) that:
1. States the overall compliance posture
2. Highlights critical issues requiring immediate attention
3. Notes any compliance strengths
4. Provides a brief recommendation

Use formal, auditor-appropriate language. Be concise and factual."""

            response = self._model.generate_content(prompt)
            narrative = response.text
            
            logger.info("Executive summary generated via Vertex AI")
            
            return {
                "success": True,
                "narrative": narrative,
                "model": self._model_name,
                "source": "vertex_ai"
            }
            
        except Exception as e:
            logger.error(f"Vertex AI generation failed: {e}")
            return self._generate_fallback_summary(
                findings, compliance_score, frameworks, project_name, mr_title
            )
    
    def generate_remediation_plan(
        self,
        findings: List[Dict[str, Any]],
        project_name: str
    ) -> Dict[str, Any]:
        """
        Generate a remediation plan for compliance findings.
        
        Args:
            findings: List of compliance findings
            project_name: Name of the project
            
        Returns:
            dict: Remediation plan or fallback
        """
        if not self._ensure_model():
            return {
                "success": False,
                "error": "Vertex AI not available",
                "plan": self._generate_fallback_remediation(findings)
            }
        
        try:
            # Filter to critical and high findings
            priority_findings = [
                f for f in findings 
                if f.get('severity', '').lower() in ['critical', 'high']
            ]
            
            if not priority_findings:
                return {
                    "success": True,
                    "plan": "No critical or high severity findings require immediate remediation.",
                    "source": "no_action_needed"
                }
            
            prompt = f"""You are a security engineer creating a remediation plan for compliance findings.

Project: {project_name}

Priority Findings Requiring Remediation:
{self._format_findings_for_remediation(priority_findings)}

Create a structured remediation plan that includes:
1. Immediate actions (0-24 hours) for critical findings
2. Short-term actions (1-7 days) for high findings
3. Specific technical steps for each finding
4. Verification steps to confirm remediation

Format as a clear, actionable checklist. Be specific and technical."""

            response = self._model.generate_content(prompt)
            plan = response.text
            
            return {
                "success": True,
                "plan": plan,
                "model": self._model_name,
                "source": "vertex_ai",
                "findings_addressed": len(priority_findings)
            }
            
        except Exception as e:
            logger.error(f"Remediation plan generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "plan": self._generate_fallback_remediation(findings)
            }
    
    def _format_top_findings(self, findings: List[Dict[str, Any]]) -> str:
        """Format top findings for the prompt."""
        lines = []
        for i, f in enumerate(findings, 1):
            severity = f.get('severity', 'unknown').upper()
            desc = f.get('description', f.get('title', 'No description'))[:100]
            control = f.get('control_id', f.get('control_ids', ['N/A'])[0] if isinstance(f.get('control_ids'), list) else 'N/A')
            lines.append(f"{i}. [{severity}] {desc} (Control: {control})")
        return '\n'.join(lines) if lines else "No findings to display."
    
    def _format_findings_for_remediation(self, findings: List[Dict[str, Any]]) -> str:
        """Format findings for remediation prompt."""
        lines = []
        for f in findings:
            severity = f.get('severity', 'unknown').upper()
            title = f.get('title', f.get('description', 'Unknown finding'))[:80]
            file_path = f.get('file_path', f.get('file_paths', ['N/A'])[0] if isinstance(f.get('file_paths'), list) else 'N/A')
            remediation = f.get('remediation_steps', f.get('remediation', 'Review and fix'))
            lines.append(f"- [{severity}] {title}\n  File: {file_path}\n  Suggested: {remediation}")
        return '\n'.join(lines)
    
    def _generate_fallback_summary(
        self,
        findings: List[Dict[str, Any]],
        compliance_score: int,
        frameworks: List[str],
        project_name: str,
        mr_title: str = None
    ) -> Dict[str, Any]:
        """Generate a fallback summary when Vertex AI is not available."""
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for f in findings:
            sev = f.get('severity', 'low').lower()
            if sev in severity_counts:
                severity_counts[sev] += 1
        
        # Determine posture
        if compliance_score >= 85:
            posture = "satisfactory"
            status = "meets compliance requirements"
        elif compliance_score >= 70:
            posture = "needs attention"
            status = "has gaps that should be addressed"
        else:
            posture = "unsatisfactory"
            status = "requires immediate remediation"
        
        narrative = f"""## Executive Summary

**Project:** {project_name}
**Compliance Score:** {compliance_score}/100
**Assessment Status:** {posture.title()}

This compliance assessment evaluated the project against {', '.join(frameworks)} frameworks and identified {len(findings)} total findings.

**Findings Breakdown:**
- Critical: {severity_counts['critical']}
- High: {severity_counts['high']}
- Medium: {severity_counts['medium']}
- Low: {severity_counts['low']}

**Assessment:** The project {status}. {"Immediate action is required for critical findings." if severity_counts['critical'] > 0 else ""}{"High-severity findings should be prioritized for remediation." if severity_counts['high'] > 0 else ""}

*Note: This summary was generated without AI enhancement. For detailed narrative analysis, configure GCP Vertex AI credentials.*"""

        return {
            "success": True,
            "narrative": narrative,
            "source": "fallback",
            "gcp_status": get_gcp_client().get_status()
        }
    
    def _generate_fallback_remediation(self, findings: List[Dict[str, Any]]) -> str:
        """Generate fallback remediation plan."""
        priority = [f for f in findings if f.get('severity', '').lower() in ['critical', 'high']]
        
        if not priority:
            return "No critical or high severity findings require immediate remediation."
        
        lines = ["## Remediation Plan\n"]
        lines.append("### Immediate Actions Required\n")
        
        for i, f in enumerate(priority[:10], 1):
            title = f.get('title', f.get('description', 'Finding'))[:60]
            remediation = f.get('remediation_steps', f.get('remediation', 'Review and remediate'))
            lines.append(f"{i}. **{title}**")
            lines.append(f"   - Action: {remediation}\n")
        
        lines.append("\n*Note: For AI-generated detailed remediation steps, configure GCP Vertex AI credentials.*")
        
        return '\n'.join(lines)


# Convenience function
def generate_compliance_narrative(
    findings: List[Dict[str, Any]],
    compliance_score: int,
    frameworks: List[str],
    project_name: str,
    mr_title: str = None
) -> Dict[str, Any]:
    """
    Convenience function to generate compliance narrative.
    Safe to call even if GCP is not configured.
    """
    narrator = VertexAINarrative()
    return narrator.generate_executive_summary(
        findings=findings,
        compliance_score=compliance_score,
        frameworks=frameworks,
        project_name=project_name,
        mr_title=mr_title
    )
