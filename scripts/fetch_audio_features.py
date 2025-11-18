"""Fetch playlist-level audio features using Spotipy.

This script mirrors the user's snippet but integrates with the existing repo:

Usage (PowerShell):
  # Install dependencies once
  python -m pip install spotipy pandas

  # Fetch audio features for every playlist in data/playlist_config.json
  python scripts/fetch_audio_features.py

  # Limit to a couple of playlists by slug from playlist_config.json
  python scripts/fetch_audio_features.py --slugs afrobeats-hits afro-nation-united

Outputs:
  - outputs/audio_features.csv (wide table of meta + audio features)
  - outputs/audio_features_preview.parquet (optional parquet snapshot)
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from fetch_spotify_data import ENV_FILE, PLAYLIST_CONFIG_FILE, load_env_file

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "outputs"


def load_playlist_config(path: Path) -> Dict[str, Dict]:
    if not path.exists():
        raise SystemExit(f"Playlist config not found at {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    cfg = payload.get("playlists") if isinstance(payload, dict) else payload
    if not isinstance(cfg, dict):
        raise SystemExit("playlist_config.json must map slugs to playlist metadata")
    return cfg


def chunked(items: List[str], size: int = 100) -> Iterable[List[str]]:
    chunk: List[str] = []
    for item in items:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def get_playlist_dataframe(
    *,
    spotify_client: spotipy.Spotify,
    playlist_id: str,
    playlist_label: str,
    batch_size: int,
) -> pd.DataFrame:
    print(f"--- Scraping {playlist_label} ({playlist_id}) ---", flush=True)

    tracks_data: List[dict] = []
    results = spotify_client.playlist_items(playlist_id)
    tracks_data.extend(results.get("items", []))
    while results.get("next"):
        results = spotify_client.next(results)
        tracks_data.extend(results.get("items", []))

    track_meta: List[dict] = []
    track_ids: List[str] = []
    for item in tracks_data:
        track = item.get("track") if item else None
        if not track or not track.get("id"):
            continue
        track_ids.append(track["id"])
        track_meta.append(
            {
                "track_name": track.get("name"),
                "artist_name": (track.get("artists") or [{}])[0].get("name"),
                "album_name": (track.get("album") or {}).get("name"),
                "release_date": (track.get("album") or {}).get("release_date"),
                "popularity": track.get("popularity"),
                "track_id": track.get("id"),
                "playlist_source": playlist_label,
            }
        )

    audio_features_data: List[dict] = []
    for batch in chunked(track_ids, batch_size):
        try:
            features_batch = spotify_client.audio_features(batch)
        except spotipy.SpotifyException as exc:
            status = getattr(exc, "http_status", "?")
            print(f"  ! audio features batch failed (status {status}): {exc}")
            if len(batch) == 1:
                continue
            # Retry each track individually to detect per-track gating.
            for track_id in batch:
                try:
                    single = spotify_client.audio_features([track_id])
                except spotipy.SpotifyException as inner_exc:
                    status_inner = getattr(inner_exc, "http_status", "?")
                    print(f"    - fallback failed for {track_id} (status {status_inner}): {inner_exc}")
                    continue
                audio_features_data.extend([feat for feat in single or [] if feat])
                time.sleep(0.1)
            continue
        audio_features_data.extend([feat for feat in features_batch or [] if feat])
        time.sleep(0.2)

    df_meta = pd.DataFrame(track_meta)
    df_features = pd.DataFrame(audio_features_data)

    if df_meta.empty or df_features.empty:
        return pd.DataFrame()

    merged = pd.merge(df_meta, df_features, left_on="track_id", right_on="id", how="inner")
    if "id" in merged.columns:
        merged = merged.drop(columns=["id"])
    merged["bpm"] = merged.get("tempo")
    return merged


def build_spotify_client() -> spotipy.Spotify:
    load_env_file(ENV_FILE)
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env")
    manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=manager)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch playlist audio features via Spotipy")
    parser.add_argument(
        "--slugs",
        nargs="*",
        default=None,
        help="Optional playlist slugs from playlist_config.json to limit the run",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_DIR / "audio_features.csv",
        help="Path to write the combined CSV",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of track IDs per audio-features request (max 100)",
    )
    args = parser.parse_args()

    config = load_playlist_config(PLAYLIST_CONFIG_FILE)
    if args.slugs:
        missing = [slug for slug in args.slugs if slug not in config]
        if missing:
            raise SystemExit(f"Unknown playlist slugs: {', '.join(missing)}")
        selected = {slug: config[slug] for slug in args.slugs}
    else:
        selected = config

    client = build_spotify_client()
    frames: List[pd.DataFrame] = []
    for slug, meta in selected.items():
        playlist_id = meta.get("id")
        label = meta.get("label", slug)
        if not playlist_id:
            print(f"Skipping {slug}: missing playlist ID")
            continue
        try:
            df = get_playlist_dataframe(
                spotify_client=client,
                playlist_id=playlist_id,
                playlist_label=label,
                batch_size=max(1, min(args.batch_size, 100)),
            )
        except spotipy.SpotifyException as exc:
            print(f"Failed to scrape {label}: {exc}")
            continue
        if df.empty:
            print(f"No tracks/features for {label}")
            continue
        frames.append(df)

    if not frames:
        print("No data collected.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(args.output, index=False)
    parquet_path = Path(str(args.output)).with_suffix(".parquet")
    try:
        combined.to_parquet(parquet_path, index=False)
    except Exception as exc:
        print(f"Warning: failed to write parquet snapshot: {exc}")

    print(
        f"Success! Scraped {len(combined)} tracks from {len(frames)} playlists.\n"
        f"CSV: {args.output}\nParquet: {parquet_path}"
    )
    preview_cols = [col for col in ("track_name", "danceability", "energy", "bpm", "playlist_source") if col in combined]
    if preview_cols:
        print("\nPreview:")
        print(combined[preview_cols].head())


if __name__ == "__main__":
    main()
