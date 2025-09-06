from flask import Blueprint, render_template

photograph_bp = Blueprint('photograph',__name__,url_prefix='/photograph',template_folder='../templates' )

@photograph_bp.route('/post_past')
def post_past():
    return render_template('photograph/post_past.html')


@photograph_bp.route('/post')
def post():
    return render_template('photograph/post.html')