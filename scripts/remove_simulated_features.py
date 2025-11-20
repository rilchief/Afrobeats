"""Remove simulated audio features from processed playlist dataset.

This script deletes the "features" key from every track in
`data/processed/afrobeats_playlists.json` and reports counts.
Run once to revert dataset to pre-simulation state.
"""
from __future__ import annotations
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "processed" / "afrobeats_playlists.json"
BACKUP_FILE = REPO_ROOT / "data" / "processed" / "afrobeats_playlists_with_features_backup.json"


def main() -> None:
    if not DATA_FILE.exists():
        raise SystemExit(f"Dataset not found: {DATA_FILE}")

    with DATA_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    playlists = data.get("playlists", [])
    total_tracks = 0
    removed = 0
    for playlist in playlists:
        for track in playlist.get("tracks", []):
            total_tracks += 1
            if "features" in track:
                removed += 1
                track.pop("features", None)

    # Backup original with features before overwrite
    if removed:
        with BACKUP_FILE.open("w", encoding="utf-8") as bf:
            json.dump(data, bf, indent=2, ensure_ascii=False)

    # Write cleaned file (without features)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Processed tracks: {total_tracks}")
    print(f"Removed feature blocks: {removed}")
    if removed:
        print(f"Backup (with features) saved to: {BACKUP_FILE}")
    else:
        print("No feature blocks found; dataset already clean.")


if __name__ == "__main__":
    main()
