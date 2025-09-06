from flask import Blueprint, render_template , session, redirect, url_for, flash , request
from werkzeug.security import check_password_hash
import psycopg2
from datetime import datetime
import base64

photograph_bp = Blueprint(
    'photograph',
    __name__,
    template_folder='../../templates/photograph',
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
    conn = psycopg2.connect(**DB_PARAMS)
    return conn

@photograph_bp.route('/post_past')
def post_past():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('post_past.html')


@photograph_bp.route('/post', methods=['GET', 'POST'])
def post():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        photo = request.files.get('photo')

        if not title or not photo:
            flash("タイトルと写真をアップロードしてください", "error")
            return render_template('post.html')

        try:
            # 画像をBase64エンコード
            photo_data = photo.read()
            image_base64 = base64.b64encode(photo_data).decode('utf-8')

            # DBにINSERT
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO posts (user_id, landmark_id, title, body, image_url, created_at)
                VALUES (%s, NULL, %s, '', %s, %s)
            """, (
                session['user_id'],
                title,
                image_base64,
                datetime.utcnow()
            ))
            conn.commit()
            cur.close()
            conn.close()

            flash("投稿が完了しました！", "success")
            return redirect(url_for('home.home'))

        except Exception as e:
            flash(f"エラーが発生しました: {e}", "error")

    return render_template('post.html')
