import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

DEFAULT_FLOWERS = [
    {
        "id": 1,
        "name": "Azure Briar Rose",
        "character_theme": "Charlotte Roselei (Blue Rose)",
        "riddle": "Where weary students quench their thirst with crystal drops of cool water.",
        "location_hint": "Main Water Cooler / Fountain Station",
        "passcode": "BRIAR-01",
        "points": 100,
        "color": "#4285F4"  # Google Blue
    },
    {
        "id": 2,
        "name": "Crimson Flame Dahlia",
        "character_theme": "Fuegoleon Vermillion (Crimson Lion)",
        "riddle": "Surrounded by beakers, flasks, and reactions that burn bright with experimental fire.",
        "location_hint": "Science / Chemistry Lab Hallway",
        "passcode": "FLAME-02",
        "points": 100,
        "color": "#EA4335"  # Google Red
    },
    {
        "id": 3,
        "name": "Verdant Mantis Blossom",
        "character_theme": "Jack the Ripper (Green Mantis)",
        "riddle": "Where fresh grass sways and sunlight pierces through the leaves in the open air.",
        "location_hint": "School Courtyard / Botanical Garden",
        "passcode": "SLASH-03",
        "points": 100,
        "color": "#34A853"  # Google Green
    },
    {
        "id": 4,
        "name": "Golden Dawn Sunflower",
        "character_theme": "William Vangeance & Yuno (Golden Dawn)",
        "riddle": "At the grand threshold where voices amplify and leaders take the stage.",
        "location_hint": "Main Auditorium / Amphitheater Stage",
        "passcode": "SOLAR-04",
        "points": 100,
        "color": "#FBBC05"  # Google Yellow
    },
    {
        "id": 5,
        "name": "Anti-Magic Black Lotus",
        "character_theme": "Asta (Black Bulls)",
        "riddle": "Hidden in the deep shadow beneath the stone steps that carry students upward.",
        "location_hint": "Under the Central Staircase (Ground Floor)",
        "passcode": "ASTA-05",
        "points": 150,
        "color": "#202124"  # Black Bulls Charcoal / Red Accent
    },
    {
        "id": 6,
        "name": "Silver Mercury Lily",
        "character_theme": "Nozel Silva (Silver Eagles)",
        "riddle": "Look into the reflective surface where students check their uniforms and medals.",
        "location_hint": "Trophy Showcase / Mirror Corridor",
        "passcode": "SILVR-06",
        "points": 100,
        "color": "#9AA0A6"  # Silver / Ice Blue
    },
    {
        "id": 7,
        "name": "Wizard King's Chrono Violet",
        "character_theme": "Julius Novachrono (Wizard King)",
        "riddle": "Time waits for no Magic Knight. Seek where the ticking hands measure every second.",
        "location_hint": "The Grand Wall Clock in Central Hall",
        "passcode": "CHRONO-07",
        "points": 120,
        "color": "#4285F4"  # Google Blue
    },
    {
        "id": 8,
        "name": "Thunderstrike Orchid",
        "character_theme": "Luck Voltia (Black Bulls)",
        "riddle": "Crackling with electric currents, where heavy cables hum and servers breathe.",
        "location_hint": "Computer Lab / Server Switch Box",
        "passcode": "SPARK-08",
        "points": 100,
        "color": "#FBBC05"  # Google Yellow
    },
    {
        "id": 9,
        "name": "Spatial Portal Camellia",
        "character_theme": "Finral Roulacase (Black Bulls)",
        "riddle": "The gateway between realms: where hundreds enter at sunrise and depart at twilight.",
        "location_hint": "Main Entrance Lobby / Turnstiles",
        "passcode": "PORTL-09",
        "points": 100,
        "color": "#34A853"  # Google Green
    },
    {
        "id": 10,
        "name": "Wind Spirit Sylph Blossom",
        "character_theme": "Sylph & Yuno (Golden Dawn)",
        "riddle": "Where the highest wind whispers through open glass overlooking the entire school.",
        "location_hint": "Top Floor Terrace / High Window Bay",
        "passcode": "SYLPH-10",
        "points": 120,
        "color": "#34A853"  # Google Green
    },
    {
        "id": 11,
        "name": "Forbidden Archive Lotus",
        "character_theme": "Zagred / Shadow Palace",
        "riddle": "Where ancient wisdom rests undisturbed on the lowest, quietest book stack.",
        "location_hint": "Library Back History / Archive Section",
        "passcode": "ARCHV-11",
        "points": 130,
        "color": "#EA4335"  # Google Red
    },
    {
        "id": 12,
        "name": "Mirror Magic Peony",
        "character_theme": "Gauche Adlai (Black Bulls)",
        "riddle": "Reflecting double the light beside the glass art boards and student sketches.",
        "location_hint": "Art Workshop / Gallery Display",
        "passcode": "MIRROR-12",
        "points": 100,
        "color": "#4285F4"  # Google Blue
    },
    {
        "id": 13,
        "name": "Cotton Sheep Blossom",
        "character_theme": "Charmy Pappitson (Black Bulls)",
        "riddle": "Follow the sweet scent of fresh pastries, warm tea, and delicious meals.",
        "location_hint": "School Cafeteria / Canteen Snack Counter",
        "passcode": "CHARMY-13",
        "points": 100,
        "color": "#FBBC05"  # Google Yellow
    },
    {
        "id": 14,
        "name": "Sealing Swallowtail Blossom",
        "character_theme": "Nero / Secre Swallowtail",
        "riddle": "Perched like an observant bird right beside the front reception and keys.",
        "location_hint": "Administration Desk / Reception Area",
        "passcode": "SEAL-14",
        "points": 110,
        "color": "#202124"  # Charcoal Black
    },
    {
        "id": 15,
        "name": "Dark Cloaked Nightshade",
        "character_theme": "Yami Sukehiro (Captain Black Bulls)",
        "riddle": "'Surpass your limits!' Located near the teachers' strong coffee brew machine.",
        "location_hint": "Teachers Lounge / Staff Coffee Point",
        "passcode": "YAMI-15",
        "points": 150,
        "color": "#EA4335"  # Google Red
    },
    {
        "id": 16,
        "name": "Valiant Valkyrie Iris",
        "character_theme": "Noelle Silva (Black Bulls)",
        "riddle": "Guarded by pure water mana, near the emergency wash fountain in the hallway.",
        "location_hint": "Hallway Safety Wash Station",
        "passcode": "VALK-16",
        "points": 100,
        "color": "#4285F4"  # Google Blue
    },
    {
        "id": 17,
        "name": "Dream World Marigold",
        "character_theme": "Dorothy Unsworth (Coral Peacock)",
        "riddle": "A peaceful sanctuary of soft beds and silence where sick students rest their eyes.",
        "location_hint": "School Infirmary / Medical Room Doorway",
        "passcode": "DREAM-17",
        "points": 100,
        "color": "#FBBC05"  # Google Yellow
    },
    {
        "id": 18,
        "name": "Paint Magic Cosmos",
        "character_theme": "Rill Boismortier (Aqua Deer)",
        "riddle": "Surrounded by colorful announcements, club posters, and creative student flyers.",
        "location_hint": "Student Central Notice Board",
        "passcode": "COLOR-18",
        "points": 100,
        "color": "#34A853"  # Google Green
    },
    {
        "id": 19,
        "name": "Replication Narcissus",
        "character_theme": "Rhya (Third Eye)",
        "riddle": "Where thousands of identical exam papers and test sheets are printed each morning.",
        "location_hint": "School Printing / Copy Room",
        "passcode": "CLONE-19",
        "points": 110,
        "color": "#9AA0A6"  # Silver Gray
    },
    {
        "id": 20,
        "name": "The 5-Leaf Clover Demon Blossom",
        "character_theme": "The Legendary Grimoire (GDG Special)",
        "riddle": "Inside the 5th leaf resides immense developer power! Found at the GDG Headquarters booth!",
        "location_hint": "GDG Official Welcome Booth / Info Desk",
        "passcode": "GDG-DEVIL-20",
        "points": 250,
        "color": "#EA4335"  # Special Multi-color / Google Red
    }
]

