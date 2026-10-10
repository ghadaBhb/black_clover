import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response, make_response
from database import get_db, init_db, DEFAULT_FLOWERS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gdg-black-clover-secret-mana-key-2026')

ADMIN_PIN = os.environ.get('ADMIN_PIN', "10GDG-open10DAY26")

init_db()

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

def log_activity(event_type, description):
    modify_db(
        "INSERT INTO activity_log (event_type, description) VALUES (?, ?)",
        (event_type, description)
    )

@app.route('/')
def index():
    squads = query_db('''
        SELECT s.*, 
               COUNT(c.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) as total_points,
               MAX(c.claimed_at) as last_claim
        FROM squads s
        LEFT JOIN claims c ON s.id = c.squad_id
        LEFT JOIN flowers f ON c.flower_id = f.id
        GROUP BY s.id
        ORDER BY flowers_count DESC, total_points DESC, last_claim ASC
    ''')
    
    total_flowers = query_db("SELECT COUNT(*) as count FROM flowers", one=True)['count']
    total_claims = query_db("SELECT COUNT(*) as count FROM claims", one=True)['count']
    total_squads = len(squads)
    
    flowers = query_db("SELECT id, name, character_theme, color, points FROM flowers ORDER BY id ASC")
    
    return render_template('index.html',
                           squads=squads,
                           flowers=flowers,
                           total_flowers=total_flowers,
                           total_claims=total_claims,
                           total_squads=total_squads)

@app.route('/leaderboard')
def leaderboard():
    squads = query_db('''
        SELECT s.*, 
               COUNT(c.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) as total_points,
               MAX(c.claimed_at) as last_claim
        FROM squads s
        LEFT JOIN claims c ON s.id = c.squad_id
        LEFT JOIN flowers f ON c.flower_id = f.id
        GROUP BY s.id
        ORDER BY flowers_count DESC, total_points DESC, last_claim ASC
    ''')
    total_flowers = query_db("SELECT COUNT(*) as count FROM flowers", one=True)['count']
    return render_template('leaderboard.html', squads=squads, total_flowers=total_flowers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        captain = request.form.get('captain', '').strip()
        color = request.form.get('color', 'google-blue')
        motto = request.form.get('motto', '').strip()
        
        member_names = request.form.getlist('members[]')
        member_roles = request.form.getlist('roles[]')
        
        if not name or not captain:
            flash("Squad Name and Captain Name are required!", "danger")
            return redirect(url_for('register'))
        
        # Check uniqueness
        existing = query_db("SELECT id FROM squads WHERE LOWER(name) = LOWER(?)", (name,), one=True)
        if existing:
            flash(f"A squad named '{name}' is already registered in the Magic Knights!", "warning")
            return redirect(url_for('register'))
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO squads (name, captain, color, motto) VALUES (?, ?, ?, ?)",
            (name, captain, color, motto)
        )
        squad_id = cur.lastrowid
        
        # Add captain as member if not in list
        cur.execute(
            "INSERT INTO members (squad_id, name, role) VALUES (?, ?, 'Captain')",
            (squad_id, captain)
        )
        
        for m_name, m_role in zip(member_names, member_roles):
            m_name = m_name.strip()
            if m_name and m_name.lower() != captain.lower():
                cur.execute(
                    "INSERT INTO members (squad_id, name, role) VALUES (?, ?, ?)",
                    (squad_id, m_name, m_role.strip() or 'Magic Knight')
                )
        
        conn.commit()
        conn.close()
        
        log_activity("REGISTER", f"New Squad registered: '{name}' led by {captain}")
        flash(f"Squad '{name}' registered successfully! Your Grimoire is now active.", "success")
        return redirect(url_for('squad_detail', squad_id=squad_id))

    return render_template('register.html')

@app.route('/squads')
def squads_list():
    squads = query_db('''
        SELECT s.*, 
               COUNT(c.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) as total_points,
               (SELECT COUNT(*) FROM members WHERE squad_id = s.id) as members_count
        FROM squads s
        LEFT JOIN claims c ON s.id = c.squad_id
        LEFT JOIN flowers f ON c.flower_id = f.id
        GROUP BY s.id
        ORDER BY flowers_count DESC, total_points DESC
    ''')
    total_flowers = query_db("SELECT COUNT(*) as count FROM flowers", one=True)['count']
    return render_template('squads.html', squads=squads, total_flowers=total_flowers)

