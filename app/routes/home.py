from flask import Blueprint, render_template, jsonify, session, redirect, url_for, flash, current_app
from psycopg2.extras import RealDictCursor
from ..db import get_conn, put_conn
import json

home_bp = Blueprint(
    "home",
    __name__,
    template_folder='../../templates/home',
    url_prefix=""
)

@home_bp.route("/home")
def home():
    if "user_id" not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for("index.login"))
    return render_template("home.html", display_name=session.get("display_name"))

# --- 診断用: サーバ生存確認（あとで消してOK） ---
@home_bp.get("/api/ping")
def api_ping():
    return jsonify({"ok": True, "pong": True})

# --- 診断用: DB 接続だけ確認（あとで消してOK） ---
@home_bp.get("/api/dbcheck")
def api_dbcheck():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return jsonify({"ok": True})
    except Exception as e:
        current_app.logger.exception("DB check failed")
        return jsonify({"ok": False, "where": "connect_or_select", "detail": str(e)}), 500
    finally:
        try:
            put_conn(conn)
        except Exception:
            pass

@home_bp.get("/api/landmarks")
def api_landmarks():
    """ランドマーク一覧を GeoJSON FeatureCollection で返す。
       失敗時も JSON で原因を返す（フロントで中身を読めるようにする）。
    """
    # 接続
    try:
        conn = get_conn()
    except Exception as e:
        current_app.logger.exception("DB connect failed")
        return jsonify({"ok": False, "where": "connect", "detail": str(e)}), 500

    try:
        # 取得
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, geom_json, created_at
                FROM landmarks
                ORDER BY id
            """)
            rows = cur.fetchall()

        # 変換（geom_json が text の場合に備える）
        features = []
        for r in rows:
            geom = r["geom_json"]
            if isinstance(geom, str):
                try:
                    geom = json.loads(geom)
                except Exception:
                    current_app.logger.warning("invalid geom_json string id=%s name=%s", r["id"], r["name"])
                    # 壊れた行はスキップ
                    continue

            features.append({
                "type": "Feature",
                "id": r["id"],
                "properties": {
                    "name": r["name"],
                    "created_at": (r["created_at"].isoformat()
                                   if r.get("created_at") else None),
                },
                "geometry": geom  # None も GeoJSON 仕様的に許容される
            })

        return jsonify({"ok": True, "type": "FeatureCollection", "features": features})

    except Exception as e:
        current_app.logger.exception("Query/serialize failed")
        return jsonify({"ok": False, "where": "query_or_serialize", "detail": str(e)}), 500

    finally:
        put_conn(conn)