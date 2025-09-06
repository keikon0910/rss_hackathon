# app/routes/landmarks.py
from flask import Blueprint, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
DB_PARAMS = {
    "dbname": "posts_db_rkcz",
    "user": "posts_db_rkcz_user",
    "password": "rPcuE4VPsn79TPngWJd8ZAQrDF1ktI7F",
    "host": "dpg-d2top2p5pdvs739pct1g-a.oregon-postgres.render.com",
    "port": "5432",
    # "sslmode": "require",
}
def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)
landmark_bp = Blueprint(
    "landmark",
    __name__,
    template_folder='../../templates/landmark',
    url_prefix=""
)
@landmark_bp.get("/api/landmarks")
def api_landmarks():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""SELECT id, name, geom_json FROM landmarks ORDER BY id DESC""")
            rows = cur.fetchall()
        return jsonify({
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": r["id"],
                    "properties": {"name": r["name"]},
                    "geometry": r["geom_json"]
                }
                for r in rows
            ]
        })
    finally:
        conn.close()