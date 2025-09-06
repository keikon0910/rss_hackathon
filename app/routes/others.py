from flask import Blueprint, render_template , session, redirect, url_for, flash

others_bp = Blueprint('others',__name__,url_prefix='/others',template_folder='../templates' )

others_bp.route('/others_personal')
def others_personal():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('others/others_personal.html')

others_bp.route('/others_post')
def others_post():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('others/others_post.html')
