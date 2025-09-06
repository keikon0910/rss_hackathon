from flask import Blueprint, render_template

others_bp = Blueprint('others',__name__,url_prefix='/others',template_folder='../templates' )

others_bp.route('/others_personal')
def others_personal():
    return render_template('others/others_personal.html')

others_bp.route('/others_post')
def others_post():
    return render_template('others/others_post.html')
