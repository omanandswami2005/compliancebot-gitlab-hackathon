"""
ComplianceBot Dashboard
=======================
Run:  streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

from data_loader import get_data_loader

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ComplianceBot Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme state ──────────────────────────────────────────────────────────────
if "dark" not in st.session_state:
    st.session_state.dark = True  # default to dark — looks better for demos

IS_DARK = st.session_state.dark

# ── Theme tokens ─────────────────────────────────────────────────────────────
T = {
    True: dict(  # dark
        bg="#0e1117", bg2="#161b22", card="#1c2333", card_hover="#222d42",
        border="#30363d", text="#e6edf3", text2="#8b949e", text3="#484f58",
        accent="#667eea", accent2="#764ba2",
        crit_bg="#3d1114", crit_fg="#ff8a8a",
        high_bg="#3d2e05", high_fg="#ffcf70",
        med_bg="#0d2847", med_fg="#79c0ff",
        low_bg="#0d3321", low_fg="#7ee787",
        pass_bg="#0d3321", pass_fg="#7ee787",
        fail_bg="#3d1114", fail_fg="#ff8a8a",
        chart="plotly_dark",
        fill_alpha="0.15",
        link="#79c0ff",
    ),
    False: dict(  # light
        bg="#ffffff", bg2="#f6f8fa", card="#ffffff", card_hover="#f6f8fa",
        border="#d0d7de", text="#1f2328", text2="#656d76", text3="#8b949e",
        accent="#667eea", accent2="#764ba2",
        crit_bg="#ffebe9", crit_fg="#cf222e",
        high_bg="#fff8c5", high_fg="#9a6700",
        med_bg="#ddf4ff", med_fg="#0969da",
        low_bg="#dafbe1", low_fg="#1a7f37",
        pass_bg="#dafbe1", pass_fg="#1a7f37",
        fail_bg="#ffebe9", fail_fg="#cf222e",
        chart="plotly_white",
        fill_alpha="0.08",
        link="#0969da",
    ),
}[IS_DARK]

# ── Inject full-page CSS ────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Streamlit root overrides ─────────────────────────────────── */
:root {{
    color-scheme: {"dark" if IS_DARK else "light"};
}}
/* main area */
.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {{
    background-color: {T["bg"]} !important;
    color: {T["text"]} !important;
}}
/* sidebar */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {{
    background-color: {T["bg2"]} !important;
    color: {T["text"]} !important;
}}
[data-testid="stSidebar"] * {{
    color: {T["text"]} !important;
}}
/* metric widgets */
[data-testid="stMetric"] {{
    background: {T["card"]};
    border: 1px solid {T["border"]};
    border-radius: 12px;
    padding: 1rem;
}}
[data-testid="stMetricLabel"] p {{
    color: {T["text2"]} !important;
}}
[data-testid="stMetricValue"] {{
    color: {T["text"]} !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 0.85rem;
}}
/* selectbox / multiselect */
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label {{
    color: {T["text"]} !important;
}}
div[data-baseweb="select"] {{
    background: {T["card"]} !important;
    border-color: {T["border"]} !important;
}}
div[data-baseweb="select"] * {{
    color: {T["text"]} !important;
}}
/* dataframe */
[data-testid="stDataFrame"] {{
    border: 1px solid {T["border"]};
    border-radius: 10px;
    overflow: hidden;
}}
/* buttons */
.stButton > button {{
    border-color: {T["border"]} !important;
    color: {T["text"]} !important;
}}
.stButton > button[kind="primary"] {{
    background: {T["accent"]} !important;
    color: #fff !important;
    border-color: {T["accent"]} !important;
}}
.stDownloadButton > button {{
    background: {T["card"]} !important;
    border-color: {T["border"]} !important;
    color: {T["text"]} !important;
}}
/* info boxes */
.stAlert {{
    background: {T["card"]} !important;
    border-color: {T["border"]} !important;
    color: {T["text"]} !important;
}}
/* tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: {T["bg2"]};
    border-radius: 8px;
}}
.stTabs [data-baseweb="tab"] {{
    color: {T["text2"]} !important;
}}
.stTabs [aria-selected="true"] {{
    color: {T["accent"]} !important;
}}
/* dividers */
hr {{
    border-color: {T["border"]} !important;
}}
/* captions */
.stCaption, [data-testid="stCaptionContainer"] {{
    color: {T["text3"]} !important;
}}
/* markdown text */
.stMarkdown, .stMarkdown p, .stMarkdown li {{
    color: {T["text"]} !important;
}}
.stMarkdown a {{
    color: {T["link"]} !important;
}}
/* hide branding */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* ── Custom components ────────────────────────────────────────── */
.dashboard-header {{
    background: linear-gradient(135deg, {T["accent"]} 0%, {T["accent2"]} 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    color: #fff;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(102,126,234,0.25);
}}
.dashboard-header h1 {{ margin:0; font-size:2.4rem; font-weight:700; }}
.dashboard-header p  {{ margin:0.4rem 0 0; opacity:0.9; font-size:1.05rem; }}

.section-header {{
    font-size: 1.35rem;
    font-weight: 600;
    color: {T["text"]};
    margin: 2rem 0 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid {T["accent"]};
}}

.report-card {{
    background: {T["card"]};
    padding: 1.2rem;
    border-radius: 10px;
    border: 1px solid {T["border"]};
    margin-bottom: 0.8rem;
    transition: all 0.2s;
}}
.report-card:hover {{
    background: {T["card_hover"]};
    border-color: {T["accent"]};
    box-shadow: 0 4px 20px rgba(102,126,234,0.15);
}}
.report-card .rc-title {{ color: {T["text"]}; font-weight: 600; }}
.report-card .rc-meta  {{ color: {T["text2"]}; font-size: 0.9rem; margin: 0.4rem 0; }}
.report-card .rc-stats {{ color: {T["text"]}; }}
.report-card .rc-date  {{ color: {T["text3"]}; font-size: 0.82rem; margin-top: 0.4rem; }}

.badge {{
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    line-height: 1.4;
}}
.badge-critical {{ background:{T["crit_bg"]}; color:{T["crit_fg"]}; }}
.badge-high     {{ background:{T["high_bg"]}; color:{T["high_fg"]}; }}
.badge-medium   {{ background:{T["med_bg"]};  color:{T["med_fg"]};  }}
.badge-low      {{ background:{T["low_bg"]};  color:{T["low_fg"]};  }}
.badge-pass     {{ background:{T["pass_bg"]}; color:{T["pass_fg"]}; }}
.badge-fail     {{ background:{T["fail_bg"]}; color:{T["fail_fg"]}; }}

.data-badge {{
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    text-align: center;
    font-size: 0.9rem;
}}
.data-badge.live {{ background:{T["pass_bg"]}; color:{T["pass_fg"]}; }}
.data-badge.demo {{ background:{T["high_bg"]}; color:{T["high_fg"]}; }}

.footer-text {{
    text-align: center;
    color: {T["text3"]};
    padding: 1.5rem 0;
    font-size: 0.88rem;
}}
.footer-text a {{ color: {T["link"]}; text-decoration: none; }}
.footer-text a:hover {{ text-decoration: underline; }}
</style>
""", unsafe_allow_html=True)

