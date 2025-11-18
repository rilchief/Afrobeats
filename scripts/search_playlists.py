"""Search Spotify for Afrobeats playlists (editorial and credible) and optionally update playlist_config.json.

Usage examples (PowerShell):
  # Show Spotify-owned editorial matches across markets
  python scripts/search_playlists.py --keywords "African Heat" "Afrobeats" "Afro Hits" \
      --markets NG GH KE ZA US GB --spotify-only

  # Also include credible curators (not just Spotify) and write to config
  python scripts/search_playlists.py --keywords "Afrobeats" "Afrobeats Hits" \
      --markets NG GH KE ZA US GB --write-config
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env"
PLAYLIST_CONFIG_FILE = REPO_ROOT / "data" / "playlist_config.json"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"'))


def basic_auth_header(client_id: str, client_secret: str) -> str:
    token = base64.b64encode(f"{client_id}:{client_secret}".encode("ascii")).decode("ascii")
    return f"Basic {token}"


def get_client_credentials_token(client_id: str, client_secret: str) -> str:
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers={"Authorization": basic_auth_header(client_id, client_secret)},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def refresh_user_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        headers={"Authorization": basic_auth_header(client_id, client_secret)},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("access_token"):
        raise SystemExit("Failed to refresh Spotify access token; check SPOTIFY_REFRESH_TOKEN.")
    return data["access_token"]


def ensure_access_token() -> str:
    load_env_file(ENV_FILE)
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env")
    refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
    if refresh_token:
        return refresh_user_token(client_id, client_secret, refresh_token)
    return get_client_credentials_token(client_id, client_secret)


def load_playlist_config(path: Path) -> Dict[str, Dict]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    cfg = payload.get("playlists") if isinstance(payload, dict) else payload
    return cfg if isinstance(cfg, dict) else {}


def write_playlist_config(path: Path, config: Dict[str, Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"playlists": config}, indent=2) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    import re
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "playlist"


@dataclass
class FoundPlaylist:
    id: str
    name: str
    owner_id: str
    owner_name: str
    followers: Optional[int]
    market: str

    @property
    def is_spotify_editorial(self) -> bool:
        oid = (self.owner_id or "").lower()
        return oid == "spotify" or oid.startswith("spotify")


def fetch_playlist_details(pid: str, token: str, market: Optional[str]) -> Dict:
    params = {"market": market} if market else None
    r = requests.get(
        f"https://api.spotify.com/v1/playlists/{pid}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=20,
    )
    if r.status_code == 404 and market:
        # Retry without market
        r = requests.get(
            f"https://api.spotify.com/v1/playlists/{pid}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
    r.raise_for_status()
    return r.json()


def search_playlists(
    *,
    keywords: Sequence[str],
    markets: Sequence[str],
    token: str,
    spotify_only: bool,
) -> List[FoundPlaylist]:
    headers = {"Authorization": f"Bearer {token}"}
    seen: set[str] = set()
    results: List[FoundPlaylist] = []

    for kw in keywords:
        for market in markets:
            try:
                resp = requests.get(
                    "https://api.spotify.com/v1/search",
                    params={"q": kw, "type": "playlist", "limit": 15, "market": market},
                    headers=headers,
                    timeout=20,
                )
                resp.raise_for_status()
            except requests.RequestException as exc:
                print(f"! search error for '{kw}' market={market}: {exc}")
                continue
            items = (resp.json().get("playlists", {}) or {}).get("items", []) or []
            for it in items:
                if not it:
                    continue
                pid = it.get("id")
                if not pid or pid in seen:
                    continue
                owner = it.get("owner") or {}
                owner_id = owner.get("id") or ""
                owner_name = owner.get("display_name") or owner_id or "?"
                name = it.get("name") or pid
                # Fetch details to get followers and validate availability
                try:
                    det = fetch_playlist_details(pid, token, market)
                except requests.RequestException as exc:
                    # Skip if still not available
                    print(f"  - skip {name} ({pid}) market={market}: {exc}")
                    continue
                followers = (det.get("followers") or {}).get("total")
                found = FoundPlaylist(
                    id=pid,
                    name=name,
                    owner_id=owner_id,
                    owner_name=owner_name,
                    followers=followers,
                    market=market,
                )
                if spotify_only and not found.is_spotify_editorial:
                    continue
                seen.add(pid)
                results.append(found)
    return results


def add_to_config(found: List[FoundPlaylist]) -> List[Tuple[str, Dict]]:
    cfg = load_playlist_config(PLAYLIST_CONFIG_FILE)
    existing_ids = {v.get("id") for v in cfg.values() if isinstance(v, dict)}
    added: List[Tuple[str, Dict]] = []
    for pl in found:
        if pl.id in existing_ids:
            continue
        slug_base = slugify(pl.name)
        slug = slug_base
        n = 2
        while slug in cfg:
            slug = f"{slug_base}-{n}"
            n += 1
        curator = "Spotify Editorial" if pl.is_spotify_editorial else "Curated"
        entry = {
            "id": pl.id,
            "curatorType": curator,
            "label": pl.name,
            "market": pl.market,
        }
        cfg[slug] = entry
        added.append((slug, entry))
    if added:
        write_playlist_config(PLAYLIST_CONFIG_FILE, cfg)
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Spotify for Afrobeats playlists")
    parser.add_argument(
        "--keywords",
        nargs="*",
        default=[
            "African Heat",
            "Afrobeats",
            "Afrobeats Hits",
            "Afrobeats Mix",
            "Afro Hits",
            "Afro Party",
            "Afropop",
            "RADAR Africa",
            "EQUAL Africa",
            "New Music Africa",
            "Afrobeats Radio",
        ],
        help="Search keywords (playlist names/aliases)",
    )
    parser.add_argument(
        "--markets",
        nargs="*",
        default=[os.getenv("SPOTIFY_MARKET") or "NG", "GH", "KE", "ZA", "US", "GB"],
        help="Market codes to search",
    )
    parser.add_argument("--spotify-only", action="store_true", help="Limit to Spotify-owned playlists")
    parser.add_argument("--write-config", action="store_true", help="Append findings to playlist_config.json")
    args = parser.parse_args()

    token = ensure_access_token()
    found = search_playlists(
        keywords=args.keywords,
        markets=args.markets,
        token=token,
        spotify_only=args.spotify_only,
    )

    if not found:
        print("No playlists found.")
        return

    # Present results
    print("\nFound playlists:\n")
    # Sort: Spotify editorial first, then by followers desc
    found.sort(key=lambda x: (not x.is_spotify_editorial, -(x.followers or 0), x.name.lower()))
    for pl in found:
        kind = "Spotify" if pl.is_spotify_editorial else "Curated"
        print(f"- [{kind}] {pl.name} | id={pl.id} | owner={pl.owner_name} | followers={pl.followers} | market={pl.market}")

    if args.write_config:
        added = add_to_config(found)
        if added:
            print("\nAdded to playlist_config.json:")
            for slug, entry in added:
                print(f"  - {slug}: {entry['id']} ({entry['label']}) [{entry.get('market')}] {entry['curatorType']}")
        else:
            print("\nNo new entries added (IDs already present).")


if __name__ == "__main__":
    main()
