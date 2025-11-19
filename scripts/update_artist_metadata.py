"""
Update artist metadata CSV with country and region information
from Spotify API and manual research
"""
import json
import csv
import os
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
))

# Manual overrides for artists with known countries based on research
MANUAL_ARTIST_DATA = {
    # === International Artists (USA) ===
    "Chris Brown": {"country": "United States", "region": "North America", "diaspora": False},
    "Ty Dolla $ign": {"country": "United States", "region": "North America", "diaspora": False},
    "Travis Scott": {"country": "United States", "region": "North America", "diaspora": False},
    "J. Cole": {"country": "United States", "region": "North America", "diaspora": False},
    "Lil Wayne": {"country": "United States", "region": "North America", "diaspora": False},
    "Nicki Minaj": {"country": "United States", "region": "North America", "diaspora": False},
    "H.E.R.": {"country": "United States", "region": "North America", "diaspora": False},
    "GIVĒON": {"country": "United States", "region": "North America", "diaspora": False},
    "Jacquees": {"country": "United States", "region": "North America", "diaspora": False},
    "Jeremih": {"country": "United States", "region": "North America", "diaspora": False},
    "Lucky Daye": {"country": "United States", "region": "North America", "diaspora": False},
    "Masego": {"country": "United States", "region": "North America", "diaspora": False},
    "Victoria Monét": {"country": "United States", "region": "North America", "diaspora": False},
    "Sexyy Red": {"country": "United States", "region": "North America", "diaspora": False},
    "Dess Dior": {"country": "United States", "region": "North America", "diaspora": False},
    "Chlöe": {"country": "United States", "region": "North America", "diaspora": False},
    "Justin Bieber": {"country": "United States", "region": "North America", "diaspora": False},
    "Selena Gomez": {"country": "United States", "region": "North America", "diaspora": False},
    "Jason Derulo": {"country": "United States", "region": "North America", "diaspora": False},
    "Kelly Rowland": {"country": "United States", "region": "North America", "diaspora": False},
    
    # === US Diaspora (African heritage) ===
    "Wale": {"country": "United States", "region": "North America", "diaspora": True},
    "Rotimi": {"country": "United States", "region": "North America", "diaspora": True},
    "Jidenna": {"country": "United States", "region": "North America", "diaspora": True},
    
    # === UK Artists ===
    "Ed Sheeran": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": False},
    "Stormzy": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": False},
    "RAYE": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": False},
    
    # === UK Diaspora (African/Caribbean heritage) ===
    "Skepta": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "J Hus": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Central Cee": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Dave": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Not3s": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Maleek Berry": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Headie One": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Tion Wayne": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "One Acen": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    
    # === France & French Diaspora ===
    "Alonzo": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Abou Debeing": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Niska": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Koba LaD": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Tiakola": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Gisèle": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Guy2Bezbar": {"country": "France", "region": "Western Europe", "diaspora": True},
    "RK": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Stromae": {"country": "Belgium", "region": "Western Europe", "diaspora": True},
    "Dany Synthé": {"country": "France", "region": "Western Europe", "diaspora": True},
    "DODDY": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Imen Es": {"country": "France", "region": "Western Europe", "diaspora": True},
    
    # === Morocco & North Africa ===
    "DYSTINCT": {"country": "Morocco", "region": "North Africa", "diaspora": False},
    
    # === Caribbean (Jamaica) ===
    "Damian Marley": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    "Vybz Kartel": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    "Konshens": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    "Kranium": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    "Skillibeng": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    "Sean Paul": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    "Spice": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    "Serani": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    "ZJ Liquid": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    "Anju Blaxx": {"country": "Jamaica", "region": "Caribbean", "diaspora": False},
    
    # === Haiti ===
    "Mack H.D": {"country": "Haiti/USA", "region": "North America", "diaspora": True},
    
    # === Latin America ===
    "Ozuna": {"country": "Puerto Rico", "region": "Caribbean", "diaspora": False},
    "Rauw Alejandro": {"country": "Puerto Rico", "region": "Caribbean", "diaspora": False},
    "Anitta": {"country": "Brazil", "region": "South America", "diaspora": False},
    "LUDMILLA": {"country": "Brazil", "region": "South America", "diaspora": False},
    
    # === India ===
    "Shreya Ghoshal": {"country": "India", "region": "South Asia", "diaspora": False},
    "Jacqueline Fernandez": {"country": "India", "region": "South Asia", "diaspora": False},
    "Rajat Nagpal": {"country": "India", "region": "South Asia", "diaspora": False},
    "Nora Fatehi": {"country": "Canada", "region": "North America", "diaspora": True},  # Moroccan-Canadian
    
    # === Benin ===
    "Angelique Kidjo": {"country": "Benin", "region": "West Africa", "diaspora": False},
    
    # === Italy ===
    "Rondodasosa": {"country": "Italy", "region": "Southern Europe", "diaspora": True},
    
    # === Tanzania ===
    "Diamond Platnumz": {"country": "Tanzania", "region": "East Africa", "diaspora": False},
    "Rayvanny": {"country": "Tanzania", "region": "East Africa", "diaspora": False},
    
    # === South Africa ===
    "Master KG": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Blxckie": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Brenden Praise": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Ceeka RSA": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Ch'cco": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Da Muziqal Chef": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Djy Biza": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Kabelo Sings": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "LeeMcKrazy": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Musa Keys": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Muzi": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Naledi Aphiwe": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Nandipha808": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Pcee": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Scotts Maphuma": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Semi Tee": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Sir Trill": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Sje Konka": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Tony Duardo": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Young Stunna": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Zee Nxumalo": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Sino Msolo": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Tebogo G Mashego": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Tumelo_za": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "MphoEL": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Mashudu": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Bianca Hester": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    
    # === Ghana ===
    "Medikal": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    "Stonebwoy": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    "Shatta Wale": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    "Black Sherif": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    "King Promise": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    "Sarkodie": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    "Ama Nova": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    
    # === Madagascar ===
    "Taylor Gasy": {"country": "Madagascar", "region": "East Africa", "diaspora": False},
    
    # === Canada ===
    "Shay Lia": {"country": "Canada", "region": "North America", "diaspora": True},
    
    # === Nigeria - Established Artists ===
    "234sagi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "2bigg": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Al Mubaraq": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "BadBoy Vinci": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "CEEXZA OLOWO": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Craig Isto": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "DJ Rymzy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Dwillsharmony": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Elinala": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "ErusMa": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "GhostwriterMel": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "HEISFARA": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "JEMIYO": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "JO3ZY": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Jolá": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "KODP": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kahren": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kris-Karz": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Lastnght Shy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Mahriisah": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Meemah Jackson": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Melinda Njoku": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ononi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ophi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Prinny": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Rayvnn": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Recon PRD": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Spray Zee": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "TERIRO": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "TRILOGY": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Toye Aru": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Vibes SZN": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "funkcleff": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kel-P": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "T.I BLAZE": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "prodbyneck": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    
    # === Nigeria - Additional from Missing List ===
    "250Sauce": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "ANIJAMZ": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "AX'EL": {"country": "Cameroon", "region": "Central Africa", "diaspora": False},
    "Badman Chorus": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Badmanprezzy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Bala": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "BhadBoi OML": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Bloody Civilian": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Boy Spyce": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "CHUMA": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Chief Dr. Sikiru Ayinde Barrister (MFR)": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "CowBoii": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "DaBlixx Osha": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Daecolm": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Damzee": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Dapsy Ade": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Eemoh": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ego Slimflow": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Evelle": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Fistosvalley": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Flawless": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Flourishways": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "FreAze": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Friyie": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Fxrtune": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Gabzy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Gmix": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Gubziin": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Haile": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Jaethevert": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Jamall Ray": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Jayneziss": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "JujuTheB": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Juno": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kagedimes": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kashcoming": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Keziah": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kidashine": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kuraye": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kwamzy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Leehard": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Lorda": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Lossa": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Love Star": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Lysense Slim": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Madumane": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "Malachiii": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Malemon": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Masta T": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Masterkraft": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Merveille": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Mikun": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Mmzy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Mohzix": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Mooseylion": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Morris Babyface": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Niniola": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Nonso Amadi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Oga Silachi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ohene Parker": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Portable": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Rahman Jago": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Richie Benson": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "SadBoyPineapple": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Savage": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Seun Kuti": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Seun1401": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Shaker": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Sheenworks": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Shine TTW": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Silent Addy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Simi Liadi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Skaame": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Snatcha": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Soundslucid": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Stelair": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Stryv": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Styl-Plus": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Successful O5": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Supa Gaeta": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Suprano C": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Swashii": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Tango Supreme": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Tempoe": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Tension": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Terry Apala": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Terry G": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Timzy Lamar": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Tyrone Dee": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "UGENE NGHT": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Valentino Rose": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Van Gee": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Victor Grand": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Wande Coal": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Xauce": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Xduppy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Young Bone": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Yuppe": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "oluu.": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "taves": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "zzamar": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    
    # === Producers & DJs ===
    "DJ Aka-m": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "DJ Guti BPM": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "DJ Rosco": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Dj 4kerty": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Dj Lux": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Dj Reckline": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Dj Yo!": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Emxbeatz": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "GL_Ceejay": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Lekaa Beats": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "NuelMiuzik": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Rocky vibes": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Vj Alkane": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Snapback08": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "TripleDose Production": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Trippynova": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Tvdz": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Take A Daytrip": {"country": "United States", "region": "North America", "diaspora": False},
    "Keinemusik": {"country": "Germany", "region": "Western Europe", "diaspora": False},
    "MADEINPARRIS": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Major Lazer": {"country": "United States", "region": "North America", "diaspora": False},
    "The FaNaTiX": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    
    # === Collective/Group Artists ===
    "AFROCHILL": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Afrisounds": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ancestral Rituals": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "bees & honey": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Cafe De Anatolia": {"country": "Turkey", "region": "Middle East", "diaspora": False},
    "Loud Urban Choir": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "UBA Choir": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "G & Machines": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    
    # === Additional Artists ===
    "BIGKHALID": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "BMS": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Brown Bread": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "CM CLIPZ": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Chanelle Tru": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Chaszr": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "DTG": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "DUTCHMAN": {"country": "Netherlands", "region": "Western Europe", "diaspora": True},
    "Dash Villz": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Derrick UGC": {"country": "Uganda", "region": "East Africa", "diaspora": False},
    "EHIDIAMHEN": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Elana Dara": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Emma'a": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Enrge": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Eyo-E": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Francoise Sanders": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "General Splash": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ghetto Boy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "IJULU": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "JR": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "JR Player": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Jamie Lancaster": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": False},
    "Jess ETA": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "KLN": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kalash": {"country": "Martinique", "region": "Caribbean", "diaspora": False},
    "KaliHi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kyla": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "LUNNAGRAM": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Lindsey": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Morrelo": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Night Myl": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Nú": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Orso": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "P.T.A": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Pokaface": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Prince Swanny": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Rage": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ranger": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ras Bohya": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "S.N.E": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "SPIKES": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ta liebe": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Theomaa": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "TiZ EAST": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "UNVRS": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "YG Marley": {"country": "United States", "region": "North America", "diaspora": True},  # Bob Marley's grandson
    "Zigala": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    
    # Existing artists from previous dataset
    "Maleek Berry": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},  # UK-based Nigerian producer
    "234sagi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "2bigg": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Al Mubaraq": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ama Nova": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    "BadBoy Vinci": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Bianca Hester": {"country": "South Africa", "region": "Southern Africa", "diaspora": False},
    "CEEXZA OLOWO": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Craig Isto": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "DJ Rymzy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Dwillsharmony": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Elinala": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "ErusMa": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "GhostwriterMel": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Gisèle": {"country": "France", "region": "Western Europe", "diaspora": True},
    "HEISFARA": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "JEMIYO": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "JO3ZY": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Jolá": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "KODP": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kahren": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kris-Karz": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Lastnght Shy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Mahriisah": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Meemah Jackson": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Melinda Njoku": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ononi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ophi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Prinny": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Rayvnn": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Recon PRD": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Spray Zee": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "TERIRO": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "TRILOGY": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Taylor Gasy": {"country": "Madagascar", "region": "East Africa", "diaspora": False},
    "Toye Aru": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Vibes SZN": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "funkcleff": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    
    # Producers
    "Kel-P": {"country": "Nigeria", "region": "West Africa", "diaspora": False},  # Nigerian producer
    "T.I BLAZE": {"country": "Nigeria", "region": "West Africa", "diaspora": False},  # Nigerian artist
    "prodbyneck": {"country": "Nigeria", "region": "West Africa", "diaspora": False},  # Nigerian producer
    
    # UK-based artists
    "Central Cee": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "J Hus": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Skepta": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Dave": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Not3s": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    
    # US-based artists
    "Rotimi": {"country": "United States", "region": "North America", "diaspora": True},
    "Jidenna": {"country": "United States", "region": "North America", "diaspora": True},
    "Wale": {"country": "United States", "region": "North America", "diaspora": True},
    
    # Canadian artists
    "Shay Lia": {"country": "Canada", "region": "North America", "diaspora": True},
    
    # French artists
    "Niska": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Koba LaD": {"country": "France", "region": "Western Europe", "diaspora": True},
    "Tiakola": {"country": "France", "region": "Western Europe", "diaspora": True},
    
    # Nigerian artists (based on typical naming and research)
    "6uff": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ajebo Hustlers": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Akiniz": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ashidapo": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ba6luv": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Becini": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Bella Alubo": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Big Lans": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Blak Diamon": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "BOI GEORGE": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Brown Joel": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ceeprince": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "DRAYY": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Driiper": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Eastsideindian": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Emali": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "HIGH M": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "JB Diamondz": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Judy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kammy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Kliffie": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "LC Trapper": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Leo B": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Lerical Jackpal": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Mariobe": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "MeJosh": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Morgan": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Papi Azed": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "PROJECT": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Q2 BORNSTAR": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Ragga": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Regal Imperial": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Shanky Grey": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Shegzsmiles": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "SmartBeatz": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Stunnermusic": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "StUreets": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Succzz": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Supa Boy": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Sweep": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Swypar": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "The Show": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Tru Star": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Wiznelson": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Y3NKO140": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "Yomzi": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "ZeD1ST": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    "A.TEE": {"country": "Nigeria", "region": "West Africa", "diaspora": False},
    
    # Ghanaian artists
    "Culture Rock": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    "BM Casso": {"country": "Ghana", "region": "West Africa", "diaspora": False},
    
    # Jamaican artists
    "1ne Portal": {"country": "Jamaica", "region": "Caribbean", "diaspora": True},
    
    # French producer/DJ
    "Bob Sinclar": {"country": "France", "region": "Western Europe", "diaspora": False},
    
    # UK artists
    "Blaise": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    "Black Mattic": {"country": "United Kingdom", "region": "Northern Europe", "diaspora": True},
    
    # International collaboration
    "Together for Dawit": {"country": "Ethiopia", "region": "East Africa", "diaspora": False},
}

