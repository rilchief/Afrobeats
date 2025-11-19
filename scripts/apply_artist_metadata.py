"""
Apply updated artist metadata from CSV to the processed JSON file
This will update artist countries/regions and recalculate missing artists
"""
import json
import csv
from pathlib import Path
from datetime import datetime

def load_artist_metadata_csv(csv_path):
    """Load artist metadata from CSV into a dictionary"""
    artist_map = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Store by normalized artist name
            artist_name = row['artist'].strip()
            artist_map[artist_name] = {
                'country': row['artistCountry'],
                'region': row['regionGroup'],
                'diaspora': row['diaspora'].upper() == 'TRUE'
            }
    return artist_map

def get_first_artist_name(artist_string):
    """Extract first artist name from collaboration string"""
    return artist_string.split(',')[0].strip()

def apply_metadata_to_json(json_path, artist_map):
    """Apply artist metadata to all tracks in the JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_artists = set()
    missing_artists = []
    updated_tracks = 0
    
    # Process all tracks
    for playlist in data['playlists']:
        for track in playlist['tracks']:
            artist_name = get_first_artist_name(track.get('artist', ''))
            all_artists.add(artist_name)
            
            if artist_name in artist_map:
                # Update track with CSV metadata
                metadata = artist_map[artist_name]
                track['artistCountry'] = metadata['country']
                track['regionGroup'] = metadata['region']
                track['diaspora'] = metadata['diaspora']
                updated_tracks += 1
            else:
                # Track missing artist
                if artist_name not in missing_artists:
                    missing_artists.append(artist_name)
    
    # Update run metadata
    if 'runMetadata' not in data:
        data['runMetadata'] = {}
    
    data['runMetadata']['missingArtists'] = sorted(missing_artists)
    data['runMetadata']['artistCount'] = len(all_artists)
    data['runMetadata']['metadataUpdatedAt'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    return data, updated_tracks, len(missing_artists), len(all_artists)

def main():
    base_path = Path(__file__).parent.parent
    csv_path = base_path / 'data' / 'data' / 'artist_metadata.csv'
    json_path = base_path / 'data' / 'processed' / 'afrobeats_playlists.json'
    
    print("📊 Loading artist metadata from CSV...")
    artist_map = load_artist_metadata_csv(csv_path)
    print(f"   Found {len(artist_map)} artists in CSV")
    
    print("\n🔄 Applying metadata to tracks...")
    updated_data, updated_tracks, missing_count, total_artists = apply_metadata_to_json(json_path, artist_map)
    
    print(f"   ✓ Updated {updated_tracks} track entries")
    print(f"   ✓ Total unique artists: {total_artists}")
    print(f"   ✓ Artists with metadata: {total_artists - missing_count}")
    print(f"   ⚠ Missing metadata: {missing_count}")
    
    if missing_count > 0:
        print(f"\n   Missing artists: {', '.join(updated_data['runMetadata']['missingArtists'][:10])}...")
    
    # Write updated JSON
    print("\n💾 Writing updated JSON...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ Saved to {json_path}")
    
    # Update web/data.js as well
    web_data_path = base_path / 'web' / 'data.js'
    print(f"\n💾 Updating web/data.js...")
    with open(web_data_path, 'w', encoding='utf-8') as f:
        f.write('window.AFROBEATS_DATA = ')
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
        f.write(';\n')
    
    print(f"   ✓ Saved to {web_data_path}")
    
    print("\n✅ Update complete!")
    print(f"   • Artists in CSV: {len(artist_map)}")
    print(f"   • Total unique artists: {total_artists}")
    print(f"   • Coverage: {((total_artists - missing_count) / total_artists * 100):.1f}%")
    print(f"   • Missing: {missing_count} artists")

if __name__ == "__main__":
    main()