@app.route('/squad/<int:squad_id>')
def squad_detail(squad_id):
    squad = query_db("SELECT * FROM squads WHERE id = ?", (squad_id,), one=True)
    if not squad:
        flash("Squad not found!", "danger")
        return redirect(url_for('squads_list'))
    
    members = query_db("SELECT * FROM members WHERE squad_id = ? ORDER BY id ASC", (squad_id,))
    
    # Get all flowers and whether this squad claimed them
    flowers = query_db('''
        SELECT f.*, 
               CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END as is_claimed,
               c.claimed_at,
               c.claimed_by
        FROM flowers f
        LEFT JOIN claims c ON f.id = c.flower_id AND c.squad_id = ?
        ORDER BY f.id ASC
    ''', (squad_id,))
    
    claimed_count = sum(1 for f in flowers if f['is_claimed'])
    total_points = sum(f['points'] for f in flowers if f['is_claimed'])
    total_flowers = len(flowers)
    
    return render_template('grimoire.html',
                           squad=squad,
                           members=members,
                           flowers=flowers,
                           claimed_count=claimed_count,
                           total_points=total_points,
                           total_flowers=total_flowers)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Simple PIN verification
    pin = request.args.get('pin') or request.form.get('pin') or request.cookies.get('admin_pin')
    is_authenticated = (pin == ADMIN_PIN)

    if request.method == 'POST' and request.form.get('action') == 'login':
        entered = request.form.get('pin', '').strip()
        if entered == ADMIN_PIN:
            resp = make_response(redirect(url_for('admin')))
            resp.set_cookie('admin_pin', ADMIN_PIN, max_age=86400, path='/')
            flash("Admin access granted! Welcome, Grand Magic Master.", "success")
            return resp
        else:
            flash("Incorrect Organizer PIN!", "danger")
            return render_template('admin.html', is_authenticated=False, squads=[], flowers=[], claim_matrix={}, logs=[])

    if not is_authenticated:
        return render_template('admin.html', is_authenticated=False, squads=[], flowers=[], claim_matrix={}, logs=[])

    squads = query_db('''
        SELECT s.*, 
               COUNT(c.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) as total_points
        FROM squads s
        LEFT JOIN claims c ON s.id = c.squad_id
        LEFT JOIN flowers f ON c.flower_id = f.id
        GROUP BY s.id
        ORDER BY s.id ASC
    ''')
    
    flowers = query_db("SELECT * FROM flowers ORDER BY id ASC")
    claims = query_db("SELECT squad_id, flower_id, claimed_at FROM claims")
    claim_matrix = {}
    for cl in claims:
        claim_matrix[(cl['squad_id'], cl['flower_id'])] = cl['claimed_at']

    logs = query_db("SELECT * FROM activity_log ORDER BY id DESC LIMIT 50")

    resp = make_response(render_template('admin.html',
                                          is_authenticated=True,
                                          squads=squads,
                                          flowers=flowers,
                                          claim_matrix=claim_matrix,
                                          logs=logs,
                                          admin_pin=ADMIN_PIN))
    resp.set_cookie('admin_pin', ADMIN_PIN, max_age=86400)
    return resp

# --- JSON API Endpoints ---

@app.route('/api/leaderboard')
def api_leaderboard():
    squads = query_db('''
        SELECT s.id, s.name, s.captain, s.color, s.motto,
               COUNT(c.id) as flowers_count, 
               COALESCE(SUM(f.points), 0) as total_points,
               MAX(c.claimed_at) as last_claim
        FROM squads s
        LEFT JOIN claims c ON s.id = c.squad_id
        LEFT JOIN flowers f ON c.flower_id = f.id
        GROUP BY s.id
        ORDER BY flowers_count DESC, total_points DESC, last_claim ASC
    ''')
    
    total_flowers = query_db("SELECT COUNT(*) as count FROM flowers", one=True)['count']
    total_claims = query_db("SELECT COUNT(*) as count FROM claims", one=True)['count']
    
    return jsonify({
        "status": "success",
        "total_flowers": total_flowers,
        "total_claims": total_claims,
        "timestamp": datetime.now().isoformat(),
        "leaderboard": [dict(s) for s in squads]
    })

