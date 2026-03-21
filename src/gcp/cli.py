#!/usr/bin/env python3
# src/gcp/cli.py
"""
GCP Integration CLI - Command-line interface for GCP operations.
Can be called from CI/CD pipelines or manually.
"""

import argparse
import json
import sys
import logging
from typing import Optional

from .integration import archive_compliance_results, get_gcp_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='ComplianceBot GCP Integration CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check GCP status
  python -m src.gcp.cli status
  
  # Archive compliance results from JSON file
  python -m src.gcp.cli archive --input results.json
  
  # Archive with specific parameters
  python -m src.gcp.cli archive \\
    --project-id "my-org/my-project" \\
    --project-name "My Project" \\
    --mr-id 10 \\
    --mr-url "https://gitlab.com/my-org/my-project/-/merge_requests/10" \\
    --score 75 \\
    --frameworks "SOC2,ISO27001" \\
    --findings findings.json

Environment Variables:
  GCP_PROJECT_ID          - Google Cloud project ID (required)
  GCP_SERVICE_ACCOUNT_KEY - Base64-encoded service account JSON
  GCP_CREDENTIALS_PATH    - Path to service account JSON file
  GCP_REGION              - GCP region (default: us-central1)
  BIGQUERY_DATASET        - BigQuery dataset (default: compliance)
  GCS_BUCKET              - Cloud Storage bucket name
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check GCP integration status')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Archive compliance results to GCP')
    archive_parser.add_argument('--input', '-i', help='JSON file with compliance results')
    archive_parser.add_argument('--project-id', help='GitLab project ID or path')
    archive_parser.add_argument('--project-name', help='Human-readable project name')
    archive_parser.add_argument('--mr-id', type=int, help='Merge request IID')
    archive_parser.add_argument('--mr-url', help='Full URL to merge request')
    archive_parser.add_argument('--mr-title', help='Merge request title')
    archive_parser.add_argument('--score', type=int, help='Compliance score (0-100)')
    archive_parser.add_argument('--frameworks', help='Comma-separated list of frameworks')
    archive_parser.add_argument('--findings', help='JSON file with findings list')
    archive_parser.add_argument('--evidence', help='JSON file with evidence package')
    archive_parser.add_argument('--no-pdf', action='store_true', help='Skip PDF generation')
    archive_parser.add_argument('--output', '-o', help='Output file for results JSON')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        handle_status(args)
    elif args.command == 'archive':
        handle_archive(args)
    else:
        parser.print_help()
        sys.exit(1)


def handle_status(args):
    """Handle status command."""
    status = get_gcp_status()
    
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print("\n🔧 GCP Integration Status")
        print("=" * 40)
        print(f"  Available:    {'✅ Yes' if status['gcp_available'] else '❌ No'}")
        print(f"  Configured:   {'✅ Yes' if status['gcp_configured'] else '❌ No'}")
        print(f"  Credentials:  {'✅ Set' if status['credentials_set'] else '❌ Not set'}")
        print(f"  Project ID:   {status['project_id'] or 'Not configured'}")
        print(f"  Region:       {status['region'] or 'Not configured'}")
        print(f"  BQ Dataset:   {status['bigquery_dataset'] or 'Not configured'}")
        print(f"  GCS Bucket:   {status['gcs_bucket'] or 'Not configured'}")
        
        if status['error']:
            print(f"\n⚠️  Error: {status['error']}")
        
        print()
    
    sys.exit(0 if status['gcp_available'] else 1)


def handle_archive(args):
    """Handle archive command."""
    # Load from input file if provided
    if args.input:
        try:
            with open(args.input, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load input file: {e}")
            sys.exit(1)
    else:
        data = {}
    
    # Override with command-line arguments
    project_id = args.project_id or data.get('project_id')
    project_name = args.project_name or data.get('project_name') or project_id
    mr_id = args.mr_id or data.get('mr_id')
    mr_url = args.mr_url or data.get('mr_url')
    mr_title = args.mr_title or data.get('mr_title')
    score = args.score if args.score is not None else data.get('compliance_score', 0)
    
    frameworks = []
    if args.frameworks:
        frameworks = [f.strip() for f in args.frameworks.split(',')]
    elif data.get('frameworks'):
        frameworks = data['frameworks']
    else:
        frameworks = ['SOC2', 'ISO27001']
    
    # Load findings
    findings = data.get('findings', [])
    if args.findings:
        try:
            with open(args.findings, 'r') as f:
                findings = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load findings file: {e}")
            sys.exit(1)
    
    # Load evidence
    evidence = data.get('evidence_package')
    if args.evidence:
        try:
            with open(args.evidence, 'r') as f:
                evidence = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load evidence file: {e}")
            sys.exit(1)
    
    # Validate required fields
    if not all([project_id, mr_id, mr_url]):
        logger.error("Missing required fields: project-id, mr-id, mr-url")
        sys.exit(1)
    
    # Archive results
    logger.info(f"Archiving compliance results for {project_id} MR !{mr_id}")
    
    results = archive_compliance_results(
        findings=findings,
        compliance_score=score,
        frameworks=frameworks,
        project_id=project_id,
        project_name=project_name,
        mr_id=mr_id,
        mr_url=mr_url,
        mr_title=mr_title,
        evidence_package=evidence,
        generate_pdf=not args.no_pdf
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results written to {args.output}")
    else:
        print(json.dumps(results, indent=2))
    
    # Print summary
    summary = results.get('summary', {})
    print("\n📊 Archive Summary")
    print("=" * 40)
    print(f"  Successful: {', '.join(summary.get('successful', [])) or 'None'}")
    print(f"  Failed:     {', '.join(summary.get('failed', [])) or 'None'}")
    print(f"  Skipped:    {', '.join(summary.get('skipped', [])) or 'None'}")
    print()
    
    # Exit with appropriate code
    if summary.get('failed'):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
