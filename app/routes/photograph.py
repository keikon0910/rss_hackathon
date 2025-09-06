from flask import Blueprint, render_template

photograph_bp = Blueprint(
    'photograph',
    __name__,
    template_folder='../../templates/photograph',
    url_prefix=''
)

@photograph_bp.route('/post_past')
def post_past():
    return render_template('post_past.html')


@photograph_bp.route('/post')
def post():
    return render_template('post.html')