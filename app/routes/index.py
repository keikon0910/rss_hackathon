from flask import Blueprint, render_template, request, redirect, url_for, flash , session
from werkzeug.security import generate_password_hash ,check_password_hash
from datetime import datetime
import psycopg2

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

index_bp = Blueprint(
    'index',
    __name__,
    template_folder='../../templates/index',  
    url_prefix=''  
)

# ルート /
@index_bp.route('/')
def index():
    return render_template('index.html')

@index_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # フォームから値を取得
        display_name = request.form.get('display_name')
        password = request.form.get('password')

        # 入力チェック
        if not display_name or not password:
            flash("ユーザーネームとパスワードを入力してください", "error")
            return render_template('login.html')

        try:
            # DB接続してユーザー情報を取得
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, display_name, password_hash
                FROM users
                WHERE display_name = %s
            """, (display_name,))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if user is None:
                flash("ユーザーが存在しません", "error")
                return render_template('login.html')

            user_id, user_name, password_hash = user

            # パスワード照合
            if check_password_hash(password_hash, password):
                # ログイン成功 → セッションに保存
                session['user_id'] = user_id
                session['display_name'] = user_name
                flash(f"{user_name}さん、ログイン成功！", "success")
                return redirect(url_for('home.home'))  # home.html へ
            else:
                flash("パスワードが間違っています", "error")
                return render_template('login.html')

        except Exception as e:
            flash(f"データベースエラー: {e}", "error")
            return render_template('login.html')

    # GETリクエストの場合はログインページ表示
    return render_template('login.html')



# 登録ページ
@index_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        display_name = request.form.get('display_name')
        password_confirm = request.form.get('password_confirm')

        # 入力チェック
        if not all([email, password, display_name, password_confirm]):
            flash("すべての項目を入力してください", "error")
            return render_template('registration.html')

        if password != password_confirm:
            flash("パスワードが一致しません", "error")
            return render_template('registration.html')

        password_hash = generate_password_hash(password)
        created_at = datetime.utcnow()

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (email, password_hash, display_name, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (email, password_hash, display_name, created_at))
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()

            flash(f"ユーザー登録が完了しました（ID: {user_id}）", "success")
            return render_template('login.html')
        except Exception as e:
            flash(f"データベースエラー: {e}", "error")
            return render_template('registration.html')

    return render_template('registration.html')


    index_bp = Blueprint('index',__name__,url_prefix='/',template_folder='../templates' )



    @index_bp.route('/')
    def home():
        return render_template('index/index.html')

    @index_bp.route('/login', methods=['GET', 'POST'])
    def login():
        return render_template('index/login.html')

    @index_bp.route('/registration', methods=['GET', 'POST'])
    def registration():
        return render_template('index/registration.html')