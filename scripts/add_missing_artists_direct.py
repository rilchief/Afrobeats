"""
Directly add the 262 missing artists to the artist_metadata.csv
"""
import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = REPO_ROOT / "data" / "data" / "artist_metadata.csv"

# All 262 missing artists with metadata from manual research
NEW_ARTISTS = {
    # === International Artists (USA) ===
    "Chris Brown": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Ty Dolla $ign": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Travis Scott": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "J. Cole": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Lil Wayne": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Nicki Minaj": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "H.E.R.": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "GIVĒON": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Jacquees": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Jeremih": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Lucky Daye": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Masego": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Victoria Monét": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Sexyy Red": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Dess Dior": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Chlöe": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Justin Bieber": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Selena Gomez": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Jason Derulo": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Kelly Rowland": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    
    # === US Diaspora ===
    "Wale": {"country": "United States", "region": "North America", "diaspora": "TRUE"},
    "YG Marley": {"country": "United States", "region": "North America", "diaspora": "TRUE"},
    
    # === UK Artists ===
    "Ed Sheeran": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": "FALSE"},
    "Stormzy": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": "FALSE"},
    "RAYE": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": "FALSE"},
    "Jamie Lancaster": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": "FALSE"},
    
    # === UK Diaspora ===
    "Headie One": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": "TRUE"},
    "Tion Wayne": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": "TRUE"},
    "One Acen": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": "TRUE"},
    "The FaNaTiX": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": "TRUE"},
    
    # === France & Diaspora ===
    "Alonzo": {"country": "France", "region": "Western Europe", "diaspora": "TRUE"},
    "Abou Debeing": {"country": "France", "region": "Western Europe", "diaspora": "TRUE"},
    "Guy2Bezbar": {"country": "France", "region": "Western Europe", "diaspora": "TRUE"},
    "RK": {"country": "France", "region": "Western Europe", "diaspora": "TRUE"},
    "Dany Synthé": {"country": "France", "region": "Western Europe", "diaspora": "TRUE"},
    "DODDY": {"country": "France", "region": "Western Europe", "diaspora": "TRUE"},
    "Imen Es": {"country": "France", "region": "Western Europe", "diaspora": "TRUE"},
    "MADEINPARRIS": {"country": "France", "region": "Western Europe", "diaspora": "TRUE"},
    
    # === Belgium ===
    "Stromae": {"country": "Belgium", "region": "Western Europe", "diaspora": "TRUE"},
    
    # === Netherlands ===
    "DUTCHMAN": {"country": "Netherlands", "region": "Western Europe", "diaspora": "TRUE"},
    
    # === Germany ===
    "Keinemusik": {"country": "Germany", "region": "Western Europe", "diaspora": "FALSE"},
    
    # === Italy ===
    "Rondodasosa": {"country": "Italy", "region": "Southern Europe", "diaspora": "TRUE"},
    
    # === Morocco ===
    "DYSTINCT": {"country": "Morocco", "region": "North Africa", "diaspora": "FALSE"},
    
    # === Jamaica ===
    "Damian Marley": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    "Vybz Kartel": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    "Konshens": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    "Kranium": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    "Skillibeng": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    "Sean Paul": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    "Spice": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    "Serani": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    "ZJ Liquid": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    "Anju Blaxx": {"country": "Jamaica", "region": "Caribbean", "diaspora": "FALSE"},
    
    # === Puerto Rico ===
    "Ozuna": {"country": "Puerto Rico", "region": "Caribbean", "diaspora": "FALSE"},
    "Rauw Alejandro": {"country": "Puerto Rico", "region": "Caribbean", "diaspora": "FALSE"},
    
    # === Martinique ===
    "Kalash": {"country": "Martinique", "region": "Caribbean", "diaspora": "FALSE"},
    
    # === Brazil ===
    "Anitta": {"country": "Brazil", "region": "South America", "diaspora": "FALSE"},
    "LUDMILLA": {"country": "Brazil", "region": "South America", "diaspora": "FALSE"},
    
    # === India ===
    "Shreya Ghoshal": {"country": "India", "region": "South Asia", "diaspora": "FALSE"},
    "Jacqueline Fernandez": {"country": "India", "region": "South Asia", "diaspora": "FALSE"},
    "Rajat Nagpal": {"country": "India", "region": "South Asia", "diaspora": "FALSE"},
    
    # === Canada ===
    "Nora Fatehi": {"country": "Canada", "region": "North America", "diaspora": "TRUE"},
    
    # === Turkey ===
    "Cafe De Anatolia": {"country": "Turkey", "region": "Middle East", "diaspora": "FALSE"},
    
    # === Benin ===
    "Angelique Kidjo": {"country": "Benin", "region": "West Africa", "diaspora": "FALSE"},
    
    # === Cameroon ===
    "AX'EL": {"country": "Cameroon", "region": "Central Africa", "diaspora": "FALSE"},
    
    # === Uganda ===
    "Derrick UGC": {"country": "Uganda", "region": "East Africa", "diaspora": "FALSE"},
    
    # === Tanzania ===
    "Diamond Platnumz": {"country": "Tanzania", "region": "East Africa", "diaspora": "FALSE"},
    
    # === South Africa ===
    "Master KG": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Blxckie": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Brenden Praise": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Ceeka RSA": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Ch'cco": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Da Muziqal Chef": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Djy Biza": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Kabelo Sings": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "LeeMcKrazy": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Musa Keys": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Muzi": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Naledi Aphiwe": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Nandipha808": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Pcee": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Scotts Maphuma": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Semi Tee": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Sir Trill": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Sje Konka": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Tony Duardo": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Young Stunna": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Zee Nxumalo": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Sino Msolo": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Tebogo G Mashego": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Tumelo_za": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "MphoEL": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Mashudu": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Madumane": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    "Ancestral Rituals": {"country": "South Africa", "region": "Southern Africa", "diaspora": "FALSE"},
    
    # === Ghana ===
    "Medikal": {"country": "Ghana", "region": "West Africa", "diaspora": "FALSE"},
    
    # === Nigeria (remainder) ===
    "250Sauce": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "AFROCHILL": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "ANIJAMZ": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Afrisounds": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Alorman": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "BIGKHALID": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "BMS": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Badman Chorus": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Badmanprezzy": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Bala": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "BhadBoi OML": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Bloody Civilian": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Boy Spyce": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Brown Bread": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "CHUMA": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "CM CLIPZ": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Chanelle Tru": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Chaszr": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Chief Dr. Sikiru Ayinde Barrister (MFR)": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "CowBoii": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "DJ Aka-m": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "DJ Guti BPM": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "DJ Rosco": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "DTG": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "DaBlixx Osha": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Daecolm": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Damzee": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Dapsy Ade": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Dash Villz": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Dj 4kerty": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Dj Lux": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Dj Reckline": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Dj Yo!": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "EHIDIAMHEN": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Eemoh": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Ego Slimflow": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Elana Dara": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Emma'a": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Emxbeatz": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Enrge": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Evelle": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Eyo-E": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Fistosvalley": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Flawless": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Flourishways": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Francoise Sanders": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "FreAze": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Friyie": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Fxrtune": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "G & Machines": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "GL_Ceejay": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Gabzy": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "General Splash": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Ghetto Boy": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Gmix": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Gubziin": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Haile": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "IJULU": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "JR": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "JR Player": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Jaethevert": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Jamall Ray": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Jayneziss": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Jess ETA": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "JujuTheB": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Juno": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "KLN": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Kagedimes": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "KaliHi": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Kashcoming": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Keziah": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Kidashine": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Kuraye": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Kwamzy": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Kyla": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "LUNNAGRAM": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Leehard": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Lekaa Beats": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Lindsey": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Lorda": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Lossa": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Loud Urban Choir": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Love Star": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Lysense Slim": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Malachiii": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Malemon": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Masta T": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Masterkraft": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Merveille": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Mikun": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Mmzy": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Mohzix": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Mooseylion": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Morrelo": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Morris Babyface": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Night Myl": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Niniola": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Nonso Amadi": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "NuelMiuzik": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Nú": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Oga Silachi": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Ohene Parker": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Orso": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "P.T.A": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Pokaface": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Portable": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Prince Swanny": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Rage": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Rahman Jago": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Ranger": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Ras Bohya": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Richie Benson": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Rocky vibes": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "S.N.E": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "SPIKES": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "SadBoyPineapple": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Savage": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Seun Kuti": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Seun1401": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Shaker": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Sheenworks": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Shine TTW": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Silent Addy": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Simi Liadi": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Skaame": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Snapback08": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Snatcha": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Soundslucid": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Stelair": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Stryv": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Styl-Plus": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Successful O5": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Supa Gaeta": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Suprano C": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Swashii": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Ta liebe": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Take A Daytrip": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
    "Tango Supreme": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Tempoe": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Tension": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Terry Apala": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Terry G": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Theomaa": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "TiZ EAST": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Timzy Lamar": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "TripleDose Production": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Trippynova": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Tvdz": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Tyrone Dee": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "UBA Choir": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "UGENE NGHT": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "UNVRS": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Valentino Rose": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Van Gee": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Victor Grand": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Vj Alkane": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Wande Coal": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Xauce": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Xduppy": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Young Bone": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Yuppe": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Zigala": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "bees & honey": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "oluu.": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "taves": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "zzamar": {"country": "Nigeria", "region": "West Africa", "diaspora": "FALSE"},
    "Major Lazer": {"country": "United States", "region": "North America", "diaspora": "FALSE"},
}