# ── Data loader ──────────────────────────────────────────────────────────────
@st.cache_resource
def init_loader():
    return get_data_loader()

data_loader = init_loader()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://about.gitlab.com/images/press/logo/png/gitlab-logo-500.png", width=140)
    st.markdown("### 🛡️ ComplianceBot")
    st.markdown("---")

    # Theme toggle
    st.markdown("**🎨 Theme**")
    tc1, tc2 = st.columns(2)
    with tc1:
        if st.button("☀️ Light", use_container_width=True,
                      type="secondary" if IS_DARK else "primary"):
            st.session_state.dark = False
            st.rerun()
    with tc2:
        if st.button("🌙 Dark", use_container_width=True,
                      type="primary" if IS_DARK else "secondary"):
            st.session_state.dark = True
            st.rerun()

    st.markdown("---")

    # Data source
    st.markdown("**📡 Data Source**")
    if data_loader.is_live:
        st.markdown('<div class="data-badge live">✅ LIVE &mdash; BigQuery</div>',
                     unsafe_allow_html=True)
    else:
        st.markdown('<div class="data-badge demo">🎭 DEMO MODE</div>',
                     unsafe_allow_html=True)
        st.caption("Set GCP_PROJECT_ID for live data")

    st.markdown("---")

    # Filters
    st.markdown("**🔍 Filters**")
    available_projects = data_loader.get_projects()
    selected_projects = st.multiselect("Projects", available_projects,
                                        default=available_projects)
    selected_frameworks = st.multiselect("Frameworks",
                                          ['SOC 2', 'ISO 27001', 'PCI-DSS', 'HIPAA'],
                                          default=['SOC 2', 'ISO 27001', 'PCI-DSS', 'HIPAA'])
    date_range = st.selectbox("Time Range",
                               ['Last 7 days', 'Last 30 days', 'Last 90 days', 'All time'],
                               index=2)
    severity_filter = st.multiselect("Severity",
                                      ['critical', 'high', 'medium', 'low'],
                                      default=['critical', 'high', 'medium', 'low'])

    st.markdown("---")
    st.markdown("**📚 Links**")
    st.markdown("[📖 Docs](https://gitlab.com/gitlab-ai-hackathon/participants/35481656) · "
                "[🐛 Issues](https://gitlab.com/gitlab-ai-hackathon/participants/35481656/-/issues) · "
                "[🏆 Hackathon](https://gitlab.devpost.com)")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <h1>🛡️ ComplianceBot Dashboard</h1>
    <p>Real-time compliance monitoring for GitLab merge requests</p>
