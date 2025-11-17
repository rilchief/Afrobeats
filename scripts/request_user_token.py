"""Utility script to obtain a Spotify refresh token via the Authorization Code flow.

Usage:
1. Ensure SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI are set in .env.
2. Run:  python scripts/request_user_token.py
3. Follow the printed URL, authorise the app, then paste the redirected URL back into the prompt.
4. The script prints the access token (short-lived) and refresh token (store in .env as SPOTIFY_REFRESH_TOKEN).
"""
from __future__ import annotations

import base64
import os
import urllib.parse
import webbrowser
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


def build_authorize_url(client_id: str, redirect_uri: str, scope: str) -> str:
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
    }
    return "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)


def exchange_code_for_tokens(client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict:
    token = base64.b64encode(f"{client_id}:{client_secret}".encode("ascii")).decode("ascii")
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        },
        headers={"Authorization": f"Basic {token}"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    load_env(repo_root / ".env")

    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

    if not client_id or not client_secret:
        raise SystemExit("Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in environment")

    scope = "playlist-read-private user-read-private user-library-read"
    auth_url = build_authorize_url(client_id, redirect_uri, scope)
    print("Authorize URL:\n", auth_url)

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    redirect_response = input("\nAfter authorising, paste the full redirect URL here:\n").strip()
    if "code=" not in redirect_response:
        raise SystemExit("No authorization code found in the provided URL.")

    parsed = urllib.parse.urlparse(redirect_response)
    query = urllib.parse.parse_qs(parsed.query)
    code = query.get("code", [None])[0]
    if not code:
        raise SystemExit("Unable to parse authorization code from redirect URL.")

    token_data = exchange_code_for_tokens(client_id, client_secret, code, redirect_uri)
    print("\nAccess token:", token_data.get("access_token"))
    print("Expires in (s):", token_data.get("expires_in"))
    print("Refresh token:", token_data.get("refresh_token"))


if __name__ == "__main__":
    main()
