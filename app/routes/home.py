from flask import Blueprint, render_template, jsonify, session, redirect, url_for, flash
from psycopg2.extras import RealDictCursor
from ..db import get_conn, put_conn
home_bp = Blueprint('home', __name__,
    template_folder='../../templates/home',  
    url_prefix=''  
)

home_bp = Blueprint(
    'home',
    __name__,
    template_folder='../../templates/home',
    url_prefix=''
)

@home_bp.route('/home')
def home():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('home.html', display_name=session.get('display_name'))

@home_bp.get('/api/landmarks')
def api_landmarks():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name, geom_json FROM landmarks ORDER BY id")
            rows = cur.fetchall()
        return jsonify({
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": r["id"],
                    "properties": {"name": r["name"]},
                    "geometry": r["geom_json"]
                } for r in rows
            ]
        })
    finally:
        put_conn(conn)