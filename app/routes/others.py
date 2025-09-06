# others/routes.py など
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from psycopg2.extras import RealDictCursor
from ..db import get_conn, put_conn

others_bp = Blueprint('others', __name__,
                      template_folder='../../templates/others',
                      url_prefix='')

@others_bp.route('/others_post')
def others_post():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))

    landmark_id = request.args.get('landmark_id')
    posts = []

    if landmark_id:
        conn = get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT p.id, p.title, p.body, p.image_url, p.created_at, u.display_name as user_name
                    FROM posts p
                    JOIN users u ON p.user_id = u.id
                    WHERE p.landmark_id = %s
                    ORDER BY p.created_at DESC
                """, (landmark_id,))
                posts = cur.fetchall()
        finally:
            put_conn(conn)

    return render_template('others/others_post.html', posts=posts)



others_bp.route('/others_personal')
def others_personal():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('others/others_personal.html')
