import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response, make_response
from database import get_db, init_db, DEFAULT_FLOWERS

app = Flask(__name__)
app.secret_key = 'gdg-black-clover-v2-reality-master-key'

ADMIN_PIN = "10GDG-open10DAY26"

def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    r = cur.fetchall()
    conn.commit()
    conn.close()
    return (r[0] if r else None) if one else r

def modify_db(query, args=()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    last_id = cur.lastrowid
    conn.commit()
    conn.close()
    return last_id

def log_event(event_type, title, description, squad_id=None, flower_id=None):
    modify_db(
        "INSERT INTO live_events (event_type, title, description, squad_id, flower_id) VALUES (?, ?, ?, ?, ?)",
        (event_type, title, description, squad_id, flower_id)
    )

# ----------------- PUBLIC SPECTATOR ROUTES (TEAMS DON'T LOG IN) -----------------

@app.route('/')
def scoreboard():
    squads = query_db('''
        SELECT s.*, 
               COUNT(fa.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) + s.bonus_points as total_points,
               MAX(fa.awarded_at) as last_award
        FROM squads s
        LEFT JOIN flower_awards fa ON s.id = fa.squad_id
        LEFT JOIN flowers f ON fa.flower_id = f.id
        GROUP BY s.id
        ORDER BY flowers_count DESC, total_points DESC, last_award ASC
    ''')

    total_flowers = query_db("SELECT COUNT(*) as count FROM flowers", one=True)['count']
    total_awards = query_db("SELECT COUNT(*) as count FROM flower_awards", one=True)['count']
    total_squads = len(squads)

    flowers = query_db("SELECT * FROM flowers ORDER BY id ASC")
    
    # Get matrix of who found what
    awards = query_db("SELECT squad_id, flower_id FROM flower_awards")
    award_set = set((a['squad_id'], a['flower_id']) for a in awards)

    recent_events = query_db("SELECT * FROM live_events ORDER BY id DESC LIMIT 10")

    return render_template('scoreboard.html',
                           squads=squads,
                           flowers=flowers,
                           award_set=award_set,
                           total_flowers=total_flowers,
                           total_awards=total_awards,
                           total_squads=total_squads,
                           recent_events=recent_events)

@app.route('/projector')
def projector():
    squads = query_db('''
        SELECT s.*, 
               COUNT(fa.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) + s.bonus_points as total_points,
               MAX(fa.awarded_at) as last_award
        FROM squads s
        LEFT JOIN flower_awards fa ON s.id = fa.squad_id
        LEFT JOIN flowers f ON fa.flower_id = f.id
        GROUP BY s.id
        ORDER BY flowers_count DESC, total_points DESC, last_award ASC
    ''')
    total_flowers = query_db("SELECT COUNT(*) as count FROM flowers", one=True)['count']
    recent_events = query_db("SELECT * FROM live_events ORDER BY id DESC LIMIT 6")
    return render_template('projector.html', squads=squads, total_flowers=total_flowers, recent_events=recent_events)

# ----------------- ADMIN COMMAND CENTER (ORGANIZERS ONLY) -----------------

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    pin = request.args.get('pin') or request.form.get('pin') or request.cookies.get('v2_admin_pin')
    is_authenticated = (pin == ADMIN_PIN)

    if request.method == 'POST' and request.form.get('action') == 'login':
        entered = request.form.get('pin', '').strip()
        if entered == ADMIN_PIN:
            resp = make_response(redirect(url_for('admin')))
            resp.set_cookie('v2_admin_pin', ADMIN_PIN, max_age=86400, path='/')
            flash("Welcome, Grand Magic Master. Ready to record flowers!", "success")
            return resp
        else:
            flash("Incorrect Organizer PIN!", "danger")
            return render_template('admin.html', is_authenticated=False, squads=[], flowers=[], award_dict={}, events=[])

    if not is_authenticated:
        return render_template('admin.html', is_authenticated=False, squads=[], flowers=[], award_dict={}, events=[])

    squads = query_db('''
        SELECT s.*, 
               COUNT(fa.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) + s.bonus_points as total_points
        FROM squads s
        LEFT JOIN flower_awards fa ON s.id = fa.squad_id
        LEFT JOIN flowers f ON fa.flower_id = f.id
        GROUP BY s.id
        ORDER BY s.id ASC
    ''')

    flowers = query_db("SELECT * FROM flowers ORDER BY id ASC")
    awards = query_db("SELECT squad_id, flower_id, awarded_at, notes FROM flower_awards")
    award_dict = {(a['squad_id'], a['flower_id']): a for a in awards}

    # Count how many times each flower has been brought
    flower_counts = {}
    for a in awards:
        flower_counts[a['flower_id']] = flower_counts.get(a['flower_id'], 0) + 1

    events = query_db("SELECT * FROM live_events ORDER BY id DESC LIMIT 40")

    resp = make_response(render_template('admin.html',
                                          is_authenticated=True,
                                          squads=squads,
                                          flowers=flowers,
                                          award_dict=award_dict,
                                          flower_counts=flower_counts,
                                          events=events,
                                          admin_pin=ADMIN_PIN))
    resp.set_cookie('v2_admin_pin', ADMIN_PIN, max_age=86400)
    return resp

@app.route('/admin/cheat-sheet')
def cheat_sheet():
    pin = request.cookies.get('v2_admin_pin')
    if pin != ADMIN_PIN:
        return redirect(url_for('admin'))
    flowers = query_db("SELECT * FROM flowers ORDER BY id ASC")
    return render_template('cheat_sheet.html', flowers=flowers)

# ----------------- ADMIN ACTIONS (REGISTRATION & FLOWER AWARDS) -----------------

@app.route('/api/admin/register-squad', methods=['POST'])
def api_admin_register_squad():
    pin = request.headers.get('X-Admin-PIN') or request.cookies.get('v2_admin_pin') or request.form.get('pin')
    if pin != ADMIN_PIN:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json() or request.form
    name = data.get('name', '').strip()
    captain = data.get('captain', '').strip()
    members = data.get('members', '').strip()
    color = data.get('color', 'google-blue')
    motto = data.get('motto', '').strip()

    if not name or not captain:
        return jsonify({"status": "error", "message": "Squad Name and Captain Name are required!"}), 400

    existing = query_db("SELECT id FROM squads WHERE LOWER(name) = LOWER(?)", (name,), one=True)
    if existing:
        return jsonify({"status": "error", "message": f"Squad '{name}' is already registered!"}), 409

    squad_id = modify_db(
        "INSERT INTO squads (name, captain, members, color, motto) VALUES (?, ?, ?, ?, ?)",
        (name, captain, members, color, motto)
    )

    log_event("SQUAD_REGISTERED", f"New Squad Mobilized: {name}", f"Led by Captain {captain}. Members: {members}", squad_id=squad_id)

    return jsonify({
        "status": "success",
        "message": f"Squad '{name}' registered successfully!",
        "squad": { "id": squad_id, "name": name, "captain": captain }
    })

@app.route('/api/admin/award-flower', methods=['POST'])
def api_admin_award_flower():
    pin = request.headers.get('X-Admin-PIN') or request.cookies.get('v2_admin_pin') or request.form.get('pin')
    if pin != ADMIN_PIN:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json() or request.form
    squad_id = int(data.get('squad_id'))
    flower_id = int(data.get('flower_id'))
    notes = data.get('notes', '').strip()

    squad = query_db("SELECT * FROM squads WHERE id = ?", (squad_id,), one=True)
    flower = query_db("SELECT * FROM flowers WHERE id = ?", (flower_id,), one=True)

    if not squad or not flower:
        return jsonify({"status": "error", "message": "Invalid Squad or Flower ID"}), 404

    # Check if already awarded
    already = query_db("SELECT id FROM flower_awards WHERE squad_id = ? AND flower_id = ?", (squad_id, flower_id), one=True)
    if already:
        return jsonify({"status": "error", "message": f"Squad '{squad['name']}' already received Flower #{flower_id}!"}), 409

    modify_db(
        "INSERT INTO flower_awards (squad_id, flower_id, awarded_by, notes) VALUES (?, ?, 'Admin Desk', ?)",
        (squad_id, flower_id, notes)
    )

    title = f"🌸 Flower #{flower['id']} Discovered!"
    desc = f"Squad '{squad['name']}' physically delivered {flower['name']} to the GDG Booth (+{flower['points']} MP)!"
    log_event("FLOWER_AWARDED", title, desc, squad_id=squad_id, flower_id=flower_id)

    # Get updated totals
    totals = query_db('''
        SELECT COUNT(fa.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) + s.bonus_points as total_points
        FROM squads s
        LEFT JOIN flower_awards fa ON s.id = fa.squad_id
        LEFT JOIN flowers f ON fa.flower_id = f.id
        WHERE s.id = ?
        GROUP BY s.id
    ''', (squad_id,), one=True)

    return jsonify({
        "status": "success",
        "message": f"Awarded Flower #{flower['id']} ({flower['name']}) to '{squad['name']}'!",
        "squad_name": squad['name'],
        "flower_name": flower['name'],
        "points": flower['points'],
        "new_flowers_count": totals['flowers_count'],
        "new_total_points": totals['total_points']
    })

@app.route('/api/admin/revoke-flower', methods=['POST'])
def api_admin_revoke_flower():
    pin = request.headers.get('X-Admin-PIN') or request.cookies.get('v2_admin_pin') or request.form.get('pin')
    if pin != ADMIN_PIN:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json() or request.form
    squad_id = int(data.get('squad_id'))
    flower_id = int(data.get('flower_id'))

    squad = query_db("SELECT name FROM squads WHERE id = ?", (squad_id,), one=True)
    flower = query_db("SELECT name FROM flowers WHERE id = ?", (flower_id,), one=True)

    existing = query_db("SELECT id FROM flower_awards WHERE squad_id = ? AND flower_id = ?", (squad_id, flower_id), one=True)
    if not existing:
        return jsonify({"status": "error", "message": "This flower is not awarded to this squad."}), 404

    modify_db("DELETE FROM flower_awards WHERE id = ?", (existing['id'],))
    log_event("FLOWER_REVOKED", f"Revoked Flower #{flower_id}", f"Admin removed Flower #{flower_id} ({flower['name']}) from '{squad['name']}'", squad_id=squad_id, flower_id=flower_id)

    return jsonify({"status": "success", "message": f"Revoked Flower #{flower_id} from '{squad['name']}'"})

@app.route('/api/admin/edit-flower', methods=['POST'])
def api_admin_edit_flower():
    pin = request.headers.get('X-Admin-PIN') or request.cookies.get('v2_admin_pin') or request.form.get('pin')
    if pin != ADMIN_PIN:
        flash("Unauthorized organizer PIN!", "danger")
        return redirect(url_for('admin'))

    flower_id = int(request.form.get('flower_id'))
    name = request.form.get('name', '').strip()
    character_theme = request.form.get('character_theme', '').strip()
    location = request.form.get('location', '').strip()
    riddle = request.form.get('riddle', '').strip()
    points = int(request.form.get('points', 100))

    modify_db('''
        UPDATE flowers
        SET name = ?, character_theme = ?, location = ?, riddle = ?, points = ?
        WHERE id = ?
    ''', (name, character_theme, location, riddle, points, flower_id))

    log_event("FLOWER_EDIT", f"Updated Flower #{flower_id}", f"Admin updated {name} ({points} MP, Location: {location})", flower_id=flower_id)
    flash(f"Flower #{flower_id} ('{name}') updated to {points} MP!", "success")
    return redirect(url_for('admin'))

@app.route('/api/admin/add-flower', methods=['POST'])
def api_admin_add_flower():
    pin = request.headers.get('X-Admin-PIN') or request.cookies.get('v2_admin_pin') or request.form.get('pin')
    if pin != ADMIN_PIN:
        flash("Unauthorized organizer PIN!", "danger")
        return redirect(url_for('admin'))

    name = request.form.get('name', '').strip()
    character_theme = request.form.get('character_theme', '').strip()
    location = request.form.get('location', '').strip()
    riddle = request.form.get('riddle', '').strip()

    try:
        points = int(request.form.get('points', '100'))
    except ValueError:
        flash("Flower points must be a whole number.", "danger")
        return redirect(url_for('admin'))

    if not all((name, character_theme, location, riddle)):
        flash("Flower name, theme, location, and riddle are required.", "danger")
        return redirect(url_for('admin'))
    if points < 0:
        flash("Flower points cannot be negative.", "danger")
        return redirect(url_for('admin'))

    flower_id = query_db("SELECT COALESCE(MAX(id), 0) + 1 FROM flowers", one=True)[0]
    modify_db('''
        INSERT INTO flowers (id, name, character_theme, riddle, location, points)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (flower_id, name, character_theme, riddle, location, points))

    log_event("FLOWER_ADDED", f"Added Flower #{flower_id}", f"Admin added {name} ({points} MP, Location: {location})", flower_id=flower_id)
    flash(f"Flower #{flower_id} ('{name}') added successfully!", "success")
    return redirect(url_for('admin'))

@app.route('/api/admin/bonus-points', methods=['POST'])
def api_admin_bonus_points():
    pin = request.cookies.get('v2_admin_pin')
    if pin != ADMIN_PIN:
        flash("Unauthorized", "danger")
        return redirect(url_for('admin'))

    squad_id = int(request.form.get('squad_id'))
    pts = int(request.form.get('points', 0))
    reason = request.form.get('reason', 'Organizer bonus').strip()

    squad = query_db("SELECT * FROM squads WHERE id = ?", (squad_id,), one=True)
    if squad:
        modify_db("UPDATE squads SET bonus_points = bonus_points + ? WHERE id = ?", (pts, squad_id))
        log_event("BONUS_POINTS", f"Bonus Points: {pts:+d} MP", f"'{squad['name']}' awarded {pts:+d} MP by Admin: {reason}", squad_id=squad_id)
        flash(f"Adjusted points for '{squad['name']}' by {pts:+d} MP ({reason})", "success")

    return redirect(url_for('admin'))

@app.route('/api/admin/delete-squad', methods=['POST'])
def api_admin_delete_squad():
    pin = request.cookies.get('v2_admin_pin')
    if pin != ADMIN_PIN:
        flash("Unauthorized", "danger")
        return redirect(url_for('admin'))

    squad_id = int(request.form.get('squad_id'))
    squad = query_db("SELECT name FROM squads WHERE id = ?", (squad_id,), one=True)
    if squad:
        modify_db("DELETE FROM squads WHERE id = ?", (squad_id,))
        modify_db("DELETE FROM flower_awards WHERE squad_id = ?", (squad_id,))
        log_event("SQUAD_DELETED", f"Squad Removed", f"Admin deleted '{squad['name']}'", squad_id=squad_id)
        flash(f"Removed squad '{squad['name']}'.", "info")

    return redirect(url_for('admin'))

@app.route('/api/admin/reset-awards', methods=['POST'])
def api_admin_reset_awards():
    pin = request.cookies.get('v2_admin_pin')
    if pin != ADMIN_PIN:
        flash("Unauthorized", "danger")
        return redirect(url_for('admin'))

    modify_db("DELETE FROM flower_awards")
    log_event("GAME_RESET", "Game Awards Reset", "All flower check-ins cleared by Grand Magic Admin.")
    flash("All squad flower awards have been reset for a fresh round!", "warning")
    return redirect(url_for('admin'))

@app.route('/admin/export-csv')
def export_csv():
    pin = request.cookies.get('v2_admin_pin')
    if pin != ADMIN_PIN:
        return "Unauthorized", 401

    squads = query_db('''
        SELECT s.id, s.name, s.captain, s.members, s.bonus_points,
               COUNT(fa.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) + s.bonus_points as total_points,
               GROUP_CONCAT(f.id) as awarded_flower_ids
        FROM squads s
        LEFT JOIN flower_awards fa ON s.id = fa.squad_id
        LEFT JOIN flowers f ON fa.flower_id = f.id
        GROUP BY s.id
        ORDER BY flowers_count DESC, total_points DESC
    ''')

    csv_data = "Rank,Squad ID,Squad Name,Captain,Members,Flowers Found (out of 20),Bonus MP,Total Mana Points,Flowers IDs\n"
    for rank, s in enumerate(squads, start=1):
        csv_data += f"{rank},{s['id']},\"{s['name']}\",\"{s['captain']}\",\"{s['members']}\",{s['flowers_count']},{s['bonus_points']},{s['total_points']},\"{s['awarded_flower_ids'] or ''}\"\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=gdg_v2_black_clover_results.csv"}
    )

# ----------------- REAL-TIME PUBLIC POLLING API -----------------

@app.route('/api/scoreboard')
def api_scoreboard():
    squads = query_db('''
        SELECT s.id, s.name, s.captain, s.members, s.color, s.motto, s.bonus_points,
               COUNT(fa.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) + s.bonus_points as total_points,
               MAX(fa.awarded_at) as last_award
        FROM squads s
        LEFT JOIN flower_awards fa ON s.id = fa.squad_id
        LEFT JOIN flowers f ON fa.flower_id = f.id
        GROUP BY s.id
        ORDER BY flowers_count DESC, total_points DESC, last_award ASC
    ''')

    total_flowers = query_db("SELECT COUNT(*) as count FROM flowers", one=True)['count']
    total_awards = query_db("SELECT COUNT(*) as count FROM flower_awards", one=True)['count']

    # Get awarded flower ids for each squad
    awards = query_db("SELECT squad_id, flower_id FROM flower_awards")
    squad_flowers = {}
    for a in awards:
        squad_flowers.setdefault(a['squad_id'], []).append(a['flower_id'])

    recent_events = query_db("SELECT * FROM live_events ORDER BY id DESC LIMIT 5")

    squads_list = []
    for s in squads:
        sd = dict(s)
        sd['awarded_ids'] = squad_flowers.get(s['id'], [])
        squads_list.append(sd)

    return jsonify({
        "status": "success",
        "total_flowers": total_flowers,
        "total_awards": total_awards,
        "timestamp": datetime.now().isoformat(),
        "squads": squads_list,
        "recent_events": [dict(e) for e in recent_events]
    })

if __name__ == '__main__':
    init_db()
    print("GDG x Black Clover v2 (Admin Reality Managed) running on http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
