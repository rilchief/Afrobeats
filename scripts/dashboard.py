"""Streamlit dashboard for analysing gatekeeping dynamics in Afrobeats playlists."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "processed" / "afrobeats_playlists.json"
ARTIST_METADATA_PATH = REPO_ROOT / "data" / "data" / "artist_metadata.csv"
MAJOR_LABEL_KEYWORDS = (
    "sony",
    "columbia",
    "rca",
    "arista",
    "warner",
    "atlantic",
    "def jam",
    "interscope",
    "island",
    "virgin",
    "polydor",
    "umg",
    "universal",
    "motown",
    "republic",
    "emi",
    "capitol",
)

MIN_COUNTRY_TRACK_COUNT = 2


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

    df = df.rename(
        columns={
            "artistCountry": "artistCountry",
            "regionGroup": "regionGroup",
            "diaspora": "diaspora",
            "artist": "artist",
        }
    )
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


@st.cache_data(show_spinner=False)
def load_dataset(path: Path = DATA_PATH) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
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
            # Features removed from dataset; retain legacy columns with None
            features = track.get("features") or {}
            track_rows.append(
                {
                    "playlist_id": playlist.get("id"),
                    "playlist_name": playlist.get("name"),
                    "curator_type": playlist.get("curatorType"),
                    "curator": playlist.get("curator"),
                    "follower_count": playlist.get("followerCount"),
                    "launch_year": playlist.get("launchYear"),
                    "track_id": track.get("id"),
                    "track_title": track.get("title"),
                    "artist": track.get("artist"),
                    "artist_id": track.get("artistId"),
                    "artist_country": track.get("artistCountry", "Unknown") or "Unknown",
                    "region_group": track.get("regionGroup", "Unknown") or "Unknown",
                    "diaspora": bool(track.get("diaspora")),
                    "release_year": track.get("releaseYear"),
                    "track_popularity": track.get("trackPopularity"),
                    "artist_popularity": track.get("artistPopularity"),
                    "playlist_position": track.get("playlistPosition"),
                    "album_label": track.get("albumLabel") or "Unknown",
                    "label_type": classify_label(track.get("albumLabel")),
                    "album_release_date": track.get("albumReleaseDate"),
                    "added_at": track.get("addedAt"),
                    "artist_genres": ", ".join(track.get("artistGenres") or []),
                    # Audio feature columns preserved (now None since simulation removed)
                    "danceability": None,
                    "energy": None,
                    "valence": None,
                    "tempo": None,
                    "acousticness": None,
                    "instrumentalness": None,
                    "liveness": None,
                    "speechiness": None,
                    "loudness": None,
                }
            )

    playlists_df = pd.DataFrame(playlist_rows).drop_duplicates("playlist_id")
    tracks_df = pd.DataFrame(track_rows)

    if not tracks_df.empty:
        tracks_df["release_year"] = pd.to_numeric(tracks_df["release_year"], errors="coerce")
        tracks_df["follower_count"] = pd.to_numeric(tracks_df["follower_count"], errors="coerce")
        tracks_df["track_popularity"] = pd.to_numeric(tracks_df["track_popularity"], errors="coerce")
        tracks_df["artist_popularity"] = pd.to_numeric(tracks_df["artist_popularity"], errors="coerce")
        tracks_df["playlist_position"] = pd.to_numeric(tracks_df["playlist_position"], errors="coerce")
        tracks_df["album_release_date"] = pd.to_datetime(tracks_df["album_release_date"], errors="coerce")
        tracks_df["added_at"] = pd.to_datetime(tracks_df["added_at"], errors="coerce")
        tracks_df["label_type"] = tracks_df["label_type"].fillna("Unknown")

        artist_metadata = load_artist_metadata(ARTIST_METADATA_PATH)
        if not artist_metadata.empty:
            tracks_df = apply_artist_metadata(tracks_df, artist_metadata)

    return playlists_df, tracks_df, metadata


def format_share(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "0%"
    return f"{value:.0f}%"


def build_region_chart(df: pd.DataFrame) -> px.bar:
    region_counts = (
        df.assign(region_group=df["region_group"].fillna("Unknown"))
        .groupby("region_group")["track_id"]
        .count()
        .sort_values(ascending=False)
    )
    fig = px.bar(
        region_counts,
        x=region_counts.index,
        y=region_counts.values,
        labels={"x": "Region", "y": "Tracks"},
        title="Regional representation",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def build_region_map(df: pd.DataFrame, *, background_color: str | None = None) -> px.choropleth | None:
    clean = (
        df.assign(artist_country=df["artist_country"].fillna("Unknown").astype(str).str.strip())
        .loc[lambda frame: frame["artist_country"].ne("Unknown") & frame["artist_country"].ne("")]
    )
    if clean.empty:
        return None

    aggregates = (
        clean.groupby(["artist_country", "region_group"])
        .agg(
            tracks=("track_id", "count"),
            playlists=("playlist_id", "nunique"),
            avg_popularity=("track_popularity", "mean"),
            diaspora_share=("diaspora", "mean"),
        )
        .reset_index()
    )

    aggregates["avg_popularity"] = aggregates["avg_popularity"].round(1)
    aggregates["Diaspora share (%)"] = (aggregates["diaspora_share"] * 100).round(0)

    # Colorful vibrant scale for better visibility
    colorful_scale = [
        (0.0, "#4A148C"),   # Deep purple
        (0.15, "#6A1B9A"),  # Purple
        (0.3, "#1E88E5"),   # Blue
        (0.45, "#00ACC1"),  # Cyan
        (0.6, "#00E676"),   # Green
        (0.75, "#FFD600"),  # Yellow
        (0.9, "#FF6F00"),   # Orange
        (1.0, "#D50000"),   # Red
    ]

    fig = px.choropleth(
        aggregates,
        locations="artist_country",
        locationmode="country names",
        color="tracks",
        hover_name="artist_country",
        hover_data={
            "region_group": True,
            "tracks": True,
            "playlists": True,
            "avg_popularity": True,
            "Diaspora share (%)": True,
        },
        color_continuous_scale=colorful_scale,
        labels={
            "tracks": "Tracks",
            "playlists": "Playlists",
            "avg_popularity": "Avg popularity",
            "Diaspora share (%)": "Diaspora share (%)",
            "region_group": "Region group",
        },
        title="Global footprint by artist country (Interactive - Drag to rotate)",
        template="plotly_dark",
    )

    # Make it an orthographic projection (3D globe) that can be rotated
    fig.update_layout(
        margin=dict(l=10, r=10, t=60, b=10),
        coloraxis_colorbar=dict(title="Tracks"),
        height=600,
        geo=dict(
            projection_type="orthographic",  # 3D globe projection
            showocean=True,
            oceancolor="#1A1F2E",  # Dark ocean matching background
            showlakes=True,
            lakecolor="#1A1F2E",
            showland=True,
            landcolor="#2A2F3E",  # Subtle dark land
            coastlinecolor="rgba(255, 255, 255, 0.2)",
            coastlinewidth=0.5,
            showframe=False,
            showcountries=True,
            countrycolor="rgba(255, 255, 255, 0.15)",
            bgcolor="rgba(0, 0, 0, 0)",
        )
    )

    fig.update_traces(
        marker_line_color="rgba(255, 255, 255, 0.4)", 
        marker_line_width=0.5
    )

    return fig


def build_release_year_chart(df: pd.DataFrame) -> px.histogram | None:
    clean = df.dropna(subset=["release_year"])
    if clean.empty:
        return None
    fig = px.histogram(
        clean,
        x="release_year",
        color="curator_type",
        nbins=20,
        barmode="overlay",
        opacity=0.7,
        labels={"release_year": "Release year", "count": "Tracks", "curator_type": "Curator type"},
        title="Release year distribution",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def build_popularity_chart(df: pd.DataFrame) -> px.box | None:
    clean = df.dropna(subset=["track_popularity"])
    if clean.empty:
        return None
    fig = px.box(
        clean,
        x="curator_type",
        y="track_popularity",
        labels={"curator_type": "Curator type", "track_popularity": "Track popularity"},
        title="Track popularity by curator type",
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=60, b=10))
    return fig


def build_exposure_chart(df: pd.DataFrame) -> px.bar | None:
    exposure = (
        df.groupby("artist")["playlist_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
    )
    if exposure.empty:
        return None
    exposure_df = exposure.reset_index().sort_values("playlist_id", ascending=True)
    exposure_df.columns = ["artist", "playlist_count"]
    fig = px.bar(
        exposure_df,
        x="playlist_count",
        y="artist",
        orientation="h",
        labels={"playlist_count": "Playlists", "artist": "Artist"},
        title="Top recurring artists across playlists",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


def build_curator_chart(df: pd.DataFrame) -> px.bar:
    pivot = (
        df.assign(is_nigeria=df["artist_country"].str.lower().eq("nigeria"))
        .groupby("curator_type")["is_nigeria"]
        .mean()
        .sort_values(ascending=False)
        * 100
    )
    fig = px.bar(
        pivot,
        x=pivot.index,
        y=pivot.values,
        labels={"x": "Curator type", "y": "Nigeria share (%)"},
        title="Nigeria share by curator type",
        range_y=[0, 100],
    )
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=10))
    return fig


## Audio feature analysis removed (simulated data eliminated for integrity). Functions previously
## providing ANOVA & violin plots have been dropped along with SciPy dependency.


def build_country_summary(df: pd.DataFrame, *, min_tracks: int = MIN_COUNTRY_TRACK_COUNT) -> pd.DataFrame:
    columns = [
        "Country",
        "Tracks",
        "Unique artists",
        "Playlists",
        "Avg popularity",
        "Diaspora share",
        "Follower reach",
    ]
    if df.empty:
        return pd.DataFrame(columns=columns)

    clean = df.copy()
    clean["artist_country"] = clean["artist_country"].fillna("Unknown").astype(str).str.strip()
    clean = clean.loc[clean["artist_country"].ne("")]
    if clean.empty:
        return pd.DataFrame(columns=columns)
    clean["artist_key"] = clean["artist_id"].fillna(clean["artist"])

    grouped = (
        clean.groupby("artist_country")
        .agg(
            tracks=("track_id", "count"),
            unique_artists=("artist_key", "nunique"),
            unique_playlists=("playlist_id", "nunique"),
            avg_popularity=("track_popularity", "mean"),
            diaspora_share=("diaspora", "mean"),
        )
        .reset_index()
    )

    playlist_followers = (
        clean.groupby(["artist_country", "playlist_id"])["follower_count"]
        .max()
        .reset_index()
        .groupby("artist_country")["follower_count"]
        .sum()
        .rename("follower_reach")
        .reset_index()
    )

    summary = grouped.merge(playlist_followers, on="artist_country", how="left")
    summary["follower_reach"] = summary["follower_reach"].fillna(0)
    summary["avg_popularity"] = summary["avg_popularity"].round(1)
    summary["diaspora_pct"] = summary["diaspora_share"] * 100
    summary = summary.loc[summary["tracks"] >= min_tracks]
    summary.sort_values(["tracks", "artist_country"], ascending=[False, True], inplace=True)

    summary = summary.rename(
        columns={
            "artist_country": "Country",
            "tracks": "Tracks",
            "unique_artists": "Unique artists",
            "unique_playlists": "Playlists",
            "avg_popularity": "Avg popularity",
            "follower_reach": "Follower reach",
        }
    )

    summary["Tracks"] = summary["Tracks"].astype(int)
    summary["Unique artists"] = summary["Unique artists"].astype(int)
    summary["Playlists"] = summary["Playlists"].astype(int)
    summary["Avg popularity"] = summary["Avg popularity"].round(1)
    summary["Follower reach"] = summary["Follower reach"].round(0).astype("Int64")
    summary["Diaspora share"] = summary["diaspora_pct"].apply(format_share)
    summary.drop(columns=["diaspora_share", "diaspora_pct"], inplace=True)

    return summary[columns]


def build_country_detail(df: pd.DataFrame, country: str) -> Dict[str, object]:
    empty_response = {
        "metrics": {
            "tracks": 0,
            "artists": 0,
            "playlists": 0,
            "avg_popularity": None,
            "diaspora_pct": 0.0,
            "follower_reach": 0.0,
        },
        "top_region": "Unknown",
        "region_summary": [],
        "artists": pd.DataFrame(
            columns=["Artist", "Placements", "Playlists", "Avg popularity", "Median position", "Diaspora share"]
        ),
        "playlists": pd.DataFrame(
            columns=[
                "Playlist",
                "Curator",
                "Curator type",
                "Track placements",
                "Unique artists",
                "Median position",
                "Followers",
                "Launch year",
            ]
        ),
    }

    if df.empty:
        return empty_response

    clean = df.assign(artist_country=df["artist_country"].fillna("Unknown").astype(str).str.strip())
    subset = clean.loc[clean["artist_country"].eq(country)]
    if subset.empty:
        return empty_response

    artist_keys = subset["artist_id"].fillna(subset["artist"])
    track_count = int(subset.shape[0])
    unique_artists = artist_keys.nunique()
    unique_playlists = subset["playlist_id"].nunique()
    avg_popularity = subset["track_popularity"].mean()
    diaspora_pct = subset["diaspora"].mean() * 100 if track_count else 0
    follower_reach = (
        subset.groupby("playlist_id")["follower_count"].max().sum() if unique_playlists else 0
    )

    region_counts = subset["region_group"].fillna("Unknown").value_counts()
    top_region = region_counts.index[0] if not region_counts.empty else "Unknown"
    region_summary = list(zip(region_counts.index.tolist()[:3], region_counts.values.tolist()[:3]))

    artist_table = (
        subset.assign(artist_key=artist_keys)
        .groupby(["artist_key", "artist"], dropna=False)
        .agg(
            placements=("track_id", "count"),
            playlists=("playlist_id", "nunique"),
            avg_popularity=("track_popularity", "mean"),
            median_position=("playlist_position", "median"),
            diaspora_share=("diaspora", "mean"),
        )
        .reset_index(drop=False)
    )

    artist_table = artist_table.sort_values(["placements", "artist"], ascending=[False, True]).head(20)
    artist_table["avg_popularity"] = artist_table["avg_popularity"].round(1)
    artist_table["median_position"] = artist_table["median_position"].round().astype("Int64")
    artist_table["diaspora_share"] = artist_table["diaspora_share"] * 100
    artist_table = artist_table.rename(
        columns={
            "artist": "Artist",
            "placements": "Placements",
            "playlists": "Playlists",
            "avg_popularity": "Avg popularity",
            "median_position": "Median position",
            "diaspora_share": "Diaspora share",
        }
    )
    artist_table["Diaspora share"] = artist_table["Diaspora share"].apply(format_share)
    artist_table["Avg popularity"] = artist_table["Avg popularity"].round(1)
    artist_table = artist_table[
        ["Artist", "Placements", "Playlists", "Avg popularity", "Median position", "Diaspora share"]
    ]

    playlist_table = (
        subset.assign(artist_key=artist_keys)
        .groupby(["playlist_id", "playlist_name", "curator", "curator_type"], dropna=False)
        .agg(
            track_count=("track_id", "count"),
            unique_artists=("artist_key", "nunique"),
            median_position=("playlist_position", "median"),
            followers=("follower_count", "max"),
            launch_year=("launch_year", "max"),
        )
        .reset_index(drop=False)
    )

    playlist_table = playlist_table.sort_values(["track_count", "playlist_name"], ascending=[False, True]).head(20)
    playlist_table["median_position"] = playlist_table["median_position"].round().astype("Int64")
    playlist_table["followers"] = playlist_table["followers"].round().astype("Int64")
    playlist_table["launch_year"] = playlist_table["launch_year"].round().astype("Int64")
    playlist_table = playlist_table.rename(
        columns={
            "playlist_name": "Playlist",
            "curator": "Curator",
            "curator_type": "Curator type",
            "track_count": "Track placements",
            "unique_artists": "Unique artists",
            "median_position": "Median position",
            "followers": "Followers",
            "launch_year": "Launch year",
        }
    )
    playlist_table = playlist_table[
        [
            "Playlist",
            "Curator",
            "Curator type",
            "Track placements",
            "Unique artists",
            "Median position",
            "Followers",
            "Launch year",
        ]
    ]

    return {
        "metrics": {
            "tracks": track_count,
            "artists": int(unique_artists),
            "playlists": int(unique_playlists),
            "avg_popularity": avg_popularity,
            "diaspora_pct": float(diaspora_pct) if pd.notna(diaspora_pct) else 0.0,
            "follower_reach": float(follower_reach) if pd.notna(follower_reach) else 0.0,
        },
        "top_region": top_region,
        "region_summary": region_summary,
        "artists": artist_table,
        "playlists": playlist_table,
    }


def playlist_summary(filtered_tracks: pd.DataFrame, playlists_df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "Playlist",
        "Curator",
        "Curator type",
        "Followers",
        "Tracks",
        "Unique regions",
        "Diaspora share",
        "Nigeria share",
        "Major label share",
        "Mean track popularity",
        "Mean artist popularity",
        "Avg release year",
    ]
    if filtered_tracks.empty:
        return pd.DataFrame(columns=columns)

    def summarise(group: pd.DataFrame) -> pd.Series:
        known_regions = group.loc[group["region_group"] != "Unknown", "region_group"].nunique()
        diaspora_share = group["diaspora"].mean() * 100 if len(group) else None
        nigeria_share = group["artist_country"].astype(str).str.lower().eq("nigeria").mean() * 100 if len(group) else None
        major_share = (group["label_type"].eq("Major").mean() * 100) if len(group) else None
        return pd.Series(
            {
                "Tracks": len(group),
                "Unique regions": known_regions,
                "Diaspora share": diaspora_share,
                "Nigeria share": nigeria_share,
                "Major label share": major_share,
                "Mean track popularity": group["track_popularity"].mean(),
                "Mean artist popularity": group["artist_popularity"].mean(),
                "Avg release year": group["release_year"].mean(),
            }
        )

    aggregated = filtered_tracks.groupby("playlist_id").apply(summarise).reset_index()
    merged = aggregated.merge(playlists_df, on="playlist_id", how="left")
    merged = merged[
        [
            "playlist_name",
            "curator",
            "curator_type",
            "follower_count",
            "Tracks",
            "Unique regions",
            "Diaspora share",
            "Nigeria share",
            "Major label share",
            "Mean track popularity",
            "Mean artist popularity",
            "Avg release year",
        ]
    ]
    merged = merged.rename(
        columns={
            "playlist_name": "Playlist",
            "curator": "Curator",
            "curator_type": "Curator type",
            "follower_count": "Followers",
        }
    )

    merged["Followers"] = merged["Followers"].round(0)
    merged["Followers"] = merged["Followers"].apply(lambda value: pd.NA if pd.isna(value) else int(value)).astype("Int64")
    merged["Diaspora share"] = merged["Diaspora share"].apply(format_share)
    merged["Nigeria share"] = merged["Nigeria share"].apply(format_share)
    merged["Major label share"] = merged["Major label share"].apply(format_share)
    merged["Mean track popularity"] = merged["Mean track popularity"].round(1)
    merged["Mean artist popularity"] = merged["Mean artist popularity"].round(1)
    merged["Avg release year"] = merged["Avg release year"].apply(
        lambda value: pd.NA if pd.isna(value) else int(round(value))
    ).astype("Int64")
    merged.sort_values("Followers", ascending=False, inplace=True)
    return merged


def main() -> None:
    st.set_page_config(
        page_title="Afrobeats Playlist Observatory",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': "Interactive dashboard focusing on regional representation, curator concentration and temporal patterns in Spotify Afrobeats playlists."
        }
    )
    
    # Custom CSS for academic styling
    st.markdown("""
    <style>
        /* Academic theme enhancements */
        .main {
            background: linear-gradient(135deg, #0B0E11 0%, #1A1F2E 100%);
        }
        
        .stMetric {
            background: rgba(19, 24, 33, 0.92);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        }
        
        .stMetric label {
            color: #B3B8C2 !important;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            color: #FFB400;
            font-size: 2rem;
            font-weight: 700;
        }
        
        h1, h2, h3 {
            font-family: 'Georgia', serif;
            color: #FFB400 !important;
            letter-spacing: -0.5px;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: rgba(19, 24, 33, 0.5);
            padding: 0.5rem;
            border-radius: 12px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 999px;
            padding: 0.5rem 1.5rem;
            color: #B3B8C2;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #FFB400 0%, #FF8C00 100%);
            color: #111;
            border-color: #FFB400;
        }
        
        .stDownloadButton button {
            background: linear-gradient(135deg, #FFB400 0%, #FF8C00 100%);
            color: #111;
            font-weight: 700;
            border: none;
            border-radius: 999px;
            padding: 0.75rem 1.5rem;
        }
        
        .citation-box {
            background: rgba(255, 180, 0, 0.1);
            border-left: 4px solid #FFB400;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .methodology-section {
            background: rgba(19, 24, 33, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with academic branding
    st.title("🎵 Afrobeats Playlist Observatory")
    st.caption("Explore regional representation, curator concentration, temporal patterns and label dynamics.")

    playlists_df, tracks_df, run_metadata = load_dataset()
    if tracks_df.empty:
        st.warning("The dataset does not contain any tracks. Double-check the data export step.")
        return

    # Sidebar filters
    with st.sidebar:
        st.markdown("### 🎛️ Dashboard Filters")
        st.markdown("---")
        
        search_text = st.text_input("🔍 Search playlist", "", placeholder="Type playlist name...")

        curator_options = sorted(tracks_df["curator_type"].dropna().unique())
        selected_curators = st.multiselect("🎭 Curator type", curator_options, default=curator_options)

        region_options = sorted(tracks_df["region_group"].fillna("Unknown").unique())
        selected_regions = st.multiselect("🌍 Region", region_options, default=region_options)

        label_options = sorted(tracks_df["label_type"].fillna("Unknown").unique())
        selected_labels = st.multiselect("🏢 Label type", label_options, default=label_options)

        valid_years = tracks_df["release_year"].dropna().astype(int)
        if not valid_years.empty:
            year_min, year_max = int(valid_years.min()), int(valid_years.max())
            selected_years = st.slider("📅 Release year range", min_value=year_min, max_value=year_max, value=(year_min, year_max))
        else:
            selected_years = (None, None)
            st.info("Release year metadata missing; timeline filter disabled.")

        diaspora_only = st.checkbox("✨ Diaspora artists only", value=False)

        st.markdown("---")
        
        if run_metadata:
            with st.expander("📊 Dataset Metadata", expanded=False):
                started = run_metadata.get("startedAt", "Unknown")
                generated = run_metadata.get("generatedAt", "Unknown")
                playlist_total = run_metadata.get("playlistCount") or playlists_df.shape[0]
                artist_detail_count = run_metadata.get("artistDetailsFetched")
                st.markdown(f"**Started:** {started}")
                st.markdown(f"**Generated:** {generated}")
                st.markdown(f"**Playlists:** {playlist_total}")
                if artist_detail_count is not None:
                    st.markdown(f"**Artist records:** {artist_detail_count}")
                missing = run_metadata.get("missingArtists") or []
                if missing:
                    st.warning(f"{len(missing)} artists missing metadata")
    
    # Apply filters
    filtered = tracks_df.copy()

    if selected_curators:
        filtered = filtered[filtered["curator_type"].isin(selected_curators)]
    if selected_regions:
        filtered = filtered[filtered["region_group"].isin(selected_regions)]
    if selected_labels:
        filtered = filtered[filtered["label_type"].isin(selected_labels)]
    if diaspora_only:
        filtered = filtered[filtered["diaspora"]]
    if search_text:
        filtered = filtered[filtered["playlist_name"].str.contains(search_text, case=False, na=False)]
    if selected_years != (None, None):
        start_year, end_year = selected_years
        filtered = filtered[filtered["release_year"].between(start_year, end_year, inclusive="both")]

    if filtered.empty:
        st.error("❌ No tracks match the current filters. Please adjust your selection.")
        return
    
    # Tabbed interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "🌍 Regional Analysis", 
        "📅 Temporal Trends",
        "🏢 Label Distribution"
    ])
    
    # TAB 1: OVERVIEW
    with tab1:
        st.markdown("### Key Performance Indicators")
        
        # Calculate metrics
        st.markdown("### Key Performance Indicators")
        
        # Calculate metrics
        playlist_count = filtered["playlist_id"].nunique()
        track_count = int(filtered.shape[0])
        nigeria_share = filtered["artist_country"].str.lower().eq("nigeria").mean() * 100
        diaspora_share = filtered["diaspora"].mean() * 100
        diversity = (
            filtered.loc[filtered["region_group"] != "Unknown"]
            .groupby("playlist_id")["region_group"]
            .nunique()
        )
        diversity_score = diversity.mean() if not diversity.empty else 0
        avg_release_year = filtered["release_year"].mean()
        avg_track_popularity = filtered["track_popularity"].mean()
        avg_artist_popularity = filtered["artist_popularity"].mean()
        major_label_share = filtered["label_type"].eq("Major").mean() * 100

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📋 Playlists", f"{playlist_count:,}")
        col2.metric("🎵 Tracks", f"{track_count:,}")
        col3.metric("🇳🇬 Nigeria Share", format_share(nigeria_share))
        col4.metric("✨ Diaspora Share", format_share(diaspora_share))
        col5.metric("🌍 Avg Regions/Playlist", f"{diversity_score:.1f}")

        st.markdown("---")
        
        sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)
        release_year_metric = "N/A" if pd.isna(avg_release_year) else f"{avg_release_year:.0f}"
        sub_col1.metric("📅 Avg Release Year", release_year_metric)
        sub_col2.metric("⭐ Avg Track Popularity", "N/A" if pd.isna(avg_track_popularity) else f"{avg_track_popularity:.1f}")
        sub_col3.metric("👤 Avg Artist Popularity", "N/A" if pd.isna(avg_artist_popularity) else f"{avg_artist_popularity:.1f}")
        sub_col4.metric("🏢 Major Label Share", format_share(major_label_share))
        
        st.markdown("---")
        st.markdown("### Regional Representation")
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.plotly_chart(build_region_chart(filtered), use_container_width=True)
        with col_chart2:
            release_fig = build_release_year_chart(filtered)
            if release_fig:
                st.plotly_chart(release_fig, use_container_width=True)
            else:
                st.info("📊 Release year metadata unavailable for this selection.")
        
        st.markdown("### Playlist Breakdown")
        summary = playlist_summary(filtered, playlists_df)
        st.dataframe(summary, use_container_width=True, height=400)
        
        csv_export = filtered.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Filtered Data (CSV)",
            data=csv_export,
            file_name="afrobeats_filtered_tracks.csv",
            mime="text/csv",
        )
    
    # TAB 2: REGIONAL ANALYSIS
    with tab2:
        st.markdown("### Geographic Distribution Analysis")
        
        theme_background = st.get_option("theme.backgroundColor")
        region_map_fig = build_region_map(filtered, background_color=theme_background)
        if region_map_fig:
            st.plotly_chart(region_map_fig, use_container_width=True)
        else:
            st.info("🗺️ Artist country metadata unavailable for the map visualization.")
        
        st.markdown("---")
        st.markdown("### Country Spotlight")
        
        country_summary = build_country_summary(filtered)
        if country_summary.empty:
            st.info("Country-level view unavailable for this selection.")
        else:
            country_options = country_summary["Country"].tolist()
            selected_country = st.selectbox(
                "🔍 Focus Country",
                country_options,
                index=0,
                key="country_spotlight_select",
            )
            
            col_summary, col_detail = st.columns([1, 2])
            
            with col_summary:
                st.dataframe(country_summary.head(10), use_container_width=True)
            
            with col_detail:
                detail = build_country_detail(filtered, selected_country)
                metrics = detail["metrics"]
                
                metric_row1 = st.columns(3)
                metric_row1[0].metric("🎵 Tracks", f"{metrics['tracks']:,}")
                metric_row1[1].metric("👥 Unique Artists", f"{metrics['artists']:,}")
                metric_row1[2].metric("📋 Playlists", f"{metrics['playlists']:,}")
                
                metric_row2 = st.columns(3)
                avg_pop_display = "N/A" if pd.isna(metrics["avg_popularity"]) else f"{metrics['avg_popularity']:.1f}"
                metric_row2[0].metric("⭐ Avg Popularity", avg_pop_display)
                metric_row2[1].metric("✨ Diaspora Share", format_share(metrics["diaspora_pct"]))
                follower_metric = metrics["follower_reach"]
                follower_display = "0" if pd.isna(follower_metric) else f"{int(round(follower_metric)):,}"
                metric_row2[2].metric("📊 Follower Reach", follower_display)
                
                if detail["region_summary"]:
                    region_blurb = ", ".join(f"{region} ({count})" for region, count in detail["region_summary"])
                    st.caption(f"**Primary Region:** {detail['top_region']} • **Mixes:** {region_blurb}")
        
        st.markdown("---")
        
        if not country_summary.empty and detail:
            col_artists, col_playlists = st.columns(2)
            
            with col_artists:
                st.markdown(f"**Top Artists from {selected_country}**")
                if detail["artists"].empty:
                    st.info("No artist placements for this country.")
                else:
                    st.dataframe(detail["artists"].head(15), use_container_width=True)
            
            with col_playlists:
                st.markdown(f"**Playlists Featuring {selected_country}**")
                if detail["playlists"].empty:
                    st.info("No playlists feature this country.")
                else:
                    st.dataframe(detail["playlists"].head(15), use_container_width=True)
    
    # TAB 3: TEMPORAL TRENDS
    with tab3:
        st.markdown("### Release Momentum & Popularity Analysis")
        
        popularity_fig = build_popularity_chart(filtered)
        if popularity_fig:
            st.plotly_chart(popularity_fig, use_container_width=True)
        else:
            st.info("📊 Popularity data unavailable for this selection.")
        
        st.markdown("---")
        
        exposure_fig = build_exposure_chart(filtered)
        if exposure_fig:
            st.plotly_chart(exposure_fig, use_container_width=True)
        else:
            st.info("📊 Exposure concentration data unavailable.")
        
        st.markdown("---")
        st.markdown("### Track Preview (First 100 Tracks)")
        
        preview_cols = [
            "playlist_name",
            "playlist_position",
            "track_title",
            "artist",
            "track_popularity",
            "artist_popularity",
            "artist_country",
            "region_group",
            "label_type",
            "release_year",
        ]
        preview_df = filtered[preview_cols].rename(
            columns={
                "playlist_name": "Playlist",
                "playlist_position": "Position",
                "track_title": "Track",
                "artist": "Artist",
                "track_popularity": "Track Pop.",
                "artist_popularity": "Artist Pop.",
                "artist_country": "Country",
                "region_group": "Region",
                "label_type": "Label",
                "release_year": "Year",
            }
        )
        st.dataframe(preview_df.head(100), use_container_width=True, height=400)
    
    # TAB 4: LABEL DISTRIBUTION
    with tab4:
        st.markdown("### Curator & Label Concentration Patterns")
        
        st.plotly_chart(build_curator_chart(filtered), use_container_width=True)
        
        st.markdown("---")
        st.markdown("### Label Type Distribution")
        
        label_stats = filtered.groupby("label_type").agg(
            Tracks=("track_id", "count"),
            Playlists=("playlist_id", "nunique"),
            Avg_Popularity=("track_popularity", "mean"),
            Nigeria_Share=("artist_country", lambda x: (x.str.lower() == "nigeria").mean() * 100),
            Diaspora_Share=("diaspora", lambda x: x.mean() * 100)
        ).reset_index()
        
        label_stats = label_stats.rename(columns={
            "label_type": "Label Type",
            "Avg_Popularity": "Avg Popularity",
            "Nigeria_Share": "Nigeria Share (%)",
            "Diaspora_Share": "Diaspora Share (%)"
        })
        
        label_stats["Avg Popularity"] = label_stats["Avg Popularity"].round(1)
        label_stats["Nigeria Share (%)"] = label_stats["Nigeria Share (%)"].round(1)
        label_stats["Diaspora Share (%)"] = label_stats["Diaspora Share (%)"].round(1)
        
        st.dataframe(label_stats, use_container_width=True)
    


if __name__ == "__main__":
    main()
