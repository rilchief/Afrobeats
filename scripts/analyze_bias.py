"""Bias analysis utilities for Afrobeats playlist dataset."""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, f_oneway, kruskal, ttest_ind

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "processed" / "afrobeats_playlists.json"
OUTPUT_PATH = REPO_ROOT / "outputs" / "analysis_summary.md"


def load_dataset(path: Path = DATA_PATH) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    track_rows: List[Dict] = []
    for playlist in payload.get("playlists", []):
        for track in playlist.get("tracks") or []:
            track_rows.append(
                {
                    "playlist_id": playlist.get("id"),
                    "playlist_name": playlist.get("name"),
                    "curator_type": playlist.get("curatorType"),
                    "track_id": track.get("id"),
                    "artist": track.get("artist"),
                    "artist_country": track.get("artistCountry", "Unknown") or "Unknown",
                    "region_group": track.get("regionGroup", "Unknown") or "Unknown",
                    "diaspora": bool(track.get("diaspora")),
                    "release_year": track.get("releaseYear"),
                    "track_popularity": track.get("trackPopularity"),
                    "artist_popularity": track.get("artistPopularity"),
                    "artist_followers": track.get("artistFollowers"),
                    "playlist_position": track.get("playlistPosition"),
                    "label_type": track.get("labelType") or track.get("label_type"),
                    "album_label": track.get("albumLabel"),
                }
            )
    df = pd.DataFrame(track_rows)
    if df.empty:
        raise SystemExit("Dataset contains no tracks. Run fetch_spotify_data.py first.")
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
    df["track_popularity"] = pd.to_numeric(df["track_popularity"], errors="coerce")
    df["artist_popularity"] = pd.to_numeric(df["artist_popularity"], errors="coerce")
    df["artist_followers"] = pd.to_numeric(df["artist_followers"], errors="coerce")
    df["playlist_position"] = pd.to_numeric(df["playlist_position"], errors="coerce")
    df["label_type"] = df["label_type"].fillna("Unknown")
    return df


def chi_square_region(df: pd.DataFrame) -> Tuple[float, float, int]:
    contingency = pd.crosstab(df["curator_type"], df["region_group"])
    chi2, p_value, dof, _ = chi2_contingency(contingency)
    return chi2, p_value, dof


def chi_square_label(df: pd.DataFrame) -> Tuple[float, float, int]:
    contingency = pd.crosstab(df["curator_type"], df["label_type"])
    chi2, p_value, dof, _ = chi2_contingency(contingency)
    return chi2, p_value, dof


def one_way_anova(series: pd.Series, groups: pd.Series) -> Tuple[float, float]:
    grouped_values = [series[groups == group].dropna() for group in groups.unique()]
    grouped_values = [values for values in grouped_values if len(values) >= 3]
    if len(grouped_values) < 2:
        return float("nan"), float("nan")
    stat, p_value = f_oneway(*grouped_values)
    return stat, p_value


def kruskal_wallis(series: pd.Series, groups: pd.Series) -> Tuple[float, float]:
    grouped_values = [series[groups == group].dropna() for group in groups.unique()]
    grouped_values = [values for values in grouped_values if len(values) >= 3]
    if len(grouped_values) < 2:
        return float("nan"), float("nan")
    stat, p_value = kruskal(*grouped_values)
    return stat, p_value


def compute_eta_squared(series: pd.Series, groups: pd.Series) -> float:
    data = pd.DataFrame({"value": series, "group": groups}).dropna()
    if data.empty:
        return float("nan")
    overall_mean = data["value"].mean()
    ss_between = 0.0
    for _, group_df in data.groupby("group"):
        n = len(group_df)
        if n == 0:
            continue
        group_mean = group_df["value"].mean()
        ss_between += n * (group_mean - overall_mean) ** 2
    ss_total = ((data["value"] - overall_mean) ** 2).sum()
    if ss_total == 0:
        return float("nan")
    return float(ss_between / ss_total)


def pairwise_t_tests(series: pd.Series, groups: pd.Series) -> List[Dict[str, float]]:
    data = pd.DataFrame({"value": series, "group": groups}).dropna()
    unique_groups = data["group"].unique()
    results: List[Dict[str, float]] = []
    for group_a, group_b in combinations(unique_groups, 2):
        values_a = data.loc[data["group"] == group_a, "value"]
        values_b = data.loc[data["group"] == group_b, "value"]
        if len(values_a) < 2 or len(values_b) < 2:
            continue
        stat, p_value = ttest_ind(values_a, values_b, equal_var=False, nan_policy="omit")
        var_a = values_a.var(ddof=1)
        var_b = values_b.var(ddof=1)
        pooled_denom = ((len(values_a) - 1) * var_a + (len(values_b) - 1) * var_b)
        pooled_df = len(values_a) + len(values_b) - 2
        pooled_sd = float(np.sqrt(pooled_denom / pooled_df)) if pooled_df > 0 and pooled_denom >= 0 else float("nan")
        mean_diff = values_a.mean() - values_b.mean()
        cohen_d = float(mean_diff / pooled_sd) if pooled_sd and not np.isnan(pooled_sd) and pooled_sd != 0 else float("nan")
        results.append(
            {
                "group_a": group_a,
                "group_b": group_b,
                "stat": float(stat),
                "p_value": float(p_value),
                "cohen_d": cohen_d,
            }
        )

    if not results:
        return []

    correction = len(results)
    for entry in results:
        entry["p_adj"] = float(min(entry["p_value"] * correction, 1.0))

    results.sort(key=lambda row: row["p_adj"])
    return results


