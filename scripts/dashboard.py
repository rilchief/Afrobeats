"""Streamlit dashboard for analysing gatekeeping dynamics in Afrobeats playlists."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    import pycountry  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    pycountry = None

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "processed" / "afrobeats_playlists.json"
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

COUNTRY_COLOR_SEQUENCE = (
    px.colors.qualitative.Alphabet
    + px.colors.qualitative.Dark24
    + px.colors.qualitative.Set3
    + px.colors.qualitative.Bold
)

COUNTRY_CODE_OVERRIDES = {
    "Congo": "CG",
    "Congo - Brazzaville": "CG",
    "Congo - Kinshasa": "CD",
    "Côte d'Ivoire": "CI",
    "Ivory Coast": "CI",
    "South Korea": "KR",
    "North Korea": "KP",
    "United States": "US",
    "United Kingdom": "GB",
    "UK": "GB",
    "Russia": "RU",
    "Vietnam": "VN",
    "Taiwan": "TW",
    "Hong Kong": "HK",
    "UAE": "AE",
    "United Arab Emirates": "AE",
    "Trinidad & Tobago": "TT",
    "Trinidad and Tobago": "TT",
    "Martinique": "MQ",
    "Réunion": "RE",
    "Guadeloupe": "GP",
}


def country_code_from_name(name: str | None) -> str | None:
    if not name:
        return None
    normalized = name.strip()
    if not normalized or normalized.lower() == "unknown":
        return None
    override = COUNTRY_CODE_OVERRIDES.get(normalized)
    if override:
        return override
    if pycountry is None:
        return None
    try:
        match = pycountry.countries.search_fuzzy(normalized)[0]
        return match.alpha_2
    except (LookupError, AttributeError):
        return None


def country_to_flag(name: str | None) -> str:
    code = country_code_from_name(name)
    if not code:
        return ""
    try:
        return "".join(chr(ord("🇦") + ord(letter) - ord("A")) for letter in code.upper())
    except ValueError:
        return ""


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

    return playlists_df, tracks_df, metadata


def format_share(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "0%"
    return f"{value:.0f}%"


def build_region_chart(df: pd.DataFrame) -> px.bar:
    region_counts = (
        df.assign(region_group=df["region_group"].fillna("Unknown"))
        .loc[lambda frame: frame["region_group"].ne("Unknown")]
        .groupby("region_group")["track_id"]
        .count()
        .sort_values(ascending=False)
    )
    region_df = region_counts.reset_index()
    region_df.columns = ["region", "tracks"]
    fig = px.bar(
        region_df,
        x="region",
        y="tracks",
        color="tracks",
        color_continuous_scale="Viridis",
        labels={"region": "Region", "tracks": "Tracks"},
        title="Regional representation",
        template="plotly_dark",
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Tracks: %{y:,}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=60, b=10),
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
    )
    return fig


def aggregate_country_footprint(df: pd.DataFrame) -> pd.DataFrame:
    clean = (
        df.assign(artist_country=df["artist_country"].fillna("Unknown").astype(str).str.strip())
        .loc[lambda frame: frame["artist_country"].ne("Unknown") & frame["artist_country"].ne("")]
    )
    if clean.empty:
        return pd.DataFrame()

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
    return aggregates


def build_region_map(
    df: pd.DataFrame,
    *,
    background_color: str | None = None,
    aggregates: pd.DataFrame | None = None,
    color_map: Dict[str, str] | None = None,
) -> px.choropleth | None:
    aggregates = aggregates if aggregates is not None else aggregate_country_footprint(df)
    if aggregates is None or aggregates.empty:
        return None

    if color_map is None:
        countries = sorted(aggregates["artist_country"].astype(str).unique())
        color_map = {
            country: COUNTRY_COLOR_SEQUENCE[idx % len(COUNTRY_COLOR_SEQUENCE)]
            for idx, country in enumerate(countries)
        }

    fig = px.choropleth(
        aggregates,
        locations="artist_country",
        locationmode="country names",
        color="artist_country",
        hover_name="artist_country",
        hover_data={
            "region_group": True,
            "tracks": True,
            "playlists": True,
            "avg_popularity": True,
            "Diaspora share (%)": True,
        },
        custom_data=[
            "region_group",
            "tracks",
            "playlists",
            "avg_popularity",
            "Diaspora share (%)",
        ],
        color_discrete_map=color_map,
        labels={
            "tracks": "Tracks",
            "playlists": "Playlists",
            "avg_popularity": "Avg popularity",
            "Diaspora share (%)": "Diaspora share (%)",
            "region_group": "Region group",
        },
        title="Global footprint by artist country",
        template="plotly_dark",
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=60, b=10),
        height=520,
    )

    fig.update_traces(
        marker_line_color="rgba(255, 255, 255, 0.45)",
        marker_line_width=0.7,
        hovertemplate=(
            "<b>%{location}</b><br>Region: %{customdata[0]}<br>Tracks: %{customdata[1]}<br>"
            "Playlists: %{customdata[2]}<br>Avg popularity: %{customdata[3]}<br>"
            "Diaspora share: %{customdata[4]}%<extra></extra>"
        ),
    )

    if background_color:
        fig.update_layout(paper_bgcolor=background_color, plot_bgcolor=background_color)
        fig.update_geos(
            bgcolor=background_color,
            showcoastlines=False,
            showframe=False,
            projection_type="natural earth",
            landcolor="rgba(255, 255, 255, 0.12)",
            oceancolor="rgba(0, 0, 0, 0)",
            showlakes=False,
        )
    else:
        fig.update_geos(
            showcoastlines=False,
            showframe=False,
            projection_type="natural earth",
            landcolor="rgba(38, 38, 47, 1)",
            oceancolor="rgba(18, 18, 24, 1)",
            showlakes=False,
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
        nbins=25,
        barmode="overlay",
        opacity=0.75,
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"release_year": "Release year", "count": "Tracks", "curator_type": "Curator type"},
        title="Release year distribution",
        template="plotly_dark",
    )
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="rgba(255,255,255,0.3)",
        hovertemplate="<b>Year: %{x}</b><br>Tracks: %{y}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        bargap=0.1,
    )
    return fig


def build_popularity_chart(df: pd.DataFrame) -> px.box | None:
    clean = df.dropna(subset=["track_popularity"])
    if clean.empty:
        return None
    fig = px.box(
        clean,
        x="curator_type",
        y="track_popularity",
        color="curator_type",
        color_discrete_sequence=px.colors.qualitative.Vivid,
        labels={"curator_type": "Curator type", "track_popularity": "Track popularity"},
        title="Track popularity by curator type",
        template="plotly_dark",
        points="outliers",
    )
    fig.update_traces(
        marker=dict(opacity=0.6, size=4),
        line=dict(width=1.5),
        hovertemplate="<b>%{x}</b><br>Popularity: %{y}<extra></extra>",
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
    )
    return fig


def build_exposure_chart(df: pd.DataFrame) -> px.bar | None:
    exposure = (
        df.groupby("artist")["playlist_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(15)
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
        color="playlist_count",
        color_continuous_scale="Sunset",
        labels={"playlist_count": "Playlists", "artist": "Artist"},
        title="Top recurring artists across playlists",
        template="plotly_dark",
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Appears in %{x} playlists<extra></extra>",
        texttemplate="%{x}",
        textposition="outside",
        textfont=dict(size=10, color="rgba(255,255,255,0.8)"),
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=60, b=10),
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(showgrid=False),
        height=450,
    )
    return fig


def build_curator_chart(df: pd.DataFrame) -> px.bar:
    pivot = (
        df.assign(is_nigeria=df["artist_country"].str.lower().eq("nigeria"))
        .groupby("curator_type")["is_nigeria"]
        .mean()
        .sort_values(ascending=False)
        * 100
    )
    curator_df = pivot.reset_index()
    curator_df.columns = ["curator_type", "nigeria_share"]
    fig = px.bar(
        curator_df,
        x="curator_type",
        y="nigeria_share",
        color="nigeria_share",
        color_continuous_scale="Oranges",
        labels={"curator_type": "Curator type", "nigeria_share": "Nigeria share (%)"},
        title="Nigeria share by curator type",
        range_y=[0, 100],
        template="plotly_dark",
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Nigeria share: %{y:.1f}%<extra></extra>",
        texttemplate="%{y:.0f}%",
        textposition="outside",
        textfont=dict(size=11, color="rgba(255,255,255,0.9)"),
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=60, b=10),
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
    )
    return fig


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
    st.set_page_config(page_title="Afrobeats Playlist Observatory", layout="wide")
    st.title("Afrobeats Playlist Gatekeeping Observatory")
    st.caption("Interactively explore representation, exposure, and temporal patterns across Spotify Afrobeats playlists.")

    playlists_df, tracks_df, run_metadata = load_dataset()
    if tracks_df.empty:
        st.warning("The dataset does not contain any tracks. Double-check the data export step.")
        return

    with st.sidebar:
        st.header("Filters")
        search_text = st.text_input("Search playlist", "").strip()

        curator_options = sorted(tracks_df["curator_type"].dropna().unique())
        selected_curators = st.multiselect("Curator type", curator_options, default=curator_options)

        region_options = sorted(tracks_df["region_group"].fillna("Unknown").unique())
        selected_regions = st.multiselect("Region", region_options, default=region_options)

        label_options = sorted(tracks_df["label_type"].fillna("Unknown").unique())
        selected_labels = st.multiselect("Label type", label_options, default=label_options)

        valid_years = tracks_df["release_year"].dropna().astype(int)
        if not valid_years.empty:
            year_min, year_max = int(valid_years.min()), int(valid_years.max())
            selected_years = st.slider("Release year", min_value=year_min, max_value=year_max, value=(year_min, year_max))
        else:
            selected_years = (None, None)
            st.info("Release year metadata missing; timeline filter disabled.")

        diaspora_only = st.checkbox("Diaspora artists only", value=False)

        if run_metadata:
            with st.expander("Dataset run metadata", expanded=False):
                started = run_metadata.get("startedAt", "Unknown")
                generated = run_metadata.get("generatedAt", "Unknown")
                playlist_total = run_metadata.get("playlistCount") or playlists_df.shape[0]
                artist_detail_count = run_metadata.get("artistDetailsFetched")
                st.write(f"Started: {started}")
                st.write(f"Generated: {generated}")
                st.write(f"Playlists collected: {playlist_total}")
                if artist_detail_count is not None:
                    st.write(f"Artist detail records fetched: {artist_detail_count}")
                missing = run_metadata.get("missingArtists") or []
                if missing:
                    st.write("Missing artist metadata:")
                    st.write(", ".join(missing))

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
        st.warning("No tracks match the current filters.")
        return

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
    col1.metric("Playlists", playlist_count)
    col2.metric("Tracks", track_count)
    col3.metric("Nigeria share", format_share(nigeria_share))
    col4.metric("Diaspora share", format_share(diaspora_share))
    release_year_metric = "N/A" if pd.isna(avg_release_year) else f"{avg_release_year:.0f}"
    col5.metric("Avg release year", release_year_metric)

    sub_col1, sub_col2, sub_col3 = st.columns(3)
    sub_col1.metric("Mean track popularity", "N/A" if pd.isna(avg_track_popularity) else f"{avg_track_popularity:.1f}")
    sub_col2.metric("Mean artist popularity", "N/A" if pd.isna(avg_artist_popularity) else f"{avg_artist_popularity:.1f}")
    sub_col3.metric("Major label share", format_share(major_label_share))

    tagged_regions = (
        filtered["region_group"].fillna("Unknown").astype(str).str.strip()
    )
    tagged_regions = tagged_regions[tagged_regions.str.lower().ne("unknown")]
    unique_region_count = int(tagged_regions.nunique()) if not tagged_regions.empty else 0

    release_years = filtered["release_year"].dropna().astype(int)
    if release_years.empty:
        release_window = "unknown release window"
    else:
        release_start = int(release_years.min())
        release_end = int(release_years.max())
        release_window = f"{release_start}" if release_start == release_end else f"{release_start} – {release_end}"

    focus_tokens = []
    if diaspora_only:
        focus_tokens.append("diaspora artists only")
    if search_text:
        focus_tokens.append(f"playlist keyword '{search_text}'")
    focus_copy = f" Focus: {', '.join(focus_tokens)}." if focus_tokens else ""

    st.info(
        f"{playlist_count} playlists / {track_count} tracks | "
        f"{unique_region_count} tagged region{'s' if unique_region_count != 1 else ''} | releases {release_window}."
        f"{focus_copy}"
    )

    theme_background = st.get_option("theme.backgroundColor")
    country_overview = aggregate_country_footprint(filtered)
    country_color_map: Dict[str, str] | None = None
    if not country_overview.empty:
        countries_sorted = sorted(country_overview["artist_country"].astype(str).unique())
        country_color_map = {
            country: COUNTRY_COLOR_SEQUENCE[idx % len(COUNTRY_COLOR_SEQUENCE)]
            for idx, country in enumerate(countries_sorted)
        }
    region_map_fig = build_region_map(
        filtered,
        background_color=theme_background,
        aggregates=country_overview,
        color_map=country_color_map,
    )
    if region_map_fig:
        st.plotly_chart(region_map_fig, use_container_width=True)
    else:
        st.info("Artist country metadata unavailable for the map.")

    region_chart = build_region_chart(filtered)
    release_fig = build_release_year_chart(filtered)
    popularity_fig = build_popularity_chart(filtered)
    curator_fig = build_curator_chart(filtered)
    exposure_fig = build_exposure_chart(filtered)

    mix_tab, timeline_tab, concentration_tab = st.tabs(
        ["Regional mix", "Release & popularity", "Curator & exposure"]
    )

    with mix_tab:
        st.plotly_chart(region_chart, use_container_width=True)

    with timeline_tab:
        trend_cols = st.columns(2)
        with trend_cols[0]:
            if release_fig:
                st.plotly_chart(release_fig, use_container_width=True)
            else:
                st.info("Release year metadata unavailable for this selection.")
        with trend_cols[1]:
            if popularity_fig:
                st.plotly_chart(popularity_fig, use_container_width=True)
            else:
                st.info("Popularity data unavailable for this selection.")

    with concentration_tab:
        st.plotly_chart(curator_fig, use_container_width=True)
        if exposure_fig:
            st.plotly_chart(exposure_fig, use_container_width=True)
        else:
            st.info("No recurring artist data for this slice.")

    summary = playlist_summary(filtered, playlists_df)
    st.subheader("Playlist breakdown")
    if not summary.empty:
        sort_columns = summary.columns.tolist()
        default_sort_index = sort_columns.index("Followers") if "Followers" in sort_columns else 0
        sort_field = st.selectbox(
            "Sort playlists by",
            sort_columns,
            index=default_sort_index,
            key="playlist_sort_by",
            help="Reorder the summary table without exporting to Excel first."
        )
        sort_direction = st.radio(
            "Order",
            ("Descending", "Ascending"),
            horizontal=True,
            key="playlist_sort_order"
        )
        summary = summary.sort_values(sort_field, ascending=(sort_direction == "Ascending"))
    else:
        st.caption("No playlists to summarise with the current filters.")
    st.dataframe(summary, use_container_width=True)

    with st.expander("Preview filtered tracks"):
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
                "track_popularity": "Track popularity",
                "artist_popularity": "Artist popularity",
                "artist_country": "Artist country",
                "region_group": "Region",
                "label_type": "Label type",
                "release_year": "Release year",
            }
        )
        st.dataframe(preview_df.head(100), use_container_width=True)

    csv_export = filtered.to_csv(index=False)
    st.download_button(
        label="Download filtered tracks (CSV)",
        data=csv_export,
        file_name="afrobeats_filtered_tracks.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
