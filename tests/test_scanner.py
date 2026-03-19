import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from dataclasses import asdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.scanner import ComplianceScanner, ComplianceFinding


@pytest.fixture
def mock_gitlab():
    """Mock GitLab API client."""
    with patch('agents.scanner.gitlab.Gitlab') as mock_gl:
        yield mock_gl


@pytest.fixture
def sample_mr_diff():
    """Load sample MR diff fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_mr_diff.json"
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def scanner(mock_gitlab):
    """Create a ComplianceScanner instance with mocked GitLab."""
    scanner = ComplianceScanner("fake_token", "123")
    scanner.project = MagicMock()
    return scanner


class TestComplianceScanner:
    """Test suite for ComplianceScanner agent."""

    def test_scanner_initialization(self, scanner):
        """Test scanner can be initialized."""
        assert scanner is not None
        assert scanner.project is not None

    def test_scan_merge_request_authentication_change(self, scanner):
        """Test detection of authentication-related changes."""
        # Create mock MR with auth change
        mock_mr = MagicMock()
        mock_diff = {
            'new_path': 'src/auth.js',
            'diff': '+jwt.verify(token, process.env.JWT_SECRET)'
        }
        mock_mr.diffs.list.return_value = [mock_diff]
        mock_mr.pipelines.list.return_value = []
        
        scanner.project.mergerequests.get.return_value = mock_mr

        findings = scanner.scan_merge_request(42)

        # Should find at least one auth-related finding
        auth_findings = [f for f in findings if 'auth' in f.description.lower()]
        assert len(auth_findings) > 0
        assert auth_findings[0].severity == "high"
        assert auth_findings[0].control_id == "SOC2-CC6.1"

    def test_scan_merge_request_dependency_change(self, scanner):
        """Test detection of dependency updates."""
        mock_mr = MagicMock()
        mock_diff = {
            'new_path': 'requirements.txt',
            'diff': '-mongoose==6.0.0\n+mongoose==7.5.0'
        }
        mock_mr.diffs.list.return_value = [mock_diff]
        mock_mr.pipelines.list.return_value = []
        
        scanner.project.mergerequests.get.return_value = mock_mr

        findings = scanner.scan_merge_request(42)

        dependency_findings = [f for f in findings if f.evidence_type == "dependency"]
        assert len(dependency_findings) > 0
        assert dependency_findings[0].severity == "medium"
        assert dependency_findings[0].control_id == "SOC2-CC7.1"

    def test_scan_merge_request_encryption_change(self, scanner):
        """Test detection of encryption-related changes."""
        mock_mr = MagicMock()
        mock_diff = {
            'new_path': 'src/database.js',
            'diff': '+    ssl: true,\n+    sslValidate: true,'
        }
        mock_mr.diffs.list.return_value = [mock_diff]
        mock_mr.pipelines.list.return_value = []
        
        scanner.project.mergerequests.get.return_value = mock_mr

        findings = scanner.scan_merge_request(42)

        encryption_findings = [f for f in findings 
                             if 'encrypt' in f.description.lower() or 'ssl' in f.description.lower()]
        assert len(encryption_findings) > 0
        assert encryption_findings[0].control_id == "SOC2-CC6.7"
        assert encryption_findings[0].severity == "high"

    def test_scan_merge_request_with_sast_findings(self, scanner):
        """Test integration with SAST pipeline results."""
        mock_mr = MagicMock()
        mock_mr.diffs.list.return_value = []
        
        # Mock pipeline with SAST report
        mock_pipeline = MagicMock()
        mock_pipeline.id = 123456
        mock_mr.pipelines.list.return_value = [mock_pipeline]
        
        mock_job = MagicMock()
        mock_job.name = "sast_scan"
        
        mock_pipeline_obj = MagicMock()
        mock_pipeline_obj.jobs.list.return_value = [mock_job]
        
        scanner.project.mergerequests.get.return_value = mock_mr
        scanner.project.pipelines.get.return_value = mock_pipeline_obj
        
        # Mock artifacts with security findings
        sast_report = {
            "vulnerabilities": [
                {
                    "severity": "Critical",
                    "message": "SQL injection vulnerability",
                    "location": {"file": "src/db.js"},
                    "solution": "Use parameterized queries"
                }
            ]
        }
        mock_job.artifacts.return_value = {'gl-sast-report.json': json.dumps(sast_report)}

        findings = scanner.scan_merge_request(42)

        # Should detect critical vulnerability
        critical_findings = [f for f in findings if f.severity == "critical"]
        assert len(critical_findings) > 0

    def test_scan_merge_request_ignores_boilerplate(self, scanner):
        """Test that boilerplate files are not reported."""
        mock_mr = MagicMock()
        mock_diff = {
            'new_path': 'README.md',
            'diff': '+New documentation'
        }
        mock_mr.diffs.list.return_value = [mock_diff]
        mock_mr.pipelines.list.return_value = []
        
        scanner.project.mergerequests.get.return_value = mock_mr

        findings = scanner.scan_merge_request(42)

        # README changes shouldn't produce findings
        readme_findings = [f for f in findings if 'README' in f.file_path]
        assert len(readme_findings) == 0

    def test_compliance_finding_dataclass(self):
        """Test ComplianceFinding dataclass creation."""
        finding = ComplianceFinding(
            control_id="SOC2-CC6.1",
            severity="high",
            description="Test finding",
            evidence_type="code_change",
            file_path="src/test.js",
            remediation="Review code",
            framework="SOC2"
        )
        
        assert finding.control_id == "SOC2-CC6.1"
        assert finding.severity == "high"
        assert finding.framework == "SOC2"
        
        # Test conversion to dict
        finding_dict = asdict(finding)
        assert isinstance(finding_dict, dict)
        assert finding_dict["control_id"] == "SOC2-CC6.1"

    def test_multiple_frameworks_detection(self, scanner):
        """Test that findings map to multiple frameworks."""
        mock_mr = MagicMock()
        mock_diff = {
            'new_path': 'src/auth.js',
            'diff': '+jwt.verify(token)'
        }
        mock_mr.diffs.list.return_value = [mock_diff]
        mock_mr.pipelines.list.return_value = []
        
        scanner.project.mergerequests.get.return_value = mock_mr

        findings = scanner.scan_merge_request(42)

        # At least one finding should be SOC2
        soc2_findings = [f for f in findings if f.framework == "SOC2"]
        assert len(soc2_findings) > 0

    def test_empty_merge_request(self, scanner):
        """Test scanning MR with no findings."""
        mock_mr = MagicMock()
        mock_mr.diffs.list.return_value = []
        mock_mr.pipelines.list.return_value = []
        
        scanner.project.mergerequests.get.return_value = mock_mr

        findings = scanner.scan_merge_request(42)

        # Should return empty list or low severity findings
        assert isinstance(findings, list)

    def test_analyze_auth_change_method(self, scanner):
        """Test _analyze_auth_change method directly."""
        change = {
            'new_path': 'src/auth.js',
            'diff': '+jwt.verify(token)'
        }
        
        findings = scanner._analyze_auth_change(change)
        
        assert len(findings) > 0
        assert findings[0].control_id == "SOC2-CC6.1"
        assert findings[0].severity == "high"
        assert findings[0].file_path == "src/auth.js"

    def test_analyze_encryption_change_method(self, scanner):
        """Test _analyze_encryption_change method directly."""
        change = {
            'new_path': 'src/database.js',
            'diff': '+    ssl: true,'
        }
        
        findings = scanner._analyze_encryption_change(change)
        
        assert len(findings) > 0
        assert findings[0].control_id == "SOC2-CC6.7"
        assert findings[0].severity == "high"

    def test_analyze_dependency_change_method(self, scanner):
        """Test _analyze_dependency_change method directly."""
        change = {
            'new_path': 'requirements.txt',
            'diff': '+mongoose==7.5.0'
        }
        
        findings = scanner._analyze_dependency_change(change)
        
        assert len(findings) > 0
        assert findings[0].control_id == "SOC2-CC7.1"
        assert findings[0].severity == "medium"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
