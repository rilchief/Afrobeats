"""Quick test to verify audio features are loaded correctly."""
import json
from pathlib import Path

data = json.loads(Path("data/processed/afrobeats_playlists.json").read_text(encoding="utf-8"))
track = data["playlists"][0]["tracks"][0]
print(f"Track: {track['title']} by {track['artist']}")
print(f"Has features: {'features' in track}")
if "features" in track:
    features = track["features"]
    print(f"Danceability: {features.get('danceability')}")
    print(f"Energy: {features.get('energy')}")
    print(f"Valence: {features.get('valence')}")
    print(f"Tempo: {features.get('tempo')}")
    print("✓ Audio features loaded successfully!")
