import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'v2_black_clover.db')

DEFAULT_FLOWERS = [
    {
        "id": 1,
        "name": "Azure Briar Rose",
        "character_theme": "Charlotte Roselei (Blue Rose)",
        "riddle": "Where weary students quench their thirst with crystal drops of cool water.",
        "location": "Main Water Cooler / Fountain Station",
        "points": 100,
        "color": "#4285F4"  # Google Blue
    },
    {
        "id": 2,
        "name": "Crimson Flame Dahlia",
        "character_theme": "Fuegoleon Vermillion (Crimson Lion)",
        "riddle": "Surrounded by beakers, flasks, and reactions that burn bright with experimental fire.",
        "location": "Science / Chemistry Lab Hallway",
        "points": 100,
        "color": "#EA4335"  # Google Red
    },
    {
        "id": 3,
        "name": "Verdant Mantis Blossom",
        "character_theme": "Jack the Ripper (Green Mantis)",
        "riddle": "Where fresh grass sways and sunlight pierces through the leaves in the open air.",
        "location": "School Courtyard / Botanical Garden",
        "points": 100,
        "color": "#34A853"  # Google Green
    },
    {
        "id": 4,
        "name": "Golden Dawn Sunflower",
        "character_theme": "William Vangeance & Yuno (Golden Dawn)",
        "riddle": "At the grand threshold where voices amplify and leaders take the stage.",
        "location": "Main Auditorium / Amphitheater Stage",
        "points": 100,
        "color": "#FBBC05"  # Google Yellow
    },
    {
        "id": 5,
        "name": "Anti-Magic Black Lotus",
        "character_theme": "Asta (Black Bulls)",
        "riddle": "Hidden in the deep shadow beneath the stone steps that carry students upward.",
        "location": "Under the Central Staircase (Ground Floor)",
        "points": 150,
        "color": "#202124"  # Black Bulls Dark / Gold
    },
    {
        "id": 6,
        "name": "Silver Mercury Lily",
        "character_theme": "Nozel Silva (Silver Eagles)",
        "riddle": "Look into the reflective surface where students check their uniforms and medals.",
        "location": "Trophy Showcase / Mirror Corridor",
        "points": 100,
        "color": "#9AA0A6"  # Silver / Ice Blue
    },
    {
        "id": 7,
        "name": "Wizard King Chrono Violet",
        "character_theme": "Julius Novachrono (Wizard King)",
        "riddle": "Time waits for no Magic Knight. Seek where the ticking hands measure every second.",
        "location": "The Grand Wall Clock in Central Hall",
        "points": 120,
        "color": "#4285F4"  # Google Blue
    },
    {
        "id": 8,
        "name": "Thunderstrike Orchid",
        "character_theme": "Luck Voltia (Black Bulls)",
        "riddle": "Crackling with electric currents, where heavy cables hum and servers breathe.",
        "location": "Computer Lab / Server Switch Box",
        "points": 100,
        "color": "#FBBC05"  # Google Yellow
    },
    {
        "id": 9,
        "name": "Spatial Portal Camellia",
        "character_theme": "Finral Roulacase (Black Bulls)",
        "riddle": "The gateway between realms: where hundreds enter at sunrise and depart at twilight.",
        "location": "Main Entrance Lobby / Turnstiles",
        "points": 100,
        "color": "#34A853"  # Google Green
    },
    {
        "id": 10,
        "name": "Wind Spirit Sylph Blossom",
        "character_theme": "Sylph & Yuno (Golden Dawn)",
        "riddle": "Where the highest wind whispers through open glass overlooking the entire school.",
        "location": "Top Floor Terrace / High Window Bay",
        "points": 120,
        "color": "#34A853"  # Google Green
    },
    {
        "id": 11,
        "name": "Forbidden Archive Lotus",
        "character_theme": "Zagred / Shadow Palace",
        "riddle": "Where ancient wisdom rests undisturbed on the lowest, quietest book stack.",
        "location": "Library Back History / Archive Section",
        "points": 130,
        "color": "#EA4335"  # Google Red
    },
    {
        "id": 12,
        "name": "Mirror Magic Peony",
        "character_theme": "Gauche Adlai (Black Bulls)",
        "riddle": "Reflecting double the light beside the glass art boards and student sketches.",
        "location": "Art Workshop / Gallery Display",
        "points": 100,
        "color": "#4285F4"  # Google Blue
    },
    {
        "id": 13,
        "name": "Cotton Sheep Blossom",
        "character_theme": "Charmy Pappitson (Black Bulls)",
        "riddle": "Follow the sweet scent of fresh pastries, warm tea, and delicious meals.",
        "location": "School Cafeteria / Canteen Snack Counter",
        "points": 100,
        "color": "#FBBC05"  # Google Yellow
    },
    {
        "id": 14,
        "name": "Sealing Swallowtail Blossom",
        "character_theme": "Nero / Secre Swallowtail",
        "riddle": "Perched like an observant bird right beside the front reception and keys.",
        "location": "Administration Desk / Reception Area",
        "points": 110,
        "color": "#202124"  # Charcoal Black
    },
    {
        "id": 15,
        "name": "Dark Cloaked Nightshade",
        "character_theme": "Yami Sukehiro (Captain Black Bulls)",
        "riddle": "'Surpass your limits!' Located near the teachers' strong coffee brew machine.",
        "location": "Teachers Lounge / Staff Coffee Point",
        "points": 150,
        "color": "#EA4335"  # Google Red
    },
    {
        "id": 16,
        "name": "Valiant Valkyrie Iris",
        "character_theme": "Noelle Silva (Black Bulls)",
        "riddle": "Guarded by pure water mana, near the emergency wash fountain in the hallway.",
        "location": "Hallway Safety Wash Station",
        "points": 100,
        "color": "#4285F4"  # Google Blue
    },
    {
        "id": 17,
        "name": "Dream World Marigold",
        "character_theme": "Dorothy Unsworth (Coral Peacock)",
        "riddle": "A peaceful sanctuary of soft beds and silence where sick students rest their eyes.",
        "location": "School Infirmary / Medical Room Doorway",
        "points": 100,
        "color": "#FBBC05"  # Google Yellow
    },
    {
        "id": 18,
        "name": "Paint Magic Cosmos",
        "character_theme": "Rill Boismortier (Aqua Deer)",
        "riddle": "Surrounded by colorful announcements, club posters, and creative student flyers.",
        "location": "Student Central Notice Board",
        "points": 100,
        "color": "#34A853"  # Google Green
    },
    {
        "id": 19,
        "name": "Replication Narcissus",
        "character_theme": "Rhya (Third Eye)",
        "riddle": "Where thousands of identical exam papers and test sheets are printed each morning.",
        "location": "School Printing / Copy Room",
        "points": 110,
        "color": "#9AA0A6"  # Silver Gray
    },
    {
        "id": 20,
        "name": "The 5-Leaf Clover Demon Blossom",
        "character_theme": "The Legendary Grimoire (GDG Special)",
        "riddle": "Inside the 5th leaf resides immense developer power! Found at the GDG Headquarters booth!",
        "location": "GDG Official Welcome Booth / Info Desk",
        "points": 250,
        "color": "#EA4335"  # Special Multi-color / Google Red
    }
]

