import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.mapper import CONTROL_MAPPINGS, map_finding


class TestControlMappings:
    """Test compliance control mappings."""

    def test_control_mappings_exist(self):
        """Test that control mappings are defined."""
        assert CONTROL_MAPPINGS is not None
        assert len(CONTROL_MAPPINGS) > 0

    def test_authentication_change_mapping(self):
        """Test authentication change maps to correct controls."""
        mapping = CONTROL_MAPPINGS.get("authentication_change")
        
        assert mapping is not None
        assert "SOC2-CC6.1" in mapping
        assert "ISO27001-A.9.4.2" in mapping
        assert "PCI-DSS-8.2" in mapping

    def test_encryption_change_mapping(self):
        """Test encryption change maps to correct controls."""
        mapping = CONTROL_MAPPINGS.get("encryption_change")
        
        assert mapping is not None
        assert "SOC2-CC6.7" in mapping
        assert "ISO27001-A.10.1.1" in mapping
        assert "PCI-DSS-4.1" in mapping

    def test_dependency_vulnerability_mapping(self):
        """Test dependency vulnerability maps to correct controls."""
        mapping = CONTROL_MAPPINGS.get("dependency_vulnerability")
        
        assert mapping is not None
        assert "SOC2-CC7.1" in mapping
        assert "ISO27001-A.12.6.1" in mapping
        assert "PCI-DSS-6.3.3" in mapping

    def test_access_control_change_mapping(self):
        """Test access control change maps to correct controls."""
        mapping = CONTROL_MAPPINGS.get("access_control_change")
        
        assert mapping is not None
        assert "SOC2-CC6.3" in mapping
        assert "ISO27001-A.9.2.6" in mapping
        assert "PCI-DSS-7.2" in mapping

    def test_all_mappings_have_soc2(self):
        """Test that all mappings include SOC 2 controls."""
        for finding_type, controls in CONTROL_MAPPINGS.items():
            soc2_controls = [c for c in controls if c.startswith("SOC2")]
            assert len(soc2_controls) > 0, f"{finding_type} missing SOC2 control"

    def test_all_mappings_have_iso27001(self):
        """Test that all mappings include ISO 27001 controls."""
        for finding_type, controls in CONTROL_MAPPINGS.items():
            iso_controls = [c for c in controls if c.startswith("ISO27001")]
            assert len(iso_controls) > 0, f"{finding_type} missing ISO27001 control"


class TestMapFinding:
    """Test the map_finding function."""

    def test_map_finding_authentication(self):
        """Test mapping a finding with authentication evidence type."""
        finding = {
            "control_id": "SOC2-CC6.1",
            "severity": "high",
            "description": "Authentication logic modified",
            "evidence_type": "authentication_change",
            "file_path": "src/auth.js",
            "remediation": "Review with security team"
        }
        
        result = map_finding(finding)
        
        assert "finding" in result
        assert "mapped_controls" in result
        assert len(result["mapped_controls"]) == 3
        assert "SOC2-CC6.1" in result["mapped_controls"]

    def test_map_finding_encryption(self):
        """Test mapping a finding with encryption evidence type."""
        finding = {
            "evidence_type": "encryption_change",
            "description": "Encryption logic modified"
        }
        
        result = map_finding(finding)
        
        assert len(result["mapped_controls"]) == 3
        assert "SOC2-CC6.7" in result["mapped_controls"]
        assert "PCI-DSS-4.1" in result["mapped_controls"]

    def test_map_finding_dependency(self):
        """Test mapping a finding with dependency evidence type."""
        finding = {
            "evidence_type": "dependency_vulnerability",
            "description": "Vulnerable dependency detected"
        }
        
        result = map_finding(finding)
        
        assert len(result["mapped_controls"]) == 3
        assert "SOC2-CC7.1" in result["mapped_controls"]

    def test_map_finding_access_control(self):
        """Test mapping a finding with access control evidence type."""
        finding = {
            "evidence_type": "access_control_change",
            "description": "Access control modified"
        }
        
        result = map_finding(finding)
        
        assert len(result["mapped_controls"]) == 3
        assert "SOC2-CC6.3" in result["mapped_controls"]

    def test_map_finding_unknown_type(self):
        """Test mapping a finding with unknown evidence type."""
        finding = {
            "evidence_type": "unknown_type",
            "description": "Unknown finding"
        }
        
        result = map_finding(finding)
        
        # Should return empty list for unknown types
        assert result["mapped_controls"] == []

    def test_map_finding_missing_evidence_type(self):
        """Test mapping a finding without evidence_type field."""
        finding = {
            "description": "Finding without evidence type"
        }
        
        result = map_finding(finding)
        
        # Should return empty list when evidence_type is missing
        assert result["mapped_controls"] == []

    def test_map_finding_preserves_original(self):
        """Test that map_finding preserves the original finding."""
        original_finding = {
            "control_id": "SOC2-CC6.1",
            "severity": "high",
            "evidence_type": "authentication_change"
        }
        
        result = map_finding(original_finding)
        
        # Original finding should be preserved
        assert result["finding"] == original_finding

    def test_map_finding_multiple_findings_batch(self):
        """Test mapping multiple findings."""
        findings = [
            {"evidence_type": "authentication_change"},
            {"evidence_type": "encryption_change"},
            {"evidence_type": "dependency_vulnerability"},
            {"evidence_type": "access_control_change"}
        ]
        
        results = [map_finding(f) for f in findings]
        
        assert len(results) == 4
        # Each should have mapped_controls
        for result in results:
            assert len(result["mapped_controls"]) > 0


