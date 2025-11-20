"""Export track data with audio features to CSV for analysis.

This script extracts all tracks from the playlist JSON and creates a comprehensive
CSV file including metadata and audio features. For collaborative tracks, it combines
all artist countries and regions (e.g., "Nigeria, United Kingdom").
"""
from pathlib import Path
import json
import pandas as pd
import csv

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "processed" / "afrobeats_playlists.json"
METADATA_PATH = REPO_ROOT / "data" / "data" / "artist_metadata.csv"
OUTPUT_PATH = REPO_ROOT / "outputs" / "tracks_with_audio_features.csv"


def load_artist_metadata():
    """Load artist metadata from CSV"""
    artist_map = {}
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            artist_map[row['artist'].strip()] = {
                'country': row['artistCountry'],
                'region': row['regionGroup'],
                'diaspora': row['diaspora']
            }
    return artist_map


def get_combined_metadata(artist_string, artist_map):
    """Get combined country and region for all artists in a track"""
    artists = [a.strip() for a in artist_string.split(',')]
    
    countries = []
    regions = []
    diaspora_flags = []
    
    for artist in artists:
        if artist in artist_map:
            metadata = artist_map[artist]
            countries.append(metadata['country'])
            regions.append(metadata['region'])
            diaspora_flags.append(metadata['diaspora'])
        else:
            countries.append('Unknown')
            regions.append('Unknown')
            diaspora_flags.append('FALSE')
    
    # Deduplicate while preserving order
    unique_countries = []
    unique_regions = []
    seen_countries = set()
    seen_regions = set()
    
    for country, region in zip(countries, regions):
        if country not in seen_countries:
            unique_countries.append(country)
            seen_countries.add(country)
        if region not in seen_regions:
            unique_regions.append(region)
            seen_regions.add(region)
    
    # Check if any artist is diaspora
    is_diaspora = any(d.upper() == 'TRUE' for d in diaspora_flags)
    
    return {
        'countries': ', '.join(unique_countries),
        'regions': ', '.join(unique_regions),
        'diaspora': is_diaspora
    }


