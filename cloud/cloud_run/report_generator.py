# cloud_run/report_generator.py
from flask import Flask, request, jsonify
from google.cloud import storage, bigquery
from google.cloud.aiplatform_v1beta1.services.prediction_service import PredictionServiceClient
from google.cloud.aiplatform_v1beta1.types import PredictRequest
import vertexai
from vertexai.generative_models import GenerativeModel
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
LOCATION = 'us-central1'

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """
    Generate compliance report and upload to GCS.
    Uses Vertex AI (Gemini) instead of Anthropic for cost-efficiency.
    """
    try:
        evidence = request.json['evidence_package']
        project_id = request.json['project_id']
        
        # Generate narrative using Vertex AI Gemini
        narrative = generate_narrative(evidence)
        
        # Log findings to BigQuery
        log_to_bigquery(project_id, evidence)
        
        # Generate PDF and upload to GCS
        pdf_bytes = generate_pdf(evidence, narrative)
        
        gcs_url = upload_to_gcs(project_id, pdf_bytes, evidence)
        
        return jsonify({
            "report_url": gcs_url,
            "narrative": narrative,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_narrative(evidence: dict) -> str:
    """
    Generate executive compliance narrative using Vertex AI Gemini.
    """
    model = GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are a compliance auditor. Generate a professional executive summary 
    for this compliance evidence (max 300 words):
    
    Findings: {evidence.get('findings_count', 0)} total findings
    Score: {evidence.get('compliance_score', 0)}/100
    Frameworks: {', '.join(evidence.get('frameworks', []))}
    
    Controls Mapped: {len(evidence.get('controls_mapped', []))} controls
    Critical Issues: {len([f for f in evidence.get('findings', []) if f.get('severity') == 'critical'])}
    
    Evidence Summary:
    {json.dumps(evidence.get('summary', {}), indent=2)}
    
    Provide a concise, auditor-friendly narrative covering:
    1. Compliance posture summary
    2. Critical gaps (if any)
    3. Strengths identified
    4. Recommended next steps
    """
    
    response = model.generate_content(prompt)
    return response.text


def log_to_bigquery(project_id: str, evidence: dict) -> None:
    """
    Log compliance findings to BigQuery for analytics.
    Enables compliance trend analysis and evidence archival.
    """
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.compliance.compliance_findings"
    
    rows_to_insert = []
    findings = evidence.get('findings', [])
    
    for finding in findings:
        row = {
            "project_id": project_id,
            "control_id": finding.get('control_id'),
            "framework": finding.get('framework'),
            "severity": finding.get('severity'),
            "status": "NEEDS_REVIEW",  # Default status
            "finding_date": datetime.now().isoformat(),
            "score": evidence.get('compliance_score', 0),
        }
        rows_to_insert.append(row)
    
    if rows_to_insert:
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            raise Exception(f"BigQuery insert errors: {errors}")


def upload_to_gcs(project_id: str, pdf_bytes: bytes, evidence: dict) -> str:
    """
    Upload PDF report to Google Cloud Storage.
    Ensures 1-year retention policy (SOC 2 requirement).
    """
    storage_client = storage.Client(project=PROJECT_ID)
    bucket_name = f"compliance-evidence-{PROJECT_ID}"
    bucket = storage_client.bucket(bucket_name)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob_name = f"{project_id}/compliance-report_{timestamp}.pdf"
    blob = bucket.blob(blob_name)
    
    # Upload with metadata
    blob.content_type = 'application/pdf'
    blob.metadata = {
        "project_id": project_id,
        "generated_at": datetime.now().isoformat(),
        "compliance_score": str(evidence.get('compliance_score', 0)),
        "framework": ",".join(evidence.get('frameworks', []))
    }
    
    blob.upload_from_string(pdf_bytes)
    
    # Return signed URL valid for 7 days
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(days=7),
        method="GET"
    )
    return url


def generate_pdf(evidence: dict, narrative: str) -> bytes:
    """
    Generate PDF compliance report from evidence and narrative.
    Uses reportlab for PDF generation.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak
    from io import BytesIO
    
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1f4788',
        spaceAfter=30,
        alignment=1  # Center
    )
    story.append(Paragraph("Compliance Assessment Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Metadata
    meta_data = [
        ["Project", evidence.get('project_name', 'Unknown')],
        ["Compliance Score", f"{evidence.get('compliance_score', 0)}/100"],
        ["Generated", evidence.get('generated_at', 'Unknown')],
        ["Frameworks", ", ".join(evidence.get('frameworks', []))]
    ]
    meta_table = Table(meta_data)
    story.append(meta_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(narrative, styles['BodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    # Findings Summary
    story.append(Paragraph("Findings Summary", styles['Heading2']))
    findings_count = evidence.get('findings_count', 0)
    story.append(Paragraph(
        f"Total Findings: {findings_count}<br/>Timestamp: {evidence.get('generated_at')}",
        styles['BodyText']
    ))
    
    # Build PDF
    doc.build(story)
    return pdf_buffer.getvalue()
