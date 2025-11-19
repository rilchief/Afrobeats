"""Search for Spotify Editorial Afrobeats playlists"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
))

# Search for Afrobeats playlists
print("Searching for Afrobeats playlists...\n")
results = sp.search(q='Afrobeats', type='playlist', limit=50)

print("=" * 80)
print("SPOTIFY EDITORIAL PLAYLISTS:")
print("=" * 80)

spotify_playlists = []
for p in results['playlists']['items']:
    if p and p.get('owner') and p['owner'].get('id') == 'spotify':
        spotify_playlists.append(p)
        print(f"\n✓ {p['name']}")
        print(f"  ID: {p['id']}")
        print(f"  Followers: {p.get('followers', {}).get('total', 0):,}")
        print(f"  Tracks: {p.get('tracks', {}).get('total', 0)}")

if not spotify_playlists:
    print("\nNo Spotify Editorial playlists found.")
    print("\nShowing all playlists:")
    print("=" * 80)
    for p in results['playlists']['items']:
        if p:
            print(f"\n{p.get('name', 'Unknown')}")
            print(f"  ID: {p.get('id', 'Unknown')}")
            owner = p.get('owner', {})
            print(f"  Owner: {owner.get('display_name', 'Unknown')} ({owner.get('id', 'Unknown')})")
            print(f"  Followers: {p.get('followers', {}).get('total', 0):,}")

print(f"\n\nTotal Spotify Editorial playlists found: {len(spotify_playlists)}")