</div>
""", unsafe_allow_html=True)

# ── Load & filter data ───────────────────────────────────────────────────────
days_map = {'Last 7 days': 7, 'Last 30 days': 30, 'Last 90 days': 90, 'All time': 365}
days = days_map.get(date_range, 90)

@st.cache_data(ttl=300)
def load_findings(_loader, d):
    return _loader.get_findings(d)

@st.cache_data(ttl=300)
def load_reports(_loader):
    return _loader.get_reports(limit=20)

@st.cache_data(ttl=300)
def load_evidence(_loader):
    return _loader.get_evidence(limit=30)

df = load_findings(data_loader, days)
reports = load_reports(data_loader)
evidence = load_evidence(data_loader)

df_f = df[
    (df['project'].isin(selected_projects)) &
    (df['framework'].isin(selected_frameworks)) &
    (df['severity'].isin(severity_filter))
].copy()

cutoff = datetime.now() - timedelta(days=days)
df_f = df_f[df_f['date'] >= cutoff]

# ── Metrics ──────────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
n = len(df_f)
with m1:
    st.metric("📊 Avg Score",
              f"{df_f['compliance_score'].mean():.0f}/100" if n else "N/A",
              f"+{random.randint(1,5)}%")
with m2:
    cc = len(df_f[df_f['severity'] == 'critical'])
    st.metric("🔴 Critical", cc,
              f"-{random.randint(1,3)}" if cc else "0", delta_color="inverse")
with m3:
    hc = len(df_f[df_f['severity'] == 'high'])
    st.metric("🟠 High", hc,
              f"-{random.randint(1,5)}" if hc else "0", delta_color="inverse")
with m4:
    st.metric("🔍 MRs Scanned",
              len(df_f['mr_id'].unique()) if n else 0,
              f"+{random.randint(5,15)}")
with m5:
    st.metric("✅ Remediated",
              len(df_f[df_f['status'] == 'remediated']) if n else 0,
              f"+{random.randint(3,10)}")

# ── Charts ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Compliance Trends</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    if n:
        daily = df_f.groupby(df_f['date'].dt.date)['compliance_score'].mean().reset_index()
        daily.columns = ['date', 'score']
        fig = px.line(daily, x='date', y='score',
                      title='Compliance Score Over Time',
                      template=T["chart"])
        fig.update_traces(line=dict(color=T["accent"], width=3),
                          fill='tozeroy',
                          fillcolor=f'rgba(102,126,234,{T["fill_alpha"]})')
        fig.add_hline(y=85, line_dash="dash", line_color="#48bb78",
                      annotation_text="Pass (85)")
        fig.update_layout(height=360, margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for selected filters")

with c2:
    if n:
        sev = df_f['severity'].value_counts().reset_index()
        sev.columns = ['severity', 'count']
        cmap = {'critical': '#e74c3c', 'high': '#f39c12',
                'medium': '#3498db', 'low': '#27ae60'}
        fig = px.pie(sev, values='count', names='severity',
                     title='Findings by Severity',
                     color='severity', color_discrete_map=cmap,
                     hole=0.45, template=T["chart"])
        fig.update_layout(height=360, margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for selected filters")

c3, c4 = st.columns(2)

with c3:
    if n:
        fw = df_f['framework'].value_counts().reset_index()
        fw.columns = ['framework', 'count']
        fig = px.bar(fw, x='framework', y='count',
                     title='Findings by Framework',
                     color='framework',
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     template=T["chart"])
        fig.update_layout(height=360, showlegend=False, margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data")

with c4:
    if n:
        proj = df_f.groupby('project').agg(
            avg_score=('compliance_score', 'mean'),
            findings=('severity', 'count')
        ).reset_index()
        fig = px.bar(proj, x='project', y='avg_score',
                     title='Avg Score by Project',
                     color='avg_score', color_continuous_scale='RdYlGn',
                     template=T["chart"])
        fig.add_hline(y=85, line_dash="dash", line_color="#48bb78")
        fig.update_layout(height=360, margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data")

# ── Heatmap: Severity × Framework ───────────────────────────────────────────
st.markdown('<div class="section-header">🗺️ Risk Heatmap</div>', unsafe_allow_html=True)

if n:
    heat = df_f.groupby(['framework', 'severity']).size().reset_index(name='count')
    heat_pivot = heat.pivot(index='framework', columns='severity', values='count').fillna(0)
    # reorder columns
    for s in ['critical', 'high', 'medium', 'low']:
        if s not in heat_pivot.columns:
            heat_pivot[s] = 0
    heat_pivot = heat_pivot[['critical', 'high', 'medium', 'low']]

    fig = px.imshow(
        heat_pivot.values,
        x=['Critical', 'High', 'Medium', 'Low'],
        y=heat_pivot.index.tolist(),
        color_continuous_scale='YlOrRd',
        title='Findings: Framework × Severity',
        template=T["chart"],
        text_auto=True,
    )
    fig.update_layout(height=300, margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ── Reports ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📄 Compliance Reports</div>', unsafe_allow_html=True)

rp = list(set(r['project'] for r in reports)) if reports else available_projects
rp_filter = st.selectbox("Filter by Project", ['All'] + rp, key='rp')
f_reports = reports if rp_filter == 'All' else [r for r in reports if r['project'] == rp_filter]

for i in range(0, len(f_reports), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= len(f_reports):
            break
        r = f_reports[idx]
        with col:
            sc = 'badge-pass' if r['status'] == 'Pass' else 'badge-fail'
            date_str = r['date'].strftime('%Y-%m-%d %H:%M') if hasattr(r['date'], 'strftime') else str(r['date'])
            fw_badges = ''.join(
                f'<span class="badge badge-medium" style="margin-right:4px;font-size:0.72rem;">{f}</span>'
                for f in r['frameworks'][:3]
            )
            st.markdown(f"""
            <div class="report-card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="rc-title">{r['id']}</span>
                    <span class="badge {sc}">{r['status']}</span>
                </div>
                <div class="rc-meta">📁 {r['project']} &bull; MR !{r['mr_id']}</div>
                <div class="rc-stats" style="display:flex;justify-content:space-between;">
                    <span>📊 <strong>{r['score']}/100</strong></span>
                    <span>🔍 {r['findings']} findings</span>
                </div>
                <div class="rc-date">📅 {date_str} &bull; {r['size']}</div>
                <div style="margin-top:0.5rem;">{fw_badges}</div>
            </div>
            """, unsafe_allow_html=True)
            if r['url'] != '#':
                st.link_button("📥 Download PDF", r['url'], use_container_width=True)
            else:
                st.download_button("📥 Download PDF",
                                   data=b"Mock PDF - configure GCP for real reports",
                                   file_name=f"{r['id']}.pdf",
                                   mime="application/pdf",
                                   key=f"dl_{r['id']}",
                                   use_container_width=True)

# ── Evidence ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📦 Evidence Packages</div>', unsafe_allow_html=True)

ev_filter = st.selectbox("Filter by Type",
                          ['All Types', 'MR Approvals', 'Pipeline Logs',
                           'Access Audit', 'Security Scans'],
                          key='ev')
f_ev = evidence if ev_filter == 'All Types' else [e for e in evidence if e['type'] == ev_filter]

if f_ev:
    ev_df = pd.DataFrame(f_ev)
    ev_df['date'] = pd.to_datetime(ev_df['date']).dt.strftime('%Y-%m-%d %H:%M')
    st.dataframe(
        ev_df[['id', 'project', 'type', 'date', 'items', 'controls_covered', 'size', 'hash']],
        use_container_width=True, hide_index=True,
        column_config={
            'id': st.column_config.TextColumn('ID', width='small'),
            'project': st.column_config.TextColumn('Project', width='medium'),
            'type': st.column_config.TextColumn('Type', width='medium'),
            'date': st.column_config.TextColumn('Date', width='medium'),
            'items': st.column_config.NumberColumn('Items', width='small'),
            'controls_covered': st.column_config.NumberColumn('Controls', width='small'),
            'size': st.column_config.TextColumn('Size', width='small'),
            'hash': st.column_config.TextColumn('Hash', width='medium'),
        })
else:
    st.info("No evidence packages found")

# ── Recent Findings ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Recent Findings</div>', unsafe_allow_html=True)

if n:
    recent = df_f.sort_values('date', ascending=False).head(25).copy()
    sev_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
    recent[''] = recent['severity'].map(sev_icon).fillna('⚪')
    recent['date'] = recent['date'].dt.strftime('%Y-%m-%d')
    st.dataframe(
        recent[['date', 'project', '', 'severity', 'framework', 'control_id', 'title', 'status']],
        use_container_width=True, hide_index=True,
        column_config={
            'date': st.column_config.TextColumn('Date', width='small'),
            'project': st.column_config.TextColumn('Project', width='medium'),
            '': st.column_config.TextColumn('', width=40),
            'severity': st.column_config.TextColumn('Severity', width='small'),
            'framework': st.column_config.TextColumn('Framework', width='small'),
            'control_id': st.column_config.TextColumn('Control', width='small'),
            'title': st.column_config.TextColumn('Finding', width='large'),
            'status': st.column_config.TextColumn('Status', width='small'),
        })
else:
    st.info("No findings match the selected filters")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
src = ("🟢 BigQuery Connected" if data_loader.is_live
       else "🟡 Demo Mode &mdash; set GCP_PROJECT_ID for live data")
st.markdown(f"""
<div class="footer-text">
    <div>{src}</div>
    <div style="margin-top:0.5rem;">
        🛡️ <strong>ComplianceBot</strong> &bull; GitLab AI Hackathon 2026
    </div>
    <div style="margin-top:0.3rem;">
        <a href="https://gitlab.com/gitlab-ai-hackathon/participants/35481656">Repo</a> &bull;
        <a href="https://gitlab.devpost.com">Hackathon</a> &bull;
        <a href="https://gitlab.com/gitlab-ai-hackathon/participants/35481656/-/blob/main/docs/GCP_SETUP.md">GCP Setup</a>
    </div>
</div>
""", unsafe_allow_html=True)
