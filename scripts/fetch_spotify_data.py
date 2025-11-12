"""Fetch playlist and track metadata from the Spotify Web API and
rewrite data/scripts/data.js for the Afrobeats dashboard.

Usage (PowerShell example):

  # 1. Ensure SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are available.
  #    Consider keeping them in a .env file next to this script.
  # 2. If requests isn't installed yet, run:  python -m pip install requests
  # 3. Execute the script from the repository root:
  #      python scripts/fetch_spotify_data.py
"""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"
OUTPUT_FILE = REPO_ROOT / "data" / "scripts" / "data.js"

# Update this structure with the playlists you want to analyse.
# Keys become the playlist ids in the dashboard output.
PLAYLIST_CONFIG = {
    "afrobeats-hits": {
        "id": "25Y75ozl2aI0NylFToefO5",
        "curatorType": "Independent Curator",
    },
    "afrobeats-2026": {
        "id": "5myeBzohhCVewaK2Thqmo5",
        "curatorType": "Independent Curator",
    },
}

ARTIST_METADATA = {
    "Rema": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Ayra Starr": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Burna Boy": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Wizkid": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Davido": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Tems": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Omah Lay": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "CKay": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Lojay": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Fireboy DML": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Joeboy": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Oxlade": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Tyla": {"artistCountry": "South Africa", "regionGroup": "Southern Africa", "diaspora": False},
    "Rotimi": {"artistCountry": "United States", "regionGroup": "US Diaspora", "diaspora": True},
    "Chris Brown": {"artistCountry": "United States", "regionGroup": "US Diaspora", "diaspora": True},
    "Don Toliver": {"artistCountry": "United States", "regionGroup": "US Diaspora", "diaspora": True},
    "Ed Sheeran": {"artistCountry": "United Kingdom", "regionGroup": "UK Collaborator", "diaspora": True},
    "Sarz": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Victony": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Mack H.D": {"artistCountry": "Canada", "regionGroup": "Diaspora Collective", "diaspora": True},
    "Black Sherif": {"artistCountry": "Ghana", "regionGroup": "Ghana", "diaspora": False},
    "King Promise": {"artistCountry": "Ghana", "regionGroup": "Ghana", "diaspora": False},
    "Amaarae": {"artistCountry": "Ghana", "regionGroup": "Ghana", "diaspora": True},
    "Stonebwoy": {"artistCountry": "Ghana", "regionGroup": "Ghana", "diaspora": False},
    "Kuami Eugene": {"artistCountry": "Ghana", "regionGroup": "Ghana", "diaspora": False},
    "Lasmid": {"artistCountry": "Ghana", "regionGroup": "Ghana", "diaspora": False},
    "Shatta Wale": {"artistCountry": "Ghana", "regionGroup": "Ghana", "diaspora": False},
    "Teni": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Tiwa Savage": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Kizz Daniel": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Mr Eazi": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
    "Yemi Alade": {"artistCountry": "Nigeria", "regionGroup": "Nigeria", "diaspora": False},
}


def load_env_file(path: Path) -> None:
    """Populate os.environ with variables from a simple KEY=VALUE .env file."""
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"')
        os.environ.setdefault(key, value)


def build_basic_auth_header(client_id: str, client_secret: str) -> str:
    token = base64.b64encode(f"{client_id}:{client_secret}".encode("ascii")).decode("ascii")
    return f"Basic {token}"


def get_access_token(client_id: str, client_secret: str) -> str:
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers={"Authorization": build_basic_auth_header(client_id, client_secret)},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["access_token"]


def fetch_playlist_snapshot(playlist_id: str, token: str) -> Dict:
    """Fetch playlist metadata plus the first page of tracks."""
    response = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def fetch_all_playlist_tracks(playlist: Dict, token: str) -> List[Dict]:
    """Walk the paginated playlist tracks feed and collect all track entries."""
    items: List[Dict] = []
    tracks_block = playlist.get("tracks", {})
    next_url = tracks_block.get("next")
    items.extend(tracks_block.get("items", []))

    while next_url:
        response = requests.get(next_url, headers={"Authorization": f"Bearer {token}"}, timeout=20)
        response.raise_for_status()
        page = response.json()
        next_url = page.get("next")
        items.extend(page.get("items", []))

    return items


