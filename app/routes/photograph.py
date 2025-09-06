from flask import Blueprint, render_template , session, redirect, url_for, flash

photograph_bp = Blueprint(
    'photograph',
    __name__,
    template_folder='../../templates/photograph',
    url_prefix=''
)

@photograph_bp.route('/post_past')
def post_past():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('post_past.html')


@photograph_bp.route('/post')
def post():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('post.html')