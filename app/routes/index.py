from flask import Blueprint, render_template
from flask import request, redirect, url_for, flash

index_bp = Blueprint(
    'index',
    __name__,
    template_folder='../../templates/index'  
)

@index_bp.route('/')
def index():
    return render_template('index.html')  

@index_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u_name = request.form.get('u_name')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not all([u_name, email, password1, password2]):
            flash("すべての項目を入力してください", "error")
            return render_template('signup.html')

        if password1 != password2:
            flash("パスワードが一致しません", "error")
            return render_template('signup.html')

        password_hash = generate_password_hash(password1)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users_table (u_name, email, password_hash) VALUES (?, ?, ?)",
                (u_name, email, password_hash)
            )
            conn.commit()
            conn.close()

            flash("登録が完了しました。ログインしてください。", "success")
            return redirect(url_for('users_login.login'))

        except sqlite3.IntegrityError:
            flash("このメールアドレスはすでに使用されています", "error")
            return render_template('signup.html')
        except Exception as e:
            logging.error(f"サインアップエラー: {e}")
            flash("予期せぬエラーが発生しました。管理者にお問い合わせください。", "error")
            return render_template('signup.html')

    return render_template('login.html')

@index_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    return render_template('registration.html')
