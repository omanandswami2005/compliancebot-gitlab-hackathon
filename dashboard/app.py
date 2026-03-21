"""
ComplianceBot Dashboard - Beautiful UI for Hackathon Demo
=========================================================
A Streamlit dashboard showing compliance analytics, reports, and evidence.

Run locally:
    streamlit run dashboard/app.py

Deploy to Streamlit Cloud:
    1. Push to GitHub/GitLab
    2. Go to share.streamlit.io
    3. Connect repo and deploy
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json

# Page config
st.set_page_config(
    page_title="ComplianceBot Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .dashboard-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .dashboard-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    .metric-card.critical { border-left-color: #e74c3c; }
    .metric-card.high { border-left-color: #f39c12; }
    .metric-card.medium { border-left-color: #3498db; }
    .metric-card.success { border-left-color: #27ae60; }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* Report cards */
    .report-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        border: 1px solid #eee;
    }
    
    .report-card:hover {
        box-shadow: 0 4px 25px rgba(0,0,0,0.1);
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-critical { background: #ffebee; color: #c62828; }
    .badge-high { background: #fff3e0; color: #ef6c00; }
    .badge-medium { background: #e3f2fd; color: #1565c0; }
    .badge-low { background: #e8f5e9; color: #2e7d32; }
    .badge-pass { background: #e8f5e9; color: #2e7d32; }
    .badge-fail { background: #ffebee; color: #c62828; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# MOCK DATA GENERATION (Replace with real BigQuery data when available)
# =============================================================================

@st.cache_data(ttl=300)
def generate_mock_findings():
    """Generate mock compliance findings data."""
    frameworks = ['SOC 2', 'ISO 27001', 'PCI-DSS', 'HIPAA']
    severities = ['critical', 'high', 'medium', 'low']
    controls = {
        'SOC 2': ['CC6.1', 'CC6.2', 'CC6.7', 'CC7.1', 'CC8.1'],
        'ISO 27001': ['A.8.2', 'A.9.4', 'A.10.1', 'A.12.6'],
        'PCI-DSS': ['6.3', '8.2', '10.2'],
        'HIPAA': ['164.312(a)', '164.312(b)', '164.312(e)']
    }
    
    data = []
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(200):
        framework = random.choice(frameworks)
        date = base_date + timedelta(days=random.randint(0, 90))
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
            'title': random.choice([
                'Hardcoded API key detected',
                'SQL injection vulnerability',
                'Weak password hashing',
                'Missing input validation',
                'Insecure session management',
                'Outdated dependency with CVE',
                'Debug mode enabled',
                'Missing encryption',
                'Excessive permissions',
                'Missing audit logging'
            ])
        })
    
    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def generate_mock_reports():
    """Generate mock PDF reports data."""
    reports = []
    for i in range(15):
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
            'url': f'https://storage.googleapis.com/compliance-evidence/reports/report-{i}.pdf'
        })
    return sorted(reports, key=lambda x: x['date'], reverse=True)


@st.cache_data(ttl=300)
def generate_mock_evidence():
    """Generate mock evidence packages data."""
    evidence = []
    for i in range(20):
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
            'url': f'https://storage.googleapis.com/compliance-evidence/evidence/evidence-{i}.json'
        })
    return sorted(evidence, key=lambda x: x['date'], reverse=True)


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.image("https://about.gitlab.com/images/press/logo/png/gitlab-logo-500.png", width=150)
    st.markdown("### 🛡️ ComplianceBot")
    st.markdown("---")
    
    # Filters
    st.markdown("#### 🔍 Filters")
    
    selected_projects = st.multiselect(
        "Projects",
        ['frontend-app', 'backend-api', 'data-service', 'auth-service'],
        default=['frontend-app', 'backend-api', 'data-service', 'auth-service']
    )
    
    selected_frameworks = st.multiselect(
        "Frameworks",
        ['SOC 2', 'ISO 27001', 'PCI-DSS', 'HIPAA'],
        default=['SOC 2', 'ISO 27001', 'PCI-DSS', 'HIPAA']
    )
    
    date_range = st.selectbox(
        "Time Range",
        ['Last 7 days', 'Last 30 days', 'Last 90 days', 'All time'],
        index=2
    )
    
    severity_filter = st.multiselect(
        "Severity",
        ['critical', 'high', 'medium', 'low'],
        default=['critical', 'high', 'medium', 'low']
    )
    
    st.markdown("---")
    
    # GCP Status
    st.markdown("#### ☁️ GCP Status")
    
    # Check if GCP is configured (mock for demo)
    gcp_configured = False  # Set to True when GCP is configured
    
    if gcp_configured:
        st.success("✅ Connected")
        st.caption("BigQuery: Active")
        st.caption("Cloud Storage: Active")
        st.caption("Vertex AI: Active")
    else:
        st.warning("⚠️ Demo Mode")
        st.caption("Using mock data")
        st.caption("Configure GCP for live data")
    
    st.markdown("---")
    st.markdown("#### 📚 Resources")
    st.markdown("[📖 Documentation](https://gitlab.com/gitlab-ai-hackathon/participants/35481656)")
    st.markdown("[🐛 Report Issue](https://gitlab.com/gitlab-ai-hackathon/participants/35481656/-/issues)")
    st.markdown("[🏆 Hackathon](https://gitlab.devpost.com)")


# =============================================================================
# HEADER
# =============================================================================

st.markdown("""
<div class="dashboard-header">
    <h1>🛡️ ComplianceBot Dashboard</h1>
    <p>Real-time compliance monitoring for GitLab merge requests</p>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# LOAD DATA
