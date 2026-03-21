# src/gcp/client.py
"""
GCP Client - Handles Google Cloud authentication and configuration.
Provides graceful degradation when GCP credentials are not available.
"""

import os
import json
import base64
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GCPConfig:
    """GCP Configuration container."""
    project_id: str
    region: str = "us-central1"
    bigquery_dataset: str = "compliance"
    bigquery_table: str = "compliance_findings"
    gcs_bucket: Optional[str] = None
    credentials_path: Optional[str] = None
    
    def __post_init__(self):
        if not self.gcs_bucket:
            self.gcs_bucket = f"compliance-evidence-{self.project_id}"


class GCPClient:
    """
    Google Cloud Platform client with graceful degradation.
    
    If GCP credentials are not configured, all operations return
    success=False with descriptive error messages, allowing the
    main ComplianceBot flow to continue working.
    """
    
    def __init__(self):
        self._config: Optional[GCPConfig] = None
        self._initialized = False
        self._init_error: Optional[str] = None
        self._credentials_set = False
        
    def initialize(self) -> bool:
        """
        Initialize GCP client from environment variables.
        
        Required environment variables:
        - GCP_PROJECT_ID: Google Cloud project ID
        
        Optional environment variables:
        - GCP_SERVICE_ACCOUNT_KEY: Base64-encoded service account JSON
        - GCP_CREDENTIALS_PATH: Path to service account JSON file
        - GCP_REGION: GCP region (default: us-central1)
        - BIGQUERY_DATASET: BigQuery dataset name (default: compliance)
        - GCS_BUCKET: Cloud Storage bucket name
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Check for project ID (required)
            project_id = os.environ.get('GCP_PROJECT_ID')
            if not project_id:
                self._init_error = "GCP_PROJECT_ID environment variable not set"
                logger.warning(f"GCP initialization skipped: {self._init_error}")
                return False
            
            # Create config
            self._config = GCPConfig(
                project_id=project_id,
                region=os.environ.get('GCP_REGION', 'us-central1'),
                bigquery_dataset=os.environ.get('BIGQUERY_DATASET', 'compliance'),
                bigquery_table=os.environ.get('BIGQUERY_TABLE', 'compliance_findings'),
                gcs_bucket=os.environ.get('GCS_BUCKET'),
            )
            
            # Handle credentials
            self._credentials_set = self._setup_credentials()
            
            if not self._credentials_set:
                self._init_error = "GCP credentials not configured (GCP_SERVICE_ACCOUNT_KEY or GCP_CREDENTIALS_PATH required)"
                logger.warning(f"GCP initialization partial: {self._init_error}")
                # Still return True - we have project ID, just no credentials
                # This allows for testing and local development
            
            self._initialized = True
            logger.info(f"GCP client initialized for project: {project_id}")
            return True
            
        except Exception as e:
            self._init_error = f"GCP initialization failed: {str(e)}"
            logger.error(self._init_error)
            return False
    
    def _setup_credentials(self) -> bool:
        """
        Setup GCP credentials from environment.
        
        Supports:
        1. GCP_SERVICE_ACCOUNT_KEY - Base64-encoded JSON
        2. GCP_CREDENTIALS_PATH - Path to JSON file
        3. GOOGLE_APPLICATION_CREDENTIALS - Standard GCP env var
        
        Returns:
            bool: True if credentials were set up successfully
        """
        # Check if already set via standard env var
        if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            creds_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
            if os.path.exists(creds_path):
                logger.info(f"Using existing GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
                self._config.credentials_path = creds_path
                return True
        
        # Try base64-encoded key
        b64_key = os.environ.get('GCP_SERVICE_ACCOUNT_KEY')
        if b64_key:
            try:
                # Decode and write to temp file
                key_json = base64.b64decode(b64_key).decode('utf-8')
                
                # Validate it's valid JSON
                json.loads(key_json)
                
                # Write to temp location
                creds_path = '/tmp/gcp-credentials.json'
                with open(creds_path, 'w') as f:
                    f.write(key_json)
                
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
                self._config.credentials_path = creds_path
                logger.info("GCP credentials set from GCP_SERVICE_ACCOUNT_KEY")
                return True
                
            except Exception as e:
                logger.warning(f"Failed to decode GCP_SERVICE_ACCOUNT_KEY: {e}")
        
        # Try path to credentials file
        creds_path = os.environ.get('GCP_CREDENTIALS_PATH')
        if creds_path and os.path.exists(creds_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
            self._config.credentials_path = creds_path
            logger.info(f"GCP credentials set from GCP_CREDENTIALS_PATH: {creds_path}")
            return True
        
        return False
    
    @property
    def is_available(self) -> bool:
        """Check if GCP integration is fully available."""
        return self._initialized and self._credentials_set
    
    @property
    def is_configured(self) -> bool:
        """Check if GCP is configured (may not have credentials)."""
        return self._initialized
    
    @property
    def config(self) -> Optional[GCPConfig]:
        """Get GCP configuration."""
        return self._config
    
    @property
    def error_message(self) -> Optional[str]:
        """Get initialization error message if any."""
        return self._init_error
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get GCP integration status for reporting.
        
        Returns:
            dict: Status information including availability and any errors
        """
        return {
            "gcp_available": self.is_available,
            "gcp_configured": self.is_configured,
            "project_id": self._config.project_id if self._config else None,
            "region": self._config.region if self._config else None,
            "bigquery_dataset": self._config.bigquery_dataset if self._config else None,
            "gcs_bucket": self._config.gcs_bucket if self._config else None,
            "credentials_set": self._credentials_set,
            "error": self._init_error
        }


# Global singleton instance
_gcp_client: Optional[GCPClient] = None


def get_gcp_client() -> GCPClient:
    """
    Get the global GCP client instance.
    
    Initializes on first call. Thread-safe for read operations.
    
    Returns:
        GCPClient: The global GCP client instance
    """
    global _gcp_client
    
    if _gcp_client is None:
        _gcp_client = GCPClient()
        _gcp_client.initialize()
    
    return _gcp_client
