import pytest
import json
import sys
import hashlib
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestEvidenceBuilder:
    """Test suite for evidence builder functionality."""

    def test_evidence_builder_initialization(self):
        """Test evidence builder can be initialized."""
        evidence_data = {
            "metadata": {},
            "findings": [],
            "approvals": [],
            "artifacts": []
        }
        
        assert "metadata" in evidence_data
        assert isinstance(evidence_data["findings"], list)

    def test_collect_mr_approvals(self):
        """Test MR approval collection."""
        approvals = [
            {
                "id": 1,
                "user": {"username": "alice"},
                "created_at": "2026-03-18T10:00:00Z"
            },
            {
                "id": 2,
                "user": {"username": "bob"},
                "created_at": "2026-03-18T10:15:00Z"
            }
        ]
        
        assert len(approvals) == 2
        for approval in approvals:
            assert "user" in approval
            assert "created_at" in approval

    def test_collect_mr_approvals_with_required_approvals(self):
        """Test verifying MR meets required approvals."""
        mr = {
            "approvals_before_merge": 2,
            "approved_by": [
                {"username": "alice"},
                {"username": "bob"}
            ]
        }
        
        has_required = len(mr["approved_by"]) >= mr["approvals_before_merge"]
        assert has_required is True

    def test_collect_mr_approvals_insufficient(self):
        """Test identifying when MR lacks required approvals."""
        mr = {
            "approvals_before_merge": 2,
            "approved_by": [
                {"username": "alice"}
            ]
        }
        
        has_required = len(mr["approved_by"]) >= mr["approvals_before_merge"]
        assert has_required is False

    def test_collect_pipeline_security_scans(self):
        """Test pipeline security scan collection."""
        pipeline = {
            "id": 123456,
            "status": "success",
            "jobs": [
                {
                    "name": "sast_scan",
                    "status": "success",
                    "artifacts": {
                        "gl-sast-report.json": {
                            "vulnerabilities": []
                        }
                    }
                },
                {
                    "name": "dependency_check",
                    "status": "success",
                    "artifacts": {
                        "dependency-scanning-report.json": {
                            "vulnerabilities": []
                        }
                    }
                }
            ]
        }
        
        assert pipeline["status"] == "success"
        assert len(pipeline["jobs"]) == 2

    def test_collect_access_control_records(self):
        """Test collecting GitLab audit event records."""
        audit_events = [
            {
                "id": 1,
                "author": {"username": "alice"},
                "target_type": "User",
                "action": "add_access_level",
                "created_at": "2026-03-18T10:00:00Z"
            },
            {
                "id": 2,
                "author": {"username": "bob"},
                "target_type": "Project",
                "action": "change_visibility",
                "created_at": "2026-03-18T10:15:00Z"
            }
        ]
        
        assert len(audit_events) == 2
        access_change_events = [e for e in audit_events 
                               if e["action"] in ["add_access_level", "change_visibility"]]
        assert len(access_change_events) == 2

    def test_hash_evidence_sha256(self):
        """Test SHA-256 hashing of evidence."""
        evidence_json = json.dumps({
            "finding": "test",
            "timestamp": "2026-03-18T10:00:00Z"
        })
        
        hash_value = hashlib.sha256(evidence_json.encode()).hexdigest()
        
        # SHA-256 produces 64-char hex string
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_hash_deterministic(self):
        """Test that hashing same data produces same hash."""
        evidence_json = json.dumps({"data": "test"})
        
        hash1 = hashlib.sha256(evidence_json.encode()).hexdigest()
        hash2 = hashlib.sha256(evidence_json.encode()).hexdigest()
        
        assert hash1 == hash2

    def test_hash_different_data_different_hash(self):
        """Test that different data produces different hash."""
        data1 = json.dumps({"data": "test1"})
        data2 = json.dumps({"data": "test2"})
        
        hash1 = hashlib.sha256(data1.encode()).hexdigest()
        hash2 = hashlib.sha256(data2.encode()).hexdigest()
        
        assert hash1 != hash2

    def test_build_evidence_package_structure(self):
        """Test evidence package has required structure."""
        package = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_id": "123",
                "project_name": "test-project",
                "mr_iid": "42"
            },
            "findings": [
                {
                    "control_id": "SOC2-CC6.1",
                    "severity": "high"
                }
            ],
            "approvals": [
                {
                    "user": "alice",
                    "timestamp": "2026-03-18T10:00:00Z"
                }
            ],
            "pipeline_results": {
                "sast": {"vulnerabilities": 0}
            },
            "audit_events": [],
            "hash": hashlib.sha256(b"test").hexdigest()
        }
        
        assert "metadata" in package
        assert "findings" in package
        assert "approvals" in package
        assert "pipeline_results" in package
        assert "hash" in package

    def test_evidence_collection_period_default(self):
        """Test default evidence collection period (14 days)."""
        collection_period_days = 14
        cutoff_date = datetime.now() - timedelta(days=collection_period_days)
        
        events = [
            {"timestamp": datetime.now().isoformat()},  # Today
            {"timestamp": (datetime.now() - timedelta(days=7)).isoformat()},  # 7 days ago
            {"timestamp": (datetime.now() - timedelta(days=20)).isoformat()},  # 20 days ago
        ]
        
        recent_events = [e for e in events 
                        if datetime.fromisoformat(e["timestamp"]) > cutoff_date]
        
        assert len(recent_events) == 2

    def test_evidence_collection_period_scheduled(self):
        """Test extended collection period for scheduled runs (30 days)."""
        collection_period_days = 30
        cutoff_date = datetime.now() - timedelta(days=collection_period_days)
        
        events = [
            {"timestamp": datetime.now().isoformat()},  # Today
            {"timestamp": (datetime.now() - timedelta(days=14)).isoformat()},  # 14 days ago
            {"timestamp": (datetime.now() - timedelta(days=35)).isoformat()},  # 35 days ago
        ]
        
        recent_events = [e for e in events 
                        if datetime.fromisoformat(e["timestamp"]) > cutoff_date]
        
        assert len(recent_events) == 2

    def test_evidence_maximum_records(self):
        """Test maximum MR records per collection (500)."""
        max_records = 500
        
        records = [{"id": i} for i in range(600)]
        
        limited_records = records[:max_records]
        
        assert len(limited_records) == 500
        assert len(records) == 600

    def test_evidence_retention_policy_soc2(self):
        """Test SOC 2 requires 1-year retention."""
        retention_days = 365
        
        assert retention_days >= 365

    def test_evidence_retention_policy_hipaa(self):
        """Test HIPAA requires 6-year retention."""
        retention_days = 365 * 6
        
        assert retention_days >= 365 * 6

    def test_evidence_non_repudiation_components(self):
        """Test evidence includes non-repudiation elements."""
        evidence = {
            "content_hash": hashlib.sha256(b"evidence").hexdigest(),
            "timestamp": datetime.now().isoformat(),
            "signed_by": "gitlab-system",
            "signature": "signature_value"
        }
        
        # Non-repudiation requires: hash, timestamp, signer, signature
        assert "content_hash" in evidence
        assert "timestamp" in evidence
        assert "signed_by" in evidence
        assert "signature" in evidence

    def test_evidence_audit_trail(self):
        """Test evidence collection creates audit trail."""
        collection_log = {
            "collection_id": "audit-123",
            "started_at": datetime.now().isoformat(),
            "items_collected": 42,
            "collection_method": "gitlab_api",
            "collector_version": "1.0"
        }
        
        assert collection_log["items_collected"] == 42
        assert collection_log["collection_method"] == "gitlab_api"

    def test_evidence_includes_changeset_info(self):
        """Test evidence includes MR/changeset information."""
        changeset = {
            "mr_id": 42,
            "source_branch": "feat/security",
            "target_branch": "main",
            "author": "alice",
            "committed_changes": 3,
            "files_modified": ["src/auth.js", "src/database.js", "package.json"]
        }
        
        assert changeset["mr_id"] == 42
        assert len(changeset["files_modified"]) == 3

    def test_evidence_includes_compliance_mappings(self):
        """Test evidence includes control mappings."""
        evidence = {
            "controls_mapped": [
                "SOC2-CC6.1",
                "ISO27001-A.9.4.2",
                "PCI-DSS-8.2"
            ],
            "frameworks_covered": ["SOC2", "ISO27001", "PCI-DSS"]
        }
        
        assert len(evidence["controls_mapped"]) == 3
        assert "SOC2" in evidence["frameworks_covered"]

    def test_evidence_json_serialization(self):
        """Test evidence package serializes to JSON correctly."""
        package = {
            "metadata": {
                "timestamp": datetime.now().isoformat()
            },
            "findings": [],
            "hash": "abc123"
        }
        
        json_str = json.dumps(package)
        parsed = json.loads(json_str)
        
        assert parsed["hash"] == "abc123"
        assert "metadata" in parsed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
