from flask import Blueprint, render_template, jsonify
from psycopg2.extras import RealDictCursor
from app.db import get_conn, put_conn

home_bp = Blueprint("home", __name__)

@home_bp.get("/")
def home_page():
    return render_template("home/home.html")  # テンプレパスは環境に合わせて

@home_bp.get("/api/landmarks")
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