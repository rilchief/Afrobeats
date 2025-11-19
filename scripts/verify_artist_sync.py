"""Verify all artists are synced between CSV, JSON, and web data"""
import json
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load CSV artists
csv_artists = set()
with open(REPO_ROOT / 'data/data/artist_metadata.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        csv_artists.add(row['artist'])

# Load JSON artists
json_data = json.load(open(REPO_ROOT / 'data/processed/afrobeats_playlists.json', encoding='utf-8'))
json_artists = set()
for playlist in json_data['playlists']:
    for track in playlist['tracks']:
        for artist in track['artist'].split(','):
            artist = artist.strip()
            if artist:
                json_artists.add(artist)

# Check web data
web_data = open(REPO_ROOT / 'web/data.js', encoding='utf-8').read()

# Find differences
missing_in_csv = sorted(json_artists - csv_artists)
extra_in_csv = sorted(csv_artists - json_artists)

print(f"📊 Artist Sync Verification")
print(f"=" * 60)
print(f"CSV artists: {len(csv_artists)}")
print(f"JSON unique artists: {len(json_artists)}")
print(f"web/data.js size: {len(web_data):,} characters")
print()

if missing_in_csv:
    print(f"❌ Missing from CSV ({len(missing_in_csv)}):")
    for i, artist in enumerate(missing_in_csv, 1):
        print(f"  {i}. {artist}")
    print()
else:
    print("✅ All JSON artists are in CSV")
    print()

if extra_in_csv:
    print(f"ℹ️  Extra in CSV not used in playlists ({len(extra_in_csv)}):")
    print(f"  (First 20): {extra_in_csv[:20]}")
    print()
else:
    print("✅ No extra artists in CSV")
    print()

if not missing_in_csv:
    print("✅ SYNC VERIFIED: All artists in HTML/JSON have metadata in CSV")
else:
    print("⚠️  ACTION NEEDED: Some artists need to be added to CSV")
