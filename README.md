# 🍀 GDG x Black Clover: The 20 Mana Flowers Scavenger Hunt

**Open Day Platform for Google Developer Groups (GDG) themed with *Black Clover* Anime.**

This repository contains two complete versions designed for different event styles:

---

## 📌 Comparison: Which version should you use?

| Feature | **v1 (Participant Self-Service)** | **v2 (Reality Managed by Admins)** 🌟 *(Recommended)* |
|---|---|---|
| **How Teams Play** | Teams enter Rune Codes / scan QR codes on their phones | Teams hunt physical flowers in school and **bring them to the GDG Booth** |
| **Team Access** | Teams have direct access to their online Grimoire | **Teams have NO access to platform**; it is purely spectator & projector |
| **Registration** | Teams self-register on the website | **Admin registers teams** at the GDG Desk when they arrive |
| **Flower Scoring** | Teams enter secret passcodes | **Admin taps the flower icon** to award points in real time |
| **Screen Display** | Interactive participant website + projector | **Cinema-grade Stage Projector & Spectator Scoreboard** |
| **Default Port** | `http://localhost:5000` | `http://localhost:5001` |

In both versions, organizers can add flowers from the **Admin** page. New flowers are assigned the next available number and appear in the flower lists; v1 also requires a unique passcode for each new flower.

---

## 🚀 How to Run

### Launcher Menu:
Simply double-click `run.bat` and choose:
- Press `1` for **v1 (Online Self-Service)**
- Press `2` for **v2 (Reality Managed by Admin)**

Or run them individually:
* **v1**: Double click `run_v1.bat` (or `python app.py`) &rarr; **[http://localhost:5000](http://localhost:5000)**
* **v2**: Double click `run_v2.bat` (or `python v2/app.py`) &rarr; **[http://localhost:5001](http://localhost:5001)**

### Use Supabase and deploy v1 on Render

This repository's Render Blueprint deploys the Flask app in `app.py` (v1):

1. Create the five tables (`squads`, `members`, `flowers`, `claims`, and `activity_log`) in Supabase using the schema for this app.
2. In Supabase, copy the PostgreSQL connection string from **Connect**. Keep it private.
3. For local development, put that value in the root `.env` file as `DATABASE_URL=...`. The app reads `.env` automatically.
4. Push this repository to GitHub and create a new **Blueprint** in Render for it.
5. Choose the repository and apply the settings in `render.yaml`. Enter the Supabase connection string for the `DATABASE_URL` environment variable when prompted in Render.
6. After the service is live, use its Render URL. Keep `DATABASE_URL`, `SECRET_KEY`, and `ADMIN_PIN` private.

On first startup, the app inserts its default flowers and demo squads if those tables are empty. Existing rows are left in place. The app now uses Supabase directly; it does not automatically copy existing records from `black_clover.db`.

---

## 🌟 v2 Platform Details (Reality Managed)

### 1. Public Scoreboard (`/`) & Stage Projector (`/projector`)
* **Auditorium Display**: Designed to project onto the hall screen or TV during the open day.
* **Read-only**: Clean spectator interface for the audience with no claim/login buttons.
* **1st Rank Wizard King**: Highlighted with glowing animated crown and stars.
* **20-Flowers Matrix**: Visual pill strip (`#1` to `#20`) showing which flowers each squad has collected.
* **Live Ticker**: "📢 BREAKING: Black Bulls delivered Flower #5 (Anti-Magic Lotus) to the GDG Booth! (+150 MP)".
* **Audio & Confetti**: Auto-plays crystalline anime fanfare and bursts confetti whenever an admin awards a flower!

### 2. Organizer Command Center (`/admin` - PIN: `10GDG-open10DAY26`)
* **⚡ 2-Click Flower Awarder**:
  1. Click the arriving Squad button (e.g., *Black Bulls*).
  2. Click the Flower icon they physically brought (e.g., *Flower #5*).
  * Points are awarded instantly, sound chimes on the stage, and leaderboard updates!
* **Undo / Revoke**: If a marshal clicks by accident, click "Undo" to remove the award.
* **Squad Registration Desk**: Quickly register teams as they arrive in the morning (Name, Captain, Teammates, Theme Color).
* **Bonus Points**: Award extra Mana Points (MP) for speed or mini-challenges.
* **Marshal Cheat Sheet (`/admin/cheat-sheet`)**: Printable A4 reference table listing all 20 flower locations for school marshals.
* **CSV Export**: 1-click download of final standings.

---

## 🌸 Master Flower Locations

| # | Flower Name | Anime Character / Squad | School Location Hint | Points |
|---|---|---|---|---|
| **1** | Azure Briar Rose | Charlotte (Blue Rose) | Water Fountain / Cooler | 100 MP |
| **2** | Crimson Flame Dahlia | Fuegoleon (Crimson Lions) | Science / Chemistry Lab | 100 MP |
| **3** | Verdant Mantis Blossom | Jack the Ripper (Green Mantis) | Courtyard / Garden | 100 MP |
| **4** | Golden Dawn Sunflower | Vangeance & Yuno | Auditorium / Stage | 100 MP |
| **5** | Anti-Magic Black Lotus | Asta (Black Bulls) | Under Central Staircase | 150 MP |
| **6** | Silver Mercury Lily | Nozel (Silver Eagles) | Trophy Showcase / Mirror | 100 MP |
| **7** | Wizard King Chrono Violet | Julius Novachrono | Grand Hall Wall Clock | 120 MP |
| **8** | Thunderstrike Orchid | Luck Voltia (Black Bulls) | Computer Lab / Server Rack | 100 MP |
| **9** | Spatial Portal Camellia | Finral (Black Bulls) | Main Entrance Turnstiles | 100 MP |
| **10** | Wind Spirit Sylph Blossom | Sylph & Yuno | Top Floor Terrace / Balcony | 120 MP |
| **11** | Forbidden Archive Lotus | Zagred / Shadow Palace | Library Back Archives | 130 MP |
| **12** | Mirror Magic Peony | Gauche Adlai | Art Studio / Glass Board | 100 MP |
| **13** | Cotton Sheep Blossom | Charmy Pappitson | Cafeteria / Canteen Counter | 100 MP |
| **14** | Sealing Swallowtail Blossom | Nero / Secre | Front Reception Desk | 110 MP |
| **15** | Dark Cloaked Nightshade | Yami Sukehiro (Black Bulls) | Teachers Lounge / Coffee | 150 MP |
| **16** | Valiant Valkyrie Iris | Noelle Silva | Emergency Safety Wash | 100 MP |
| **17** | Dream World Marigold | Dorothy Unsworth | School Infirmary / Medical Room | 100 MP |
| **18** | Paint Magic Cosmos | Rill Boismortier | Student Central Notice Board | 100 MP |
| **19** | Replication Narcissus | Rhya (Third Eye) | Printing / Copy Room | 110 MP |
| **20** | **5-Leaf Clover Demon Blossom** | **Legendary Grimoire** | **GDG Welcome Booth** | **250 MP** |