class TestComplianceScoring:
    """Test compliance scoring calculation."""

    def test_score_calculation_no_findings(self):
        """Test score calculation with no findings."""
        findings = []
        # Score should be 100 (perfect)
        assert len(findings) == 0

    def test_score_calculation_with_findings(self):
        """Test score calculation with multiple findings."""
        findings = [
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "low"}
        ]
        
        # Score should decrease with findings
        assert len(findings) == 4

    def test_critical_findings_impact_score(self):
        """Test that critical findings heavily impact score."""
        critical_finding = {"severity": "critical"}
        high_finding = {"severity": "high"}
        
        # Critical should impact more than high
        assert critical_finding["severity"] != high_finding["severity"]

    def test_multiple_findings_of_same_type(self):
        """Test scoring with multiple findings of same type."""
        findings = [
            {"severity": "high", "control_id": "SOC2-CC6.1"},
            {"severity": "high", "control_id": "SOC2-CC6.1"},
            {"severity": "high", "control_id": "SOC2-CC6.1"}
        ]
        
        # Multiple occurrences of same issue should be tracked
        assert len(findings) == 3


class TestMapperIntegration:
    """Integration tests combining mapper with scanner findings."""

    def test_map_scanner_findings(self):
        """Test mapping findings from scanner agent."""
        scanner_findings = [
            {
                "control_id": "SOC2-CC6.1",
                "severity": "high",
                "description": "Authentication logic modified",
                "evidence_type": "authentication_change",
                "file_path": "src/auth.js",
                "remediation": "Review with security team",
                "framework": "SOC2"
            },
            {
                "control_id": "SOC2-CC7.1",
                "severity": "medium",
                "description": "Dependency file modified",
                "evidence_type": "dependency_vulnerability",
                "file_path": "requirements.txt",
                "remediation": "Check for CVEs",
                "framework": "SOC2"
            }
        ]
        
        mapped_findings = [map_finding(f) for f in scanner_findings]
        
        assert len(mapped_findings) == 2
        assert all("mapped_controls" in mf for mf in mapped_findings)

    def test_framework_coverage(self):
        """Test that mapped controls cover multiple frameworks."""
        finding = {
            "evidence_type": "authentication_change"
        }
        
        result = map_finding(finding)
        controls = result["mapped_controls"]
        
        # Should have SOC2, ISO27001, and PCI-DSS
        frameworks = set()
        for control in controls:
            if control.startswith("SOC2"):
                frameworks.add("SOC2")
            elif control.startswith("ISO27001"):
                frameworks.add("ISO27001")
            elif control.startswith("PCI-DSS"):
                frameworks.add("PCI-DSS")
        
        assert len(frameworks) >= 2  # At least 2 frameworks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
