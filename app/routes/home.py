from flask import Blueprint, render_template, session, redirect, url_for, flash
home_bp = Blueprint('home', __name__,
    template_folder='../../templates/home',  
    url_prefix=''  
)

@home_bp.route('/home')
def home():
    if 'user_id' not in session:
        flash("ログインが必要です", "error")
        return redirect(url_for('index.login'))
    
    return render_template('home.html', display_name=session.get('display_name'))