def load_existing_csv(csv_path):
    """Load existing artist metadata CSV"""
    artists = {}
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                artists[row['artist']] = row
    return artists

def load_missing_artists(json_path):
    """Load list of missing artists from processed JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('runMetadata', {}).get('missingArtists', [])

def get_artist_info_from_tracks(json_path):
    """Extract artist info from track data in JSON"""
    artist_map = {}
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for playlist in data.get('playlists', []):
        for track in playlist.get('tracks', []):
            artist_name = track.get('artist', '').split(',')[0].strip()
            if artist_name and artist_name not in artist_map:
                artist_map[artist_name] = {
                    'artistId': track.get('artistId'),
                    'artistCountry': track.get('artistCountry'),
                    'regionGroup': track.get('regionGroup'),
                    'diaspora': track.get('diaspora', False)
                }
    return artist_map

def update_artist_metadata():
    """Main function to update artist metadata"""
    base_path = Path(__file__).parent.parent
    csv_path = base_path / 'data' / 'data' / 'artist_metadata.csv'
    json_path = base_path / 'data' / 'processed' / 'afrobeats_playlists.json'
    
    print("📊 Loading existing artist metadata...")
    existing_artists = load_existing_csv(csv_path)
    print(f"   Found {len(existing_artists)} existing artists")
    
    print("\n🔍 Loading missing artists from JSON...")
    missing_artists = load_missing_artists(json_path)
    print(f"   Found {len(missing_artists)} missing artists")
    
    print("\n🎵 Extracting artist info from track data...")
    track_artist_info = get_artist_info_from_tracks(json_path)
    
    # Count unknowns
    unknown_count = sum(1 for a in existing_artists.values() 
                       if a.get('artistCountry') == 'Unknown')
    print(f"   Found {unknown_count} artists with Unknown country/region")
    
    updates_made = 0
    new_additions = 0
    
    # Update Unknown artists with manual data
    print("\n🔄 Updating artists with Unknown metadata...")
    for artist_name, data in existing_artists.items():
        if data.get('artistCountry') == 'Unknown' and artist_name in MANUAL_ARTIST_DATA:
            manual_data = MANUAL_ARTIST_DATA[artist_name]
            data['artistCountry'] = manual_data['country']
            data['regionGroup'] = manual_data['region']
            data['diaspora'] = str(manual_data['diaspora']).upper()
            updates_made += 1
            print(f"   ✓ Updated {artist_name}: {manual_data['country']}, {manual_data['region']}")
    
    # Add missing artists
    print(f"\n➕ Adding {len(missing_artists)} missing artists...")
    for artist_name in missing_artists:
        if artist_name not in existing_artists:
            # Check if we have manual data
            if artist_name in MANUAL_ARTIST_DATA:
                manual_data = MANUAL_ARTIST_DATA[artist_name]
                existing_artists[artist_name] = {
                    'artist': artist_name,
                    'artistCountry': manual_data['country'],
                    'regionGroup': manual_data['region'],
                    'diaspora': str(manual_data['diaspora']).upper()
                }
                new_additions += 1
                print(f"   ✓ Added {artist_name}: {manual_data['country']}, {manual_data['region']}")
            # Check if we have it from track data
            elif artist_name in track_artist_info:
                track_data = track_artist_info[artist_name]
                if track_data.get('artistCountry') and track_data['artistCountry'] != 'Unknown':
                    existing_artists[artist_name] = {
                        'artist': artist_name,
                        'artistCountry': track_data['artistCountry'],
                        'regionGroup': track_data['regionGroup'],
                        'diaspora': str(track_data.get('diaspora', False)).upper()
                    }
                    new_additions += 1
                    print(f"   ✓ Added {artist_name} from track data: {track_data['artistCountry']}")
                else:
                    # Add as Unknown for now
                    existing_artists[artist_name] = {
                        'artist': artist_name,
                        'artistCountry': 'Unknown',
                        'regionGroup': 'Unknown',
                        'diaspora': 'FALSE'
                    }
                    new_additions += 1
                    print(f"   ⚠ Added {artist_name}: No metadata available")
    
    # Write updated CSV
    print(f"\n💾 Writing updated CSV...")
    sorted_artists = sorted(existing_artists.values(), key=lambda x: x['artist'])
    
    # Write to a new file first (in case original is open)
    csv_new_path = csv_path.parent / 'artist_metadata_updated.csv'
    
    with open(csv_new_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['artist', 'artistCountry', 'regionGroup', 'diaspora']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_artists)
    
    print(f"   💾 Saved to: {csv_new_path}")
    print(f"   ℹ️  Please close the original CSV if open, then rename this file.")
    
    print(f"\n✅ Update complete!")
    print(f"   • Total artists in CSV: {len(existing_artists)}")
    print(f"   • Artists updated: {updates_made}")
    print(f"   • New artists added: {new_additions}")
    
    # Count remaining unknowns
    remaining_unknown = sum(1 for a in existing_artists.values() 
                           if a.get('artistCountry') == 'Unknown')
    print(f"   • Remaining Unknown: {remaining_unknown}")
    
    return existing_artists

if __name__ == "__main__":
    update_artist_metadata()
