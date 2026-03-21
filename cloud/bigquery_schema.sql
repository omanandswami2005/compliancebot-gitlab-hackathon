-- ComplianceBot BigQuery Schema
-- Creates the compliance dataset and findings table for analytics

-- Create dataset (run once)
-- CREATE SCHEMA IF NOT EXISTS compliance
-- OPTIONS (
--   location = 'US',
--   description = 'ComplianceBot compliance findings and evidence'
-- );

-- Main findings table
CREATE TABLE IF NOT EXISTS compliance.compliance_findings (
  -- Identifiers
  project_id STRING NOT NULL,
  mr_id INT64 NOT NULL,
  mr_url STRING,
  pipeline_id INT64,
  
  -- Finding details
  control_id STRING NOT NULL,
  framework STRING NOT NULL,
  severity STRING NOT NULL,
  status STRING DEFAULT 'NEEDS_REVIEW',
  title STRING,
  description STRING,
  file_path STRING,
  remediation_steps STRING,
  
  -- Scores and hashes
  compliance_score INT64,
  evidence_hash STRING,
  
  -- Timestamps
  finding_date TIMESTAMP NOT NULL,
  remediated_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(finding_date)
CLUSTER BY project_id, framework, severity;

-- Evidence packages table
CREATE TABLE IF NOT EXISTS compliance.evidence_packages (
  id STRING NOT NULL,
  project_id STRING NOT NULL,
  mr_id INT64 NOT NULL,
  
  compliance_score INT64,
  frameworks ARRAY<STRING>,
  finding_count INT64,
  
  gcs_path STRING,
  content_hash STRING,
  
  generated_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(generated_at)
CLUSTER BY project_id;

-- ============================================
-- ANALYTICS QUERIES
-- ============================================

-- Query 1: Compliance trend over last 90 days
SELECT
  DATE(finding_date) as date,
  framework,
  AVG(compliance_score) as avg_score,
  COUNT(*) as total_findings,
  COUNTIF(severity = 'critical') as critical_count,
  COUNTIF(severity = 'high') as high_count,
  COUNTIF(status = 'REMEDIATED') as remediated_count
FROM compliance.compliance_findings
WHERE project_id = @project_id
  AND finding_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY date, framework
ORDER BY date DESC;

-- Query 2: Top recurring findings
SELECT
  control_id,
  framework,
  severity,
  COUNT(*) as occurrence_count,
  COUNT(DISTINCT project_id) as affected_projects,
  AVG(compliance_score) as avg_score_impact
FROM compliance.compliance_findings
WHERE finding_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY control_id, framework, severity
ORDER BY occurrence_count DESC
LIMIT 20;

-- Query 3: Project compliance summary
SELECT
  project_id,
  COUNT(DISTINCT mr_id) as total_mrs_scanned,
  AVG(compliance_score) as avg_compliance_score,
  COUNTIF(severity = 'critical') as total_critical,
  COUNTIF(severity = 'high') as total_high,
  COUNTIF(status = 'REMEDIATED') as total_remediated,
  MAX(finding_date) as last_scan_date
FROM compliance.compliance_findings
WHERE finding_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY project_id
ORDER BY avg_compliance_score ASC;

-- Query 4: Remediation velocity
SELECT
  project_id,
  framework,
  severity,
  AVG(TIMESTAMP_DIFF(remediated_date, finding_date, HOUR)) as avg_hours_to_remediate,
  COUNT(*) as remediated_count
FROM compliance.compliance_findings
WHERE remediated_date IS NOT NULL
  AND finding_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY project_id, framework, severity
ORDER BY avg_hours_to_remediate DESC;
