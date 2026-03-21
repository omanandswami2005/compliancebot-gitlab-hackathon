# tests/test_gcp_integration.py
"""
Tests for GCP integration module.
Tests graceful degradation when GCP is not configured.
"""

import os
import pytest
import json
from unittest.mock import patch, MagicMock

# Import GCP modules
from src.gcp.client import GCPClient, get_gcp_client, GCPConfig
from src.gcp.bigquery import BigQueryLogger, log_compliance_findings
from src.gcp.storage import CloudStorageUploader, upload_compliance_pdf
from src.gcp.vertex_ai import VertexAINarrative, generate_compliance_narrative
from src.gcp.integration import GCPIntegration, archive_compliance_results, get_gcp_status


class TestGCPClient:
    """Tests for GCPClient class."""
    
    def test_client_without_credentials(self):
        """Test that client handles missing credentials gracefully."""
        # Clear any existing env vars
        with patch.dict(os.environ, {}, clear=True):
            client = GCPClient()
            result = client.initialize()
            
            assert result is False
            assert client.is_available is False
            assert "GCP_PROJECT_ID" in client.error_message
    
    def test_client_with_project_id_only(self):
        """Test client with project ID but no credentials."""
        with patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'}, clear=True):
            client = GCPClient()
            result = client.initialize()
            
            # Should initialize but not be fully available
            assert result is True
            assert client.is_configured is True
            assert client.is_available is False
            assert client.config.project_id == 'test-project'
    
    def test_get_status(self):
        """Test status reporting."""
        with patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'}, clear=True):
            client = GCPClient()
            client.initialize()
            
            status = client.get_status()
            
            assert 'gcp_available' in status
            assert 'gcp_configured' in status
            assert 'project_id' in status
            assert status['project_id'] == 'test-project'


class TestBigQueryLogger:
    """Tests for BigQueryLogger class."""
    
    def test_log_findings_without_gcp(self):
        """Test that logging fails gracefully without GCP."""
        with patch.dict(os.environ, {}, clear=True):
            # Reset the global client
            import src.gcp.client as client_module
            client_module._gcp_client = None
            
            result = log_compliance_findings(
                findings=[{'severity': 'high', 'description': 'Test finding'}],
                project_id='test/project',
                mr_id=1,
                mr_url='https://gitlab.com/test/project/-/merge_requests/1',
                compliance_score=75
            )
            
            assert result['success'] is False
            assert 'not available' in result['error'].lower()
            assert result['logged_count'] == 0
    
    def test_extract_framework(self):
        """Test framework extraction from control IDs."""
        logger = BigQueryLogger()
        
        # SOC2 controls
        assert logger._extract_framework({'control_ids': ['SOC2-CC6.1']}) == 'SOC2'
        assert logger._extract_framework({'control_ids': ['CC6.1']}) == 'SOC2'
        
        # ISO controls
        assert logger._extract_framework({'control_ids': ['ISO27001-A.8.2']}) == 'ISO27001'
        assert logger._extract_framework({'control_ids': ['A.8.2.3']}) == 'ISO27001'
        
        # PCI-DSS
        assert logger._extract_framework({'control_ids': ['PCI-DSS-6.3']}) == 'PCI-DSS'
        
        # Custom org controls
        assert logger._extract_framework({'control_ids': ['ORG-001']}) == 'ORG-CUSTOM'
        
        # Unknown
        assert logger._extract_framework({'control_ids': []}) == 'UNKNOWN'


class TestCloudStorageUploader:
    """Tests for CloudStorageUploader class."""
    
    def test_upload_without_gcp(self):
        """Test that upload fails gracefully without GCP."""
        with patch.dict(os.environ, {}, clear=True):
            import src.gcp.client as client_module
            client_module._gcp_client = None
            
            result = upload_compliance_pdf(
                pdf_content=b'%PDF-1.4 test',
                project_id='test/project',
                mr_id=1,
                compliance_score=75,
                frameworks=['SOC2']
            )
            
            assert result['success'] is False
            assert 'not available' in result['error'].lower()


class TestVertexAINarrative:
    """Tests for VertexAINarrative class."""
    
    def test_fallback_narrative(self):
        """Test fallback narrative generation without Vertex AI."""
        with patch.dict(os.environ, {}, clear=True):
            import src.gcp.client as client_module
            client_module._gcp_client = None
            
            result = generate_compliance_narrative(
                findings=[
                    {'severity': 'critical', 'description': 'Critical issue'},
                    {'severity': 'high', 'description': 'High issue'},
                    {'severity': 'medium', 'description': 'Medium issue'},
                ],
                compliance_score=50,
                frameworks=['SOC2', 'ISO27001'],
                project_name='Test Project',
                mr_title='Test MR'
            )
            
            assert result['success'] is True
            assert result['source'] == 'fallback'
            assert 'narrative' in result
            assert 'Test Project' in result['narrative']
            assert '50/100' in result['narrative']
    
    def test_fallback_with_high_score(self):
        """Test fallback narrative for passing score."""
        narrator = VertexAINarrative()
        
        result = narrator._generate_fallback_summary(
            findings=[],
            compliance_score=95,
            frameworks=['SOC2'],
            project_name='Good Project',
            mr_title=None
        )
        
        assert 'satisfactory' in result['narrative'].lower()
        assert 'meets compliance requirements' in result['narrative'].lower()


class TestGCPIntegration:
    """Tests for main GCPIntegration class."""
    
    def test_process_without_gcp(self):
        """Test full processing without GCP configured."""
        with patch.dict(os.environ, {}, clear=True):
            import src.gcp.client as client_module
            client_module._gcp_client = None
            
            results = archive_compliance_results(
                findings=[
                    {
                        'severity': 'high',
                        'description': 'Test finding',
                        'control_ids': ['SOC2-CC6.1'],
                        'file_paths': ['test.py']
                    }
                ],
                compliance_score=75,
                frameworks=['SOC2', 'ISO27001'],
                project_id='test/project',
                project_name='Test Project',
                mr_id=1,
                mr_url='https://gitlab.com/test/project/-/merge_requests/1',
                mr_title='Test MR',
                generate_pdf=True
            )
            
            # Should complete without errors
            assert 'operations' in results
            assert 'summary' in results
            
            # Narrative should use fallback
            assert results['operations']['narrative']['source'] == 'fallback'
            
            # BigQuery should be skipped
            assert results['operations']['bigquery']['success'] is False
    
    def test_get_status_function(self):
        """Test the get_gcp_status convenience function."""
        status = get_gcp_status()
        
        assert isinstance(status, dict)
        assert 'gcp_available' in status
        assert 'gcp_configured' in status


class TestGCPConfig:
    """Tests for GCPConfig dataclass."""
    
    def test_default_bucket_name(self):
        """Test that default bucket name is generated."""
        config = GCPConfig(project_id='my-project')
        
        assert config.gcs_bucket == 'compliance-evidence-my-project'
    
    def test_custom_bucket_name(self):
        """Test custom bucket name."""
        config = GCPConfig(
            project_id='my-project',
            gcs_bucket='custom-bucket'
        )
        
        assert config.gcs_bucket == 'custom-bucket'


# Integration test (requires GCP credentials)
@pytest.mark.skipif(
    not os.environ.get('GCP_PROJECT_ID'),
    reason="GCP_PROJECT_ID not set - skipping integration tests"
)
class TestGCPIntegrationLive:
    """Live integration tests (only run when GCP is configured)."""
    
    def test_live_status(self):
        """Test live GCP status check."""
        status = get_gcp_status()
        
        assert status['gcp_configured'] is True
        assert status['project_id'] is not None
    
    def test_live_narrative_generation(self):
        """Test live Vertex AI narrative generation."""
        if not os.environ.get('GCP_SERVICE_ACCOUNT_KEY'):
            pytest.skip("GCP credentials not set")
        
        result = generate_compliance_narrative(
            findings=[
                {'severity': 'high', 'description': 'Test finding', 'control_ids': ['SOC2-CC6.1']}
            ],
            compliance_score=75,
            frameworks=['SOC2'],
            project_name='Test Project'
        )
        
        # Should either succeed with Vertex AI or fallback
        assert result['success'] is True
        assert 'narrative' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