# =============================================================================

df = generate_mock_findings()
reports = generate_mock_reports()
evidence = generate_mock_evidence()

# Apply filters
df_filtered = df[
    (df['project'].isin(selected_projects)) &
    (df['framework'].isin(selected_frameworks)) &
    (df['severity'].isin(severity_filter))
]

if date_range == 'Last 7 days':
    df_filtered = df_filtered[df_filtered['date'] >= datetime.now() - timedelta(days=7)]
elif date_range == 'Last 30 days':
    df_filtered = df_filtered[df_filtered['date'] >= datetime.now() - timedelta(days=30)]
elif date_range == 'Last 90 days':
    df_filtered = df_filtered[df_filtered['date'] >= datetime.now() - timedelta(days=90)]


# =============================================================================
# METRICS ROW
# =============================================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    avg_score = df_filtered['compliance_score'].mean()
    st.metric(
        label="📊 Avg Compliance Score",
        value=f"{avg_score:.0f}/100",
        delta=f"+{random.randint(1, 5)}% vs last period"
    )

with col2:
    critical_count = len(df_filtered[df_filtered['severity'] == 'critical'])
    st.metric(
        label="🔴 Critical Findings",
        value=critical_count,
        delta=f"-{random.randint(1, 3)}" if critical_count > 0 else "0",
        delta_color="inverse"
    )

with col3:
    high_count = len(df_filtered[df_filtered['severity'] == 'high'])
    st.metric(
        label="🟠 High Findings",
        value=high_count,
        delta=f"-{random.randint(1, 5)}" if high_count > 0 else "0",
        delta_color="inverse"
    )

with col4:
    total_scans = len(df_filtered['mr_id'].unique())
    st.metric(
        label="🔍 MRs Scanned",
        value=total_scans,
        delta=f"+{random.randint(5, 15)}"
    )

with col5:
    remediated = len(df_filtered[df_filtered['status'] == 'remediated'])
    st.metric(
        label="✅ Remediated",
        value=remediated,
        delta=f"+{random.randint(3, 10)}"
    )


# =============================================================================
# CHARTS ROW
# =============================================================================

st.markdown('<div class="section-header">📈 Compliance Trends</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Compliance Score Trend
    daily_scores = df_filtered.groupby(df_filtered['date'].dt.date)['compliance_score'].mean().reset_index()
    daily_scores.columns = ['date', 'score']
    
    fig_trend = px.line(
        daily_scores,
        x='date',
        y='score',
        title='Compliance Score Over Time',
        labels={'date': 'Date', 'score': 'Average Score'},
        template='plotly_white'
    )
    fig_trend.update_traces(
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
    )
    fig_trend.add_hline(y=85, line_dash="dash", line_color="green", annotation_text="Pass Threshold (85)")
    fig_trend.update_layout(height=350)
    st.plotly_chart(fig_trend, use_container_width=True)

with chart_col2:
    # Findings by Severity
    severity_counts = df_filtered['severity'].value_counts().reset_index()
    severity_counts.columns = ['severity', 'count']
    
    colors = {'critical': '#e74c3c', 'high': '#f39c12', 'medium': '#3498db', 'low': '#27ae60'}
    
    fig_severity = px.pie(
        severity_counts,
        values='count',
        names='severity',
        title='Findings by Severity',
        color='severity',
        color_discrete_map=colors,
        hole=0.4
    )
    fig_severity.update_layout(height=350)
    st.plotly_chart(fig_severity, use_container_width=True)


# Second row of charts
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    # Findings by Framework
    framework_counts = df_filtered['framework'].value_counts().reset_index()
    framework_counts.columns = ['framework', 'count']
    
    fig_framework = px.bar(
        framework_counts,
        x='framework',
        y='count',
        title='Findings by Framework',
        color='framework',
        color_discrete_sequence=px.colors.qualitative.Set2,
        template='plotly_white'
    )
    fig_framework.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_framework, use_container_width=True)

with chart_col4:
    # Findings by Project
    project_counts = df_filtered.groupby('project').agg({
        'compliance_score': 'mean',
        'severity': 'count'
    }).reset_index()
    project_counts.columns = ['project', 'avg_score', 'findings']
    
    fig_project = px.bar(
        project_counts,
        x='project',
        y='avg_score',
        title='Average Compliance Score by Project',
        color='avg_score',
        color_continuous_scale='RdYlGn',
        template='plotly_white'
    )
    fig_project.add_hline(y=85, line_dash="dash", line_color="green")
    fig_project.update_layout(height=350)
    st.plotly_chart(fig_project, use_container_width=True)


