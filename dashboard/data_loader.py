"""
Data Loader for ComplianceBot Dashboard
========================================
Handles loading data from BigQuery (live) or mock data (demo mode).
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

# Check if GCP is available
GCP_AVAILABLE = False
try:
    from google.cloud import bigquery
    from google.cloud import storage
    GCP_AVAILABLE = True
except ImportError:
    logger.warning("Google Cloud libraries not installed. Using mock data.")


class DataLoader:
    """
    Loads compliance data from BigQuery or generates mock data.
    Automatically falls back to mock data if GCP is not configured.
    """
    
    def __init__(self):
        self.gcp_configured = self._check_gcp_config()
        self.bq_client = None
        self.storage_client = None
        
        if self.gcp_configured:
            try:
                self.bq_client = bigquery.Client()
                self.storage_client = storage.Client()
                logger.info("GCP clients initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize GCP clients: {e}")
                self.gcp_configured = False
    
    def _check_gcp_config(self) -> bool:
        """Check if GCP is properly configured."""
        if not GCP_AVAILABLE:
            return False
        
        project_id = os.environ.get('GCP_PROJECT_ID')
        creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or \
                os.environ.get('GCP_SERVICE_ACCOUNT_KEY')
        
        return bool(project_id and creds)
    
    @property
    def is_live(self) -> bool:
        """Check if using live data."""
        return self.gcp_configured
    
    def get_projects(self) -> list:
        """
        Get list of projects with compliance data.
        
        In LIVE mode: Fetches from BigQuery (distinct projects with findings)
        In DEMO mode: Returns hardcoded demo projects
        
        Returns:
            List of project names/paths
        """
        if self.gcp_configured:
            return self._get_projects_from_bigquery()
        else:
            return self._get_mock_projects()
    
    def _get_projects_from_bigquery(self) -> list:
        """Fetch distinct projects from BigQuery."""
        try:
            query = f"""
            SELECT DISTINCT project_id as project
            FROM `{os.environ['GCP_PROJECT_ID']}.compliance.compliance_findings`
            WHERE finding_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
            ORDER BY project
            """
            df = self.bq_client.query(query).to_dataframe()
            return df['project'].tolist()
        except Exception as e:
            logger.error(f"Failed to fetch projects from BigQuery: {e}")
            return self._get_mock_projects()
    
    def _get_mock_projects(self) -> list:
        """Return demo project list."""
        return [
            'gitlab-ai-hackathon/participants/35481656',  # Our actual project
            'frontend-app',
            'backend-api', 
            'data-service',
            'auth-service'
        ]
    
    def get_findings(self, days: int = 90) -> pd.DataFrame:
        """
        Get compliance findings data.
        
        Args:
            days: Number of days to look back
            
        Returns:
            DataFrame with findings data
        """
        if self.gcp_configured:
            return self._get_findings_from_bigquery(days)
        else:
            return self._generate_mock_findings(days)
    
    def get_reports(self, limit: int = 20) -> list:
        """
        Get list of compliance reports.
        
        Args:
            limit: Maximum number of reports to return
            
        Returns:
            List of report dictionaries
        """
        if self.gcp_configured:
            return self._get_reports_from_gcs(limit)
        else:
            return self._generate_mock_reports(limit)
    
    def get_evidence(self, limit: int = 30) -> list:
        """
        Get list of evidence packages.
        
        Args:
            limit: Maximum number of evidence packages to return
            
        Returns:
            List of evidence dictionaries
        """
        if self.gcp_configured:
            return self._get_evidence_from_gcs(limit)
        else:
            return self._generate_mock_evidence(limit)
    
    # =========================================================================
    # BIGQUERY METHODS
    # =========================================================================
    
    def _get_findings_from_bigquery(self, days: int) -> pd.DataFrame:
        """Load findings from BigQuery."""
        try:
            query = f"""
            SELECT
                finding_date as date,
                project_id as project,
                mr_id,
                framework,
                control_id,
                severity,
                compliance_score,
                status,
                title
            FROM `{os.environ['GCP_PROJECT_ID']}.compliance.compliance_findings`
            WHERE finding_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            ORDER BY finding_date DESC
            LIMIT 1000
            """
            
            df = self.bq_client.query(query).to_dataframe()
            df['date'] = pd.to_datetime(df['date'])
            return df
            
        except Exception as e:
            logger.error(f"BigQuery query failed: {e}")
            return self._generate_mock_findings(days)
    
    def _get_reports_from_gcs(self, limit: int) -> list:
        """Load report list from Cloud Storage."""
        try:
            bucket_name = os.environ.get('GCS_BUCKET', f"compliance-evidence-{os.environ['GCP_PROJECT_ID']}")
            bucket = self.storage_client.bucket(bucket_name)
            
            reports = []
            blobs = bucket.list_blobs(prefix='reports/', max_results=limit)
            
            for blob in blobs:
                if blob.name.endswith('.pdf'):
                    metadata = blob.metadata or {}
                    reports.append({
                        'id': blob.name.split('/')[-1].replace('.pdf', ''),
                        'project': metadata.get('project_id', 'unknown'),
                        'mr_id': int(metadata.get('mr_id', 0)),
                        'date': blob.time_created,
                        'score': int(metadata.get('compliance_score', 0)),
                        'status': 'Pass' if int(metadata.get('compliance_score', 0)) >= 85 else 'Fail',
                        'findings': int(metadata.get('finding_count', 0)),
                        'frameworks': metadata.get('frameworks', '').split(','),
                        'size': f'{blob.size // 1024} KB',
                        'url': blob.generate_signed_url(expiration=timedelta(hours=1))
                    })
            
            return sorted(reports, key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            logger.error(f"GCS list failed: {e}")
            return self._generate_mock_reports(limit)
    
    def _get_evidence_from_gcs(self, limit: int) -> list:
        """Load evidence list from Cloud Storage."""
        try:
            bucket_name = os.environ.get('GCS_BUCKET', f"compliance-evidence-{os.environ['GCP_PROJECT_ID']}")
            bucket = self.storage_client.bucket(bucket_name)
            
            evidence = []
            blobs = bucket.list_blobs(prefix='evidence/', max_results=limit)
            
            for blob in blobs:
                if blob.name.endswith('.json'):
                    metadata = blob.metadata or {}
                    evidence.append({
                        'id': blob.name.split('/')[-1].replace('.json', ''),
                        'project': metadata.get('project_id', 'unknown'),
                        'type': metadata.get('evidence_type', 'Unknown'),
                        'date': blob.time_created,
                        'items': int(metadata.get('item_count', 0)),
                        'hash': metadata.get('content_hash', 'N/A')[:20] + '...',
                        'controls_covered': int(metadata.get('controls_covered', 0)),
                        'size': f'{blob.size // 1024} KB',
                        'url': blob.generate_signed_url(expiration=timedelta(hours=1))
                    })
            
            return sorted(evidence, key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            logger.error(f"GCS evidence list failed: {e}")
            return self._generate_mock_evidence(limit)
    
    # =========================================================================
    # MOCK DATA METHODS
    # =========================================================================
    
    def _generate_mock_findings(self, days: int) -> pd.DataFrame:
        """Generate mock compliance findings data."""
        frameworks = ['SOC 2', 'ISO 27001', 'PCI-DSS', 'HIPAA']
        severities = ['critical', 'high', 'medium', 'low']
        controls = {
            'SOC 2': ['CC6.1', 'CC6.2', 'CC6.7', 'CC7.1', 'CC8.1'],
            'ISO 27001': ['A.8.2', 'A.9.4', 'A.10.1', 'A.12.6'],
            'PCI-DSS': ['6.3', '8.2', '10.2'],
            'HIPAA': ['164.312(a)', '164.312(b)', '164.312(e)']
        }
        
        titles = [
            'Hardcoded API key detected',
            'SQL injection vulnerability',
            'Weak password hashing (MD5)',
            'Missing input validation',
            'Insecure session management',
            'Outdated dependency with CVE',
            'Debug mode enabled in production',
            'Missing encryption at rest',
            'Excessive IAM permissions',
            'Missing audit logging',
            'Disabled SSL verification',
            'Hardcoded database credentials',
            'Weak session token generation',
            'Missing CSRF protection',
            'Insecure cookie configuration'
        ]
        
        data = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(min(days * 3, 300)):
            framework = random.choice(frameworks)
            date = base_date + timedelta(days=random.randint(0, days))
            severity = random.choices(severities, weights=[5, 15, 40, 40])[0]
            
            data.append({
                'date': date,
                'project': random.choice(['frontend-app', 'backend-api', 'data-service', 'auth-service']),
                'mr_id': random.randint(1, 500),
                'framework': framework,
                'control_id': random.choice(controls[framework]),
                'severity': severity,
                'compliance_score': random.randint(40, 100),
                'status': random.choice(['open', 'remediated', 'accepted']),
                'title': random.choice(titles)
            })
        
        return pd.DataFrame(data)
    
    def _generate_mock_reports(self, limit: int) -> list:
        """Generate mock PDF reports data."""
        reports = []
        for i in range(limit):
            date = datetime.now() - timedelta(days=random.randint(0, 30))
            score = random.randint(45, 98)
            reports.append({
                'id': f'RPT-{1000+i}',
                'project': random.choice(['frontend-app', 'backend-api', 'data-service', 'auth-service']),
                'mr_id': random.randint(1, 100),
                'date': date,
                'score': score,
                'status': 'Pass' if score >= 85 else 'Fail',
                'findings': random.randint(0, 25),
                'frameworks': random.sample(['SOC 2', 'ISO 27001', 'PCI-DSS', 'HIPAA'], k=random.randint(2, 4)),
                'size': f'{random.randint(100, 500)} KB',
                'url': '#'
            })
        return sorted(reports, key=lambda x: x['date'], reverse=True)
    
    def _generate_mock_evidence(self, limit: int) -> list:
        """Generate mock evidence packages data."""
        evidence = []
        for i in range(limit):
            date = datetime.now() - timedelta(days=random.randint(0, 60))
            evidence.append({
                'id': f'EVD-{2000+i}',
                'project': random.choice(['frontend-app', 'backend-api', 'data-service', 'auth-service']),
                'type': random.choice(['MR Approvals', 'Pipeline Logs', 'Access Audit', 'Security Scans']),
                'date': date,
                'items': random.randint(5, 50),
                'hash': f'sha256:{random.randbytes(8).hex()}...',
                'controls_covered': random.randint(3, 12),
                'size': f'{random.randint(50, 300)} KB',
                'url': '#'
            })
        return sorted(evidence, key=lambda x: x['date'], reverse=True)


# Singleton instance
_data_loader = None

def get_data_loader() -> DataLoader:
    """Get the singleton DataLoader instance."""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader
