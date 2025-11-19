# Spotify Editorial Playlists - Addition Plan

## Summary

I've identified **6 official Spotify Editorial playlists** to add to your dataset for a more comprehensive gatekeeping analysis.

## New Playlists to Add

### Core Spotify Editorial Playlists:

1. **Afrobeats Hits (Spotify)**
   - Playlist ID: `37i9dQZF1EQqFPe2ux3rbj`
   - Curator: Spotify Editorial
   - Why: Main Afrobeats editorial playlist, high follower count

2. **Naija Hits** 
   - Playlist ID: `37i9dQZEVXbKY7jLzlJ11V`
   - Curator: Spotify Editorial
   - Why: Nigeria's top chart - critical for regional bias analysis

3. **Afro Fire**
   - Playlist ID: `37i9dQZF1DWYkztttC2YdR`
   - Curator: Spotify Editorial
   - Why: "Hottest" tracks - shows Spotify's selection criteria

4. **New Afrobeats**
   - Playlist ID: `37i9dQZF1DX4pJhijJmndF`
   - Curator: Spotify Editorial
   - Why: Latest releases - shows temporal gatekeeping patterns

5. **Ghana Hits**
   - Playlist ID: `37i9dQZEVXbJkgIdfsJyTv`
   - Curator: Spotify Editorial
   - Why: Ghana chart - compares Nigeria vs Ghana representation

6. **African Heat**
   - Playlist ID: `37i9dQZF1DX7QOv5kjbU68`
   - Curator: Spotify Editorial
   - Why: Broader African music - shows Afrobeats within African context

## Updated Dataset Composition

### Before (13 playlists):
- Independent Curators: 4
- Media Publishers: 7
- User-Generated: 1
- Festival Curators: 1
- **Spotify Editorial: 0**

### After (19 playlists):
- Independent Curators: 4 (21%)
- Media Publishers: 7 (37%)
- User-Generated: 1 (5%)
- Festival Curators: 1 (5%)
- **Spotify Editorial: 6 (32%)** ⭐

## Dissertation Impact

### Enhanced Analysis Opportunities:

1. **Institutional Gatekeeping**
   - Compare Spotify Editorial vs Independent curators
   - Analyze algorithmic + editorial curation patterns
   - Examine power dynamics in platform-controlled playlists

2. **Regional Bias Validation**
   - Cross-validate findings across curator types
   - Compare Nigeria-centric bias in editorial vs independent playlists
   - Analyze Ghana Hits vs Naija Hits for regional equity

3. **Temporal Patterns**
   - "New Afrobeats" vs established playlists
   - Release year distribution in editorial vs independent

4. **Statistical Robustness**
   - Larger sample size (19 vs 13 playlists)
   - More curator type categories for Chi-Square tests
   - Better representation of Spotify's ecosystem

## Next Steps

1. **Backup current data:**
   ```powershell
   Copy-Item "data\playlist_config.json" "data\playlist_config_backup.json"
   ```

2. **Update configuration:**
   ```powershell
   Copy-Item "data\playlist_config_updated.json" "data\playlist_config.json"
   ```

3. **Fetch new data:**
   ```powershell
   python scripts\fetch_spotify_data.py
   ```

4. **Update artist metadata:**
   ```powershell
   python scripts\update_artist_metadata.py
   python scripts\apply_artist_metadata.py
   ```

5. **Regenerate dashboards:**
   ```powershell
   python scripts\dashboard.py
   ```

## Expected Data Growth

- **Current:** 1,138 tracks, 426 artists, 13 playlists
- **Estimated after:** ~1,800-2,200 tracks, ~500-600 artists, 19 playlists

## Research Questions Enhanced

### RQ1: Regional Representation
- **Before:** General regional bias analysis
- **After:** Compare editorial vs independent curator regional preferences

### RQ2: Sonic Homogenization  
- **Before:** Overall audio feature patterns
- **After:** Compare diversity in editorial vs independent playlists

### RQ3: Curator Type Impact
- **Before:** 4 curator types
- **After:** 5 curator types with Spotify Editorial as key institutional player

### RQ4: Temporal Gatekeeping
- **Before:** Limited temporal analysis
- **After:** "New Afrobeats" vs established playlists comparison

## Files Created

1. `data/playlist_config_updated.json` - Ready to use configuration
2. `SPOTIFY_EDITORIAL_PLAYLISTS.md` - Full research notes
3. This summary document

## Recommendation

**Add all 6 Spotify Editorial playlists** to strengthen your dissertation's analysis of institutional gatekeeping in the Afrobeats ecosystem. The editorial playlists represent Spotify's direct curatorial power and will provide critical comparison points for your existing independent/media publisher data.
