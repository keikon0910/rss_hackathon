# others.py
from flask import Blueprint, render_template, session, redirect, url_for, flash
from ..db import get_conn

others_bp = Blueprint('others', __name__, template_folder='../../templates/others', url_prefix='/others')

@others_bp.route('/others_post/<int:landmark_id>')
def others_post(landmark_id):
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))

    # DBからそのランドマークの投稿を取得
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM posts WHERE landmark_id = %s ORDER BY created_at DESC", (landmark_id,))
    posts = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('others/others_post.html', landmark_id=landmark_id, posts=posts)