@app.route('/api/claim', methods=['POST'])
def api_claim():
    data = request.get_json() or request.form
    squad_id = data.get('squad_id')
    passcode = (data.get('passcode') or '').strip().upper()
    claimed_by = (data.get('claimed_by') or 'Magic Knight').strip()

    if not squad_id or not passcode:
        return jsonify({"status": "error", "message": "Please select a squad and enter the Rune Passcode!"}), 400

    try:
        squad_id = int(squad_id)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid squad ID"}), 400

    squad = query_db("SELECT * FROM squads WHERE id = ?", (squad_id,), one=True)
    if not squad:
        return jsonify({"status": "error", "message": "Squad does not exist!"}), 404

    # Lookup flower by passcode
    flower = query_db("SELECT * FROM flowers WHERE UPPER(passcode) = ?", (passcode,), one=True)
    if not flower:
        return jsonify({
            "status": "error", 
            "message": "Invalid Rune Passcode! The flower mana rejected your entry."
        }), 400

    # Check if already claimed
    already = query_db("SELECT id FROM claims WHERE squad_id = ? AND flower_id = ?", (squad_id, flower['id']), one=True)
    if already:
        return jsonify({
            "status": "error", 
            "message": f"Your squad already unlocked Flower #{flower['id']} ({flower['name']})!"
        }), 409

    # Insert claim
    modify_db(
        "INSERT INTO claims (squad_id, flower_id, claimed_by) VALUES (?, ?, ?)",
        (squad_id, flower['id'], claimed_by)
    )

    log_activity(
        "CLAIM",
        f"Squad '{squad['name']}' discovered Flower #{flower['id']} ({flower['name']}) [+ {flower['points']} MP] by {claimed_by}"
    )

    # Get updated totals for this squad
    totals = query_db('''
        SELECT COUNT(c.id) as flowers_count, COALESCE(SUM(f.points), 0) as total_points
        FROM claims c
        JOIN flowers f ON c.flower_id = f.id
        WHERE c.squad_id = ?
    ''', (squad_id,), one=True)

    return jsonify({
        "status": "success",
        "message": f"Mana Unlocked! You claimed Flower #{flower['id']}: {flower['name']}!",
        "flower": {
            "id": flower['id'],
            "name": flower['name'],
            "character_theme": flower['character_theme'],
            "points": flower['points'],
            "color": flower['color']
        },
        "squad": {
            "name": squad['name'],
            "flowers_count": totals['flowers_count'],
            "total_points": totals['total_points']
        }
    })

@app.route('/api/admin/toggle-claim', methods=['POST'])
def api_admin_toggle_claim():
    pin = request.headers.get('X-Admin-PIN') or request.form.get('pin') or request.cookies.get('admin_pin')
    if pin != ADMIN_PIN:
        return jsonify({"status": "error", "message": "Unauthorized organizer PIN"}), 401

    data = request.get_json() or request.form
    squad_id = int(data.get('squad_id'))
    flower_id = int(data.get('flower_id'))

    existing = query_db("SELECT id FROM claims WHERE squad_id = ? AND flower_id = ?", (squad_id, flower_id), one=True)
    squad = query_db("SELECT name FROM squads WHERE id = ?", (squad_id,), one=True)
    flower = query_db("SELECT name, points FROM flowers WHERE id = ?", (flower_id,), one=True)

    if existing:
        modify_db("DELETE FROM claims WHERE id = ?", (existing['id'],))
        log_activity("ADMIN_REVOKE", f"Organizer revoked Flower #{flower_id} ({flower['name']}) from '{squad['name']}'")
        action = "revoked"
    else:
        modify_db("INSERT INTO claims (squad_id, flower_id, claimed_by) VALUES (?, ?, 'Organizer')", (squad_id, flower_id))
        log_activity("ADMIN_GRANT", f"Organizer granted Flower #{flower_id} ({flower['name']}) to '{squad['name']}'")
        action = "granted"

    return jsonify({"status": "success", "action": action, "squad_id": squad_id, "flower_id": flower_id})

@app.route('/api/admin/edit-flower', methods=['POST'])
def api_admin_edit_flower():
    pin = request.cookies.get('admin_pin') or request.form.get('pin')
    if pin != ADMIN_PIN:
        flash("Unauthorized!", "danger")
        return redirect(url_for('admin'))

    flower_id = int(request.form.get('flower_id'))
    name = request.form.get('name')
    character_theme = request.form.get('character_theme')
    riddle = request.form.get('riddle')
    location_hint = request.form.get('location_hint')
    passcode = request.form.get('passcode').strip().upper()
    points = int(request.form.get('points', 100))

    modify_db('''
        UPDATE flowers
        SET name = ?, character_theme = ?, riddle = ?, location_hint = ?, passcode = ?, points = ?
        WHERE id = ?
    ''', (name, character_theme, riddle, location_hint, passcode, points, flower_id))

    log_activity("ADMIN_EDIT", f"Updated Flower #{flower_id} ({name}) settings/riddle")
    flash(f"Flower #{flower_id} successfully updated!", "success")
    return redirect(url_for('admin'))

