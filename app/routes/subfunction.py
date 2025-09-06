from flask import Blueprint, render_template , session, redirect, url_for, flash

subfunction_bp = Blueprint(
    'subfunction',
    __name__,
    template_folder='../../templates/subfunction',
    url_prefix=''
)


@subfunction_bp.route('/DM')
def DM():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('DM.html')

@subfunction_bp.route('/DM_personal')
def DM_personal():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('DM_personal.html')

@subfunction_bp.route('/notification')
def notification():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    return render_template('notification.html')