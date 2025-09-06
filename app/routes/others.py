from flask import Blueprint, render_template, session, redirect, url_for, flash
from ..db import get_conn
from psycopg2.extras import RealDictCursor

others_bp = Blueprint(
    'others', 
    __name__, 
    template_folder='../../templates/others', 
    url_prefix='/others'
)

@others_bp.route('/others_post/<int:landmark_id>')
def others_post(landmark_id):
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))

    posts = []
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 投稿を取得（画像URLも取得）
        cur.execute(
            "SELECT id, title, body, image_url, created_at FROM posts WHERE landmark_id = %s ORDER BY created_at DESC",
            (landmark_id,)
        )
        for row in cur.fetchall():
            posts.append({
                'id': row['id'],
                'title': row['title'],
                'body': row['body'],
                'image_url': row['image_url'] or '',  # 画像がない場合は空文字
                'created_at': row['created_at'].strftime("%Y/%m/%d %H:%M") if row['created_at'] else ''
            })

        cur.close()
        conn.close()

    except Exception as e:
        flash(f"投稿取得エラー: {e}", "error")

    return render_template('others_post.html', landmark_id=landmark_id, posts=posts)