def main():
    print("📊 Loading artist metadata...")
    artist_map = load_artist_metadata()
    print(f"   Found {len(artist_map)} artists")
    
    print("\n📂 Loading playlist data...")
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    playlists = data.get("playlists", [])
    
    # Extract all tracks with audio features
    tracks = []
    multi_artist_count = 0
    
    for playlist in playlists:
        playlist_id = playlist.get("id")
        playlist_name = playlist.get("name")
        curator_type = playlist.get("curatorType")
        curator = playlist.get("curator")
        followers = playlist.get("followerCount")
        
        for track in playlist.get("tracks", []):
            # Features removed from dataset; set empty dict
            features = {}
            artist_string = track.get("artist", '')
            
            # Get combined metadata for all artists
            combined = get_combined_metadata(artist_string, artist_map)
            
            if ',' in artist_string:
                multi_artist_count += 1
            
            track_row = {
                # Playlist info
                "playlist_id": playlist_id,
                "playlist_name": playlist_name,
                "curator_type": curator_type,
                "curator": curator,
                "playlist_followers": followers,
                
                # Track info
                "track_id": track.get("id"),
                "track_title": track.get("title"),
                "artist": artist_string,
                "artist_id": track.get("artistId"),
                "artist_country": combined['countries'],
                "region_group": combined['regions'],
                "diaspora": combined['diaspora'],
                
                # Popularity & position
                "track_popularity": track.get("trackPopularity"),
                "artist_popularity": track.get("artistPopularity"),
                "playlist_position": track.get("playlistPosition"),
                
                # Release info
                "release_year": track.get("releaseYear"),
                "album_label": track.get("albumLabel"),
                "label_type": "Major" if track.get("albumLabel") and any(
                    label in str(track.get("albumLabel")).lower() 
                    for label in ["sony", "warner", "universal", "def jam"]
                ) else "Independent",
                
                # Audio features
                # Audio features no longer available (simulation removed)
                "danceability": None,
                "energy": None,
                "valence": None,
                "tempo": None,
                "acousticness": None,
                "instrumentalness": None,
                "liveness": None,
                "speechiness": None,
                "loudness": None,
                "key": None,
                "mode": None,
                "time_signature": None,
            }
            tracks.append(track_row)
    
    # Create DataFrame
    df = pd.DataFrame(tracks)
    
    unknown_count = df['artist_country'].str.contains('Unknown').sum()
    
    print(f"\n📈 Dataset Summary:")
    print(f"   Total tracks: {len(df)}")
    print(f"   Unique playlists: {df['playlist_id'].nunique()}")
    print(f"   Multi-artist tracks: {multi_artist_count}")
    print(f"   Tracks with audio features: {df['danceability'].notna().sum()}")
    print(f"   Tracks with Unknown country: {unknown_count}")
    print(f"   Tracks with full metadata: {len(df) - unknown_count}")
    
    # Save to CSV
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    
    print(f"\n✅ Exported to: {OUTPUT_PATH}")
    
    # Show sample multi-artist tracks
    print(f"\n📝 Sample multi-artist tracks:")
    multi_artist_df = df[df['artist'].str.contains(',', na=False)].head(5)
    for _, row in multi_artist_df.iterrows():
        print(f"   • {row['artist']}")
        print(f"     Countries: {row['artist_country']}")
        print(f"     Regions: {row['region_group']}")
    

    print("Loading playlist data...")
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    playlists = data.get("playlists", [])
    
    # Extract all tracks with audio features
    tracks = []
    for playlist in playlists:
        playlist_id = playlist.get("id")
        playlist_name = playlist.get("name")
        curator_type = playlist.get("curatorType")
        curator = playlist.get("curator")
        followers = playlist.get("followerCount")
        
        for track in playlist.get("tracks", []):
            features = {}
            
            track_row = {
                # Playlist info
                "playlist_id": playlist_id,
                "playlist_name": playlist_name,
                "curator_type": curator_type,
                "curator": curator,
                "playlist_followers": followers,
                
                # Track info
                "track_id": track.get("id"),
                "track_title": track.get("title"),
                "artist": track.get("artist"),
                "artist_id": track.get("artistId"),
                "artist_country": track.get("artistCountry"),
                "region_group": track.get("regionGroup"),
                "diaspora": track.get("diaspora"),
                
                # Popularity & position
                "track_popularity": track.get("trackPopularity"),
                "artist_popularity": track.get("artistPopularity"),
                "playlist_position": track.get("playlistPosition"),
                
                # Release info
                "release_year": track.get("releaseYear"),
                "album_label": track.get("albumLabel"),
                "label_type": "Major" if track.get("albumLabel") and any(
                    label in str(track.get("albumLabel")).lower() 
                    for label in ["sony", "warner", "universal", "def jam"]
                ) else "Independent",
                
                # Audio features
                "danceability": None,
                "energy": None,
                "valence": None,
                "tempo": None,
                "acousticness": None,
                "instrumentalness": None,
                "liveness": None,
                "speechiness": None,
                "loudness": None,
                "key": None,
                "mode": None,
                "time_signature": None,
            }
            tracks.append(track_row)
    
    # Create DataFrame
    df = pd.DataFrame(tracks)
    
    print(f"\nDataset Summary:")
    print(f"Total tracks: {len(df)}")
    print(f"Unique playlists: {df['playlist_id'].nunique()}")
    print(f"Unique artists: {df['artist'].nunique()}")
    print(f"Tracks with audio features: {df['danceability'].notna().sum()}")
    
    # Save to CSV
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    
    print(f"\n✓ Exported to: {OUTPUT_PATH}")
    print(f"\nColumns: {', '.join(df.columns.tolist())}")
    
    # Show preview
    print("\nPreview (first 5 rows):")
    preview_cols = ["track_title", "artist", "curator_type", "danceability", "energy", "tempo"]
    print(df[preview_cols].head().to_string(index=False))
    
    # Audio features summary statistics
    if df["danceability"].notna().any():
        print("\n\nAudio Features Summary Statistics:")
        audio_cols = ["danceability", "energy", "valence", "tempo"]
        print(df[audio_cols].describe().round(3).to_string())
        
        print("\n\nAudio Features by Curator Type:")
        curator_summary = df.groupby("curator_type")[audio_cols].mean().round(3)
        print(curator_summary.to_string())


if __name__ == "__main__":
    main()
