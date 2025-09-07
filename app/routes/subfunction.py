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
# 通知画面取得
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

        # すべてのフォローリクエストを取得（pending と accepted 両方）
        cur.execute("""
            SELECT fr.request_id, fr.sender_uid, fr.receiver_uid, fr.status, fr.created_at,
                   u.display_name, u.icon
            FROM follow_requests fr
            JOIN users u ON fr.sender_uid = u.id
            WHERE fr.receiver_uid = %s
            ORDER BY fr.created_at DESC
        """, (current_user_id,))
        rows = cur.fetchall()

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
    print("[DEBUG] request_id from form:", request_id)

    if not request_id:
        flash("リクエストIDがありません", "error")
        return redirect(url_for('subfunction.notification'))

    try:
        request_id = int(request_id)
    except ValueError:
        flash("リクエストIDが不正です", "error")
        return redirect(url_for('subfunction.notification'))

    current_user_id = session['user_id']
    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print("[DEBUG] DB接続成功")

        # 1. フォローリクエストを取得
        cur.execute("SELECT sender_uid, receiver_uid, status FROM follow_requests WHERE request_id=%s", (request_id,))
        row = cur.fetchone()
        print("[DEBUG] DB row fetched:", row)

        if not row:
            flash("リクエストが存在しません", "error")
            return redirect(url_for('subfunction.notification'))

        sender_uid, receiver_uid, status = row
        print(f"[DEBUG] sender_uid={sender_uid}, receiver_uid={receiver_uid}, status={status}")

        if status == 'accepted':
            flash("すでに承認済みです", "info")
            return redirect(url_for('subfunction.notification'))

        # 2. user_follow に相互フォローを追加
        try:
            cur.execute("""
                INSERT INTO user_follow (follower_uid, followee_uid)
                VALUES (%s, %s), (%s, %s)
                ON CONFLICT (follower_uid, followee_uid) DO NOTHING
            """, (sender_uid, receiver_uid, receiver_uid, sender_uid))
            print("[DEBUG] user_followへのINSERT成功")
        except Exception as e_insert:
            print("[ERROR] user_follow INSERT失敗:", e_insert)
            raise

        # 3. follow_requests のステータス更新
        try:
            cur.execute("UPDATE follow_requests SET status='accepted' WHERE request_id=%s", (request_id,))
            print("[DEBUG] follow_requests UPDATE成功, updated rows:", cur.rowcount)
        except Exception as e_update:
            print("[ERROR] follow_requests UPDATE失敗:", e_update)
            raise

        # 4. コミット
        conn.commit()
        print("[DEBUG] コミット成功")
        flash("フォローを承認しました", "success")

    except Exception as e:
        print("[ERROR] 承認処理で例外発生:", e)
        if conn:
            conn.rollback()
            print("[DEBUG] ロールバック実行")
        flash(f"承認エラー: {e}", "error")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            print("[DEBUG] DB接続クローズ")

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