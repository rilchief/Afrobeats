# Afrobeats Playlist Gatekeeping Observatory

A reproducible toolkit for measuring regional representation, curator influence, and label bias across Spotify Afrobeats playlists. The repo bundles the ingestion scripts, cleaned dataset, statistical tests, and two dashboards (web + Streamlit).

## Project layout

```
web/                  Static dashboard (index + assets + data.js export)
scripts/              Data ingestion, Spotify helpers, analytics, Streamlit dashboard
data/raw/             Raw playlist payloads captured per slug
data/processed/       Normalized dataset consumed by analysis and dashboards
outputs/              Markdown/CSV/Parquet summaries (bias report, audio exports)
notebooks/            Narrative research notebook(s)
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

- **Static web** (`web/index.html`): rich exploratory UI pointing at `web/data.js`. The repository root `index.html` simply redirects here.
- **Streamlit** (`scripts/dashboard.py`): quick analytical playground; run with `streamlit run scripts/dashboard.py` if desired.

### Artist metadata refresh

- Both dashboards now reload `data/data/artist_metadata.csv` every time they start. Edit the CSV and simply refresh the browser (or rerun `streamlit run …`) to see updated country/region/diaspora annotations—no need to regenerate `web/data.js` first.
- For the static dashboard, serve the `web/` folder via a local web server (for example `python -m http.server 8000`) so the browser can fetch the CSV without file:// restrictions.

## Statistical analysis & tests

`scripts/analyze_bias.py` ingests the processed dataset, runs chi-square, ANOVA, and Kruskal–Wallis diagnostics, and writes `outputs/analysis_summary.md`. Re-run after every ingestion refresh to keep the bias summary in sync.

## Audio-feature limitation

`scripts/fetch_audio_features.py` remains optional. Spotify currently rejects `audio-features` requests (HTTP 403) for this app, so the live dataset excludes danceability/energy fields. Document the limitation in methodology write-ups; all primary analyses rely on curator mix, artist metadata, labels, popularity, and release year, which remain unaffected.

## Housekeeping

- Web assets now live exclusively inside `web/` (HTML, JS, CSS, data export).
- Legacy placeholders (`data/playlist.js`, `scripts/discover_afrobeats_playlists.py`, `scripts/verify_playlists.py`) were removed to avoid confusion.
- Use the new `README`, plus `notebooks/` narratives, to anchor academic submissions.
