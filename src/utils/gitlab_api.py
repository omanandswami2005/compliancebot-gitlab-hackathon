# src/utils/gitlab_api.py
import os
import gitlab

def get_gitlab_client() -> gitlab.Gitlab:
    """Get authenticated GitLab client from CI environment."""
    return gitlab.Gitlab(
        os.environ['CI_SERVER_URL'],
        private_token=os.environ.get('AI_FLOW_GITLAB_TOKEN') or
                      os.environ.get('GITLAB_TOKEN')
    )

def post_compliance_comment(project_id: str, mr_iid: int, score: int, findings_count: int):
    """Post a compliance score badge as an MR comment."""
    gl = get_gitlab_client()
    project = gl.projects.get(project_id)
    mr = project.mergerequests.get(mr_iid)

    color = "brightgreen" if score >= 85 else "yellow" if score >= 70 else "red"
    badge_url = f"https://img.shields.io/badge/compliance-{score}%25-{color}"

    comment = f"""## 🔒 ComplianceBot Scan Results

![Compliance Score]({badge_url})

**Score: {score}/100** | **Findings: {findings_count}**

{'✅ This MR meets compliance requirements.' if score >= 85 else '⚠️ Review compliance findings before merging.'}

[View Full Report](../issues?label_name=compliance)
"""

    mr.notes.create({'body': comment})

def create_compliance_issue(project_id: str, report_markdown: str, labels: list):
    """Create a GitLab issue with the compliance report."""
    gl = get_gitlab_client()
    project = gl.projects.get(project_id)

    project.issues.create({
        'title': f'🔒 Compliance Report — {os.environ.get("CI_COMMIT_REF_NAME", "main")}',
        'description': report_markdown,
        'labels': labels,
        'assignee_ids': []
    })
