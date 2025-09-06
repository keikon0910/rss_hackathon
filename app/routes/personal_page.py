from flask import Blueprint, render_template , session, redirect, url_for, flash


personal_page_bp = Blueprint(
    'personal_page',
    __name__,
    url_prefix='',
    template_folder='../../templates/personal_page'
)


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
    return render_template('personal_setting.html')