def top_recurring_artists(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    exposure = (
        df.groupby("artist")["playlist_id"].nunique().sort_values(ascending=False).head(limit)
    )
    return exposure.reset_index(name="playlist_count")


def build_summary(df: pd.DataFrame) -> str:
    lines: List[str] = []
    lines.append("# Afrobeats Playlist Bias Analysis\n")

    lines.append("## Regional representation\n")
    chi2_region, p_region, dof_region = chi_square_region(df)
    lines.append(f"Chi-square = {chi2_region:.2f}, df = {dof_region}, p-value = {p_region:.4f}\n")

    lines.append("## Label representation\n")
    chi2_label, p_label, dof_label = chi_square_label(df)
    lines.append(f"Chi-square = {chi2_label:.2f}, df = {dof_label}, p-value = {p_label:.4f}\n")

    lines.append("## Track popularity across curator types\n")
    anova_track, p_track = one_way_anova(df["track_popularity"], df["curator_type"])
    kruskal_track, p_kruskal_track = kruskal_wallis(df["track_popularity"], df["curator_type"])
    lines.append(f"ANOVA F = {anova_track:.2f}, p = {p_track:.4f}\n")
    lines.append(f"Kruskal-Wallis H = {kruskal_track:.2f}, p = {p_kruskal_track:.4f}\n")

    lines.append("## Artist popularity across curator types\n")
    anova_artist, p_artist = one_way_anova(df["artist_popularity"], df["curator_type"])
    kruskal_artist, p_kruskal_artist = kruskal_wallis(df["artist_popularity"], df["curator_type"])
    lines.append(f"ANOVA F = {anova_artist:.2f}, p = {p_artist:.4f}\n")
    lines.append(f"Kruskal-Wallis H = {kruskal_artist:.2f}, p = {p_kruskal_artist:.4f}\n")

    lines.append("## Artist follower counts across curator types\n")
    follower_series = df["artist_followers"]
    if follower_series.dropna().shape[0] < 6:
        lines.append("Not enough follower data points for reliable testing.\n")
    else:
        anova_followers, p_followers = one_way_anova(follower_series, df["curator_type"])
        eta_followers = compute_eta_squared(follower_series, df["curator_type"])
        kruskal_followers, p_kruskal_followers = kruskal_wallis(follower_series, df["curator_type"])
        lines.append(
            f"ANOVA F = {anova_followers:.2f}, p = {p_followers:.4f}, eta^2 = {eta_followers:.3f}\n"
        )
        lines.append(
            f"Kruskal-Wallis H = {kruskal_followers:.2f}, p = {p_kruskal_followers:.4f}\n"
        )

        post_hoc = pairwise_t_tests(follower_series, df["curator_type"])
        if post_hoc:
            lines.append("|Group A|Group B|t|p_adj|Cohen d|")
            lines.append("|---|---|---|---|---|")
            for entry in post_hoc[:5]:
                lines.append(
                    f"|{entry['group_a']}|{entry['group_b']}|{entry['stat']:.2f}|{entry['p_adj']:.4f}|{entry['cohen_d']:.2f}|"
                )
            lines.append("")
        else:
            lines.append("Pairwise tests skipped due to limited overlap across curator types.\n")

    lines.append("## Release year across curator types\n")
    anova_year, p_year = one_way_anova(df["release_year"], df["curator_type"])
    kruskal_year, p_kruskal_year = kruskal_wallis(df["release_year"], df["curator_type"])
    lines.append(f"ANOVA F = {anova_year:.2f}, p = {p_year:.4f}\n")
    lines.append(f"Kruskal-Wallis H = {kruskal_year:.2f}, p = {p_kruskal_year:.4f}\n")

    lines.append("## Top recurring artists\n")
    top_artists_df = top_recurring_artists(df)
    if not top_artists_df.empty:
        lines.append(top_artists_df.to_string(index=False))
        lines.append("\n")

    return "\n".join(lines)


def main() -> None:
    df = load_dataset()
    summary = build_summary(df)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(summary, encoding="utf-8")
    print("Analysis summary written to", OUTPUT_PATH)


if __name__ == "__main__":
    main()
