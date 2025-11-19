"""Plotly Dash dashboard for analysing gatekeeping dynamics in Afrobeats playlists."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, dash_table, dcc, html

# Constants
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "processed" / "afrobeats_playlists.json"
ARTIST_METADATA_PATH = REPO_ROOT / "data" / "data" / "artist_metadata.csv"
MAJOR_LABEL_KEYWORDS = (
    "sony", "columbia", "rca", "arista", "warner", "atlantic", "def jam",
    "interscope", "island", "virgin", "polydor", "umg", "universal",
    "motown", "republic", "emi", "capitol",
)

# Helper functions
def classify_label(label: str | None) -> str:
    if not label:
        return "Unknown"
    normalized = label.lower().strip()
    if not normalized:
        return "Unknown"
    for keyword in MAJOR_LABEL_KEYWORDS:
        if keyword in normalized:
            return "Major"
    if "independent" in normalized or "self" in normalized:
        return "Independent"
    return "Independent"


def load_artist_metadata(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

    df = df.rename(columns={
        "artistCountry": "artistCountry",
        "regionGroup": "regionGroup",
        "diaspora": "diaspora",
        "artist": "artist",
    })
    df["artist"] = df.get("artist", pd.Series(dtype=str)).fillna("").astype(str).str.strip()
    df = df.loc[df["artist"].ne("")].copy()
    if df.empty:
        return pd.DataFrame()
    df["artistCountry"] = df.get("artistCountry", pd.Series(dtype=str)).fillna("Unknown").astype(str)
    df["regionGroup"] = df.get("regionGroup", pd.Series(dtype=str)).fillna("Unknown").astype(str)
    df["diaspora"] = (
        df.get("diaspora", pd.Series(dtype=str))
        .fillna("false")
        .astype(str)
        .str.lower()
        .isin({"true", "1", "yes", "y"})
    )
    return df


def normalize_artist_name(value: str | None) -> str:
    if not value:
        return ""
    primary = str(value).split(",")[0]
    return primary.strip().lower()


def apply_artist_metadata(tracks_df: pd.DataFrame, metadata_df: pd.DataFrame) -> pd.DataFrame:
    working = tracks_df.copy()
    metadata_df = metadata_df.copy()
    metadata_df["artist_norm"] = metadata_df["artist"].map(normalize_artist_name)
    lookup = metadata_df.set_index("artist_norm")[
        ["artistCountry", "regionGroup", "diaspora"]
    ].to_dict("index")
    if not lookup:
        return working

    def enrich_row(row: pd.Series) -> pd.Series:
        key = normalize_artist_name(row.get("artist"))
        meta = lookup.get(key)
        if not meta:
            return row
        row["artist_country"] = meta.get("artistCountry") or row.get("artist_country") or "Unknown"
        row["region_group"] = meta.get("regionGroup") or row.get("region_group") or "Unknown"
        row["diaspora"] = bool(meta.get("diaspora"))
        return row

    return working.apply(enrich_row, axis=1)


def load_dataset(path: Path = DATA_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")
    
    payload = json.loads(path.read_text(encoding="utf-8"))
    playlists = payload.get("playlists", [])
    metadata = payload.get("runMetadata", {})

    playlist_rows: List[Dict] = []
    track_rows: List[Dict] = []

    for playlist in playlists:
        playlist_row = {
            "playlist_id": playlist.get("id"),
            "playlist_name": playlist.get("name"),
            "curator_type": playlist.get("curatorType"),
            "curator": playlist.get("curator"),
            "follower_count": playlist.get("followerCount"),
            "launch_year": playlist.get("launchYear"),
            "description": playlist.get("description"),
            "track_total": len(playlist.get("tracks") or []),
        }
        playlist_rows.append(playlist_row)

        for track in playlist.get("tracks") or []:
            track_rows.append({
                "playlist_id": playlist.get("id"),
                "playlist_name": playlist.get("name"),
                "curator_type": playlist.get("curatorType"),
                "curator": playlist.get("curator"),
                "follower_count": playlist.get("followerCount"),
                "track_id": track.get("id"),
                "track_title": track.get("title"),
                "artist": track.get("artist"),
                "artist_country": track.get("artistCountry", "Unknown") or "Unknown",
                "region_group": track.get("regionGroup", "Unknown") or "Unknown",
                "diaspora": bool(track.get("diaspora")),
                "release_year": track.get("releaseYear"),
                "track_popularity": track.get("trackPopularity"),
                "artist_popularity": track.get("artistPopularity"),
                "playlist_position": track.get("playlistPosition"),
                "album_label": track.get("albumLabel") or "Unknown",
                "label_type": classify_label(track.get("albumLabel")),
            })

    playlists_df = pd.DataFrame(playlist_rows).drop_duplicates("playlist_id")
    tracks_df = pd.DataFrame(track_rows)

    if not tracks_df.empty:
        tracks_df["release_year"] = pd.to_numeric(tracks_df["release_year"], errors="coerce")
        tracks_df["follower_count"] = pd.to_numeric(tracks_df["follower_count"], errors="coerce")
        tracks_df["track_popularity"] = pd.to_numeric(tracks_df["track_popularity"], errors="coerce")
        tracks_df["artist_popularity"] = pd.to_numeric(tracks_df["artist_popularity"], errors="coerce")
        tracks_df["playlist_position"] = pd.to_numeric(tracks_df["playlist_position"], errors="coerce")

        artist_metadata = load_artist_metadata(ARTIST_METADATA_PATH)
        if not artist_metadata.empty:
            tracks_df = apply_artist_metadata(tracks_df, artist_metadata)

    return playlists_df, tracks_df, metadata


# Load data
playlists_df, tracks_df, run_metadata = load_dataset()

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
    title="Afrobeats Observatory | Dash"
)

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background: linear-gradient(135deg, #0B0E11 0%, #1A1F2E 100%);
                font-family: 'Inter', sans-serif;
            }
            .card {
                background: rgba(19, 24, 33, 0.95) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 16px !important;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25) !important;
            }
            .metric-card {
                text-align: center;
                padding: 1.5rem;
                background: rgba(19, 24, 33, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
            }
            .metric-value {
                font-size: 2rem;
                font-weight: 700;
                color: #FFB400;
                margin: 0.5rem 0;
            }
            .metric-label {
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 1.2px;
                color: #B3B8C2;
                font-weight: 600;
            }
            .nav-tabs .nav-link {
                background: transparent !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                border-radius: 999px !important;
                color: #B3B8C2 !important;
                margin-right: 0.5rem !important;
                padding: 0.5rem 1.5rem !important;
            }
            .nav-tabs .nav-link.active {
                background: linear-gradient(135deg, #FFB400 0%, #FF8C00 100%) !important;
                color: #111 !important;
                border-color: #FFB400 !important;
            }
            .badge-custom {
                background: rgba(255, 180, 0, 0.15);
                border: 1px solid rgba(255, 180, 0, 0.3);
                border-radius: 999px;
                padding: 0.5rem 1.25rem;
                color: #FFB400;
                font-size: 0.85rem;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                display: inline-block;
                margin-bottom: 1rem;
            }
            h1, h2, h3, h4 {
                color: #FFB400 !important;
                font-family: Georgia, serif;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div("MSc Computing & Data Science Dissertation", className="badge-custom text-center"),
            ], style={'textAlign': 'center', 'marginTop': '2rem'}),
            html.H1("🎵 Afrobeats Playlist Gatekeeping Observatory", 
                   className="text-center mt-3"),
            html.P("An interactive analytical platform examining regional representation, curator concentration, "
                  "and temporal patterns in Spotify's Afrobeats ecosystem.",
                  className="text-center text-muted mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        # Sidebar Filters
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🎛️ Filters", className="mb-3"),
                    html.Hr(),
                    
                    html.Label("🔍 Search Playlist"),
                    dcc.Input(
                        id='search-input',
                        type='text',
                        placeholder='Type playlist name...',
                        className='form-control mb-3',
                        style={'background': 'rgba(255,255,255,0.04)', 'border': '1px solid rgba(255,255,255,0.08)', 'color': '#F7F8FA'}
                    ),
                    
                    html.Label("🎭 Curator Type"),
                    dcc.Dropdown(
                        id='curator-filter',
                        options=[{'label': c, 'value': c} for c in sorted(tracks_df['curator_type'].dropna().unique())],
                        value=sorted(tracks_df['curator_type'].dropna().unique()),
                        multi=True,
                        className='mb-3',
                        style={'background': '#131821', 'color': '#F7F8FA'}
                    ),
                    
                    html.Label("🌍 Region"),
                    dcc.Dropdown(
                        id='region-filter',
                        options=[{'label': r, 'value': r} for r in sorted(tracks_df['region_group'].fillna("Unknown").unique())],
                        value=sorted(tracks_df['region_group'].fillna("Unknown").unique()),
                        multi=True,
                        className='mb-3'
                    ),
                    
                    html.Label("🏢 Label Type"),
                    dcc.Dropdown(
                        id='label-filter',
                        options=[{'label': l, 'value': l} for l in sorted(tracks_df['label_type'].fillna("Unknown").unique())],
                        value=sorted(tracks_df['label_type'].fillna("Unknown").unique()),
                        multi=True,
                        className='mb-3'
                    ),
                    
                    html.Label("📅 Release Year Range"),
                    dcc.RangeSlider(
                        id='year-slider',
                        min=int(tracks_df['release_year'].min()) if not tracks_df['release_year'].isna().all() else 2000,
                        max=int(tracks_df['release_year'].max()) if not tracks_df['release_year'].isna().all() else 2025,
                        value=[
                            int(tracks_df['release_year'].min()) if not tracks_df['release_year'].isna().all() else 2000,
                            int(tracks_df['release_year'].max()) if not tracks_df['release_year'].isna().all() else 2025
                        ],
                        marks={i: str(i) for i in range(
                            int(tracks_df['release_year'].min()) if not tracks_df['release_year'].isna().all() else 2000,
                            int(tracks_df['release_year'].max()) if not tracks_df['release_year'].isna().all() else 2025,
                            5
                        )},
                        className='mb-3'
                    ),
                    
                    dbc.Checklist(
                        id='diaspora-check',
                        options=[{'label': ' ✨ Diaspora Artists Only', 'value': 'diaspora'}],
                        value=[],
                        className='mb-3'
                    ),
                ])
            ], className="card mb-3"),
        ], width=3),
        
        # Main Content
        dbc.Col([
            dbc.Tabs([
                # Overview Tab
                dbc.Tab([
                    dbc.Row([
                        dbc.Col(html.Div(id='metric-playlists', className='metric-card'), width=2),
                        dbc.Col(html.Div(id='metric-tracks', className='metric-card'), width=2),
                        dbc.Col(html.Div(id='metric-nigeria', className='metric-card'), width=2),
                        dbc.Col(html.Div(id='metric-diaspora', className='metric-card'), width=2),
                        dbc.Col(html.Div(id='metric-diversity', className='metric-card'), width=2),
                        dbc.Col(html.Div(id='metric-labels', className='metric-card'), width=2),
                    ], className='mb-4 mt-4'),
                    
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='region-chart'), width=6),
                        dbc.Col(dcc.Graph(id='release-chart'), width=6),
                    ], className='mb-4'),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H4("Playlist Breakdown"),
                            html.Div(id='playlist-table')
                        ], width=12)
                    ])
                ], label="📊 Overview", tab_id="tab-overview"),
                
                # Regional Analysis Tab
                dbc.Tab([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='region-map'), width=12)
                    ], className='mb-4 mt-4'),
                    
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='popularity-chart'), width=12)
                    ])
                ], label="🌍 Regional Analysis", tab_id="tab-regional"),
                
                # Temporal Tab
                dbc.Tab([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='exposure-chart'), width=12)
                    ], className='mb-4 mt-4'),
                    
                    dbc.Row([
                        dbc.Col(html.Div(id='preview-table'), width=12)
                    ])
                ], label="📅 Temporal Trends", tab_id="tab-temporal"),
                
                # Label Distribution Tab
                dbc.Tab([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='curator-chart'), width=12)
                    ], className='mb-4 mt-4'),
                    
                    dbc.Row([
                        dbc.Col(html.Div(id='label-stats'), width=12)
                    ])
                ], label="🏢 Label Distribution", tab_id="tab-labels"),
                
                # Methodology Tab
                dbc.Tab([
                    dbc.Row([
                        dbc.Col([
                            html.H3("📚 Research Methodology", className="mt-4"),
                            html.Hr(),
                            
                            html.H5("Data Collection"),
                            html.P("Playlist data was systematically extracted via the Spotify Web API, targeting influential "
                                  "Afrobeats playlists across editorial, algorithmic, and user-generated categories."),
                            
                            html.H5("Artist Metadata Enrichment"),
                            html.P("Artist origins were verified and coded into regional classifications (West Africa, East Africa, "
                                  "Southern Africa, Diaspora) and country-level granularity."),
                            
                            html.H5("Analytical Framework"),
                            html.P("Representation metrics computed include track counts, playlist penetration, follower-weighted "
                                  "exposure, position-based prominence, and regional diversity indices."),
                            
                            html.H5("Interactive Visualization"),
                            html.P("This Plotly Dash dashboard implements client-side filtering with reactive callbacks, "
                                  "multi-dimensional analysis perspectives, and data export capabilities."),
                            
                            html.Hr(),
                            html.H5("📄 Citation"),
                            html.Pre("""@misc{afrobeats_observatory_2025,
  author = {MSc Candidate},
  title = {Afrobeats Playlist Gatekeeping Observatory},
  year = {2025},
  howpublished = {MSc Computing & Data Science Dissertation}
}""", style={'background': 'rgba(255,180,0,0.1)', 'padding': '1rem', 'borderLeft': '4px solid #FFB400'})
                        ], width=12)
                    ])
                ], label="📚 Methodology", tab_id="tab-methodology"),
            ], id="tabs", active_tab="tab-overview"),
        ], width=9)
    ])
], fluid=True, style={'paddingBottom': '3rem'})


# Callbacks
@app.callback(
    [Output('metric-playlists', 'children'),
     Output('metric-tracks', 'children'),
     Output('metric-nigeria', 'children'),
     Output('metric-diaspora', 'children'),
     Output('metric-diversity', 'children'),
     Output('metric-labels', 'children'),
     Output('region-chart', 'figure'),
     Output('release-chart', 'figure'),
     Output('playlist-table', 'children'),
     Output('region-map', 'figure'),
     Output('popularity-chart', 'figure'),
     Output('exposure-chart', 'figure'),
     Output('curator-chart', 'figure'),
     Output('preview-table', 'children'),
     Output('label-stats', 'children')],
    [Input('search-input', 'value'),
     Input('curator-filter', 'value'),
     Input('region-filter', 'value'),
     Input('label-filter', 'value'),
     Input('year-slider', 'value'),
     Input('diaspora-check', 'value')]
)
def update_dashboard(search_text, curator_types, regions, labels, year_range, diaspora_check):
    # Filter data
    filtered = tracks_df.copy()
    
    if search_text:
        filtered = filtered[filtered['playlist_name'].str.contains(search_text, case=False, na=False)]
    if curator_types:
        filtered = filtered[filtered['curator_type'].isin(curator_types)]
    if regions:
        filtered = filtered[filtered['region_group'].isin(regions)]
    if labels:
        filtered = filtered[filtered['label_type'].isin(labels)]
    if year_range:
        filtered = filtered[filtered['release_year'].between(year_range[0], year_range[1])]
    if 'diaspora' in diaspora_check:
        filtered = filtered[filtered['diaspora'] == True]
    
    if filtered.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data matches filters", showarrow=False)
        empty_fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(19,24,33,0.95)', plot_bgcolor='rgba(19,24,33,0.95)')
        return ([html.Div("0", className='metric-value'), html.Div("Playlists", className='metric-label')] * 6 + 
                [empty_fig] * 7 + [html.Div("No data")] * 2)
    
    # Calculate metrics
    playlist_count = filtered['playlist_id'].nunique()
    track_count = len(filtered)
    nigeria_share = (filtered['artist_country'].str.lower() == 'nigeria').mean() * 100
    diaspora_share = filtered['diaspora'].mean() * 100
    diversity = filtered[filtered['region_group'] != 'Unknown'].groupby('playlist_id')['region_group'].nunique().mean()
    major_label_share = (filtered['label_type'] == 'Major').mean() * 100
    
    # Metric cards
    metric1 = [html.Div(f"{playlist_count:,}", className='metric-value'), html.Div("Playlists", className='metric-label')]
    metric2 = [html.Div(f"{track_count:,}", className='metric-value'), html.Div("Tracks", className='metric-label')]
    metric3 = [html.Div(f"{nigeria_share:.0f}%", className='metric-value'), html.Div("Nigeria Share", className='metric-label')]
    metric4 = [html.Div(f"{diaspora_share:.0f}%", className='metric-value'), html.Div("Diaspora Share", className='metric-label')]
    metric5 = [html.Div(f"{diversity:.1f}", className='metric-value'), html.Div("Avg Regions/PL", className='metric-label')]
    metric6 = [html.Div(f"{major_label_share:.0f}%", className='metric-value'), html.Div("Major Labels", className='metric-label')]
    
    # Region chart
    region_counts = filtered.groupby('region_group')['track_id'].count().sort_values(ascending=False)
    region_fig = px.bar(x=region_counts.index, y=region_counts.values, 
                       labels={'x': 'Region', 'y': 'Tracks'},
                       title='Regional Representation',
                       template='plotly_dark')
    region_fig.update_layout(paper_bgcolor='rgba(19,24,33,0.95)', plot_bgcolor='rgba(19,24,33,0.95)')
    region_fig.update_traces(marker_color='#FFB400')
    
    # Release year chart
    release_fig = px.histogram(filtered.dropna(subset=['release_year']), x='release_year',
                              title='Release Year Distribution',
                              template='plotly_dark')
    release_fig.update_layout(paper_bgcolor='rgba(19,24,33,0.95)', plot_bgcolor='rgba(19,24,33,0.95)')
    release_fig.update_traces(marker_color='#FF8C00')
    
    # Playlist table
    playlist_summary = filtered.groupby('playlist_name').agg({
        'track_id': 'count',
        'follower_count': 'first',
        'curator_type': 'first'
    }).reset_index().sort_values('follower_count', ascending=False).head(20)
    playlist_summary.columns = ['Playlist', 'Tracks', 'Followers', 'Curator Type']
    
    playlist_table = dash_table.DataTable(
        data=playlist_summary.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in playlist_summary.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'backgroundColor': 'rgba(19,24,33,0.95)', 'color': '#F7F8FA', 'border': '1px solid rgba(255,255,255,0.08)'},
        style_header={'backgroundColor': '#131821', 'fontWeight': 'bold', 'color': '#FFB400'},
        page_size=10
    )
    
    # Region map
    country_data = filtered[filtered['artist_country'] != 'Unknown'].groupby('artist_country').agg({
        'track_id': 'count',
        'track_popularity': 'mean'
    }).reset_index()
    country_data.columns = ['country', 'tracks', 'avg_popularity']
    
    map_fig = px.choropleth(country_data, locations='country', locationmode='country names',
                           color='tracks', hover_data=['avg_popularity'],
                           title='Global Footprint by Country',
                           template='plotly_dark',
                           color_continuous_scale='Viridis')
    map_fig.update_layout(paper_bgcolor='rgba(19,24,33,0.95)', plot_bgcolor='rgba(19,24,33,0.95)')
    
    # Popularity chart
    pop_by_region = filtered.groupby('region_group')['track_popularity'].mean().sort_values(ascending=False)
    pop_fig = px.bar(x=pop_by_region.index, y=pop_by_region.values,
                    labels={'x': 'Region', 'y': 'Avg Popularity'},
                    title='Regional Popularity',
                    template='plotly_dark')
    pop_fig.update_layout(paper_bgcolor='rgba(19,24,33,0.95)', plot_bgcolor='rgba(19,24,33,0.95)')
    pop_fig.update_traces(marker_color='#2ECC71')
    
    # Exposure chart
    top_artists = filtered.groupby('artist')['track_id'].count().sort_values(ascending=False).head(20)
    exp_fig = px.bar(x=top_artists.values, y=top_artists.index,
                    labels={'x': 'Track Placements', 'y': 'Artist'},
                    title='Top Artists by Exposure',
                    template='plotly_dark',
                    orientation='h')
    exp_fig.update_layout(paper_bgcolor='rgba(19,24,33,0.95)', plot_bgcolor='rgba(19,24,33,0.95)')
    exp_fig.update_traces(marker_color='#FFB400')
    
    # Curator chart
    curator_stats = filtered.groupby('curator_type').agg({
        'track_id': 'count',
        'artist_country': lambda x: (x.str.lower() == 'nigeria').mean() * 100
    }).reset_index()
    curator_stats.columns = ['Curator Type', 'Tracks', 'Nigeria Share (%)']
    
    curator_fig = px.bar(curator_stats, x='Curator Type', y='Nigeria Share (%)',
                        title='Curator Concentration (Nigeria Share)',
                        template='plotly_dark')
    curator_fig.update_layout(paper_bgcolor='rgba(19,24,33,0.95)', plot_bgcolor='rgba(19,24,33,0.95)')
    curator_fig.update_traces(marker_color='#E74C3C')
    
    # Preview table
    preview = filtered[['track_title', 'artist', 'playlist_name', 'track_popularity', 'region_group']].head(50)
    preview.columns = ['Track', 'Artist', 'Playlist', 'Popularity', 'Region']
    
    preview_table = dash_table.DataTable(
        data=preview.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in preview.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'backgroundColor': 'rgba(19,24,33,0.95)', 'color': '#F7F8FA', 'border': '1px solid rgba(255,255,255,0.08)'},
        style_header={'backgroundColor': '#131821', 'fontWeight': 'bold', 'color': '#FFB400'},
        page_size=25
    )
    
    # Label stats
    label_summary = filtered.groupby('label_type').agg({
        'track_id': 'count',
        'track_popularity': 'mean',
        'diaspora': lambda x: x.mean() * 100
    }).reset_index()
    label_summary.columns = ['Label Type', 'Tracks', 'Avg Popularity', 'Diaspora Share (%)']
    label_summary['Avg Popularity'] = label_summary['Avg Popularity'].round(1)
    label_summary['Diaspora Share (%)'] = label_summary['Diaspora Share (%)'].round(1)
    
    label_table = dash_table.DataTable(
        data=label_summary.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in label_summary.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'backgroundColor': 'rgba(19,24,33,0.95)', 'color': '#F7F8FA', 'border': '1px solid rgba(255,255,255,0.08)'},
        style_header={'backgroundColor': '#131821', 'fontWeight': 'bold', 'color': '#FFB400'},
    )
    
    return (metric1, metric2, metric3, metric4, metric5, metric6,
            region_fig, release_fig, playlist_table,
            map_fig, pop_fig, exp_fig, curator_fig,
            preview_table, label_table)


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
