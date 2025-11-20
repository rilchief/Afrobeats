# Afrobeats Dashboard Quick Guide

Simplified overview of the two dashboard options now focused purely on data exploration (research abstract, audio feature, and methodology content removed).

## Options

### 1. Streamlit (`scripts/dashboard.py`)
Tabs: Overview · Regional Analysis · Temporal Trends · Label Distribution.

Run:
```powershell
streamlit run scripts/dashboard.py
```
URL: http://localhost:8501

### 2. Plotly Dash (`scripts/dashboard_dash.py`)
Run:
```powershell
python scripts/dashboard_dash.py
```
URL: http://localhost:8050

## Install
```powershell
pip install -r requirements-dashboards.txt
```

## Data prerequisites
- Processed dataset: `data/processed/afrobeats_playlists.json`
- Artist metadata: `data/data/artist_metadata.csv`
Refresh via:
```powershell
python scripts/fetch_spotify_data.py
```

## Features (common)
- Multi-filter (curator, region, label, year, diaspora)
- Key metrics (playlist count, Nigeria share, diaspora share, diversity)
- Country spotlight & regional distribution
- Popularity & exposure charts
- Label concentration analysis
- CSV export (Streamlit)

## Removed
- Audio feature simulation & analysis
- Methodology / citation tabs
- Abstract and research narrative from static site

## Troubleshooting
Port busy:
```powershell
streamlit run scripts/dashboard.py --server.port 8502
```
Missing packages:
```powershell
pip install --upgrade pandas plotly streamlit dash dash-bootstrap-components
```

## Suggested workflow
Exploration: Streamlit
Deployment / portfolio: Plotly Dash
Static snapshot: `web/index.html`

## Next enhancements (optional)
- Comparative playlist mode
- Filter state persistence
- Export summary report (PDF/Markdown)

## Quick start
```powershell
pip install -r requirements-dashboards.txt
python scripts\fetch_spotify_data.py
streamlit run scripts\dashboard.py
```