def main():
    print("📊 Loading existing artist metadata...")
    existing_artists = {}
    
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_artists[row['artist']] = row
    
    print(f"   Found {len(existing_artists)} existing artists")
    
    # Filter out artists that already exist
    artists_to_add = {k: v for k, v in NEW_ARTISTS.items() if k not in existing_artists}
    
    print(f"\n➕ Adding {len(artists_to_add)} new artists...")
    
    # Add new artists to the dictionary
    for artist, data in artists_to_add.items():
        existing_artists[artist] = {
            'artist': artist,
            'artistCountry': data['country'],
            'regionGroup': data['region'],
            'diaspora': data['diaspora']
        }
    
    # Write updated CSV
    output_path = METADATA_PATH.parent / "artist_metadata_updated.csv"
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['artist', 'artistCountry', 'regionGroup', 'diaspora'])
        writer.writeheader()
        
        # Sort by artist name
        sorted_artists = sorted(existing_artists.values(), key=lambda x: x['artist'].lower())
        writer.writerows(sorted_artists)
    
    print(f"\n💾 Saved to: {output_path}")
    print(f"   Total artists: {len(existing_artists)}")
    print(f"   New artists added: {len(artists_to_add)}")
    print("\n✅ Complete! Please replace the original CSV with this updated version.")


if __name__ == "__main__":
    main()
