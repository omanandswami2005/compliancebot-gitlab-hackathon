-- Schema for compliance_findings table in BigQuery
CREATE TABLE compliance_findings (
  project_id STRING,
  pipeline_id INT64,
  mr_id INT64,
  control_id STRING,
  framework STRING,
  status STRING,  -- PASS | FAIL | NEEDS_REVIEW
  severity STRING,
  finding_date TIMESTAMP,
  remediated_date TIMESTAMP,
  score INT64
);

-- Query: Compliance trend over last 90 days
SELECT
  DATE(finding_date) as date,
  framework,
  AVG(score) as avg_score,
  COUNTIF(status = 'FAIL') as failures
FROM compliance_findings
WHERE project_id = @project_id
  AND finding_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY date, framework
ORDER BY date DESC;