def chunked(iterable: Iterable[str], size: int) -> Iterable[List[str]]:
    chunk: List[str] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def fetch_audio_features(track_ids: List[str], token: str) -> Dict[str, Dict]:
    features: Dict[str, Dict] = {}
    for batch in chunked(track_ids, 100):
        try:
            response = requests.get(
                "https://api.spotify.com/v1/audio-features",
                params={"ids": ",".join(batch)},
                headers={"Authorization": f"Bearer {token}"},
                timeout=20,
            )
            response.raise_for_status()
        except requests.HTTPError as error:
            print(
                "Warning: audio-features request failed",
                getattr(error.response, "status_code", "?"),
                getattr(error.response, "text", ""),
            )
            continue
        for entry in response.json().get("audio_features", []) or []:
            if entry and entry.get("id"):
                features[entry["id"]] = entry
    return features


def parse_release_year(album: Optional[Dict]) -> Optional[int]:
    if not album:
        return None
    release_date = album.get("release_date")
    if not release_date:
        return None
    try:
        return datetime.fromisoformat(release_date[:10]).year
    except ValueError:
        try:
            return int(release_date[:4])
        except (TypeError, ValueError):
            return None


def build_track_payload(track_item: Dict, feature: Optional[Dict]) -> Optional[Dict]:
    track = track_item.get("track")
    if not track or track.get("is_local"):
        return None

    track_id = track.get("id")
    if not track_id:
        return None

    artists = track.get("artists", [])
    artist_names = ", ".join(artist.get("name", "Unknown") for artist in artists) or "Unknown"
    primary_artist = artists[0].get("name") if artists else None
    metadata = ARTIST_METADATA.get(primary_artist or "")

    features_block = None
    if feature:
        features_block = {
            "danceability": feature.get("danceability"),
            "energy": feature.get("energy"),
            "valence": feature.get("valence"),
            "tempo": feature.get("tempo"),
            "acousticness": feature.get("acousticness"),
        }

    return {
        "id": track_id,
        "title": track.get("name", "Unknown"),
        "artist": artist_names,
        "artistCountry": metadata.get("artistCountry") if metadata else "Unknown",
        "regionGroup": metadata.get("regionGroup") if metadata else "Unknown",
        "diaspora": metadata.get("diaspora") if metadata else False,
        "releaseYear": parse_release_year(track.get("album")),
        "features": features_block,
    }


def normalize_playlist(playlist_id: str, config: Dict, token: str) -> Dict:
    snapshot = fetch_playlist_snapshot(config["id"], token)
    track_items = fetch_all_playlist_tracks(snapshot, token)
    track_ids = [item.get("track", {}).get("id") for item in track_items if item.get("track")]
    track_ids = [track_id for track_id in track_ids if track_id]

    audio_features = fetch_audio_features(track_ids, token) if track_ids else {}

    tracks_payload: List[Dict] = []
    for item in track_items:
        track_id = item.get("track", {}).get("id")
        payload = build_track_payload(item, audio_features.get(track_id))
        if payload:
            tracks_payload.append(payload)

    playlist_owner = snapshot.get("owner", {})
    followers = snapshot.get("followers", {}).get("total")

    launch_year = None
    if snapshot.get("tracks", {}).get("items"):
        first_year = parse_release_year(snapshot["tracks"]["items"][0].get("track", {}).get("album"))
        launch_year = first_year

    return {
        "id": playlist_id,
        "name": snapshot.get("name", config.get("label", playlist_id)),
        "curatorType": config.get("curatorType", "Unknown"),
        "curator": playlist_owner.get("display_name") or playlist_owner.get("id") or "Unknown",
        "followerCount": followers,
        "launchYear": launch_year,
        "description": snapshot.get("description"),
        "tracks": tracks_payload,
    }


def main() -> None:
    load_env_file(ENV_FILE)

    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set.")

    if not PLAYLIST_CONFIG:
        raise SystemExit("PLAYLIST_CONFIG is empty. Populate it with playlist ids before running.")

    access_token = get_access_token(client_id, client_secret)

    playlists_payload: List[Dict] = []
    for slug, cfg in PLAYLIST_CONFIG.items():
        if "id" not in cfg:
            raise SystemExit(f"Playlist config for '{slug}' is missing an 'id'.")
        print(f"Fetching playlist {slug} ({cfg['id']})...", flush=True)
        playlists_payload.append(normalize_playlist(slug, cfg, access_token))

    dataset = {"playlists": playlists_payload}

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        "window.AFROBEATS_DATA = " + json.dumps(dataset, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
