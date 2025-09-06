from flask import Blueprint, render_template , session, redirect, url_for, flash, request
import psycopg2
from werkzeug.security import check_password_hash

personal_page_bp = Blueprint(
    'personal_page',
    __name__,
    url_prefix='',
    template_folder='../../templates/personal_page'
)

# PostgreSQL 接続情報
DB_PARAMS = {
    "dbname": "posts_db_rkcz",
    "user": "posts_db_rkcz_user",
    "password": "rPcuE4VPsn79TPngWJd8ZAQrDF1ktI7F",
    "host": "dpg-d2top2p5pdvs739pct1g-a.oregon-postgres.render.com",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)


@personal_page_bp.route('/personal_page')
def personal_page():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('personal_page.html')

from flask import Blueprint, render_template, session, redirect, url_for, flash
import psycopg2

personal_page_bp = Blueprint(
    'personal_page',
    __name__,
    template_folder='../../templates/personal_page',
    url_prefix=''
)

# PostgreSQL 接続情報
DB_PARAMS = {
    "dbname": "posts_db_rkcz",
    "user": "posts_db_rkcz_user",
    "password": "rPcuE4VPsn79TPngWJd8ZAQrDF1ktI7F",
    "host": "dpg-d2top2p5pdvs739pct1g-a.oregon-postgres.render.com",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)

from flask import Blueprint, render_template, session, redirect, url_for, flash
import psycopg2
from datetime import datetime

personal_page_bp = Blueprint(
    'personal_page',
    __name__,
    template_folder='../../templates/personal_page',
    url_prefix=''
)

DB_PARAMS = {
    "dbname": "posts_db_rkcz",
    "user": "posts_db_rkcz_user",
    "password": "rPcuE4VPsn79TPngWJd8ZAQrDF1ktI7F",
    "host": "dpg-d2top2p5pdvs739pct1g-a.oregon-postgres.render.com",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)

@personal_page_bp.route('/personal_page')
def personal_page():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))

    user_data = {}
    posts = []
    post_count = 0
    followers_count = 0
    following_count = 0

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # ユーザー情報
        cur.execute("SELECT display_name, icon FROM users WHERE id=%s", (session['user_id'],))
        row = cur.fetchone()
        if row:
            user_data = {
                'display_name': row[0],
                'icon': row[1] or ''
            }

        # 投稿一覧
        cur.execute("""
            SELECT id, title, image_url, created_at
            FROM posts
            WHERE user_id=%s
            ORDER BY created_at DESC
        """, (session['user_id'],))
        posts = [
            {'id': r[0], 'title': r[1], 'image_url': r[2], 'created_at': r[3].strftime("%Y/%m/%d %H:%M")}
            for r in cur.fetchall()
        ]

        # 投稿数
        cur.execute("SELECT COUNT(*) FROM posts WHERE user_id=%s", (session['user_id'],))
        post_count = cur.fetchone()[0]

        # フォロー数とフォロワー数
        current_user_id = session['user_id']

        # 自分がフォローしている人数
        cur.execute("""
            SELECT COUNT(*) FROM user_follow uf
            WHERE uf.follower_uid = %s
        """, (current_user_id,))
        following_count = cur.fetchone()[0]

        # 自分をフォローしている人数
        cur.execute("""
            SELECT COUNT(*) FROM user_follow uf
            WHERE uf.followee_uid = %s
        """, (current_user_id,))
        followers_count = cur.fetchone()[0]

        cur.close()
        conn.close()

    except Exception as e:
        flash(f"データ取得エラー: {e}", "error")

    return render_template(
        'personal_page.html',
        user=user_data,
        posts=posts,
        post_count=post_count,
        followers=followers_count,
        following=following_count
    )


@personal_page_bp.route('/personal_setting')
def personal_setting():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))

    user_data = {}
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, display_name, email, icon, is_public, created_at
            FROM users
            WHERE id = %s
        """, (session['user_id'],))
        row = cur.fetchone()
        if row:
            user_data = {
                'id': row[0],
                'display_name': row[1],
                'email': row[2],
                'icon': row[3] if row[3] else '',
                'is_public': row[4],
                'created_at': row[5]
            }
        cur.close()
        conn.close()
    except Exception as e:
        flash(f"ユーザー情報の取得に失敗しました: {e}", "error")

    return render_template('personal_setting.html', user=user_data)


@personal_page_bp.route('/search_users', methods=['GET', 'POST'])
def search_users():
    users = []
    query = request.args.get('username', '').strip()
    current_user_id = session.get('user_id')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # フォローボタン押下時（POST）
        if request.method == 'POST':
            follow_user_id = request.form.get('follow_user_id')
            if follow_user_id and current_user_id:
                try:
                    cur.execute("""
                        INSERT INTO follow_requests (sender_uid, receiver_uid)
                        VALUES (%s, %s)
                        ON CONFLICT (sender_uid, receiver_uid) DO NOTHING
                        RETURNING request_id
                    """, (current_user_id, follow_user_id))
                    inserted = cur.fetchone()
                    conn.commit()

                    if inserted:
                        flash("フォローリクエストを送信しました", "success")
                    else:
                        flash("すでにリクエスト済みです", "info")

                except Exception as e:
                    conn.rollback()
                    flash(f"フォローリクエスト送信エラー: {e}", "error")

        # ユーザー検索
        if query:
            cur.execute("""
                SELECT u.id, u.display_name, u.icon,
                       CASE 
                           WHEN uf.follower_uid IS NOT NULL THEN TRUE  -- 相互フォロー済み
                           ELSE FALSE
                       END AS is_followed,
                       CASE 
                           WHEN fr.status = 'pending' THEN TRUE       -- フォローリクエスト送信済み
                           ELSE FALSE
                       END AS is_pending
                FROM users u
                LEFT JOIN follow_requests fr
                    ON fr.sender_uid = %s AND fr.receiver_uid = u.id
                LEFT JOIN user_follow uf
                    ON uf.follower_uid = %s AND uf.followee_uid = u.id
                WHERE u.display_name ILIKE %s
                  AND u.id <> %s  -- 自分自身は除外
                ORDER BY u.display_name
            """, (current_user_id, current_user_id, f"%{query}%", current_user_id))
            rows = cur.fetchall()

            users = [{
                "id": r[0],
                "name": r[1],
                "icon": r[2] or "",
                "is_followed": r[3],
                "is_pending": r[4]
            } for r in rows]

        cur.close()
        conn.close()

    except Exception as e:
        flash(f"検索エラー: {e}", "error")

    return render_template('search_users.html', users=users, query=query)
