# cloud_run/report_generator.py
from flask import Flask, request, jsonify
from google.cloud import storage
import anthropic
import json

app = Flask(__name__)

@app.route('/generate-report', methods=['POST'])
def generate_report():
    evidence = request.json['evidence_package']
    project_id = request.json['project_id']

    # Use Vertex AI / Anthropic to enhance report narrative
    client = anthropic.Anthropic()

    narrative = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"Generate an executive compliance narrative for auditors: {json.dumps(evidence)}"
        }]
    )

    # Generate PDF and upload to GCS
    pdf_bytes = generate_pdf(evidence, narrative.content[0].text)

    bucket = storage.Client().bucket('compliance-reports')
    blob = bucket.blob(f"{project_id}/report-{evidence['period']}.pdf")
    blob.upload_from_string(pdf_bytes, content_type='application/pdf')

    return jsonify({"report_url": blob.public_url})
