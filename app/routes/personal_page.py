from flask import Blueprint, render_template , session, redirect, url_for, flash
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

@personal_page_bp.route('/personal_page')
def personal_page():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('personal_page.html')

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
