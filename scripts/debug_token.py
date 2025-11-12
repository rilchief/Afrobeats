from __future__ import annotations

import base64
import os
from pathlib import Path

import requests


def load_env(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing .env file at {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    load_env(repo_root / ".env")

    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit("Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET")

    token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers={"Authorization": "Basic " + token},
        timeout=15,
    )
    print("Status:", response.status_code)
    print("Body:", response.json())

    if response.status_code != 200:
        return

    access_token = response.json().get("access_token")
    if not access_token:
        return

    playlist_id = "37i9dQZF1DWYkaDif7Ztbp"
    playlist_response = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    print("\nPlaylist status:", playlist_response.status_code)
    try:
        print("Playlist body:", playlist_response.json())
    except Exception:
        print("Playlist body could not be parsed as JSON.")

    search_response = requests.get(
        "https://api.spotify.com/v1/search",
        params={"q": "afrobeats", "type": "playlist", "limit": 5},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    print("\nSearch status:", search_response.status_code)
    try:
        data = search_response.json()
        print("Top search results (id, name):")
        for item in data.get("playlists", {}).get("items", []):
            if not isinstance(item, dict):
                continue
            print("  ", item.get("id"), "-", item.get("name"))
    except Exception:
        print("Search body could not be parsed as JSON. Raw response:")
        print(search_response.text[:1000])


if __name__ == "__main__":
    main()
