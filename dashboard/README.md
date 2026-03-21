# ComplianceBot Dashboard

A beautiful Streamlit dashboard for visualizing compliance analytics, reports, and evidence packages.

## Features

- 📊 **Compliance Score Trends** - Track scores over time
- 📈 **Findings Analytics** - Charts by severity, framework, project
- 📄 **PDF Reports** - Browse and download compliance reports
- 📦 **Evidence Packages** - View archived audit evidence
- 🔍 **Filters** - Filter by project, framework, severity, date range
- ☁️ **GCP Integration** - Connect to BigQuery for live data

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r dashboard/requirements.txt

# Run the dashboard
streamlit run dashboard/app.py

# Open in browser
# http://localhost:8501
```

### Deploy to Streamlit Cloud (Free)

1. Push code to GitLab/GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set main file: `dashboard/app.py`
5. Deploy!

### Deploy to Cloud Run

```bash
# Build and deploy
gcloud run deploy compliancebot-dashboard \
  --source dashboard/ \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

### Environment Variables

For live BigQuery data (optional):

```bash
export GCP_PROJECT_ID="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

### Streamlit Secrets

For Streamlit Cloud deployment, add secrets in the dashboard:

```toml
# .streamlit/secrets.toml
[gcp]
project_id = "your-project-id"
credentials = "base64-encoded-service-account-json"
```

## Screenshots

### Main Dashboard
![Dashboard](../docs/images/dashboard-main.png)

### Compliance Trends
![Trends](../docs/images/dashboard-trends.png)

### Reports List
![Reports](../docs/images/dashboard-reports.png)

## Demo Mode

By default, the dashboard runs in **demo mode** with mock data. This is perfect for hackathon demos!

To enable live data:
1. Configure GCP credentials
2. Set `gcp_configured = True` in `app.py`

## Customization

### Add Your Logo

Replace the GitLab logo URL in the sidebar:
```python
st.image("https://your-logo-url.png", width=150)
```

### Change Colors

Edit the CSS in the `st.markdown()` section:
```css
.dashboard-header {
    background: linear-gradient(135deg, #your-color 0%, #your-color 100%);
}
```

### Add More Charts

Use Plotly Express for quick charts:
```python
import plotly.express as px

fig = px.bar(df, x='category', y='value', title='My Chart')
st.plotly_chart(fig, use_container_width=True)
```

## Tech Stack

- **Streamlit** - Dashboard framework
- **Plotly** - Interactive charts
- **Pandas** - Data manipulation
- **Google Cloud** - BigQuery, Cloud Storage (optional)