DEFAULT_SQUADS = [
    {
        "name": "Black Bulls Devs",
        "captain": "Asta El-Khatib",
        "color": "google-yellow",
        "motto": "Surpass your limits! Right here, right now with Google Code!",
        "members": ["Asta El-Khatib", "Noelle S.", "Finral R.", "Luck V."]
    },
    {
        "name": "Golden Dawn Squad",
        "captain": "Yuno Benali",
        "color": "google-blue",
        "motto": "The elite prodigies of cloud and algorithms.",
        "members": ["Yuno Benali", "Klaus L.", "Mimosa V."]
    },
    {
        "name": "Crimson Lion Coders",
        "captain": "Fuegoleon Mansouri",
        "color": "google-red",
        "motto": "Burning passion for innovation and open source!",
        "members": ["Fuegoleon Mansouri", "Mereoleona M.", "Leopold M."]
    },
    {
        "name": "Green Mantis Hackers",
        "captain": "Jack Larbi",
        "color": "google-green",
        "motto": "Slicing through bugs with razor precision.",
        "members": ["Jack Larbi", "Sekke B.", "En Ringard"]
    }
]

def get_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured. Set it to your Supabase PostgreSQL connection string.")
    return psycopg.connect(DATABASE_URL, sslmode='require', row_factory=dict_row)

