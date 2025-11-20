# Afrobeats Playlist Observatory

Lightweight toolkit for exploring regional representation, curator concentration, label dynamics and temporal patterns across selected Spotify Afrobeats playlists. Provides ingestion scripts, a processed JSON dataset, a static web dashboard, and a simplified Streamlit dashboard.

## Project layout

```
web/                  Static dashboard (index + assets + data.js export)
scripts/              Ingestion, verification, analytics, Streamlit dashboard
data/raw/             Raw playlist payloads (per slug)
data/processed/       Normalized master dataset (afrobeats_playlists.json)
outputs/              Markdown summaries (bias report) and other derived artifacts
notebooks/            Optional exploratory notebooks
```

## Data pipeline

1. Configure `.env` with `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REFRESH_TOKEN`, `SPOTIFY_REDIRECT_URI`, and default `SPOTIFY_MARKET`.
2. Curate playlist coverage in `data/playlist_config.json` and regional metadata in `data/data/artist_metadata.csv`.
3. Run the ingestion script to refresh raw, processed, and dashboard data:

```powershell
C:/Users/Rilwan/AppData/Local/Microsoft/WindowsApps/python3.13.exe scripts/fetch_spotify_data.py
```

Outputs:
- `data/raw/<slug>.json` snapshots for auditability.
- `data/processed/afrobeats_playlists.json` master dataset.
- `web/data.js` browser-ready payload consumed by `web/index.html` and `web/assets/app.js`.

## Dashboards

- **Static web** (`web/index.html`): interactive client‑side dashboard powered by `web/data.js`.
- **Streamlit** (`scripts/dashboard.py`): simplified analytical view (Overview, Regional, Temporal, Label tabs).

### Artist metadata refresh

Update `data/data/artist_metadata.csv` then:
- Regenerate the processed dataset if playlist coverage changed.
- Reload the Streamlit app or static page to reflect new origin/diaspora annotations.

## Analysis script

`scripts/analyze_bias.py` computes selected bias indicators (e.g., regional concentration, label shares, popularity differences) and writes `outputs/analysis_summary.md`. Re-run after each ingestion refresh.

Audio feature generation & fetching scripts have been removed to preserve data integrity (simulated values discarded). The dataset intentionally excludes Spotify audio feature fields.

## Housekeeping

- Web assets live under `web/` only.
- Obsolete audio feature scripts removed (`generate_audio_features.py`, `fetch_audio_features.py`, `test_audio_features.py`, `export_audio_features_csv.py`).
- Streamlit dashboard simplified (no abstract, methodology, or audio feature tabs).
- Static HTML cleaned of research narrative; focused on operational metrics.

---

For a quick start after cloning:
```powershell
pip install -r requirements-dashboards.txt
python scripts\fetch_spotify_data.py
streamlit run scripts\dashboard.py
```

Serve the static dashboard (optional):
```powershell
python -m http.server 8000 -d web
```

Then browse to http://localhost:8000/index.html.