DEFAULT_SQUADS = [
    {
        "name": "Black Bulls Devs",
        "captain": "Asta El-Khatib",
        "members": "Asta, Noelle, Finral, Luck",
        "color": "google-yellow",
        "motto": "Surpass your limits! Right here, right now!"
    },
    {
        "name": "Golden Dawn Squad",
        "captain": "Yuno Benali",
        "members": "Yuno, Klaus, Mimosa",
        "color": "google-blue",
        "motto": "The elite prodigies of cloud and algorithms."
    },
    {
        "name": "Crimson Lion Coders",
        "captain": "Fuegoleon Mansouri",
        "members": "Fuegoleon, Mereoleona, Leopold",
        "color": "google-red",
        "motto": "Burning passion for innovation and open source!"
    },
    {
        "name": "Green Mantis Hackers",
        "captain": "Jack Larbi",
        "members": "Jack, Sekke, En Ringard",
        "color": "google-green",
        "motto": "Slicing through bugs with razor precision."
    }
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(seed=True):
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS squads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        captain TEXT NOT NULL,
        members TEXT DEFAULT '',
        color TEXT DEFAULT 'google-blue',
        motto TEXT DEFAULT '',
        bonus_points INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS flowers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        character_theme TEXT NOT NULL,
        riddle TEXT NOT NULL,
        location TEXT NOT NULL,
        points INTEGER DEFAULT 100,
        color TEXT DEFAULT '#4285F4'
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS flower_awards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        squad_id INTEGER NOT NULL,
        flower_id INTEGER NOT NULL,
        awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        awarded_by TEXT DEFAULT 'GDG Admin Desk',
        notes TEXT DEFAULT '',
        FOREIGN KEY (squad_id) REFERENCES squads(id) ON DELETE CASCADE,
        FOREIGN KEY (flower_id) REFERENCES flowers(id) ON DELETE CASCADE,
        UNIQUE (squad_id, flower_id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS live_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        squad_id INTEGER,
        flower_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Seed flowers
    cur.execute('SELECT COUNT(*) FROM flowers')
    if cur.fetchone()[0] == 0:
        for f in DEFAULT_FLOWERS:
            cur.execute('''
            INSERT INTO flowers (id, name, character_theme, riddle, location, points, color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (f['id'], f['name'], f['character_theme'], f['riddle'], f['location'], f['points'], f['color']))

    # Seed squads
    if seed:
        cur.execute('SELECT COUNT(*) FROM squads')
        if cur.fetchone()[0] == 0:
            for s in DEFAULT_SQUADS:
                cur.execute('''
                INSERT INTO squads (name, captain, members, color, motto)
                VALUES (?, ?, ?, ?, ?)
                ''', (s['name'], s['captain'], s['members'], s['color'], s['motto']))
            
            # Initial sample check-ins
            cur.execute('INSERT OR IGNORE INTO flower_awards (squad_id, flower_id, awarded_by) VALUES (1, 1, "Admin Desk")')
            cur.execute('INSERT OR IGNORE INTO flower_awards (squad_id, flower_id, awarded_by) VALUES (1, 5, "Admin Desk")')
            cur.execute('INSERT OR IGNORE INTO flower_awards (squad_id, flower_id, awarded_by) VALUES (2, 4, "Admin Desk")')
            cur.execute('INSERT OR IGNORE INTO flower_awards (squad_id, flower_id, awarded_by) VALUES (3, 2, "Admin Desk")')

            cur.execute('''
            INSERT INTO live_events (event_type, title, description, squad_id, flower_id)
            VALUES ('INITIAL', 'Grand Magic Tournament Commenced', '4 Magic Knight Squads mobilized across the Academy.', NULL, NULL)
            ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("v2 Database initialized successfully at:", DB_PATH)
