# app/routes/personal_page.py
from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    flash,
    jsonify,
    request,
    abort,
    send_file,
)
from psycopg2.extras import RealDictCursor
from io import BytesIO
import psycopg2

# ====== PostgreSQL 接続情報（あなたの index.py と同スタイル）======
DB_PARAMS = {
    "dbname": "posts_db_rkcz",
    "user": "posts_db_rkcz_user",
    "password": "rPcuE4VPsn79TPngWJd8ZAQrDF1ktI7F",
    "host": "dpg-d2top2p5pdvs739pct1g-a.oregon-postgres.render.com",
    "port": "5432",
    "sslmode": "require",  # Render/クラウド系では推奨
}


def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)


# ====== Blueprint ======
personal_page_bp = Blueprint(
    "personal_page",
    __name__,
    url_prefix="/personal_page",
    template_folder="../../templates/personal_page",
)


# ====== 画面ルート ======
@personal_page_bp.route("/")
def personal_page():
    if "user_id" not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for("index.login"))
    return render_template("personal_page.html")


@personal_page_bp.route("/settings")
def personal_settings():
    if "user_id" not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for("index.login"))
    return render_template("personal_settings.html")


# ====== 設定API（personal_settings.html のJSが叩く）======


def _require_login_user_id():
    uid = session.get("user_id")
    if not uid:
        abort(401)
    return uid


# GET /api/user/me ・・・初期表示データ
@personal_page_bp.get("/api/user/me")
def api_user_me_get():
    user_id = _require_login_user_id()
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, email, display_name, is_public, created_at,
                       CASE WHEN icon IS NOT NULL THEN TRUE ELSE FALSE END AS has_icon
                FROM users
                WHERE id = %s
            """,
                (user_id,),
            )
            row = cur.fetchone()
        if not row:
            abort(404)
        return jsonify(
            {
                "id": row["id"],
                "email": row["email"],
                "username": row["display_name"],
                "is_public": row["is_public"],
                "created_at": (
                    row["created_at"].isoformat() if row["created_at"] else None
                ),
                "avatar_url": (
                    "/personal_page/api/user/icon" if row["has_icon"] else None
                ),
            }
        )
    finally:
        conn.close()


# POST /api/user/me ・・・表示名/公開設定/メールを更新
@personal_page_bp.post("/api/user/me")
def api_user_me_post():
    user_id = _require_login_user_id()
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    # UIは「非公開にする」チェックなので、is_public はその逆（JS側で反転済み）
    is_public = bool(data.get("is_public"))

    if not username or not email:
        return jsonify({"ok": False, "message": "ユーザー名とメールは必須です"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # display_name / email のユニーク衝突チェック（自分以外）
            cur.execute(
                "SELECT 1 FROM users WHERE display_name = %s AND id <> %s",
                (username, user_id),
            )
            if cur.fetchone():
                return (
                    jsonify(
                        {"ok": False, "message": "このユーザー名は既に使われています"}
                    ),
                    409,
                )

            cur.execute(
                "SELECT 1 FROM users WHERE email = %s AND id <> %s", (email, user_id)
            )
            if cur.fetchone():
                return (
                    jsonify({"ok": False, "message": "このメールは既に使われています"}),
                    409,
                )

            # 更新
            cur.execute(
                """
                UPDATE users
                   SET display_name = %s,
                       email        = %s,
                       is_public    = %s
                 WHERE id = %s
            """,
                (username, email, is_public, user_id),
            )
            conn.commit()
        # セッション表示名を画面で使っているなら同期
        session["display_name"] = username
        return jsonify({"ok": True})
    finally:
        conn.close()


# GET /api/user/icon ・・・DBのbyteaを返す（img srcで利用）
@personal_page_bp.get("/api/user/icon")
def api_user_icon_get():
    user_id = _require_login_user_id()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT icon FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
        if not row or row[0] is None:
            abort(404)
        bio = BytesIO(row[0])
        return send_file(bio, mimetype="image/png")
    finally:
        conn.close()


# （任意）POST /api/user/icon ・・・multipart/form-data でアイコン保存
@personal_page_bp.post("/api/user/icon")
def api_user_icon_post():
    user_id = _require_login_user_id()
    file = request.files.get("file")
    if not file:
        return jsonify({"ok": False, "message": "ファイルがありません"}), 400

    data = file.read()
    # TODO: コンテンツタイプ・サイズ上限・拡張子チェック等は適宜追加
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET icon = %s WHERE id = %s",
                (psycopg2.Binary(data), user_id),
            )
            conn.commit()
        return jsonify({"ok": True})
    finally:
        conn.close()
