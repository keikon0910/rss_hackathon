from flask import Blueprint, render_template , session, redirect, url_for, flash, request
import psycopg2
from psycopg2.extras import RealDictCursor

subfunction_bp = Blueprint(
    'subfunction',
    __name__,
    template_folder='../../templates/subfunction',
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

@subfunction_bp.route('/DM')
def DM():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('DM.html')

@subfunction_bp.route('/DM_personal')
def DM_personal():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('DM_personal.html')

# 通知画面
@subfunction_bp.route('/notification')
def notification():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))

    current_user_id = session['user_id']
    follow_requests = []

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # users テーブルに JOIN して通知を取得
        cur.execute("""
            SELECT fr.request_id, fr.sender_uid, fr.receiver_uid, fr.status, fr.created_at,
                   u.display_name, u.icon
            FROM follow_requests fr
            JOIN users u ON fr.sender_uid = u.id
            WHERE fr.receiver_uid = %s AND fr.status = 'pending'
            ORDER BY fr.created_at DESC
        """, (current_user_id,))
        rows = cur.fetchall()

        # リストを辞書形式に変換してテンプレートに渡す
        for r in rows:
            follow_requests.append({
                'request_id': r[0],
                'sender_uid': r[1],
                'receiver_uid': r[2],
                'status': r[3],
                'created_at': r[4],
                'display_name': r[5],
                'icon': r[6]
            })

        cur.close()
        conn.close()

    except Exception as e:
        flash(f"通知取得エラー: {e}", "error")

    return render_template('notification.html', follow_requests=follow_requests)

# 承認
@subfunction_bp.route('/accept_follow_request', methods=['POST'])
def accept_follow_request():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))

    request_id = request.form.get('request_id')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # フォローリクエスト情報を取得
        cur.execute("SELECT sender_uid, receiver_uid FROM follow_requests WHERE request_id = %s", (request_id,))
        row = cur.fetchone()
        if row:
            sender_uid, receiver_uid = row

            # 相互フォローに追加
            cur.execute("""
                INSERT INTO user_follow (follower_uid, followee_uid)
                VALUES (%s, %s), (%s, %s)
                ON CONFLICT (follower_uid, followee_uid) DO NOTHING
            """, (sender_uid, receiver_uid, receiver_uid, sender_uid))

            # ステータス更新
            cur.execute("UPDATE follow_requests SET status='accepted' WHERE request_id = %s", (request_id,))
            conn.commit()
            flash("フォローを承認しました", "success")
        else:
            flash("リクエストが存在しません", "error")

        cur.close()
        conn.close()
    except Exception as e:
        conn.rollback()
        flash(f"承認エラー: {e}", "error")

    return redirect(url_for('subfunction.notification'))

# 拒否
@subfunction_bp.route('/reject_follow_request', methods=['POST'])
def reject_follow_request():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))

    request_id = request.form.get('request_id')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM follow_requests WHERE request_id = %s", (request_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("フォローリクエストを拒否しました", "success")
    except Exception as e:
        conn.rollback()
        flash(f"拒否エラー: {e}", "error")

    return redirect(url_for('subfunction.notification'))