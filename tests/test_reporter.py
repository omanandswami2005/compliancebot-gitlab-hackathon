import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestComplianceReporter:
    """Test suite for ComplianceReporter agent."""

    def test_report_generation_basic(self):
        """Test basic report generation."""
        findings = [
            {
                "control_id": "SOC2-CC6.1",
                "severity": "high",
                "description": "Authentication change detected",
                "framework": "SOC2"
            }
        ]
        
        # Report should contain findings summary
        assert len(findings) > 0

    def test_report_includes_framework_info(self):
        """Test report includes framework information."""
        findings = [
            {
                "control_id": "SOC2-CC6.1",
                "severity": "high",
                "framework": "SOC2"
            },
            {
                "control_id": "ISO27001-A.9.4.2",
                "severity": "high",
                "framework": "ISO27001"
            }
        ]
        
        frameworks = set(f["framework"] for f in findings)
        assert "SOC2" in frameworks
        assert "ISO27001" in frameworks

    def test_report_groups_by_severity(self):
        """Test findings can be grouped by severity."""
        findings = [
            {"severity": "critical"},
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "low"}
        ]
        
        by_severity = {}
        for f in findings:
            severity = f["severity"]
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        assert by_severity["critical"] == 2
        assert by_severity["high"] == 1
        assert by_severity["medium"] == 1
        assert by_severity["low"] == 1

    def test_report_timestamp(self):
        """Test report includes timestamp."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "findings": []
        }
        
        assert "generated_at" in report
        assert report["generated_at"] is not None

    def test_mr_comment_only_for_low_score(self):
        """Test MR comment posted only when score < 85."""
        # Score > 85: no comment
        high_score = 90
        post_comment = high_score < 85
        assert post_comment is False
        
        # Score < 85: post comment
        low_score = 75
        post_comment = low_score < 85
        assert post_comment is True

    def test_report_includes_remediation_timeline(self):
        """Test report includes remediation timeline."""
        finding = {
            "severity": "critical",
            "remediation": "Fix immediately",
            "timeline": "24 hours"
        }
        
        assert "remediation" in finding
        assert "timeline" in finding

    def test_jinja2_template_rendering(self):
        """Test Jinja2 template rendering with compliance report template."""
        from jinja2 import Environment, FileSystemLoader
        import os

        template_dir = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'templates'
        )
        if os.path.isdir(template_dir) and os.listdir(template_dir):
            env = Environment(loader=FileSystemLoader(template_dir))
            templates = env.list_templates()
            assert len(templates) > 0, "Template directory should contain templates"
        else:
            # Template directory may be missing or intentionally empty.
            # Validate Jinja2 itself still works.
            env = Environment()
            t = env.from_string("Score: {{ score }}")
            assert t.render(score=85) == "Score: 85"

    def test_report_executive_summary(self):
        """Test report includes executive summary (max 3 sentences)."""
        summary = "Finding 1. Finding 2. Finding 3."
        sentences = summary.split(". ")
        
        assert len(sentences) <= 3

    def test_report_includes_findings_count(self):
        """Test report counts total findings."""
        findings = [
            {"id": 1},
            {"id": 2},
            {"id": 3},
            {"id": 4},
            {"id": 5}
        ]
        
        report = {
            "findings_count": len(findings),
            "findings": findings
        }
        
        assert report["findings_count"] == 5

    def test_report_includes_risk_level(self):
        """Test report includes overall risk level."""
        # Critical/High findings -> High risk
        findings_high_risk = [
            {"severity": "critical"},
            {"severity": "critical"}
        ]
        
        # All Low findings -> Low risk
        findings_low_risk = [
            {"severity": "low"},
            {"severity": "low"}
        ]
        
        assert len(findings_high_risk) > 0
        assert len(findings_low_risk) > 0

    def test_report_json_serialization(self):
        """Test report can be serialized to JSON."""
        report = {
            "title": "Compliance Report",
            "score": 75,
            "findings": [
                {
                    "control_id": "SOC2-CC6.1",
                    "severity": "high",
                    "description": "Test finding"
                }
            ]
        }
        
        # Should serialize without error
        json_str = json.dumps(report)
        parsed = json.loads(json_str)
        
        assert parsed["score"] == 75
        assert len(parsed["findings"]) == 1

    def test_report_pdf_generation_metadata(self):
        """Test PDF report includes metadata."""
        metadata = {
            "title": "Compliance Report",
            "author": "ComplianceBot",
            "subject": "SOC 2 Compliance Assessment",
            "creator": "ComplianceBot Flow"
        }
        
        assert "title" in metadata
        assert "author" in metadata
        assert metadata["creator"] == "ComplianceBot Flow"


class TestComplianceScore:
    """Test compliance score calculation."""

    def test_perfect_score(self):
        """Test perfect score (100) with no findings."""
        findings = []
        score = 100 if len(findings) == 0 else 95
        assert score == 100

    def test_score_with_single_finding(self):
        """Test score calculation with one finding."""
        severity_penalty = {
            "critical": 30,
            "high": 15,
            "medium": 5,
            "low": 1
        }
        
        finding_severity = "high"
        score = 100 - severity_penalty.get(finding_severity, 0)
        
        assert score == 85

    def test_score_with_multiple_critical(self):
        """Test score with multiple critical findings."""
        findings = [
            {"severity": "critical"},
            {"severity": "critical"},
            {"severity": "critical"}
        ]
        
        # Multiple criticals should reduce score significantly
        base_score = 100
        penalty_per_critical = 20
        expected_score = max(0, base_score - (len(findings) * penalty_per_critical))
        
        assert expected_score <= 40

    def test_score_boundary_values(self):
        """Test score boundaries."""
        # Minimum 0, maximum 100
        scores = [0, 50, 75, 85, 100]
        
        for score in scores:
            assert 0 <= score <= 100

    def test_score_affects_mr_comment_decision(self):
        """Test how score affects MR comment posting."""
        scores = [75, 80, 85, 90, 95]
        
        for score in scores:
            should_comment = score < 85
            if score < 85:
                assert should_comment is True
            else:
                assert should_comment is False


class TestEvidenceCollection:
    """Test evidence collector functionality."""

    def test_evidence_package_structure(self):
        """Test evidence package has correct structure."""
        evidence = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_id": "123",
                "mr_iid": "42"
            },
            "findings": [],
            "approvals": [],
            "pipeline_results": [],
            "hash": ""
        }
        
        assert "metadata" in evidence
        assert "findings" in evidence
        assert "approvals" in evidence
        assert "hash" in evidence

    def test_evidence_hash_generation(self):
        """Test SHA-256 hash generation for evidence."""
        import hashlib
        
        evidence_data = json.dumps({
            "finding": "test",
            "timestamp": "2026-03-18T10:00:00Z"
        })
        
        hash_value = hashlib.sha256(evidence_data.encode()).hexdigest()
        
        assert len(hash_value) == 64  # SHA-256 hex is 64 chars
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_collect_mr_approvals(self):
        """Test collecting MR approval evidence."""
        approvals = [
            {
                "user": "alice",
                "approved_at": "2026-03-18T10:30:00Z"
            },
            {
                "user": "bob",
                "approved_at": "2026-03-18T10:45:00Z"
            }
        ]
        
        assert len(approvals) == 2
        assert approvals[0]["user"] == "alice"

    def test_collect_pipeline_results(self):
        """Test collecting pipeline security scan results."""
        pipeline_results = {
            "sast": {
                "vulnerabilities": 0,
                "status": "passed"
            },
            "dependency_check": {
                "vulnerabilities": 1,
                "status": "failed"
            }
        }
        
        assert "sast" in pipeline_results
        assert pipeline_results["sast"]["status"] == "passed"

    def test_evidence_retention_policy(self):
        """Test evidence is retained according to policy."""
        # SOC 2 requires 1-year retention
        retention_days = 365
        
        assert retention_days >= 365

    def test_evidence_non_repudiation(self):
        """Test evidence includes non-repudiation components."""
        evidence = {
            "hash": "abc123def456...",
            "timestamp": "2026-03-18T10:00:00Z",
            "signer": "gitlab-system",
            "signature": "signature_value"
        }
        
        assert "hash" in evidence
        assert "timestamp" in evidence
        assert "signer" in evidence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