def init_db(seed_sample_data=True):
    conn = get_db()
    cursor = conn.cursor()

    # Seed flowers if empty
    cursor.execute('SELECT COUNT(*) FROM flowers')
    if cursor.fetchone()['count'] == 0:
        for f in DEFAULT_FLOWERS:
            cursor.execute('''
            INSERT INTO flowers (id, name, character_theme, riddle, location_hint, passcode, points, color)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (f['id'], f['name'], f['character_theme'], f['riddle'], f['location_hint'], f['passcode'], f['points'], f['color']))
        
        cursor.execute('''
        INSERT INTO activity_log (event_type, description)
        VALUES ('SYSTEM', 'Initialized 20 Black Clover Mana Flowers for GDG Open Day')
        ''')

    # Seed sample squads if requested and table empty
    if seed_sample_data:
        cursor.execute('SELECT COUNT(*) FROM squads')
        if cursor.fetchone()['count'] == 0:
            seeded_squad_ids = []
            for s in DEFAULT_SQUADS:
                cursor.execute('''
                INSERT INTO squads (name, captain, color, motto)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                ''', (s['name'], s['captain'], s['color'], s['motto']))
                squad_id = cursor.fetchone()['id']
                seeded_squad_ids.append(squad_id)
                for idx, m in enumerate(s['members']):
                    role = 'Captain' if idx == 0 else ('Vice-Captain' if idx == 1 else 'Magic Knight')
                    cursor.execute('''
                    INSERT INTO members (squad_id, name, role)
                    VALUES (%s, %s, %s)
                    ''', (squad_id, m, role))

            demo_claims = (
                (seeded_squad_ids[0], 1, 'Asta El-Khatib'),
                (seeded_squad_ids[0], 5, 'Asta El-Khatib'),
                (seeded_squad_ids[1], 4, 'Yuno Benali'),
                (seeded_squad_ids[2], 2, 'Fuegoleon Mansouri'),
            )
            for squad_id, flower_id, claimed_by in demo_claims:
                cursor.execute('SELECT id FROM flowers WHERE id = %s', (flower_id,))
                if cursor.fetchone():
                    cursor.execute('''
                    INSERT INTO claims (squad_id, flower_id, claimed_by)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (squad_id, flower_id) DO NOTHING
                    ''', (squad_id, flower_id, claimed_by))

            cursor.execute('''
            INSERT INTO activity_log (event_type, description)
            VALUES ('SYSTEM', 'Seeded initial GDG Magic Knight squads for exhibition demo')
            ''')

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    init_db(seed_sample_data=True)
    print("Supabase database initialized successfully.")
