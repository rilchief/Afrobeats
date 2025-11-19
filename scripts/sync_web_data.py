"""Sync the processed playlist data with audio features to web/data.js.

This script updates the web/data.js file with the latest data from
data/processed/afrobeats_playlists.json, including audio features and
updated timestamps.
"""
from pathlib import Path
import json
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_FILE = REPO_ROOT / "data" / "processed" / "afrobeats_playlists.json"
OUTPUT_FILE = REPO_ROOT / "web" / "data.js"


def main():
    print("Loading processed playlist data with audio features...")
    
    if not PROCESSED_DATA_FILE.exists():
        print(f"Error: {PROCESSED_DATA_FILE} not found!")
        return
    
    with PROCESSED_DATA_FILE.open("r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    # Update the generated timestamp to current time
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    if "runMetadata" not in dataset:
        dataset["runMetadata"] = {}
    
    # Update timestamps
    dataset["runMetadata"]["generatedAt"] = current_time
    if "startedAt" not in dataset["runMetadata"]:
        dataset["runMetadata"]["startedAt"] = current_time
    
    # Check audio features coverage
    total_tracks = sum(len(p.get("tracks", [])) for p in dataset.get("playlists", []))
    tracks_with_features = 0
    
    for playlist in dataset.get("playlists", []):
        for track in playlist.get("tracks", []):
            if track.get("features") and isinstance(track["features"], dict):
                # Check if features has any valid numeric values
                if any(isinstance(v, (int, float)) and not (isinstance(v, bool)) for v in track["features"].values()):
                    tracks_with_features += 1
    
    coverage = (tracks_with_features / total_tracks * 100) if total_tracks > 0 else 0
    
    print(f"\nDataset Summary:")
    print(f"  Playlists: {len(dataset.get('playlists', []))}")
    print(f"  Total tracks: {total_tracks}")
    print(f"  Tracks with audio features: {tracks_with_features} ({coverage:.1f}%)")
    print(f"  Generated: {current_time}")
    
    # Write to web/data.js
    print(f"\nWriting to {OUTPUT_FILE.relative_to(REPO_ROOT)}...")
    
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        f.write("window.AFROBEATS_DATA = ")
        f.write(json.dumps(dataset, indent=2))
        f.write(";\n")
    
    # Also update the processed file with new timestamp
    with PROCESSED_DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully updated web/data.js")
    print(f"✓ Audio features: {coverage:.0f}% coverage")
    print(f"✓ Timestamp updated to: {current_time}")
    print(f"\n🔄 Please refresh your browser (Ctrl+F5 or Cmd+Shift+R) to see changes")


if __name__ == "__main__":
    main()