# =============================================================================
# REPORTS SECTION
# =============================================================================

st.markdown('<div class="section-header">📄 Compliance Reports</div>', unsafe_allow_html=True)

# Filter reports
report_project_filter = st.selectbox(
    "Filter by Project",
    ['All Projects'] + list(set([r['project'] for r in reports])),
    key='report_filter'
)

filtered_reports = reports if report_project_filter == 'All Projects' else [r for r in reports if r['project'] == report_project_filter]

# Display reports in cards
for i in range(0, len(filtered_reports), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j < len(filtered_reports):
            report = filtered_reports[i + j]
            with col:
                status_class = 'badge-pass' if report['status'] == 'Pass' else 'badge-fail'
                st.markdown(f"""
                <div class="report-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>{report['id']}</strong>
                        <span class="badge {status_class}">{report['status']}</span>
                    </div>
                    <div style="color: #666; margin: 0.5rem 0;">
                        📁 {report['project']} • MR !{report['mr_id']}
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                        <span>📊 Score: <strong>{report['score']}/100</strong></span>
                        <span>🔍 {report['findings']} findings</span>
                    </div>
                    <div style="color: #888; font-size: 0.85rem; margin-top: 0.5rem;">
                        📅 {report['date'].strftime('%Y-%m-%d %H:%M')} • {report['size']}
                    </div>
                    <div style="margin-top: 0.5rem;">
                        {''.join([f'<span class="badge badge-medium" style="margin-right: 4px; font-size: 0.7rem;">{f}</span>' for f in report['frameworks'][:3]])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.download_button(
                    "📥 Download PDF",
                    data=b"Mock PDF content",  # Replace with actual PDF
                    file_name=f"{report['id']}.pdf",
                    mime="application/pdf",
                    key=f"dl_{report['id']}"
                )


# =============================================================================
# EVIDENCE SECTION
# =============================================================================

st.markdown('<div class="section-header">📦 Evidence Packages</div>', unsafe_allow_html=True)

# Evidence type filter
evidence_type_filter = st.selectbox(
    "Filter by Type",
    ['All Types', 'MR Approvals', 'Pipeline Logs', 'Access Audit', 'Security Scans'],
    key='evidence_filter'
)

filtered_evidence = evidence if evidence_type_filter == 'All Types' else [e for e in evidence if e['type'] == evidence_type_filter]

# Display evidence in a table
evidence_df = pd.DataFrame(filtered_evidence)
evidence_df['date'] = pd.to_datetime(evidence_df['date']).dt.strftime('%Y-%m-%d %H:%M')

st.dataframe(
    evidence_df[['id', 'project', 'type', 'date', 'items', 'controls_covered', 'size', 'hash']],
    use_container_width=True,
    hide_index=True,
    column_config={
        'id': st.column_config.TextColumn('ID', width='small'),
        'project': st.column_config.TextColumn('Project', width='medium'),
        'type': st.column_config.TextColumn('Type', width='medium'),
        'date': st.column_config.TextColumn('Date', width='medium'),
        'items': st.column_config.NumberColumn('Items', width='small'),
        'controls_covered': st.column_config.NumberColumn('Controls', width='small'),
        'size': st.column_config.TextColumn('Size', width='small'),
        'hash': st.column_config.TextColumn('Hash', width='medium'),
    }
)


# =============================================================================
# RECENT FINDINGS TABLE
# =============================================================================

st.markdown('<div class="section-header">🔍 Recent Findings</div>', unsafe_allow_html=True)

# Show recent findings
recent_findings = df_filtered.sort_values('date', ascending=False).head(20)

def severity_badge(severity):
    colors = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }
    return colors.get(severity, '⚪')

recent_findings['severity_icon'] = recent_findings['severity'].apply(severity_badge)
recent_findings['date_str'] = recent_findings['date'].dt.strftime('%Y-%m-%d')

st.dataframe(
    recent_findings[['date_str', 'project', 'severity_icon', 'severity', 'framework', 'control_id', 'title', 'status']],
    use_container_width=True,
    hide_index=True,
    column_config={
        'date_str': st.column_config.TextColumn('Date', width='small'),
        'project': st.column_config.TextColumn('Project', width='medium'),
        'severity_icon': st.column_config.TextColumn('', width='small'),
        'severity': st.column_config.TextColumn('Severity', width='small'),
        'framework': st.column_config.TextColumn('Framework', width='small'),
        'control_id': st.column_config.TextColumn('Control', width='small'),
        'title': st.column_config.TextColumn('Finding', width='large'),
        'status': st.column_config.TextColumn('Status', width='small'),
    }
)


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem;">
    <p>🛡️ <strong>ComplianceBot Dashboard</strong> | Built for GitLab AI Hackathon 2026</p>
    <p>
        <a href="https://gitlab.com/gitlab-ai-hackathon/participants/35481656" target="_blank">GitLab Repo</a> •
        <a href="https://gitlab.devpost.com" target="_blank">Hackathon</a> •
        <a href="https://docs.google.com/document/d/compliancebot" target="_blank">Documentation</a>
    </p>
</div>
""", unsafe_allow_html=True)