@app.route('/api/admin/add-flower', methods=['POST'])
def api_admin_add_flower():
    pin = request.cookies.get('admin_pin') or request.form.get('pin')
    if pin != ADMIN_PIN:
        flash("Unauthorized!", "danger")
        return redirect(url_for('admin'))

    name = request.form.get('name', '').strip()
    character_theme = request.form.get('character_theme', '').strip()
    riddle = request.form.get('riddle', '').strip()
    location_hint = request.form.get('location_hint', '').strip()
    passcode = request.form.get('passcode', '').strip().upper()

    try:
        points = int(request.form.get('points', '100'))
    except ValueError:
        flash("Flower points must be a whole number.", "danger")
        return redirect(url_for('admin'))

    if not all((name, character_theme, riddle, location_hint, passcode)):
        flash("All flower fields are required.", "danger")
        return redirect(url_for('admin'))
    if points < 0:
        flash("Flower points cannot be negative.", "danger")
        return redirect(url_for('admin'))
    if query_db("SELECT id FROM flowers WHERE UPPER(passcode) = ?", (passcode,), one=True):
        flash("That passcode is already assigned to another flower.", "danger")
        return redirect(url_for('admin'))

    flower_id = query_db("SELECT COALESCE(MAX(id), 0) + 1 FROM flowers", one=True)[0]
    modify_db('''
        INSERT INTO flowers (id, name, character_theme, riddle, location_hint, passcode, points)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (flower_id, name, character_theme, riddle, location_hint, passcode, points))

    log_activity("ADMIN_ADD", f"Added Flower #{flower_id} ({name})")
    flash(f"Flower #{flower_id} added successfully!", "success")
    return redirect(url_for('admin'))

@app.route('/api/admin/delete-squad', methods=['POST'])
def api_admin_delete_squad():
    pin = request.cookies.get('admin_pin')
    if pin != ADMIN_PIN:
        flash("Unauthorized", "danger")
        return redirect(url_for('admin'))

    squad_id = int(request.form.get('squad_id'))
    squad = query_db("SELECT name FROM squads WHERE id = ?", (squad_id,), one=True)
    if squad:
        modify_db("DELETE FROM squads WHERE id = ?", (squad_id,))
        modify_db("DELETE FROM claims WHERE squad_id = ?", (squad_id,))
        modify_db("DELETE FROM members WHERE squad_id = ?", (squad_id,))
        log_activity("ADMIN_DELETE", f"Deleted Squad '{squad['name']}' and its records")
        flash(f"Squad '{squad['name']}' was removed.", "info")

    return redirect(url_for('admin'))

@app.route('/api/admin/reset-claims', methods=['POST'])
def api_admin_reset_claims():
    pin = request.cookies.get('admin_pin')
    if pin != ADMIN_PIN:
        flash("Unauthorized", "danger")
        return redirect(url_for('admin'))

    modify_db("DELETE FROM claims")
    log_activity("ADMIN_RESET", "All flower claims have been cleared by Organizer.")
    flash("All squad flower claims have been reset to 0!", "warning")
    return redirect(url_for('admin'))

@app.route('/api/admin/export-csv')
def export_csv():
    pin = request.cookies.get('admin_pin')
    if pin != ADMIN_PIN:
        return "Unauthorized", 401

    squads = query_db('''
        SELECT s.id, s.name, s.captain, 
               COUNT(c.id) as flowers_found, 
               COALESCE(SUM(f.points), 0) as total_points,
               GROUP_CONCAT(f.id) as claimed_flower_ids
        FROM squads s
        LEFT JOIN claims c ON s.id = c.squad_id
        LEFT JOIN flowers f ON c.flower_id = f.id
        GROUP BY s.id
        ORDER BY flowers_found DESC, total_points DESC
    ''')

    csv_data = "Rank,Squad ID,Squad Name,Captain,Flowers Found (out of 20),Total Mana Points,Unlocked Flower IDs\n"
    for rank, s in enumerate(squads, start=1):
        csv_data += f"{rank},{s['id']},\"{s['name']}\",\"{s['captain']}\",{s['flowers_found']},{s['total_points']},\"{s['claimed_flower_ids'] or ''}\"\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=gdg_black_clover_results.csv"}
    )

if __name__ == '__main__':
    print("Magic Kingdom Grimoire running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
