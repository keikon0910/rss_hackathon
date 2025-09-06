from flask import Blueprint, render_template

home_bp = Blueprint('index',__name__,url_prefix='/',template_folder='../templates' )

@home_bp.route('/home')
def home():
    return render_template('index/index.html')